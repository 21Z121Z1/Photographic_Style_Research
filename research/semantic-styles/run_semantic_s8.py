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
# Acquire the same dispatch once to retain the installed Apple pipeline.
# All input texture/buffer/ROI hashes must match the immutable S5 capture.
sys.path.insert(0,str(R));sys.path.insert(0,str(R/'research/vm-native'))
from extract_inputs import extract
from tools.heif_dump import parse_heif
from heif_standalone import standalone
photo=W/'IMG_2810.HEIC';res=W/'res';extract(photo,res);data=photo.read_bytes();h=parse_heif(data)
choices={'inputSubjectMatteImage':'semanticpersonmatte','inputSkinMatteImage':'semanticskinmatte','inputSkyMatteImage':'semanticskymatte','inputGainMapImage':'hdrgainmap'}
for target,suffix in choices.items():
 matches=[i for i in h['items'].values() if i.get('aux_type','').endswith(suffix)]
 if matches:(res/(target+'.heic')).write_bytes(standalone(data,matches[0]['item_id']))
GEN=W/'generated';GEN.mkdir();assert run([sys.executable,SRC/'generate_semantic_s5.py',GEN],'generate-base')==0
assert run([sys.executable,SRC/'generate_semantic_s8.py',GEN],'generate-s8')==0
OLD=R/'research/vm-native/runner';exe=W/'semantic-s8';flags=['clang','-fobjc-arc','-O2','-I'+str(OLD),'-I'+str(GEN),'-I'+str(SRC),'-framework','Foundation','-framework','CoreImage','-framework','CoreMedia','-framework','ImageIO','-framework','Metal','-framework','CoreGraphics','-Wl,-undefined,dynamic_lookup']
if run(flags+[GEN/'semantic_consumer_s8.m','-o',exe],'build-s8')==0:
 parent=W/'probe';parent.mkdir();case=parent/'consumer'
 os.environ.update({'XD_TONE_MAX_EDGE':'512','XD_TONE_THUMB_MODE':'native-stage-mirror','XD_TONE_BIAS':'0.35','S8_PRIOR':str(prior/'out/consumer-toneP035/semantic')})
 run(['xcrun','lldb','--batch','-o','run','-k','thread backtrace all','--',exe,photo,res,case],'native-s8',900)
 native=case/'semantic'
 if native.exists():
  shutil.copytree(native,O/'native')
 if (native/'s8-results.json').exists():run([sys.executable,SRC/'analyze_semantic_s8.py',native,prior/'out/consumer-toneP035/semantic',O/'analysis'],'analysis-s8',600)
for name in ['generated-sha256.json','generated-source-sha256.json']:
 if (GEN/name).exists():shutil.copy2(GEN/name,O/name)
print('S8 native inverse diagnostics complete. Private outputs encrypted by workflow.')
