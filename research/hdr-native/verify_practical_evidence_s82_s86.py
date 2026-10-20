"""Check retained hashes and numerical records without decoding photographs.

The prior streaming GPG verification is an archived receipt, not repeated here.
Use the memory-limited local wrapper; native/image work remains on macOS.
"""
from pathlib import Path
import argparse,hashlib,json,subprocess,zipfile,math

def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()

def main():
 parser=argparse.ArgumentParser();parser.add_argument('archives',type=Path);args=parser.parse_args()
 d=Path(__file__).resolve().parent;repo=d.parents[1]
 stages=[('s82',39407894040),('s84',39403808066),('s85',39408560663)]
 inv=json.loads((d/'evidence/s86/run/archive-receipt.json').read_text());stages.append(('s86',inv['run_id']))
 facts=[]
 for stage,run in stages:
  e=d/'evidence'/stage/'run';r=json.loads((e/'archive-receipt.json').read_text());assert r['run_id']==run and r['os_build']=='26A434'
  assert r['source_hashes_match_commit']and r['original_ZIPs_preserved']
  public=next(x for x in r['artifacts']if'aggregate'in x['name'])
  for a in r['artifacts']:
   p=args.archives/str(run)/('artifact-'+str(a['artifact_id'])+'.zip');assert p.stat().st_size==a['ZIP_bytes']and sha(p)==a['ZIP_sha256']
  with zipfile.ZipFile(args.archives/str(run)/('artifact-'+str(public['artifact_id'])+'.zip'))as z:
   m=json.loads(z.read('manifest.json'));assert m['run_id']==str(run)and m['commit']==r['source_commit']
   assert {x for x in z.namelist()if not x.endswith('/')}=={'manifest.json',*(x['path']for x in m['files'])}
   for x in m['files']:
    raw=z.read(x['path']);assert len(raw)==x['size']and hashlib.sha256(raw).hexdigest()==x['sha256']and sha(e/x['path'])==x['sha256']
  freeze=json.loads((e/'freeze.json').read_text())
  for name,expected in freeze['source_sha256'].items():
   assert name.startswith('research/hdr-native/')or name=='tools/heif_dump.py'
   raw=subprocess.check_output(['git','show',r['source_commit']+':'+name],cwd=repo);assert hashlib.sha256(raw).hexdigest()==expected
  private=r['private_contact_verification'];assert private['GPG_returncode']==0 and private['all_manifest_members_verified']>0 and 'GOODMDC'in private['event_names_only']and private['images_decoded_or_written_in_VM']is False
  a=json.loads((e/'analysis.json').read_text());assert not a['engineering_accepted']and not a['A_phase_complete']and not a['acceptance_complete']
  assert all(x['before_sha256']==x['after_sha256']for x in a['preview_input_checks'])
  if stage=='s82':
   assert len(a['rows'])==15 and len(a['preview_input_checks'])==21 and a['input_files_before_after_SHA_unchanged']
   assert {(x['operator'],x['strength'])for x in a['rows']}=={(op,s)for op in ['skin-color','skin-brightness','skin-both']for s in [0,.25,.5,.75,1]}
   for x in a['rows']:
    assert x['background_max_abs_change']==0 and x['background_pixels']==187224 and x['ratio_valid_pixels']==196607
    assert x['all_frame']['finite_pixels']==196608 and x['legacy_eligible']['finite_pixels']==186949
   assert not a['new_native_pixel_execution']and not a['oracle_error_selected_S15_S16_patch_used']
  else:
   assert a['all_completed']and a['full_resolution']and a['shape']==[4284,5712,3]
   for x in a['rows']:
    s=x['ImageIO_full_SDR'];assert s['decoded_sdr_max0_verified']and s['decoded_sdr_max_abs']==0 and s['changed_active_bytes']==0
    assert s['rows_checked']==4284 and s['active_SHA_original']==s['active_SHA_carrier']
    assert x['identity']['primary_coded_and_properties_identical']and x['identity']['primary_descendant_payloads_checked']==46
    if stage!='s84':
     for name in ['CI_SDR_vs_original','headroom1_native_equation','headroom2_native_equation','headroom8_native_equation']:
      q=x['metrics'][name];assert q['components']==73410624 and q['nonfinite_components']==0
     assert x['metrics']['CI_SDR_vs_original']['max_abs']==0
   if stage!='s84':
    l=a['layout_qualification'];assert l['layout_qualified']and l['fixed_storage_geometry_vs_full']['max_abs']==0 and l['full_vs_source_s44']['max_abs']==0
   if stage=='s86':assert len(a['rows'])==1 and a['rows'][0]['bits']==10 and a['rows'][0]['encoded_gain_colr']['matrix_coefficients']==6
  facts.append({'stage':stage,'run_id':run,'public_manifest_members':len(m['files']),'all_ZIP_and_public_member_SHA_verified':True,'source_SHA_at_original_commit_verified':True,'stored_GPG_receipt_checked_not_repeated':True})
 assert not json.loads((d/'evidence/s84/comparison-status.json').read_text())['S84_HDR_gain_CI_comparison_and_native_preview_panels']['qualified']
 assert json.loads((d/'evidence/s82/closure.json').read_text())['temporary_secret_release_tag_branch_absent']
 print(json.dumps({'metadata_only':True,'images_decoded':False,'stages':facts,'engineering_accepted':False,'A_phase_complete':False,'acceptance_complete':False}))

if __name__=='__main__':main()
