"""Complete conditional renderNeutralizingAdjustments for this AIR10 caller."""
from dataclasses import dataclass
import numpy as np
from leaf_numeric import V,hc,fc,vec,lazy_select
from pixel_leaves import H,F
from pixel_color import to_lab
from pixel_skin import encode
from pixel_neutral import de_red,de_yellow,red_neutral_only,skin_warmth_positive,direction,smooth
from cast_values import CastValues
from bgfg_tone import GATE


@dataclass(frozen=True)
class NeutralStats:
    s2_4: V
    s3_4: V
    s4_4: V

    def __post_init__(self):
        v=[self.s2_4,self.s3_4,self.s4_4]
        if any(not isinstance(x,V)or x.precision!='f'or np.shape(x.lo)!=()for x in v)or any(x.point!=v[0].point for x in v):raise TypeError('Three matching scalar f32 raw stats fields required')


def forward(rgb,*,enabled: bool,cast: CastValues,skin,person,use_skin: bool,stats: NeutralStats|None):
    if type(enabled)is not bool or type(use_skin)is not bool:raise TypeError('Exact caller texture-presence flags required')
    if not isinstance(cast,CastValues)or cast.raw.point!=rgb.point:raise TypeError('Matching complete cast field block required')
    if not enabled:return rgb
    if not isinstance(stats,NeutralStats)or stats.s2_4.point!=rgb.point:raise TypeError('Enabled neutralizing requires supplied raw stats, not inferred color')
    reference=vec([stats.s2_4.h(),stats.s3_4.h(),stats.s4_4.h()]);lab=to_lab(reference);encoded=to_lab(encode(reference));mask=skin if use_skin else H(0,rgb)
    r=cast.scalar(15);desat=cast.scalar(16)
    def red():
        def neutral_only():
            angle=lazy_select(encoded[2].ne(0)|encoded[1].ne(0),lambda:encoded[2].atan2(encoded[1]),lambda:H(0,rgb))
            wrapped=lazy_select(angle.ne(0),lambda:angle+H(hc('4648'),rgb),lambda:angle).fmod(H(hc('4648'),rgb))
            x=(((wrapped.f()+F(fc('BFD3333340000000'),rgb)).abs()-F(.5,rgb))*F(fc('C001C71C80000000'),rgb)).clamp()
            weight=(((x*x)*F(.5,rgb))*(3-2*x)).h()
            hue_mix=1-smooth(((wrapped-H(hc('3a00'),rgb)+weight)*H(hc('44ff'),rgb)).clamp())
            changed=red_neutral_only(rgb,mask,encoded,r.h(),desat.h(),hue_mix)
            radius,_=direction(encoded);shifted=hue_mix*weight+wrapped;radius=(1-desat)*radius.f()
            newref=vec([encoded[0],(radius*shifted.cos().f()).h(),(radius*shifted.sin().f()).h()])
            return changed,newref
        # A possible desaturation branch affects both the pixel and reference.
        condition=desat.abs().lt(F(GATE,rgb))
        if np.all(condition.yes):return de_red(rgb,mask,person,lab,r.h()),encoded
        if np.all(condition.no):return neutral_only()
        a=de_red(rgb,mask,person,lab,r.h());b,newref=neutral_only()
        return V(np.minimum(a.lo,b.lo),np.maximum(a.hi,b.hi),a.precision,False),V(np.minimum(encoded.lo,newref.lo),np.maximum(encoded.hi,newref.hi),encoded.precision,False)
    condition=r.abs().lt(F(GATE,rgb))
    if np.all(condition.yes):changed=rgb;reference=encoded
    elif np.all(condition.no):changed,reference=red()
    else:
        a,reference=red();changed=V(np.minimum(rgb.lo,a.lo),np.maximum(rgb.hi,a.hi),'h',False);reference=V(np.minimum(encoded.lo,reference.lo),np.maximum(encoded.hi,reference.hi),'h',False)
    yellow=cast.scalar(17)
    original=changed;changed=lazy_select(yellow.abs().lt(F(GATE,rgb)),lambda:original,lambda:de_yellow(original,person,reference,yellow.h()))
    warmth=cast.scalar(18);original=changed
    return lazy_select(warmth.abs().lt(F(GATE,rgb)),lambda:original,lambda:skin_warmth_positive(original,person,mask,lab,H(1,rgb),warmth.h()))
