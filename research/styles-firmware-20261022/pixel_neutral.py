"""Independent neutralizing color leaves, reusing exact working Lab transforms."""
from leaf_numeric import V,hc,fc,vec,mix,lazy_select
from leaf_domains import strictly_positive_branch
from pixel_leaves import H,F
from pixel_color import to_lab,from_lab
from pixel_skin import encode,decode


def smooth(x):return (x*x)*(3-2*x)


def direction(lab):
    radius=(lab[1].square()+lab[2].square()).sqrt();threshold=fc('3F50624DE0000000')
    normalized=lazy_select(radius.f().gt(F(threshold,lab)),lambda:vec([lab[1],lab[2]])/strictly_positive_branch(radius,threshold),lambda:H([0,0],lab))
    return radius,normalized


def alignment(unit):return (unit[0]*H(hc('3aee'),unit)+unit[1]*H(.5,unit))/H(1,unit).sqrt()


def finish(rgb,lab):return ((rgb.maximum(1)-1)+rgb.minimum(0))+decode(from_lab(lab))


def de_red(rgb,skin,person,reference,amount):
    c=rgb.clamp();lab=to_lab(encode(c));_,u=direction(lab);rr,v=direction(reference)
    reference_chroma=smooth(((rr+H(hc('adc3'),rgb))*H(hc('5243'),rgb)).clamp())
    target_hue=smooth(((alignment(u)+H(hc('bacd'),rgb))*H(hc('4723'),rgb)).clamp())
    reference_hue=smooth(((alignment(v)+H(hc('bb9a'),rgb))*H(hc('4e3e'),rgb)).clamp())
    shared=target_hue.f()*reference_chroma.f();factor=shared*F(fc('3FC3333340000000'),rgb)
    a=(lab[1].f()-((factor*lab[1].f())*reference_hue.f())).h();b=(lab[2].f()-((factor*lab[2].f())*reference_hue.f())).h()
    a=a*skin+lab[1]*(1-skin);b=b*skin+lab[2]*(1-skin)
    a2=(a.f()-(factor*reference_hue.f())*a.f()).h();b2=(b.f()-(factor*reference_hue.f())*b.f()).h()
    light=(((shared*F(fc('3F999999A0000000'),rgb))*lab[0].f())*reference_hue.f()+lab[0].f()).h()
    changed=vec([light*person+lab[0]*(1-person),a2*person+a*(1-person),b2*person+b*(1-person)])
    return mix(rgb,mix(c,finish(rgb,changed),amount),person)


def de_yellow(rgb,person,reference,amount):
    c=rgb.clamp();lab=to_lab(encode(c));_,u=direction(lab);_,v=direction(reference);hue=alignment(u)
    red=smooth(((hue+H(hc('bacd'),rgb))*H(hc('4723'),rgb)).clamp())
    yellow=smooth(((hue+H(hc('b4cd'),rgb))*H(hc('3f46'),rgb)).clamp())
    mask=((1-red.f()*F(.5,rgb))*yellow.f()).h()
    b=(lab[2].f()-mask.f()*F(fc('3FA47AE140000000'),rgb)).h();intermediate=from_lab(vec([lab[0],lab[1],b]))
    difference=((intermediate[1]-intermediate[2])*H(hc('5240'),rgb)).clamp()
    alignment_ref=(v[0]*H(hc('2a66'),rgb)+v[1]*H(hc('3666'),rgb))/H(hc('3132'),rgb).sqrt()
    weight=smooth(((alignment_ref+H(hc('bb33'),rgb))*H(hc('4989'),rgb)).clamp())
    scale=(weight.f()*F(fc('3FA47AE140000000'),rgb)+F(fc('3FA47AE140000000'),rgb)).h()
    shift=(((difference*difference)*mask)*(3-2*difference))*scale
    changed=vec([lab[0],lab[1],mix(lab[2],lab[2]-shift,person)])
    return mix(rgb,mix(c,finish(rgb,changed),amount),person)


def red_neutral_only(rgb,skin,reference,amount,desaturation,hue_mix):
    c=rgb.clamp();lab=to_lab(encode(c));radius,_=direction(lab);ref_radius,_=direction(reference)
    angle=lazy_select(lab[2].ne(0)|lab[1].ne(0),lambda:lab[2].atan2(lab[1]),lambda:H(0,rgb))
    wrapped=lazy_select(angle.ne(0),lambda:angle+H(hc('4648'),rgb),lambda:angle).fmod(H(hc('4648'),rgb))
    mask=smooth(((ref_radius+H(hc('b266'),rgb))*H(hc('cd02'),rgb)).clamp())
    x=((wrapped.f()+F(fc('BFD3333340000000'),rgb)).abs()-F(.5,rgb))*F(fc('C001C71C80000000'),rgb);x=x.clamp()
    weight=(((x*x)*(mask.f()*F(.5,rgb)))*(3-2*x)).h()
    angle=weight*hue_mix+wrapped;radius=radius*(1-desaturation)
    changed=vec([lab[0],mix(lab[1],angle.cos()*radius,skin),mix(lab[2],angle.sin()*radius,skin)])
    return mix(c,finish(rgb,changed),amount)


FUNCTIONS={'deRed':de_red,'deYellow':de_yellow,'deRedNeutralOnly':red_neutral_only}
