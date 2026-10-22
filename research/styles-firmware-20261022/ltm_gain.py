"""AIR7 SSA99..205 gain production, conditional on upstream sampled colors.

This is the per-pixel producer core, before the actual guided filter. It does
not claim that supplied reference96/linear98 have been recovered from a photo.
"""
from dataclasses import dataclass
import numpy as np
from leaf_numeric import V,vec,lazy_select,mix,hc
from pixel_leaves import H,curve_sample


@dataclass(frozen=True)
class Parameters:
    linear_CCM_columns: V
    scale6: V
    semantic7: V

    def __post_init__(self):
        fields=[self.linear_CCM_columns,self.scale6,self.semantic7]
        if any(not isinstance(x,V)or x.precision!='f'for x in fields)or [x.lo.shape for x in fields]!=[(3,3),(),(7,)]or any(x.point!=fields[0].point for x in fields):raise TypeError('Matching f32 CCM columns3x3, scale6 scalar and semantic7 required')


@dataclass(frozen=True)
class Result:
    bg203: V
    fg205: V
    transformed_linear121: V
    input_reference96: V
    guided_filter_applied: bool=False


def guarded_ratio(numerator,reference):
    eps=hc('1c04');result=[]
    for i in range(3):
        r=reference[i]
        def divide(r=r,i=i):
            # On the original nonzero side, half(ref-EPS)>=0 implies
            # ref>=EPS. Adjacent half values differ by at least one subnormal,
            # so subtraction cannot round a smaller half to signed zero here.
            active=r if r.point else V(np.maximum(r.lo,eps),r.hi,'h',False)
            return numerator[i]/active
        result.append(lazy_select((r+H(hc('9c04'),r)).lt(0),lambda:H(0,r),divide))
    return vec(result)


def forward(reference96,linear98,parameters: Parameters,curve):
    if any(not isinstance(x,V)or x.precision!='h'or x.lo.shape!=(3,)for x in [reference96,linear98])or reference96.point!=linear98.point or parameters.scale6.point!=reference96.point:raise TypeError('Matching half reference96/linear98 and parameter backend required')
    p=parameters.semantic7.h();c=parameters.linear_CCM_columns.h()
    # Original SSA112 is G product + R product, then B; do not transpose CCM.
    working=((linear98[1]*c[1]+linear98[0]*c[0])+linear98[2]*c[2])*parameters.scale6.h()
    def branch(exposure):
        scaled=(working*exposure).minimum(1)
        mapped=mix(scaled,curve_sample(scaled,curve),p[4])
        return guarded_ratio(mapped,reference96)
    return Result(branch(p[2]),branch(p[3]),working,reference96)
