"""Reuse existing v3 three-pass model with an explicit bounded input contract.

Point reproduction reuses v3; conditional sets use the existing typed bounds.
No original-frame recovery is asserted. A scalar guide is broadcast in coefficients but uses R16 lanes in
apply; a single RGB call is not silently replaced by three scalar calls.
"""
from dataclasses import dataclass
import importlib.util
from pathlib import Path
import numpy as np
from leaf_numeric import V,DomainUnknown

LEGACY=Path(__file__).resolve().parents[1]/'hdr-native/guided_reference_v3.py'
spec=importlib.util.spec_from_file_location('psr_existing_guided_v3',LEGACY);legacy=importlib.util.module_from_spec(spec);spec.loader.exec_module(legacy)


@dataclass(frozen=True)
class Inputs:
    input_gain: np.ndarray
    guide: np.ndarray
    output_shape: tuple[int,int]
    radius: int
    epsilon_f32: np.float32
    working_domain: str

    def __post_init__(self):
        arrays=[]
        for raw in [self.input_gain,self.guide]:
            a=np.array(raw,dtype='f2',copy=True)
            if a.ndim!=3 or a.shape[2]not in(1,3,4)or min(a.shape[:2])<1 or max(a.shape[:2])>32 or not np.isfinite(a).all()or np.max(abs(a))>8:raise ValueError('Supplied finite half HxWx1/3/4, sides<=32 and abs<=8 required')
            a.flags.writeable=False;arrays.append(a)
        if arrays[1].shape[2]not in(1,arrays[0].shape[2]):raise ValueError('Guide must be scalar or match gain lanes')
        if not isinstance(self.output_shape,tuple)or len(self.output_shape)!=2 or any(type(x)is not int or not 1<=x<=32 for x in self.output_shape):raise TypeError('Exact bounded output grid required')
        if type(self.radius)is not int or self.radius!=1:raise ValueError('This caller contract covers original radius1 only')
        if type(self.epsilon_f32)is not np.float32 or not np.isfinite(self.epsilon_f32)or not 0<=self.epsilon_f32<=1:raise TypeError('Explicit finite raw epsilon f32 in[0,1] required')
        if not self.working_domain:raise ValueError('Identify the supplied gain/guide working domain')
        object.__setattr__(self,'input_gain',arrays[0]);object.__setattr__(self,'guide',arrays[1])


def forward(inputs: Inputs):
    with np.errstate(invalid='ignore',divide='ignore',over='ignore'):
        a,b,ma,mb=legacy.coefficients(inputs.input_gain,inputs.guide,inputs.radius,inputs.epsilon_f32)
        out=legacy.apply(inputs.guide,ma,mb,inputs.output_shape)
    results={'a':a,'b':b,'mean_a':ma,'mean_b':mb,'output':out}
    if any(not np.isfinite(x).all()for x in results.values()):raise DomainUnknown('Guided v3 finite domain failed; no epsilon change or center fallback')
    return results


def forward_set(inputs,*,gain=None,guide=None,epsilon=None):
    """Propagate whole half input boxes and supplied f32 epsilon, never centers.

    Fixed grids/sampler weights follow the declared v3 CPU sampler. Existing
    2u/4u operation bounds are assumptions; no GPU interpolation bound follows.
    Dependency loss may make the variance denominator include zero: reject it.
    """
    gain=V.bounds(inputs.input_gain,inputs.input_gain)if gain is None else gain
    guide=V.bounds(inputs.guide,inputs.guide)if guide is None else guide
    epsilon=V.bounds(inputs.epsilon_f32,inputs.epsilon_f32,'f')if epsilon is None else epsilon
    for v,shape in [(gain,inputs.input_gain.shape),(guide,inputs.guide.shape)]:
        if not isinstance(v,V)or v.point or v.precision!='h'or v.lo.shape!=shape:raise TypeError('Matching entire half image sets required')
        if np.max(np.maximum(abs(v.lo),abs(v.hi)))>8:raise DomainUnknown('Input set exceeds declared abs<=8 domain')
    if not isinstance(epsilon,V)or epsilon.point or epsilon.precision!='f'or epsilon.lo.shape!=()or epsilon.lo<0 or epsilon.hi>1:raise TypeError('Explicit epsilon f32 set in[0,1] required')
    def constant(a):return V.value(a,'f',False)
    def broadcast(v,c):return V(np.broadcast_to(v.lo,(*v.lo.shape[:2],c)),np.broadcast_to(v.hi,(*v.hi.shape[:2],c)),'f',False)
    def sample(v,x,y):
        h,w=v.lo.shape[:2];x,y=np.broadcast_arrays(np.asarray(x,'f4'),np.asarray(y,'f4'));ix=np.floor(x).astype('i4');iy=np.floor(y).astype('i4');fx=(np.rint((x-ix)*256)/256).astype('f4');fy=(np.rint((y-iy)*256)/256).astype('f4');x0=np.clip(ix,0,w-1);x1=np.clip(ix+1,0,w-1);y0=np.clip(iy,0,h-1);y1=np.clip(iy+1,0,h-1)
        a=v[y0,x0].f();b=v[y0,x1].f();c=v[y1,x0].f();d=v[y1,x1].f();wx=constant(fx[...,None]);wy=constant(fy[...,None]);top=a+(b-a)*wx;bottom=c+(d-c)*wx
        return (top+(bottom-top)*wy).h().f()
    def normalized(v,x,y):return sample(v,np.asarray(x,'f4')*np.float32(v.lo.shape[1])-np.float32(.5),np.asarray(y,'f4')*np.float32(v.lo.shape[0])-np.float32(.5))
    h,w=guide.lo.shape[:2];c=gain.lo.shape[2];x=np.arange(w,dtype='f4')[None,:];y=np.arange(h,dtype='f4')[:,None];zero=constant(np.zeros((h,w,c)));sp=zero;si=zero;sip=zero;sii=zero
    for dx in range(-1,2):
        for dy in range(-1,2):
            ux=(x+np.float32(.5+dx))/np.float32(w);uy=(y+np.float32(.5+dy))/np.float32(h);pv=normalized(gain,ux,uy);iv=broadcast(normalized(guide,ux,uy),c)
            sp=pv+sp;si=iv+si;sip=iv*pv+sip;sii=iv.square()+sii
    # Follow actual AIR58 epsilon+mii-mi² order, preserving both appearances
    # of each mean_i via square() rather than independent interval products.
    mp=sp/9;mi=si/9;mip=sip/9;mii=sii/9;cov=mip-mp*mi;var=(epsilon+mii)-mi.square();av=cov/var;a=av.h();b=(mp-av*mi).h()
    sa=zero;sb=zero
    for dx in range(-1,2):
        for dy in range(-1,2):sa=sa+sample(a,x+np.float32(dx),y+np.float32(dy));sb=sb+sample(b,x+np.float32(dx),y+np.float32(dy))
    ma=(sa/9).h();mb=(sb/9).h();oh,ow=inputs.output_shape;ux=(np.arange(ow,dtype='f4')[None,:]+np.float32(.5))/np.float32(ow);uy=(np.arange(oh,dtype='f4')[:,None]+np.float32(.5))/np.float32(oh)
    av=normalized(ma,ux,uy);bv=normalized(mb,ux,uy);iv=normalized(guide,ux,uy)
    if guide.lo.shape[2]==1 and c>1:
        lo=np.zeros((oh,ow,c));hi=lo.copy();lo[...,0]=iv.lo[...,0];hi[...,0]=iv.hi[...,0]
        if c==4:lo[...,3]=1;hi[...,3]=1
        iv=V(lo,hi,'f',False)
    return {'a':a,'b':b,'mean_a':ma,'mean_b':mb,'output':(iv*av+bv).h()}
