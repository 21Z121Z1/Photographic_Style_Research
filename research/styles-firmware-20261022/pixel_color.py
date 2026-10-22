"""AIR10 saturation leaves with explicit f32 matrices and half polar chroma.

Input is the helper's working RGB, not an assumed camera color space. Matrices
are literal coefficients of this identified build, not a named ICC conversion.
"""
from leaf_numeric import V,fc,hc,vec,mix,select,lazy_select,smoothstep,DomainUnknown
from pixel_leaves import H,F,dot


def matrix(rgb,cols):
    c=[F([fc(x)for x in col],rgb)for col in cols]
    return (rgb[0]*c[0]+rgb[1]*c[1])+rgb[2]*c[2]


def signed_power(x,exponent):return x.abs().pow(F(fc(exponent),x))*x.sign()


def to_lab(c):
    lms=matrix(c.f(),[
        ['3FD4186A60000000','3FC3E33E40000000','3F922DAE80000000'],
        ['3FE476E3E0000000','3FE840ABE0000000','3FBC0465A0000000'],
        ['3FA7CE86C0000000','3FB6321060000000','3FEBEC1640000000']])
    return matrix(signed_power(lms,'3FDB851EC0000000'),[
        ['3FD99999A0000000','4011D1EB80000000','3FE9C779A0000000'],
        ['3FD99999A0000000','C013676C80000000','3FD6DC5D60000000'],
        ['3FC99999A0000000','3FD9581060000000','BFF29AD420000000']]).h()


def to_polar(c):
    lab=to_lab(c)
    angle=lazy_select(lab[2].ne(0)|lab[1].ne(0),lambda:lab[2].atan2(lab[1]),lambda:H(0,c))
    radius=(lab[1].square()+lab[2].square()).sqrt()
    return lab[0],angle,radius


def from_lab(lab):
    lab=lab.f()
    v=(lab[1]*F([fc(x)for x in ['3FB8FA4700000000','BFBD270280000000','3FA0B2ED80000000']],lab)+lab[0])+lab[2]*F([fc(x)for x in ['3FCA44DC20000000','3FC10D4280000000','BFE5A90F40000000']],lab)
    return matrix(signed_power(v,'40029ACA60000000'),[
        ['4015E38B80000000','BFF200FDA0000000','3F9E845300000000'],
        ['C012915E00000000','4002586A00000000','BFC8BA2560000000'],
        ['3FC5B6AB00000000','BFC57D9700000000','3FF29E4D40000000']]).h()


def from_polar(light,angle,radius,*,clamp_output=True):
    out=from_lab(vec([light,angle.cos()*radius,angle.sin()*radius]))
    return out.clamp()if clamp_output else out


def smooth_sat(rgb,gain):
    light,angle,radius=to_polar(rgb.clamp())
    out=((rgb.maximum(1)-1)+rgb.minimum(0))+from_polar(light,angle,radius*gain)
    return select(gain.f().lt(F(fc('3F947AE140000000'),rgb)),vec([out[1]]*3),out)


def rich_sat(rgb,gain,strength):
    c=rgb.clamp();norm=(H(1,rgb)/c.sum_channels())*c
    light,angle,radius=to_polar(c);dist=[]
    for a,b in [(0,1),(0,2),(1,2)]:
        x=norm[a].f()+F(fc('BFD55553E0000000'),rgb);y=norm[b].f()+F(fc('BFD55553E0000000'),rgb)
        dist.append((x.square()+y.square()).sqrt().h())
    s=smoothstep(vec(dist).max_channels().sqrt().clamp())
    mask=(s.f()*F(2,rgb)*(1-s.f())).minimum(1).h()
    mask=lazy_select(gain.gt(H(hc('3a00'),rgb))&strength.gt(H(3,rgb)),lambda:(gain.f()-F(.75,rgb)+mask.f()).minimum(1),lambda:mask.f()).h()
    work=from_polar(light,angle,mix(radius,radius*gain,light*mask))
    power=work.pow((gain-1)*strength+1);mean=dot(power,[hc('3555')]*3)
    rescaled=lazy_select(mean.gt(0),lambda:(dot(work,[hc('3555')]*3)*power)/mean,lambda:H([0,0,0],rgb))
    hue=angle.f()+F(fc('BFFE666660000000'),rgb)
    huefactor=(1-(hue.square()*F(fc('C00638E380000000'),rgb)).exp()).maximum(F(.5,rgb)).h()
    ratio=((1-light.square().f())*mask.f()*huefactor.f()).h()
    return ((rgb.maximum(1)-1)+rgb.minimum(0))+mix(work,rescaled,ratio).clamp()


FUNCTIONS={'smoothSatFilter':smooth_sat,'RichSat':rich_sat}


def models():
    from semantic_tone import I
    from bgfg_tone import MissingLeaf
    result={}
    for name,fn in FUNCTIONS.items():
        def call(rgb,amount,context,name=name,fn=fn):
            try:
                c=V.bounds(rgb.lo,rgb.hi);a=V.bounds(amount.lo,amount.hi)
                out=fn(c,a,H(3,c))if name=='RichSat'else fn(c,a)
                return I(out.lo,out.hi)
            except DomainUnknown as error:raise MissingLeaf(name+': domain unknown: '+str(error),rgb)from error
        result[name]=call
    return result
