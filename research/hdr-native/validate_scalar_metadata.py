"""Audit S55-S59 archived evidence without rerendering images or refitting models."""
from pathlib import Path
import argparse,base64,hashlib,json,zipfile
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--out',type=Path,required=True);args=p.parse_args();R=args.root
ids={'S55':39307765465,'S56':39308719398,'S57':39310642611,'S58':39311415530,'S59':39312021801};verified={}
provenance=json.loads((R/'hdr-native-20261019/archive-provenance-s55-s59.json').read_text())['runs']
def sha(path):
    with Path(path).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(phase,name):return json.loads((R/'hdr-native-20261019/runs'/str(ids[phase])/'selected'/name).read_text())
for phase,rid in ids.items():
    root=R/'hdr-native-20261019/runs'/str(rid);receipt=provenance[phase];zips=list(root.glob('artifact-*.zip'));assert len(zips)==1
    assert sha(zips[0])==receipt['ZIP_sha256'];manifest=read(phase,'manifest.json');assert manifest['os_build']=='26A434'
    assert sha(root/'selected/manifest.json')==receipt['manifest_sha256']
    for entry in manifest['files']:assert sha(root/'selected'/entry['path'])==entry['sha256']and(root/'selected'/entry['path']).stat().st_size==entry['size']
    with zipfile.ZipFile(zips[0])as z:
        assert set(z.namelist())=={x['path']for x in manifest['files']}|{'manifest.json'}
        for name in z.namelist():assert hashlib.sha256(z.read(name)).hexdigest()==sha(root/'selected'/name)
    verified[phase]={'run':rid,'artifact':receipt['artifact_id'],'ZIP_sha256':receipt['ZIP_sha256'],'manifest_sha256':receipt['manifest_sha256'],'conclusion':receipt['conclusion']}
old=read('S55','native-histogram-s55.json');assert not old['completed']and not old['rows']
syn=read('S56','synthetic-analysis-s56.json');native=read('S56','native-histogram-s56.json')
assert native['completed']and len(native['rows'])==269 and native['PSO']['original_host_object']and native['prepare_mask']==1
assert all(x['inputs_and_external_context_SHA_unchanged']for x in native['rows'])
assert syn['half_gate_passed']and syn['half_bit_exact_cases']==269 and syn['max_abs']==0 and syn['nonfinite_tail_cases']==0
s57=read('S57','analysis-s57.json');global_analysis=read('S57','global-gain-analysis-s57.json');real=read('S57','real-map-compatibility-s57.json');t=read('S57','transport-check-s57.json')
assert t['returncode']==0 and t['plaintext_sha256_matches']and t['plaintext_size_matches']and'DECRYPTION_OKAY'in t['events']
assert global_analysis['positive_finite_cases']==7 and global_analysis['finite_domain_max_abs']<=1e-5
assert s57['prior_native_histogram_cases_repeated']==0 and not s57['camera_native_execution']
assert len(real['photos'])==3 and all(not x['consumer_context_positive_finite']and x['normalizers']['captured_consumer_ltm_max']==0 and x['normalizers']['captured_consumer_lin_max']==0 for x in real['photos'])
s58=read('S58','analysis-s58.json');sets=read('S58','finite-half-normalizer-analysis-s58.json')
assert s58['all_declared_positive_half_reference_normalizers_enumerated']and not s58['native_camera_binding_proven']and not s58['native_fast_math_full_domain_proven']
assert sets['prior_native_output_components_checked']==538 and sets['prior_native_cases_reexecuted']==0 and len(sets['rows'])==6
for row in sets['rows']:
    bitmap=base64.b64decode(row['feasible_M_bitset_base64'],validate=True);assert len(bitmap)==3968 and hashlib.sha256(bitmap).hexdigest()==row['feasible_M_bitset_sha256']and not(bitmap[0]&1)
    assert sum(x.bit_count()for x in bitmap)==row['feasible_normalizer_count']and row['complete_positive_half_domain_tested']==31743
s59=read('S59','analysis-s59.json');compat=read('S59','candidate-native-compatibility-s59.json')
assert s59['original_host_PSO']and s59['new_native_cases']==768 and s59['all_six_256_bucket_codebooks_observed']
assert compat['reference_tail_different_components']==0 and compat['half_gate_passed_for_this_tail']and compat['all_encoded_map_elements_have_native_code_preimage']
assert len(compat['rows'])==6 and all(x['native_code_compatible_elements']==1024 and x['unique_bucket_elements']==1024 and x['uncovered_elements']==0 for x in compat['rows'])
for x in [s57,s58,s59]:assert x['A_phase_complete']is False and x['acceptance_complete']is False
out={'archive_integrity_passed':True,'suboperator_tail_half_gate_passed':True,'suboperator_global_finite_sample_abs_gate_passed':True,'prior_native_histogram_dispatches_repeated':0,'conditional_reference_sets_bitsets_verified':True,'native_candidate_codebook_compatible_elements':6144,'native_candidate_codebooks_buckets_each':256,'full_real_camera_scalar_generation_certified':False,'full_scene_recovery_certified':False,'native_fast_math_full_domain_certified':False,'old_skin_33_tight_hull_certified':False,'legacy_thresholds_or_masks_changed':False,'A_phase_complete':False,'acceptance_complete':False,'runs':verified,'goal_status':'active'}
with args.out.open('x')as f:json.dump(out,f,indent=2);f.write('\n')
print(json.dumps({k:v for k,v in out.items()if k!='runs'}))
