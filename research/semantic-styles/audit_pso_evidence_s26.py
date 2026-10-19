"""Read-only text/provenance audit. Exit0 does NOT certify an inverse or global hull."""
from pathlib import Path
import sys,json,hashlib,csv,subprocess,shutil
R=Path(sys.argv[1]).resolve();D=R/'semantic-20261018';O=D/'s22-s26';E=R/'repo/research/semantic-styles/evidence'
def read(p):return json.loads(p.read_text())
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
# Existing audit includes original frozen files, old previews, old gates and refs.
base=subprocess.run([sys.executable,'-I',str(D/'scripts/audit_semantic_evidence.py')],capture_output=True,text=True,check=True)
prior=json.loads(base.stdout);assert prior['verified_archives']==18
prov=read(O/'run-provenance-s22-s26-20261019.json');assert len(prov)==9
assert sum(v['conclusion']=='success' for v in prov)==5
for v in prov:
 root=D/'runs'/v['run_id'];a=read(root/'archive-audit.json');m=read(root/'selected/out/manifest.json')
 assert sha(root/'artifact.zip')==v['zip_sha256']==a['zip_sha256']
 assert a['gpg_returncode']==0 and not a['manifest_failures']
 assert sha(root/'selected/out/manifest.json')==v['manifest_sha256']
 assert sha(root/'job-public.log')==v['job_log_sha256'] and m['commit']==v['commit']
 assert v['only_text_uploaded'] and v['runner_plaintext_cleanup_success'] and v['os_build']=='26A434' and v['retention_days']==1
 for row in a['files']:
  assert Path(row['path']).suffix in ['.json','.ll','.txt','.log','.md','.asm']
  if row['materialized']:assert sha(root/'selected/out'/row['path'])==row['sha256']
 jobs=read(O/'jobs'/(v['run_id']+'.json'));steps=[s for j in jobs['jobs'] for s in j['steps'] if s['name'].startswith('Remove own runner plaintext')];assert len(steps)==1 and steps[0]['conclusion']=='success'
assert all(sha(R/x['file'])==x['sha256'] for x in read(D/'evidence-index.json').values())
state=read(O/'pre-delivery-state.json')
for row in state['files']:
 with (R/row['file']).open('rb') as f:before=f.read(row['size'])
 assert hashlib.sha256(before).hexdigest()==row['sha256'],row['file']
c=read(R/'claims.json');assert len(c['claims'])==148
assert hashlib.sha256(json.dumps(c['claims'][:state['claim_count']],sort_keys=True,ensure_ascii=False).encode()).hexdigest()==state['old_claim_array_canonical_sha256']
assert [v['id'] for v in c['claims'][-10:]]==['SEM-'+str(n) for n in range(63,73)]
assert c['semantic_acceptance']['skin_current_failures']=={'skin-color':6,'skin-brightness':27,'skin-both':33}
assert not c['acceptance_complete'] and not c['semantic_acceptance']['A_phase_complete'] and not c['semantic_acceptance']['s26_full_domain_certificate_pass']
summary=read(O/'original-pso-summary-s26.json');assert len(summary['epochs'])==5 and summary['native_photo_count']==1
for v in summary['epochs']:
 assert not v['context_mismatches'] and not v['recreated_is_original_object']
 for k in ['fresh_vs_S5','retained_hydration','reconstructed_vs_retained']:assert v[k]['half_differing_components']==v[k]['max_abs']==v[k]['max_relative']==0
sample=summary['sampler_test'];assert sample['const_vs_runtime_half_differences']==0
assert sample['center_finite_input_bit_differences']==sample['center_signed_zero_only_bit_differences']==2051
assert sample['center_other_bit_differences']==sample['center_finite_input_nonfinite_output']==0
assert summary['sampler_matches']['@__air_sampler_state']['matching_own_explicit_declarations']==['pixel_linear']
assert summary['sampler_matches']['@__air_sampler_state.3']['matching_own_explicit_declarations']==['norm_linear']
ptr=summary['pointer_contract'];assert ptr['inputInfo_bytes']==0 and ptr['inputInfo_pointer']=='0x0' and ptr['capture_environment']=='unset'
assert not summary['actual_code_candidates']['final_original_backend_ISA_authenticated']
points=read(D/'s22-s24/skin33-uncertified-outer-s24.json')['points'];cross=read(D/'s22-s24/skin33-private-crosswalk-s24.json')
assert len(points)==len(cross)==33 and len({x['point'] for x in cross})==33
assert all(x['tight_global_lower'] is None and x['tight_global_upper'] is None and not x['full_domain_coverage_certified'] and not x['original_mask_changed'] and x['finite_error_upper_bound'] is None for x in points)
assert [x['id'] for x in summary['conditions']]==['C01','C02','C03','C04','C05'] and all(not x['met'] for x in summary['conditions'])
clean=read(O/'transport-cleanup-s22-s26-20261019.json');pre=read(O/'cleanup-preflight-s22-s26-20261019.json')
assert len(clean['temporary_branches_deleted'])==5 and len(clean['temporary_secret_names_deleted'])==2
assert all(not v['head'] and not v['base'] for v in pre['pr_all_states'].values())
assert not clean['other_refs_at_temporary_heads'] and not clean['remote_semantic_secrets_after'] and not clean['remote_semantic_private_releases_after']
assert clean['master_head_before']==clean['master_head_after']=='ce25aa34fe3dac8541730971d6957401fca3e1dc'
assert not clean['plaintext_people_uploaded'] and not clean['raw_capture_uploaded'] and not clean['whole_Apple_binary_uploaded'] and not clean['private_output_key_uploaded']
with (R/'errors.csv').open(newline='') as f:rows=list(csv.DictReader(f))
new=[v for v in rows if v['operator'].startswith(('semantic_s22_s26_','semantic_s24_','semantic_s26_'))];assert len(new)==68
with (E/'errors.csv').open(newline='') as f:pub=list(csv.DictReader(f))
assert pub==[v for v in rows if v['operator'].startswith('semantic')]
assert read(E/'claims.json')['claims']==[v for v in c['claims'] if v['id'].startswith('SEM-')]
assert read(E/'evidence-index.json')==read(D/'evidence-index.json')
assert read(E/'original-pso-summary-s26.json')==summary
assert read(E/'skin33-uncertified-outer-s24.json')==read(D/'s22-s24/skin33-uncertified-outer-s24.json')
assert shutil.disk_usage(R).free>=4_000_000_000
print(json.dumps({'audit_pass':True,'inverse_or_global_certificate_pass':False,'A_phase_complete':False,'acceptance_complete':False,'verified_archives':prior['verified_archives']+len(prov),'new_archives':len(prov),'new_successful_native_epochs':5,'distinct_photos_in_new_native_epochs':1,'preview_input_SHA_checks_reused':prior['preview_input_hash_checks'],'frozen_and_original_files_verified':prior['frozen_and_original_files_verified'],'historical_document_prefixes_preserved':len(state['files']),'old_claim_array_unchanged':True,'new_claims':10,'new_metric_rows':len(new),'evidence_references':len(read(D/'evidence-index.json')),'certified_tight_skin_points':0,'remaining_skin_failures':[6,27,33],'original_mask_pixels':186949,'root_free_bytes':shutil.disk_usage(R).free}))
