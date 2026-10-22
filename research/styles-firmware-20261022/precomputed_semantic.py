"""AIR10 block290, explicit texture6/7 inputs; not fallback equivalence.

The two already prepared RGB triplet textures are sampled in normalized
coordinates. There is no new CCM/GTC/exposure multiplication inside this block.
Ideal CPU bilinear/clamp sampling remains an explicit non-GPU assumption.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from negative_tone import B
from semantic_tone import I,imix,coefficients7,SemanticSetResult


@dataclass(frozen=True)
class Texture2D:
    values: np.ndarray
    working_domain: str

    def __post_init__(self):
        a=np.array(self.values,dtype='f2',copy=True)
        if a.ndim!=3 or a.shape[2]!=3 or min(a.shape[:2])<1 or max(a.shape[:2])>1024 or not np.isfinite(a).all()or np.max(abs(a))>8 or not self.working_domain:
            raise ValueError('Explicit finite half HxWx3 texture <=1024 each side, abs<=8, named working domain required')
        a.flags.writeable=False;object.__setattr__(self,'values',a)

    def sample(self,uv):
        h,w,_=self.values.shape;u,v=map(np.float32,uv)
        # Shader uses normalized sampler .3; edge clamp is applied to indices.
        x=np.minimum(np.maximum(np.float32(u*np.float32(w)-np.float32(.5)),0),w-1)
        y=np.minimum(np.maximum(np.float32(v*np.float32(h)-np.float32(.5)),0),h-1)
        i,j=int(np.floor(x)),int(np.floor(y));ii,jj=min(i+1,w-1),min(j+1,h-1)
        fx,fy=np.float32(x-i),np.float32(y-j);a=self.values[j,i].astype('f4');b=self.values[j,ii].astype('f4');c=self.values[jj,i].astype('f4');d=self.values[jj,ii].astype('f4')
        top=np.add(a,np.multiply(np.subtract(b,a,dtype='f4'),fx,dtype='f4'),dtype='f4')
        bottom=np.add(c,np.multiply(np.subtract(d,c,dtype='f4'),fx,dtype='f4'),dtype='f4')
        return np.add(top,np.multiply(np.subtract(bottom,top,dtype='f4'),fy,dtype='f4'),dtype='f4').astype('f2')

    def range(self,low,high):
        h,w,_=self.values.shape
        x=np.clip(np.array([low[0],high[0]])*w-.5,0,w-1);y=np.clip(np.array([low[1],high[1]])*h-.5,0,h-1)
        # Every bilinear output is a convex combination of these texel nodes;
        # including full boundary texels is conservative, not a tight range.
        part=self.values[int(np.floor(y[0])):int(np.ceil(y[1]))+1,int(np.floor(x[0])):int(np.ceil(x[1]))+1].astype('f8')
        return I(np.min(part,axis=(0,1)),np.max(part,axis=(0,1)))


@dataclass(frozen=True)
class PrecomputedInputs:
    grid: tuple[int,int]
    texture6: Texture2D
    texture7: Texture2D
    roi_field5: tuple[float,float,float,float]
    roi_field6: tuple[float,float,float,float]
    reference_rgb: tuple[float,float,float]
    person_weight: float

    def validate(self):
        if len(self.grid)!=2 or any(type(x)is not int or not 0<=x<=65535 for x in self.grid):raise ValueError('Exact uint16 grid coordinates required')
        roi=np.array([self.roi_field5,self.roi_field6],dtype='f4');ref=np.array(self.reference_rgb,dtype='f2');person=np.float16(self.person_weight)
        if roi.shape!=(2,4)or not np.isfinite(roi).all()or np.max(abs(roi))>16 or ref.shape!=(3,)or not np.isfinite(ref).all()or np.max(abs(ref))>2 or not 0<=person<=1:
            raise ValueError('Supplied bounded f32 ROI, half reference RGB and person weight required')
        if self.texture6.working_domain!=self.texture7.working_domain:raise ValueError('The two supplied precomputed textures must identify the same working domain')
        return roi,ref,person

    def coordinates(self):
        roi,_,_=self.validate();p=np.add(np.array(self.grid,dtype='f4'),np.float32(.5),dtype='f4')
        return [np.add(np.multiply(r[:2],p,dtype='f4'),r[2:],dtype='f4')for r in roi]

    def coordinate_ranges(self):
        roi,_,_=self.validate();p=np.add(np.array(self.grid,dtype='f4'),np.float32(.5),dtype='f4');result=[]
        for r in roi:
            coords=[B(float(a))*B(float(b))+B(float(c))for a,b,c in zip(r[:2],p,r[2:])]
            result.append(([x.lo for x in coords],[x.hi for x in coords]))
        return result


def forward_half(inputs: PrecomputedInputs,values):
    _,reference,person=inputs.validate();p=coefficients7(values).astype('f2');uv6,uv7=inputs.coordinates()
    sample6=inputs.texture6.sample(uv6);sample7=inputs.texture7.sample(uv7)
    def h(a):
        a=np.asarray(a,dtype='f2')
        if not np.isfinite(a).all():raise ValueError('Nonfinite half intermediate; unknown')
        return a
    def mix(a,b,w):return h(h(a)+h(h(h(b)-h(a))*h(w)))
    bg=mix(sample6,h(1),p[0]);bg=h(mix(bg,np.minimum(bg,h(1)),p[5])*reference)
    fg=mix(sample7,h(1),p[1]);fg=h(mix(fg,np.minimum(fg,h(1)),p[6])*reference)
    return mix(bg,fg,person)


def forward_set(inputs: PrecomputedInputs,lower,upper,*,input_branches=()):
    _,reference,person=inputs.validate();lo=coefficients7(lower,dtype='f8');hi=coefficients7(upper,dtype='f8')
    if np.any(lo>hi):raise ValueError('Ordered coefficient intervals required')
    p=I.half_cast(lo,hi);coords=inputs.coordinate_ranges()
    samples=[texture.range(*bounds)for texture,bounds in zip([inputs.texture6,inputs.texture7],coords)]
    def get(n):return I(p.lo[n],p.hi[n])
    def branch(sample,ltm,hr):
        local=imix(sample,1,ltm);return imix(local,local.minimum_one(),hr)*reference.astype('f8')
    out=imix(branch(samples[0],get(0),get(5)),branch(samples[1],get(1),get(6)),float(person))
    return SemanticSetResult(out.lo,out.hi,tuple(input_branches))
