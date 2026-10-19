"""Chunked numerical reference for the pinned Apple _flexMap kernel.

This module transports an independently supplied target. It does not derive a
scene, infer missing operator parameters, or remove local tone mapping by itself.
Run image calculations on the macOS runner; callers stream bounded tiles.
"""
import numpy as np

def gain_from_pair(sdr,hdr,*,offset_sdr,offset_hdr):
 s=np.asarray(sdr,dtype='f8');h=np.asarray(hdr,dtype='f8')
 if s.shape!=h.shape or s.shape[-1]!=3:raise ValueError('Matching linear RGB tiles required')
 if s.size>3*262144:raise ValueError('Tile exceeds262144 pixels; stream rows on runner')
 # The native generator clips negative RGB before taking a ratio. That loss
 # cannot be reversed by applying the ratio to the original signed RGB.
 si=np.maximum(s,0)+np.asarray(offset_sdr);ho=np.maximum(h,0)+np.asarray(offset_hdr);valid=np.isfinite(si).all(-1)&np.isfinite(ho).all(-1)&(si.min(-1)>0)&(ho.min(-1)>0)&(s.min(-1)>=0)&(h.min(-1)>=0)
 loggain=np.full_like(si,np.nan);np.log2(np.divide(ho,si,out=np.ones_like(si),where=valid[...,None]),out=loggain,where=valid[...,None])
 return {'log2_gain':loggain,'positive_ratio_mask':valid,'negative_base_component_mask':np.any(s<0,-1),'negative_target_component_mask':np.any(h<0,-1),'scope':'Pinned flexMapLinGainRGB positive-component convention; negative color loss must be reported separately'}

def apply_decoded_map(sdr,gain_code,*,inverse_gamma,gain_min,gain_max,scale,offset_sdr,offset_hdr):
 """Native equation AFTER texture sampling in the correct image coordinates.

 _s_pow(x,g)=sign(x)*pow(max(abs(x),1e-6),g). No hidden resizing or finalclip.
 Sampler/coordinate order must come from native evidence, not this function.
 """
 s=np.asarray(sdr,dtype='f8');g=np.asarray(gain_code,dtype='f8')
 if s.shape!=g.shape or s.shape[-1]!=3 or s.size>3*262144:raise ValueError('Matching bounded RGB tiles required')
 if not np.isfinite(scale) or not 0<=scale<=1:raise ValueError('Native application scale required in[0,1]')
 transformed=np.sign(g)*np.power(np.maximum(abs(g),1e-6),np.asarray(inverse_gamma));loggain=(np.asarray(gain_max)-np.asarray(gain_min))*transformed+np.asarray(gain_min)
 return np.exp2(scale*loggain)*(s+np.asarray(offset_sdr))-np.asarray(offset_hdr)

def iso_scale(display_headroom,*,capacity_min_log2,capacity_max_log2):
 """ISO/UltraHDR reference only; verify native metadata uses this convention."""
 if display_headroom<1 or not np.isfinite(display_headroom) or capacity_max_log2<=capacity_min_log2:raise ValueError('Valid declared headroom interval required')
 return float(np.clip((np.log2(display_headroom)-capacity_min_log2)/(capacity_max_log2-capacity_min_log2),0,1))
