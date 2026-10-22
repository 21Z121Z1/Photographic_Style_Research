"""All positive/zero AIR11 Tone coefficients, with explicit supplied context.

The 38 newly covered fields use the existing negative-Tone interval arithmetic.
FG9/10 call the accepted positive_tone_skin implementation; they are excluded
from the new native comparison. This is not a pixel renderer or GPU proof.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from numpy.typing import NDArray
from negative_tone import B,box,k,h,clamp,min_b,max_b,mix,power,select_ge
from positive_tone_skin import coefficients as accepted_skin_coefficients


@dataclass(frozen=True)
class PositiveToneStats:
    slot0_field6: float
    slot5_field6: float
    slot6_field5: float

    def values(self):
        a=np.array([self.slot0_field6,self.slot5_field6,self.slot6_field5],dtype='f4')
        if not np.isfinite(a).all()or np.any(a<0)or np.any(a>16):
            raise ValueError('Positive Tone needs three finite nonnegative stats slots <=16')
        return [B(float(x))for x in a]


@dataclass(frozen=True)
class PositiveToneContext:
    stats: PositiveToneStats
    tone_tuning: tuple[float,...]
    tuning_type: int=0  # SSRParams byte652, distinct from sceneType at byte32.
    cast_code: int=0
    scene_brightness: float=0.
    baseline_exposure_field7: float=1.

    def validate(self):
        a=np.array(self.tone_tuning,dtype='f4')
        other=np.array([self.scene_brightness,self.baseline_exposure_field7],dtype='f4')
        if a.shape!=(66,)or not np.isfinite(a).all()or np.max(abs(a))>16:
            raise ValueError('66 finite tone-tuning scalars with absolute value <=16 required')
        if not np.isfinite(other).all()or np.max(abs(other))>16:
            raise ValueError('Finite brightness/reference budget <=16 required')
        if any(type(x)is not int or not 0<=x<=255 for x in (self.tuning_type,self.cast_code)):
            raise ValueError('Explicit bounded integer tuningType/cast codes required')
        if self.tuning_type==4 and abs(float(a[29])-float(a[30]))<2**-8:
            raise ValueError('Scene4 tuning thresholds need a separated nonzero denominator')
        return [B(float(x))for x in a],[B(float(x))for x in other]


@dataclass(frozen=True)
class PositiveToneResult:
    background: NDArray[np.float64]
    foreground: NDArray[np.float64]
    semantic: NDArray[np.float64]
    host_f32_absolute_allowance: NDArray[np.float64]
    native_GPU_verified: bool=False
    original_stats_recovered: bool=False

    def values(self):return np.r_[self.background,self.foreground,self.semantic]


def select_gt(condition: B,threshold: float,a: B,b: B) -> B:
    """Strict comparison with both branches retained if rounding can cross it."""
    threshold=k(threshold)
    if condition.lo>threshold:return a
    if condition.hi<=threshold:return b
    v=a.v if condition.v>threshold else b.v
    return B(v,max(v-min(a.lo,b.lo),max(a.hi,b.hi)-v))


def coefficients(tone: float,context: PositiveToneContext) -> PositiveToneResult:
    tv=k(tone)
    if not np.isfinite(tv)or not 0<=tv<=1:raise ValueError('Positive/zero supplied SSR tone domain [0,1]')
    t=B(tv);tun,(brightness,reference)=context.validate();g06,g56,g65=context.stats.values()
    # Same actual indexed base4 selection as negative branch; no inferred scene
    # labels, UI mapping, statistics regeneration or physical units are supplied.
    start={2:47,3:35,5:39,6:43,7:55,8:51}.get(context.tuning_type,21)
    base=tun[start:start+4]
    if context.tuning_type==4:
        weight=clamp((brightness-tun[30])/(tun[29]-tun[30]))
        base=[mix(tun[31+i],tun[25+i],weight)for i in range(4)]
    base122,base121,base120,base119=base
    q=power(t,h('3FF3333340000000'))
    a201=max_b(q*2*tun[14],tun[14])+base122
    a206=min_b(max_b(q+h('BFD99999A0000000'),0)+base120,h('3FE99999A0000000'))
    a216=min_b(max_b(q*h('3FC5566D00000000')+h('BFB1134040000000'),0)+base121,h('3FC99999A0000000'))
    left=q*.875;right=min_b(q*h('3FC432CA60000000')+h('3FD3FB15C0000000'),h('3FDE147AE0000000'))
    a227=select_gt(q,h('3FDBDB8CE0000000'),right,left)
    a229=min_b(a227+base119,h('3FECCCCCC0000000'))
    bg=[min_b(q*h('3FF2666660000000'),h('3FDD70A3E0000000')),a201,box(0),box(0),
        min_b(q*.5,.5),q*h('BFD6666660000000'),q*-.25,a206,a216+1,a229,
        min_b(q*h('3FECCCCCC0000000'),h('3FDCCCCCC0000000')),1+(q*-.25)*.5,
        box(0),box(0),box(0),box(0),box(1)]
    r=power(t,.75);quarter=t*.25
    a346=select_ge(r,.5,r*h('3FF3333340000000')-.5,r*.5)
    a349=r*(.5 if tv<=.5 else h('3FE3333340000000'))
    low=tv<h('3FD99999A0000000')
    a354=t*h('3FDCCCCCC0000000')if low else t*h('3FC99999A0000000')+h('3FB99999A0000000')
    a357=quarter if low else h('3FC5557140000000')-t*h('3FC5557140000000')
    a361=t*-.5 if low else t*h('3FD54FDF40000000')+h('BFD54FDF40000000')
    old=accepted_skin_coefficients(tv)  # Reuse, no new polynomial implementation.
    td=float(tv);u=2**-24;gamma=3*u/(1-3*u)
    old9=B(float(old.theta9),gamma*(2.75*td+3.75*td*td)+3*2**-126)
    old10=B(float(old.theta10),gamma*(.20829999446868896*td*td+.708299994468689*td)+3*2**-126)
    fg=[min_b(h('3FC99999A0000000')-t*h('3FBC28F5C0000000'),1),quarter,a346,
        min_b(r,h('3FE3333340000000')),a349,1+quarter*.5,a354,a357,box(0),old9,old10,
        t*h('3FD99999A0000000')*tun[11],box(0),box(0),box(-.25 if context.cast_code==14 else 0),a361]
    a534=max_b(1-t*h('3FE3333340000000'),h('3FE6666660000000'))
    a538=clamp(g56*2.5+h('3FE19999A0000000'),h('3FE99999A0000000'),1)
    a543=clamp((g06-g56)*h('4006666660000000')+h('BFF9EB8520000000'),h('3FAEB851E0000000'),h('3FC99999A0000000'))
    a545=max_b(t*h('BFF3333340000000'),h('BFEB333340000000'))
    a553=clamp(g65*10*(1-tun[12])+tun[12],h('3FE99999A0000000'),1)
    a557=max_b(1+a545*a538*a553,a543)
    a564=(1-power(t,h('3FE19999A0000000'))*(1-tun[13]))*reference
    sem=[a534,a557,reference,a564,max_b(1-t,h('3FC99999A0000000')),box(1),box(1)]
    all_=bg+fg+sem
    return PositiveToneResult(np.array([x.v for x in bg]),np.array([x.v for x in fg]),np.array([x.v for x in sem]),np.array([x.e for x in all_]))
