"""Runner-only full-frame native witnesses, never upload private plaintext."""
from pathlib import Path
import os,sys,hashlib,json,subprocess,zipfile,shutil,tarfile
W=Path(os.environ['W']);O=W/'out';O.mkdir(exist_ok=True);R=Path.cwd();SRC=R/'research/semantic-styles';status=[]
def run(args,label,timeout=300):
 with (O/(label+'.log')).open('w') as log:rc=subprocess.run(list(map(str,args)),stdout=log,stderr=subprocess.STDOUT,timeout=timeout).returncode
 status.append({'operation':label,'returncode':rc});(O/'status.json').write_text(json.dumps(status,indent=2)+'\n');assert rc==0,label
assert subprocess.check_output(['sw_vers','-buildVersion'],text=True).strip()=='26A434'
verified=[]
for label,artifact,want,env in [
 ('s5',12140624073,'55f845778415b22276bc92e166416e60a29df6ce559df8f3fd71f6f5911d12fc','S5_ARCHIVE_SESSION'),
 ('s17',12149258316,'ce03b63fa5d35757f228d95d71fd6b13e8592d0d472eb9add70f9389df002c47','S17_ARCHIVE_SESSION')]:
 p=W/(label+'.zip')
 with p.open('wb') as f:subprocess.run(['gh','api',f'repos/21Z121Z1/Photographic_Style_Research/actions/artifacts/{artifact}/zip'],stdout=f,check=True)
 with p.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==want
 with zipfile.ZipFile(p) as z:
  name=next(n for n in z.namelist() if n.endswith('.gpg'))
  with z.open(name) as a,(W/(label+'.gpg')).open('wb') as b:shutil.copyfileobj(a,b)
 key=W/(label+'-key');key.write_text(os.environ[env]+'\n');key.chmod(0o600)
 with key.open('rb') as f,(O/(label+'-decrypt.log')).open('w') as log:subprocess.run(['gpg','--batch','--override-session-key-fd',str(f.fileno()),'--output',str(W/(label+'.tar.gz')),'--decrypt',str(W/(label+'.gpg'))],pass_fds=(f.fileno(),),stdout=log,stderr=subprocess.STDOUT,check=True)
 key.unlink();dest=W/label;dest.mkdir()
 with tarfile.open(W/(label+'.tar.gz')) as t:t.extractall(dest,filter='data')
 manifest=json.loads((dest/'out/manifest.json').read_text())
 for row in manifest['files']:
  p=dest/'out'/row['path']
  with p.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==row['sha256']
  assert p.stat().st_size==row['size']
 verified.append({'source_artifact':artifact,'zip_sha256':want,'files':len(manifest['files']),'failures':0})
(O/'prior-verification.json').write_text(json.dumps(verified,indent=2)+'\n')
photo=W/'IMG_2810.HEIC';assert hashlib.sha256(photo.read_bytes()).hexdigest()=='52ea41f0dd16590cef83abfd8093ccf8082994113e0c2cee86f90c42f7ab21c2'
sys.path.insert(0,str(R));sys.path.insert(0,str(R/'research/vm-native'))
from extract_inputs import extract
from tools.heif_dump import parse_heif
from heif_standalone import standalone
res=W/'res';extract(photo,res);data=photo.read_bytes();heif=parse_heif(data)
for target,suffix in {'inputSubjectMatteImage':'semanticpersonmatte','inputSkinMatteImage':'semanticskinmatte','inputSkyMatteImage':'semanticskymatte','inputGainMapImage':'hdrgainmap'}.items():
 matches=[i for i in heif['items'].values() if i.get('aux_type','').endswith(suffix)]
 if matches:(res/(target+'.heic')).write_bytes(standalone(data,matches[0]['item_id']))
GEN=W/'generated';GEN.mkdir();run([sys.executable,SRC/'generate_semantic_s5.py',GEN],'generate-base')
text=(SRC/'semantic_consumer_s5.m').read_text();a=text.index('static void Probe(');b=text.index('static int Process(',a);text=text[:a]+'#include "semantic_s20.inc"\n'+text[b:];source=GEN/'semantic_consumer_s20.m';source.write_text(text)
old=R/'research/vm-native/runner';exe=W/'semantic-s20';flags=['clang','-fobjc-arc','-O2','-I'+str(old),'-I'+str(GEN),'-I'+str(SRC),'-framework','Foundation','-framework','CoreImage','-framework','CoreMedia','-framework','ImageIO','-framework','Metal','-framework','CoreGraphics','-Wl,-undefined,dynamic_lookup']
run(flags+[source,'-o',exe],'build-s20')
P=W/'s5/out/consumer-toneP035/semantic';witness=W/'s17/out/diagnostics/all-impossibility-witnesses.private.json'
os.environ.update({'XD_TONE_MAX_EDGE':'512','XD_TONE_THUMB_MODE':'native-stage-mirror','XD_TONE_BIAS':'0.35','S20_PRIOR':str(P),'S20_WITNESSES':str(witness)})
case=W/'probe/consumer';case.parent.mkdir();run(['xcrun','lldb','--batch','-o','run','-k','thread backtrace all','--',exe,photo,res,case],'native-s20',1200)
native=case/'semantic';assert (native/'s20-results.json').exists(),'No validated native witness replay'
shutil.copytree(native,O/'native');run([sys.executable,SRC/'analyze_semantic_s20.py',O/'native',witness,O/'analysis'],'exact-rational-audit')
(O/'generated-source-sha256.json').write_text(json.dumps({'source':hashlib.sha256((SRC/'semantic_consumer_s5.m').read_bytes()).hexdigest(),'generated':hashlib.sha256(source.read_bytes()).hexdigest(),'probe':hashlib.sha256((SRC/'semantic_s20.inc').read_bytes()).hexdigest()},indent=2)+'\n')
print('S20 full-frame witnesses and rational certificates finished; all results encrypted.')
