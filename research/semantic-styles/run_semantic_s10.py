"""Native nonzero texture final units with explicitly artificial context."""
from pathlib import Path
import os, sys, subprocess, hashlib, zipfile, shutil, tarfile, json
import numpy as np
from PIL import Image
import PyOpenColorIO as ocio
W=Path(os.environ['W']);O=W/'out';O.mkdir(exist_ok=True);SRC=Path('research/semantic-styles');status=[]
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def run(args,name):
 with (O/(name+'.log')).open('w') as f:rc=subprocess.run(list(map(str,args)),stdout=f,stderr=subprocess.STDOUT,timeout=360).returncode
 status.append({'operation':name,'returncode':rc});(O/'status.json').write_text(json.dumps(status,indent=2)+'\n');return rc
assert subprocess.check_output(['sw_vers','-buildVersion'],text=True).strip()=='26A434'
p=W/'s5.zip'
with p.open('wb') as f:subprocess.run(['gh','api','repos/21Z121Z1/Photographic_Style_Research/actions/artifacts/12140624073/zip'],stdout=f,check=True)
assert sha(p)=='55f845778415b22276bc92e166416e60a29df6ce559df8f3fd71f6f5911d12fc'
with zipfile.ZipFile(p) as z:
 n=next(n for n in z.namelist() if n.endswith('.gpg'))
 with z.open(n) as a,(W/'s5.gpg').open('wb') as b:shutil.copyfileobj(a,b)
key=W/'session-key';key.write_text(os.environ['S5_ARCHIVE_SESSION']+'\n');key.chmod(0o600)
with key.open('rb') as f,(O/'s5-decrypt.log').open('w') as log:
 subprocess.run(['gpg','--batch','--override-session-key-fd',str(f.fileno()),'--output',str(W/'s5.tar.gz'),'--decrypt',str(W/'s5.gpg')],pass_fds=(f.fileno(),),stdout=log,stderr=subprocess.STDOUT,check=True)
key.unlink();prior=W/'prior';prior.mkdir()
with tarfile.open(W/'s5.tar.gz') as t:t.extractall(prior,filter='data')
manifest=json.loads((prior/'out/manifest.json').read_text())
for a in manifest['files']:
 f=prior/'out'/a['path'];assert sha(f)==a['sha256'] and f.stat().st_size==a['size']
P=prior/'out/consumer-toneP035/semantic';I=W/'inputs';I.mkdir();raw=W/'native-raw';raw.mkdir()
x=np.fromfile(P/'texture-0.bin','f2').reshape(384,512,4).astype('f4');skin=np.fromfile(P/'texture-11.bin','f2').reshape(384,512);person=np.fromfile(P/'texture-10.bin','f2').reshape(384,512)
# Fixed diagnostic blur; no claim that this approximates Apple's upstream blur.
b=x.copy()
for axis in [0,1]:
 pads=[(0,0),(0,0),(0,0)];pads[axis]=(2,2);padded=np.pad(b,pads,mode='edge');q=np.zeros_like(b)
 for j in range(5):
  sl=[slice(None)]*3;sl[axis]=slice(j,j+b.shape[axis]);q+=padded[tuple(sl)]*.2
 b=q
b[...,3]=1
pre=np.zeros_like(x);pre[...,0]=skin
arrays={'original':x,'blur':b,'scaledblur':b*.9,'skin':skin,'person':person,'precomputed':pre,'gfA':np.full_like(x,.5),'gfB':np.full_like(x,.1),'ones':np.ones((384,512),'f4'),'zero':np.zeros_like(x)}
for name,a in arrays.items():a.astype('f2').tofile(I/(name+'.f16'))
exe=W/'texture-units'
if run(['clang','-fobjc-arc','-O2','-framework','Foundation','-framework','Metal',SRC/'texture_units_s10.m','-o',exe],'build')!=0:sys.exit(0)
run(['xcrun','lldb','--batch','-o','run','-k','thread backtrace all','--',exe,I,raw],'native')
if not (raw/'native.json').exists():
 (O/'native-missing.json').write_text(json.dumps({'operator_success':False,'reason':'Inspect native checkpoint/LLDB; no native.json'})+'\n');sys.exit(0)
facts=json.loads((raw/'native.json').read_text());shutil.copy2(raw/'native.json',O/'native.json')
out=O/'analysis';out.mkdir();rows=[];checks=[]
cfg=ocio.Config.CreateFromBuiltinConfig('cg-config-v2.2.0_aces-v1.3_ocio-v2.4');proc=cfg.getProcessor('Linear P3-D65','sRGB - Display','ACES 1.0 - SDR Video',ocio.TRANSFORM_DIR_FORWARD).getDefaultCPUProcessor()
def preview(a,name):
 before=hashlib.sha256(a.tobytes()).hexdigest();z=np.array(a[...,:3],dtype='f4',copy=True,order='C');proc.apply(ocio.PackedImageDesc(z,512,384,3));im=Image.fromarray(np.rot90(np.round(np.clip(z,0,1)*255).astype('u1'),3));im.thumbnail((512,512));im.save(out/(name+'-ACES.png'));after=hashlib.sha256(a.tobytes()).hexdigest();assert before==after;checks.append({'image':name,'before':before,'after':after})
def metric(a,b,valid):
 d=abs(a-b);r=np.max(d/np.maximum(abs(b),1e-12),-1);lum=lambda z:z@np.array([.22897456,.69173852,.07928691]);q=valid&(lum(a)>0)&(lum(b)>0);ev=np.log2(lum(a)[q]/lum(b)[q]);return {'pixels':int(valid.sum()),'coverage':float(valid.mean()),'max_abs':float(d[valid].max()),'max_relative':float(r[valid].max()),'failed_gt_1e3':int(np.count_nonzero(valid&(r>.001))),'psnr_db':float(-10*np.log10(np.mean(d[valid]**2))) if d[valid].any() else 'inf','EV_MAE':float(abs(ev).mean()) if ev.size else None}
original=x[...,:3].astype('f8');preview(original,'reference')
for a in facts['rows']:
 if 'error' in a:continue
 stem=f"{a['operator']}-{a['strength']:g}"
 y=np.fromfile(raw/(stem+'-native.f16'),'f2').reshape(384,512,4)[...,:3].astype('f8');inv=np.fromfile(raw/(stem+'-inverse.f32'),'f4').reshape(384,512,4)[...,:3].astype('f8');rt=np.fromfile(raw/(stem+'-roundtrip.f16'),'f2').reshape(384,512,4)[...,:3].astype('f8');valid=np.isfinite(y).all(-1)&(np.min(y,-1)>1/255)
 r={'operator':a['operator'],'strength':a['strength'],'native_changed_half_components':int(np.count_nonzero(y!=original)),'effect_max_abs':float(abs(y-original).max()),'native_roundtrip':metric(rt,y,valid),'recovered_vs_original':metric(inv,original,valid),'context_is_artificial':True,'camera_undo_verified':False,'source_input_sha256':sha(I/'original.f16')}
 if a['strength']>0:
  # Lossless native-delta evidence relative to immutable S5 half source. Keep
  # encrypted; no full-size original or duplicate buffers in the new archive.
  np.savez_compressed(out/(stem+'-deltas.npz'),native_delta=(y-original).astype('f4'),inverse_delta=(inv-original).astype('f4'),native_roundtrip_delta=(rt-y).astype('f4'),eligible=valid,failed_relative_1e3=valid&(np.max(abs(rt-y)/np.maximum(abs(y),1e-12),-1)>.001))
  r['deltas_sha256']=sha(out/(stem+'-deltas.npz'));preview(y,stem+'-applied');preview(np.where(valid[...,None],inv,y),stem+'-conditional-inverse')
 rows.append(r)
(out/'results.json').write_text(json.dumps({'os_build':'26A434','source_run':39139035394,'rows':rows,'preview_integrity':checks,'original_input_used_as_seed':False,'context':'Synthetic fixed5x5 box blur, fixed gfA=.5/gfB=.1/stats; real native primary+skin+person; original Apple final kernels only. All upstream items held fixed during parameter-only tests.','complete_camera_inverse_verified':False},indent=2)+'\n')
# Hash all native evidence before discarding only this job's redundant temporary
# raw files; their final native deltas plus immutable source reconstruct outputs.
(O/'raw-sha256.json').write_text(json.dumps([{'path':p.name,'sha256':sha(p),'bytes':p.stat().st_size} for p in raw.iterdir() if p.is_file()],indent=2)+'\n')
