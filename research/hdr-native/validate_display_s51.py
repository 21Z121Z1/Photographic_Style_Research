"""Read-only five-photo receipts, with the original gates and masks preserved."""
from pathlib import Path
import argparse,json,hashlib,sys
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def validate(prior_path,suite_path,library):
    sys.path.insert(0,str(library))
    from hdr_display_progress import display_progress
    prior_path=Path(prior_path);suite_path=Path(suite_path);suite=json.loads(suite_path.read_text());parent=suite_path.parent;freeze=parent/'suite-freeze.json';f=json.loads(freeze.read_text())
    assert suite['completed'] and suite['completed_photos']==suite['required_new_photos']==4 and len(suite['rows'])==4
    assert sha(freeze)==suite['suite_freeze_sha256'] and suite['os_build']=='26A434' and suite['original_thresholds_or_masks_changed'] is False and suite['full_master_recomputed'] is False
    assert f['original_thresholds']=={'max_abs':1e-5,'PSNR_peak1_min_db':60,'relative_max':1e-3,'SDR_max_abs':0}
    assert f['total_master_download_bytes']==922251766 and len(f['cases'])==4
    cases=[(prior_path,'development')]+[(parent/c['photo']/'analysis-s47.json',c['role']) for c in f['cases']]
    expected={c['photo']:c for c in f['cases']};results=[];all_rows=[]
    for path,role in cases:
        a=json.loads(path.read_text());fp=path.parent/'freeze.json';cf=json.loads(fp.read_text());name=a['photo'];old=display_progress(path)
        assert old['master_and_preview_integrity']['pass'] and a['source_input_before']==a['source_input_after']
        assert a['original_inverse_masks_changed'] is False and a['physical_scene_verified'] is False and a['encoded_carrier_verified'] is False
        dependencies={Path(k).name:v for k,v in cf['source_sha256'].items()};assert dependencies==f['frozen_source_sha256']
        if name in expected:
            c=expected[name];assert a['shape']==c['shape'] and a['source_input_before']['master_EXR']==c['master_EXR_sha256'] and a['source_input_before']['original_photo']==c['source_sha256']
            deriv=f['derivations'][name];assert deriv['mathematical_processing_changed'] is False and deriv['inverse_binding_and_layout_substitutions_equal_original_prefix'] is True
            assert sha(path.parent/'derived-source.txt')==deriv['derived_script_sha256']
            embedded=next(r for r in suite['rows'] if r['photo']==name);same=dict(embedded);same.pop('role');assert same==a
        variants=[]
        for v,ov in zip(a['variants'],old['variants']):
            nr=v['native']['headrooms'];assert [r['headroom'] for r in nr]==[1,1.25,2,4,8];all_rows.extend(nr)
            assert len(nr)==5 and ov['original_inverse_mask_replaced'] is False
            end=nr[-1];h1=nr[0];defined=ov['defined_target_relative_and_PSNR_gate'] and end['target_endpoint_max_abs']<=1e-5
            variants.append({'tag':v['tag'],'representation_mask_coverage':v['coverage'],'defined_region_target_gate':defined,'whole_photo_target_gate':defined and v['valid_pixels']==v['all_pixels'],'source_inverse_mask_changed':False,'saved_logmap_max_relative':ov['saved_f32_map_max_relative'],'native_target_max_abs':end['target_endpoint_max_abs'],'native_target_max_relative':end['target_endpoint_max_relative'],'native_target_PSNR_peak1_db':end['target_endpoint_PSNR_peak1_db'],'unencoded_native_h1_max_abs':h1['unencoded_SDR_h1_max_abs'],'unencoded_native_h1_max0':h1['unencoded_SDR_h1_max_abs']==0,'new_encoded_ImageIO_SDR_max0_certified':False})
        results.append({'photo':name,'role':role,'shape':a['shape'],'display_exposure_intent':dict(a['display_intent'],classification='假设: creative display policy, not physical exposure'),'chromaticity_max_abs':a['render_chromaticity_max_abs'],'frozen_master_and_preview_SHA_unchanged':True,'variants':variants,'evidence':{'analysis':str(path),'analysis_sha256':sha(path),'freeze_sha256':sha(fp)}})
    names=[r['photo'] for r in results];assert len(names)==len(set(names))==5 and set(names)=={'IMG_2600','IMG_2604','IMG_2608','IMG_0032','IMG_0033'}
    assert sum(r['role']=='display-formula-holdout' for r in results)==2 and len(all_rows)==50
    forward_gate=all(x['nonfinite_components']==0 and x['formula_max_abs']<=1e-5 and (x['formula_PSNR_peak1_db']=='inf' or x['formula_PSNR_peak1_db']>=60) for x in all_rows)
    finite=[x['formula_PSNR_peak1_db'] for x in all_rows if x['formula_PSNR_peak1_db']!='inf']
    return {'os_build':'26A434','five_photo_frozen_display_protocol_complete':True,'holdouts':2,'holdout_scope':f['holdout_scope'],'original_formula_modules_SHA_unchanged':True,'new_native_formula_comparisons':40,'total_including_prior_S47_native_formula_comparisons':50,'native_float_formula_gate':forward_gate,'native_float_formula_max_abs':max(x['formula_max_abs'] for x in all_rows),'native_float_formula_min_PSNR_peak1_db':min(finite) if finite else 'inf','photos':results,'all_whole_photo_targets_accepted':all(v['whole_photo_target_gate'] for r in results for v in r['variants']),'new_encoded_native_carrier_accepted':False,'scene_referred_accepted':False,'skin_33_tight_hulls_accepted':False,'physical_RAW_and_same_frame_curves_pending':True,'old_precision_thresholds':f['original_thresholds'],'all_original_inverse_masks_preserved':True,'relative_denominator_floor':1e-6,'A_phase_complete':False,'acceptance_complete':False,'goal_status':'active','evidence':{'S47_analysis_sha256':sha(prior_path),'S51_analysis_sha256':sha(suite_path),'S51_suite_freeze_sha256':sha(freeze),'validator_sha256':sha(Path(__file__))}}
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--s47',type=Path,required=True);parser.add_argument('--s51',type=Path,required=True);parser.add_argument('--library',type=Path,required=True);parser.add_argument('--out',type=Path,required=True);a=parser.parse_args();value=validate(a.s47,a.s51,a.library)
    with a.out.open('x') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({k:value[k] for k in ['five_photo_frozen_display_protocol_complete','native_float_formula_gate','native_float_formula_max_abs','native_float_formula_min_PSNR_peak1_db','all_whole_photo_targets_accepted','acceptance_complete']}))
