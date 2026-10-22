"""Conditional negative-Tone BG/FG/semantic coefficients from actual AIR11.

The three negative branches of RenderingParamsFromStats are modeled on supplied
f32 stats/tuning context. This is coefficient generation, not pixel rendering,
UI Tone/EV calibration or recovery of original capture statistics. Positive
Tone and the existing skin/inverse models remain unchanged.
"""
from __future__ import annotations
from dataclasses import dataclass
import math
import struct
import numpy as np
from numpy.typing import NDArray


def k(value: float) -> float:return float(np.float32(value))
def h(bits: str) -> float:return struct.unpack('>d',bytes.fromhex(bits))[0]


@dataclass(frozen=True)
class B:
    """Continuous center plus conservative host-f32 allowance.

    Each arithmetic op allows 2u rounding/contraction; pow uses an explicit
    assumed 4u host-libm allowance. This is NOT an Apple GPU fast_pow proof.
    """
    v: float
    e: float=0.
    @property
    def lo(self):return self.v-self.e
    @property
    def hi(self):return self.v+self.e
    def __add__(self,other):
        b=box(other);v=self.v+b.v;e=self.e+b.e;return B(v,e+2**-23*(abs(v)+e)+2**-149)
    __radd__=__add__
    def __neg__(self):return B(-self.v,self.e)
    def __sub__(self,other):return self+-box(other)
    def __rsub__(self,other):return box(other)+-self
    def __mul__(self,other):
        b=box(other);v=self.v*b.v;e=abs(self.v)*b.e+abs(b.v)*self.e+self.e*b.e
        return B(v,e+2**-23*(abs(v)+e)+2**-149)
    __rmul__=__mul__
    def __truediv__(self,other):
        b=box(other)
        if b.lo<=0<=b.hi:raise ValueError('Denominator interval includes zero')
        vals=[a/d for a in (self.lo,self.hi)for d in (b.lo,b.hi)];v=self.v/b.v
        e=max(abs(v-min(vals)),abs(max(vals)-v));return B(v,e+2**-23*max(map(abs,vals))+2**-149)


def box(x):return x if isinstance(x,B)else B(k(x))
def clamp(x,lo=0.,hi=1.):
    x=box(x);lo=k(lo);hi=k(hi);v=min(max(x.v,lo),hi)
    return B(v,max(v-min(max(x.lo,lo),hi),min(max(x.hi,lo),hi)-v))
def min_b(x,cap):
    x=box(x);cap=k(cap);v=min(x.v,cap);return B(v,max(v-min(x.lo,cap),min(x.hi,cap)-v))
def max_b(x,floor):
    x=box(x);floor=box(floor);v=max(x.v,floor.v)
    return B(v,max(v-max(x.lo,floor.lo),max(x.hi,floor.hi)-v))
def mix(a,b,w):return box(a)+(box(b)-box(a))*box(w)
def power(x,exponent):
    x=box(x);exponent=k(exponent)
    if x.lo<0:raise ValueError('Negative power base interval')
    v=math.pow(x.v,exponent);a=math.pow(x.lo,exponent);b=math.pow(x.hi,exponent)
    return B(v,max(v-a,b-v)+2**-22*max(abs(a),abs(b))+2**-149)
def select_ge(condition,threshold,a,b):
    condition=box(condition);a=box(a);b=box(b);threshold=k(threshold)
    if condition.lo>=threshold:return a
    if condition.hi<threshold:return b
    v=a.v if condition.v>=threshold else b.v
    return B(v,max(v-min(a.lo,b.lo),max(a.hi,b.hi)-v))


@dataclass(frozen=True)
class ToneStats:
    # Exact SSRGlobalStats slot/field labels; physical units are not inferred.
    slot0_field4: float
    slot1_field4: float
    slot5_field4: float
    slot6_field4: float
    slot5_field6: float
    slot6_field6: float
    slot9_field5: float
    slot9_field6: float
    stats_field4: float

    def values(self):
        a=np.array(list(self.__dict__.values()),dtype='f4')
        if not np.isfinite(a).all()or np.any(a[:8]<0)or np.any(a[:8]>16)or abs(a[8])>16:
            raise ValueError('Finite nonnegative stats slots <=16; finite blend input <=16')
        return [B(float(x))for x in a]


@dataclass(frozen=True)
class NegativeToneContext:
    stats: ToneStats
    tone_tuning: tuple[float,...]
    scene_code: int=0
    cast_code: int=0
    scene_brightness: float=0.
    blend_low: float=0.
    blend_high: float=1.
    foreground_modulation_input: float=1.
    semantic_reference_field7: float=1.

    def validate(self):
        a=np.array(self.tone_tuning,dtype='f4')
        if a.shape!=(66,)or not np.isfinite(a).all()or np.max(abs(a))>16:raise ValueError('66 finite tone-tuning scalars required')
        other=np.array([self.scene_brightness,self.blend_low,self.blend_high,self.foreground_modulation_input,self.semantic_reference_field7],dtype='f4')
        if not np.isfinite(other).all()or np.max(abs(other))>16 or other[2]-other[1]<2**-8:raise ValueError('Finite context and separated increasing blend thresholds required')
        if not isinstance(self.scene_code,int)or not 0<=self.scene_code<=255 or not isinstance(self.cast_code,int)or not 0<=self.cast_code<=255:raise ValueError('Explicit bounded scene/cast codes required')
        if self.scene_code==4 and abs(float(a[29])-float(a[30]))<2**-8:raise ValueError('Scene4 tuning thresholds need a separated nonzero denominator')
        return [B(float(x))for x in a],[B(float(x))for x in other]


@dataclass(frozen=True)
class NegativeToneResult:
    background: NDArray[np.float64]
    foreground: NDArray[np.float64]
    semantic: NDArray[np.float64]
    host_f32_absolute_allowance: NDArray[np.float64]
    native_GPU_verified: bool=False
    original_stats_recovered: bool=False

    def values(self):return np.r_[self.background,self.foreground,self.semantic]


def coefficients(tone: float,context: NegativeToneContext) -> NegativeToneResult:
    tv=k(tone)
    if not -1<=tv<=-2**-24:raise ValueError('Declared negative Tone domain [-1,-2^-24]; zero/positive use prior model')
    t=B(tv);tun,(scene,low,high,modulation,reference)=context.validate()
    g0,g1,g5,g6,g56,g66,g95,g96,statblend=context.stats.values();eps=k(1e-6)
    blend=clamp((statblend-low)/(high-low));blend=blend*blend*(3-2*blend)
    # Scene-specific base4. Scene4 interpolates tuning[31..34] -> [25..28].
    start={2:47,3:35,5:39,6:43,7:55,8:51}.get(context.scene_code,21)
    base=tun[start:start+4]
    if context.scene_code==4:
        weight=clamp((scene-tun[30])/(tun[29]-tun[30]))
        base=[mix(tun[31+i],tun[25+i],weight)for i in range(4)]
    base122,base121,base120,base119=base
    ratio=(g0+eps)/(g5+eps);p=power(-t,1.2)
    c136=clamp(1.5-(g1+eps)*k(.1)/(g6+eps),.5,1)
    c139=clamp(g96*100,.5,1)
    # Original hex constants are loaded below to avoid decimal approximation.
    c143=clamp(g96*h('402AAA7F00000000')+h('BFB1134040000000'))
    q=clamp(ratio*.5-2.5)
    m150=1+q*(c139-1);m153=1+q*(c143-1)
    c155=m150*(p*-.5);c156=p*k(.4);c159=c136*(p*.5)*m153
    c162=m150*(p*k(.2))+base122
    c167=clamp(k(1.2)-ratio*k(.1),.5,.7);c170=clamp(g56*100,.5,1)
    bg=[mix(c167*(p*.5),c159,blend),mix(c170*(p*k(.2))+base122,c162,blend),box(0),mix(c170*(p*-.5),c155,blend),box(0),box(0),box(0),base120,base121+1,base119,c156,box(1),box(0),box(0),box(0),box(0),box(1)]
    # Foreground negative branch267; positive theta9/10 logic is not copied.
    c290=clamp(k(1.1)-(g1+eps)*k(.06)/(g6+eps),.5,.8)
    c294=clamp(g95*20+k(.6))
    c298=clamp(g96*h('40148346E0000000')+h('BF9A36E2E0000000'))
    c302=1+(c298-1)*(1-c294);c306=clamp(select_ge(c302,1,c302,c294),.6,1)
    c310=clamp(g96*h('402AAA7F00000000')+h('BFB1134040000000'))
    c315=clamp((g0+eps)*.5/(g5+eps)-2.5)
    c318=1+c315*(c306-1);c321=1+c315*(c310-1);root=power(-t,.4)
    sm=clamp((modulation-k(1.8))*h('4013FFFFC0000000'));sm=sm*sm*(3-2*sm)
    weight=mix(.5,k(.1),sm);signed=c318*t
    fg=[box(0),box(0),box(0),box(0),c290*k(.3)*root*c321,box(1),signed*weight,signed*k(-.2),box(0),box(0),box(0),box(0),box(0),box(0),box(-.25 if context.cast_code==14 else 0),root*k(.6)]
    # Semantic negative branch419; reference is an explicit field, not gain/EV.
    a440=clamp(g96*80+k(.2),.6,1);a444=clamp(ratio*.5-2.5);a448=clamp(g56*10)*a444
    a453=clamp(k(1.2)-(g1+eps)*k(.1)/(g6+eps),.5,.7)
    a456=1+a448*(a440-1);a457=a456*a453
    a458=reference*k(1.3);a462=clamp(k(3.4)-g96*160,1,2.6);a465=1+(a462-1)*a448
    a466=a458/a465;a467=a466*a465
    a471=clamp(g96*100-.5,.5,1);a474=1+(a471-1)*a448
    a479=clamp(max_b(g96,g66)*h('402638D500000000')+h('BFBC710CC0000000'))
    a482=1+a479*(a457-1);amount=-t
    first=[mix(1,a457,amount),mix(1,a457,amount),mix(reference,a467,amount),mix(reference,a466,amount),mix(1,a474,amount),mix(1,a457,amount),mix(1,a482,amount)]
    a492=clamp(k(1.2)-ratio*k(.1),.5,.7);a496=clamp(k(1.6)-g56*60,1,1.3);a499=1+(a496-1)*a448;a500=a458/a499
    second=[mix(1,a492,amount),box(1),mix(reference,a500,amount),reference,box(1),mix(1,.7,amount),box(1)]
    sem=[mix(a,b,blend)for a,b in zip(second,first)]
    all_=bg+fg+sem
    return NegativeToneResult(np.array([x.v for x in bg]),np.array([x.v for x in fg]),np.array([x.v for x in sem]),np.array([x.e for x in all_]))
