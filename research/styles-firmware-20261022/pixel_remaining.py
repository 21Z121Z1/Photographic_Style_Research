"""Remaining AIR10 BG/FG leaves; argument identity is explicit at adapters."""
from leaf_numeric import V,hc,fc,mix,lazy_select,select,exterior,smoothstep,DomainUnknown
from pixel_leaves import H,F,dot,root_components
from pixel_color import to_polar,from_polar
from leaf_domains import strictly_positive_branch


def under_grass(rgb,person,amount):
    c=rgb.clamp();light,angle,radius=to_polar(c)
    shifted=angle+amount*H(hc('3266'),rgb)
    h=angle.f()+F(fc('BFFBA55FE0000000'),rgb)
    angle=mix(angle,shifted,(h.square()*F(fc('C020539780000000'),rgb)).exp().h())
    damp=((amount.abs()*light).maximum(H(.5,rgb))*H(hc('2a66'),rgb)).f()
    radius=((1-damp)*radius.f()).h()
    work=from_polar(light,angle,radius,clamp_output=False)
    return ((rgb.maximum(1)-1)+rgb.minimum(0))+mix(work,c,person).clamp()


def under_tone(rgb,skin,amount):
    c=rgb.clamp();light,angle,radius=to_polar(c)
    shifted=(amount.f()*F(fc('3FC99999A0000000'),rgb)+angle.f()).h()
    h=angle.f()+F(fc('BFF79FF020000000'),rgb)
    angle=mix(angle,shifted,(h.square()*F(fc('C000539780000000'),rgb)).exp().h())
    damp=(amount.abs()*light).maximum(H(.5,rgb)).f()*F(fc('3FC3333340000000'),rgb)
    radius=((1-damp)*radius.f()).h()
    work=from_polar(light,angle,radius,clamp_output=False)
    return ((rgb.maximum(1)-1)+rgb.minimum(0))+mix(c,work,skin).clamp()


def tonal_contrast(rgb,skin,amount):
    c=rgb.clamp();luma=dot(c,[hc('34cd'),hc('3800'),hc('3266')])
    def scale():
        p4=luma.pow(H(4,rgb)).f()*F(fc('3FFA182AA0000000'),rgb)
        p3=luma.pow(H(3,rgb)).f()*F(fc('C00D923A20000000'),rgb)
        p2=luma.pow(H(2,rgb)).f()*F(fc('4005A02760000000'),rgb)
        p1=luma.f()*F(fc('3FD765FD80000000'),rgb)
        polynomial=(((p4+p1)+p3)+p2).h()
        return (polynomial*c)/strictly_positive_branch(luma)
    changed=lazy_select(luma.gt(0),scale,lambda:H([0,0,0],rgb))
    work=mix(c,mix(c,changed,amount),((skin.f()+1)*F(.5,rgb)).h()).clamp()
    return ((rgb.maximum(1)-1)+rgb.minimum(0))+work


def smart_contrast(rgb,guide,amount):
    s=dot(rgb,[hc('3555')]*3).pow(H(hc('3e00'),rgb));delta=rgb-s
    shape=((s.f()*F(2.25,rgb))*(1-s.f())).h();amp=shape*amount
    r,g,b=root_components(rgb,amp)
    color=(((amp*H(hc('b800'),rgb)+rgb)+g)+r)+b
    neutral=mix(rgb,H(.5,rgb),(-amount)*shape)
    weight=((delta[1].square()+H(hc('399a'),rgb))+delta[0].square())+delta[2].square()
    changed=mix(neutral,color,weight).maximum(0)
    q=guide*H(hc('42cd'),rgb)+H(hc('bccd'),rgb)
    q=((q.f()+F(fc('3FF0FDBF40000000'),rgb))*F(fc('3FDA374BC0000000'),rgb)).h()
    weight=(q.f()*F(4,rgb)*(1-q.f())).h()
    return mix(rgb,changed,weight)


def highlight_neg(rgb,guide,amount):
    t=1-smoothstep((amount-1).clamp())
    q=mix(H(0,rgb),(guide.f()*F(fc('400B333340000000'),rgb)-t.f()*F(fc('3FE99999A0000000'),rgb)).h(),-amount)
    exponent=select(q.gt(0),(q.f()*F(1.5,rgb)+1).h(),H(1,rgb))
    c=rgb.clamp();s=dot(c,[hc('3555')]*3).sqrt();root=c.pow(exponent).clamp().sqrt();guide_root=guide.sqrt()
    shape=((1-s.f())*s.f()).h();amp=(exponent*H(hc('b800'),rgb))*shape
    r,g,b=root_components(root,amp)
    color=(((amp*(-guide_root)+root)+g)+r)+b
    neutral=mix(root,guide_root,(exponent*H(hc('b800'),rgb))*(-shape))
    out=mix(neutral,color,H(hc('3a66'),rgb)).maximum(0).square().clamp()
    return ((rgb.maximum(1)-1)+rgb.minimum(0))+out


def local_contrast(rgb,guide,amount):
    c=rgb.clamp();s=dot(c,[hc('3555')]*3).sqrt();shape=((1-s.f())*s.f()).h();root=c.sqrt();groot=guide.sqrt()
    a=shape*amount;amp=a*H(2,rgb);r,g,b=root_components(root,amp)
    color=(((g+root)+r)+b)+(a*H(-2,rgb))*groot
    neutral=mix(root,groot,a*H(-2,rgb));out=mix(neutral,color,H(hc('3a66'),rgb)).maximum(0).square()
    work=exterior(rgb)+out
    return mix(work,work.maximum(rgb),H(0,rgb))


def gamma_contrast(rgb,guide,amount):
    c=rgb.clamp();mean=dot(c,[hc('3555')]*3)
    q=(guide.f()*F(fc('400B333340000000'),rgb)+F(fc('BFF3340000000000'),rgb)).h()
    q=((q.f()+F(fc('3FF0FDBF40000000'),rgb))*F(fc('3FDA374BC0000000'),rgb)).h()
    exponent=((amount*H(2,rgb))*(q-mean)+1).maximum(0)
    return exterior(rgb)+c.pow(exponent).maximum(0)


FUNCTIONS={'underGrassFilter':under_grass,'underToneFilter':under_tone,'tonalContrastFilter':tonal_contrast,'smartContrast':smart_contrast,'highlightNeg':highlight_neg,'BG.localContrast_inline':local_contrast,'BG.gammaContrast_inline':gamma_contrast}
ARGUMENTS={'underGrassFilter':'person_weight','underToneFilter':'skin_weight','tonalContrastFilter':'skin_weight'}


def models():
    from semantic_tone import I
    from bgfg_tone import MissingLeaf
    result={}
    for name,fn in FUNCTIONS.items():
        def call(rgb,amount,context,name=name,fn=fn):
            try:
                value=getattr(context,ARGUMENTS.get(name,'guide'));value=V.bounds(value.lo,value.hi)if isinstance(value,I)else V.bounds(value,value)
                out=fn(V.bounds(rgb.lo,rgb.hi),value,V.bounds(amount.lo,amount.hi));return I(out.lo,out.hi)
            except DomainUnknown as error:raise MissingLeaf(name+': domain unknown: '+str(error),rgb)from error
        result[name]=call
    return result
