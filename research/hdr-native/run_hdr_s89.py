"""Five original photographs: unchanged S88 carrier math and ideal headrooms.

All numerical image work runs on macOS. Exact pixels and contacts are encrypted.
No new full carrier/master archive is promised for this bounded validation.
"""
from pathlib import Path
import ast,hashlib,json,os,subprocess,sys,math,shutil,tarfile
import numpy as np
import PyOpenColorIO as ocio
from PIL import Image,ImageDraw
R=Path.cwd();D=R/'research/hdr-native';W=Path(os.environ['W']);O=W/'out';PRIVATE=W/'private';ENC=W/'encrypted';sys.path[:0]=[str(R),str(D)]
from tools.heif_dump import parse_heif
Y=np.array([.2289745641,.6917385218,.0792869141]);ROWS=32
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,x):
 with Path(p).open('x')as f:json.dump(x,f,indent=2,allow_nan=False);f.write('\n')
def bindings(template,swaps):
 value=template;counts=[]
 for old,new in swaps:
  count=value.count(old);assert count>0,(old,count);counts.append(count);value=value.replace(old,new)
 inverse=value
 for(old,new),count in reversed(list(zip(swaps,counts))):
  assert inverse.count(new)==count,(old,count);inverse=inverse.replace(new,old)
 assert inverse==template,'Change outside permitted input/archival binding'
 ast.parse(value)
 return value,{'original_sha256':hashlib.sha256(template.encode()).hexdigest(),'derived_sha256':hashlib.sha256(value.encode()).hexdigest(),'inverse_substitutions_equal_original':True,'swaps':[{'old':a,'new':b,'count':n}for(a,b),n in zip(swaps,counts)],'pixel_math_changed':False}
def derive_case(case):
 photo=case['photo'];driver=(D/'run_hdr_s88.py').read_text();helper=(D/'rebuild_master_s88.py').read_text()
 old="case=next(c.copy()for c in json.loads((D/'inputs-s51.json').read_text())['cases']if c['photo']=='IMG_0032');case['role']='integration-development; previous display-only holdout'"
 old_guard="assert case['ZIP_bytes']<1_000_000_000 and subprocess.check_output(['sw_vers','-buildVersion'],text=True).strip()=='26A434'"
 new_guard="assert subprocess.check_output(['sw_vers','-buildVersion'],text=True).strip()=='26A434' # Obsolete ZIP is not read"
 swaps=[(old,"case=json.loads(os.environ['HDR_S89_CASE_JSON'])"),(old_guard,new_guard),("D/'rebuild_master_s88.py'","Path(os.environ['HDR_S89_REBUILD'])"),("[(PRIVATE,'contacts',300000),(full,'carrier',20000000)]","[(PRIVATE,'contacts',300000)]")]
 if photo!='IMG_0032':swaps.append(('IMG_0032',photo))
 driver,dr=bindings(driver,swaps)
 swaps=[]
 for old,new in [('IMG_0032',photo),('9b392ea7cf996d1cbc70fbf82911b3c04e51562653010e7a78ee4a7a8129b012',case['master_EXR_sha256']),('76a2fa2723e5a2419b3752042dda7675077451d957594f6d497f0e613ef6501a',case['source_sha256'])]:
  if old!=new:swaps.append((old,new))
 helper,hr=bindings(helper,swaps)
 return driver,helper,{'driver':dr,'rebuild':hr,'scope':'Only input labels/SHA/selector/helper path and contacts-only archival; S88 pixel math and original S42 AST selection unchanged'}
cfg=ocio.Config.CreateFromBuiltinConfig('cg-config-v2.2.0_aces-v1.3_ocio-v2.4');cpu=cfg.getProcessor('Linear P3-D65','sRGB - Display','ACES 1.0 - SDR Video',ocio.TRANSFORM_DIR_FORWARD).getDefaultCPUProcessor();config_sha=hashlib.sha256(cfg.serialize().encode()).hexdigest();assert config_sha=='5aefc668796eabb1902b9593340496231758eceaec18ce290e12901042bd4440'
input_rows=json.loads((D/'inputs-s89.json').read_text())['cases']
sources=['run_hdr_s89.py','inputs-s89.json','run_hdr_s88.py','rebuild_master_s88.py','run_hdr_s42.py','run_hdr_s47.py','render_intent_s44.py','derive_display_s51.py','carrier_case_s87.py','carrier_readback_s87.m','iso_splice.py']
freeze={'os_build':'26A434','image_version':os.environ.get('ImageVersion'),'cases':input_rows,'source_sha256':{str((D/p).relative_to(R)):sha(D/p)for p in sources},'formula':'Exactly S88 independent HDR target and matrix6/10bit carrier; no retuning of display scale policy, masks, offset/range or quantization','ideal_headroom_target':'I(h)=(S+o)*exp2(log2(h)/3*log2((H+o)/(S+o)))-o, h in1,2,8; o is original full-precision common offset. H=S44/S47 independent intent. Compare to actual encoded native readback, not merely actual gain equation.','worst_RGB_point':'Full RGB maxrelative with original floor1e-6. Private exact coordinate/RGB/contributions; public threshold/sign classifications only.','display':{'config_sha256':config_sha,'view':'ACES1.0 SDR Video','source':'LinearP3-D65','display':'sRGB','exposure_EV':0},'holdout_scope':'IMG2608/0033 withheld from the encoded independent-HDR S88 integration math until this source freeze; previously used in old projection/display/stress studies, not never-seen or physical-scene holdouts. IMG0032 already integration development in S88.','archival':'Aggregate text plus encrypted contacts/witnesses only. S88 already retains one full carrier. No new full carriers or masters archived in S89; file hashes alone are not those files delivered.','public_text_max_bytes':1000000,'private_combined_cipher_max_bytes':1500000,'original_gates_or_masks_changed':False,'engineering_accepted':False,'A_phase_complete':False,'acceptance_complete':False}
save(O/'suite-freeze.json',freeze);frozen_sha=sha(O/'suite-freeze.json');assert subprocess.check_output(['sw_vers','-buildVersion'],text=True).strip()=='26A434'
node=next(n for n in ast.parse((D/'carrier_case_s87.py').read_text()).body if isinstance(n,ast.ClassDef)and n.name=='ErrorState')
results=[]
for case in input_rows:
 photo=case['photo'];cw=W/photo;cw.mkdir();co=cw/'out';cp=cw/'private';ce=cw/'encrypted'
 for p in [co,cp,ce,cw/'secure']:p.mkdir()
 actual=O/photo;actual.mkdir();secret=PRIVATE/photo;secret.mkdir();row={'photo':photo,'role':case['role'],'completed':False};results.append(row)
 try:
  assert shutil.disk_usage(W).free>6_000_000_000
  driver,helper,receipt=derive_case(case);save(actual/'input-bindings.json',receipt)
  # The exact executed generated source is harmless text and archived publicly.
  (actual/'derived-driver.txt').write_text(driver);(actual/'derived-rebuild.txt').write_text(helper)
  driver_path=cw/'driver.py';helper_path=cw/'rebuild.py';driver_path.write_text(driver);helper_path.write_text(helper)
  env=os.environ.copy();env.update(W=str(cw),HDR_S89_CASE_JSON=json.dumps(case),HDR_S89_REBUILD=str(helper_path))
  with(actual/'child.log').open('x')as log:process=subprocess.run([sys.executable,driver_path],env=env,stdout=log,stderr=subprocess.STDOUT,timeout=2400)
  row['child_returncode']=process.returncode
  for p in co.iterdir():
   if p.is_file():shutil.copyfile(p,actual/p.name)
  assert process.returncode==0,'Child failed: inspect original child.log and copied checkpoints'
  analysis=json.loads((co/'analysis.json').read_text());native=json.loads((co/'native.json').read_text());source=R/case['source_path'];raw=parse_heif(source.read_bytes());primary=raw['items'][str(raw['primary_item_id'])];turn=primary.get('irot',{}).get('angle_ccw_degrees',0)//90
  h,w=case['shape'][:2];height,width=analysis['shape'][:2];folder=cw/'case';sraw=np.memmap(folder/'original-sdr.f32',mode='r',dtype='<f4',shape=(h,w,4));t=np.memmap(folder/'HDR.f32',mode='r',dtype='<f4',shape=(h,w,3));sr=np.rot90(sraw[...,:3],k=turn);hr=np.rot90(t,k=turn);assert sr.shape==(height,width,3)
  original_off=json.loads((co/'analysis-s47.json').read_text())['common_offset'];lo,hi=analysis['metadata_values'][2:4];encoded_off=analysis['metadata_values'][5]
  read=lambda spec:np.memmap(folder/'native'/spec['file'],mode='r',dtype='<f4',shape=(height,width,4))
  heads={r['headroom']:read(r)for r in native['headrooms']};ah=read(native['files']['HDR']);gain=read(native['files']['gain']);lgr=np.rot90(np.memmap(folder/'integration-log.f32',mode='r',dtype='<f4',shape=(h,w,3)),k=turn);codes=np.rot90(np.memmap(folder/'codes.u16',mode='r',dtype='<u2',shape=(h,w,3)),k=turn)
  before={f:sha(folder/f)for f in ['master.exr','master.f16','original-sdr.f32','HDR.f32']};namespace={'np':np,'math':math,'Y':Y,'PRIVATE':secret,'save':save};exec(compile(ast.Module(body=[node],type_ignores=[]),'S87-original-ErrorState','exec'),namespace);states={head:namespace['ErrorState'](folder,'ideal-headroom'+str(head))for head in heads};worst=None;worst_public=None
  for top in range(0,height,ROWS):
   stop=min(height,top+ROWS);s=sr[top:stop].astype('f8');H=hr[top:stop].astype('f8');ratio=(H+original_off)/(s+original_off);assert np.isfinite(ratio).all()and(ratio>0).all();log=np.log2(ratio)
   for head,arr in heads.items():ideal=(s+original_off)*np.exp2(math.log2(head)/3*log)-original_off;states[head].add(arr[top:stop,:,:3],ideal)
   a=ah[top:stop,:,:3].astype('f8');relative=abs(a-H)/np.maximum(abs(H),1e-6);value=float(relative.max())
   if worst is None or value>worst['max_relative_floor1e6']:
    iy,ix,ch=np.unravel_index(int(np.argmax(relative)),relative.shape);b=H[iy,ix];base=s[iy,ix];l=lgr[top+iy,ix].astype('f8');q=(codes[top+iy,ix]>>6).astype('f8')/1023;g=gain[top+iy,ix,:3].astype('f8');f32=(base+original_off)*np.exp2(l)-original_off;rounded=(base+encoded_off)*np.exp2(l)-encoded_off;quant=(base+encoded_off)*np.exp2(lo+(hi-lo)*q)-encoded_off
    worst={'storage_y':top+int(iy),'x':int(ix),'channel':int(ch),'reference_RGB':b.tolist(),'actual_RGB':a[iy,ix].tolist(),'max_relative_floor1e6':value,'component_error_contributions':{'log_f32':float(f32[ch]-b[ch]),'offset_rational':float(rounded[ch]-f32[ch]),'actual_quantization':float(quant[ch]-rounded[ch]),'codec_provider':float(a[iy,ix,ch]-quant[ch])}}
    worst_public={'max_relative_floor1e6':value,'reference_component_abs_le_1e6':bool(abs(b[ch])<=1e-6),'reference_component_abs_le_1e4':bool(abs(b[ch])<=1e-4),'reference_luma_le_1e4':bool(b@Y<=1e-4),'reference_component_negative':bool(b[ch]<0),'actual_component_negative':bool(a[iy,ix,ch]<0),'absolute_component_error':float(abs(a[iy,ix,ch]-b[ch])),'private_only':'Exact coordinate/RGB and individual error contributions are encrypted'}
  row['ideal_headroom_metrics']={str(k):v.finish()for k,v in states.items()};save(secret/'max-RGB-relative-witness.json',worst);row['max_RGB_relative_diagnostic']=worst_public;assert worst['max_relative_floor1e6']==analysis['metrics']['encoded_HDR_vs_target']['max_relative_floor_1e6']
  ys=np.floor((np.arange(120)+.5)*height/120).astype(int);xs=np.floor((np.arange(160)+.5)*width/160).astype(int);ss=sr[ys[:,None],xs[None,:]].astype('f8');hh=hr[ys[:,None],xs[None,:]].astype('f8');log=np.log2((hh+original_off)/(ss+original_off));sheet=Image.new('RGB',(480,288),'white');draw=ImageDraw.Draw(sheet);checks=[]
  for col,head in enumerate([1,2,8]):
   ideal=(ss+original_off)*np.exp2(math.log2(head)/3*log)-original_off;observed=np.array(heads[head][ys[:,None],xs[None,:],:3],copy=True)
   for row_index,label,v in [(0,'ideal h'+str(head),ideal),(1,'native h'+str(head),observed)]:
    before_sample=hashlib.sha256(v.tobytes()).hexdigest();x=np.array(v,'f4',copy=True);cpu.apply(ocio.PackedImageDesc(x,160,120,3));image=Image.fromarray(np.rint(np.clip(x,0,1)*255).astype('u1'));sheet.paste(image,(col*160,row_index*144));draw.text((col*160+2,row_index*144+123),label,fill='black');after_sample=hashlib.sha256(v.tobytes()).hexdigest();assert before_sample==after_sample;checks.append({'label':label,'before':before_sample,'after':after_sample})
  sheet.save(secret/'ideal-native-headrooms.png');assert before=={f:sha(folder/f)for f in before};assert sha(source)==case['source_sha256'];row.update(preview_checks=checks,source_SHA_before_after=before,SDR_max0=native['ImageIO_full_SDR']['decoded_sdr_max0_verified'],original_S88_metrics=analysis['metrics'],actual_master_matches_old_EXR=json.loads((co/'rebuild-rebuild-result.json').read_text())['EXR_matches_old_archive_member'],completed=True)
  shutil.copyfile(ce/'contacts.tar.gz.gpg',ENC/(photo+'-contacts.tar.gz.gpg'))
 except Exception as error:
  row['failure_type']=type(error).__name__;row['failure']=str(error)
 finally:
  save(actual/'additional-analysis.json',row);assert sha(O/'suite-freeze.json')==frozen_sha
  # Children have exited. Remove only the newly created suite case directory.
  for checkpoint in co.iterdir():
   if checkpoint.is_file()and not(actual/checkpoint.name).exists():shutil.copyfile(checkpoint,actual/checkpoint.name)
  for name in ['sraw','t','sr','hr','heads','ah','gain','lgr','codes','states','arr']:
   globals().pop(name,None)
  assert cw.parent==W and cw.name==photo;shutil.rmtree(cw)
 if not row['completed']:break
save(O/'analysis.json',{'os_build':'26A434','image_version':os.environ.get('ImageVersion'),'source_commit':os.environ['GITHUB_SHA'],'rows':results,'all_completed':len(results)==5 and all(r['completed']for r in results),'completed_photos':sum(r['completed']for r in results),'completed_recipe_holdouts':sum(r['completed']and r['role']=='encoded-integration-holdout'for r in results),'scope':freeze['archival'],'engineering_accepted':False,'A_phase_complete':False,'acceptance_complete':False})
save(PRIVATE/'manifest.json',{'run_id':os.environ['GITHUB_RUN_ID'],'commit':os.environ['GITHUB_SHA'],'os_build':'26A434','people_results_encrypted':True,'files':[{'path':str(p.relative_to(PRIVATE)),'size':p.stat().st_size,'sha256':sha(p)}for p in sorted(PRIVATE.rglob('*'))if p.is_file()]})
with tarfile.open(W/'additional.tar.gz','w:gz')as tar:tar.add(PRIVATE,arcname='out')
with(O/'additional-encrypt.log').open('x')as log:subprocess.run(['gpg','--batch','--trust-model','always','--recipient','28E62F64A29764C2F2AEBF5D5B6B1C101E5F5ABA','--encrypt','--output',ENC/'additional.tar.gz.gpg',W/'additional.tar.gz'],stdout=log,stderr=subprocess.STDOUT,check=True)
save(O/'encrypted-inventory.json',{'files':[{'file':p.name,'size':p.stat().st_size,'sha256':sha(p)}for p in sorted(ENC.glob('*.gpg'))],'full_new_carrier_master_archived':False,'plaintext_uploaded':False});assert sum(p.stat().st_size for p in ENC.glob('*.gpg'))<1500000
assert sha(O/'suite-freeze.json')==frozen_sha
print(json.dumps({'completed_photos':sum(r['completed']for r in results),'A_phase_complete':False}));sys.exit(0 if len(results)==5 and all(r['completed']for r in results)else 1)
