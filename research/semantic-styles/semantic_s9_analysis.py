"""Runner-only diagnostics of saved native arrays. No inverse search or retuning."""
from pathlib import Path
import json, sys, itertools, hashlib
import numpy as np
P,S,O=map(Path,sys.argv[1:]);O.mkdir(exist_ok=True)
def load(p,c=4,typ='f2'):
 return np.fromfile(p,typ).reshape(384,512,c)[...,:3].astype('f8')
y=load(P/'native.f16');rt=load(S/'new-roundtrip.f16');old_rt=load(P/'native-inverse-roundtrip.f16')
eligible=np.fromfile(S/'original-eligible.u8','u1').reshape(384,512).astype(bool)
m=np.fromfile(P/'texture-11.bin','f2').reshape(384,512).astype('f8');mp=np.pad(m,1,mode='edge')
mx=np.maximum.reduce([mp[a:a+384,b:b+512] for a in range(3) for b in range(3)])
mn=np.minimum.reduce([mp[a:a+384,b:b+512] for a in range(3) for b in range(3)])
support=(mx>0)&eligible;edge=(mx-mn>1/255)&eligible
rel=lambda a,b:np.max(abs(a-b)/np.maximum(abs(b),1e-12),-1)
recorded=np.fromfile(P/'native-inverse-relative.f32','f4').reshape(384,512)
rounded=np.float32(.001)
threshold={'threshold':.001,'recorded_float32_residual_promoted_to_float64_failures':int(np.count_nonzero(eligible&(recorded.astype('f8')>.001))), 'recomputed_from_half_values_in_float64_failures':int(np.count_nonzero(eligible&(rel(old_rt,y)>.001))), 'recorded_float32_equal_to_float32_threshold':int(np.count_nonzero(eligible&(recorded==rounded))), 'explanation':'Six residuals round to float32(0.001), which exceeds real 0.001. Audit both stored-C-float and recomputed-half-float64 definitions; no threshold change.'}
roots=[load(S/f'seed-{k}-input.f32',3,'f4').astype('f2') for k in range(3)]
exact=[(load(S/f'seed-{k}-native.f16')==y).all(-1) for k in range(3)]
J=np.fromfile(S/'true-control-jacobian.f32','f4').reshape(384,512,3,3)
low_rank=np.linalg.svd(J,compute_uv=False)[...,-1]<1e-5
source=load(P/'texture-0.bin')
preimage=np.fromfile(S/'new-preimage.f32','f4').reshape(384,512,3)
lum=lambda x:x@np.array([.22897456,.69173852,.07928691])
def stat(a,mask):
 z=a[mask];return {'pixels':int(mask.sum()),'max_abs':float(abs(z).max()) if z.size else None,'p99_abs':float(np.quantile(abs(z),.99)) if z.size else None,'rms':float(np.sqrt(np.mean(z*z))) if z.size else None}
def gradient(a):
 dx=np.diff(a,axis=1,append=a[:,-1:]);dy=np.diff(a,axis=0,append=a[-1:]);return np.sqrt(dx*dx+dy*dy)
rows=[]
for op in ['skin-color','skin-brightness','skin-both']:
 expected=load(P/(op+'-removed-oracle.f16'));neutral=load(S/(op+'-new-neutral.f16'));estimate=y+neutral-rt
 r=rel(estimate,expected);failed=eligible&(r>.001)
 nroot=[load(S/f'seed-{k}-{op}.f16') for k in range(3)]
 ambiguity=np.zeros_like(eligible);lo=np.full_like(y,np.inf);hi=np.full_like(y,-np.inf)
 for a,b in itertools.combinations(range(3),2):
  q=eligible&exact[a]&exact[b]&(roots[a]!=roots[b]).any(-1)&(nroot[a]!=nroot[b]).any(-1)
  ambiguity |= q
  lo[q]=np.minimum(lo[q],np.minimum(nroot[a][q],nroot[b][q]));hi[q]=np.maximum(hi[q],np.maximum(nroot[a][q],nroot[b][q]))
 span=np.zeros_like(y);span[ambiguity]=hi[ambiguity]-lo[ambiguity]
 vl=eligible&(lum(estimate)>0)&(lum(expected)>0)&(lum(y)>0)
 ev_delta=np.zeros_like(m);ev_delta[vl]=np.log2(lum(estimate)[vl]/lum(expected)[vl])
 correction=np.zeros_like(m);correction[vl]=np.log2(lum(estimate)[vl]/lum(y)[vl])
 difference=estimate-expected
 row={'operator':op,'failed_pixels':int(failed.sum()),'failed_on_matte_edge':int(np.count_nonzero(failed&edge)),'failed_on_skin_interior_m_gt_half':int(np.count_nonzero(failed&(m>.5))),'failed_with_low_finite_difference_jacobian_rank':int(np.count_nonzero(failed&low_rank)), 'observed_nonunique_pixels_union':int(ambiguity.sum()),'failed_and_observed_nonunique':int(np.count_nonzero(failed&ambiguity)), 'observed_neutral_output_span_max':float(span.max()),'max_abs_error':float(abs(difference[eligible]).max()), 'error_gradient_EV':{'skin_support':stat(gradient(ev_delta),support&vl),'matte_edge':stat(gradient(ev_delta),edge&vl)},'correction_gradient_EV':{'skin_support':stat(gradient(correction),support&vl),'matte_edge':stat(gradient(correction),edge&vl)}, 'outside_skin_footprint_max_change':float(abs(estimate[mx==0]-y[mx==0]).max()),'outside_skin_footprint_max_oracle_error':float(abs(difference[mx==0]).max()),'mask_coverage':float(eligible.mean()),'relative_threshold':.001,'camera_undo_verified':False,'complete_inverse_interval_available':False}
 # A union of observed roots is an ambiguity witness, never an upper bound.
 # No failed, near-black or ill-conditioned pixel is removed from acceptance.
 np.savez_compressed(O/(op+'-diagnostic-masks.npz'),eligible=eligible,near_black_or_nonfinite=~eligible,failed_relative_1e3=failed,matte_edge=edge,observed_nonunique=ambiguity,observed_span_lower_bound=span.astype('f4'),low_finite_difference_jacobian_rank=low_rank,preimage_near_search_box=np.any((preimage<=-.0199)|(preimage>=1.2499),-1),source_negative=np.any(source<0,-1))
 row['diagnostic_masks_sha256']=hashlib.sha256((O/(op+'-diagnostic-masks.npz')).read_bytes()).hexdigest();rows.append(row)
(O/'s9-diagnostics.json').write_text(json.dumps({'source_runs':[39139035394,39156000731],'os_build':'26A434','threshold_audit':threshold,'rows':rows,'new_inverse_search_performed':False,'scope':'Saved native context; masks and edge-error measurements, no original camera effect reconstruction.'},indent=2)+'\n')
