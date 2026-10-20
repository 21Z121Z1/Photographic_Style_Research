"""Check five-photo saved evidence and report original thresholds separately."""
from pathlib import Path
import hashlib,json,zipfile,subprocess,sys,math
def sha(path):
    with Path(path).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def gates(v):
    return {'max_abs_le_1e5':v['max_abs']<=1e-5,'max_relative_floor1e6_le_1e3':v['max_relative_floor_1e6']<=1e-3,'PSNR_peak1_ge_60':v['PSNR_peak1_dB']=='inf'or v['PSNR_peak1_dB']>=60}
def inspect(root,archive_root):
    e=root/'evidence/s89/run';receipt=json.loads((e/'archive-receipt.json').read_text());repo=root.parents[1];files={}
    for row in receipt['artifacts']:
        p=archive_root/str(receipt['run_id'])/('artifact-'+str(row['artifact_id'])+'.zip');assert sha(p)==row['ZIP_sha256']and p.stat().st_size==row['ZIP_bytes']
        if row['name']=='hdr-s89-aggregate':
            with zipfile.ZipFile(p)as z:
                m=json.loads(z.read('manifest.json'));assert m['run_id']==str(receipt['run_id'])and m['commit']==receipt['source_commit']and m['os_build']=='26A434'
                for r in m['files']:
                    data=z.read(r['path']);assert len(data)==r['size']and hashlib.sha256(data).hexdigest()==r['sha256'];assert(e/r['path']).read_bytes()==data;files[r['path']]=data
    suite=json.loads(files['suite-freeze.json']);analysis=json.loads(files['analysis.json']);assert not analysis['engineering_accepted']and not analysis['A_phase_complete']and not analysis['acceptance_complete']
    for path,h in suite['source_sha256'].items():
        source=subprocess.check_output(['git','show',receipt['source_commit']+':'+path],cwd=repo);assert hashlib.sha256(source).hexdigest()==h
    assert [c['photo']for c in suite['cases']]==[r['photo']for r in analysis['rows']]
    rows=[]
    for r in analysis['rows']:
        assert r['completed']and r['child_returncode']==0
        photo=r['photo'];original=r['original_S88_metrics'];ideal=r['ideal_headroom_metrics'];assert set(ideal)=={'1','2','8'}
        assert all(v['nonfinite_components']==0 for v in [*original.values(),*ideal.values()])
        assert r['SDR_max0']and original['CI_SDR_vs_original']['max_abs']==0
        assert all(c['before']==c['after']for c in r['preview_checks'])
        a=json.loads(files[photo+'/analysis.json']);assert all(c['before']==c['after']for c in a['preview_checks'])
        assert a['source_photo_SHA_unchanged']and a['master_EXR_SHA_unchanged']and a['integration_freeze_SHA_unchanged']
        rows.append({'photo':photo,'role':r['role'],'shape':a['shape'],'master_EXR_matches_old':r['actual_master_matches_old_EXR'],'SDR_max0':r['SDR_max0'],'original_float_gates_per_operator':{k:gates(v)for k,v in original.items()},'ideal_headroom_original_float_gates':{k:gates(v)for k,v in ideal.items()},'target_EV_p99':original['encoded_HDR_vs_target']['EV_abs_p99'],'target_EV_max':original['encoded_HDR_vs_target']['EV_abs_max_f64'],'ideal_h2_EV_p99':ideal['2']['EV_abs_p99'],'max_RGB_relative_point':r['max_RGB_relative_diagnostic']})
    assert len(rows)==5 and analysis['completed_photos']==5 and analysis['completed_recipe_holdouts']==2
    assert len(receipt['private_stream_verifications'])==6
    for v in receipt['private_stream_verifications']:assert v['GPG_returncode']==0 and'DECRYPTION_OKAY'in v['event_names_only']and not v['images_decoded_or_written_in_VM']
    return {'run_id':receipt['run_id'],'source_commit':receipt['source_commit'],'os_build':'26A434','image_version':receipt['image_version'],'original_public_members_SHA_verified':len(m['files']),'private_archive_GPG_receipts_checked_without_image_decode':6,'completed_photos':5,'completed_encoded_integration_holdouts':2,'holdout_scope':suite['holdout_scope'],'all_five_SDR_max0':True,'rows':rows,'legacy_thresholds_changed':False,'A_phase_complete':False,'engineering_accepted':False,'acceptance_complete':False}
def main():
    d=Path(__file__).resolve().parent;r=d.parents[1].parent;archive=Path(sys.argv[1])if len(sys.argv)>1 else r/'hdr-native-20261019/runs';result=inspect(d,archive);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
