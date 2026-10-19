"""Exact existing resize/area definitions, reused only for new paired diagnostics."""
import numpy as np
def linear_resize(a,shape,top=0,stop=None):
 h,w=shape;stop=h if stop is None else stop;x=np.clip((np.arange(w,dtype='f8')+.5)*a.shape[1]/w-.5,0,a.shape[1]-1);y=np.clip((np.arange(top,stop,dtype='f8')+.5)*a.shape[0]/h-.5,0,a.shape[0]-1);ix=x.astype(int);iy=y.astype(int);fx=(x-ix)[None,:,None];fy=(y-iy)[:,None,None];v=np.asarray(a);a0=v[iy[:,None],ix[None,:]].astype('f4');b=v[iy[:,None],np.minimum(ix+1,a.shape[1]-1)[None,:]].astype('f4');c=v[np.minimum(iy+1,a.shape[0]-1)[:,None],ix[None,:]].astype('f4');d=v[np.minimum(iy+1,a.shape[0]-1)[:,None],np.minimum(ix+1,a.shape[1]-1)[None,:]].astype('f4');return((a0+(b-a0)*fx)*(1-fy)+(c+(d-c)*fx)*fy).astype('f4')
class AreaAccumulator:
 def __init__(self,shape,target,channels=3):
  self.h,self.w=shape;self.th,self.tw=target;self.c=channels;self.sx=self.w/self.tw;self.sy=self.h/self.th;edges=np.linspace(0,self.w,self.tw+1);self.ix=np.floor(edges).astype(int);self.fx=edges-self.ix;self.out=np.zeros((self.th,self.tw,channels),'f8')
 def add(self,top,v):
  v=np.maximum(np.asarray(v,dtype='f8'),0);n=len(v);p=np.concatenate([np.zeros((n,1,self.c)),np.cumsum(v,axis=1)],axis=1);i=p[:,self.ix]+v[:,np.minimum(self.ix,self.w-1)]*self.fx[None,:,None];row=np.diff(i,axis=1)/self.sx;sy=np.arange(top,top+n);t0=np.minimum((sy/self.sy).astype(int),self.th-1);t1=np.minimum(((sy+1)/self.sy).astype(int),self.th-1);w0=np.minimum(sy+1,(t0+1)*self.sy)-sy;np.add.at(self.out,t0,row*w0[:,None,None]);np.add.at(self.out,t1,row*(1-w0)[:,None,None])
 def result(self):return(self.out/self.sy).astype('f4')
