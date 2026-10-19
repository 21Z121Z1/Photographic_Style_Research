"""Stream one encrypted artifact, optionally retain only its exact master EXR.

Run local Python through scripts/local-python-scope.sh. No pixel decoder/numpy.
The caller must obtain explicit permission before raising the 100 MB phase cap.
"""
from pathlib import Path
import argparse,json,subprocess,hashlib,struct,threading,tarfile,shutil,os,resource,datetime
parser=argparse.ArgumentParser();parser.add_argument('--work-root',type=Path,required=True);parser.add_argument('--photo',choices=['IMG_0032','IMG_0033','IMG_2604','IMG_2608'],default='IMG_0032');parser.add_argument('--output',type=Path);parser.add_argument('--receipt',type=Path,required=True);parser.add_argument('--phase-cap-bytes',type=int,default=100_000_000);parser.add_argument('--authorization-note',default='Original continuing-phase100MB permission');args=parser.parse_args()
R=args.work_root.resolve();O=R/'hdr-native-20261019';D=R/'repo/research/hdr-native';repo='21Z121Z1/Photographic_Style_Research';plan=json.loads((D/'inputs-s51.json').read_text());case=next(c for c in plan['cases'] if c['photo']==args.photo);row=next(r for r in json.loads((O/'runs/39254061338/selected/analysis-s42.json').read_text())['rows'] if r['photo']==args.photo);master=next(x for x in row['EXRs'] if x['path']=='scene_candidate_linear_P3.exr');cipher=row['encrypted_full'];pre=json.loads((O/'s33/preflight.json').read_text())
def tree(p):return sum(q.stat().st_size for q in p.rglob('*') if q.is_file() and not q.is_symlink())
used=tree(O)+tree(D)+sum(max(0,Path(p).stat().st_size-m['size']) for p,m in pre['documents'].items());retain=master['size'] if args.output else 0
assert not args.receipt.exists() and args.receipt.resolve().is_relative_to(O)
assert args.phase_cap_bytes==100_000_000 or args.authorization_note!='Original continuing-phase100MB permission','Record the explicit new user authorization; elapsed time is not approval'
assert used+retain+131072<=args.phase_cap_bytes and shutil.disk_usage('/').free-retain>4_100_000_000,'Phase write or disk floor would be exceeded'
output=args.output.resolve() if args.output else None;partial=None;created=False;finalized=False
if output:
    assert output.is_relative_to(O/'scene-candidates') and not output.exists(),'Only new private candidate paths outside repository are allowed'
    output.parent.mkdir(parents=True,exist_ok=True,mode=0o700);partial=output.with_name(output.name+'.owned-partial');assert not partial.exists()
api=json.loads(subprocess.check_output(['gh','api',f"repos/{repo}/actions/artifacts/{case['artifact_id']}"]));assert not api['expired'] and api['size_in_bytes']==case['ZIP_bytes']<1_000_000_000 and api['digest']=='sha256:'+case['ZIP_sha256']
remote=subprocess.Popen(['gh','api',f"repos/{repo}/actions/artifacts/{case['artifact_id']}/zip"],stdout=subprocess.PIPE,stderr=subprocess.PIPE);local=None;events=[];failures=[];ziphash=hashlib.sha256();cipherhash=hashlib.sha256();zipbytes=0;members=[];status_thread=None;feeder=None
def get(n):
    global zipbytes
    b=remote.stdout.read(n);zipbytes+=len(b);ziphash.update(b);assert zipbytes<=case['ZIP_bytes'];return b
try:
    header=get(30);assert len(header)==30 and header[:4]==b'PK\x03\x04';fields=struct.unpack('<IHHHHHIIIHH',header);assert fields[3]==0;nl,xl=fields[-2:];assert nl+xl<4096;names=get(nl+xl);assert len(names)==nl+xl and names[:nl].decode()==cipher['file']==case['cipher_member']
    local=subprocess.Popen(['gpg','--homedir',str(R/'semantic-20261018/private/gnupg'),'--batch','--status-fd','2','--decrypt'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    def status():
        for line in iter(local.stderr.readline,b''):
            if line.startswith(b'[GNUPG:] '):
                parts=line.split();events.append(parts[1].decode())
    def feed():
        try:
            remain=cipher['size']
            while remain:
                b=get(min(remain,65536));assert b,'Truncated ciphertext';remain-=len(b);cipherhash.update(b);local.stdin.write(b)
            local.stdin.close()
            while get(65536):pass
            assert remote.wait(timeout=30)==0 and zipbytes==case['ZIP_bytes'] and ziphash.hexdigest()==case['ZIP_sha256'] and cipherhash.hexdigest()==case['cipher_sha256']
        except BaseException as exc:
            failures.append(type(exc).__name__+': '+str(exc))
            try:local.stdin.close()
            except (BrokenPipeError,ValueError):pass
    status_thread=threading.Thread(target=status,daemon=True);status_thread.start();feeder=threading.Thread(target=feed,daemon=True);feeder.start()
    with tarfile.open(fileobj=local.stdout,mode='r|gz') as tar:
        for m in tar:
            if not m.isfile():continue
            rel=Path(m.name);assert len(rel.parts)==2 and rel.parts[0]=='full' and not rel.is_absolute() and rel.name in {'scene_candidate_linear_P3.exr','log2_RGB_gain.exr','positive_pair_mask.npy','meaning.json'};assert 0<=m.size<400_000_000;digest=hashlib.sha256();total=0;dest=None
            if rel.name=='scene_candidate_linear_P3.exr' and output:
                assert m.size==master['size'];dest=os.fdopen(os.open(partial,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'wb');created=True
            try:
                with tar.extractfile(m) as src:
                    while b:=src.read(65536):digest.update(b);total+=len(b);dest.write(b) if dest else None
            finally:
                if dest:dest.close()
            assert total==m.size;members.append({'path':m.name,'size':total,'sha256':digest.hexdigest(),'retained':bool(dest)})
    # GPG may still have gzip/tar padding to deliver after tar's logical EOF.
    while local.stdout.read(65536):pass
    feeder.join(timeout=120);assert not feeder.is_alive() and not failures,failures;rc=local.wait(timeout=120);status_thread.join(timeout=10);assert rc==0 and 'DECRYPTION_OKAY' in events and 'GOODMDC' in events
    assert {Path(x['path']).name for x in members}=={'scene_candidate_linear_P3.exr','log2_RGB_gain.exr','positive_pair_mask.npy','meaning.json'}
    master_member=next(x for x in members if Path(x['path']).name=='scene_candidate_linear_P3.exr');gain_member=next(x for x in members if Path(x['path']).name=='log2_RGB_gain.exr');assert master_member['size']==master['size'] and master_member['sha256']==case['master_EXR_sha256'];assert gain_member['sha256']==case['old_logmap_EXR_sha256']
    if output:
        # No-clobber promotion. Only this invocation's partial is removed.
        os.link(partial,output);partial.unlink();created=False;finalized=True
    receipt={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'photo':args.photo,'source_run':'39254061338','source_artifact_id':case['artifact_id'],'source_build':'26A434','ZIP_bytes':zipbytes,'ZIP_sha256':ziphash.hexdigest(),'cipher_sha256':cipherhash.hexdigest(),'GPG_returncode':rc,'GPG_status_event_names_only':events,'all_members':members,'retained_master':str(output.relative_to(R)) if output else None,'retained_bytes':retain,'phase_accounted_bytes_before':used,'authorized_phase_cap_bytes':args.phase_cap_bytes,'authorization_note':args.authorization_note,'private_key_or_session_key_exported':False,'full_cipher_or_tar_saved':False,'local_pixel_decoding_or_image_computation':False,'scene_physical_accuracy_certified':False,'meaning':'Exact S42 half-linearP3 candidate bytes only; global/local/semantic and RAW limitations remain. No nit calibration.','max_self_RSS_KiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'max_child_RSS_KiB':resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,'root_free_bytes':shutil.disk_usage('/').free}
    with args.receipt.open('x') as f:json.dump(receipt,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({k:v for k,v in receipt.items() if k not in ['all_members','GPG_status_event_names_only','authorization_note']}))
finally:
    for p in [local,remote]:
        if p is not None and p.poll() is None:
            p.terminate()
            try:p.wait(timeout=10)
            except subprocess.TimeoutExpired:p.kill();p.wait(timeout=10)
    if created and partial and partial.exists():partial.unlink()
