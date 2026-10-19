"""Inspect S32's existing synthetic encodings, no new codec or inverse fit."""
from pathlib import Path
import os,sys,subprocess,json,hashlib,zipfile,math
sys.path.insert(0,str(Path('.').resolve()))
import numpy as np
from analyze_hdr_s29 import metric
W=Path(os.environ['W']);O=W/'out';O.mkdir(exist_ok=True);D=Path('research/hdr-native');up=W/'S32.zip'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert subprocess.check_output(['sw_vers','-buildVersion'],text=True).strip()=='26A434'
upsha=os.environ.get('S32_ARCHIVE_SHA256','907be588e641ba3ec55a6aa5e0cf6ba9eca5bceae9e602c3f3b3010f2b3ed8bb');assert sha(up)==upsha
(O/'freeze.json').write_text(json.dumps({'scope':'Existing synthetic S32 provider/CPU/GPU decode decomposition, no new encoding or photo','upstream_sha256':upsha,'source_sha256':{p.name:sha(p) for p in [D/'run_hdr_s33.py',D/'decode_layers_s33.m',D/'hdr_headroom_s29.m']},'cases':[[6,8],[6,10],[6,12],[1,12]],'cache_modes':[0,1],'working':'No CI color management; CPU CGContext uses original CGImage color space to avoid a new CMS transform','row_order':'Direct comparison and vertical-flip diagnostic separately; no best-score selection','all_old_gates_masks_unchanged':True},indent=2)+'\n')
with (O/'build.log').open('w') as f:subprocess.run(['clang','-O2','-fobjc-arc','-framework','Foundation','-framework','CoreImage','-framework','ImageIO','-framework','Metal','-framework','CoreGraphics',str(D/'decode_layers_s33.m'),'-o',str(W/'probe')],stdout=f,stderr=subprocess.STDOUT,check=True)
rows=[];w,h=256,128;u=np.broadcast_to((np.arange(w)+.5)/w,(h,w));v=np.broadcast_to(((np.arange(h)+.5)/h)[:,None],(h,w));ev=np.stack([3*u,-.5+2*v,2*(1-u)],-1);code=(ev+.5)/3.5
def comparison(a,b):
 finite=np.isfinite(a).all(-1)&np.isfinite(b).all(-1);out={'vs_expected_integer_rgb':metric(a,b),'nonfinite_pixels':int((~finite).sum())}
 if not finite.all():return out|{'max_abs':None,'vertical_flip_max_abs_diagnostic':None,'pixel_min':None,'pixel_max':None}
 return out|{'max_abs':float(abs(a-b).max()),'vertical_flip_max_abs_diagnostic':float(abs(a[::-1]-b).max()),'pixel_min':float(a.min()),'pixel_max':float(a.max())}
with zipfile.ZipFile(up) as z:
 manifest=json.loads(z.read('manifest.json'));assert manifest['synthetic_only'] and manifest['photos_used'] is False and manifest['os_build']=='26A434'
 for matrix,bits in [(6,8),(6,10),(6,12),(1,12)]:
  case=f'matrix{matrix}-bit{bits}';p=O/case;p.mkdir();q=np.rint(code*(2**bits-1))/(2**bits-1);expected=q.astype('f4').astype('f8');rgba=np.concatenate([expected,np.ones((h,w,1))],-1).astype('<f4');rgba.tofile(p/'expected.f32')
  for name in ['encoded-gain.heic','carrier.heic']:
   b=z.read(case+'/'+name);e=next(x for x in manifest['files'] if x['path']==case+'/'+name);assert hashlib.sha256(b).hexdigest()==e['sha256'];(p/name).write_bytes(b)
  for immediate in [0,1]:
   out=p/f'cache-{immediate}';out.mkdir()
   with (out/'native.log').open('w') as f:rc=subprocess.run([W/'probe',p/'encoded-gain.heic',p/'carrier.heic',p/'expected.f32',out,str(immediate)],stdout=f,stderr=subprocess.STDOUT,timeout=240).returncode
   r={'matrix':matrix,'bits':bits,'immediate_cache':immediate,'native_returncode':rc,'native':json.loads((out/'native.json').read_text()),'comparisons':{}};rows.append(r)
   def load(name,dtype='<f4'):return np.fromfile(out/name,dtype=dtype).reshape(h,w,4)[...,:3].astype('f8')
   for name,spec in r['native'].get('CI_outputs',{}).items():
    if 'file' not in spec:continue
    a=load(spec['file']);r['comparisons'][name]=comparison(a,expected)
   for name,file,dtype,scale in [('CPU-f32','cpu-context.f32','<f4',1),('CPU-u16','cpu-context.u16','<u2',65535)]:
    if not (out/file).exists():continue
    a=load(file,dtype)/scale;r['comparisons'][name]=comparison(a,expected)
   # Equality is checked explicitly, not inferred from coinciding error maxima.
   outputs=r['native'].get('CI_outputs',{});pairs={}
   for x,y in [('URL-Metal','URL-software'),('CGImage-Metal','CGImage-software'),('URL-Metal','CGImage-Metal'),('CPU-bitmap-Metal','CPU-bitmap-software'),('URL-Metal','aux-Metal')]:
    if x in outputs and y in outputs and 'file' in outputs[x] and 'file' in outputs[y]:
     a=load(outputs[x]['file']);b=load(outputs[y]['file']);pairs[x+'__'+y]={'max_abs':float(abs(a-b).max()) if np.isfinite(a).all() and np.isfinite(b).all() else None,'nonfinite_components':int((~np.isfinite(a)|~np.isfinite(b)).sum()),'different_float32_components':int(np.count_nonzero(a.astype('f4').view('u4')!=b.astype('f4').view('u4')))}
   r['explicit_pairwise_readback_comparison']=pairs
report={'os_build':'26A434','scope':'Original ImageIO/Quartz/CI decode layers on existing synthetic files only; no inverse/scene/photograph certification','rows':rows,'acceptance_complete':False}
(O/'analysis-s33.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');print(json.dumps({'cases':len(rows),'native_returncodes':[r['native_returncode'] for r in rows],'acceptance_complete':False}))
