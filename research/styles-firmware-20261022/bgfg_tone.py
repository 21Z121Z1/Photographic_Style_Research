"""Separate BG/FG helper order/gates and a shared mids set operator.

Missing leaf models return unknown with their input set; they never silently
pass through, render a coefficient center, or certify the complete helper.
External leaf providers must implement the supplied set contract themselves.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable
import numpy as np
from negative_tone import h
from semantic_tone import I,imix

GATE=h('3EE4F8B580000000')


def mids_half(rgb,amount):
    cast=lambda x:np.asarray(x,dtype='f2')
    rgb=cast(rgb);c=np.clip(rgb,cast(0),cast(1));maximum=np.max(c);root=cast(np.sqrt(maximum))
    gain=cast(cast(1)+cast(cast(cast(1)-root)*cast(amount)))
    return cast(cast(cast(np.minimum(rgb,cast(0))-cast(1))+np.maximum(rgb,cast(1)))+np.clip(cast(c*gain),cast(0),cast(1)))


def clip(x,lo,hi):return I(np.clip(x.lo,lo,hi),np.clip(x.hi,lo,hi))
def half(x):return I.half_cast(x.lo,x.hi)


def mids_set(rgb: I,amount: I) -> I:
    """Complete inline mids expression shared by BG and FG (AIR10)."""
    c=clip(rgb,0,1);maximum=I(np.max(c.lo),np.max(c.hi))
    root=I(np.sqrt(maximum.lo),np.sqrt(maximum.hi)).widen()
    gain=1+(1-root)*half(amount);changed=clip(c*gain,0,1)
    exterior=I(np.minimum(rgb.lo,0),np.minimum(rgb.hi,0))+I(np.maximum(rgb.lo,1),np.maximum(rgb.hi,1))-1
    return exterior+changed


def fadd(x: I,value: float):
    lo=x.lo+value;hi=x.hi+value;e=np.maximum(abs(lo),abs(hi))*2**-23+2**-149
    return I(lo-e,hi+e)


def fscale(x: I,value: float):
    a=x.lo*value;b=x.hi*value;lo=np.minimum(a,b);hi=np.maximum(a,b);e=np.maximum(abs(lo),abs(hi))*2**-23+2**-149
    return I(lo-e,hi+e)


def active(x: I):
    maximum=max(abs(float(x.lo)),abs(float(x.hi)));minimum=0 if x.lo<=0<=x.hi else min(abs(float(x.lo)),abs(float(x.hi)))
    return 'skip'if maximum<GATE else 'run'if minimum>=GATE else 'undetermined'


def positive(x: I):return 'yes'if x.lo>0 else 'no'if x.hi<=0 else 'undetermined'


@dataclass(frozen=True)
class PixelContext:
    guide: float | I
    person_weight: float
    skin_weight: float=0.

    def validate(self):
        guide=self.guide if isinstance(self.guide,I)else I.point(float(np.float16(self.guide)))
        if not np.isfinite(guide.lo).all()or not np.isfinite(guide.hi).all()or np.any(guide.lo<0)or np.any(guide.hi>1)or np.any(guide.lo>guide.hi):raise ValueError('Supplied guide interval must stay in [0,1]; no center fallback')
        a=np.array([self.person_weight,self.skin_weight],dtype='f2')
        if not np.isfinite(a).all()or np.min(a)<0 or np.max(a)>1:raise ValueError('Supplied half guide/person/skin weights in [0,1] required')
        return guide,*a.astype('f8')


@dataclass(frozen=True)
class PixelResult:
    status: str
    output: I | None
    missing_operator: str | None
    missing_input_set: I | None
    trace: tuple
    input_branches: tuple
    full_helper_numeric_verified: bool=False


class MissingLeaf(Exception):
    def __init__(self,name,rgb):self.name=name;self.rgb=rgb


LeafProvider=Callable[[I,I,PixelContext],I]


def run(block: str,rgb: I,fields,context: PixelContext,*,semantic_rgb: I | None=None,leaf_models: dict[str,LeafProvider] | None=None) -> PixelResult:
    if block not in ('bg','fg'):raise ValueError('Explicit bg/fg helper required')
    guide,person,skin=context.validate();models={'mids':lambda x,p,c:mids_set(x,p),**(leaf_models or {})};trace=[]
    offset=0 if block=='bg'else 17;p=[I(fields.output_lower[offset+i],fields.output_upper[offset+i])for i in range(17 if block=='bg'else 16)]
    def apply(name,param,x,*,gate=None,only_positive=False):
        condition=param if gate is None else gate;state=active(condition)
        if only_positive:
            sign=positive(condition)
            if sign=='no':state='skip'
            elif sign=='undetermined'and state!='skip':state='undetermined'
        trace.append({'operator':name,'gate':state,'parameter_lower':float(param.lo),'parameter_upper':float(param.hi)})
        if state=='skip':return x
        if name not in models:raise MissingLeaf(name,x)
        out=models[name](x,half(param),context)
        if not isinstance(out,I):raise ValueError('Leaf providers must return output intervals, not centers')
        if not np.isfinite(out.lo).all()or not np.isfinite(out.hi).all()or np.any(out.lo>out.hi):raise ValueError('Invalid leaf output interval')
        if state=='undetermined':out=I(np.minimum(x.lo,out.lo),np.maximum(x.hi,out.hi))
        return out
    def signed(pos,neg,param,x,*,gate=None):
        if active(param if gate is None else gate)=='skip':return apply(pos,param,x,gate=gate)
        sign=positive(param)
        if sign=='undetermined':raise MissingLeaf(f'{pos}|{neg}: sign-set requires both models',x)
        return apply(pos if sign=='yes'else neg,param,x,gate=gate)
    def lighten(value,x):
        gate=fscale(value,.5);x=apply('ShadowsFilter',gate,x,gate=gate,only_positive=True)
        if active(gate)=='skip':return apply('lightenFilter',gate,x,gate=gate)
        sign=positive(gate)
        if sign=='undetermined':raise MissingLeaf('lightenFilter|negativeLightenFilter: sign set',x)
        amount=fscale(value,.75)
        if sign=='no':
            amount=fadd(fscale(amount,-1),1);amount=I(np.minimum(abs(amount.lo),abs(amount.hi)),np.maximum(abs(amount.lo),abs(amount.hi)))
        return apply('lightenFilter'if sign=='yes'else 'negativeLightenFilter',amount,x,gate=gate)
    try:
        if block=='bg':
            x=signed('ShadowsFilter','ShadowsNegativeFilter',p[3],rgb)
            x=apply('contrastFilter',p[1],x);x=apply('whitesCurve_BG_mode0',p[0],x)
            x=apply('airyFilter',p[11],x,gate=fadd(p[11],-1));x=apply('mids',p[7],x)
            x=apply('smoothSatFilter',p[8],x,gate=fadd(p[8],-1))
            x=apply('BG.localContrast_inline',p[5],x);x=apply('BG.gammaContrast_inline',p[4],x)
            x=lighten(p[9],x);x=apply('underGrassFilter',p[10],x)
            gate=fscale(p[2],.5)
            if active(gate)=='skip':x=apply('RichSat',gate,x,gate=gate)
            else:
                sign=positive(gate)
                if sign=='undetermined':raise MissingLeaf('RichSat|smoothSatFilter: sign set',x)
                x=apply('RichSat'if sign=='yes'else 'smoothSatFilter',fadd(p[2]if sign=='yes'else gate,1),x,gate=gate)
        else:
            if semantic_rgb is None:raise ValueError('FG requires the separate semantic RGB set for its initial blend')
            initial=imix(rgb,semantic_rgb,fscale(fadd(fscale(p[0],-1),1),person));x=initial
            x=apply('whitesCurve_FG_mode1',p[4],x);x=signed('ShadowsFilter','ShadowsNegativeFilter',p[6],x)
            x=apply('tonalContrastFilter',p[15],x);x=apply('contrastFilter',p[7],x)
            if active(p[11])=='skip':x=apply('RichSat',p[11],x)
            else:
                sign=positive(p[11])
                if sign=='undetermined':raise MissingLeaf('RichSat|smoothSatFilter: sign set',x)
                x=apply('RichSat'if sign=='yes'else 'smoothSatFilter',fadd(p[11],1),x,gate=p[11])
            x=apply('airyFilter',p[5],x,gate=fadd(p[5],-1));x=apply('mids',p[2],x)
            x=apply('underToneFilter',p[14],x);x=lighten(p[3],x)
            if active(p[8])!='skip'and positive(p[8])!='no':x=apply('highlightNeg',fscale(p[8],h('BFCC28F5C0000000')),x,gate=p[8],only_positive=True)
            x=apply('smartContrast',p[8],x);x=imix(initial,x,person)
        return PixelResult('computed_set',x,None,None,tuple(trace),fields.branch_decisions)
    except MissingLeaf as missing:
        return PixelResult('unknown_operator',None,missing.name,missing.rgb,tuple(trace),fields.branch_decisions)
