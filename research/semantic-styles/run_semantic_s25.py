"""Runner-only observational probe of the original retained PSO. Text outputs only."""
from pathlib import Path
import os,sys,hashlib,json,subprocess,zipfile,shutil,tarfile
W=Path(os.environ['W']);O=W/'out';O.mkdir(exist_ok=True);R=Path.cwd();SRC=R/'research/semantic-styles';status=[]
def run(args,label,timeout=300,required=True):
 with (O/(label+'.log')).open('w') as log:
  rc=subprocess.run(list(map(str,args)),stdout=log,stderr=subprocess.STDOUT,timeout=timeout).returncode
 status.append({'operation':label,'returncode':rc});(O/'status.json').write_text(json.dumps(status,indent=2)+'\n')
 if required:assert rc==0,label
 return rc
assert subprocess.check_output(['sw_vers','-buildVersion'],text=True).strip()=='26A434'
p=W/'s5.zip'
with p.open('wb') as f:subprocess.run(['gh','api','repos/21Z121Z1/Photographic_Style_Research/actions/artifacts/12140624073/zip'],stdout=f,check=True)
with p.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()=='55f845778415b22276bc92e166416e60a29df6ce559df8f3fd71f6f5911d12fc'
with zipfile.ZipFile(p) as z:
 name=next(n for n in z.namelist() if n.endswith('.gpg'))
 with z.open(name) as a,(W/'s5.gpg').open('wb') as b:shutil.copyfileobj(a,b)
key=W/'s5-key';key.write_text(os.environ['S5_ARCHIVE_SESSION']+'\n');key.chmod(0o600)
with key.open('rb') as f,(O/'s5-decrypt.log').open('w') as log:
 subprocess.run(['gpg','--batch','--override-session-key-fd',str(f.fileno()),'--output',str(W/'s5.tar.gz'),'--decrypt',str(W/'s5.gpg')],pass_fds=(f.fileno(),),stdout=log,stderr=subprocess.STDOUT,check=True)
key.unlink();dest=W/'s5';dest.mkdir()
with tarfile.open(W/'s5.tar.gz') as t:t.extractall(dest,filter='data')
manifest=json.loads((dest/'out/manifest.json').read_text())
for row in manifest['files']:
 p=dest/'out'/row['path']
 with p.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==row['sha256']
 assert p.stat().st_size==row['size']
(O/'prior-verification.json').write_text(json.dumps({'source_artifact':12140624073,'zip_sha256':'55f845778415b22276bc92e166416e60a29df6ce559df8f3fd71f6f5911d12fc','files':len(manifest['files']),'failures':0},indent=2)+'\n')
photo=W/'IMG_2810.HEIC'
with photo.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()=='52ea41f0dd16590cef83abfd8093ccf8082994113e0c2cee86f90c42f7ab21c2'
sys.path.insert(0,str(R));sys.path.insert(0,str(R/'research/vm-native'))
from extract_inputs import extract
from tools.heif_dump import parse_heif
from heif_standalone import standalone
res=W/'res';extract(photo,res);data=photo.read_bytes();heif=parse_heif(data)
for target,suffix in {'inputSubjectMatteImage':'semanticpersonmatte','inputSkinMatteImage':'semanticskinmatte','inputSkyMatteImage':'semanticskymatte','inputGainMapImage':'hdrgainmap'}.items():
 matches=[i for i in heif['items'].values() if i.get('aux_type','').endswith(suffix)]
 if matches:(res/(target+'.heic')).write_bytes(standalone(data,matches[0]['item_id']))
GEN=W/'generated';GEN.mkdir();run([sys.executable,SRC/'generate_semantic_s5.py',GEN],'generate-base')
text=(SRC/'semantic_consumer_s5.m').read_text();a=text.index('static void Probe(');b=text.index('static int Process(',a);text=text[:a]+'#include "pso_capture_s22.inc"\n#include "pso_original_variant_s25.inc"\n'+text[b:]
text=text.replace('ECInstall();m=class_getInstanceMethod','ECInstall();S22Install();S25Install();m=class_getInstanceMethod')
assert 'S22Install();' in text
source=GEN/'semantic_consumer_s25.m';source.write_text(text)
old=R/'research/vm-native/runner';exe=W/'semantic-s25';flags=['clang','-fobjc-arc','-O2','-I'+str(old),'-I'+str(GEN),'-I'+str(SRC),'-framework','Foundation','-framework','CoreImage','-framework','CoreMedia','-framework','ImageIO','-framework','Metal','-framework','CoreGraphics','-Wl,-undefined,dynamic_lookup']
run(flags+[source,'-o',exe],'build-s25')
os.environ.update({'XD_TONE_MAX_EDGE':'512','XD_TONE_THUMB_MODE':'native-stage-mirror','XD_TONE_BIAS':'0.35','S22_PRIOR':str(W/'s5/out/consumer-toneP035/semantic')})
case=W/'probe/consumer';case.parent.mkdir();run(['xcrun','lldb','--batch','-o','run','-k','thread backtrace all','--',exe,photo,res,case],'native-s25',1200)
native=case/'semantic';assert (native/'s22-results.json').exists(),'No validated original-PSO metadata'
(O/'native').mkdir()
for name in ['creation-events.json','s22-context.json','s22-results.json','exception.json','s25-original-variant.json']:
 p=native/name
 if p.exists():shutil.copyfile(p,O/'native'/name)
# The archive can contain Apple binary code. NEVER put it or a GPU capture in O.
run([sys.executable,SRC/'inspect_variant_s25.py',W/'backend',O/'variant-text'],'inspect-backend',600,required=False)
assert (native/'s25-original-variant.json').exists(),'No original initializer record'
(O/'generated-source-sha256.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [SRC/'semantic_consumer_s5.m',source,SRC/'pso_capture_s22.inc',SRC/'semantic_s22.inc',SRC/'pso_original_variant_s25.inc']},indent=2)+'\n')
print('S22 original PSO observation finished. Only whitelisted metadata/text is archived, encrypted.')
