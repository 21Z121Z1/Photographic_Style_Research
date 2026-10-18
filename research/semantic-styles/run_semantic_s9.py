"""Run only saved-array diagnostics on macOS; no new native/precision search."""
from pathlib import Path
import os, sys, subprocess, hashlib, zipfile, shutil, tarfile, json
W=Path(os.environ['W']);O=W/'out';O.mkdir(exist_ok=True);SRC=Path('research/semantic-styles');status=[]
assert subprocess.check_output(['sw_vers','-buildVersion'],text=True).strip()=='26A434'
for label,artifact,sha,env in [('s5',12140624073,'55f845778415b22276bc92e166416e60a29df6ce559df8f3fd71f6f5911d12fc','S5_ARCHIVE_SESSION'),('s8',12146693880,'b48ae649e8c491474f8a34a3927b5d354e4920ead46c783794c8aaab8c8c4746','S8_ARCHIVE_SESSION')]:
 dest=W/label;dest.mkdir();p=W/(label+'.zip')
 with p.open('wb') as f:subprocess.run(['gh','api',f'repos/21Z121Z1/Photographic_Style_Research/actions/artifacts/{artifact}/zip'],stdout=f,check=True)
 with p.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==sha
 with zipfile.ZipFile(p) as z:
  n=next(n for n in z.namelist() if n.endswith('.gpg'))
  with z.open(n) as a,(W/(label+'.gpg')).open('wb') as b:shutil.copyfileobj(a,b)
 key=W/(label+'-key');key.write_text(os.environ[env]+'\n');key.chmod(0o600)
 with key.open('rb') as f,(O/(label+'-decrypt.log')).open('w') as log:
  subprocess.run(['gpg','--batch','--override-session-key-fd',str(f.fileno()),'--output',str(W/(label+'.tar.gz')),'--decrypt',str(W/(label+'.gpg'))],pass_fds=(f.fileno(),),stdout=log,stderr=subprocess.STDOUT,check=True)
 key.unlink()
 with tarfile.open(W/(label+'.tar.gz')) as t:t.extractall(dest,filter='data')
 manifest=json.loads((dest/'out/manifest.json').read_text())
 for row in manifest['files']:
  f=dest/'out'/row['path']
  with f.open('rb') as h:assert hashlib.file_digest(h,'sha256').hexdigest()==row['sha256']
  assert f.stat().st_size==row['size']
 status.append({'archive':label,'sha256':sha,'verified_files':len(manifest['files']),'failures':0})
(O/'prior-verification.json').write_text(json.dumps(status,indent=2)+'\n')
with (O/'diagnostics.log').open('w') as log:
 rc=subprocess.run([sys.executable,SRC/'semantic_s9_analysis.py',W/'s5/out/consumer-toneP035/semantic',W/'s8/out/native',O/'diagnostics'],stdout=log,stderr=subprocess.STDOUT,timeout=300).returncode
(O/'status.json').write_text(json.dumps({'diagnostics_returncode':rc,'new_inverse_search_performed':False})+'\n')
sys.exit(rc)
