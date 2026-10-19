"""Runner-only original consumer LTM-control retargeting. Encrypted outputs."""
from pathlib import Path
import os,sys,hashlib,json,subprocess,zipfile,shutil,tarfile
W=Path(os.environ['W']);O=W/'out';O.mkdir(exist_ok=True);R=Path.cwd();SRC=R/'research/semantic-styles';status=[]
def run(args,label,timeout=300):
 with (O/(label+'.log')).open('w') as log:rc=subprocess.run(list(map(str,args)),stdout=log,stderr=subprocess.STDOUT,timeout=timeout).returncode
 status.append({'operation':label,'returncode':rc});(O/'status.json').write_text(json.dumps(status,indent=2)+'\n');assert rc==0,label
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
text=(SRC/'semantic_consumer_s5.m').read_text();a=text.index('static void Probe(');b=text.index('static int Process(',a);text=text[:a]+'#include "tone_retarget_s27.inc"\n'+text[b:];source=GEN/'tone_retarget_s27.m';source.write_text(text)
old=R/'research/vm-native/runner';exe=W/'tone-s27';flags=['clang','-fobjc-arc','-O2','-I'+str(old),'-I'+str(GEN),'-I'+str(SRC),'-framework','Foundation','-framework','CoreImage','-framework','CoreMedia','-framework','ImageIO','-framework','Metal','-framework','CoreGraphics','-Wl,-undefined,dynamic_lookup']
run(flags+[source,'-o',exe],'build-s27')
os.environ.update({'XD_TONE_MAX_EDGE':'512','XD_TONE_THUMB_MODE':'native-stage-mirror','XD_TONE_BIAS':'0.35','S27_PRIOR':str(W/'s5/out')})
case=W/'probe/consumer';case.parent.mkdir();run(['xcrun','lldb','--batch','-o','run','-k','thread backtrace all','--',exe,photo,res,case],'native-s27',1200)
native=case/'semantic';assert (native/'s27-results.json').exists(),'No validated S27 capture'
(O/'native').mkdir()
for p in native.iterdir():
 if p.name.startswith(('s27-','original-params')) or p.name in ['reference.f16','source.f16'] or any(p.name.startswith(n) for n in ['local-neutral','local-half-neutral','background-local-neutral','person-local-neutral','gtc-weight-only-reset','semantic-tone-reset','ui-tone-reset','opposite-ui-tone','naive-negative-after-positive']):
  shutil.copyfile(p,O/'native'/p.name)
for n in ['renderer.f32','primary_input.f32']:shutil.copyfile(case/n,O/n)
run([sys.executable,SRC/'analyze_tone_s27.py',O,W/'s5/out/consumer-toneP035/semantic'],'analyze-s27',600)
(O/'source-sha256.json').write_text(json.dumps({str(p.relative_to(R)) if p.is_relative_to(R) else p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [source,SRC/'semantic_consumer_s5.m',SRC/'tone_retarget_s27.inc',SRC/'analyze_tone_s27.py',SRC/'plot_brightening_s27.py',SRC/'semantic_curve_inverse.py']},indent=2)+'\n')
print('S27 finished. Original files/frozen models unchanged; only encrypted native outputs and synthetic plot are archived.')
