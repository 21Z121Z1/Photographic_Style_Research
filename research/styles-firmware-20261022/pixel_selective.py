"""Complete conditional selective-color root with explicit 4x360 RGBA texture.

Sampling reuses the existing normalized linear/clamp Texture2D implementation.
This fixes a declared input shape; it does not recover Apple's lookup producer.
"""
from dataclasses import dataclass,field
import numpy as np
from leaf_numeric import V,hc,fc,vec,mix,lazy_select
from precomputed_semantic import Texture2D
from pixel_leaves import H,F
from pixel_color import to_lab,from_lab
from pixel_skin import decode
from pixel_neutral import smooth
from cast_values import CastValues


@dataclass(frozen=True)
class SelectiveTexture:
    values: np.ndarray
    working_domain: str
    rgb: Texture2D=field(init=False,repr=False)
    alpha: Texture2D=field(init=False,repr=False)

    def __post_init__(self):
        a=np.array(self.values,dtype='f2',copy=True)
        if a.shape!=(4,360,4)or not np.isfinite(a).all()or np.max(abs(a))>8 or not self.working_domain:raise ValueError('Explicit finite 4x360 RGBA half lookup, abs<=8, named domain required')
        a.setflags(write=False);object.__setattr__(self,'values',a)
        object.__setattr__(self,'rgb',Texture2D(a[:,:,:3],self.working_domain));object.__setattr__(self,'alpha',Texture2D(np.repeat(a[:,:,3:],3,axis=2),self.working_domain))

    def sample_row(self,u: V,row: int):
        v=np.float32((row+.5)*.25)
        if u.point:
            a=self.rgb.sample([u.lo,v]);b=self.alpha.sample([u.lo,v]);return V.value(np.r_[a,b[0]])
        a=self.rgb.range([float(u.lo),v],[float(u.hi),v]);b=self.alpha.range([float(u.lo),v],[float(u.hi),v])
        return V.bounds(np.r_[a.lo,b.lo[0]],np.r_[a.hi,b.hi[0]])


def selective(rgb,person,skin,sky,texture,offsets,amplitudes,output_mix):
    lab=to_lab(rgb.clamp());light=lab[0]
    angle=lazy_select(lab[2].ne(0)|lab[1].ne(0),lambda:lab[2].atan2(lab[1]),lambda:H(0,rgb));radius=(lab[1].square()+lab[2].square()).sqrt()
    u=(angle.f()*F(fc('404C9178A0000000'),rgb)+F(179.5,rgb)).h().clamp(0,hc('5d9c'))
    u=(u+H(.5,rgb)).f()*F(fc('3F66C16C20000000'),rgb)
    samples=[texture.sample_row(u,i)for i in range(4)]
    def lookup(channel,add=0):
        a,b,c,d=[p[channel]+H(add,rgb)if add else p[channel]for p in samples]
        return mix(mix(a,d,sky),mix(b,c,skin),person)
    saturation=lookup(1,1)
    def moderate():
        x=(radius*H(hc('4900'),rgb)).clamp();weight=((x*x)*(1-light.square()))*(3-2*x)
        return mix(saturation,H(1,rgb),weight)
    saturation=lazy_select(saturation.gt(H(1,rgb)),moderate,lambda:saturation)
    luminosity=lookup(2,1);hue=lookup(0);new_radius=saturation*radius;new_angle=hue+angle
    new_light=mix(H(1,rgb),luminosity,new_radius.clamp(hc('b99a'),hc('399a')))*light
    basic=vec([new_light,new_angle.cos()*new_radius,new_angle.sin()*new_radius])
    high=(((light.f()-1).square()*F(-16,rgb)).exp()*amplitudes[2].f()).h()
    middle=(((light.f()-F(.5,rgb)).square()*F(-16,rgb)).exp()*amplitudes[1].f()).h()
    low=(((-light.square()).f()*F(16,rgb)).exp()*amplitudes[0].f()).h()
    ab=vec([basic[1],basic[2]])
    for offset,weight in zip(offsets,[low,middle,high]):ab=mix(ab,ab+offset,weight)
    changed=vec([new_light,ab[0],ab[1]])
    changed=mix(changed,mix(basic,changed,output_mix),person)
    converted=from_lab(changed);gamma=lookup(3,1);powered=converted.pow(gamma)
    root=new_radius.sqrt();weight=((H(hc('2e66'),rgb)-root)/(-root)).clamp()
    weight=((weight*weight)*light.sqrt())*(3-2*weight)
    out=mix(converted,powered,weight).clamp()
    return ((rgb.maximum(1)-1)+rgb.minimum(0))+out


def forward(rgb,cast: CastValues,texture: SelectiveTexture,person,skin,sky,output_mix):
    if not isinstance(cast,CastValues)or cast.raw.point!=rgb.point:raise TypeError('Matching full renderer cast fields required')
    if not isinstance(texture,SelectiveTexture):raise TypeError('Explicit four-row RGBA lookup required, no texture substitution')
    offsets=[];amplitudes=[]
    for scalar,array in [(9,12),(10,13),(11,14)]:
        coefficient=cast.scalar(scalar)
        offsets.append(lazy_select(coefficient.ne(0),lambda array=array:to_lab(decode(cast.array(array).h()))[slice(1,3)],lambda:H([0,0],rgb)))
        amplitudes.append(coefficient.h())
    return selective(rgb,person,skin,sky,texture,offsets,vec(amplitudes),output_mix)
