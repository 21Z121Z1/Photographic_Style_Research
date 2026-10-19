"""AIR 0142/0143/0144 CMIGuidedFilter replay, tiled and precision-explicit.

The coefficient grid is the GUIDE grid, not the low-resolution input grid.
The coefficient pass broadcasts a scalar guide, but the apply pass uses Metal
R16 texture lanes [r,0,0,1]. RGB gains need three R16 calls or an RGB guide.
Radius is in guide pixels.
This file does not claim native bit exactness until oracle results establish it.
"""
from pathlib import Path
import numpy as np

def fma(a,b,c):return(np.asarray(a,dtype='f8')*np.asarray(b,dtype='f8')+np.asarray(c,dtype='f8')).astype('f4')
def sample(image,x,y):
 a=np.asarray(image);x=np.asarray(x,'f4');y=np.asarray(y,'f4');x,y=np.broadcast_arrays(x,y);ix=np.floor(x).astype('i4');iy=np.floor(y).astype('i4');fx=(np.rint((x-ix)*256)/256).astype('f4');fy=(np.rint((y-iy)*256)/256).astype('f4');h,w=a.shape[:2];x0=np.clip(ix,0,w-1);x1=np.clip(ix+1,0,w-1);y0=np.clip(iy,0,h-1);y1=np.clip(iy+1,0,h-1)
 if a.ndim==2:a=a[...,None]
 q00=a[y0,x0].astype('f4');q10=a[y0,x1].astype('f4');q01=a[y1,x0].astype('f4');q11=a[y1,x1].astype('f4');top=fma(q10-q00,fx[...,None],q00);bot=fma(q11-q01,fx[...,None],q01);raw=fma(bot-top,fy[...,None],top);rounded=raw.astype('f2');up=np.nextafter(rounded,np.float16(np.inf));tie=(raw.astype('f8')==(rounded.astype('f8')+up.astype('f8'))*.5)&(raw>rounded);return np.where(tie,up,rounded).astype('f4')
def normalized_sample(image,uvx,uvy):return sample(image,np.asarray(uvx,'f4')*np.float32(image.shape[1])-np.float32(.5),np.asarray(uvy,'f4')*np.float32(image.shape[0])-np.float32(.5))
def allocate(path,shape,dtype='f2'):
 if path is None:return np.empty(shape,dtype)
 return np.lib.format.open_memmap(path,mode='w+',dtype=dtype,shape=shape)
def coefficients(p,guide,radius=1,epsilon=.05,out_dir=None,rows=64):
 p=np.asarray(p);guide=np.asarray(guide);p=p[...,None]if p.ndim==2 else p;guide=guide[...,None]if guide.ndim==2 else guide;h,w=guide.shape[:2];c=p.shape[-1]
 if guide.shape[-1]not in(1,c):raise ValueError('Guide must be scalar or one component per input component')
 if out_dir:out_dir=Path(out_dir);out_dir.mkdir(parents=True,exist_ok=True)
 a=allocate(out_dir/'a.npy'if out_dir else None,(h,w,c));b=allocate(out_dir/'b.npy'if out_dir else None,(h,w,c));count=np.float32((2*radius+1)**2);inv=np.float32(1)/count
 for start in range(0,h,rows):
  end=min(h,start+rows);x=np.arange(w,dtype='f4')[None,:];y=np.arange(start,end,dtype='f4')[:,None];shape=(end-start,w,c);sp=np.zeros(shape,'f4');si=np.zeros(shape,'f4');sip=np.zeros(shape,'f4');sii=np.zeros(shape,'f4')
  for dx in range(-radius,radius+1):
   for dy in range(-radius,radius+1):
    ux=(x+np.float32(.5+dx))/np.float32(w);uy=(y+np.float32(.5+dy))/np.float32(h);pv=normalized_sample(p,ux,uy);iv=normalized_sample(guide,ux,uy);sp+=pv;si+=iv;sip=fma(iv,pv,sip);sii=fma(iv,iv,sii)
  mp=sp*inv;mi=si*inv;mip=sip*inv;mii=sii*inv;cov=fma(-mi,mp,mip);var=fma(-mi,mi,mii)+np.float32(epsilon);av=(cov/var).astype('f4');bv=fma(-av,mi,mp);a[start:end]=av.astype('f2');b[start:end]=bv.astype('f2')
 ma=allocate(out_dir/'mean_a.npy'if out_dir else None,(h,w,c));mb=allocate(out_dir/'mean_b.npy'if out_dir else None,(h,w,c))
 for start in range(0,h,rows):
  end=min(h,start+rows);sa=np.zeros((end-start,w,c),'f4');sb=np.zeros_like(sa);xx=np.arange(w)[None,:];yy=np.arange(start,end)[:,None]
  for dx in range(-radius,radius+1):
   for dy in range(-radius,radius+1):
    ix=np.clip(xx+dx,0,w-1);iy=np.clip(yy+dy,0,h-1);sa+=a[iy,ix].astype('f4');sb+=b[iy,ix].astype('f4')
  ma[start:end]=(sa*inv).astype('f2');mb[start:end]=(sb*inv).astype('f2')
 return a,b,ma,mb

def apply(guide,mean_a,mean_b,shape=None,out=None,rows=64):
 h,w=shape or guide.shape[:2];c=mean_a.shape[-1];result=allocate(out,(h,w,c));x=(np.arange(w,dtype='f4')[None,:]+np.float32(.5))/np.float32(w)
 for start in range(0,h,rows):
  end=min(h,start+rows);y=(np.arange(start,end,dtype='f4')[:,None]+np.float32(.5))/np.float32(h);a=normalized_sample(mean_a,x,y);b=normalized_sample(mean_b,x,y);i=normalized_sample(guide,x,y)
  if i.shape[-1]==1 and c>1:
   lanes=np.zeros(i.shape[:-1]+(c,),dtype='f4');lanes[...,0]=i[...,0]
   if c==4:lanes[...,3]=1
   i=lanes
  result[start:end]=fma(i,a,b).astype('f2')
 return result

def upsample(p,guide,shape=None,radius=1,epsilon=.05,out_dir=None,rows=64):
 a,b,ma,mb=coefficients(p,guide,radius,epsilon,out_dir,rows);return apply(guide,ma,mb,shape,Path(out_dir)/'output.npy'if out_dir else None,rows)
