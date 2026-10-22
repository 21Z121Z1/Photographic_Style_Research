"""Shared real-reference RGB/LMS/power enclosures, with outward remainders.

No native arithmetic is reassociated. Affine forms describe joint real
references; the caller separately retains every native FP-stage allowance.
"""
from dataclasses import dataclass
import math
import numpy as np
from guided_affine import A
from leaf_numeric import V,DomainUnknown


@dataclass(frozen=True)
class JointRGB(V):
    affine: tuple=()
    relation: str=''

    def __post_init__(self):
        super().__post_init__()
        if self.point or self.precision!='h'or np.shape(self.lo)!=(3,)or len(self.affine)!=3 or any(not isinstance(a,A)for a in self.affine)or not self.relation:raise TypeError('Explicit three-channel half-set affine relation required')


def as_value(values,relation):
    lo,hi=np.array([a.bounds()for a in values]).T
    if max(np.max(abs(lo)),np.max(abs(hi)))>65504:raise DomainUnknown('Shared RGB finite half range exceeded')
    v=V.bounds(lo,hi);return JointRGB(v.lo,v.hi,'h',False,tuple(values),relation)


def sources(rgb):return list(rgb.affine)if isinstance(rgb,JointRGB)else[A.box(lo,hi)for lo,hi in zip(rgb.lo,rgb.hi)]


def clipped(a,lo,hi):
    # Original input clamp, approximated jointly by its secant plus the exact
    # piecewise-linear residual extrema at0/1. Not an added output clamp.
    if hi<=0:return A.value(0)
    if lo>=1:return A.value(1)
    if lo>=0 and hi<=1:return a
    f=lambda x:min(max(x,0.),1.)
    if lo==hi:return A.value(f(lo))
    slope=(f(hi)-f(lo))/(hi-lo);bias=f(lo)-slope*lo;knots=[lo,hi]+[v for v in [0.,1.]if lo<v<hi];res=[f(v)-(slope*v+bias)for v in knots]
    return a.scale(slope).add(bias).noise(min(res)-2e-12,max(res)+2e-12).guard()


def clamped_sources(rgb):return [clipped(a,float(lo),float(hi))for a,lo,hi in zip(sources(rgb),rgb.lo,rgb.hi)]


def mat(values,matrix):
    result=[]
    for row in matrix:
        a=A.value(0)
        for coefficient,v in zip(row,values):a=a.add(v.scale(float(coefficient)))
        result.append(a)
    return result


def concave_power(a,p):
    lo,hi=a.bounds();lo=max(0.,lo);hi=max(lo,hi)
    if not 0<p<1:raise TypeError('This real secant proof requires0<p<1')
    if lo==hi:return A.value(lo**p)
    slope=(hi**p-lo**p)/(hi-lo);bias=lo**p-slope*lo
    critical=(slope/p)**(1/(p-1))if slope>0 else lo;critical=min(max(critical,lo),hi)
    gap=max(0.,critical**p-(slope*critical+bias));e=2e-12*max(1.,hi**p)
    return a.scale(slope).add(bias).noise(-e,gap+e).guard()


def shared_ideal(rgb,M,N,p):
    source=clamped_sources(rgb);lms=mat(source,M);roots=[concave_power(a,p)for a in lms];lab=mat(roots,N);ll,lh=np.array([a.bounds()for a in lms]).T;nl,nh=np.array([a.bounds()for a in lab]).T
    return source,np.maximum(ll,0),lh,nl,nh,{'method':'same RGB generators in M; concave power secant plus whole-domain residual; N shares those roots','LMS_max_width':float(np.max(lh-ll)),'Lab_max_width':float(np.max(nh-nl)),'original_RGB_relation_retained':isinstance(rgb,JointRGB),'original_FP_budgets_applied_separately':True}


def half_round(a):
    lo,hi=a.bounds();e=math.nextafter(2**-10*max(abs(lo),abs(hi))+2**-24,math.inf)
    if max(abs(lo-e),abs(hi+e))>65504:raise DomainUnknown('Shared half arithmetic budget exceeded')
    return a.noise(-e,e).guard()
