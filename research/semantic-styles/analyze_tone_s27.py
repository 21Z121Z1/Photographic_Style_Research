"""Runner-only local parameter counterfactuals, with immutable preview inputs.

Native counterfactuals use known input as an oracle. Gain-map reconstruction
is representation self-consistency, never an inverse accuracy measurement.
"""
from pathlib import Path
import sys,json,hashlib
import numpy as np
from PIL import Image,ImageDraw
import PyOpenColorIO as ocio
from plot_brightening_s27 import plot
O=Path(sys.argv[1]);N=O/'native';P=Path(sys.argv[2]);A=O/'analysis';A.mkdir()
native=json.loads((N/'s27-results.json').read_text());assert native['source_unchanged'] and not native['context_mismatches']
cfg=ocio.Config.CreateFromBuiltinConfig('cg-config-v2.2.0_aces-v1.3_ocio-v2.4')
cpu=cfg.getProcessor('Linear P3-D65','sRGB - Display','ACES 1.0 - SDR Video',ocio.TRANSFORM_DIR_FORWARD).getDefaultCPUProcessor()
display={'config':'cg-config-v2.2.0_aces-v1.3_ocio-v2.4','config_sha256':hashlib.sha256(cfg.serialize().encode()).hexdigest(),'source':'Linear P3-D65','display':'sRGB - Display','view':'ACES 1.0 - SDR Video','exposure_ev':0,'orientation':'irot3: clockwise 90 degrees'}
def save(name,value):
 (A/name).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def read(p,dtype='<f2',channels=4):return np.fromfile(p,dtype=dtype).reshape(384,512,channels).astype('f8')
checks=[]
def preview(x,name):
 before=hashlib.sha256(x.tobytes()).hexdigest();copy=np.array(x[...,:3],dtype='f4',order='C',copy=True);cpu.apply(ocio.PackedImageDesc(copy,copy.shape[1],copy.shape[0],3));img=Image.fromarray(np.rot90(np.round(np.clip(copy,0,1)*255).astype('u1'),3));img.save(A/(name+'-ACES.png'));after=hashlib.sha256(x.tobytes()).hexdigest();assert before==after;checks.append({'name':name,'input_before_sha256':before,'input_after_sha256':after});return img
def lum(x):return x[...,:3]@np.array([.22897456,.69173852,.07928691])
ref=read(N/'reference.f16');ci=read(O/'renderer.f32','<f4');space_control=float(np.max(np.abs(ref-ci)))
assert space_control<=1e-5,'Captured output cannot yet be interpreted as linear P3'
source=read(N/'source.f16');primary=read(O/'primary_input.f32','<f4');main_control=float(np.max(np.abs(source-primary)));half_main_control=float(np.max(np.abs(source-primary.astype('f2').astype('f8'))))
# Input texture0 can have a different decoding step. Record the control and
# label naive composition conditional; do not silently reinterpret a domain.
v=np.isfinite(ref[...,:3]).all(-1)&(ref[...,:3].min(-1)>1/255)
person=read(P/'texture-10.bin',channels=1)[...,0]
rows=[];images={};images['reference']=preview(ref,'reference')
for spec in native['trials']:
 name=spec['operator'];out=read(N/(name+'.f16'));diff=abs(out[...,:3]-ref[...,:3]);eligible=v&(out[...,:3].min(-1)>0)&np.isfinite(out[...,:3]).all(-1);ev=np.full(eligible.shape,np.nan);ev[eligible]=np.log2(lum(out)[eligible]/lum(ref)[eligible]);g=np.zeros_like(out[...,:3]);g[eligible]=np.log2(out[...,:3][eligible]/ref[...,:3][eligible]);recon=ref[...,:3]*np.exp2(g);err=np.abs(recon-out[...,:3]);scalar=np.ones(eligible.shape);scalar[eligible]=lum(out)[eligible]/lum(ref)[eligible];one=ref[...,:3]*scalar[...,None];one_err=abs(one-out[...,:3]);
 correction=np.where(eligible,ev,0);gx=np.abs(np.diff(correction,axis=1));gy=np.abs(np.diff(correction,axis=0));vx=eligible[:,1:]&eligible[:,:-1];vy=eligible[1:,:]&eligible[:-1,:];grad=np.r_[gx[vx],gy[vy]];lap=correction[1:-1,:-2]+correction[1:-1,2:]+correction[:-2,1:-1]+correction[2:,1:-1]-4*correction[1:-1,1:-1];vl=eligible[1:-1,1:-1]&eligible[1:-1,:-2]&eligible[1:-1,2:]&eligible[:-2,1:-1]&eligible[2:,1:-1]
 regions={}
 for rn,mask in [('person',person>.5),('background',person<.01)]:
  z=ev[eligible&mask];regions[rn]={'pixels':int(z.size),'median_EV':float(np.median(z)) if z.size else None,'min_EV':float(z.min()) if z.size else None,'max_EV':float(z.max()) if z.size else None}
 row={'operator':name,'native':spec,'reference_eligible_pixels':int(v.sum()),'representation_positive_pixels':int(eligible.sum()),'representation_coverage':float(eligible.mean()),'all_pixel_max_abs_change':float(diff.max()),'change_luma_EV_median':float(np.median(ev[eligible])),'change_luma_EV_min':float(ev[eligible].min()),'change_luma_EV_max':float(ev[eligible].max()),'regions':regions,'correction_gradient_EV_p99':float(np.quantile(grad,.99)),'correction_gradient_EV_max':float(grad.max()),'correction_laplacian_EV_p99':float(np.quantile(abs(lap[vl]),.99)),'RGB_gain_representation_max_relative':float(np.max((err/np.maximum(abs(out[...,:3]),1e-12))[eligible])),'scalar_gain_max_relative_vs_RGB_counterfactual':float(np.max((one_err/np.maximum(abs(out[...,:3]),1e-12))[eligible])),'inverse_accuracy_measured':False,'camera_inverse_verified':False}
 if name=='local-neutral':np.savez_compressed(A/'local-neutral-gain-map.private.npz',log2_rgb_gain=g.astype('f4'),positive_representation_mask=eligible)
 rows.append(row);images[name]=preview(out,name)
naive=read(N/'naive-negative-after-positive.f16');images['naive-negative-after-positive']=preview(naive,'naive-negative-after-positive')
contact=['reference','local-half-neutral','local-neutral','gtc-weight-only-reset','semantic-tone-reset','ui-tone-reset','opposite-ui-tone','naive-negative-after-positive']
sheet=Image.new('RGB',(4*192,2*(256+28)),'white');draw=ImageDraw.Draw(sheet)
for k,n in enumerate(contact):
 im=images[n].resize((192,256));x=(k%4)*192;y=(k//4)*284;sheet.paste(im,(x,y));draw.text((x+3,y+258),n,fill='black')
sheet.save(A/'tone-counterfactuals.private.png')
save('tone-analysis.json',{'os_build':'26A434','photo':'IMG_2810','width':512,'height':384,'native_output_vs_CI_P3_max_abs':space_control,'source_vs_decoded_primary_max_abs':main_control,'source_vs_half_decoded_primary_max_abs':half_main_control,'naive_composition_same_space_verified':half_main_control==0,'display':display,'rows':rows,'native_summary':native,'preview_input_sha_checks':checks,'preview_sha_failures':sum(c['input_before_sha256']!=c['input_after_sha256'] for c in checks),'operator_coverage_scope':'One development image, conditional native counterfactuals only, not five-photo acceptance','acceptance_complete':False,'old_gate_modified':False,'global_local_semantic_stages_kept_separate':True,'gain_map_metrics_scope':'Same-frame output ratio representation; no estimate of original camera gain or inverse accuracy','edge_metrics_scope':'Correction finite-difference diagnostics, not proof of absence of halo/ringing'})
plot(O/'public-figure')
print('S27 conditional curve figure and isolated native tone analysis finished; private data encrypted.')
