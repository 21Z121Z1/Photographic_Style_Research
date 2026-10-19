"""Synthetic geometry/resource isolation after S38 lost an exception detail."""
from pathlib import Path
import os,subprocess,json,hashlib,struct,shutil
import numpy as np
W=Path(os.environ['W']);O=W/'out';D=Path('research/hdr-native')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,x):p.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
assert subprocess.check_output(['sw_vers','-buildVersion'],text=True).strip()=='26A434'
save(O/'freeze.json',{'scope':'Synthetic geometry and original allocator preconditions only, not inverse/photograph accuracy','geometries':[[960,1280],[3024,4032],[4284,5712]],'linear_shape':[768,1024,4],'original_host':'prepareToProcess:2 then _processLTMGainMap, no allocation override','radius':1,'epsilon':float(np.float32(.001)),'source_sha256':{str(p):sha(p) for p in [D/'ltm_geometry_s39.m',D/'run_hdr_s39.py']},'original_metallib_sha256':sha('/System/Library/PrivateFrameworks/CMImaging.framework/Versions/A/Resources/default.metallib'),'synthetic_only':True,'photos_used':False,'acceptance_complete':False})
with (O/'build.log').open('w') as f:subprocess.run(['clang','-O2','-g','-fobjc-arc','-framework','Foundation','-framework','Metal',D/'ltm_geometry_s39.m','-o',W/'probe'],stdout=f,stderr=subprocess.STDOUT,check=True)
rows=[]
for h,w in [(960,1280),(3024,4032),(4284,5712)]:
 case=W/f'{w}x{h}';case.mkdir();out=case/'native';out.mkdir();dest=O/f'{w}x{h}';dest.mkdir();assert shutil.disk_usage(W).free>6_000_000_000
 main=np.memmap(case/'main.f16',mode='w+',dtype='<f2',shape=(h,w,4))
 for t in range(0,h,32):main[t:t+32,:,:3]=np.float16(.18);main[t:t+32,:,3]=1
 main.flush();del main
 linear=np.full((768,1024,4),np.float16(.02),dtype='<f2');linear[...,3]=1;linear.tofile(case/'linear.f16');np.linspace(0,1,256,dtype='f2').reshape(1,256,1).tofile(case/'gtc.f16');save(case/'fixture.json',{'main':{'file':'main.f16','shape':[h,w,4]},'linear':{'file':'linear.f16','shape':[768,1024,4]},'gtc':{'file':'gtc.f16','shape':[1,256,1]}})
 p=bytearray(672);c=bytearray(320)
 for off,val in [(24,1.),(28,1.),(628,1.),(632,1.),(636,0.)]:struct.pack_into('<f',p,off,val)
 for start in range(0,320,80):
  for k in range(3):struct.pack_into('<f',c,start+16+16*k+4*k,1.)
 (case/'params.bin').write_bytes(p);(case/'color.bin').write_bytes(c)
 with (dest/'native.log').open('w') as f:
  try:rc=subprocess.run([W/'probe',case,out,'host'],stdout=f,stderr=subprocess.STDOUT,timeout=600).returncode
  except subprocess.TimeoutExpired:rc=124
 for p in out.glob('*'):
  if p.suffix in ['.json','.log','.txt']:shutil.copyfile(p,dest/p.name)
 native=json.loads((out/'native.json').read_text()) if (out/'native.json').exists() else None
 row={'shape':[h,w,4],'native_returncode':rc,'native':native,'checkpoint':json.loads((out/'checkpoint.json').read_text()) if (out/'checkpoint.json').exists() else None};rows.append(row)
 if rc==0 and native:
  spec=native['textures']['bg-full'];a=np.memmap(out/spec['file'],dtype=spec['dtype'],mode='r',shape=tuple(spec['shape']));count=0;minimum=float('inf');maximum=float('-inf');nonfinite=0
  for t in range(0,h,32):
   v=a[t:t+32,:,:3];count+=int(np.count_nonzero(v));nonfinite+=int((~np.isfinite(v)).sum());minimum=min(minimum,float(v.min()));maximum=max(maximum,float(v.max()))
  row['full_output_summary']={'nonzero_components':count,'nonfinite_components':nonfinite,'minimum':minimum,'maximum':maximum};del a
 save(O/'analysis-s39.json',{'os_build':'26A434','image_version':os.environ.get('ImageVersion'),'rows':rows,'all_geometry_native_success':len(rows)==3 and all(r['native_returncode']==0 for r in rows),'scope':'Diagnostic completion is not a gate pass; original default allocator only','acceptance_complete':False})
 shutil.rmtree(case)
print(json.dumps({'native_returncodes':[r['native_returncode'] for r in rows],'acceptance_complete':False}))
