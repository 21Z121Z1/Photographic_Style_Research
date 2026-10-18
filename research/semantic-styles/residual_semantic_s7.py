"""Isolate semantic removal error from an imperfect whole-consumer preimage.

Reuses immutable S5 native captures; no forward model is retuned. The corrected
estimate is y + F_neutral(x_hat) - F_actual(x_hat), instead of F_neutral(x_hat).
Original native input is used only for diagnostics/expected counterfactuals.
"""
from pathlib import Path
import sys,json,hashlib
import numpy as np
from PIL import Image
import PyOpenColorIO as ocio
R=Path(sys.argv[1]);O=Path(sys.argv[2]);O.mkdir(exist_ok=True);S=R/'consumer-toneP035/semantic'
shape=(384,512,4)
def half(p):return np.fromfile(p,'f2').reshape(shape)[...,:3].astype('f4')
def digest(x):return hashlib.sha256(x.tobytes()).hexdigest()
y=half(S/'native.f16');rt=half(S/'native-inverse-roundtrip.f16');original=half(S/'texture-0.bin');recovered=np.fromfile(S/'native-inverse-rgb.f32','f4').reshape(384,512,3)
eligible=np.fromfile(S/'native-inverse-eligible.u8','u1').reshape(384,512).astype(bool)
relative=np.fromfile(S/'native-inverse-relative.f32','f4').reshape(384,512);failed=eligible&(relative>1e-3)
m=np.fromfile(S/'texture-11.bin','f2').reshape(384,512).astype('f4')
pad=np.pad(m,1,mode='edge');mx=np.maximum.reduce([pad[a:a+384,b:b+512] for a in range(3) for b in range(3)]);mn=np.minimum.reduce([pad[a:a+384,b:b+512] for a in range(3) for b in range(3)])
regions={'all_eligible':eligible,'skin_nonzero':eligible&(m>0),'skin_interior':eligible&(m>.5),'skin_soft':eligible&(m>0)&(m<=.5),'matte_edge':eligible&((mx-mn)>1/255),'outside_skin_footprint':eligible&(mx==0),'original_outside_solver_box':eligible&np.any((original<2**-20)|(original>1.25),-1),'recovered_at_bound':eligible&np.any((recovered<=2**-20*1.05)|(recovered>=1.249),-1)}
def stats(a,b,region):
 d=abs(a-b);q=np.max(d/np.maximum(abs(b),1e-12),-1);r=region&np.isfinite(a).all(-1)&np.isfinite(b).all(-1)
 if not r.any():return {'pixels':0}
 lum=lambda t:np.sum(t*np.array([.22897456,.69173852,.07928691],dtype='f4'),-1)
 ev_valid=r&(lum(a)>0)&(lum(b)>0);ev=np.log2(lum(a)[ev_valid]/lum(b)[ev_valid])
 return {'pixels':int(r.sum()),'coverage_of_frame':float(r.mean()),'max_abs':float(d[r].max()),'max_relative':float(q[r].max()),'relative_p99':float(np.quantile(q[r],.99)),'failed_relative_1e3':int(np.count_nonzero(r&(q>1e-3))),'psnr_peak1_db':float(-10*np.log10(np.mean(d[r].astype('f8')**2))) if d[r].any() else 'inf','ev_mae':float(np.mean(abs(ev))) if len(ev) else None,'ev_max_abs':float(np.max(abs(ev))) if len(ev) else None}
diag=[]
for name,r in regions.items():
 diag.append({'region':name,'pixels':int(r.sum()),'S5_failed':int(np.count_nonzero(failed&r)),'S5_failure_rate':float(np.mean(failed[r])) if r.any() else None,'S5_relative_p50':float(np.median(relative[r])) if r.any() else None,'S5_relative_p99':float(np.quantile(relative[r],.99)) if r.any() else None,'recovered_preimage_vs_original':stats(recovered,original,r)})
cfg=ocio.Config.CreateFromBuiltinConfig('cg-config-v2.2.0_aces-v1.3_ocio-v2.4');proc=cfg.getProcessor('Linear P3-D65','sRGB - Display','ACES 1.0 - SDR Video',ocio.TRANSFORM_DIR_FORWARD).getDefaultCPUProcessor();integrity=[]
def preview(a,name):
 h=digest(a);b=np.array(a,dtype='f4',order='C',copy=True);proc.apply(ocio.PackedImageDesc(b,512,384,3));im=Image.fromarray(np.rot90(np.round(255*np.clip(b,0,1)).astype('u1'),3));im.thumbnail((512,512));im.save(O/(name+'-ACES.png'));assert h==digest(a);integrity.append({'image':name,'before':h,'after':digest(a)})
preview(y,'reference');trials=[]
for op in ['skin-color','skin-brightness','skin-both']:
 old=half(S/(op+'-removed-estimate.f16'));expected=half(S/(op+'-removed-oracle.f16'));delta=old-rt;corrected=y+delta
 # No clipping, per-channel rescaling or masking conceals errors. A genuine
 # zero operator delta remains an exact identity outside its spatial support.
 fixed=(delta==0).all(-1);unaffected=(expected==y).all(-1)
 row={'operator':op,'old_vs_native_oracle':{k:stats(old,expected,r) for k,r in regions.items()},'residual_corrected_vs_native_oracle':{k:stats(corrected,expected,r) for k,r in regions.items()},'unaffected_oracle_pixels':int(unaffected.sum()),'spurious_changed_pixels_in_unaffected_oracle':int(np.count_nonzero(unaffected&~fixed)),'outside_skin_footprint_max_change':float(abs(corrected[mx==0]-y[mx==0]).max()) if np.any(mx==0) else None,'input_original_used_as_inverse_seed':False,'camera_undo_verified':False}
 positive=(np.min(y,axis=-1)>0)&(np.min(corrected,axis=-1)>0)&np.isfinite(corrected).all(-1)
 lg=np.zeros_like(corrected);lg[positive]=np.log2(corrected[positive]/y[positive]);row['positive_gain_map_coverage']=float(positive.mean())
 np.savez_compressed(O/(op+'-residual-estimate.npz'),rgb=corrected,log2_gain=lg,gain_valid=positive,old_solver_failed=failed,skin_weight=m)
 preview(expected,op+'-oracle');preview(corrected,op+'-residual');trials.append(row)
# Only the previously unarchived half-budget sensitivity previews are added.
base=np.fromfile(R/'consumer-tone0/primary_input.f32','f4').reshape(shape)[...,:3]
def smooth(a):
 a=np.clip(a,0,1)
 for axis in [0,1]:
  pads=[(0,0),(0,0)];pads[axis]=(2,2);p=np.pad(a,pads,mode='edge');out=np.zeros_like(a)
  for j,w in enumerate([1,4,6,4,1]):
   sl=[slice(None),slice(None)];sl[axis]=slice(j,j+a.shape[axis]);out+=p[tuple(sl)]*(w/16)
  a=out
 return a*a*(3-2*a)
face=smooth(np.fromfile(R/'consumer-tone0/semantic/faceSkinMatte.f16','f2').reshape(384,512).astype('f4'));person=smooth(np.fromfile(R/'consumer-tone0/semantic/personMatte.f16','f2').reshape(384,512).astype('f4'))
for name,w in [('face-only',face),('body-only',person*(1-face))]:preview(base*np.exp2(-np.float32(np.log2(1.09765625)*.5)*w)[...,None],name+'-half-budget')
result={'source_run_id':39139035394,'os_build':'26A434','source_archive_sha256':'55f845778415b22276bc92e166416e60a29df6ce559df8f3fd71f6f5911d12fc','method':'y + F_neutral(x_hat) - F_actual(x_hat), fixed S5 native captured context','diagnostics':diag,'trials':trials,'preview_integrity':integrity,'old_eligible_pixels':int(eligible.sum()),'old_failed_pixels':int(failed.sum()),'scope':'Targeted semantic estimator in linear P3 native output space; no claim to unique producer inversion or recovery of original camera pixels.'}
(O/'residual-results.json').write_text(json.dumps(result,indent=2)+'\n')
