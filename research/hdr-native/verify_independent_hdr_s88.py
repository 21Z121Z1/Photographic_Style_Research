"""Metadata-only evidence check; no image decoding or new native execution."""
from pathlib import Path
import hashlib,json,zipfile,subprocess,sys
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
    p=Path(__file__).resolve();repo=p.parents[2];root=repo.parent;e=p.parent/'evidence/s88';receipt=json.loads((e/'run/archive-receipt.json').read_text());out=Path(sys.argv[1])if len(sys.argv)>1 else root/'hdr-native-20261019/runs'
    files={}
    for a in receipt['artifacts']:
        path=out/str(receipt['run_id'])/('artifact-'+str(a['artifact_id'])+'.zip');assert path.stat().st_size==a['ZIP_bytes']and sha(path)==a['ZIP_sha256']
        if a['name']=='hdr-s88-aggregate':
            with zipfile.ZipFile(path)as z:
                m=json.loads(z.read('manifest.json'));assert m['run_id']==str(receipt['run_id'])and m['commit']==receipt['source_commit']and m['os_build']=='26A434'
                for row in m['files']:
                    raw=z.read(row['path']);assert len(raw)==row['size']and hashlib.sha256(raw).hexdigest()==row['sha256'];assert(e/'run'/row['path']).read_bytes()==raw;files[row['path']]=raw
    f=json.loads(files['integration-freeze.json'])
    for name,h in f['source_sha256'].items():
        source=subprocess.check_output(['git','show',receipt['source_commit']+':'+name],cwd=repo);assert hashlib.sha256(source).hexdigest()==h
    a=json.loads(files['analysis.json']);summary=json.loads((e/'phase-summary.json').read_text());n=json.loads(files['native.json'])
    assert a['shape']==[4032,3024,3]and a['source_photo_SHA_unchanged']and a['master_EXR_SHA_unchanged']and a['integration_freeze_SHA_unchanged']
    assert all(r['before']==r['after']for r in a['preview_checks'])and n['ImageIO_full_SDR']['decoded_sdr_max0_verified']and a['metrics']['CI_SDR_vs_original']['max_abs']==0
    assert summary['actual_gain_native_equation_and_headroom_original_float_gates_pass']and not summary['full_HDR_target_original_gates_pass']
    assert len(receipt['private_stream_verifications'])==2
    for v in receipt['private_stream_verifications']:assert v['GPG_returncode']==0 and'DECRYPTION_OKAY'in v['event_names_only']and not v['images_decoded_or_written_in_VM']
    assert not a['engineering_accepted']and not a['A_phase_complete']and not a['acceptance_complete']
    print(json.dumps({'run_id':receipt['run_id'],'original_ZIP_and_public_manifest_SHA_verified':len(m['files']),'source_commit_hashes_verified':True,'SDR_full_max0':True,'native_actual_gain_float_gates':True,'defined_HDR_target_original_gates':False,'private_GPG_receipts_checked_without_redecrypt_or_image_decode':2,'A_phase_complete':False}))
if __name__=='__main__':main()
