"""Diagnose S5 and test residual-corrected semantic removal, without retuning."""
from pathlib import Path
import os,sys,json,zipfile,hashlib,subprocess,tarfile,shutil
R=Path.cwd();W=Path(os.environ['W']);O=W/'out';O.mkdir(exist_ok=True);SRC=R/'research/semantic-styles';prior=W/'prior';prior.mkdir();status=[]
def run(args,name,timeout=300):
 with (O/(name+'.log')).open('w') as log:
  try:rc=subprocess.run(list(map(str,args)),stdout=log,stderr=subprocess.STDOUT,timeout=timeout).returncode
  except subprocess.TimeoutExpired:rc='timeout'
 status.append({'operation':name,'returncode':rc});(O/'status.json').write_text(json.dumps(status,indent=2)+'\n');return rc
assert subprocess.check_output(['sw_vers','-buildVersion'],text=True).strip()=='26A434'
p=W/'s5.zip'
with p.open('wb') as f:subprocess.run(['gh','api','repos/21Z121Z1/Photographic_Style_Research/actions/artifacts/12140624073/zip'],stdout=f,check=True)
with p.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()=='55f845778415b22276bc92e166416e60a29df6ce559df8f3fd71f6f5911d12fc'
with zipfile.ZipFile(p) as z:
 n=next(n for n in z.namelist() if n.endswith('.gpg'))
 with z.open(n) as f,(W/'s5.gpg').open('wb') as g:shutil.copyfileobj(f,g,1048576)
with (W/'prior-session-key').open('w') as f:f.write(os.environ['S5_ARCHIVE_SESSION']+'\n')
os.chmod(W/'prior-session-key',0o600)
with (W/'prior-session-key').open('rb') as key,(O/'prior-decrypt.log').open('w') as log:
 subprocess.run(['gpg','--batch','--override-session-key-fd',str(key.fileno()),'--output',str(W/'prior.tar.gz'),'--decrypt',str(W/'s5.gpg')],pass_fds=(key.fileno(),),stdout=log,stderr=subprocess.STDOUT,check=True)
(W/'prior-session-key').unlink()
with tarfile.open(W/'prior.tar.gz') as t:t.extractall(prior,filter='data')
manifest=json.loads((prior/'out/manifest.json').read_text());fail=[]
for row in manifest['files']:
 f=prior/'out'/row['path']
 with f.open('rb') as h:d=hashlib.file_digest(h,'sha256').hexdigest()
 if d!=row['sha256'] or f.stat().st_size!=row['size']:fail.append(row['path'])
assert not fail
(O/'prior-verification.json').write_text(json.dumps({'source_run':39139035394,'files':len(manifest['files']),'manifest_failures':fail,'archive_sha256':'55f845778415b22276bc92e166416e60a29df6ce559df8f3fd71f6f5911d12fc'},indent=2)+'\n')
assert run([sys.executable,SRC/'residual_semantic_s7.py',prior/'out',O/'residual'],'residual-analysis',600)==0
# First native execution of this final blend. S6 failed only at linking, so
# add CoreGraphics; original Metal kernel/parameters are not changed.
sys.path.insert(0,str(R));sys.path.insert(0,str(R/'research/vm-native'))
from extract_inputs import extract
from tools.heif_dump import parse_heif
from heif_standalone import standalone
photo=W/'IMG_2810.HEIC';res=W/'res';extract(photo,res);data=photo.read_bytes();h=parse_heif(data)
names={'person':'personMatte','faceskin':'faceSkinMatte','lips':'lipsMatte','ears':'earsMatte','tattoo':'tattooMatte','glassesv2':'glassesMatteV2'}
for item in h['items'].values():
 aux=item.get('aux_type','')
 for key,target in names.items():
  if aux.endswith('semantic'+key+'matte') or (key.endswith('v2') and aux.endswith('semantic'+key[:-2]+'mattev2')):(res/(target+'.heic')).write_bytes(standalone(data,item['item_id']))
exe=W/'under-eye-final';flags=['clang','-fobjc-arc','-O2','-framework','Foundation','-framework','Metal','-framework','CoreImage','-framework','ImageIO','-framework','CoreGraphics']
if run(flags+[SRC/'under_eye_final_s6.m','-o',exe],'build-under-eye')==0:
 raw=W/'under-eye-raw';ue=O/'under-eye';ue.mkdir()
 run(['xcrun','lldb','--batch','-o','run','-k','thread backtrace all','--',exe,prior/'out/consumer-tone0/primary_input.f32',res,raw,photo],'under-eye-native')
 if (raw/'native.json').exists():
  run([sys.executable,SRC/'analyze_under_eye_s6.py',raw,ue,exe,res,photo],'under-eye-analysis')
  for name in ['native.json','imageio-properties.json']:
   if (raw/name).exists():shutil.copy2(raw/name,ue/name)
  hashes=[]
  for p in raw.rglob('*'):
   if p.is_file():
    with p.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
    hashes.append({'file':p.name,'bytes':p.stat().st_size,'sha256':digest})
  (ue/'raw-sha256.json').write_text(json.dumps(hashes,indent=2)+'\n')
  (ue/'candidate.f32').unlink(missing_ok=True)
 elif (raw/'native-error.json').exists():shutil.copy2(raw/'native-error.json',ue/'native-error.json')
 else:(ue/'missing-native-output.json').write_text(json.dumps({'status':'failed','reason':'No native.json; inspect LLDB inferior outcome and stack, not its process return code.'})+'\n')
print('S7 diagnostics and isolated native stage finished. Encrypted outputs only.')
