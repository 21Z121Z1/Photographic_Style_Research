from pathlib import Path
import json,hashlib,subprocess,sys
import numpy as np
from PIL import Image
import PyOpenColorIO as ocio
import studio_under_eye as model
raw=Path(sys.argv[1]);out=Path(sys.argv[2]);out.mkdir(exist_ok=True);exe,res,photo=sys.argv[3:6]
def load(p,channels=4):return np.fromfile(p,'f2').reshape(384,512,channels).astype('f4')
def metric(a,b,mask=None):
 d=abs(a[...,:3]-b[...,:3]);v=np.isfinite(a[...,:3]).all(-1)&np.isfinite(b[...,:3]).all(-1)&(np.min(b[...,:3],-1)>1/255)
 if mask is not None:v &= mask
 return {'max_abs_all':float(d.max()),'coverage':float(v.mean()),'max_relative_in_mask':float(np.max((d/np.maximum(abs(b[...,:3]),1e-12))[v])) if v.any() else None,'psnr_db':float(-10*np.log10(np.mean(d.astype('f8')**2))) if d.any() else 'inf'}
cfg=ocio.Config.CreateFromBuiltinConfig('cg-config-v2.2.0_aces-v1.3_ocio-v2.4');proc=cfg.getProcessor('Linear P3-D65','sRGB - Display','ACES 1.0 - SDR Video',ocio.TRANSFORM_DIR_FORWARD).getDefaultCPUProcessor()
def preview(a,p):
 h=hashlib.sha256(a.tobytes()).hexdigest();x=np.array(a[...,:3],dtype='f4',order='C',copy=True);proc.apply(ocio.PackedImageDesc(x,512,384,3));im=Image.fromarray(np.rot90(np.round(np.clip(x,0,1)*255).astype('u1'),3));im.thumbnail((256,256));im.save(p);assert h==hashlib.sha256(a.tobytes()).hexdigest()
x=load(raw/'original.f16')[...,:3];e=load(raw/'edited.f16')[...,:3];rows=[]
for mix in [0,.5,1]:
 y=load(raw/f'mix-{mix:g}-image.f16')[...,:3];w=load(raw/f'mix-{mix:g}-weight.f16')[...,0]
 prediction=model.forward(x,e,w);q=model.inverse(y,e,w);v=q['valid'];inv=q['candidate'];inside=np.all((x>=q['lower'])&(x<=q['upper']),-1)
 r={'brightnessMix':mix,'weight_min':float(w.min()),'weight_max':float(w.max()),'weight_nonzero_coverage':float((w>0).mean()),'affine_model_vs_native':metric(prediction,y),'inverse_vs_known_original':metric(inv[v],x[v]) if v.any() else None,'valid_coverage':float(v.mean()),'plateau_coverage':float(q['plateau'].mean()),'near_black_coverage':float(q['near_black'].mean()),'finite_box_interval_excludes_original_in_valid_mask':int(np.count_nonzero(v&~inside)),'interval_max_width_in_valid_mask':float(np.max((q['upper']-q['lower'])[v])) if v.any() else None,'domain_assumption':list(q['domain']),'camera_interval_verified':False,'scope':'Native final blend with known edited image and native 0/1 weight probe; upstream person/eye statistics not recovered.'}
 if mix==.5:
  # Quantize only through the original Apple kernel; edited image and mattes
  # are held fixed. Original input is used solely to assess the recovered root.
  candidate=np.ones((384,512,4),'f4');candidate[...,:3]=np.where(v[...,None],inv,y);cp=out/'candidate.f32';candidate.tofile(cp);rp=raw.parent/'under-eye-replay'
  log=out/'replay.log'
  with log.open('w') as f:rc=subprocess.run([exe,str(cp),res,str(rp),photo,str(raw/'edited.f16')],stdout=f,stderr=subprocess.STDOUT,timeout=180).returncode
  r['native_roundtrip_returncode']=rc
  if rc==0:r['native_roundtrip']=metric(load(rp/'mix-0.5-image.f16')[...,:3],y,v)
  preview(x,out/'under-eye-reference-ACES.png');preview(y,out/'under-eye-controlled-applied-ACES.png');preview(np.where(v[...,None],inv,x),out/'under-eye-conditional-inverse-ACES.png')
 rows.append(r)
(out/'under-eye-results.json').write_text(json.dumps({'os_build':'26A434','native_library_sha256':json.loads((raw/'native.json').read_text())['library_sha256'],'rows':rows,'edited_input_is_controlled':True,'actual_camera_undo_verified':False},indent=2)+'\n')
