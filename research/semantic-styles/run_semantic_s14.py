"""Private macOS-only finite-set audit of S8's remaining skin failures."""
from pathlib import Path
import os, sys, json, zipfile, hashlib, subprocess, tarfile, shutil
import numpy as np
R=Path.cwd(); W=Path(os.environ['W']); O=W/'out'; O.mkdir(exist_ok=True)
SRC=R/'research/semantic-styles'; status=[]
def run(args, name, timeout=300):
    with (O/(name+'.log')).open('w') as log:
        try: rc=subprocess.run(list(map(str,args)), stdout=log, stderr=subprocess.STDOUT, timeout=timeout).returncode
        except subprocess.TimeoutExpired: rc='timeout'
    status.append({'operation':name,'returncode':rc})
    (O/'status.json').write_text(json.dumps(status,indent=2)+'\n'); return rc
assert subprocess.check_output(['sw_vers','-buildVersion'],text=True).strip()=='26A434'
verified=[]
for label,artifact,sha,env in [
    ('s5',12140624073,'55f845778415b22276bc92e166416e60a29df6ce559df8f3fd71f6f5911d12fc','S5_ARCHIVE_SESSION'),
    ('s8',12146693880,'b48ae649e8c491474f8a34a3927b5d354e4920ead46c783794c8aaab8c8c4746','S8_ARCHIVE_SESSION')]:
    dest=W/label; dest.mkdir(); p=W/(label+'.zip')
    with p.open('wb') as f: subprocess.run(['gh','api',f'repos/21Z121Z1/Photographic_Style_Research/actions/artifacts/{artifact}/zip'],stdout=f,check=True)
    with p.open('rb') as f: assert hashlib.file_digest(f,'sha256').hexdigest()==sha
    with zipfile.ZipFile(p) as z:
        name=next(n for n in z.namelist() if n.endswith('.gpg'))
        with z.open(name) as f,(W/(label+'.gpg')).open('wb') as g: shutil.copyfileobj(f,g,1048576)
    key=W/(label+'-key'); key.write_text(os.environ[env]+'\n'); key.chmod(0o600)
    with key.open('rb') as f,(O/(label+'-decrypt.log')).open('w') as log:
        subprocess.run(['gpg','--batch','--override-session-key-fd',str(f.fileno()),'--output',str(W/(label+'.tar.gz')),'--decrypt',str(W/(label+'.gpg'))],pass_fds=(f.fileno(),),stdout=log,stderr=subprocess.STDOUT,check=True)
    key.unlink()
    with tarfile.open(W/(label+'.tar.gz')) as t: t.extractall(dest,filter='data')
    manifest=json.loads((dest/'out/manifest.json').read_text())
    for row in manifest['files']:
        f=dest/'out'/row['path']
        with f.open('rb') as h: assert hashlib.file_digest(h,'sha256').hexdigest()==row['sha256']
        assert f.stat().st_size==row['size']
    verified.append({'source_artifact':artifact,'zip_sha256':sha,'files':len(manifest['files']),'failures':0})
(O/'prior-verification.json').write_text(json.dumps(verified,indent=2)+'\n')
P=W/'s5/out/consumer-toneP035/semantic'; S=W/'s8/out/native'
def load(p): return np.fromfile(p,'f2').reshape(384,512,4)[...,:3].astype('f8')
y=load(P/'native.f16'); rt=load(S/'new-roundtrip.f16')
eligible=np.fromfile(S/'original-eligible.u8','u1').reshape(384,512).astype(bool)
points=np.zeros((384,512),bool); old_counts={}
for op in ['skin-color','skin-brightness','skin-both']:
    pred=y+load(S/(op+'-new-neutral.f16'))-rt; truth=load(P/(op+'-removed-oracle.f16'))
    failed=eligible&(np.max(abs(pred-truth)/np.maximum(abs(truth),1e-12),-1)>1e-3)
    old_counts[op]=int(failed.sum()); points|=failed
points.astype('u1').tofile(W/'points.u8')
(O/'requested-points.json').write_text(json.dumps({'old_counts':old_counts,'union':int(points.sum()),'threshold':1e-3,'definition':'Original S8 eligible mask, float64 arithmetic on stored native half arrays; no mask shrink.'},indent=2)+'\n')
sys.path.insert(0,str(R)); sys.path.insert(0,str(R/'research/vm-native'))
from extract_inputs import extract
from tools.heif_dump import parse_heif
from heif_standalone import standalone
photo=W/'IMG_2810.HEIC'; res=W/'res'; extract(photo,res)
assert hashlib.sha256(photo.read_bytes()).hexdigest()=='52ea41f0dd16590cef83abfd8093ccf8082994113e0c2cee86f90c42f7ab21c2'
data=photo.read_bytes(); heif=parse_heif(data)
for target,suffix in {'inputSubjectMatteImage':'semanticpersonmatte','inputSkinMatteImage':'semanticskinmatte','inputSkyMatteImage':'semanticskymatte','inputGainMapImage':'hdrgainmap'}.items():
    matches=[i for i in heif['items'].values() if i.get('aux_type','').endswith(suffix)]
    if matches: (res/(target+'.heic')).write_bytes(standalone(data,matches[0]['item_id']))
GEN=W/'generated'; GEN.mkdir()
assert run([sys.executable,SRC/'generate_semantic_s5.py',GEN],'generate-base')==0
assert run([sys.executable,SRC/'generate_semantic_s14.py',GEN],'generate-s14')==0
OLD=R/'research/vm-native/runner'; exe=W/'semantic-s14'
flags=['clang','-fobjc-arc','-O2','-I'+str(OLD),'-I'+str(GEN),'-I'+str(SRC),'-framework','Foundation','-framework','CoreImage','-framework','CoreMedia','-framework','ImageIO','-framework','Metal','-framework','CoreGraphics','-Wl,-undefined,dynamic_lookup']
if run(flags+[GEN/'semantic_consumer_s14.m','-o',exe],'build-s14')==0:
    parent=W/'probe'; parent.mkdir(); case=parent/'consumer'
    os.environ.update({'XD_TONE_MAX_EDGE':'512','XD_TONE_THUMB_MODE':'native-stage-mirror','XD_TONE_BIAS':'0.35','S14_PRIOR':str(P),'S14_S8':str(S),'S14_POINTS':str(W/'points.u8')})
    run(['xcrun','lldb','--batch','-o','run','-k','thread backtrace all','--',exe,photo,res,case],'native-s14',1500)
    native=case/'semantic'
    if native.exists(): shutil.copytree(native,O/'native')
    if (native/'s14-results.json').exists():
        run([sys.executable,SRC/'analyze_semantic_s14.py',O/'native',P,S,W/'s5/out',O/'analysis'],'analysis-s14',300)
for name in ['generated-sha256.json','generated-source-sha256.json']:
    if (GEN/name).exists(): shutil.copy2(GEN/name,O/name)
print('S14 finite-domain audit finished. All private output encrypted; no global-hull certificate assumed.')
assert all(s['returncode']==0 for s in status), 'Probe subprocess failed; inspect encrypted logs'
assert (O/'analysis/s14-analysis.json').exists(), 'No validated finite-set result; inspect native context/checkpoints'
