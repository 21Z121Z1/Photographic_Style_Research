"""Keep transport evidence separate from inverse/scene acceptance.

The legacy validate.py and its frozen gates are never edited by this tool.
No missing photo/oracle evidence can become a pass because a synthetic probe ran.
"""
import argparse,json,math,hashlib
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from hdr_operator_progress import operator_progress
def sha(path):
 with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def validate(s29_path,s30_path=None,s31_path=None,s32_path=None,*,rgb_host=None,photo_suite=None):
 s29=json.loads(Path(s29_path).read_text());s30=json.loads(Path(s30_path).read_text()) if s30_path else None
 observations=[h['reference_vs_native'] for r in s29['rows'] for h in r.get('headrooms',[])]
 assert len(observations)==35 and s29['os_build']=='26A434'
 original_precision={'max_abs':1e-5,'PSNR_peak1_db_min':60,'inverse_or_transport_relative_max':1e-3}
 synthetic_transport_pass=all(x['max_abs']<=1e-5 and (x['PSNR_peak1_db']=='inf' or x['PSNR_peak1_db']>=60) for x in observations)
 status={
  'legacy_acceptance_complete':False,
  'HDR_render_transport':{
   'native_headroom_equation_synthetic_35':{'pass':synthetic_transport_pass,'status':'已验证数值','max_abs':max(x['max_abs'] for x in observations),'min_PSNR_peak1_db':min(x['PSNR_peak1_db'] for x in observations if x['PSNR_peak1_db']!='inf')},
   'automatic_writer_preserves_original_SDR':{'pass':s29['original_SDR_preservation_pass'],'status':'已验证数值','scope':'Measured writer failure; not a promise from its successful return code'},
   'five_photos_full_resolution_two_post_freeze_holdouts':{'pass':False,'status':'可交给macOS runner','photos_in_new_S29_S30_suite':0,'required':5,'holdouts_required':2},
   'new_target_original_SDR_ImageIO_full_max0':{'pass':False,'status':'可交给macOS runner','scope':'Old carriers retain their earlier passes; this new target has no new lossless-splice native receipt'},
   'new_target_encoded_RGB_relative_1e3':{'pass':False,'status':'可交给macOS runner','scope':'Synthetic codec failures are retained; no threshold or mask change'},
   'actual_HDR_screen_and_viewing_environment':{'pass':False,'status':'待实机解决'}},
  'physical_scene_recovery':{
   'global_only_local_only_separate':{'pass':False,'status':'可交给macOS runner','scope':'Conditional curve sets / known-input counterfactuals available; actual full capture factorization not certified'},
   'skin_33_global_tight_hulls':{'pass':False,'status':'可交给macOS runner','scope':'Original C01-C05 contracts and mask unchanged; no local sweep substituted for a proof'},
   'same_frame_camera_j_curves_and_pixel_EV':{'pass':False,'status':'待实机解决'},
   'Studio_original_stats':{'pass':False,'status':'待实机解决'},
   'paired_RAW_EV_IMG_2679_IMG_2408':{'pass':False,'status':'待实机解决'}},
  'scope':'Independent goal progress; synthetic transport checks do not certify an inverse, scene radiance, five-photo suite or original-SDR preservation',
  'old_precision_thresholds':original_precision,
  'evidence':{'S29':{'path':str(s29_path),'sha256':sha(s29_path)}}}
 if s30:
  assert s30['os_build']=='26A434'
  status['evidence']['S30']={'path':str(s30_path),'sha256':sha(s30_path)}
  unencoded=[x['reference_vs_native'] for r in s30['rows'] for x in r.get('unencoded_headrooms',[])]
  verified=len(unencoded)==70 and all(x.get('gate') for x in unencoded)
  status['HDR_render_transport']['explicit_RGB_unencoded_native_synthetic']={'pass':verified,'status':'已验证数值','native_comparisons':len(unencoded),'required_comparisons':70,'successful_writer_cases':sum(r['native_returncode']==0 for r in s30['rows']),'total_writer_requests':len(s30['rows'])}
 if s31_path:
  s31=json.loads(Path(s31_path).read_text());assert s31['os_build']=='26A434'
  status['evidence']['S31']={'path':str(s31_path),'sha256':sha(s31_path)}
  good=[r for r in s31['rows'] if r['native_returncode']==0]
  status['HDR_render_transport']['preserved_SDR_synthetic_direct_ISO_8_10bit']={'pass':len(good)==10 and all(r['SDR_native_max_abs']==0 and r['identity']['primary_coded_and_properties_identical'] for r in good),'status':'已验证数值','cases':len(good),'scope':'Synthetic256x128 direct gain items; not the five full-size photographs'}
  status['HDR_render_transport']['explicit_ISO_synthetic_target']={'pass':len(good)==15 and all(r['encoded_target_gate'] for r in good),'status':'已验证数值','native_readback_success':len(good),'requests':len(s31['rows']),'scope':'Failure retained: native code-domain mismatch and twelve-bit nil; no inverse conclusion'}
 if s32_path:
  s32=json.loads(Path(s32_path).read_text());assert s32['os_build']=='26A434'
  status['evidence']['S32']={'path':str(s32_path),'sha256':sha(s32_path)}
  cases=[{'matrix':r['matrix'],'bits':r['bits'],'native_returncode':r['native_returncode'],'native_aux_code_max_abs':r.get('native_aux_vs_integer_code_max_abs'),'target_relative_max':r.get('native_HDR_vs_target',{}).get('max_relative'),'headroom_comparisons':len(r.get('headrooms',[]))} for r in s32['rows']]
  status['HDR_render_transport']['matrix_diagnosis']={'pass':False,'status':'已验证数值','scope':'Single fixture diagnosis cannot pass target acceptance','cases':cases}
 status['HDR_native_target_accepted']=all(g['pass'] for g in status['HDR_render_transport'].values())
 status['scene_referred_accepted']=all(g['pass'] for g in status['physical_scene_recovery'].values())
 status['acceptance_complete']=status['HDR_native_target_accepted'] and status['scene_referred_accepted'] and status['legacy_acceptance_complete']
 status['goal_status']='active'
 if rgb_host or photo_suite:status['operator_progress']=operator_progress(rgb_host=rgb_host,photo_suite=photo_suite)
 return status
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--s29',required=True,type=Path);p.add_argument('--s30',type=Path);p.add_argument('--s31',type=Path);p.add_argument('--s32',type=Path);p.add_argument('--rgb-host',type=Path);p.add_argument('--photo-suite',type=Path);p.add_argument('--out',required=True,type=Path);a=p.parse_args();r=validate(a.s29,a.s30,a.s31,a.s32,rgb_host=a.rgb_host,photo_suite=a.photo_suite)
 # Never replace a historical receipt.
 with a.out.open('x') as f:json.dump(r,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'acceptance_complete':r['acceptance_complete'],'goal_status':r['goal_status'],'headroom':r['HDR_render_transport']['native_headroom_equation_synthetic_35']},ensure_ascii=False))
