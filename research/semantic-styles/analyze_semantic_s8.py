from pathlib import Path
import sys,json,hashlib,itertools
import numpy as np
from PIL import Image
import PyOpenColorIO as ocio
S=Path(sys.argv[1]);P=Path(sys.argv[2]);O=Path(sys.argv[3]);O.mkdir(exist_ok=True)
def load(p,c=4,dtype='f2'):return np.fromfile(p,dtype).reshape(384,512,c)[...,:3].astype('f8')
target=load(P/'native.f16');old_rt=load(P/'native-inverse-roundtrip.f16');rt=load(S/'new-roundtrip.f16');eligible=np.fromfile(S/'original-eligible.u8','u1').reshape(384,512).astype(bool);active=np.fromfile(S/'optimizer-support.u8','u1').reshape(384,512).astype(bool)
old_relative=np.fromfile(P/'native-inverse-relative.f32','f4').astype('f8').reshape(384,512)
matte=np.fromfile(P/'texture-11.bin','f2').reshape(384,512);pad=np.pad(matte,1,mode='edge');footprint=np.maximum.reduce([pad[a:a+384,b:b+512] for a in range(3) for b in range(3)])>0
def metrics(a,b,mask):
 d=abs(a-b);r=np.max(d/np.maximum(abs(b),1e-12),-1);v=mask&np.isfinite(r)
 if not v.any():return {'pixels':0}
 lum=lambda z:z@np.array([.22897456,.69173852,.07928691]);evm=v&(lum(a)>0)&(lum(b)>0);ev=np.log2(lum(a)[evm]/lum(b)[evm])
 return {'pixels':int(v.sum()),'coverage':float(v.mean()),'max_abs':float(d[v].max()),'max_relative':float(r[v].max()),'failed_gt_1e3_float64':int(np.count_nonzero(v&(r>1e-3))),'psnr_db':float(-10*np.log10(np.mean(d[v]**2))) if d[v].any() else 'inf','ev_mae':float(abs(ev).mean()) if len(ev) else None,'ev_max_abs':float(abs(ev).max()) if len(ev) else None}
cfg=ocio.Config.CreateFromBuiltinConfig('cg-config-v2.2.0_aces-v1.3_ocio-v2.4');proc=cfg.getProcessor('Linear P3-D65','sRGB - Display','ACES 1.0 - SDR Video',ocio.TRANSFORM_DIR_FORWARD).getDefaultCPUProcessor();integrity=[]
def preview(x,name):
 h=hashlib.sha256(x.tobytes()).hexdigest();z=np.array(x,dtype='f4',order='C',copy=True);proc.apply(ocio.PackedImageDesc(z,512,384,3));im=Image.fromarray(np.rot90(np.round(255*np.clip(z,0,1)).astype('u1'),3));im.thumbnail((512,512));im.save(O/(name+'-ACES.png'));assert h==hashlib.sha256(x.tobytes()).hexdigest();integrity.append({'image':name,'input_sha256':h,'unchanged':True})
diag={}
for name in ['old-recovery','true-control']:
 J=np.fromfile(S/(name+'-jacobian.f32'),'f4').reshape(384,512,3,3);sv=np.linalg.svd(J,compute_uv=False);bad=(sv[...,-1]<1e-5);cond=sv[...,0]/np.maximum(sv[...,-1],1e-12)
 diag[name]={}
 for rn,r in [('all',eligible),('skin_support',active),('outside_support',eligible&~active),('old_failed',eligible&(old_relative>1e-3))]:
  diag[name][rn]={'pixels':int(r.sum()),'rank_deficient_at_h_0p004':int(np.count_nonzero(bad&r)),'condition_median':float(np.median(cond[r])) if r.any() else None,'condition_p99':float(np.quantile(cond[r],.99)) if r.any() else None}
preview(target,'reference');rows=[];examples=[]
rootY=[load(S/f'seed-{k}-native.f16') for k in range(3)];rootX=[load(S/f'seed-{k}-input.f32',3,'f4').astype('f2') for k in range(3)]
exact=[(z==target).all(-1) for z in rootY]
for op in ['skin-color','skin-brightness','skin-both']:
 expected=load(P/(op+'-removed-oracle.f16'));old=load(P/(op+'-removed-estimate.f16'));old_corrected=target+old-old_rt;neutral=load(S/(op+'-new-neutral.f16'));result=target+neutral-rt
 row={'operator':op,'old_direct':metrics(old,expected,eligible),'S7_residual_recomputed_float64':metrics(old_corrected,expected,eligible),'new_residual':metrics(result,expected,eligible),'new_residual_skin_support':metrics(result,expected,active),'outside_skin_support_max_change':float(abs(result[~footprint]-target[~footprint]).max()),'empirical_ambiguities':[]}
 neutral_roots=[load(S/f'seed-{k}-{op}.f16') for k in range(3)]
 for a,b in itertools.combinations(range(3),2):
  distinct=(rootX[a]!=rootX[b]).any(-1);amb=eligible&exact[a]&exact[b]&distinct&(neutral_roots[a]!=neutral_roots[b]).any(-1)
  d=np.max(abs(neutral_roots[a]-neutral_roots[b]),-1);row['empirical_ambiguities'].append({'seed_pair':[a,b],'exact_native_output_same_as_target':True,'distinct_half_inputs_and_distinct_neutral_outputs':int(amb.sum()),'largest_counterfactual_absolute_separation':float(d[amb].max()) if amb.any() else 0.,'interpretation':'Observed pairwise nonidentifiability; this is a lower bound on ambiguity, not a complete inverse interval.'})
  for yy,xx in np.argwhere(amb)[:4]:examples.append({'operator':op,'row':int(yy),'col':int(xx),'seed_pair':[a,b],'x1':rootX[a][yy,xx].astype('f4').tolist(),'x2':rootX[b][yy,xx].astype('f4').tolist(),'same_y':target[yy,xx].tolist(),'neutral1':neutral_roots[a][yy,xx].tolist(),'neutral2':neutral_roots[b][yy,xx].tolist()})
 good=(result>0).all(-1)&(target>0).all(-1)&eligible;g=np.zeros_like(result,dtype='f4');g[good]=np.log2(result[good]/target[good]).astype('f4');np.savez_compressed(O/(op+'-estimate.npz'),rgb=result.astype('f4'),log2_gain=g,gain_valid=good,optimizer_support=active,near_black_or_nonfinite=~eligible)
 preview(result,op+'-estimated');preview(expected,op+'-oracle');rows.append(row)
report={'source_run':39139035394,'os_build':'26A434','old_full_solver_failed_float64':int(np.count_nonzero(eligible&(old_relative>1e-3))),'old_mask_threshold_rounding_ties':int(np.count_nonzero(eligible&(old_relative==float(np.float32(.001))))),'old_native_roundtrip':metrics(old_rt,target,eligible),'new_native_roundtrip_all_original_eligible':metrics(rt,target,eligible),'new_native_roundtrip_optimizer_support':metrics(rt,target,active),'diagnostics':diag,'trials':rows,'preview_integrity':integrity,'original_input_used_as_seed':False,'camera_undo_verified':False,'acceptance_threshold_unchanged':1e-3}
(O/'s8-analysis.json').write_text(json.dumps(report,indent=2)+'\n');(O/'private-ambiguity-examples.json').write_text(json.dumps(examples,indent=2)+'\n')
