"""Reuse fixed point BG/FG controller, add whole-set control over existing leaves."""
from dataclasses import dataclass
import numpy as np
from leaf_numeric import V,lazy_select,hc,fc,mix
from pixel_leaves import H,F,whites_curve,contrast,airy
from pixel_tonal import shadows,shadows_negative
from pixel_lighten import lighten,negative_lighten
from pixel_color import smooth_sat,rich_sat
from pixel_remaining import under_grass,under_tone,tonal_contrast,smart_contrast,highlight_neg,local_contrast,gamma_contrast
from pixel_haze import mids
from bgfg_tone import GATE
from bgfg_fixed import ExactHelperFields,forward as fixed


@dataclass(frozen=True)
class Fields:
    bg17: V
    fg16: V

    def __post_init__(self):
        if any(not isinstance(x,V)or x.precision!='f'for x in [self.bg17,self.fg16])or self.bg17.lo.shape!=(17,)or self.fg16.lo.shape!=(16,)or self.bg17.point!=self.fg16.point:raise TypeError('Matching full f32 BG17/FG16 required, never centers')


def forward(block,rgb,semantic,fields: Fields,*,guide,person,skin,whites):
    values=fields.bg17 if block=='bg'else fields.fg16
    if block not in('bg','fg')or values.point!=rgb.point:raise TypeError('Exact block and matching field backend required')
    if rgb.point:return fixed(rgb,semantic,ExactHelperFields(block,values.lo.astype('f4'),'explicit typed f32 point fields'),guide=guide,person=person,skin=skin,whites=whites)
    if any(not isinstance(v,V)or v.point or v.precision!='h'for v in [rgb,semantic,guide,person,skin]):raise TypeError('Whole half input sets required')
    p=[values[i]for i in range(len(values.lo))]
    def apply(fn,x,amount,gate=None):return lazy_select((amount if gate is None else gate).abs().lt(F(GATE,rgb)),lambda:x,lambda:fn(x,amount.h()))
    def with_guide(fn,x,amount,gate=None):return apply(lambda c,a:fn(c,guide,a),x,amount,gate)
    def shadow(x,amount):return apply(lambda c,a:lazy_select(amount.gt(F(0,rgb)),lambda:shadows(c,guide,a),lambda:shadows_negative(c,guide,a)),x,amount)
    def light(x,value):
        gate=value*F(.5,rgb)
        x=lazy_select(gate.gt(F(0,rgb)),lambda:with_guide(shadows,x,gate),lambda:x)
        return lazy_select(gate.abs().lt(F(GATE,rgb)),lambda:x,lambda:lazy_select(gate.gt(F(0,rgb)),lambda:lighten(x,guide,(value*F(.75,rgb)).h()),lambda:negative_lighten(x,guide,((1-value*F(.75,rgb)).h().abs()if block=='bg'else(1-value*F(.75,rgb)).abs().h()))))
    if block=='bg':
        x=shadow(rgb,p[3]);x=apply(contrast,x,p[1]);x=apply(lambda c,a:whites_curve(c,a,whites,H(0,c)),x,p[0]);x=apply(airy,x,p[11],p[11]-1);x=apply(mids,x,p[7]);x=apply(smooth_sat,x,p[8],p[8]-1);x=with_guide(local_contrast,x,p[5]);x=with_guide(gamma_contrast,x,p[4]);x=light(x,p[9]);x=apply(lambda c,a:under_grass(c,person,a),x,p[10]);gate=p[2]*F(.5,rgb)
        return lazy_select(gate.abs().lt(F(GATE,rgb)),lambda:x,lambda:lazy_select((gate+1).gt(F(1,rgb)),lambda:rich_sat(x,(p[2]+1).h(),H(3,rgb)),lambda:smooth_sat(x,(gate+1).h())))
    initial=mix(rgb,semantic,((1-p[0])*person.f()).h());x=apply(lambda c,a:whites_curve(c,a,whites,H(1,c)),initial,p[4]);x=shadow(x,p[6]);x=apply(lambda c,a:tonal_contrast(c,skin,a),x,p[15]);x=apply(contrast,x,p[7]);x=lazy_select(p[11].abs().lt(F(GATE,rgb)),lambda:x,lambda:lazy_select(p[11].gt(F(0,rgb)),lambda:rich_sat(x,(p[11]+1).h(),H(3,rgb)),lambda:smooth_sat(x,(p[11]+1).h())));x=apply(airy,x,p[5],p[5]-1);x=apply(mids,x,p[2]);x=apply(lambda c,a:under_tone(c,skin,a),x,p[14]);x=light(x,p[3])
    def smart():
        y=lazy_select(p[8].gt(F(0,rgb)),lambda:highlight_neg(x,guide,(p[8]*F(fc('BFCC28F5C0000000'),rgb)).h()),lambda:x)
        return smart_contrast(y,guide,p[8].h())
    x=lazy_select(p[8].abs().lt(F(GATE,rgb)),lambda:x,smart);return mix(initial,x,person)
