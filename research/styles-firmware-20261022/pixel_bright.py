"""Complete AIR10 renderBrightAndContrast with five explicit f32 stats fields.

Inputs are at original SSA400, which reads skin393, NOT highlight398. Reuses
skin transfer equations, polar transform, contrast and RichSat leaf models.
"""
from dataclasses import dataclass
import numpy as np
from leaf_numeric import V,hc,fc,mix,select
from pixel_leaves import H,F,dot,contrast
from pixel_color import to_polar,rich_sat
from pixel_skin import encode,decode


@dataclass(frozen=True)
class BrightStats:
    s2_4: V
    s3_4: V
    s5_0: V
    s6_6: V
    s6_4: V

    def __post_init__(self):
        values=[self.s2_4,self.s3_4,self.s5_0,self.s6_6,self.s6_4]
        if any(not isinstance(v,V)or v.precision!='f'or np.shape(v.lo)!=()for v in values):raise TypeError('Five explicit scalar f32 SSRGlobalStats fields required')
        if any(v.point!=values[0].point for v in values):raise TypeError('Stats point/set backends must match')


def smooth(x):return (x*x)*(3-2*x)


def forward(rgb,working,person,skin,exposure,stats: BrightStats):
    if not isinstance(stats,BrightStats):raise TypeError('Raw supplied stats fields required; no frame-stat estimation')
    if stats.s2_4.point!=rgb.point:raise TypeError('Working inputs and stats must share the point/set contract')
    c=rgb.clamp();w=working.clamp();a=stats.s2_4.h();b=stats.s3_4.h()
    tone=mix(H(1,rgb),H(hc('3266'),rgb),smooth(((a+H(hc('ae66'),rgb))*H(hc('41b6'),rgb)).clamp()))
    ratio=a/b.maximum(H(hc('1419'),rgb))
    spread=(((stats.s6_6-stats.s6_4).h()*H(hc('4d00'),rgb)).f()-2).clamp().h()
    ev=(exposure.f()*F(.25,rgb)-F(1.5,rgb)).clamp().h()
    ratio_shape=ratio.f()*F(4,rgb)-F(9,rgb);base=ratio_shape.clamp(1,3).h();factor=spread.minimum(ev)
    strength=((factor.f()*F(3,rgb)+1)*base.f()).maximum(1).h()
    gain=((exposure.f()*F(4,rgb))*F(2,rgb).pow(tone.f()*F(fc('3FEB333340000000'),rgb))).h()
    primary=mix(c,(gain*w).clamp(),H(hc('34cd'),rgb)).clamp()*H(hc('3c36'),rgb)+H(hc('2666'),rgb)
    weight=mix(H(hc('34cd'),rgb),H(hc('3666'),rgb),smooth(((strength-1)*H(.5,rgb)).clamp()))
    primary=mix(primary,1-H(2,rgb).pow(primary*H(hc('c600'),rgb)),weight)
    protection=smooth(((c.sum_channels()+H(hc('b8cd'),rgb))*H(hc('4100'),rgb)).clamp())
    curved=encode(primary);reference=encode(c)
    chroma=curved.square().sum_channels()/curved.sum_channels()
    luminance=dot(curved,[hc('399a'),hc('3266'),hc('2e66')])
    mixture=mix(mix(chroma,luminance,person),curved,((1-protection.f())*F(fc('3FEE680000000000'),rgb)).h())
    square=mix(reference,reference.square(),(strength*H(hc('2e66'),rgb)).clamp(0,hc('359a')))
    low=(((square*H(hc('4c00'),rgb)+H(hc('ca00'),rgb))*square)+H(4,rgb))*square
    shaped=select(square.le(H(hc('3400'),rgb)),low,square.sqrt())
    delta=select(mixture.le(H(.5,rgb)),(1-square)*square,shaped-square)
    adjusted=(delta*(mixture*H(2,rgb)-1)+square).clamp()
    target=decode(mix(square,adjusted,H(hc('399a'),rgb)));reference=decode(reference)
    changed=mix(reference,target,H(hc('399a'),rgb))
    _,angle,_=to_polar(changed);angle=angle+H(hc('bc88'),rgb)
    region=((angle.square()*H(hc('c449'),rgb)).exp().f()).clamp().h()
    contrasted=contrast(changed,H(hc('34cd'),rgb))
    enhanced=mix(changed,changed.maximum(contrasted),region)
    original_mix=mix(reference,target,H(hc('34cd'),rgb));enhanced=mix(original_mix,enhanced,person)
    scale=((1-factor.f()*F(fc('3FE6666660000000'),rgb))*(1-ratio_shape.clamp()*F(fc('3FE3333340000000'),rgb)).h().f()).h()
    complement=(1-stats.s5_0).h();working_ratio=working/gain
    gray=(dot(working_ratio,[hc('32d1'),hc('39b8'),hc('2c9c')]).f()+F(fc('3F1A36E2E0000000'),rgb)).minimum(1)
    blend=((exposure.f()*F(.5,rgb))*gray).h()
    blend=smooth(((blend+H(hc('b266'),rgb))*H(2,rgb)).clamp()).pow(H(hc('3746'),rgb)).clamp()
    curve=working_ratio.pow(H(1,rgb));base=complement.f().pow(F(1,rgb)).h()
    curve=(curve/(base+curve)).clamp().pow(H(hc('3f33'),rgb))
    changed=mix(enhanced,mix(enhanced,curve,blend),(scale.f()*F(.5,rgb)).clamp().h())
    changed=mix(enhanced,changed,skin)
    a=rich_sat(changed,H(hc('3c66'),rgb),H(3,rgb));b=rich_sat(changed,H(hc('3c14'),rgb),H(3,rgb))
    out=mix(a,b,((skin+person).f()*F(.5,rgb)).clamp().h()).clamp()
    return ((rgb.maximum(1)-1)+rgb.minimum(0))+out
