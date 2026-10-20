"""Runner only: encrypt remaining new private outputs after a failed child."""
from pathlib import Path
import hashlib,json,os,subprocess,tarfile
W=Path(os.environ['W']);P=W/'private';ENC=W/'encrypted';O=W/'out';records=[]
def sha(p):
    with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
for folder in sorted(P.iterdir()):
    assert folder.is_dir()and not folder.is_symlink()
    files=[p for p in folder.rglob('*')if p.is_file()]
    if not files:continue
    # Avoid encrypting/uploading a duplicate when the main driver already sealed
    # this folder and only its per-run plaintext cleanup failed.
    checkpoint=O/folder.name/'delivery-analysis.json';saved=json.loads(checkpoint.read_text())if checkpoint.exists()else{}
    existing=saved.get('encrypted')or saved.get('partial_encrypted')
    if existing:
        path=ENC/existing['file'];assert path.is_file()and path.stat().st_size==existing['bytes']and sha(path)==existing['sha256'];records.append({'folder':folder.name,'already_sealed':True,'cipher':existing});continue
    manifest=folder/'manifest.json'
    if not manifest.exists():
        manifest.write_text(json.dumps({'run_id':os.environ['GITHUB_RUN_ID'],'commit':os.environ['GITHUB_SHA'],'os_build':'26A434','partial_after_failure':True,'files':[{'path':str(p.relative_to(folder)),'size':p.stat().st_size,'sha256':sha(p)}for p in sorted(files)]},indent=2)+'\n')
    m=json.loads(manifest.read_text());assert m['run_id']==os.environ['GITHUB_RUN_ID']and m['commit']==os.environ['GITHUB_SHA']and m['os_build']=='26A434'
    assert {str(p.relative_to(folder))for p in folder.rglob('*')if p.is_file()}=={'manifest.json',*(x['path']for x in m['files'])}
    for row in m['files']:
        path=folder/row['path'];assert path.stat().st_size==row['size']and sha(path)==row['sha256']
    name=folder.name+'-fallback-delivery';tarpath=W/(name+'.tar.gz');cipher=ENC/(name+'.tar.gz.gpg');assert not cipher.exists()
    with tarfile.open(tarpath,'w:gz')as t:t.add(folder,arcname='out')
    subprocess.run(['gpg','--batch','--trust-model','always','--recipient','28E62F64A29764C2F2AEBF5D5B6B1C101E5F5ABA','--output',cipher,'--encrypt',tarpath],check=True,timeout=1200)
    records.append({'folder':folder.name,'already_sealed':False,'file':cipher.name,'bytes':cipher.stat().st_size,'sha256':sha(cipher),'partial_after_failure':True})
(O/'fallback-seal.json').write_text(json.dumps({'files':records,'private_plaintext_uploaded':False},indent=2)+'\n')
print(json.dumps({'remaining_private_folders':len(records),'plaintext_uploaded':False}))
