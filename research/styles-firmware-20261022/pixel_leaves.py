"""Independent typed numerical models of selected AIR10 pixel leaf operators.

Arithmetic order/half/f32 transitions are explicit. Interval mode preserves
branch unions or rejects an unproved domain; no fitting or native GPU claim.
"""
import numpy as np
from leaf_numeric import V,hc,fc,mix,vec,select,lazy_select,exterior,smoothstep,DomainUnknown
from leaf_domains import strictly_positive_branch
from leaf_correlations import channel_span


def H(x,like):return V.value(x,'h',like.point)
def F(x,like):return V.value(x,'f',like.point)
def dot(rgb,weights):return (rgb*H(weights,rgb)).sum_channels()


def curve_sample(coordinate: V,curve):
    index=coordinate*H(len(curve.red_samples)-1,coordinate)
    if coordinate.point:return H(curve.sample(index.lo/(len(curve.red_samples)-1)),coordinate)
    a,b=curve.range(index.lo/(len(curve.red_samples)-1),index.hi/(len(curve.red_samples)-1))
    return V.bounds(a,b,'h')


def columns(rgb,values):
    cols=[H([hc(x)for x in column],rgb)for column in values]
    return (rgb[0]*cols[0]+rgb[1]*cols[1])+rgb[2]*cols[2]


def whites_curve(rgb: V,amount: V,curve,mode: V):
    work=columns(rgb,[['383c','2e4c','2452'],['3548','3afd','2f88'],['307f','2734','3aec']])
    c=work.clamp().pow(H(hc('3872'),rgb));z=c.min_channels()
    target=select(z.gt(H(hc('3a00'),rgb)),H(1,rgb),curve_sample(z,curve).clamp())
    changed=mix(z,target,amount)
    first=lazy_select(z.gt(0),lambda:mix(c,(changed*c)/strictly_positive_branch(z),z),lambda:c)
    second=mix(c,(c-z)+changed,mix(z,changed,mode))
    value=exterior(work)+mix(first,second,z).clamp().pow(H(hc('3f33'),rgb))
    return columns(value,[['4011','b353','a060'],['b9d2','3ced','b0e8'],['b4e9','99de','3ca6']]).maximum(0)


def airy(rgb: V,gamma: V):
    c=rgb.clamp();norm=(H(1,rgb)/c.sum_channels())*c
    chroma=((norm[0].maximum(norm[1])-H(hc('3555'),rgb))+norm[1].maximum(norm[2]))*H(hc('3dff'),rgb)
    weight=smoothstep(chroma.clamp())*dot(c,[hc('3555')]*3).sqrt()
    return exterior(rgb)+mix(c,c.pow(gamma),weight).clamp()


def root_components(root: V,amplitude: V):
    # f32 weighting then explicit half conversion, as in the original helpers.
    return [(amplitude.f()*F(fc(bits),root)).h()*root[i]for i,bits in enumerate(['3FD322D0E0000000','3FE2C8B440000000','3FBD2F1AA0000000'])]


def contrast(rgb: V,amount: V):
    c=rgb.clamp();s=dot(c,[hc('3555')]*3).sqrt();delta=c-s;variance=(delta*delta).sum_channels()
    shape=((1-s.f())*s.f()).h();root=c.sqrt();scaled=(amount.f()*F(fc('400B333340000000'),rgb)).h();amplitude=shape*scaled
    r,g,b=root_components(root,amplitude)
    colored=(((root+amplitude*H(hc('b800'),rgb))+g)+r)+b
    neutral=mix(root,H(hc('3800'),rgb),(-scaled)*shape)
    newroot=mix(neutral,colored,(variance.f()+F(fc('3FE99999A0000000'),rgb)).h()).maximum(0)
    changed=exterior(rgb)+newroot*newroot;low=rgb.min_channels();span=channel_span(rgb)
    def preserve():
        newlow=changed.min_channels();newspan=channel_span(changed)
        return (rgb-low)*(newspan/strictly_positive_branch(span,fc('3EE4F8B580000000')))+newlow
    return lazy_select(span.f().gt(F(fc('3EE4F8B580000000'),rgb)),preserve,lambda:changed)


LEAVES={'contrastFilter':contrast,'airyFilter':airy}


def models(curve=None):
    """Adapters consume/return boxes; an unproved domain remains unknown."""
    from semantic_tone import I
    from bgfg_tone import MissingLeaf
    result={}
    def adapt(name,fn):
        def call(rgb,amount,context):
            try:
                out=fn(V.bounds(rgb.lo,rgb.hi),V.bounds(amount.lo,amount.hi),context)
                return I(out.lo,out.hi)
            except DomainUnknown as error:raise MissingLeaf(name+': domain unknown: '+str(error),rgb)from error
        return call
    for name,fn in LEAVES.items():result[name]=adapt(name,lambda rgb,amount,ctx,fn=fn:fn(rgb,amount))
    if curve is not None:
        for name,mode in [('whitesCurve_BG_mode0',0),('whitesCurve_FG_mode1',1)]:
            result[name]=adapt(name,lambda rgb,amount,ctx,mode=mode:whites_curve(rgb,amount,curve,H(mode,rgb)))
    return result
