"""Check S27 existing-data joint results and write one NEW evidence receipt."""
from pathlib import Path
import argparse,json,re,subprocess
from baseline_archive import sha,encoded
from context_color_api import load
from joint_color_api import V3,FIELD,VERSION,ACCEPTED
from raw_f32_sets import Interval,population,same_members

ROOT=Path(__file__).parent;E=ROOT/'evidence';REPO=ROOT.parents[1]


def verify(output):
    if output.exists():raise FileExistsError(output)
    result_files={n:E/f'joint-result-{n}-s27b2.json'for n in ['state7','platform','incompatible']};results={n:load(p)for n,p in result_files.items()};a=results['state7'];z=results['platform'];bad=results['incompatible'];audit=load(E/'joint-example-audit-s27c2.json');current_api_sha=sha(ROOT/'joint_color_api.py');interval_sha=sha(ROOT/'raw_f32_sets.py')
    for name,r in results.items():
        assert r['shared_parameter_declaration']['same_raw_f32_across_contexts']is True and r['shared_parameter_declaration']['field_definition']==FIELD
        assert tuple(r['contract']['version'])==VERSION and r['contract']['precision_sha256']==V3 and r['contract']['domain']==[0,0x3ec00000]
        assert r['input_files_unchanged_during_solve']and r['new_forward_or_original_kernel_calls']==0 and r['joint_class_acceptance']=='model_only'
        assert not r['single_target_invalidity_claim']and not r['nearest_fallback_used']and not r['unique_parameter_claim']
        assert r['joint_API_source_sha256']==current_api_sha and r['raw_interval_source_sha256']==interval_sha
        assert all(o['catalog_provenance']['mode']=='exact accepted full catalog SHA'and not o['catalog_provenance']['new_model_rows_accepted']for o in r['observations'])
        for field,count in [('confirmed_model_joint_candidates','confirmed_model_f32_population'),('possible_joint_candidates','possible_f32_population'),('unresolved_joint_candidates','unresolved_joint_f32_population')]:assert population(tuple(Interval.read(d)for d in r[field]))==r[count]
        for key,expected in r['file_inputs_sha256'].items():assert sha(E/key.split(':',1)[1])==expected
        assert sha(result_files[name])==audit['result_sha256'][name]
    assert a['confirmed_joint_interface_state_ids']==[7]and a['confirmed_model_f32_population']==a['possible_f32_population']==860159
    assert a['observations'][0]['query']['model_matching_state_ids']==[7,8,9]and a['observations'][0]['known_f32_population']==2400255
    assert a['information']['joint_equal_to_single_possible_sets']==['second']and a['information']['extra_population_reduction_beyond_smallest_single']==0 and not a['information']['strictly_smaller_than_every_single_possible_set']
    assert a['information']['reduction_from_each_single_possible_population']=={'first':1540096,'second':0}
    interval=a['possible_joint_candidates'][0];assert not interval['lower_closed']and not interval['upper_closed']and interval['first_f32_bits']==0x3d961001 and interval['last_f32_bits']==0x3da32fff
    assert z['confirmed_joint_interface_state_ids']==[0,1]and z['possible_f32_population']==1018499073
    assert bad['possible_joint_candidates']==[]and bad['confirmed_model_joint_candidates']==[]and bad['all_individual_possible_sets_nonempty']and not bad['information']['information_gain_interpretation_applicable']
    precision=load(E/'model-precision-v3-s25c6.json');assert sha(E/'model-precision-v3-s25c6.json')==V3
    assert all(sha(ROOT/n)==h for n,h in precision['model_source_sha256'].items())and sha(ROOT/'context_color_api.py')==precision['inverse_API_sha256']
    for filename,expected in ACCEPTED.values():assert sha(E/filename)==expected
    prior=load(E/'verification-s26.json');source_changes=[n for n,h in prior['current_source_sha256'].items()if sha(ROOT/n)!=h];assert source_changes==['bound_validation.py']
    prior_evidence={n:sha(E/n)==h for n,h in prior['evidence_sha256'].items()};assert all(prior_evidence.values())
    old_cost=load(E/'stage-audit-s25h2.json')['full_point_cost'];assert old_cost['total_recorded_plus_uninstrumented_range']==[162,163]
    iteration=load(E/'source-iteration-s27e.json')
    initial_pre=load(E/'test-binding-s27d.pre.json')
    for name,record in iteration['initial_sources'].items():assert sha(REPO.parent/record['private_relative_to_task'])==record['sha256']==initial_pre['source_sha256_before_execution'][name]
    math_keys=['confirmed_model_joint_candidates','confirmed_model_f32_population','possible_joint_candidates','possible_f32_population','unresolved_joint_candidates','information','confirmed_joint_interface_state_ids']
    for name,r in results.items():
        old=load(E/f'joint-result-{name}-s27b.json');assert old['joint_API_source_sha256']==iteration['initial_sources']['joint_color_api.py']['sha256'];assert all(old[k]==r[k]for k in math_keys)
    bindings={}
    for f in sorted(E.glob('*binding*s27*.json')):
        if f.name.endswith('.pre.json'):continue
        d=load(f);pre=f.with_name(f.stem+'.pre.json');log=f.with_suffix('.log');assert sha(pre)==d['pre_run_binding_sha256']and sha(log)==d['log_sha256'];assert d['exit_code']==0 and d['source_unchanged_during_command']and d['inputs_unchanged_during_command'];bindings[f.stem]={'pre_sha256':sha(pre),'post_sha256':sha(f),'raw_log_sha256':sha(log),'exit_code':0,'source_and_inputs_unchanged':True,'elapsed_seconds':d['elapsed_seconds']}
    text=(E/'test-binding-s27d2.log').read_text();m=re.search(r'Ran (\d+) tests in ([\d.]+)s\n\nOK',text);assert m and int(m[1])==23
    test_pre=load(E/'test-binding-s27d2.pre.json');assert all(test_pre['source_sha256_before_execution'][n]==sha(ROOT/n)for n in ['joint_color_api.py','raw_f32_sets.py','test_joint_color_api.py'])
    for f in E.glob('*s27*'):
        if not f.is_file():continue
        assert b'\0'not in f.read_bytes()and re.search(rb'/Users/[A-Za-z0-9._-]+/',f.read_bytes())is None
        if f.suffix=='.json':load(f)
    assert not subprocess.check_output(['git','diff','--name-only','HEAD','--',str(E)],cwd=REPO,text=True).strip()
    output_data={'scope':'S27 exact joint raw-parameter candidate API using only the two pinned existing-v3 contexts; no new forwards or kernels','status':'passed_existing_catalog_joint_queries_and_partial_provenance_tests','repository':{'base_HEAD':subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),'branch':subprocess.check_output(['git','branch','--show-current'],cwd=REPO,text=True).strip(),'initial_remote_branch':'9692aae1bceee28fe9f479ea82f74760d515d8b9','master':'ce25aa34fe3dac8541730971d6957401fca3e1dc','reference_vm_native':'2132e1fcb6505e601d006b5ca1afde04e36ae649'},'precision_contract_sha256':V3,'accepted_context_catalogs':ACCEPTED,'single_context_API_and243_model_sources_unchanged':True,'shared_parameter_declaration_required':True,'field_definition':FIELD,'scene_domain_cast_or_free_fields_expanded':False,'interval_semantics':'exact inclusive uint32 f32 sets, with checked real binary endpoints/closure/population','known_possible_unresolved_sets_separate':True,'unknown_missing_not_implicitly_excluded':True,'partial_known_rows_must_match_pinned_baseline':True,'new_writer_injection_rejected':True,'examples':audit,'state7_joint_intervals':a['possible_joint_candidates'],'platform_joint_intervals':z['possible_joint_candidates'],'joint_acceptance_grade':'model_only; no joint original-host witness or GPU proof','individual_target_invalidity_claim':False,'nearest_fallback':False,'new_model_forward_calls':0,'new_original_kernel_calls':0,'new_compilations':0,'initial_source_iteration':iteration,'initial_and_final_mathematical_candidates_identical':True,'tests':{'count':23,'unittest_seconds':float(m[2]),'result':'OK','raw_output_sha256':sha(E/'test-binding-s27d2.log'),'partial_examples':'synthetic omissions/unknowns/new-row injection fixtures only; actual full directories unchanged','forward_and_original_kernel_entrypoints_blocked_in_test':True},'S25_cost_limit_retained':old_cost,'prior_source_changes_only_stage_binding_metadata':source_changes,'prior_S26_evidence_SHA_unchanged':prior_evidence,'pre_execution_bindings':bindings,'current_source_sha256':{f.name:sha(f)for f in sorted(ROOT.glob('*.py'))},'document_sha256':{n:sha(ROOT/n)for n in ['PROGRESS-S27.zh-CN.md','README.zh-CN.md']},'evidence_sha256':{f.name:sha(f)for f in sorted(E.glob('*s27*'))if f.is_file()},'no_IR_or_binary_created_or_uploaded':True,'no_new_download_mount_cache_search_private_media_or_process_retry':True,'remaining':['raw-sharing is an explicit caller assumption; no inference from same UI settings or Styles metadata','class7 joint evidence is model-only;140 states per context still not original-host exhaustive','bright6+18 residuals retained; cast16/multiple free parameters prohibited','set unknowns, nine-field missing-cache software bridge, historical IR cause, originalGPU/UI/real paired frames/IMG_2810 build and unknown-source inverse unverified','S19 recovery and S25 failed-v2 cost/source retention limits preserved']}
    output.write_bytes(encoded(output_data));print(json.dumps({'status':output_data['status'],'state7_joint_population':860159,'extra_gain_beyond_second':0,'platform_population':1018499073,'incompatible_joint_empty':True,'new_forward_or_kernel_calls':0,'tests':23}));return output_data


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path);a=p.parse_args();verify(a.output)
