"""Independent typed tonal leaves; explicit guide and half/f32 transitions."""
from leaf_numeric import V,hc,fc,mix,select,lazy_select,smoothstep,DomainUnknown
from pixel_leaves import H,F,dot,root_components
from leaf_domains import strictly_positive_branch


def blue_mask(blue):
    t=((blue+H(hc('b666'),blue))*H(hc('44ff'),blue)).clamp()
    return 1-((t*t)*H(hc('3b33'),blue))*(3-2*t)


def span_preserved(original,changed):
    low=original.min_channels();span=original.max_channels()-low
    def preserve():
        newlow=changed.min_channels();newspan=changed.max_channels()-newlow
        return (original-low)*(newspan/strictly_positive_branch(span,fc('3EE4F8B580000000')))+newlow
    return lazy_select(span.f().gt(F(fc('3EE4F8B580000000'),original)),preserve,lambda:changed)


def shadows_negative(rgb,guide,amount):
    c=rgb.clamp();scale=((-amount).f()-1).maximum(F(1,rgb)).h()
    q=mix(H(0,rgb),(guide.f()*F(fc('400B333340000000'),rgb)-scale.f()*F(fc('3FF3333340000000'),rgb)).h(),amount)
    square=q*q;negative=q.lt(0)
    weights=select(negative,H([0,0,0],rgb),square*H([hc('4180'),hc('4180'),hc('4100')],rgb))
    neg_square=select(negative,square.minimum(1),H(0,rgb));s=dot(c,[hc('3555')]*3).sqrt()
    boost=(q.f()*F(fc('3FFD9999A0000000'),rgb))*(H(hc('2e66'),rgb)-s).maximum(0).f()
    shaped=mix(c,c*c,blue_mask(c[2])*weights)
    lit=(((boost*blue_mask(shaped[2]).f())+1).h()*shaped).clamp()
    shape=((1-s.f())*s.f()).h();root=lit.sqrt();amplitude=neg_square*shape
    r,g,b=root_components(root,amplitude)
    colored=(((amplitude*H(hc('b666'),rgb)+root)+g)+r)+b
    neutral=mix(root,H(hc('3666'),rgb),(-neg_square)*shape)
    out=mix(neutral,colored,H(hc('3a66'),rgb)).maximum(0);out=(out*out).clamp()
    changed=((rgb.maximum(1)-1)+rgb.minimum(0))+out
    return span_preserved(rgb,changed)


def shadows(rgb,guide,amount):
    q=mix(H(0,rgb),(guide.f()*F(fc('400B333340000000'),rgb)-F(fc('3FF3333340000000'),rgb)).h(),amount)
    square=q*q;neg_square=select(q.lt(0),square.minimum(1).f(),F(0,rgb))
    weights=select(q.gt(0),H([0,0,0],rgb),square*H([hc('c180'),hc('c180'),hc('c100')],rgb))
    c=rgb.clamp();s=dot(c,[hc('3555')]*3).sqrt()
    boost=(q.f()*F(fc('3FFD9999A0000000'),rgb))*(H(hc('2e66'),rgb)-s).maximum(0).f()
    t=((c[2]+H(hc('b666'),rgb))*H(hc('44ff'),rgb)).clamp()
    mask=(1-smoothstep(t).f()*F(fc('3FECCCCCC0000000'),rgb)).h()
    shaped=mix(H(1,rgb),c,mask*weights)*c
    lit=(((boost*blue_mask(shaped[2]).f())+1).h()*shaped).clamp()
    shape=((1-s.f())*s.f()).h();root=lit.sqrt();amplitude=neg_square*shape.f()
    r,g,b=root_components(root,amplitude)
    colored=((((amplitude*F(fc('BFD99999A0000000'),rgb)).h()+root)+g)+r)+b
    neutral=mix(root,H(hc('3666'),rgb),(neg_square*(-shape).f()).h())
    out=mix(neutral,colored,H(hc('3a66'),rgb)).maximum(0);out=(out*out).clamp()
    return ((rgb.maximum(1)-1)+rgb.minimum(0))+out


FUNCTIONS={'ShadowsFilter':shadows,'ShadowsNegativeFilter':shadows_negative}


def models():
    from semantic_tone import I
    from bgfg_tone import MissingLeaf
    result={}
    for name,fn in FUNCTIONS.items():
        def call(rgb,amount,context,name=name,fn=fn):
            try:
                guide=context.guide
                guide=V.bounds(guide.lo,guide.hi)if isinstance(guide,I)else V.bounds(guide,guide)
                out=fn(V.bounds(rgb.lo,rgb.hi),guide,V.bounds(amount.lo,amount.hi))
                return I(out.lo,out.hi)
            except DomainUnknown as error:raise MissingLeaf(name+': domain unknown: '+str(error),rgb)from error
        result[name]=call
    return result
