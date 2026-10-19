"""Read-only aggregate/manifest audit; no local image processing or gate waiver."""
from pathlib import Path
import argparse,hashlib,json,zipfile
p=argparse.ArgumentParser();p.add_argument('--archive-root',type=Path,required=True);a=p.parse_args()
def sha(p):
    with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
root=Path(__file__).resolve().parent;pro=json.loads((root/'evidence/s64/archive-provenance.json').read_text());found={}
for rid,r in pro['runs'].items():
    where=a.archive_root/'runs'/rid;archive=where/f"artifact-{r['artifact_id']}.zip";assert sha(archive)==r['ZIP_sha256']
    with zipfile.ZipFile(archive)as z:
        m=z.read('manifest.json');assert hashlib.sha256(m).hexdigest()==r['manifest_sha256'];m=json.loads(m)
        assert m['commit']==r['commit']and m['run_id']==rid and m['os_build']=='26A434'
        assert set(z.namelist())=={'manifest.json'}|{x['path']for x in m['files']}
        for x in m['files']:assert len(z.read(x['path']))==x['size']and hashlib.sha256(z.read(x['path'])).hexdigest()==x['sha256']
        if rid=='39324317293':
            found['rows']=[json.loads(z.read(n))for n in z.namelist()if n.endswith('-summary.json')]
        if rid=='39326316262':
            found['diag']=json.loads(z.read('geometry-diagnostics-s64.json'));found['colour']=json.loads(z.read('color-context-s64.json'));found['decrypt']=json.loads(z.read('decrypt-check-s64.json'))
rows=found['rows'];assert len(rows)==5
for x in rows:
    h=x['host'];g=x['global_context'];assert x['completed']and x['basic_stats_finite']and len(h['dispatches'])==9
    assert h['input_textures_SHA_unchanged']and h['barrier_queue_matches_supplied']and h['SRL_before_stats']==0
    assert h['reduction_calls'][0]['argument']is False and not any(d['PSO']=='_updateBaseGainWithStats'for d in h['dispatches'])
    assert g['native_base_gain']==g['metadata_base_gain']and g['native_baseline_exposure']==g['metadata_baseline_exposure']
different=sum(x['maps'][n]['different_half_codes']for x in rows for n in ['c','d']);assert different==9279
assert not found['diag']['identity_half_bit_exact_for_all']and found['diag']['selected_development_hypothesis']=='identity'
assert all(x['all_320_bytes_equal']for x in found['colour']['photos']if 'old_consumer_run'in x)
assert found['decrypt']['returncode']==0 and found['decrypt']['plaintext_tar_sha256_matches']
private=json.loads((a.archive_root/'runs/39324317293/private-verification.json').read_text());assert private['compressed_plaintext_sha256_verified']and private['all_private_members_verified']==70
print(json.dumps({'five_full_size_stats_hosts_completed':True,'all_artifact_members_verified':True,'native_dispatches':45,'file_map_different_half_codes':different,'file_map_samples':10240,'file_map_half_gate_passed':False,'original_camera_source_domain_authenticated':False,'old_masks_thresholds_changed':False,'A_phase_complete':False,'acceptance_complete':False}))
