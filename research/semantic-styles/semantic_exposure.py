"""Separate directional face/body exposure estimates, not an Apple calibration.

Use on a macOS runner for image-sized arrays. Work in chunks for a large image.
The caller supplies its linear RGB image and already-aligned continuous masks.
Neither j nor a base+gain-map file identifies these spatial exposure budgets.
"""
import numpy as np

def remove(rgb,weight,*,budget_ev):
    """Scalar RGB gain: neutral in chromaticity, bounded by chosen budget.

    A negative budget adds light. An EV budget is a caller-selected hypothesis,
    not a certified camera interval. Call separately for face and body outputs;
    zero budget is the identity. Original encoded SDR is never modified here.
    """
    x=np.asarray(rgb,dtype='f4');w=np.asarray(weight,dtype='f4')
    if w.shape!=x.shape[:-1]:raise ValueError('Aligned mask and RGB shapes differ')
    if x.size>65536*3:raise ValueError('Pass <=65536 pixels per chunk; image work belongs on the macOS runner')
    if not np.isfinite(budget_ev) or not np.isfinite(w).all():raise ValueError('Finite budget/mask required')
    log2_gain=-np.float32(budget_ev)*np.clip(w,0,1)
    result=x*np.exp2(log2_gain)[...,None]
    return {'rgb':result,'log2_gain':log2_gain,'near_black_mask':np.min(x,axis=-1)<=1/255,'camera_calibrated':False,'scene_referred_verified':False}

def reapply(rgb,log2_gain):
    """Self-consistency inverse of the selected estimate, not camera forward."""
    return np.asarray(rgb,dtype='f4')*np.exp2(-np.asarray(log2_gain,dtype='f4'))[...,None]
