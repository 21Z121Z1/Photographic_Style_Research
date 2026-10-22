"""Point-only BG/FG connection model for explicitly supplied exact f32 fields.

This is NOT an adapter for uncertain producer coefficients. The existing set
controller remains independent and fail closed, including boundary unions.
"""
from dataclasses import dataclass
import numpy as np
from leaf_numeric import V,fc,hc,mix,DomainUnknown
from pixel_leaves import H,F,whites_curve,contrast,airy
from pixel_tonal import shadows,shadows_negative
from pixel_lighten import lighten,negative_lighten
from pixel_color import smooth_sat,rich_sat
from pixel_remaining import under_grass,under_tone,tonal_contrast,smart_contrast,highlight_neg,local_contrast,gamma_contrast
from bgfg_tone import GATE,mids_half


@dataclass(frozen=True)
class ExactHelperFields:
    block: str
    values: np.ndarray
    origin: str

    def __post_init__(self):
        if self.block not in ('bg','fg'):raise ValueError('Exact BG or FG field block required')
        if not isinstance(self.values,np.ndarray)or self.values.dtype!=np.dtype('f4')or self.values.shape!=((17,)if self.block=='bg'else(16,)):raise TypeError('Explicit f32 vector of exactly 17 BG or 16 FG fields required; no producer-center adapter')
        if not np.isfinite(self.values).all()or np.any(abs(self.values)>8):raise ValueError('Finite explicit field domain abs<=8 required')
        if not isinstance(self.origin,str)or not self.origin.strip():raise ValueError('Exact input provenance required')
        v=self.values.copy();v.setflags(write=False);object.__setattr__(self,'values',v)


def forward(rgb,semantic,fields: ExactHelperFields,*,guide,person,skin,whites):
    if not isinstance(fields,ExactHelperFields):raise TypeError('Uncertain producer values cannot enter the fixed-field point model')
    for x in [rgb,semantic,guide,person,skin]:
        if not isinstance(x,V)or not x.point or x.precision!='h':raise TypeError('Explicit half point inputs required; no interval-center conversion')
    if rgb.lo.shape!=(3,)or semantic.lo.shape!=(3,):raise ValueError('RGB vector inputs required')
    if any(x.lo.shape!=()or x.lo<0 or x.lo>1 for x in [guide,person,skin]):raise ValueError('Guide/person/skin half scalars in [0,1] required')
    p=[F(x,rgb)for x in fields.values]
    active=lambda x:bool(x.abs().lo>=GATE)
    def apply(fn,x,amount,gate=None):return fn(x,amount.h())if active(amount if gate is None else gate)else x
    def with_guide(fn,x,amount,gate=None):return apply(lambda c,a:fn(c,guide,a),x,amount,gate)
    def shadow(x,amount):return with_guide(shadows if amount.lo>0 else shadows_negative,x,amount)
    def light(x,value):
        gate=value*F(.5,rgb)
        if gate.lo>0:x=with_guide(shadows,x,gate)
        if not active(gate):return x
        if gate.lo>0:return with_guide(lighten,x,value*F(.75,rgb),gate)
        amount=(1-value*F(.75,rgb));amount=amount.h().abs()if fields.block=='bg'else amount.abs().h()
        return negative_lighten(x,guide,amount)
    if fields.block=='bg':
        x=shadow(rgb,p[3]);x=apply(contrast,x,p[1])
        x=apply(lambda c,a:whites_curve(c,a,whites,H(0,c)),x,p[0])
        x=apply(airy,x,p[11],p[11]-1);x=apply(lambda c,a:V.value(mids_half(c.lo,a.lo)),x,p[7])
        x=apply(smooth_sat,x,p[8],p[8]-1);x=with_guide(local_contrast,x,p[5]);x=with_guide(gamma_contrast,x,p[4]);x=light(x,p[9])
        x=apply(lambda c,a:under_grass(c,person,a),x,p[10]);gate=p[2]*F(.5,rgb)
        if active(gate):x=rich_sat(x,(p[2]+1).h(),H(3,rgb))if (gate+1).lo>1 else smooth_sat(x,(gate+1).h())
        return x
    initial=mix(rgb,semantic,((1-p[0])*person.f()).h());x=initial
    x=apply(lambda c,a:whites_curve(c,a,whites,H(1,c)),x,p[4]);x=shadow(x,p[6])
    x=apply(lambda c,a:tonal_contrast(c,skin,a),x,p[15]);x=apply(contrast,x,p[7])
    if active(p[11]):x=rich_sat(x,(p[11]+1).h(),H(3,rgb))if p[11].lo>0 else smooth_sat(x,(p[11]+1).h())
    x=apply(airy,x,p[5],p[5]-1);x=apply(lambda c,a:V.value(mids_half(c.lo,a.lo)),x,p[2])
    x=apply(lambda c,a:under_tone(c,skin,a),x,p[14]);x=light(x,p[3])
    if active(p[8]):
        if p[8].lo>0:x=highlight_neg(x,guide,(p[8]*F(fc('BFCC28F5C0000000'),rgb)).h())
        x=smart_contrast(x,guide,p[8].h())
    return mix(initial,x,person)
