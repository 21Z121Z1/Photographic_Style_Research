"""Complete AIR10 semantic helper, conditional on working-domain inputs/GTC.

Point mode spells out half arithmetic and an ideal pixel-linear clamp sampler.
Set mode propagates coefficient intervals with an explicit 2u half-operation
allowance (u=2^-11); it is a host assumption, not Apple GPU/sampler accuracy.
No scene-linear/P3, original-frame statistics or whole-camera claim is made.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
import sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'semantic-styles'))
from spatial_curve_retarget import _evaluate

EPS=float(np.array([0x1c04],dtype='u2').view('f2')[0])


@dataclass(frozen=True)
class Curve1D:
    red_samples: tuple[float,...]
    coordinate_space: str

    def __post_init__(self):
        a=np.asarray(self.red_samples,dtype='f2')
        if not self.coordinate_space or not 2<=len(a)<=1024 or not np.isfinite(a).all()or np.max(abs(a))>8:raise ValueError('2..1024 supplied finite half red samples and identified coordinate required')
        object.__setattr__(self,'red_samples',tuple(map(float,a)))

    def sample(self,q):
        # Pixel u=q*(width-1)+.5: sampler's index is u-.5. This is the
        # same supplied piecewise-linear/clamped table evaluation, not a new
        # camera-curve fit. Original hardware interpolation precision is open.
        knots=[Fraction(i,len(self.red_samples)-1)for i in range(len(self.red_samples))]
        table=list(map(Fraction.from_float,self.red_samples))
        return np.array([float(_evaluate(table,knots,Fraction.from_float(float(x))))for x in np.asarray(q).flat]).reshape(np.asarray(q).shape)

    def range(self,lo,hi):
        out_lo=[];out_hi=[];nodes=np.linspace(0,1,len(self.red_samples))
        for a,b in zip(np.asarray(lo).flat,np.asarray(hi).flat):
            vals=[float(self.sample(a)),float(self.sample(b))]+[v for x,v in zip(nodes,self.red_samples)if a<=x<=b]
            out_lo.append(min(vals));out_hi.append(max(vals))
        return np.asarray(out_lo).reshape(np.asarray(lo).shape),np.asarray(out_hi).reshape(np.asarray(hi).shape)


@dataclass(frozen=True)
class SemanticInputs:
    working_rgb: tuple[float,float,float]
    reference_rgb: tuple[float,float,float]
    person_weight: float
    curve: Curve1D

    def arrays(self):
        x=np.asarray(self.working_rgb,dtype='f2');ref=np.asarray(self.reference_rgb,dtype='f2');weight=np.float16(self.person_weight)
        if x.shape!=(3,)or ref.shape!=(3,)or not np.isfinite(x).all()or not np.isfinite(ref).all()or np.any(x<0)or np.max(x)>1 or np.min(ref)<2**-10 or np.max(ref)>2 or not 0<=weight<=1:
            raise ValueError('Declared finite-intermediate domain: RGB[0,1], reference[2^-10,2], person weight[0,1]')
        return x,ref,weight


def coefficients7(values,*,dtype='f4'):
    a=np.asarray(values,dtype=dtype)
    if a.shape!=(7,)or not np.isfinite(a).all()or np.max(abs(a))>8:raise ValueError('Seven finite supplied semantic coefficients, abs <=8')
    return a


def forward_half(inputs: SemanticInputs,values):
    x,ref,person=inputs.arrays();p=coefficients7(values).astype('f2')
    def h(a):
        out=np.asarray(a,dtype='f2')
        if not np.isfinite(out).all():raise ValueError('Nonfinite half intermediate: unknown outside the finite-intermediate contract')
        return out
    def mix(a,b,w):return h(h(a)+h(h(h(b)-h(a))*h(w)))
    def branch(exposure,ltm,hr):
        scaled=np.minimum(h(x*exposure),h(1))
        index=h(scaled*h(h(len(inputs.curve.red_samples))-h(1)))
        # Original coord is f32(index)+.5; subtracting .5 in the CPU sampler
        # yields this exact half index before ideal float interpolation.
        sample=h(inputs.curve.sample(index.astype('f8')/(len(inputs.curve.red_samples)-1)))
        gtc=mix(scaled,sample,p[4]);ratio=h(gtc/ref)
        ratio=np.where(h(ref-h(EPS))<0,h(0),ratio)
        local=mix(ratio,h(1),ltm);limited=np.minimum(local,h(1))
        return h(mix(local,limited,hr)*ref)
    with np.errstate(over='ignore',invalid='ignore',divide='ignore'):
        bg=branch(p[2],p[0],p[5]);fg=branch(p[3],p[1],p[6]);out=mix(bg,fg,person)
    if not np.isfinite(out).all():raise ValueError('Nonfinite half intermediate/output outside declared execution contract')
    return out


@dataclass(frozen=True)
class I:
    lo: np.ndarray
    hi: np.ndarray

    @classmethod
    def point(cls,x):a=np.asarray(x,dtype='f8');return cls(a,a)

    @classmethod
    def half_cast(cls,lo,hi):
        a=np.asarray(lo,dtype='f2');b=np.asarray(hi,dtype='f2')
        return cls(np.nextafter(a,np.float16(-np.inf)).astype('f8'),np.nextafter(b,np.float16(np.inf)).astype('f8'))

    def widen(self):
        e=np.maximum(abs(self.lo),abs(self.hi))*2**-10+2**-24
        if not np.isfinite(e).all()or np.max(np.maximum(abs(self.lo),abs(self.hi))+e)>65504:
            raise ValueError('Half intermediate enclosure exceeds finite domain; unknown')
        return I(np.nextafter(self.lo-e,-np.inf),np.nextafter(self.hi+e,np.inf))

    def __add__(self,b):b=interval(b);return I(self.lo+b.lo,self.hi+b.hi).widen()
    __radd__=__add__
    def __neg__(self):return I(-self.hi,-self.lo)
    def __sub__(self,b):return self+-interval(b)
    def __rsub__(self,b):return interval(b)+-self
    def __mul__(self,b):
        b=interval(b);corners=np.array([self.lo*b.lo,self.lo*b.hi,self.hi*b.lo,self.hi*b.hi])
        return I(np.min(corners,axis=0),np.max(corners,axis=0)).widen()
    __rmul__=__mul__
    def __truediv__(self,b):
        b=interval(b)
        if np.any((b.lo<=0)&(b.hi>=0)):raise ValueError('Unknown interval division across zero')
        return self*I(1/b.hi,1/b.lo)
    def minimum_one(self):return I(np.minimum(self.lo,1),np.minimum(self.hi,1))


def interval(x):return x if isinstance(x,I)else I.point(x)
def imix(a,b,w):return interval(a)+(interval(b)-interval(a))*interval(w)


@dataclass(frozen=True)
class SemanticSetResult:
    lower: np.ndarray
    upper: np.ndarray
    input_branches: tuple
    set_coverage_only: bool=True
    original_GPU_accuracy_verified: bool=False
    full_pixel_pipeline_verified: bool=False


def forward_set(inputs: SemanticInputs,lower,upper,*,input_branches=()):
    x,ref,person=inputs.arrays();lo=coefficients7(lower,dtype='f8');hi=coefficients7(upper,dtype='f8')
    if np.any(lo>hi):raise ValueError('Ordered semantic coefficient intervals required')
    p=I.half_cast(lo,hi);x=I.point(x.astype('f8'));ref=I.point(ref.astype('f8'))
    def get(n):return I(p.lo[n],p.hi[n])
    def branch(exposure,ltm,hr):
        scaled=(x*exposure).minimum_one();index=scaled*(len(inputs.curve.red_samples)-1)
        a,b=inputs.curve.range(index.lo/(len(inputs.curve.red_samples)-1),index.hi/(len(inputs.curve.red_samples)-1))
        sample=I.half_cast(a,b);gtc=imix(scaled,sample,get(4));ratio=gtc/ref
        # Reference is supplied exact half. This branch uses ref + half(-EPS),
        # whose sign is exact at this half threshold; equality is NOT zeroed.
        mask=ref.lo<EPS;ratio=I(np.where(mask,0,ratio.lo),np.where(mask,0,ratio.hi))
        local=imix(ratio,1,ltm);return imix(local,local.minimum_one(),hr)*ref
    bg=branch(get(2),get(0),get(5));fg=branch(get(3),get(1),get(6));out=imix(bg,fg,float(person))
    if not np.isfinite(out.lo).all()or not np.isfinite(out.hi).all():raise ValueError('Nonfinite interval result; unknown')
    return SemanticSetResult(out.lo,out.hi,tuple(input_branches))


def from_consumer_fields(inputs: SemanticInputs,fields):
    """Carry the complete contract/unknown branch state, never just its center."""
    return forward_set(inputs,fields.output_lower[33:40],fields.output_upper[33:40],input_branches=fields.branch_decisions)
