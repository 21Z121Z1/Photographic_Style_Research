"""Runner-only analysis of isolated controls and explicitly estimated removal.

All images, masks and reconstructible outputs remain in the encrypted archive.
No curve, matte, statistics, or GTM/LTM parameter is fitted to these results.
"""
from pathlib import Path
import json,hashlib,sys,os
import numpy as np
from PIL import Image
import PyOpenColorIO as ocio
import semantic_skin_model as skin
O=Path(sys.argv[1]);cfg=ocio.Config.CreateFromBuiltinConfig('cg-config-v2.2.0_aces-v1.3_ocio-v2.4')
proc=cfg.getProcessor('Linear P3-D65','sRGB - Display','ACES 1.0 - SDR Video',ocio.TRANSFORM_DIR_FORWARD).getDefaultCPUProcessor()
DISPLAY={'config':'cg-config-v2.2.0_aces-v1.3_ocio-v2.4','config_sha256':hashlib.sha256(cfg.serialize().encode()).hexdigest(),'source':'Linear P3-D65','view':'ACES 1.0 - SDR Video','display':'sRGB - Display','exposure_ev':0,'orientation':'irot3: np.rot90(k=3), 90 degrees clockwise'}
rows=[];preview_integrity=[]
reuse_path=O/'analysis-s5.json'
reuse={r['case']:r for r in json.loads(reuse_path.read_text())['cases']} if os.environ.get('SEMANTIC_REUSE_NUMERIC_ANALYSIS') and reuse_path.exists() else {}
def save_json(p,x):
 def clean(v):
  if isinstance(v,float) and not np.isfinite(v):return None
  if isinstance(v,dict):return {k:clean(z) for k,z in v.items()}
  if isinstance(v,list):return [clean(z) for z in v]
  return v
 p.write_text(json.dumps(clean(x),indent=2,allow_nan=False)+'\n')
def image(p,dtype='f2',shape=(384,512,4)):
 return np.fromfile(p,dtype=dtype).reshape(shape).astype('f4')
def preview(x,p):
 before=hashlib.sha256(x.tobytes()).hexdigest()
 a=np.array(x[...,:3],dtype='f4',order='C',copy=True);proc.apply(ocio.PackedImageDesc(a,a.shape[1],a.shape[0],3));Image.fromarray(np.rot90(np.round(np.clip(a,0,1)*255).astype('u1'),3)).save(p)
 after=hashlib.sha256(x.tobytes()).hexdigest();assert before==after
 preview_integrity.append({'file':str(p.relative_to(O)),'input_sha256_before':before,'input_sha256_after':after})
def lum(a):return np.sum(a[...,:3]*np.array([.22897456,.69173852,.07928691],dtype='f4'),axis=-1)
def compare(a,b,scope,region=None):
 a=a[...,:3];b=b[...,:3];v=np.isfinite(a).all(-1)&np.isfinite(b).all(-1)&(np.min(a,axis=-1)>1/255)&(np.min(b,axis=-1)>1/255)
 if region is not None:v &= region
 d=np.abs(a-b);ev=np.log2(lum(a)[v]/lum(b)[v])
 return {'scope':scope,'max_abs':float(d.max()),'components_changed':int(np.count_nonzero(d)),'coverage':float(v.mean()),'ev_mae':float(np.mean(abs(ev))) if len(ev) else None,'ev_max_abs':float(np.max(abs(ev))) if len(ev) else None,'max_relative_in_mask':float(np.max((d/np.maximum(abs(b),1e-12))[v])) if v.any() else None}
def smooth_mask(m):
 """Fixed nonnegative binomial interpolation, not claimed as Apple tuning."""
 a=np.clip(m,0,1).astype('f4');k=[1,4,6,4,1]
 for axis in [0,1]:
  pads=[(0,0)]*2;pads[axis]=(2,2);p=np.pad(a,pads,mode='edge');b=np.zeros_like(a)
  for j,w in enumerate(k):
   sl=[slice(None)]*2;sl[axis]=slice(j,j+a.shape[axis]);b+=p[tuple(sl)]*(w/16)
  a=b
 return a*a*(3-2*a)
def estimate_metrics(x,y,w,amplitude):
 v=np.isfinite(x).all(-1)&(np.min(x,axis=-1)>1/255);g=-np.float32(amplitude)*w
 c0=x/np.maximum(x.sum(-1,keepdims=True),1e-12);c1=y/np.maximum(y.sum(-1,keepdims=True),1e-12)
 dx=np.diff(g,axis=1);dy=np.diff(g,axis=0);gg=np.r_[abs(dx).ravel(),abs(dy).ravel()]
 lap=g[1:-1,2:]+g[1:-1,:-2]+g[2:,1:-1]+g[:-2,1:-1]-4*g[1:-1,1:-1]
 rt=y*np.exp2(-g)[...,None];r=compare(rt,x,'Self-consistency of chosen scalar estimate; not Apple inverse accuracy')
 ev=np.log2(lum(y)[v]/lum(x)[v]);roi=v&(w>.5);bg=w==0
 # The correction is bounded by the explicitly chosen budget. This is not a
 # statistical confidence interval or a certified bound on camera processing.
 return {'chosen_budget_ev':float(amplitude),'ev_min':float(ev.min()),'ev_max':float(ev.max()),'ev_mae':float(abs(ev).mean()),'roi_median_ev':float(np.median(g[roi])) if roi.any() else None,'roi_coverage':float(roi.mean()),'background_max_abs':float(abs(y[bg]-x[bg]).max()) if bg.any() else None,'chromaticity_max_abs':float(abs(c0[v]-c1[v]).max()),'correction_gradient_ev_p99':float(np.quantile(gg,.99)),'correction_gradient_ev_max':float(gg.max()),'correction_laplacian_ev_p99':float(np.quantile(abs(lap),.99)),'budget_overshoot_pixels':int(np.count_nonzero((g>1e-7)|(g<-amplitude-1e-7))),'roundtrip':r,'camera_accuracy':None,'identifiability':'j and final RGB do not identify a spatial camera gain; amplitude and selected matte are explicit hypotheses.'}
for case in sorted(O.glob('consumer-*')):
 s=case/'semantic';rp=s/'results.json'
 if not rp.exists():continue
 result=json.loads(rp.read_text());row={'case':case.name,'native':result}
 p=case/'renderer.f32'
 if p.exists():
  ref=image(s/'native.f16')[...,:3];ci=image(p,'f4')[...,:3];control=compare(ref,ci,'Native texture13 versus CI extended-linear P3 render')
  row['p3_output_control']=control
  if control['max_abs']<=1e-5:
   preview(ref,case/'reference-ACES.png')
   for op in ['skin-color','skin-brightness','skin-both']:
    for kind in ['oracle','estimate']:
     f=s/f'{op}-removed-{kind}.f16'
     if f.exists():
      a=image(f)[...,:3];row[f'{op}-{kind}']=compare(a,ref,'Isolated native parameter counterfactual, not original-camera truth');preview(a,case/f'{op}-{kind}-ACES.png')
   row['gain_map_scope']='Positive linear P3 ratio between controlled native outputs; not a camera-ground-truth gain map.'
  else:row['preview_native_ablation_status']='Not emitted: texture13 color-space control failed'
 sp=s/'model-skin-stage.f32'
 if case.name in reuse:
  for k in ['skin_continuous_forward','skin_continuous_inverse']:
   if k in reuse[case.name]:row[k]=reuse[case.name][k]
 elif sp.exists():
  stages=np.fromfile(sp,'f4').reshape(384,512,3,4);x=stages[:,:,0,:3];y=stages[:,:,1,:3];w=stages[:,:,2,0];guide=stages[:,:,2,1]
  params=np.fromfile(s/'buffer-1.bin','f4');t9=float(params[148]);t10=float(params[149]);f=skin.forward(x,w,guide,t9,t10);row['skin_continuous_forward']=compare(f,y,'Continuous AIR-derived skin operator versus half MSL stage; model observations, not native internal captures')
  recovered=np.empty_like(x);valid=np.zeros(w.shape,bool);singular=np.zeros(w.shape,bool)
  for r0 in range(0,384,32):
   sl=slice(r0,r0+32);q=skin.inverse(y[sl],w[sl],guide[sl],t9,t10);recovered[sl]=q['candidate'];valid[sl]=q['residual_valid_mask'];singular[sl]=q['singular_mask']
  row['skin_continuous_inverse']={'theta9':t9,'theta10':t10,'coverage':float(valid.mean()),'singular_coverage':float(singular.mean()),'roundtrip':compare(skin.forward(recovered,w,guide,t9,t10),y,'Continuous candidate root self-consistency',valid),'preimage_error':compare(recovered,x,'Against held original model-stage preimage; not used as inverse seed',valid),'uniqueness_verified':False}
  np.savez_compressed(s/'skin-continuous-inverse.npz',candidate=recovered,valid=valid,singular=singular)
 rows.append(row)
# Directional face/body estimates operate separately on the decoded primary.
# No frozen GTM/LTM inverse is changed or combined into these previews.
case=O/'consumer-tone0';s=case/'semantic';p=case/'primary_input.f32'
if p.exists() and (s/'faceSkinMatte.f16').exists():
 x=image(p,'f4')[...,:3];face=smooth_mask(image(s/'faceSkinMatte.f16',shape=(384,512)));person=smooth_mask(image(s/'personMatte.f16',shape=(384,512)));body=person*(1-face)
 out=O/'directional-estimates';out.mkdir(exist_ok=True);preview(x,out/'reference-ACES.png');j=1.09765625;budget=float(np.log2(j));est=[]
 for op,w in [('face-only',face),('body-only',body)]:
  for fraction in [.5,1.]:
   amp=budget*fraction;g=-np.float32(amp)*w;y=x*np.exp2(g)[...,None];name=f'{op}-budget{fraction:g}';preview(y,out/(name+'-ACES.png'));np.savez_compressed(out/(name+'.npz'),rgb=y,log2_gain=g,mask=w)
   est.append({'operator':op,'fraction_of_log2j':fraction,**estimate_metrics(x,y,w,amp)})
 save_json(out/'estimates.json',{'status':'hypothesis with real-image numerical validation of direction, neutrality, smoothness and chosen-transform self-consistency','j':j,'masks':'faceSkinMatte for face; personMatte*(1-faceSkinMatte) for body; fixed nonnegative 5-tap binomial and smoothstep','matte_smoother_is_apple_proven':False,'body_amplitude_identified':False,'display':DISPLAY,'rows':est})
save_json(O/'analysis-s5.json',{'os_build':'26A434','display':DISPLAY,'cases':rows,'camera_ground_truth_available':False})
save_json(O/'preview-integrity.json',{'checks':preview_integrity,'failed':sum(r['input_sha256_before']!=r['input_sha256_after'] for r in preview_integrity)})
