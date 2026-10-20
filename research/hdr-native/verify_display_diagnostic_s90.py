"""Metadata-only verification of fixed-display/bit-depth diagnostic evidence."""
from pathlib import Path
import hashlib,json,zipfile,subprocess,sys
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def inspect(d,archives):
    e=d/'evidence/s90/run';q=json.loads((e/'archive-receipt.json').read_text());repo=d.parents[1];files={}
    for r in q['artifacts']:
        path=archives/str(q['run_id'])/('artifact-'+str(r['artifact_id'])+'.zip');assert path.stat().st_size==r['ZIP_bytes']and sha(path)==r['ZIP_sha256']
        if r['name']=='hdr-s90-aggregate':
            with zipfile.ZipFile(path)as z:
                m=json.loads(z.read('manifest.json'));assert m['run_id']==str(q['run_id'])and m['commit']==q['source_commit']and m['os_build']=='26A434'
                for v in m['files']:
                    raw=z.read(v['path']);assert len(raw)==v['size']and hashlib.sha256(raw).hexdigest()==v['sha256'];assert(e/v['path']).read_bytes()==raw;files[v['path']]=raw
    f=json.loads(files['suite-freeze.json']);a=json.loads(files['analysis.json'])
    for name,h in f['source_sha256'].items():assert hashlib.sha256(subprocess.check_output(['git','show',q['source_commit']+':'+name],cwd=repo)).hexdigest()==h
    b=json.loads((d/'evidence/s89/run/IMG_2600/analysis.json').read_text());assert a['M_S_H_SHA_baseline']==b['source_pixel_SHA_before_after_unchanged']
    rows=[]
    for r in a['rows']:
        if not r['completed']:rows.append({'bits':r['bits'],'completed':False,'actual_hvcC':r.get('actual_hvcC')});continue
        assert r['actual_hvcC']['bit_depth_luma']==r['bits']and r['actual_colr']['matrix_coefficients']==6 and r['SDR_max0']and r['source_and_native_inputs_SHA_unchanged']
        n=json.loads(files['native-'+str(r['bits'])+'.json']);assert n['success']and n['ImageIO_full_SDR']['decoded_sdr_max0_verified']
        assert sum(x['pixels']for x in r['brightness_bins'])==5712*4284
        assert set(r['display'])=={'1','2','8'}
        for head,v in r['display'].items():
            assert v['display_pixel_max_RGB_code_error']['n']==5712*4284 and v['all_preview_input_SHA_equal']
            assert all(0<=x<=5712*4284 for x in v['pixel_counts_error_gt_codes'].values())
        rows.append({'bits':r['bits'],'completed':True,'actual_bit_depth':r['actual_hvcC']['bit_depth_luma'],'SDR_max0':True,'gain_nominal_step_EV':r['gain_nominal_step_EV'],'display':r['display'],'brightness_bins':r['brightness_bins'],'linear_metrics':r['metrics']})
    assert not a['engineering_accepted']and not a['A_phase_complete']and not a['acceptance_complete']
    assert len(q['private_stream_verifications'])==1 and q['private_stream_verifications'][0]['GPG_returncode']==0 and'DECRYPTION_OKAY'in q['private_stream_verifications'][0]['event_names_only']
    failure=json.loads(files['failure.json'])if'failure.json'in files else None
    return {'run_id':q['run_id'],'source_commit':q['source_commit'],'OS_build':'26A434','image_version':q['image_version'],'run_conclusion':q['conclusion'],'source_S_M_H_same_as_S89':True,'public_manifest_members_SHA_verified':len(m['files']),'GPG_cipher_verified':True,'completed_variants':[r['bits']for r in rows if r['completed']],'rows':rows,'failure':failure,'diagnostic_not_acceptance':True,'A_phase_complete':False,'engineering_accepted':False,'acceptance_complete':False}
def main():
    d=Path(__file__).resolve().parent;archives=Path(sys.argv[1])if len(sys.argv)>1 else d.parents[1].parent/'hdr-native-20261019/runs';print(json.dumps(inspect(d,archives),indent=2))
if __name__=='__main__':main()
