"""One new paired full-resolution comparison, reusing both old scene and S42 native output."""
from pathlib import Path
import os,sys,subprocess,json,hashlib,zipfile,tarfile,threading,shutil,math
import numpy as np
import OpenEXR,Imath,PyOpenColorIO as ocio
from PIL import Image,ImageDraw
from baseline_ops_s48 import linear_resize,AreaAccumulator
from render_intent_s44 import Y
R=Path.cwd();D=R/'research/hdr-native';W=Path(os.environ['W']);O=W/'out';PRIVATE=W/'private';CASE=W/'case';CASE.mkdir();ROWS=32
PHOTO=R/'research/vm-native/samples/IMG_2600.HEIC';SOURCE_SHA='63872222783e757a41a41337b48875e1172e68ace0f6e411db999c77b027a4d0';ZIP_SHA='897065d3ea71e3068f2af8ee98ef8745065b923c6692f0366d98cd1b3069d621';CIPHER_SHA='d1c3d9beabec857f972f897a7ef91f0fbee8df8d9ab270c7f97949235ae30c86';EXR_SHA='69c553e49f3c70ffbebc6e85d32ad6933fe3582535088dd24f60f59c398c4634'
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,v):p.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def command(args,log,timeout=1200):
 with log.open('w') as f:r=subprocess.run([str(x) for x in args],stdout=f,stderr=subprocess.STDOUT,timeout=timeout)
 if r.returncode:raise RuntimeError(f'{Path(str(args[0])).name} return{r.returncode}; see {log.name}')
assert sys.platform=='darwin' and subprocess.check_output(['sw_vers','-buildVersion'],text=True).strip()=='26A434';assert sha(PHOTO)==SOURCE_SHA and sha(W/'S42.zip')==ZIP_SHA
cfg=ocio.Config.CreateFromBuiltinConfig('cg-config-v2.2.0_aces-v1.3_ocio-v2.4');cpu=cfg.getProcessor('Linear P3-D65','sRGB - Display','ACES 1.0 - SDR Video',ocio.TRANSFORM_DIR_FORWARD).getDefaultCPUProcessor();display={'config':'cg-config-v2.2.0_aces-v1.3_ocio-v2.4','config_sha256':hashlib.sha256(cfg.serialize().encode()).hexdigest(),'source':'Linear P3-D65','display':'sRGB - Display','view':'ACES 1.0 - SDR Video','exposure_ev':0,'common_scene_display_scale':13.164076042436493}
desc=json.loads((D/'transport-input-s49.json').read_text());assert sha(W/'legacy.tar.gpg')==desc['cipher_sha256']
freeze={'os_build':'26A434','source_sha256':{str(p):sha(p) for p in [D/x for x in ['run_hdr_s49.py','baseline_ops_s48.py','read_sdr_s44.m']]},'upstream':{'run_id':'39254061338','artifact_id':'12188060302','ZIP_sha256':ZIP_SHA,'cipher_sha256':CIPHER_SHA,'master_EXR_sha256':EXR_SHA},'legacy_input':desc,'comparison':'Existing frozen2048 RGB output bilinear-upsampled, versus immutable S42 nativeRGB projection. No key1 or guided recomputation. Same original full-resolution SDR edge reference for both.','units':'Multiply S42 relative M by the original stored legacy exposure factor, no exposure fitting; identical final display conversion K/legacyFactor on both.','edge_selection':'Joint finite/nonnegative luma domain of both outputs and original SDR Y>1e-4, source central gradient above fixed sparse-neighbor p95. Diagnostic selection only, no original inverse mask or acceptance gate changed.','metrics':'Paired edge-gradient transfer, gain curvature and sign reversals, edge/far pair difference. These are proxies without pristine scene truth. All negative/nonfinite components and area-anchor errors reported separately.','reference_scope':'New paired SDR-reference metric, not interchangeable with older u-reference metrics; frozen legacy file is exact but previous scalar rows are context only.','ROIs':[[1600,1800,256,256],[4000,1100,256,256],[2800,3400,256,256]],'display':display,'precision_thresholds_unchanged':True,'scope':'One development photograph, not new five-photo suite, native whole-consumer inverse, RAW or physical scene proof'}
save(O/'freeze.json',freeze);freeze_sha=sha(O/'freeze.json');failed=[];member_facts=[]
with zipfile.ZipFile(W/'S42.zip') as z:
 assert z.namelist()==['IMG_2600-full.tar.gz.gpg']
 with z.open(z.namelist()[0]) as f:assert hashlib.file_digest(f,'sha256').hexdigest()==CIPHER_SHA
 # Scope the temporary secret to this one cipher; no archive private key.
 session=os.environ.pop('S49_S42_SESSION').encode();assert b':' in session and len(session)<200
 readfd,writefd=os.pipe();plaintext=CASE/'upstream.tar.gz';pipe_error=None
 with (W/'secure/decrypt.log').open('w') as err,plaintext.open('xb') as output:
  p=subprocess.Popen(['gpg','--batch','--override-session-key-fd',str(readfd),'--status-fd','2','--decrypt'],pass_fds=(readfd,),stdin=subprocess.PIPE,stdout=output,stderr=err)
  os.close(readfd);os.write(writefd,session+b'\n');os.close(writefd);del session
  try:
   with z.open(z.namelist()[0]) as f:shutil.copyfileobj(f,p.stdin,1<<16)
  except BrokenPipeError:pipe_error='Cipher pipe closed before EOF'
  finally:
   try:p.stdin.close()
   except BrokenPipeError:pipe_error='Cipher pipe closed before EOF'
  rc=p.wait(timeout=120)
 private_stderr=(W/'secure/decrypt.log').read_text(errors='replace');events=[line.split()[1] for line in private_stderr.splitlines() if line.startswith('[GNUPG:] ') and len(line.split())>1];del private_stderr
 with plaintext.open('rb') as f:magic=f.read(2)
 save(O/'decrypt-status.json',{'GPG_returncode':rc,'GPG_version':subprocess.check_output(['gpg','--version'],text=True).splitlines()[0],'status_event_names_only':events,'pipe_error':pipe_error,'plaintext_bytes':plaintext.stat().st_size,'gzip_magic':magic.hex(),'archive_private_key_supplied':False,'raw_private_stderr_uploaded':False})
 assert rc==0 and not pipe_error and magic==b'\x1f\x8b','GPG/gzip prerequisite failed; inspect sanitized decrypt-status.json'
 with tarfile.open(plaintext,'r:gz') as tar:
  for m in tar:
   if not m.isfile():continue
   rel=Path(m.name);assert rel.parts[0]=='full' and '..' not in rel.parts and not rel.is_absolute();assert m.size<400_000_000;h=hashlib.sha256();output=(CASE/'master.exr').open('xb') if rel.name=='scene_candidate_linear_P3.exr' else None
   with tar.extractfile(m) as f:
    while data:=f.read(1<<20):h.update(data);output.write(data) if output else None
   if output:output.close()
   member_facts.append({'path':str(rel),'size':m.size,'sha256':h.hexdigest(),'materialized':output is not None})
assert {Path(x['path']).name for x in member_facts}=={'scene_candidate_linear_P3.exr','log2_RGB_gain.exr','positive_pair_mask.npy','meaning.json'};assert sha(CASE/'master.exr')==EXR_SHA;assert next(x['sha256'] for x in member_facts if x['path'].endswith('/log2_RGB_gain.exr'))=='b846859e6e5bcdc82921c4038aa7863c96dacc27245020953eff0bb6f10f0014';save(O/'upstream-verified.json',{'upstream':freeze['upstream'],'GPG_returncode':rc,'members':member_facts,'private_key_uploaded_in_artifact':False,'session_only_transport':True})
# Decrypt only the existing frozen legacy output, no local generation or refit.
password=os.environ.pop('S49_LEGACY_PASS').encode();fd,wr=os.pipe()
with (W/'secure/legacy-decrypt.log').open('w') as err,(CASE/'legacy.tar').open('xb') as output:
 proc=subprocess.Popen(['gpg','--batch','--pinentry-mode','loopback','--passphrase-fd',str(fd),'--status-fd','2','--decrypt',W/'legacy.tar.gpg'],pass_fds=(fd,),stdin=subprocess.DEVNULL,stdout=output,stderr=err);os.close(fd);os.write(wr,password+b'\n');os.close(wr);del password;rc=proc.wait(timeout=180)
save(O/'legacy-decrypt-status.json',{'returncode':rc,'cipher_sha256':sha(W/'legacy.tar.gpg'),'private_material_uploaded':False});assert rc==0
legacy=CASE/'legacy';legacy.mkdir();members=[]
with tarfile.open(CASE/'legacy.tar','r:') as tar:
 for m in tar:
  if not m.isfile():continue
  path=Path(m.name);assert len(path.parts)==1 and not path.is_absolute() and path.name in {'legacy_scene.npy','native_linear.f32','legacy_scene.json','thumbnail-facts.json','previous-comparison.json','manifest.json'}
  with tar.extractfile(m) as a,(legacy/path).open('xb') as b:shutil.copyfileobj(a,b,1<<16)
  members.append(path.name)
assert sha(legacy/'manifest.json')==desc['manifest_sha256'];mf=json.loads((legacy/'manifest.json').read_text());assert set(members)=={x['path'] for x in mf['files']}|{'manifest.json'}
for x in mf['files']:assert (legacy/x['path']).stat().st_size==x['size'] and sha(legacy/x['path'])==x['sha256']
save(O/'legacy-input-verified.json',{'files':mf['files'],'originals_unchanged':True,'cipher_sha256':desc['cipher_sha256'],'legacy_algorithm_not_recomputed':True})
old=np.load(legacy/'legacy_scene.npy',mmap_mode='r');assert old.shape==(1536,2048,3) and old.dtype==np.dtype('<f4');meta=json.loads((legacy/'legacy_scene.json').read_text());exposure=float(np.exp2(meta['exposure_ev']));native_thumb=np.memmap(legacy/'native_linear.f32',dtype='<f4',mode='r',shape=(768,1024,4));half_hash=hashlib.sha256(native_thumb.astype('<f2').tobytes()).hexdigest();expected_half='2d8ee1596d8f2d1f79a870a288ca398a445883f8499ef9bb9bee8d0fcca6f0a0';save(O/'anchor-compatibility.json',{'old_anchor_float32_sha256':sha(legacy/'native_linear.f32'),'old_float32_to_half_sha256':half_hash,'S42_native_GPU_input_half_sha256':expected_half,'same_GPU_anchor':half_hash==expected_half,'old_exposure_EV':meta['exposure_ev'],'units_scale':exposure});assert half_hash==expected_half,'Anchor differs: do not claim same input'
target=(np.maximum(native_thumb[...,:3],0)*np.exp2(meta['exposure_ev'])).astype('f4');h,w=4284,5712;master=np.memmap(CASE/'master.f16',dtype='<f2',mode='w+',shape=(h,w,3));exr=OpenEXR.InputFile(str(CASE/'master.exr'));pt=Imath.PixelType(Imath.PixelType.HALF)
for c,name in enumerate('RGB'):
 for top in range(0,h,ROWS):stop=min(h,top+ROWS);master[top:stop,:,c]=np.frombuffer(exr.channel(name,pt,top,stop-1),dtype='<f2').reshape(stop-top,w)
exr.close();master.flush();flags=['clang','-O2','-fobjc-arc','-framework','Foundation','-framework','CoreImage','-framework','ImageIO','-framework','Metal','-framework','CoreGraphics'];command(flags+[D/'read_sdr_s44.m','-o',W/'source'],O/'source-build.log');command([W/'source',PHOTO,CASE],O/'source.log');sdr=np.memmap(CASE/'original-sdr.f32',dtype='<f4',mode='r',shape=(h,w,4));before={'legacy_scene':sha(legacy/'legacy_scene.npy'),'master':sha(CASE/'master.exr'),'SDR':sha(CASE/'original-sdr.f32'),'photo':sha(PHOTO)}
sy=np.arange(0,h-1,16);sx=np.arange(0,w-1,16)
def sample_s(y,x):return np.maximum(sdr[y,x,:3].astype('f4'),0)@Y
y0=sample_s(sy[:,None],sx[None,:]);yx=sample_s(sy[:,None],sx[None,:]+1);yy=sample_s(sy[:,None]+1,sx[None,:]);threshold=float(np.percentile(np.hypot(np.log2((yx+1e-6)/(y0+1e-6)),np.log2((yy+1e-6)/(y0+1e-6))),95));stats={};acc={};joint_edge=0;joint_valid=0;edge_delta=[];far_delta=[]
for name in ['legacy2048','nativeRGB']:stats[name]={'gradient':[],'curvature_sum':0.,'curvature_n':0,'slope_reversal_n':0,'negative_components':0,'nonfinite_components':0};acc[name]=AreaAccumulator((h,w),(768,1024))
for top in range(0,h,ROWS):
 stop=min(h,top+ROWS);a=max(0,top-1);b=min(h,stop+1);begin=top-a;end=stop-a;tiles={'legacy2048':linear_resize(old,(h,w),a,b),'nativeRGB':(master[a:b].astype('f8')*exposure).astype('f4')};source=np.maximum(sdr[a:b,:,:3].astype('f4'),0)@Y;logs=np.log2(source+1e-6);gy,gx=np.gradient(logs);mag=np.hypot(gy,gx);lum={k:rgb@Y for k,rgb in tiles.items()};valid=np.isfinite(source)&(source>1e-4)
 for k in lum:valid&=np.isfinite(lum[k])&(lum[k]>1e-4)
 region=np.zeros_like(valid);region[begin:end]=True;valid&=region;valid[[0,-1],:]=False;valid[:,[0,-1]]=False;edges=valid&(mag>threshold);joint_valid+=int(valid.sum());joint_edge+=int(edges.sum());gains={}
 for name,rgb in tiles.items():
  state=stats[name];state['negative_components']+=int((rgb[begin:end]<0).sum());state['nonfinite_components']+=int((~np.isfinite(rgb[begin:end])).sum());acc[name].add(top,rgb[begin:end]);l=np.log2(np.maximum(lum[name]+1e-6,1e-30));dy,dx=np.gradient(l);state['gradient'].append((np.hypot(dy,dx)[edges]/np.maximum(mag[edges],1e-6))[::16]);ev=l-logs;gains[name]=ev
  for axis in [0,1]:
   left=np.diff(ev,axis=axis);lo=[slice(None),slice(None)];hi=[slice(None),slice(None)];center=[slice(None),slice(None)];lo[axis]=slice(None,-1);hi[axis]=slice(1,None);center[axis]=slice(1,-1);p=left[tuple(lo)];q=left[tuple(hi)];sel=edges[tuple(center)];state['curvature_sum']+=float(abs(q-p)[sel].sum());state['curvature_n']+=int(sel.sum());state['slope_reversal_n']+=int(((p*q<0)&sel).sum())
 diff=abs(gains['nativeRGB']-gains['legacy2048']);edge_delta.append(diff[edges][::16]);far_delta.append(diff[valid&(mag<=threshold*.2)][::32])
rows=[]
for name,state in stats.items():
 anchor=acc[name].result();ev=np.log2((anchor@Y+1e-6)/(target@Y+1e-6));ratios=np.concatenate(state.pop('gradient'));n=state.pop('curvature_n');curv=state.pop('curvature_sum');reversal=state.pop('slope_reversal_n');rows.append({'variant':name,'anchor_MAE_EV':float(abs(ev).mean()),'anchor_p99_EV':float(np.percentile(abs(ev),99)),'anchor_max_EV':float(abs(ev).max()),'joint_edge_gradient_ratio_median':float(np.median(ratios)) if ratios.size else None,'joint_edge_gradient_ratio_p95':float(np.percentile(ratios,95)) if ratios.size else None,'joint_edge_gain_curvature_mean_EV':curv/n if n else None,'joint_edge_gain_slope_reversal_fraction':reversal/n if n else None,'edge_gradient_samples':len(ratios),**state})
report={'os_build':'26A434','image_version':os.environ.get('ImageVersion'),'freeze_sha256':freeze_sha,'photo':'IMG_2600','shape':[h,w,3],'rows':rows,'same_GPU_half_anchor':True,'legacy_exposure_EV':meta['exposure_ev'],'joint_valid_pixels':joint_valid,'joint_edge_pixels':joint_edge,'source_edge_threshold_EV_per_pixel':threshold,'edge_pair_difference_p99_EV':float(np.percentile(np.concatenate(edge_delta),99)),'far_pair_difference_p99_EV':float(np.percentile(np.concatenate(far_delta),99)),'proxy_scope':freeze['metrics'],'comparison_mask_scope':'New common diagnostic region, no inverse/33-point/transport acceptance mask modified','display':display,'inputs_before':before,'acceptance_complete':False,'A_phase_complete':False,'physical_scene_verified':False,'native_guided_recomputed':False,'legacy_scene_recomputed':False};save(O/'analysis-s49.json',report)
preview_checks=[];cards=[]
def preview(name,rgb):
 first=hashlib.sha256(np.ascontiguousarray(rgb).tobytes()).hexdigest();x=np.array(rgb,dtype='f4',order='C',copy=True);x[~np.isfinite(x)]=0;cpu.apply(ocio.PackedImageDesc(x,x.shape[1],x.shape[0],3));im=Image.fromarray(np.rint(np.clip(x,0,1)*255).astype('u1'));im.save(PRIVATE/(name+'.png'));assert first==hashlib.sha256(np.ascontiguousarray(rgb).tobytes()).hexdigest();preview_checks.append({'name':name,'input_before_sha256':first,'input_after_sha256':first});return im
ph,pw=480,640;py=np.floor((np.arange(ph)+.5)*h/ph).astype(int);px=np.floor((np.arange(pw)+.5)*w/pw).astype(int)
# Bounded one-row legacy sampling; never construct a full float64 resized image.
old_over=np.stack([linear_resize(old,(h,w),int(y),int(y)+1)[0,px] for y in py]);new_over=master[py[:,None],px[None,:]].astype('f4');scale=display['common_scene_display_scale'];cards.append((preview('legacy2048-overview',old_over*(scale/exposure)),preview('nativeRGB-overview',new_over*scale)))
for i,(x,y,cw,ch) in enumerate(freeze['ROIs']):
 oldcrop=linear_resize(old,(h,w),y,y+ch)[:,x:x+cw];newcrop=master[y:y+ch,x:x+cw].astype('f4');cards.append((preview(f'ROI{i}-legacy',oldcrop*(scale/exposure)),preview(f'ROI{i}-nativeRGB',newcrop*scale)))
sheet=Image.new('RGB',(640,len(cards)*280),'white');draw=ImageDraw.Draw(sheet)
for n,pair in enumerate(cards):
 for col,im in enumerate(pair):im.thumbnail((320,256));sheet.paste(im,(col*320,n*280));draw.text((col*320+3,n*280+260),('legacy2048','nativeRGB')[col]+(' overview' if n==0 else f' ROI{n-1}'),fill='black')
sheet.save(PRIVATE/'contact.private.png');after={'legacy_scene':sha(legacy/'legacy_scene.npy'),'master':sha(CASE/'master.exr'),'SDR':sha(CASE/'original-sdr.f32'),'photo':sha(PHOTO)};assert after==before;report['inputs_after']=after;report['preview_input_checks']=preview_checks;report['completed']=True;save(O/'analysis-s49.json',report);assert sha(O/'freeze.json')==freeze_sha
save(PRIVATE/'manifest.json',{'run_id':os.environ['GITHUB_RUN_ID'],'commit':os.environ['GITHUB_SHA'],'os_build':'26A434','people_results_encrypted':True,'files':[{'path':p.name,'size':p.stat().st_size,'sha256':sha(p)} for p in sorted(PRIVATE.glob('*.png'))]})
with tarfile.open(W/'previews.tar.gz','w:gz') as tar:tar.add(PRIVATE,arcname='out')
command(['gpg','--batch','--trust-model','always','--recipient','28E62F64A29764C2F2AEBF5D5B6B1C101E5F5ABA','--encrypt','--output',W/'encrypted/previews.tar.gz.gpg',W/'previews.tar.gz'],O/'encrypt.log');out=W/'encrypted/previews.tar.gz.gpg';save(O/'encrypted-inventory.json',{'files':[{'file':out.name,'size':out.stat().st_size,'sha256':sha(out)}],'plaintext_uploaded':False});print(json.dumps({'completed':True,'joint_edge_pixels':joint_edge,'legacy_and_native_recomputed':False,'rows':rows,'acceptance_complete':False}))
