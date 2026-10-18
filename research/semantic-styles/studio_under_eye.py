"""Conditional UnderEye FinalMix, from macOS26A434 AIR0138:140-158.

This is the final convex blend only. The edited image, per-person statistics and
eye-region preparation are external context. It is not a complete Studio undo.
"""
import numpy as np

def weight(face,instance,hair,lips,ears,tattoo,glasses,blend,brightness_mix,strength):
    excluded=lips+ears+tattoo+glasses+hair
    return np.clip((face-excluded)*instance,0,1)*blend*brightness_mix*strength

def forward(original,edited,w):
    return original+(edited-original)*w[...,None]

def inverse(observed,edited,w,*,domain=(0.,1.25)):
    """An estimate plus conservative half-arithmetic intervals in a stated box.

    Native half weights are supplied by an independent 0/1 affine probe. The
    interval includes three half roundings, potential half subnormal flushing,
    and the final stored value. It assumes finite nonnegative domain/context;
    it is not a certified interval for the unobserved camera inputs/statistics.
    """
    y=np.asarray(observed,dtype='f8');e=np.asarray(edited,dtype='f8');w=np.asarray(w,dtype='f8')
    denominator=1-w;plateau=denominator<=2**-10
    near_black=np.min(y,axis=-1)<=1/255
    u=2**-11;gamma=3*u/(1-3*u);M=max(abs(domain[0]),abs(domain[1]))
    rho=gamma*(M+np.abs(w[...,None])*(M+abs(e)))+3*2**-14
    safe=np.where(plateau,1,denominator)[...,None]
    estimate=(y-w[...,None]*e)/safe
    low=np.maximum(domain[0],(y-w[...,None]*e-rho)/safe)
    high=np.minimum(domain[1],(y-w[...,None]*e+rho)/safe)
    low[plateau]=domain[0];high[plateau]=domain[1];estimate[plateau]=np.nan
    valid=~plateau&~near_black&np.isfinite(y).all(-1)&np.isfinite(e).all(-1)&(low<=high).all(-1)
    return {'candidate':estimate.astype('f4'),'valid':valid,'plateau':plateau,'near_black':near_black,'lower':low,'upper':high,'domain':domain,'camera_interval_verified':False}
