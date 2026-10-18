"""Native format and small ARM-block replay; input is immutable encrypted S17."""
from pathlib import Path
import os,sys,hashlib,json,subprocess,zipfile,shutil,tarfile
W=Path(os.environ['W']);O=W/'out';O.mkdir(exist_ok=True);SRC=Path('research/semantic-styles');status=[]
def run(args,label,timeout=300):
    with (O/(label+'.log')).open('w') as log:rc=subprocess.run(list(map(str,args)),stdout=log,stderr=subprocess.STDOUT,timeout=timeout).returncode
    status.append({'operation':label,'returncode':rc});(O/'status.json').write_text(json.dumps(status,indent=2)+'\n');assert rc==0,label
assert subprocess.check_output(['sw_vers','-buildVersion'],text=True).strip()=='26A434'
p=W/'s17.zip'
with p.open('wb') as f:subprocess.run(['gh','api','repos/21Z121Z1/Photographic_Style_Research/actions/artifacts/12149258316/zip'],stdout=f,check=True)
with p.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()=='ce03b63fa5d35757f228d95d71fd6b13e8592d0d472eb9add70f9389df002c47'
with zipfile.ZipFile(p) as z:
    n=next(n for n in z.namelist() if n.endswith('.gpg'))
    with z.open(n) as a,(W/'s17.gpg').open('wb') as b:shutil.copyfileobj(a,b)
key=W/'session-key';key.write_text(os.environ['S17_ARCHIVE_SESSION']+'\n');key.chmod(0o600)
with key.open('rb') as f,(O/'prior-decrypt.log').open('w') as log:subprocess.run(['gpg','--batch','--override-session-key-fd',str(f.fileno()),'--output',str(W/'prior.tar.gz'),'--decrypt',str(W/'s17.gpg')],pass_fds=(f.fileno(),),stdout=log,stderr=subprocess.STDOUT,check=True)
key.unlink();prior=W/'prior';prior.mkdir()
with tarfile.open(W/'prior.tar.gz') as t:t.extractall(prior,filter='data')
manifest=json.loads((prior/'out/manifest.json').read_text())
for row in manifest['files']:
    p=prior/'out'/row['path']
    with p.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==row['sha256']
    assert p.stat().st_size==row['size']
(O/'prior-verification.json').write_text(json.dumps({'source_run':39162555357,'verified_files':len(manifest['files']),'failures':0},indent=2)+'\n')
exe=W/'probe-s18';run(['clang','-fobjc-arc','-O2',SRC/'probe_s18.m','-framework','Foundation','-framework','Metal','-o',exe],'compile-format')
with (O/'native-format.json').open('w') as f:subprocess.run([exe],stdout=f,check=True)
run([sys.executable,SRC/'audit_semantic_s18.py',prior/'out',O/'analysis'],'bounds-audit')
print('S18 complete: representation envelope and limited producer block, no pixel solver.')
