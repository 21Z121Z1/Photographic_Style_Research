"""Audit S30 saved composition; no pipeline replay or original kernel call."""
from pathlib import Path
import argparse,ast,hashlib,json,re,subprocess
import numpy as np
from baseline_archive import encoded,sha
from context_color_api import load

R=Path(__file__).parent
E=R/'evidence'
REPO=R.parents[1]


def verify(output):
    if output.exists():raise FileExistsError(output)
    plan_file=E/'connected-bright-plan-s30a.json';result_file=E/'connected-bright-result-s30b.json'
    plan=load(plan_file);d=load(result_file);profile=load(E/plan['profile'])
    assert d['plan_sha256']==sha(plan_file)and d['status']=='passed_limited_source_composition'
    assert plan['pre_execution_freeze']and plan['full_model_runs_planned']==3
    assert plan['profile_sha256']==sha(E/plan['profile'])and plan['context_sha256']==sha(E/plan['context'])
    assert d['full_model_calls']==3 and d['new_kernel_calls']==0 and d['new_compilations']==0
    assert not d['native_arrays_used_as_model_inputs']and d['full_frame_reference_phase_started_only_after_all_models_completed']
    assert not d['bright_selected_into_writer_tested']and d['cast0_writer_is_independent_skin_branch']
    targets=[];compared=0;bright_calls=0
    old_inputs=load(E/'bright-saved-replay-s29a.json')['input_sha256']
    for control,row in zip(plan['controls'],d['rows']):
        assert row['control']==control and row['status']=='model_source_to_bright_connected'
        assert row['target_input_connection_complete']and row['writer_generated']
        assert not row['target_failures']and not row['pixel_unknowns']and not row['internal_unknowns']
        assert not row['native_intermediate_arrays_used_as_inputs']
        visits=[v for v in row['visits']if v['mode']=='S29_profile_target'];bright_calls+=len(row['visits'])
        assert {(tuple(v['grid']),v['expected_input_key'])for v in visits}=={(tuple(s['grid']),s['input_key'])for s in control['targets']}
        for v in visits:
            key=v['expected_input_key'];incoming=v['model_inputs']
            assert v['exact_full_input_match']and v['guard_admitted']and not v['input_differences']
            assert hashlib.sha256(encoded(incoming)).hexdigest()==v['model_input_key']==key
            assert incoming==profile['points'][key]['complete_inputs']
            assert len(v['saved_bright_checkpoint_comparison'])==52
            assert all(r['bit_mismatches']==0 for r in v['saved_bright_checkpoint_comparison'])
            targets.append({'control':control['control_id'],'raw_f32_bits':control['raw_f32_bits'],
                            'grid':v['grid'],'exact_model_input_key':key,'full_inputs_equal':True,
                            'saved_bright_checkpoints':52,'checkpoint_mismatches':0,
                            'bright_output_bits':v['bright_output_bits']})
        file=E/control['expected_saved_file'];reference=load(file)
        assert sha(file)==d['saved_host_files_sha256'][file.name]==old_inputs[file.name]
        assert reference['identity']['complete_context_sha256']==plan['context_sha256']
        expected={**reference['prefix_native_half_bits'],**reference['rows'][control['expected_saved_row']]['native_half_bits']}
        for name,record in row['model_observations'].items():
            if name not in expected:continue
            a=np.array(record['model_half_bits'],dtype='u2');b=np.array(expected[name],dtype='u2')
            if b.shape==a.shape+(1,):b=b[...,0]
            assert a.shape==b.shape and np.array_equal(a,b),name
            metric=row['saved_host_comparison'][name]
            assert metric['components']==a.size and metric['half_bit_mismatches']==0
        assert row['compared_components']==1938 and row['writer_half_bit_mismatches']==0
        assert row['all_saved_observations_equal']and row['first_differing_saved_checkpoint']is None
        o=row['model_observations'];assert o['selected404']['model_half_bits']==o['skin393']['model_half_bits']
        compared+=row['compared_components']
    assert len(targets)==4 and len({v['exact_model_input_key']for v in targets})==4
    assert compared==5814 and bright_calls==36
    # Original callsite selection is preserved in the new AST clone. Writer
    # success is therefore not promoted to bright-selected-to-writer proof.
    tree=ast.parse((R/'complete_forward.py').read_text())
    selected=[n for n in ast.walk(tree)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Subscript)and isinstance(t.slice,ast.Constant)and t.slice.value=='selected404'for t in n.targets)]
    assert len(selected)==1 and isinstance(selected[0].value,ast.Subscript)and selected[0].value.slice.value=='skin393'
    for name,h in d['source_sha256'].items():assert sha(R/name)==h
    old=load(E/'verification-s29.json')
    assert [n for n,h in old['current_source_sha256'].items()if sha(R/n)!=h]==['bound_validation.py']
    assert all(sha(E/n)==h for n,h in old['evidence_sha256'].items())
    precision=load(E/'model-precision-v3-s25c6.json')
    assert len(precision['model_source_sha256'])==243 and all(sha(R/n)==h for n,h in precision['model_source_sha256'].items())
    bindings={}
    for name in ['freeze-binding-s30a','compose-binding-s30b','test-binding-s30c']:
        b=load(E/(name+'.json'));pre=E/(name+'.pre.json');log=E/(name+'.log')
        assert b['exit_code']==0 and b['source_unchanged_during_command']and b['inputs_unchanged_during_command']
        assert sha(pre)==b['pre_run_binding_sha256']and sha(log)==b['log_sha256']
        bindings[name]={'pre_sha256':sha(pre),'post_sha256':sha(E/(name+'.json')),'log_sha256':sha(log),'elapsed_seconds':b['elapsed_seconds']}
    before=load(E/'compose-binding-s30b.pre.json')
    assert before['input_sha256_before_execution'][plan_file.name]==sha(plan_file)
    tests=re.search(r'Ran (\d+) tests in ([\d.]+)s\n\nOK',(E/'test-binding-s30c.log').read_text())
    assert tests and int(tests[1])==10
    assert not subprocess.check_output(['git','diff','--name-only','HEAD','--',str(E)],cwd=REPO,text=True).strip()
    for p in E.glob('*s30*'):
        if p.is_file():
            assert b'\0' not in p.read_bytes() and re.search(rb'/Users/[A-Za-z0-9._-]+/',p.read_bytes())is None
            if p.suffix=='.json':load(p)
    receipt={'status':'passed_limited_source_to_bright_and_actual_cast0_writer_composition',
             'base_HEAD':subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),
             'branch':subprocess.check_output(['git','branch','--show-current'],cwd=REPO,text=True).strip(),
             'version':['iPhone17,3','24A446','SmartStyleV1','CMISmartStyleProcessorV1'],
             'context_sha256':plan['context_sha256'],'independent_S29_profile_sha256':plan['profile_sha256'],
             'plan_sha256':sha(plan_file),'result_sha256':sha(result_file),'targets':targets,
             'native_intermediates_used_as_model_inputs':False,
             'raw_source_producer_guided_main_recomputed':True,
             'S29_evidence_inside_profile':'identity/whitelist comparison only; operands supplied by model',
             'upstream_exactly_reaches_all_four_complete_inputs':True,
             'saved_observation_components_compared':5814,'half_bit_mismatches':0,
             'bright_saved_checkpoint_comparisons':208,'bright_checkpoint_mismatches':0,
             'actual_cast0_writer_mismatches':[0,0,0],
             'bright_selected_into_writer_certified':False,'selected404_source':'skin393 in original actual cast0 model',
             'tests':{'count':10,'seconds':float(tests[2]),'result':'OK',
                      'wrong_tuple_rejected_before_arithmetic_and_without_fallback':True,
                      'writer_generated_but_guard_failed_fixture_remains_failure':True,
                      'admitted_helper_test_blocks_arguments_saved137_apply_and_library_load':True},
             'cost':{'new_complete_model_runs':3,'contained_bright_helper_calls':36,
                     'contained_new_profile_calls':4,'contained_unchanged_v3_bright_calls':32,
                     'test_additional_helper_calls':1,'test_actual_complete_model_runs':0,
                     'test_mocked_pipeline_fixture_calls':1,'audit_complete_model_runs':0,
                     'new_original_host_calls':0,'new_original_GPU_calls':0,'new_native_compilations':0},
             'v3_and243_model_sources_unchanged':True,'S29_profile_and_historical_evidence_unchanged':True,
             'pre_execution_bindings':bindings,
             'current_source_sha256':{p.name:sha(p)for p in sorted(R.glob('*.py'))},
             'document_sha256':{n:sha(R/n)for n in ['PROGRESS-S30.zh-CN.md','README.zh-CN.md']},
             'evidence_sha256':{p.name:sha(p)for p in sorted(E.glob('*s30*'))if p.is_file()},
             'remaining':['only three existing raw controls in one frozen synthetic context, point model',
                          'no actual bright-selected-to-writer path: cast16/multiple free fields prohibited',
                          'no new originalCPU/GPU end-to-end run; only saved CPU results compared',
                          'S29 profile remains four exact tuples, independent experiment not generic v4',
                          'FPCR/unobservedSSA/set unknowns/nine-field missing-cache software bridge remain',
                          'historicalIR/UI/real same-frame/IMG_2810 build/unknown-source inverse unverified']}
    output.write_bytes(encoded(receipt));print(json.dumps({'status':receipt['status'],'tests':10,'input_tuples':4,'components':5814,
                                                          'bit_mismatches':0,'new_complete_models':3,'new_kernels':0,
                                                          'bright_selected_writer_proven':False}))
    return receipt


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path);verify(p.parse_args().output)
