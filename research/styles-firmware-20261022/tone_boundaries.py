"""Finite-domain AIR11 branch ownership and set-valued coefficient contract.

Pow intervals reuse the S7 4u host assumption. Unknown branch means set coverage,
never native numerical agreement or permission to silently render its center.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from negative_tone import B,h,k,power,clamp


@dataclass(frozen=True)
class BranchDecision:
    name: str
    predicate: str
    threshold_f32: float
    operand_f32_lower: float
    operand_f32_upper: float
    state: str  # true / false / undetermined
    equality_branch: str
    affected_flat_fields: tuple[int,...]


def decide(name,predicate,low,high,threshold,fields):
    """low/high are possible post-pow *f32* values, not unrounded arguments."""
    if predicate=='olt':yes=high<threshold;no=low>=threshold;equality='false'
    elif predicate=='ole':yes=high<=threshold;no=low>threshold;equality='true'
    elif predicate=='ugt':yes=low>threshold;no=high<=threshold;equality='false'
    elif predicate=='oge':yes=low>=threshold;no=high<threshold;equality='true'
    else:raise ValueError('Reviewed finite-domain predicate required')
    return BranchDecision(name,predicate,float(threshold),float(low),float(high),'true'if yes else 'false'if no else 'undetermined',equality,tuple(fields))


def possible_f32(interval: B):
    lo=np.float32(interval.lo);hi=np.float32(interval.hi)
    if float(lo)<interval.lo:lo=np.nextafter(lo,np.float32(np.inf))
    if float(hi)>interval.hi:hi=np.nextafter(hi,np.float32(-np.inf))
    return float(lo),float(hi)


def positive_decisions(tone: float) -> tuple[BranchDecision,...]:
    t=float(np.float32(tone))
    if not np.isfinite(t)or not 0<=t<=1:raise ValueError('Finite positive/zero tone domain required')
    q=possible_f32(power(B(t),h('3FF3333340000000')));r=possible_f32(power(B(t),.75))
    return (decide('BG.q_lighten','ugt',*q,h('3FDBDB8CE0000000'),[9]),
            decide('FG.r_mids','olt',*r,.5,[19]),
            decide('FG.t_whites','ole',t,t,.5,[21]),
            decide('FG.t_shadows_contrast_neck','olt',t,t,h('3FD99999A0000000'),[23,24,32]))


def negative_decisions(context) -> tuple[BranchDecision,...]:
    values=context.stats.values();g95,g96=values[6:8]
    a294=clamp(g95*20+k(.6));a298=clamp(g96*h('40148346E0000000')+h('BF9A36E2E0000000'))
    a302=1+(a298-1)*(1-a294)
    return (decide('negativeFG.a302','oge',*possible_f32(a302),1.,[23,24]),)
