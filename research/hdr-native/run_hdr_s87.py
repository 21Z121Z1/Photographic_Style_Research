"""Sequential full-resolution carrier checks; no ISP/scene inverse claim."""
from pathlib import Path
import os,json,subprocess,hashlib,shutil,tarfile,sys
from PIL import Image,ImageDraw
R=Path.cwd();D=R/'research/hdr-native';W=Path(os.environ['W']);O=W/'out';PRIVATE=W/'private';ENC=W/'encrypted'
PHOTOS=[('IMG_2600','development','research/vm-native/samples/IMG_2600.HEIC','63872222783e757a41a41337b48875e1172e68ace0f6e411db999c77b027a4d0'),('IMG_2604','development','research/vm-native/samples/IMG_2604.HEIC','71d67c74fea30d1ae8e2b355ef695241d3682e80295bfa46820f7d9e1f399c4e'),('IMG_2608','development','research/vm-native/samples/IMG_2608.HEIC','8039573c1da8f235eb73748c13c5b4aee43af08d159814f8026280c4b417ad2a'),('IMG_0032','recipe-holdout','Apple_Native_Samples/IMG_0032.HEIC','76a2fa2723e5a2419b3752042dda7675077451d957594f6d497f0e613ef6501a'),('IMG_0033','recipe-holdout','Apple_Native_Samples/IMG_0033.HEIC','c2f18ab9b1349377d2e23aaa7610bb5115f28f95c4d88ce6a789d6550e1213a0')]
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,obj):
 with Path(p).open('x')as f:json.dump(obj,f,indent=2,allow_nan=False);f.write('\n')
sources=[D/n for n in ['run_hdr_s87.py','carrier_case_s87.py','carrier_readback_s87.m','read_sdr_s87.m','hdr_headroom_s29.m','iso_splice.py']]+[R/'tools/heif_dump.py']
freeze={'os_build':'26A434','image_version':os.environ.get('ImageVersion'),'source_sha256':{str(p.relative_to(R)):sha(p)for p in sources},'photos':PHOTOS,'formula':'Original S31 EV=[3u,-.5+2v,2(1-u)], evaluated on explicitly oriented native source; H=float32(S*2**EV). No fit from expected/native output.','codec':'matrix6,10-bit,4:4:4,lossless HEVC; actual colr asserted in each case.','orientation':'Native applyOrientation YES for source, base, gain, HDR; inverse primary irot_ccw before new gain encoding. Original primary coded bytes/properties retained. No alternate flip or resize chosen.','maximum_EV_audit':'Public near-zero/signed-cancellation categories; exact coordinates and RGB in encrypted private witnesses only.','new_legacy_gate_or_mask':False,'scope':'Transport on five original photographs, not global/local/semantic, original camera, RAW or artistic HDR quality validation.','holdout_limit':'0032/0033 held out for this oriented carrier recipe; seen in older research.','all_processing_sequential':True,'full_carriers_or_pixel_arrays_uploaded':False,'JPEG_contact_quality':85,'private_cipher_max_bytes':160000,'public_payload_max_bytes':90000,'public_JSON_copy':'Compact JSON with identical parsed values; original child JSON hash/size recorded per case before this run scratch cleanup.','engineering_accepted':False,'A_phase_complete':False,'acceptance_complete':False}
save(O/'freeze.json',freeze);frozen_sha=sha(O/'freeze.json');results=[];contacts=[]
selected=['analysis.json','bit10-native.json','layout.json','freeze.json','source-facts.json']
for name,role,relative,expected in PHOTOS:
 assert sha(R/relative)==expected and shutil.disk_usage(W).free>5_000_000_000
 c=W/('case-'+name);c.mkdir()
 for part in ['out','private','encrypted']:(c/part).mkdir()
 env=dict(os.environ,W=str(c),S87_SOURCE=relative,S87_SOURCE_SHA=expected)
 with(c/'child.log').open('x')as log:p=subprocess.run([sys.executable,str(D/'carrier_case_s87.py')],env=env,stdout=log,stderr=subprocess.STDOUT,timeout=2000)
 row={'photo':name,'role':role,'returncode':p.returncode,'source_SHA256_before_after':expected,'source_SHA_unchanged':sha(R/relative)==expected}
 assert row['source_SHA_unchanged']
 row['child_original_JSON_receipts']={}
 for f in selected:
  src=c/'out'/f
  if src.exists():
   assert src.stat().st_size<50000
   raw=src.read_bytes();value=json.loads(raw);compact=(json.dumps(value,separators=(',',':'),allow_nan=False)+'\n').encode();assert json.loads(compact)==value
   row['child_original_JSON_receipts'][f]={'size':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'compact_copy_preserves_parsed_values':True}
   with(O/(name+'-'+f)).open('xb')as target:target.write(compact)
 a=c/'out/analysis.json'
 if a.exists():
  report=json.loads(a.read_text());row.update({'shape':report['shape'],'all_completed':report['all_completed'],'preview_input_checks_unchanged':all(v['before_sha256']==v['after_sha256']for v in report['preview_input_checks']),'layout_qualified':report['layout_qualification']['layout_qualified']})
 else:row['all_completed']=False
 if p.returncode:
  raw=(c/'child.log').read_bytes();assert len(raw)<50000
  with(O/(name+'-failure.log')).open('xb')as f:f.write(raw)
 for src in(c/'private').glob('*-worst.json'):
  with(PRIVATE/(name+'-'+src.name)).open('xb')as target:target.write(src.read_bytes())
 contact=c/'private/carrier-transport-contact.png'
 if contact.exists():
  with Image.open(contact)as im:contacts.append((name,im.convert('RGB').copy()))
 results.append(row);shutil.rmtree(c)
 assert sha(O/'freeze.json')==frozen_sha and all(sha(p)==freeze['source_sha256'][str(p.relative_to(R))]for p in sources)
save(O/'analysis.json',{'os_build':'26A434','image_version':os.environ.get('ImageVersion'),'freeze_sha256':frozen_sha,'rows':results,'real_photos_completed':sum(r['returncode']==0 and r['all_completed']for r in results),'recipe_holdouts_completed':sum(r['role']=='recipe-holdout'and r['returncode']==0 and r['all_completed']for r in results),'full_resolution':True,'all_completed':all(r['returncode']==0 and r['all_completed']for r in results),'all_processing_sequential':True,'original_primary_coded_or_models_modified':False,'original_styles_global_local_semantic_or_scene_verified':False,'headrooms':[1,2,8],'new_input_secret_release':False,'full_carriers_retained':False,'engineering_accepted':False,'A_phase_complete':False,'acceptance_complete':False})
if contacts:
 sheet=Image.new('RGB',(256,266*len(contacts)),'white');draw=ImageDraw.Draw(sheet)
 for index,(name,im)in enumerate(contacts):draw.text((3,index*266+3),name,fill='black');sheet.paste(im,(0,index*266+22))
 sheet.save(PRIVATE/'carrier-five-contact.jpg',quality=85,optimize=True,subsampling=0)
 save(PRIVATE/'meaning.json',{'display':'Same fixed OCIO ACES1.0 SDR Video / LinearP3-D65 /0EV as S82,S85,S86','layout':'Each photo: original SDR, defined RGB stress target; native10-bit, blank. All explicitly oriented.','scope':'Transport stress diagnostic only, not proposed HDR look or scene recovery.','worst_point_files':'Encrypted exact stored processing coordinates and actual/reference RGB; aggregate sign/cancellation categories are public.'})
save(PRIVATE/'manifest.json',{'run_id':os.environ['GITHUB_RUN_ID'],'commit':os.environ['GITHUB_SHA'],'os_build':'26A434','people_results_encrypted':True,'files':[{'path':p.name,'size':p.stat().st_size,'sha256':sha(p)}for p in sorted(PRIVATE.iterdir())if p.is_file()]})
with tarfile.open(W/'previews.tar.gz','w:gz')as tar:tar.add(PRIVATE,arcname='out')
with(O/'preview-encrypt.log').open('x')as log:subprocess.run(['gpg','--batch','--trust-model','always','--recipient','28E62F64A29764C2F2AEBF5D5B6B1C101E5F5ABA','--encrypt','--output',str(ENC/'previews.tar.gz.gpg'),str(W/'previews.tar.gz')],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
cipher=ENC/'previews.tar.gz.gpg';assert cipher.stat().st_size<160000
save(O/'encrypted-inventory.json',{'file':cipher.name,'size':cipher.stat().st_size,'sha256':sha(cipher),'plaintext_uploaded':False,'private_payload':'One JPEG contact plus exact worst-point JSON witnesses, no full carrier/EXR or pixel arrays'})
assert sum(p.stat().st_size for p in O.iterdir()if p.is_file())<90000
if not all(r['returncode']==0 and r['all_completed']for r in results):raise RuntimeError('One or more declared photo cases failed; preserve evidence, no adaptive retry')
print(json.dumps({'completed_photos':len(results),'recipe_holdouts':2,'full_carriers_uploaded':False,'engineering_accepted':False}))
