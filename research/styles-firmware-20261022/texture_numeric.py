"""Explicit finite R16/RGBA16 storage and normalized coordinate contracts.

The v3 point sampler is a declared CPU approximation. Set sampling takes the
whole local texel hull, including both sides of every uncertain coordinate;
it never samples an input or parameter box at its center.
"""
from dataclasses import dataclass
from enum import IntEnum
import numpy as np
from leaf_numeric import V,DomainUnknown,vec
from guided_conditioned import legacy


class PixelFormat(IntEnum):
    R16Float=25
    RGBA16Float=115


@dataclass(frozen=True)
class Texture:
    pixels: V
    pixel_format: PixelFormat
    working_domain: str

    def __post_init__(self):
        if type(self.pixel_format)is not PixelFormat:raise TypeError('Exact supported Metal storage format required')
        p=self.pixels;c=1 if self.pixel_format==PixelFormat.R16Float else 4
        if not isinstance(p,V)or p.precision!='h'or len(p.lo.shape)!=3 or p.lo.shape[2]!=c or min(p.lo.shape[:2])<1 or max(p.lo.shape[:2])>32 or not self.working_domain:raise TypeError('Named bounded half HxWxformat-lanes texture required')
        if np.max(np.maximum(abs(p.lo),abs(p.hi)))>65504:raise DomainUnknown('Texture exceeds finite half storage range')


def rgba(rgb):
    if not isinstance(rgb,V)or rgb.precision!='h'or rgb.lo.shape[-1]!=3:raise TypeError('Half RGB image required')
    shape=(*rgb.lo.shape[:-1],1)
    return V(np.concatenate([rgb.lo,np.ones(shape)],axis=-1),np.concatenate([rgb.hi,np.ones(shape)],axis=-1),'h',rgb.point)


def sample_normalized(texture: Texture,uv: V):
    p=texture.pixels
    if not isinstance(uv,V)or uv.precision!='f'or uv.lo.shape!=(2,)or uv.point!=p.point:raise TypeError('Matching normalized f32 UV2 required')
    if p.point:return V.value(legacy.normalized_sample(p.lo.astype('f2'),np.float32(uv.lo[0]),np.float32(uv.lo[1])),'h')
    h,w,c=p.lo.shape;x=np.clip(np.array([uv.lo[0],uv.hi[0]])*w-.5,0,w-1);y=np.clip(np.array([uv.lo[1],uv.hi[1]])*h-.5,0,h-1)
    part=p[int(np.floor(y[0])):int(np.ceil(y[1]))+1,int(np.floor(x[0])):int(np.ceil(x[1]))+1]
    # This hull also covers quantized linear weights. Arithmetic allowance is
    # the existing host assumption, not an empirical Metal sampler error bound.
    lo=np.min(part.lo,axis=(0,1));hi=np.max(part.hi,axis=(0,1));return V(lo,hi,'h',False).rounded(lo,hi).h()


def producer_uv(grid,destination_shape,*,point):
    if len(grid)!=2 or any(type(v)is not int or not 0<=v<=65535 for v in grid):raise TypeError('Exact uint16 logical grid required')
    h,w=destination_shape
    if any(type(v)is not int or not 1<=v<=32 for v in (h,w)):raise TypeError('Exact bounded destination grid required')
    # The original coordinate denominator is destination6, not source sizes.
    xy=V.value(grid,'f',point)+V.value(.5,'f',point)
    return xy/V.value([w,h],'f',point)


@dataclass(frozen=True)
class ROI:
    grid: tuple[int,int]
    field5: V
    field6: V

    def __post_init__(self):
        if len(self.grid)!=2 or any(type(x)is not int or not 0<=x<=65535 for x in self.grid):raise TypeError('Exact logical uint16 grid required')
        if any(not isinstance(x,V)or x.precision!='f'or x.lo.shape!=(4,)for x in [self.field5,self.field6])or self.field5.point!=self.field6.point:raise TypeError('Matching supplied f32 ROI5/6 scale-offset4 required')

    def coordinates(self):
        xy=V.value(self.grid,'f',self.field5.point)+V.value(.5,'f',self.field5.point)
        return [field[:2]*xy+field[2:]for field in [self.field5,self.field6]]


def consume_block290(bg: Texture,fg: Texture,roi: ROI,reference196,person96,semantic7):
    if bg.pixel_format!=PixelFormat.RGBA16Float or fg.pixel_format!=PixelFormat.RGBA16Float:raise TypeError('This caller has actual RGBA16 BG/FG map storage')
    if bg.working_domain!=fg.working_domain:raise TypeError('BG/FG map domains must agree')
    point=bg.pixels.point
    if any(not isinstance(v,V)or v.point!=point for v in [fg.pixels,reference196,person96,semantic7,roi.field5]):raise TypeError('Entire matching point/set backends required')
    if reference196.precision!='h'or reference196.lo.shape!=(3,)or person96.precision!='h'or person96.lo.shape!=()or semantic7.precision!='f'or semantic7.lo.shape!=(7,):raise TypeError('Actual reference196/person96 and full f32 semantic7 required')
    from leaf_numeric import mix
    uv6,uv7=roi.coordinates();a=sample_normalized(bg,uv6)[:3];b=sample_normalized(fg,uv7)[:3];p=semantic7.h()
    def branch(sample,ltm,hr):
        local=mix(sample,V.value(1,'h',point),ltm);return mix(local,local.minimum(1),hr)*reference196
    return {'output335':mix(branch(a,p[0],p[5]),branch(b,p[1],p[6]),person96),'sample305':a,'sample308':b,'uv296':uv6,'uv302':uv7}
