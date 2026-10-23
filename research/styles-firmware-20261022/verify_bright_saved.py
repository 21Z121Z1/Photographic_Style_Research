"""S29 evidence/source/product audit; never execute the original host library."""
from pathlib import Path
import argparse,json,re,subprocess
from baseline_archive import Archive,encoded,sha
from context_color_api import load

R=Path(__file__).parent
E=R/'evidence'
REPO=R.parents[1]


def verify(output):
    if output.exists():raise FileExistsError(output)
    replay=load(E/'bright-saved-replay-s29a.json')
    trace=load(E/'bright-traces-s29b.json')
    result=load(E/'bright-residual-attribution-s29c.json')
    profile=load(E/'bright-point-profile-s29c.json')
    machine=load(E/'bright-machine-map-s29e2.json')
    assert all(s['corrected_bit_mismatches']==0 for s in replay['stages'])
    assert replay['corrected_final_bits']==replay['saved_host_final_bits']==[8389,11169,9854]
    assert replay['helper_model_evaluations']==72 and replay['unique_all_saved_inputs']==70
    assert [r['half_bit_mismatches']for r in replay['residual_rows']]==[6,0,3,6,6,3,0,0,0,0]
    assert len(replay['unique_residual_inputs'])==4
    for n,h in replay['source_sha256'].items():assert sha(R/n)==h
    for n,h in replay['input_sha256'].items():assert sha(E/n)==h
    assert sha(E/'bright-saved-replay-s29a.json')==trace['inventory_sha256']
    assert trace['new_original_host_main_calls']==3 and trace['new_compilations']==0
    assert all(c['observer_stable']and c['first_observed_checkpoint_divergence']['SSA']==137 for c in trace['calls'])
    assert all(not s['bit_mismatches']for c in trace['calls']for s in c['stages']if s['SSA']<=136)
    assert result['profile_sha256']==sha(E/'bright-point-profile-s29c.json')
    assert result['corrected_residuals']==0 and result['all_saved_checkpoints_match']
    assert not result['generalized_rule_certified']and not result['v3_or_catalogs_changed']
    assert len(result['all24_residual_occurrences'])==24 and len(result['unique_points'])==4
    residuals=result['all24_residual_occurrences']
    assert sum(r['saved_file']=='native-targets-s25c.json'for r in residuals)==6
    assert sum(r['saved_file']=='native-boundaries-s25f.json'for r in residuals)==18
    expected={(row['saved_file'],row['row_index'],tuple(p['grid']),channel,p['input_key'])
              for row in replay['residual_rows']for p in row['residual_pixels']for channel in p['channels']}
    observed={(r['saved_file'],r['row_index'],tuple(r['grid']),r['output_channel'],r['input_key'])for r in residuals}
    assert expected==observed and len(expected)==24
    for r in residuals:
        p=result['unique_points'][r['input_key']]
        assert r['first_observed_divergence_SSA']==137 and r['corrected_matches_saved_host']
        assert r['old_output_half_bits']!=r['host_output_half_bits']==r['corrected_output_half_bits']
        assert r['corrected_output_half_bits']==p['corrected_final_bits'][r['output_channel']]
    for key,p in result['unique_points'].items():
        assert p['inputs']==profile['points'][key]['complete_inputs']
        assert p['old_separate137_half_bits']!=p['native137_half_bits']==p['one_round137_half_bits']
        assert all(s['bit_mismatches']==0 for s in p['corrected_stages'])
        assert p['corrected_final_bits']==p['host_final_bits']
    for n,h in profile['source_sha256'].items():assert sha(R/n)==h
    for n,h in profile['input_sha256'].items():assert sha(E/n)==h
    assert machine['SSA137_FMA_address']=='0xd014'and machine['SSA135_FMA_address']=='0xcfb8'
    assert machine['trace_store_byte_offsets']['137']==480 and machine['leaf_source_sha256']==sha(R/'bright_low_host.py')
    assert 'half-12' in machine['SSA135_register']and 'FPCR was not measured' in machine['rounding_mode']
    product_proofs={}
    for n in ['bright-traces-s29b.json','bright-machine-s29d.json']:
        receipt=load(E/n)
        a=Archive(REPO.parent/receipt['private_storage_relative_to_task'],repo=REPO)
        p=a.verify()
        assert p['sealed_manifest_sha256']==receipt['private_manifest_sha256']
        product_proofs[n]={k:v for k,v in p.items()if k!='capacity'}
    old=load(E/'bright-detail-s25c.json')
    a=Archive(REPO.parent/old['private_storage_relative_to_task'],repo=REPO)
    old_proof=a.verify(old['products'])
    assert old_proof['sealed_manifest_sha256']==old['private_manifest_sha256']
    precision=load(E/'model-precision-v3-s25c6.json')
    assert len(precision['model_source_sha256'])==243
    assert all(sha(R/n)==h for n,h in precision['model_source_sha256'].items())
    prior=load(E/'verification-s28.json')
    assert [n for n,h in prior['current_source_sha256'].items()if sha(R/n)!=h]==['bound_validation.py']
    assert all(sha(E/n)==h for n,h in prior['evidence_sha256'].items())
    iteration=load(E/'source-iteration-s29f.json')
    for item in iteration['initial_records'].values():assert sha(REPO.parent/item['private_relative_to_task'])==item['sha256']
    bad=load(E/'test-binding-s29f.json')
    assert bad['exit_code']==1 and bad['source_unchanged_during_command']and bad['inputs_unchanged_during_command']
    assert bad['log_sha256']==iteration['initial_records']['test-binding-s29f.log']['sha256']
    assert sha(E/'test-binding-s29f.redacted.log')==iteration['public_redacted_log_sha256']
    assert sha(E/'bright-machine-map-s29e.json')==iteration['rejected_map_receipt']['sha256']
    bindings={}
    for n in ['replay-binding-s29a','trace-binding-s29b','profile-binding-s29c',
              'machine-binding-s29d','map-binding-s29e','map-binding-s29e2','test-binding-s29f2']:
        d=load(E/(n+'.json'));pre=E/(n+'.pre.json');log=E/(n+'.log')
        assert d['exit_code']==0 and d['source_unchanged_during_command']and d['inputs_unchanged_during_command']
        assert sha(pre)==d['pre_run_binding_sha256']and sha(log)==d['log_sha256']
        bindings[n]={'pre_sha256':sha(pre),'post_sha256':sha(E/(n+'.json')),'log_sha256':sha(log),
                     'exit_code':0,'elapsed_seconds':d['elapsed_seconds']}
    tests=re.search(r'Ran (\d+) tests in ([\d.]+)s\n\nOK',(E/'test-binding-s29f2.log').read_text())
    assert tests and int(tests[1])==10
    cost=load(E/'stage-audit-s25h2.json')['full_point_cost']
    assert cost['total_recorded_plus_uninstrumented_range']==[162,163]
    assert not subprocess.check_output(['git','diff','--name-only','HEAD','--',str(E)],cwd=REPO,text=True).strip()
    for p in E.glob('*s29*'):
        if p.is_file():
            assert b'\0' not in p.read_bytes() and re.search(rb'/Users/[A-Za-z0-9._-]+/',p.read_bytes())is None
            if p.suffix=='.json':load(p)
    d={'status':'passed_saved_bright_downstream_residual_attribution_and_static_machine_map',
       'base_HEAD':subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),
       'branch':subprocess.check_output(['git','branch','--show-current'],cwd=REPO,text=True).strip(),
       'version':['iPhone17,3','24A446','SmartStyleV1','CMISmartStyleProcessorV1'],
       'old_default_v3_residuals_retained':{'target':6,'boundaries':18},
       'new_independent_profile':{'name':profile['schema'],'sha256':sha(E/'bright-point-profile-s29c.json'),
                                  'domain':'four exact complete saved input tuples; point-only',
                                  'residuals':0,'all_saved_checkpoints_match':True,
                                  'uncertified_neighbor_rejected':True},
       'independent_low_leaf':{'name':machine['leaf_profile'],'domain':machine['leaf_domain'],
                               'SSA135':'round_half(16*x-12)','SSA137':'round_half(half135*x+4), fused',
                               'RN_assumed_FPCR_not_measured':True,'caller_and_GPU_not_certified':True},
       'first_divergence_grade':'SSA137 is the first saved/instrumented checkpoint divergence; immediate132/135/136 operands authenticated; not a proof over every unobserved SSA',
       'all24_occurrences_and_input_bits':'bright-residual-attribution-s29c.json',
       'max_old_output_absolute_error':max(r['old_absolute_error']for r in residuals),
       'tests':{'count':10,'seconds':float(tests[2]),'result':'OK','native_library_loading_blocked_in_profile_test':True},
       'cost':{'new_original_CPU_host_main_calls':3,'reused_saved_first_trace':1,
               'new_producer_or_guided_calls':0,'new_compilations':0,'new_full_model_calls':0,
               'replay_bright_helper_model_evaluations':72,'independent_profile_evaluations':4,
               'test_runs':2,'test_bright_helper_evaluations_total':4,
               'test_low_leaf_evaluations_total':7,'static_disassembly_executions':1,
               'GPU_calls':0},
       'failure_and_rejected_semantic_record_retained':iteration,
       'v3_API_243_sources_and_directories_unchanged':True,'prior_S28_evidence_unchanged':True,
       'S25_old_failed_v2_cost_limit':cost,'private_product_hash_proofs':product_proofs,
       'pre_execution_bindings':bindings,
       'current_source_sha256':{p.name:sha(p)for p in sorted(R.glob('*.py'))},
       'document_sha256':{n:sha(R/n)for n in ['PROGRESS-S29.zh-CN.md','README.zh-CN.md']},
       'evidence_sha256':{p.name:sha(p)for p in sorted(E.glob('*s29*'))if p.is_file()},
       'remaining':['full bright arbitrary callers and upstream square domain not certified by four tuples',
                    'FPCR not measured; independent low-node RN assumption explicit',
                    'unobserved SSA graph not exhaustively compared; no original iOS/GPU execution',
                    'cast16/multiple free fields prohibition unchanged; original v3 not replaced',
                    'old set unknowns, nine-field missing-cache software bridge, historical IR cause remain',
                    'UI/real same-frame/IMG_2810 build and unknown-source inverse unverified']}
    output.write_bytes(encoded(d));print(json.dumps({'status':d['status'],'tests':10,'old24_profile_residuals':0,
                                                    'CPU_host_calls':3,'compilations':0,'GPU':False}))
    return d


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path);verify(p.parse_args().output)
