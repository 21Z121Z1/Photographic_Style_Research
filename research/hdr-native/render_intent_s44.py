"""Independent display intent. Input master and Apple Log remain untouched.

No spatial operator or inferred camera correction is hidden in this renderer.
This is a declared creative/global display transform, not physical calibration.
"""
import numpy as np
Y=np.array([.2289745641,.6917385218,.0792869141],dtype='f8')
def exposure_intent(master_sample,sdr_sample):
 m=np.asarray(master_sample,dtype='f8');s=np.asarray(sdr_sample,dtype='f8');a=m@Y;b=s@Y;mask=np.isfinite(a)&np.isfinite(b)&(a>0)&(b>0)
 if not mask.any():raise ValueError('No finite positive luminance exposure anchors')
 ev=float(np.median(np.log2(b[mask]/a[mask])));return {'display_exposure_EV':ev,'scale':float(np.exp2(ev)),'statistic_pixels':int(mask.sum()),'sample_pixels':int(mask.size),'scope':'One global display scale from fixed sample-grid median, not a scene exposure or white-level measurement'}
def hdr_intent(master,scale,headroom=8):
 m=np.asarray(master,dtype='f8');a=m*scale;y=a@Y;return a*np.divide(headroom,headroom+np.maximum(y,0))[...,None]
def supplied_pair_log(sdr,hdr,offset):
 s=np.asarray(sdr,dtype='f8');h=np.asarray(hdr,dtype='f8');den=s+offset;num=h+offset;mask=np.isfinite(den).all(-1)&np.isfinite(num).all(-1)&(den.min(-1)>0)&(num.min(-1)>0);result=np.zeros_like(s);np.log2(np.divide(num,den,out=np.ones_like(s),where=mask[...,None]),out=result,where=mask[...,None]);return result,mask
