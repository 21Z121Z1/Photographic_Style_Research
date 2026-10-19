"""Qualify original host guided participation; reuse immutable S34 controls."""
from pathlib import Path
import os,sys,json,subprocess,hashlib,zipfile,math
import numpy as np
W=Path(os.environ['W']);O=W/'out';D=Path('research/hdr-native');up=W/'S34.zip'
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def writej(p,v):p.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def metric(a,b):
 a=a[...,:3];b=b[...,:3];d=a.astype('f8')-b.astype('f8');finite=np.isfinite(d)
 if not finite.all():return {'nonfinite_components':int((~finite).sum()),'max_abs':None,'half_different_components':int(np.count_nonzero(a.view('u2')!=b.view('u2')))}
 mse=float(np.mean(d*d));pos=(a>0)&(b>0);ev=np.log2(a[pos].astype('f8')/b[pos].astype('f8'))
 return {'nonfinite_components':0,'max_abs':float(abs(d).max()),'half_different_components':int(np.count_nonzero(a.view('u2')!=b.view('u2'))),'PSNR_peak1_db':-10*math.log10(mse) if mse else 'inf','max_abs_EV_positive':float(abs(ev).max()) if ev.size else None}
assert subprocess.check_output(['sw_vers','-buildVersion'],text=True).strip()=='26A434'
assert sha(up)==os.environ['S34_ARCHIVE_SHA256']
writej(O/'freeze.json',{'scope':'Repair demonstrated S34 missing host resource precondition; no new parameters, no precision fitting','upstream_archive_sha256':sha(up),'upstream_run_id':39244341548,'host_expected_guided_calls':2,'host_expected_dispatches':7,'source_sha256':{str(p):sha(p) for p in [D/'run_hdr_s35.py',D/'ltm_materialize_s35.m',D/'ltm_materialize_s34.m']},'synthetic_only':True,'true_photos':0,'acceptance_complete':False})
with (O/'build.log').open('w') as f:subprocess.run(['clang','-O2','-g','-fobjc-arc','-framework','Foundation','-framework','Metal',D/'ltm_materialize_s35.m','-o',W/'probe'],stdout=f,stderr=subprocess.STDOUT,check=True)
rows=[]
with zipfile.ZipFile(up) as z:
 manifest=json.loads(z.read('manifest.json'));assert manifest['os_build']=='26A434' and manifest['synthetic_only'] and not manifest['photos_used'];entries={e['path']:e for e in manifest['files']}
 previous=json.loads(z.read('analysis-s34.json'))
 for prev in previous['rows']:
  case=prev['case'];root=O/case;root.mkdir();out=root/'host-prepared';out.mkdir()
  for name in ['fixture.json','main.f16','linear.f16','gtc.f16','params.bin','color.bin']:
   path=case+'/'+name;b=z.read(path);assert hashlib.sha256(b).hexdigest()==entries[path]['sha256'];(root/name).write_bytes(b)
  with (out/'native.log').open('w') as f:
   try:rc=subprocess.run([W/'probe',root,out,'host'],stdout=f,stderr=subprocess.STDOUT,timeout=240).returncode
   except subprocess.TimeoutExpired:rc=124
  native=json.loads((out/'native.json').read_text()) if (out/'native.json').exists() else {'success':False}
  row={'case':case,'native_returncode':rc,'native':native,'comparison_to_immutable_S34_direct_imageblock':{},'original_host_guided_qualified':False};rows.append(row)
  if rc:continue
  for key in ['bg-small','fg-small','bg-full','fg-full']:
   spec=native['textures'][key];a=np.fromfile(out/spec['file'],dtype=spec['dtype']).reshape(spec['shape']);old=prev['modes']['direct-imageblock']['native']['textures'][key];path=case+'/direct-imageblock/'+old['file'];b=z.read(path);assert hashlib.sha256(b).hexdigest()==entries[path]['sha256'];b=np.frombuffer(b,dtype=old['dtype']).reshape(old['shape']);row['comparison_to_immutable_S34_direct_imageblock'][key]=metric(a,b)
  row['original_host_guided_qualified']=native.get('host_preconditions_verified') is True and len(native.get('guided_calls',[]))==2 and native.get('dispatch_count')==7 and all(x['half_different_components']==0 for x in row['comparison_to_immutable_S34_direct_imageblock'].values())
qualified=len(rows)==3 and all(r['original_host_guided_qualified'] for r in rows)
writej(O/'analysis-s35.json',{'os_build':'26A434','image_version':os.environ.get('ImageVersion'),'scope':'Three unchanged S34 synthetic fixtures, original host prepare/allocator plus two guided calls; not a full photo inverse','rows':rows,'original_host_guided_qualified':qualified,'supersedes':'S34 host full-map comparisons are missing-precondition diagnostics, never accepted oracle','acceptance_complete':False})
print(json.dumps({'original_host_guided_qualified':qualified,'native_returncodes':[r['native_returncode'] for r in rows],'acceptance_complete':False}))
sys.exit(0 if qualified else 1)
