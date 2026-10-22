"""Independent positive/negative lighten leaves, with explicit guide domain."""
from leaf_numeric import V,hc,fc,mix,lazy_select,exterior,DomainUnknown
from pixel_leaves import H,F,dot,root_components


def negative_lighten(rgb,guide,amount):
    c=rgb.clamp();luma=dot(c,[hc('363d'),hc('3800'),hc('2f0a')])
    scaled=lazy_select(luma.gt(0),lambda:(luma.pow(amount)*c)/luma,lambda:H([0,0,0],rgb))
    direct=c.pow(amount)
    remapped=(((guide*H(hc('42cd'),rgb)+H(hc('bccd'),rgb)).f()+F(fc('3FF0FDBF40000000'),rgb))*F(fc('3FDA374BC0000000'),rgb)).h()
    weight=remapped.pow(H(hc('3400'),rgb));rg=dot(c,[hc('3800'),hc('3800'),0])
    shaped=mix(c,mix(direct,scaled,H(hc('3a66'),rgb)),weight).clamp()
    s=rg.f().sqrt();shape=(1-s)*s;amplitude=(shape*(amount.f()*F(fc('3FD3333340000000'),rgb))).h()
    root=shaped.sqrt();guide_root=guide.sqrt();r,g,b=root_components(root,amplitude)
    colored=((((-guide_root)*amplitude+root)+g)+r)+b
    neutral=mix(root,guide_root,((amount.f()*F(fc('BFD3333340000000'),rgb))*shape).h())
    out=mix(neutral,colored,H(hc('3a66'),rgb)).maximum(0)
    return ((rgb.maximum(1)-1)+rgb.minimum(0))+out*out


def lighten(rgb,guide,amount):
    c=rgb.clamp();rg=dot(c,[hc('3800'),hc('3800'),0])
    base=(guide.f()*F(fc('400B333340000000'),rgb)+F(fc('BFF3333340000000'),rgb)).h()
    remapped=((base.f()+F(fc('3FF0FDBF40000000'),rgb))*F(fc('3FDA374BC0000000'),rgb)).h()
    exponent=((amount.f()*F(.75,rgb))*(remapped-rg).f()+1).h()
    weight=remapped.pow(H(hc('3800'),rgb)).clamp();direct=c.pow(exponent)
    plus=amount.f()+1
    corrected=(direct-rg)+(plus*rg.f()).h()
    a=mix(direct,corrected,1-weight);b=mix(direct,direct*plus.h(),1-weight)
    changed=mix(mix(b,a,rg),c,rg.sqrt()).clamp()
    shape=((1-rg.sqrt().f())*rg.sqrt().f()).h();amplitude=(amount*H(hc('34cd'),rgb))*shape
    root=changed.sqrt();guide_root=guide.sqrt();r,g,b=root_components(root,amplitude)
    colored=(((amplitude*(-guide_root)+root)+g)+r)+b
    neutral=mix(root,guide_root,(amount*H(hc('b4cd'),rgb))*shape)
    out=mix(neutral,colored,H(hc('3a66'),rgb)).maximum(0)
    return exterior(rgb)+out*out


FUNCTIONS={'lightenFilter':lighten,'negativeLightenFilter':negative_lighten}


def models():
    from semantic_tone import I
    from bgfg_tone import MissingLeaf
    result={}
    for name,fn in FUNCTIONS.items():
        def call(rgb,amount,context,name=name,fn=fn):
            try:
                guide=context.guide;guide=V.bounds(guide.lo,guide.hi)if isinstance(guide,I)else V.bounds(guide,guide)
                out=fn(V.bounds(rgb.lo,rgb.hi),guide,V.bounds(amount.lo,amount.hi));return I(out.lo,out.hi)
            except DomainUnknown as error:raise MissingLeaf(name+': domain unknown: '+str(error),rgb)from error
        result[name]=call
    return result
