"""Readable continuous limit of consumer AIR renderSkinAdjustments.

This is not a fitted camera inverse and deliberately does not change the frozen
consumer model. Parameters are numbered by the AIR SSRFGAdjustment layout.
Input is the kernel's working RGB, not an assumed scene-linear P3 space.
Native half rounding and fast-math are not claimed by this float implementation.
"""
import numpy as np

AIR_SHA256='9ce57aea2bcc11021cf04ce4b44f57ac83270b0722283c7860436c3ec4d523c1'
AIR_LINES=(4375,4504)

def forward(x,skin_weight,guide,theta9,theta10):
 x=np.asarray(x,dtype='f4');m=np.broadcast_to(skin_weight,x.shape[:-1])[...,None];g=np.broadcast_to(guide,x.shape[:-1]);y=x.copy()
 if abs(theta10)>=1e-5:
  v=np.clip(x,0,1);root=np.sqrt(v);l=np.sqrt(np.sum(v*np.float32(.333252),axis=-1));a=l*(1-l)*np.float32(theta10);rg=np.sqrt(g)
  offset=2*a*(np.sum(root*np.array([.299,.587,.114],dtype='f4'),axis=-1)-rg)
  branch0=root+(rg[...,None]-root)*(-2*a[...,None])
  branch1=root+offset[...,None]
  root_out=branch0+(branch1-branch0)*np.float32(.799805)
  exterior=np.minimum(x,0)+np.maximum(x,1)-1
  y=np.maximum(x,exterior+np.maximum(root_out,0)**2)
 if abs(theta9)>=1e-5:
  rgb_sum=np.sum(y,axis=-1)
  with np.errstate(divide='ignore',invalid='ignore'):norm=y/rgb_sum[...,None]
  lum=np.sum(y*np.array([.5,.300049,.199951],dtype='f4'),axis=-1)
  a=np.clip((lum-np.float32(.399902))*np.float32(1.66602),0,1)
  b=np.clip((np.maximum(norm[...,0],norm[...,1])+np.maximum(norm[...,1],norm[...,2])-np.float32(.333252))*np.float32(1.49902),0,1)
  w=np.minimum(2*np.float32(theta9)*a*a*(3-2*a)*(1-b*b*(3-2*b)),1)
  c=np.array([1.,.700195,.549805],dtype='f4');c=np.where(c>.0404358,((c+.0549927)*.948242)**2.40039,c*.0773925)
  y=y+(y*c-y)*w[...,None]
 return x+(y-x)*m

def inverse(target,skin_weight,guide,theta9,theta10,*,iterations=15,step=2e-3):
 """Chunk-sized Newton candidate. Residual validity never certifies uniqueness.

 Caller must supply actual captured context and handle large images on macOS.
 Unconstrained/missing-context camera pixels have no finite certified bounds.
 """
 y=np.asarray(target,dtype='f4');shape=y.shape;x=y.reshape(-1,3).copy();mask=np.broadcast_to(skin_weight,shape[:-1]).reshape(-1);guide=np.broadcast_to(guide,shape[:-1]).reshape(-1)
 if x.shape[0]>65536:raise ValueError('Pass a chunk of <=65536 pixels; full-frame work belongs on the macOS runner')
 def f(a):return forward(a,mask,guide,theta9,theta10)
 singular=np.zeros(x.shape[0],bool)
 for _ in range(iterations):
  base=f(x);res=base-y.reshape(-1,3);jac=np.empty((len(x),3,3),dtype='f4')
  for c in range(3):
   delta=np.zeros_like(x);delta[:,c]=step;jac[:,:,c]=(f(x+delta)-f(x-delta))/(2*step)
  det=np.linalg.det(jac);bad=(np.abs(det)<1e-5)|~np.isfinite(jac).all((1,2));singular|=bad;jac[bad]=np.eye(3,dtype='f4')
  update=np.linalg.solve(jac,res[...,None])[...,0];update[bad]=0
  old=np.max(abs(res),axis=-1);origin=x.copy()
  for damping in [1.,.5,.25,.125]:
   z=origin-damping*update;loss=np.max(abs(f(z)-y.reshape(-1,3)),axis=-1);better=loss<old
   x[better]=z[better];old[better]=loss[better]
  if np.max(abs(f(x)-y.reshape(-1,3)))<=1e-6:break
 out=f(x);valid=np.isfinite(out).all(-1)&np.isfinite(x).all(-1)&(np.min(y.reshape(-1,3),axis=-1)>1/255)
 relative=np.max(abs(out-y.reshape(-1,3))/np.maximum(abs(y.reshape(-1,3)),1e-12),axis=-1);valid&=(relative<=1e-3)&~singular
 return {'candidate':x.reshape(shape),'residual_valid_mask':valid.reshape(shape[:-1]),'singular_mask':singular.reshape(shape[:-1]),'camera_unique_inverse_verified':False,'interval_lower':None,'interval_upper':None,'interval_reason':'No finite certified camera interval without original context/quantization bounds; a residual mask is not a uniqueness mask.'}
