"""Precision lift of the existing semantic_skin_model, not a new skin algorithm.

The legacy continuous implementation remains unchanged. Brightness reuses the
already modeled local operator; only its original protect mix differs. Color
uses the same legacy luminance/chroma/tint equations in original AIR order.
"""
from leaf_numeric import V,hc,fc,mix,select,lazy_select
from leaf_domains import strictly_positive_branch
from pixel_leaves import H,F,dot,columns
from pixel_remaining import local_contrast
from bgfg_tone import GATE


def decode(x):
    a=x.abs();return select(a.gt(H(hc('292d'),x)),((a+H(hc('2b0a'),x))*H(hc('3b96'),x)).pow(H(hc('40cd'),x)),a*H(hc('2cf4'),x))*x.sign()


def encode(x,*,host_fma=False,observations=None):
    if type(host_fma)is not bool:raise TypeError('Exact caller-specific host contraction flag required')
    a=x.abs();power=a.pow(H(hc('36aa'),x));scaled=power*H(hc('3c38'),x);offset=power.fma_half(H(hc('3c38'),x),H(hc('ab0a'),x))if host_fma else scaled+H(hc('ab0a'),x);chosen=select(a.gt(H(hc('1a69'),x)),offset,a*H(hc('4a76'),x));out=chosen*x.sign()
    if observations is not None:observations.update(abs=a,power=power,scaled=scaled,offset=offset,chosen=chosen,output=out)
    return out


def forward(rgb,skin,guide,theta9,theta10):
    def brightness():
        work=local_contrast(rgb,guide,theta10.h())
        return mix(work,work.maximum(rgb),H(1,rgb))
    y=lazy_select(theta10.abs().lt(F(GATE,rgb)),lambda:rgb,brightness)
    def color():
        normalized=(H(1,rgb)/y.sum_channels())*y
        luminance=dot(y,[hc('3800'),hc('34cd'),hc('3266')])
        a=((luminance+H(hc('b666'),rgb))*H(hc('3eaa'),rgb)).clamp()
        b=(((normalized[0].maximum(normalized[1])+H(hc('b555'),rgb))+normalized[1].maximum(normalized[2]))*H(hc('3dff'),rgb)).clamp()
        chroma=(b*b)*(3-2*b)
        weight=(((a*a)*(theta9*F(2,rgb)).h())*(3-2*a)).f()
        weight=((1-chroma.f())*weight).minimum(1).h()
        tint=decode(H([1,hc('399a'),hc('3866')],rgb))
        return mix(y,tint*y,weight)
    changed=lazy_select(theta9.abs().lt(F(GATE,rgb)),lambda:y,color)
    return mix(rgb,changed,skin)


def highlight_recover(rgb,guide,strength):
    work=columns(rgb,[['383c','2e4c','2452'],['3548','3afd','2f88'],['307f','2734','3aec']]).pow(H(hc('3872'),rgb))
    minimum=work.min_channels();mean=dot(work,[hc('3555')]*3);base=mix(minimum,mean,H(.5,rgb));power=base.pow(strength*H(2,rgb)+1)
    scaled=lazy_select(base.gt(0),lambda:(power*work)/strictly_positive_branch(base),lambda:H([0,0,0],rgb))
    out=mix(work,scaled,minimum).pow(H(hc('3f33'),rgb))
    out=columns(out,[['4011','b353','a060'],['b9d2','3ced','b0e8'],['b4e9','99de','3ca6']])
    ratio=lazy_select(base.gt(0),lambda:(power*guide)/strictly_positive_branch(base),lambda:H(0,rgb))
    out=mix(out,rgb,H(hc('3400'),rgb));total=out.sum_channels();luma=dot(out,[hc('3555')]*3).maximum(0).sqrt();s=strength*H(hc('3e00'),rgb)
    newguide=mix(mix(guide,ratio,minimum),guide,H(hc('3400'),rgb))
    ratio=((total-newguide*H(3,rgb))*s+total)/total.maximum(H(hc('068e'),rgb))
    q=((ratio.f()-1)*F(fc('3FF922D0E0000000'),rgb)).h();t=(q.f()/(q.abs().f()+1)).h()
    coefficient=select(t.lt(0),F(.75,rgb),F(fc('3FE4CCCCC0000000'),rgb))
    gain=(coefficient*t.f()+1).h().maximum(1-s).minimum(strength*H(hc('3b34'),rgb)+1)
    return mix(out,gain*out,luma)
