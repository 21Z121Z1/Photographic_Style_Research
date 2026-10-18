"""Reuse S5 captures. Correct display mutation and test one native texture stage."""
from pathlib import Path
import os,sys,json,zipfile,hashlib,subprocess,tarfile,shutil
R=Path.cwd();W=Path(os.environ['W']);O=W/'out';O.mkdir(exist_ok=True);SRC=R/'research/semantic-styles';prior=W/'prior';prior.mkdir();status=[]
def run(args,name,env=None,timeout=300):
 with (O/(name+'.log')).open('w') as log:
  try:rc=subprocess.run(list(map(str,args)),stdout=log,stderr=subprocess.STDOUT,env=dict(os.environ,**(env or{})),timeout=timeout).returncode
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
for r in manifest['files']:
 f=prior/'out'/r['path']
 with f.open('rb') as h:d=hashlib.file_digest(h,'sha256').hexdigest()
 if d!=r['sha256'] or f.stat().st_size!=r['size']:fail.append(r['path'])
assert not fail
(O/'prior-verification.json').write_text(json.dumps({'run_id':39139035394,'zip_sha256':'55f845778415b22276bc92e166416e60a29df6ce559df8f3fd71f6f5911d12fc','manifest_failures':fail,'files':len(manifest['files']),'private_archive_key_uploaded':False},indent=2)+'\n')
work=W/'recomputed';shutil.copytree(prior/'out',work)
assert run([sys.executable,SRC/'analyze_semantic_s5.py',work],'recompute',{'SEMANTIC_REUSE_NUMERIC_ANALYSIS':'1'})==0
# No native consumer or continuous inverse is re-executed. Only affected
# analysis/previews are recalculated from immutable, verified S5 captures.
for name in ['analysis-s5.json','preview-integrity.json']:shutil.copy2(work/name,O/name)
est=O/'directional-estimates';est.mkdir();shutil.copy2(work/'directional-estimates/estimates.json',est/'estimates.json')
from PIL import Image
def small(source,dest):
 im=Image.open(source);im.thumbnail((256,256));im.save(dest)
for name in ['reference','face-only-budget1','body-only-budget1']:small(work/'directional-estimates'/(name+'-ACES.png'),est/(name+'-ACES.png'))
import numpy as np
for op in ['face-only','body-only']:
 p=work/'directional-estimates'/(op+'-budget1.npz')
 with np.load(p) as z:np.savez_compressed(est/(op+'-gain.npz'),log2_gain=z['log2_gain'],mask=z['mask'])
skin=O/'skin-controls';skin.mkdir()
for name in ['reference','skin-color-oracle','skin-brightness-oracle','skin-both-oracle']:small(work/'consumer-toneP035'/(name+'-ACES.png'),skin/(name+'-ACES.png'))
# Extract actual matte images to temporary runner storage for a new direct
# native UnderEye FinalMix test, separate from the skipped complete pipeline.
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
exe=W/'under-eye-final';flags=['clang','-fobjc-arc','-O2','-framework','Foundation','-framework','Metal','-framework','CoreImage','-framework','ImageIO']
if run(flags+[SRC/'under_eye_final_s6.m','-o',exe],'build-under-eye')==0:
 raw=W/'under-eye-raw'
 if run([exe,work/'consumer-tone0/primary_input.f32',res,raw,photo],'under-eye-native')==0:
  ue=O/'under-eye';ue.mkdir()
  run([sys.executable,SRC/'analyze_under_eye_s6.py',raw,ue,exe,res,photo],'under-eye-analysis')
  for name in ['native.json','imageio-properties.json']:
   if (raw/name).exists():shutil.copy2(raw/name,ue/name)
  # Full temporary pixel buffers stay on this runner; record their SHA/shape
  # and archive reproducible code plus small calibrated previews/metrics.
  hashes=[]
  for p in raw.rglob('*'):
   if p.is_file():
    with p.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
    hashes.append({'file':p.name,'bytes':p.stat().st_size,'sha256':digest})
  (ue/'raw-sha256.json').write_text(json.dumps(hashes,indent=2)+'\n')
  (ue/'candidate.f32').unlink(missing_ok=True)
run([sys.executable,SRC/'producer_j_cap_s6.py',SRC/'evidence/producer-j-cap-input.json',O/'producer-j-cap-results.json'],'producer-j-cap')
# Upper limit on the new downloadable archive prevents another large result.
total=sum(p.stat().st_size for p in O.rglob('*') if p.is_file());assert total<1_500_000,total
print('S6 derived evidence and new native stage finished; encrypted output only.')
