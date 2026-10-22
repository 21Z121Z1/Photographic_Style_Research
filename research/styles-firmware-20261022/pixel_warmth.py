"""AIR10 warmth root and shared protect/white-balance leaves, explicit fields."""
from leaf_numeric import V,hc,fc,vec,mix,select,lazy_select
from pixel_leaves import H,F,columns
from pixel_color import to_lab,from_lab
from pixel_neutral import smooth
from cast_values import CastValues
from bgfg_tone import GATE


def angle_of(lab):return lazy_select(lab[2].ne(0)|lab[1].ne(0),lambda:lab[2].atan2(lab[1]),lambda:H(0,lab))


def protect(rgb,parameters,*,ignore_chroma=False):
    lab=to_lab(rgb);angle=angle_of(lab);weights=[]
    for p in parameters:
        variance=p[1].maximum(H(hc('0001'),rgb));d=angle-p[0]
        wrapped=lazy_select(angle.gt(0),lambda:d.f()-F(6.28125,rgb),lambda:d.f()+F(6.28125,rgb))
        off=(-wrapped.square()/variance.f()).exp()*p[2].f()
        base=((-d.square()/variance).exp()*p[2]).f()
        weights.append((off+base).h())
    radius=(lab[1].square()+lab[2].square()).sqrt()
    strength=H(1,rgb)if ignore_chroma else smooth(((radius+H(hc('aa66'),rgb))*H(hc('4e3e'),rgb)).clamp())
    return strength*vec(weights)


def warmth(rgb,protection,coeff):
    c=rgb.clamp();root=c.pow(H(hc('3400'),rgb))
    yiq=columns(root,[['34c9','38c4','32c4'],['38b2','b464','b82e'],['2f4c','b524','34fa']])
    chroma=((yiq[1].square()+yiq[2].square())*H(4,rgb)).minimum(1)
    chroma=smooth(((chroma+H(hc('2666'),rgb))*H(hc('3bcd'),rgb)).clamp())
    light=smooth(((yiq[0].minimum(1)+H(hc('b266'),rgb))*H(hc('4500'),rgb)).clamp())
    shift=mix(vec([coeff[0],coeff[1]]),coeff[3]*vec([coeff[0],coeff[2]]),protection[0])
    ab=vec([yiq[1],yiq[2]]);changed=mix(ab+chroma.pow(H(hc('3266'),rgb))*shift,ab,protection.sum_channels())
    changed=mix(vec([yiq[0],changed[0],changed[1]]),yiq,1-light)
    inverse=(changed[1]*H([hc('3ba6'),hc('b45b'),hc('bc6e')],rgb)+changed[0])+changed[2]*H([hc('38f8'),hc('b92e'),hc('3ed2')],rgb)
    return ((rgb.minimum(0)-1)+rgb.maximum(1))+inverse.pow(H(4,rgb))


def white_balance(rgb,parameters,amount,tint):
    shifted=amount.f()-F(.5,rgb)
    def base():
        def left():
            scale=(1-amount*H(2,rgb)).f()
            return vec([(scale*F(fc('BFB99999A0000000'),rgb)).h(),(scale*F(fc('BFC872B020000000'),rgb)).h()])
        def right():
            scale=(shifted*F(2,rgb)).h().f()
            return vec([(scale*F(fc('3FC9FBE760000000'),rgb)).h(),(scale*F(fc('3FCB573EA0000000'),rgb)).h()])
        return lazy_select(amount.lt(H(.5,rgb)),left,right)
    coeff=lazy_select(shifted.abs().lt(F(GATE,rgb)),lambda:H([0,0],rgb),base)
    def rotate():
        phase=tint*H(hc('c248'),rgb);co=phase.cos();si=phase.sin();a=co*coeff[0]-si*coeff[1]
        return vec([a,a*si+co*coeff[1]])
    coeff=lazy_select(tint.abs().f().lt(F(GATE,rgb)),lambda:coeff,rotate)
    raw_angle=angle_of(to_lab(rgb))+H(hc('3f9a'),rgb)
    restore=(raw_angle.square()*H(hc('bf1c'),rgb)).exp()
    c=rgb.clamp();lab=to_lab(c);angle=angle_of(lab);shift=lab[0].square()*coeff;weights=[]
    for p in parameters:
        d=angle-p[0];weights.append((-d.square()/p[1].maximum(H(hc('0001'),rgb))).exp()*p[2])
    total=(weights[1]+weights[0])+weights[2];shift=mix(shift,H([0,0],rgb),total)
    out=from_lab(vec([lab[0],shift[0]+lab[1],shift[1]+lab[2]]))
    out=mix(out,c,restore).clamp()
    return ((rgb.maximum(1)-1)+rgb.minimum(0))+out


def forward(rgb,cast: CastValues,person):
    if not isinstance(cast,CastValues)or cast.raw.point!=rgb.point:raise TypeError('Complete matching cast block required')
    centers=cast.array(6);widths=cast.array(7);amplitudes=cast.array(8)
    params=[vec([centers[i].h(),(widths[i].square()*F(fc('3EF02E85C0000000'),rgb)).h(),amplitudes[i].h()])for i in range(3)]
    def step(x,amount_index,tint_index):
        amount=(cast.scalar(amount_index)*F(.5,rgb)+F(.5,rgb)).h();tint=cast.scalar(tint_index).h()
        def active():
            remainder=1-amount
            a=((amount.f()-remainder.f())*F(fc('3FC99999A0000000'),rgb)).h()
            common=remainder.f()*F(fc('3FA99999A0000000'),rgb)
            b=(common-amount.f()*F(fc('3F8EB851E0000000'),rgb)).h();c=(common+amount.f()*F(fc('3FA1EB8520000000'),rgb)).h()
            def rotate():
                phase=tint*H(hc('4248'),rgb);co=phase.cos();si=phase.sin();u=co*a-si*b
                return vec([u,u*si+co*b,u*si+co*c])
            values=lazy_select(tint.abs().f().lt(F(GATE,rgb)),lambda:vec([a,b,c]),rotate)
            w=select(amount.gt(H(.5,rgb)),H(hc('3548'),rgb),H(.5,rgb))
            return warmth(x,protect(x,params),vec([values[0],values[1],values[2],w]))
        return lazy_select((amount.f()-F(.5,rgb)).abs().lt(F(GATE,rgb)),lambda:x,active)
    first=step(rgb,0,2)
    amount=(cast.scalar(1)*F(.5,rgb)+F(.5,rgb)).h();tint=cast.scalar(3).h()
    middle=lazy_select((amount.f()-F(.5,rgb)).abs().lt(F(GATE,rgb)),lambda:rgb,lambda:white_balance(rgb,params,amount,tint))
    last=step(middle,4,5)
    return mix(first,last,person)
