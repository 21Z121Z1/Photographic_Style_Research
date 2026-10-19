"""Read-only incremental audit; never rerun image/native calculations locally."""
from pathlib import Path
import json,hashlib,subprocess,sys,csv
R=Path(sys.argv[1]).resolve();D=R/'semantic-20261018';P=R/'repo';O=D/'s27';E=P/'research/semantic-styles/evidence'
def read(p):return json.loads(p.read_text())
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
state=read(O/'pre-delivery-state.json');before=read(O/'preflight.json');checks=[]
for row in state['files']:
 p=R/row['file']
 with p.open('rb') as f:assert hashlib.sha256(f.read(row['size'])).hexdigest()==row['sha256'],row['file']
 checks.append({'prefix_unchanged':row['file'],'bytes':row['size']})
for path,fact in before['files'].items():assert sha(Path(path))==fact['sha256'] and Path(path).stat().st_size==fact['size'],path
for path,n,key in [(R/'claims.json',state['old_claim_count'],'old_claim_array_sha256'),(E/'claims.json',state['public_claim_count'],'public_claim_array_sha256')]:
 obj=read(path);old=obj['claims'][:n];assert hashlib.sha256(json.dumps(old,sort_keys=True,ensure_ascii=False).encode()).hexdigest()==state[key];assert len(obj['claims'])==n+11 and not obj['acceptance_complete']
 assert [c['id'] for c in obj['claims'][n:]]==['SEM-'+str(i) for i in range(73,84)]
 for c in obj['claims'][n:]:
  assert c['status'] in obj['status_values']
  for ev in c['evidence']:
   p=R/ev['file'];assert p.is_file() and sha(p)==ev['sha256'],ev['file']
 # All pre-existing public metadata (including gates) must remain identical.
 if path==E/'claims.json':
  old_obj=json.loads(subprocess.check_output(['git','show','b3e5ef8d7cff90f31a4e0c8f072db8658559c833:research/semantic-styles/evidence/claims.json'],cwd=P))
  for k,v in old_obj.items():
   if k not in ['claims','updated_utc']:assert obj[k]==v,k
for rid in ['39227962537','39228892493']:
 base=D/'runs'/rid;meta=read(base/'archive-audit.json');assert meta['gpg_returncode']==0 and not meta['manifest_failures'] and sha(base/'artifact.zip')==meta['zip_sha256']
 assert sha(base/'selected/out/manifest.json')==meta['manifest_sha256']
 for row in meta['files']:
  if row['materialized']:assert sha(base/'selected/out'/row['path'])==row['sha256']
native=read(O/'tone-retarget-s27.aggregate.json');quant=read(E/'serialized-map-s28.json');field=read(E/'spatial-field-s28.json');cleanup=read(O/'transport-cleanup-s27-s28.json')
assert native['native_hydration']['half_differing_components']==0 and native['context_mismatches']==[] and native['source_unchanged'] and native['preview_sha_failures']==0 and native['preview_sha_checks']==10
assert len(native['rows'])==8
for row in native['rows']:
 assert row['native']['changed_bytes_outside_target']==0
 if row['operator']=='local-neutral':assert [c['offset'] for c in row['native']['target_fields']]==[620,624] and row['representation_positive_pixels']==186949
 if row['operator'] in ['ui-tone-reset','opposite-ui-tone']:assert row['native']['vs_actual_UI_capture_S5']['half_differing_components']==0 and row['native']['matches_actual_UI_capture_RGBA']
assert not native['naive_composition_same_space_verified'] and not native['acceptance_complete']
assert quant['float32_serialized_RGB_gain_map']['max_relative']<=1e-3 and quant['eight_bit_log2_RGB_scalar_quantizer']['metrics']['max_relative']>1e-3
assert field['queries']==4224 and field['interval_misses']==0 and field['guaranteed_candidate_violations']==0 and not field['full_consumer_domain_certified']
assert sha(P/'research/semantic-styles/spatial_curve_retarget.py')==field['source_sha256']
fig=read(O/'figure-provenance-s27.json');assert sha(E/'brightening-and-local-curves-s27.png')==fig['figure_sha256'] and not fig['sample_actual_curves_available']
assert cleanup['all_runs_completed_archived_verified'] and cleanup['all_runner_plaintext_cleanup_success'] and len(cleanup['temporary_secrets_deleted'])==3 and len(cleanup['temporary_branches_deleted'])==2 and not cleanup['secrets_after'] and not cleanup['private_releases_after'] and cleanup['master_before']==cleanup['master_after']==before['master']
new=read(O/'new-metric-rows.json');assert new['count']==92
for path in [R/'errors.csv',E/'errors.csv']:
 rows=list(csv.reader(path.open()));assert len(rows[-92:])==92
 for a,b in zip(rows[-92:],new['rows']):assert a==list(map(str,b))
print(json.dumps({'scope':'Incremental evidence audit; no image or native execution','pass':True,'old_document_csv_prefixes':len(checks),'old_claims_unchanged':state['old_claim_count'],'new_claims':11,'new_metric_rows':92,'verified_new_archives':2,'frozen_original_hashes':len(before['files']),'preview_sha_checks':10,'native_control_half_differences':0,'spatial_scalar_queries':4224,'eight_bit_log_gain_meets_1e3':False,'actual_camera_curve_identified':False,'original_consumer_hull_certified':False,'acceptance_complete':False},ensure_ascii=False))
