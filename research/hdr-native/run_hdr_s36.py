"""Original RGB guided host oracle at its measured epsilon=.001, not .05."""
from pathlib import Path
import os,sys,json,subprocess,hashlib,zipfile,math
import numpy as np
sys.path.insert(0,str(Path('research/hdr-native').resolve()))
import guided_reference_v3 as guided
W=Path(os.environ['W']);O=W/'out';D=Path('research/hdr-native');up=W/'S34.zip'
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def writej(p,v):p.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def metric(a,b):
 a=np.asarray(a)[...,:3];b=np.asarray(b)[...,:3];d=a.astype('f8')-b.astype('f8');finite=np.isfinite(d)
 if not finite.all():return {'nonfinite_components':int((~finite).sum()),'max_abs':None,'half_different_components':int(np.count_nonzero(a.astype('f2').view('u2')!=b.astype('f2').view('u2'))),'half_bit_exact':False}
 mse=float(np.mean(d*d));pos=(a>0)&(b>0);ev=np.log2(a[pos].astype('f8')/b[pos].astype('f8'));count=int(np.count_nonzero(a.astype('f2').view('u2')!=b.astype('f2').view('u2')))
 return {'nonfinite_components':0,'max_abs':float(abs(d).max()),'half_different_components':count,'half_bit_exact':count==0,'PSNR_peak1_db':-10*math.log10(mse) if mse else 'inf','max_relative_ref_gt_1e-6':float((abs(d[b>1e-6])/b[b>1e-6]).max()) if (b>1e-6).any() else None,'max_abs_EV_positive':float(abs(ev).max()) if ev.size else None,'rms_EV_positive':float(np.sqrt(np.mean(ev*ev))) if ev.size else None}
def edges(a,main,small):
 a=a[...,:3].astype('f8');main=main[...,:3].astype('f8');dx=np.diff(a,axis=1);dy=np.diff(a,axis=0);gx=np.max(abs(np.diff(main,axis=1)),axis=-1);gy=np.max(abs(np.diff(main,axis=0)),axis=-1);ex=gx>.08;ey=gy>.08;v=np.concatenate([abs(dx)[ex].reshape(-1),abs(dy)[ey].reshape(-1)]);lo=small[...,:3].min((0,1));hi=small[...,:3].max((0,1))
 return {'gradient_mean_x':float(abs(dx).mean()),'gradient_mean_y':float(abs(dy).mean()),'gradient_max':float(max(abs(dx).max(),abs(dy).max())),'edge_jump_mean':float(v.mean()) if v.size else None,'below_small_global_min_components':int((a<lo).sum()),'above_small_global_max_components':int((a>hi).sum()),'interpretation':'Synthetic diagnostics only; a gradient difference is not automatically a halo improvement'}
assert subprocess.check_output(['sw_vers','-buildVersion'],text=True).strip()=='26A434'
assert sha(up)==os.environ['S34_ARCHIVE_SHA256']
writej(O/'freeze.json',{'scope':'Original prepared host RGB LTM maps, measured epsilon .001, no precision fit','upstream_archive_sha256':sha(up),'upstream_run_id':39244341548,'parameter_evidence':'S35 run39245992644, six encodeToCommandBuffer calls radius1 epsilon0.0010000000474974513; scalar .05 unchanged','host_expected_guided_calls':2,'host_expected_dispatches':7,'source_sha256':{str(p):sha(p) for p in [D/'run_hdr_s36.py',D/'ltm_materialize_s36.m',D/'guided_reference_v3.py']},'only_executed_native_mode':'host','synthetic_only':True,'true_photos':0,'acceptance_complete':False})
with (O/'build.log').open('w') as f:subprocess.run(['clang','-O2','-g','-fobjc-arc','-framework','Foundation','-framework','Metal',D/'ltm_materialize_s36.m','-o',W/'probe'],stdout=f,stderr=subprocess.STDOUT,check=True)
rows=[]
with zipfile.ZipFile(up) as z:
 manifest=json.loads(z.read('manifest.json'));assert manifest['os_build']=='26A434' and manifest['synthetic_only'] and not manifest['photos_used'];entries={e['path']:e for e in manifest['files']};previous=json.loads(z.read('analysis-s34.json'))
 for prev in previous['rows']:
  case=prev['case'];root=O/case;root.mkdir();out=root/'host-prepared';out.mkdir()
  for name in ['fixture.json','main.f16','linear.f16','gtc.f16','params.bin','color.bin']:
   path=case+'/'+name;b=z.read(path);assert hashlib.sha256(b).hexdigest()==entries[path]['sha256'];(root/name).write_bytes(b)
  with (out/'native.log').open('w') as f:
   try:rc=subprocess.run([W/'probe',root,out,'host'],stdout=f,stderr=subprocess.STDOUT,timeout=240).returncode
   except subprocess.TimeoutExpired:rc=124
  native=json.loads((out/'native.json').read_text()) if (out/'native.json').exists() else {'success':False};row={'case':case,'native_returncode':rc,'native':native,'small_map_vs_immutable_S34_imageblock':{},'frozen_numpy_guided_vs_original_host':{},'bilinear_vs_original_host':{},'edge_diagnostics':{},'original_host_guided_qualified':False};rows.append(row)
  if rc:continue
  def load(key):
   s=native['textures'][key];return np.fromfile(out/s['file'],dtype=s['dtype']).reshape(s['shape'])
  main=load('main');hh,ww=main.shape[:2]
  for branch in ['bg','fg']:
   key=branch+'-small';small=load(key);old=prev['modes']['direct-imageblock']['native']['textures'][key];path=case+'/direct-imageblock/'+old['file'];b=z.read(path);assert hashlib.sha256(b).hexdigest()==entries[path]['sha256'];b=np.frombuffer(b,dtype=old['dtype']).reshape(old['shape']);row['small_map_vs_immutable_S34_imageblock'][key]=metric(small,b)
   full=load(branch+'-full');pred=guided.upsample(small,main,epsilon=float(np.float32(.001)),rows=32);row['frozen_numpy_guided_vs_original_host'][branch]=metric(pred,full)
   ux=(np.arange(ww,dtype='f4')[None,:]+np.float32(.5))/np.float32(ww);uy=(np.arange(hh,dtype='f4')[:,None]+np.float32(.5))/np.float32(hh);bilinear=guided.normalized_sample(small,ux,uy);row['bilinear_vs_original_host'][branch]=metric(bilinear,full)
   xx=(np.arange(64,dtype='f4')[None,:]+np.float32(.5))/64;yy=(np.arange(64,dtype='f4')[:,None]+np.float32(.5))/64
   row['edge_diagnostics'][branch]={'native':edges(full,main,small),'bilinear':edges(bilinear,main,small),'native_center_sample_anchor':metric(guided.normalized_sample(full,xx,yy),small),'bilinear_center_sample_anchor':metric(guided.normalized_sample(bilinear,xx,yy),small)}
  row['original_host_guided_qualified']=native.get('host_preconditions_verified') is True and len(native.get('guided_calls',[]))==2 and native.get('dispatch_count')==7 and all(x['half_bit_exact'] for x in row['small_map_vs_immutable_S34_imageblock'].values())
qualified=len(rows)==3 and all(r['original_host_guided_qualified'] for r in rows)
writej(O/'analysis-s36.json',{'os_build':'26A434','image_version':os.environ.get('ImageVersion'),'scope':'Original RGB LTM branch, three unchanged synthetic fixtures, actual host epsilon .001 and original PSOs','rows':rows,'original_host_guided_qualified':qualified,'numpy_half_bit_exact':qualified and all(m['half_bit_exact'] for r in rows for m in r['frozen_numpy_guided_vs_original_host'].values()),'supersedes':'S34 host had missing preparation; S35 failed an incorrect .05 expectation after recording .001; neither was a qualified full-map oracle','acceptance_complete':False})
print(json.dumps({'original_host_guided_qualified':qualified,'native_returncodes':[r['native_returncode'] for r in rows],'acceptance_complete':False}))
sys.exit(0 if qualified else 1)
