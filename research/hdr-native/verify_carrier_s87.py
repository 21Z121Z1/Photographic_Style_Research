"""Metadata/hash verification of S87, including its missing runner manifest."""
from pathlib import Path
import argparse,json,hashlib,zipfile,subprocess,math

def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()

def main():
 a=argparse.ArgumentParser();a.add_argument('archives',type=Path);args=a.parse_args();d=Path(__file__).resolve().parent;repo=d.parents[1];e=d/'evidence/s87/run';r=json.loads((e/'archive-receipt.json').read_text());m=json.loads((e/'derived-archive-inventory.json').read_text())
 assert r['conclusion']=='failure'and r['runner_public_manifest_missing']and r['all_public_manifest_members_SHA_verified']==0
 assert r['derived_local_inventory_not_runner_manifest']and r['public_original_members_hashed_from_API_verified_ZIP']==33 and m['runner_manifest_missing']
 for art in r['artifacts']:
  p=args.archives/str(r['run_id'])/('artifact-'+str(art['artifact_id'])+'.zip');assert p.stat().st_size==art['ZIP_bytes']and sha(p)==art['ZIP_sha256']
 public=next(x for x in r['artifacts']if'aggregate'in x['name'])
 with zipfile.ZipFile(args.archives/str(r['run_id'])/('artifact-'+str(public['artifact_id'])+'.zip'))as z:
  assert'manifest.json'not in z.namelist()and set(z.namelist())=={x['path']for x in m['files']}
  for x in m['files']:
   raw=z.read(x['path']);assert len(raw)==x['size']and hashlib.sha256(raw).hexdigest()==x['sha256']and sha(e/x['path'])==x['sha256']
 f=json.loads((e/'freeze.json').read_text())
 for name,expected in f['source_sha256'].items():
  raw=subprocess.check_output(['git','show',r['source_commit']+':'+name],cwd=repo);assert hashlib.sha256(raw).hexdigest()==expected
 a=json.loads((e/'analysis.json').read_text());assert a['all_completed']and a['real_photos_completed']==5 and a['recipe_holdouts_completed']==2
 cases=[]
 for row in a['rows']:
  assert row['returncode']==0 and row['all_completed']and row['layout_qualified']and row['source_SHA_unchanged']and row['preview_input_checks_unchanged']
  q=json.loads((e/(row['photo']+'-analysis.json')).read_text());b=q['rows'][0];s=b['ImageIO_full_SDR'];pixels=math.prod(q['shape'][:2])
  assert s['decoded_sdr_max0_verified']and s['decoded_sdr_max_abs']==0 and s['changed_active_bytes']==0 and s['active_SHA_original']==s['active_SHA_carrier']
  assert s['rows_checked']*s['original']['width']==pixels and b['encoded_gain_colr']['matrix_coefficients']==6 and b['bits']==10
  assert b['identity']['primary_coded_and_properties_identical']and q['layout_qualification']['fixed_storage_geometry_vs_full']['max_abs']==0
  assert b['metrics']['CI_SDR_vs_original']['max_abs']==0
  for h in [1,2,8]:
   v=b['metrics'][f'headroom{h}_native_equation'];assert v['nonfinite_components']==0 and v['components']==pixels*3 and v['max_abs']<=1e-5 and(v['PSNR_peak1_dB']=='inf'or v['PSNR_peak1_dB']>=60)
  cases.append({'photo':row['photo'],'shape':q['shape'],'integer_SDR_max0':True,'legacy_encoded_target_gate':b['old_strict_target_gate']})
 g=r['private_contact_verification'];assert g['GPG_returncode']==0 and g['all_manifest_members_verified']==37 and 'GOODMDC'in g['event_names_only']
 assert not a['engineering_accepted']and not a['A_phase_complete']and not a['acceptance_complete']
 print(json.dumps({'metadata_only':True,'run_id':r['run_id'],'run_conclusion':'failure','failure_scope':'90KB aggregate cap only; original public manifest absent','original_ZIP_and_33_public_members_verified':True,'stored_GPG_receipt_checked_not_repeated':True,'photos':cases,'full_SDR_zero_photo_count':5,'native_actual_code_headroom_formula_photo_count':5,'engineering_accepted':False,'A_phase_complete':False,'acceptance_complete':False}))

if __name__=='__main__':main()
