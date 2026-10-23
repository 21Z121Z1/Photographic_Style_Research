"""S31 exact saved-certificate audit; no floating candidate search or helper run."""
from pathlib import Path
import argparse,json,re,subprocess
from baseline_archive import encoded,sha
from context_color_api import load
from square132_contract import Assumptions,prefix,classify,RMAX,value
from square140_contract import evaluate

R=Path(__file__).parent
E=R/'evidence'
REPO=R.parents[1]


def verify(output):
    if output.exists():raise FileExistsError(output)
    plan_file=E/'square132-plan-s31a.json';file=E/'square132-proof-s31b.json';plan=load(plan_file);proof=load(file)
    consumer=load(E/'square140-admission-s31c.json')
    assert proof['plan_sha256']==sha(plan_file)and consumer['square_proof_sha256']==sha(file)
    assert proof['generally_proved_outer_hull_half_bits']==[0,0x3bff]and RMAX==0x3bff
    assert all(proof['symbolic_derivation']['constant_inequalities'].values())
    assert proof['symbolic_derivation']['reference_upper_rational']==[2047,2048]
    assert not proof['all_interior_half_values_claimed_reachable']and not proof['native_pow_sqrt_FPCR_or_GPU_certified']
    assert len(proof['witnesses'])==18
    for w in proof['witnesses']:
        exact=prefix(w['c'],plan['fixed_strength_half_bits'],Assumptions(True,True,w['mode']))
        assert exact==w['exact_prefix']and classify(exact['square132'])==w['classification']
        if 'target_square'in w:assert exact['square132']==w['target_square']
    for mode in ['separate','fused']:
        for target in [0x2c00,0x2c01,0x33ff,0x3400,0x3401]:
            assert any(w.get('target_square')==target and w['mode']==mode for w in proof['witnesses'])
    missing=proof['window_only_unknown_boundary_searches']
    assert [(m['target_square'],m['mode'])for m in missing]==[(0x2bff,'separate'),(0x2bff,'fused')]
    fixed=proof['full_existing_helper_model_checks']
    assert [(r['name'],r['square132_half_bits'])for r in fixed]==[('zero',0),('smallest_input_subnormal',12),('normal_below_old_domain',0x21d3),('upper_endpoint',0x3bff)]
    assert all(r['full_existing_model_helper_finite']and r['strength58_half_bits']==0x3c00 for r in fixed)
    assert consumer['low_quarter_equality_exact_result_half_bits']==0x3800
    for row in consumer['examples']:
        a=row['without_flush_or_sqrt_premise'];x=a['square132_half_bits']
        assert a==evaluate(x,rn_even=True,gradual_underflow=None)
        assert row['with_gradual_and_correct_final_sqrt_premises']==evaluate(x,rn_even=True,gradual_underflow=True,correct_final_sqrt_half=True)
    assert evaluate(12,rn_even=True,gradual_underflow=None)['status']=='unknown'
    assert evaluate(0x21d3,rn_even=True,gradual_underflow=None)['status']=='conditional_math_point'
    assert evaluate(0x3401,rn_even=True,gradual_underflow=None)['status']=='unknown'
    for n,h in proof['source_sha256'].items():assert sha(R/n)==h
    for n,h in consumer['source_sha256'].items():assert sha(R/n)==h
    old_detail=load(E/'bright-detail-s25c.json');ir=REPO.parent/old_detail['private_storage_relative_to_task']/'inputs/trace.ll'
    assert sha(ir)==proof['static_binding']['actual_saved_trace_IR_sha256']
    previous=load(E/'verification-s30.json')
    assert [n for n,h in previous['current_source_sha256'].items()if sha(R/n)!=h]==['bound_validation.py']
    assert all(sha(E/n)==h for n,h in previous['evidence_sha256'].items())
    p=load(E/'model-precision-v3-s25c6.json')
    assert len(p['model_source_sha256'])==243 and all(sha(R/n)==h for n,h in p['model_source_sha256'].items())
    bindings={}
    for name in ['freeze-binding-s31a','proof-binding-s31b','consumer-binding-s31c','test-binding-s31d']:
        b=load(E/(name+'.json'));pre=E/(name+'.pre.json');log=E/(name+'.log')
        assert b['exit_code']==0 and b['source_unchanged_during_command']and b['inputs_unchanged_during_command']
        assert sha(pre)==b['pre_run_binding_sha256']and sha(log)==b['log_sha256']
        bindings[name]={'pre_sha256':sha(pre),'post_sha256':sha(E/(name+'.json')),'log_sha256':sha(log),'elapsed_seconds':b['elapsed_seconds']}
    pre=load(E/'proof-binding-s31b.pre.json');assert pre['input_sha256_before_execution'][plan_file.name]==sha(plan_file)
    tests=re.search(r'Ran (\d+) tests in ([\d.]+)s\n\nOK',(E/'test-binding-s31d.log').read_text())
    assert tests and int(tests[1])==12
    assert not subprocess.check_output(['git','diff','--name-only','HEAD','--',str(E)],cwd=REPO,text=True).strip()
    for f in E.glob('*s31*'):
        if f.is_file():
            assert b'\0'not in f.read_bytes()and re.search(rb'/Users/[A-Za-z0-9._-]+/',f.read_bytes())is None
            if f.suffix=='.json':load(f)
    out={'status':'passed_conditional_square132_domain_derivation_and_exact_witness_audit',
         'base_HEAD':subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),
         'branch':subprocess.check_output(['git','branch','--show-current'],cwd=REPO,text=True).strip(),
         'version':['iPhone17,3','24A446','SmartStyleV1','CMISmartStyleProcessorV1'],
         'general_derivation_grade':proof['symbolic_derivation']['proof_grade'],
         'general_outer_hull_half_bits':[0,RMAX],'general_outer_hull_rational':[[0,1],[2047,2048]],
         'all_interior_values_reachable_claim':False,
         'power_condition':'nonlinear power half P in[7/128,1]; ideal correctly RN-quantized c^(853/2048) implies it; arbitrary native libm/GPU not certified',
         'rounding_conditions':'RN-even premise; subnormal paths need gradual-underflow premise; sqrt final quantization premise separate',
         'old_leaf_selected_coverage':'square in[1/16,1/4]; below1/16 old leaf unknown, above1/4 low is not selected',
         'constructive_square132_half_bits':{r['name']:r['square132_half_bits']for r in fixed},
         'quarter_and_neighbors_have_conditional_exact_prefix_witnesses':True,
         'quarter_equality_selects_low':True,'old_upper1_not_inside_conditional_prefix_hull':True,
         'unresolved':missing,
         'new_operation_contract_uses_no_coordinate_or_tuple_whitelist':True,
         'default_v3_S29_guard_or_catalogs_changed':False,
         'tests':{'count':12,'seconds':float(tests[2]),'result':'OK',
                  'exact_power_certificate_test_blocks_numpy_pow':True},
         'cost':{'floating_candidate_prefix_evaluations':1028,'floating_search_is_not_general_proof':True,
                 'exact_rational_prefix_witnesses':18,'audit_exact_witness_rechecks':18,
                 'new_existing_bright_helper_model_calls':4,'test_or_audit_helper_calls':0,
                 'new_full_pipeline_calls':0,'new_original_CPU_or_GPU_calls':0,'new_native_compilations':0},
         'prior_S30_evidence_and243_model_sources_unchanged':True,
         'pre_execution_bindings':bindings,
         'current_source_sha256':{f.name:sha(f)for f in sorted(R.glob('*.py'))},
         'document_sha256':{n:sha(R/n)for n in ['PROGRESS-S31.zh-CN.md','README.zh-CN.md']},
         'evidence_sha256':{f.name:sha(f)for f in sorted(E.glob('*s31*'))if f.is_file()},
         'remaining':['hypothetical helper-prefix reachability differs from same frozen source or camera-frame reachability',
                      'FPCR/RN/flush state and native pow/sqrt accuracy not measured; originalGPU unverified',
                      '0x2bff boundary witness not found in fixed window; no general impossibility claim',
                      'no default integration, genericv4, cast16 or multiple-free-field enablement',
                      'old set unknowns, nine-field missing-cache software bridge, historicalIR/UI/real same-frame/IMG_2810 build and unknown-source inverse remain']}
    output.write_bytes(encoded(out));print(json.dumps({'status':out['status'],'tests':12,'outer_hull':[0,RMAX],
                                                      'exact_witnesses':18,'new_helper_models':4,'new_kernels':0}))
    return out


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path);verify(p.parse_args().output)
