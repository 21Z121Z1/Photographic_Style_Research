from pathlib import Path
import sys,json,hashlib
import numpy as np
from PIL import Image
import PyOpenColorIO as ocio
O=Path(sys.argv[1]);RES=Path(sys.argv[2]);rows=[]
cfg=ocio.Config.CreateFromBuiltinConfig('cg-config-v2.2.0_aces-v1.3_ocio-v2.4');proc=cfg.getProcessor('Linear P3-D65','sRGB - Display','ACES 1.0 - SDR Video',ocio.TRANSFORM_DIR_FORWARD).getDefaultCPUProcessor()
def load(p):
 m=json.loads(Path(str(p)+'.json').read_text());return np.fromfile(p,dtype=m['dtype']).reshape(m['shape'])[...,:3].copy()
def preview(x,name):
 x=np.ascontiguousarray(x,dtype='f4');proc.apply(ocio.PackedImageDesc(x,x.shape[1],x.shape[0],3));y=np.round(255*np.clip(x,0,1)).astype('u1');Image.fromarray(np.rot90(y,3)).save(O/(name+'-ACES.png'))
def compare(a,b,operator):
 d=a.astype('f8')-b;v=np.isfinite(a).all(-1)&np.isfinite(b).all(-1)&(np.min(a,axis=-1)>1/255)&(np.min(b,axis=-1)>1/255)
 lum=lambda z:np.sum(z*np.array([.22897456,.69173852,.07928691]),axis=-1)
 ev=np.log2(lum(a[v])/lum(b[v]))if v.any()else np.array([np.nan]);q={'operator':operator,'max_abs':float(np.max(np.abs(d))),'changed_components':int(np.count_nonzero(d)),'components':d.size,'ev_valid_coverage':float(v.mean()),'ev_mae':float(np.mean(abs(ev))),'ev_max_abs':float(np.max(abs(ev))),'scope':'controlled native forward difference, not ground-truth inverse accuracy'};rows.append(q)
for engine in ['renderer','engine']:
 p=O/'face-actual'/(engine+'.f32')
 if not p.exists():continue
 a=load(p);preview(a.copy(),'face-actual-'+engine)
 for label in ['j1','j1p2']:
  p=O/('face-'+label)/(engine+'.f32')
  if p.exists():b=load(p);compare(a,b,engine+'-j-actual-vs-'+label);preview(b.copy(),'face-'+label+'-'+engine)
p=O/'texture/input.f32'
if p.exists():
 a=load(p);preview(a.copy(),'texture-reference')
 for name in ['UnderEyeBrightening','SkinSmoothingStandalone','Mattify']:
  p=O/'texture'/(name+'.f32')
  if p.exists():b=load(p);compare(a,b,'texture-'+name);preview(b.copy(),'texture-'+name)
(O/'metrics.json').write_text(json.dumps({'rows':rows,'display':{'ocio_version':ocio.__version__,'config':'cg-config-v2.2.0_aces-v1.3_ocio-v2.4','config_sha256':hashlib.sha256(cfg.serialize().encode()).hexdigest(),'source':'Linear P3-D65','display':'sRGB - Display','view':'ACES 1.0 - SDR Video','exposure_ev':0,'orientation':'coded image rotated clockwise 270 degrees for display'},'caution':'j neutralization is a controlled consumer parameter intervention; its equivalence to camera face-brightening removal is unproven. Texture trials zero-fill a missing hair matte for diagnosis only.'},indent=2)+'\n')
