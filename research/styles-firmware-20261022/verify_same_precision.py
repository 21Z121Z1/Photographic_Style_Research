"""Read-only S26 evidence checks, except writing one NEW sanitized receipt."""
from pathlib import Path
import argparse,json,re,subprocess
import numpy as np
from baseline_archive import sha,encoded
from context_color_api import BoundCatalog,load

ROOT=Path(__file__).parent;E=ROOT/'evidence';REPO=ROOT.parents[1]


def verify(output:Path):
    if output.exists():raise FileExistsError(output)
    replay=load(E/'first-scene-v3-replay-s26a.json');comparison=load(E/'same-precision-comparison-s26c.json');classes=load(E/'changed-class-queries-s26c2.json');bright=load(E/'bright137-local-s26d.json');p=E/'model-precision-v3-s25c6.json';plan=E/'color-partition-s22a.json';profile=load(p)
    first=BoundCatalog(E/'complete-context-s15a.json',p,plan,E/'first-context-catalog-v3-s26c.json',sha(E/'first-context-catalog-v3-s26c.json'));second=BoundCatalog(E/'second-context-s25a.json',p,plan,E/'context-catalog-s25e.json',sha(E/'context-catalog-s25e.json'));a=first.checked();b=second.checked()
    assert a[0].precision_contract_sha256==b[0].precision_contract_sha256==sha(p)
    assert replay['status']=='passed_thirteen_saved_first_scene_v3_points'and replay['new_point_calls']==13 and replay['native_calls']==0
    assert all(not row['differences']and not row['point']['pixel_unknowns']and row['point']['writer_known']for row in replay['rows'])
    components=sum(s['components']for row in replay['rows']for s in row['point']['observations'].values());assert components==25194
    chunks=sorted(E.glob('scan-[0-9][0-9][0-9]-s26b.json'));scans=[load(f)for f in chunks]
    assert [r['state_id']for d in scans for r in d['rows']]==list(range(146))
    assert all(d['native_calls']==0 and not d['target_read']for d in scans)
    assert all(r['writer_known']for d in scans for r in d['rows'])
    assert comparison['unique_writer_counts']=={'first':140,'second':145}
    assert comparison['changed_class_state_ids']==[4,5,7,8,9,31,32,71,72]
    assert len(comparison['removed_pairs'])==6 and not comparison['added_pairs']
    assert comparison['context_swap_rejected']and len(comparison['cross_context_target_rejections'])==2
    assert comparison['same_state_writer_arrays_differ_between_contexts']==146
    assert not classes['first_scene_legacy_vs_v3_writer_changed_states']
    legacy={r['state_id']:r for f in E.glob('scan-[0-9][0-9][0-9]-s22b.json')for r in load(f)['rows']}
    assert len(legacy)==146 and all(legacy[i]['writer_half_bits']==a[3][i]['writer_half_bits']for i in range(146))
    assert bright['before_half_bit_mismatches']==1 and bright['after_local_half_bit_mismatches']==0
    assert not bright['default_pixel_bright_modified']and not bright['v3_precision_contract_modified']
    assert bright['remaining_original_bright_differences']=={'S25_targets':6,'S25_boundaries':18}
    assert bright['native_or_full_point_forward_calls']==0 and len(bright['cast16_and_multiple_parameter_rejections'])==2
    assert all(sha(ROOT/n)==h for n,h in profile['model_source_sha256'].items())
    assert sha(ROOT/'context_color_api.py')==profile['inverse_API_sha256']
    prior=load(E/'verification-s25.json');prior_sources_changed=[n for n,h in prior['current_source_sha256'].items()if sha(ROOT/n)!=h];assert prior_sources_changed==['bound_validation.py']
    prior_evidence={n:sha(E/n)==h for n,h in prior['evidence_sha256'].items()};assert all(prior_evidence.values())
    historical=load(E/'context-analysis-s25e.json');assert historical['old_unique_writer_outputs']==140 and historical['old_context_historical_collision_groups']==comparison['collision_groups']['first']
    old_cost=load(E/'stage-audit-s25h2.json')['full_point_cost'];assert old_cost['total_recorded_plus_uninstrumented_range']==[162,163]
    bindings={}
    for f in sorted(E.glob('*binding*s26*.json')):
        if f.name.endswith('.pre.json'):continue
        d=load(f);pre=f.with_name(f.stem+'.pre.json');log=f.with_suffix('.log');assert sha(pre)==d['pre_run_binding_sha256']and sha(log)==d['log_sha256'];assert d['exit_code']==0 and d['source_unchanged_during_command']and d['inputs_unchanged_during_command'];bindings[f.stem]={'pre_sha256':sha(pre),'post_sha256':sha(f),'raw_log_sha256':sha(log),'exit_code':0,'source_and_inputs_unchanged':True,'elapsed_seconds':d['elapsed_seconds']}
    test=(E/'test-binding-s26e.log').read_text();m=re.search(r'Ran (\d+) tests in ([\d.]+)s\n\nOK',test);assert m and int(m[1])==14
    for f in E.glob('*s26*'):
        if not f.is_file():continue
        assert b'\0'not in f.read_bytes()and re.search(rb'/Users/[A-Za-z0-9._-]+/',f.read_bytes())is None
        if f.suffix=='.json':load(f)
    assert not subprocess.check_output(['git','diff','--name-only','HEAD','--',str(E)],cwd=REPO,text=True).strip()
    repo={'base_HEAD':subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),'branch':subprocess.check_output(['git','branch','--show-current'],cwd=REPO,text=True).strip(),'initial_remote_branch':'08b3c444eeba269a533fa1e93ec3895cb7ed88de','master':'ce25aa34fe3dac8541730971d6957401fca3e1dc','reference_vm_native':'2132e1fcb6505e601d006b5ca1afde04e36ae649'}
    result={'scope':'S26 exact same-v3 two-context comparison after saved first-scene replay and actual first-catalog rebuild','status':'passed_bounded_same_precision_model_comparison_and_local_saved_node_only','repository':repo,'precision_contract_sha256':sha(p),'precision_API_and243_model_source_hashes_unchanged':True,'first_context_sha256':a[0].complete_context_sha256,'second_context_sha256':b[0].complete_context_sha256,'catalog_sha256':comparison['catalog_sha256'],'first_scene_saved_point_replays':13,'saved_point_half_components':components,'saved_point_half_bit_mismatches':0,'new_first_scene_catalog_model_forwards':146,'first_scene_model_scan_seconds':sum(d['elapsed_seconds']for d in scans),'S26_total_complete_point_forwards':159,'S26_new_original_kernel_calls':0,'S26_new_compilations':0,'old8_original_boundaries_rerun':False,'old_catalog_relabelled':False,'first_fresh_catalog_vs_legacy_writer_bit_differences':0,'unique_writer_counts':comparison['unique_writer_counts'],'collision_groups':comparison['collision_groups'],'changed_class_state_ids':comparison['changed_class_state_ids'],'removed_collision_pairs':comparison['removed_pairs'],'added_collision_pairs':comparison['added_pairs'],'same_state_writer_arrays_differ_between_contexts':146,'cross_context_target_rejections':comparison['cross_context_target_rejections'],'candidate_changes':{k:{'states':q['model_matching_state_ids'],'candidate_union':q['candidate_union'],'f32_population':q['found_f32_population']}for k,q in classes['changed_class_queries'].items()},'S25_prose_erratum':{'previous_incorrect_text':'old first scene145 writer and only[0,1] collision','correct_old_evidence':{'unique_writers':140,'groups':historical['old_context_historical_collision_groups']},'original_evidence_sha256':sha(E/'context-analysis-s25e.json'),'previous_report_sha256':prior['document_sha256']['PROGRESS-S25.zh-CN.md'],'corrected_report_sha256':sha(ROOT/'PROGRESS-S25.zh-CN.md'),'historical_commit_and_raw_data_unchanged':True},'bright137':{'authentic_diagnostic_sha256':bright['saved_diagnostic_sha256'],'before':1,'after_scoped_node':0,'domain':bright['domain'],'default_pipeline_modified':False,'remaining_bright_differences':bright['remaining_original_bright_differences'],'cast16_and_multiple_free_fields':'prohibited; exact scope guard and Context cast16 refusal tested','new_native_or_complete_point_calls':0},'S25_original_cost_limitation_retained':old_cost,'prior_source_changes_only_stage_binding_metadata':prior_sources_changed,'prior_S25_evidence_SHA_unchanged':prior_evidence,'tests':{'count':14,'unittest_seconds':float(m[2]),'result':'OK','raw_output_sha256':sha(E/'test-binding-s26e.log'),'new_complete_point_or_native_calls':0},'pre_execution_bindings':bindings,'current_source_sha256':{f.name:sha(f)for f in sorted(ROOT.glob('*.py'))},'document_sha256':{n:sha(ROOT/n)for n in ['PROGRESS-S26.zh-CN.md','PROGRESS-S25.zh-CN.md','README.zh-CN.md']},'evidence_sha256':{f.name:sha(f)for f in sorted(E.glob('*s26*'))if f.is_file()},'no_IR_or_binary_created_or_uploaded':True,'no_new_download_mount_cache_search_private_media_or_process_retry':True,'remaining':['new changed collision groups have model coverage only, no original host verification;140 states per scene not original-host exhaustive','default bright6+18 residuals remain; saved node137 is not a general caller or neighborhood fix','set unknowns and nine-field missing-cache software bridge remain','historical S21/S22 raw IR cause unknown; originalGPU/UI/real paired frames/IMG_2810 build/unknown-source inverse unverified','S19 recovery and S25 failed-v2 cost/source retention limits preserved']}
    output.write_bytes(encoded(result));print(json.dumps({'status':result['status'],'same_precision':True,'unique_writers':result['unique_writer_counts'],'changed_classes':9,'complete_point_forwards':159,'native_calls':0,'tests':14,'S25_prose_erratum':'corrected, original evidence preserved'}));return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path);a=p.parse_args();verify(a.output)
