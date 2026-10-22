"""Matched ARM64 CPU contraction of AIR90, retaining legacy sampler/apply.

This host contract is demonstrated by saved f32 checkpoints. Fast AIR permits
other evaluation orders on iOS/GPU; this is not a universal bit-exact claim.
"""
import numpy as np


def stages(p,guide,epsilon,legacy):
    h,w=guide.shape[:2];c=p.shape[-1];x=np.arange(w,dtype='f4')[None,:];y=np.arange(h,dtype='f4')[:,None];sp=np.zeros((h,w,c),'f4');si=sp.copy();sip=sp.copy();sii=sp.copy()
    for dx in range(-1,2):
        for dy in range(-1,2):
            ux=(x+np.float32(.5+dx))/np.float32(w);uy=(y+np.float32(.5+dy))/np.float32(h);pv=legacy.normalized_sample(p,ux,uy);iv=legacy.normalized_sample(guide,ux,uy);sp+=pv;si+=iv;sip=legacy.fma(iv,pv,sip);sii=legacy.fma(iv,iv,sii)
    inv=np.float32(1/9);mp=sp*inv;mi=si*inv;mip=sip*inv;mii=sii*inv;cov=legacy.fma(-mi,mp,mip)
    # Host contracts SSA50*reciprocal into SSA56 before the f32 rounding of
    # mean_ii. The previous v3 path rounded mii, then added epsilon after var.
    ep=legacy.fma(sii,inv,np.float32(epsilon));var=legacy.fma(-mi,mi,ep);a=(cov/var).astype('f4');b=legacy.fma(-a,mi,mp)
    return dict(zip(['sum_p','sum_i','sum_ip','sum_ii','mean_p','mean_i','mean_ip','mean_ii','cov','epsilon_plus_mii','var','a_f32','b_f32'],[sp,si,sip,sii,mp,mi,mip,mii,cov,ep,var,a,b]))


def coefficients(p,guide,epsilon,legacy):
    d=stages(p,guide,epsilon,legacy);a=d['a_f32'].astype('f2');b=d['b_f32'].astype('f2');h,w=a.shape[:2];xx=np.arange(w)[None,:];yy=np.arange(h)[:,None];sa=np.zeros(a.shape,'f4');sb=sa.copy()
    for dx in range(-1,2):
        for dy in range(-1,2):
            ix=np.clip(xx+dx,0,w-1);iy=np.clip(yy+dy,0,h-1);sa+=a[iy,ix].astype('f4');sb+=b[iy,ix].astype('f4')
    inv=np.float32(1/9)
    return a,b,(sa*inv).astype('f2'),(sb*inv).astype('f2')
