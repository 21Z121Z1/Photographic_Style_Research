"""Join finite-model coverage, reusable inverse queries and original boundaries."""
import argparse,hashlib,json
from pathlib import Path
from color_inverse import signature,f32


def check(plan_file,inverse_file,native_file,platform_file,point3_file,prior_native,output):
    if output.exists():raise FileExistsError(output)
    load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();p=load(plan_file);inverse=load(inverse_file);native=load(native_file);queries={'platform':load(platform_file),'point3':load(point3_file)};old=load(prior_native)
    if not inverse['coverage']['complete_model_coverage']or native['inverse_sha256']!=sha(inverse_file):raise ValueError('Incomplete/unbound model or original boundary evidence')
    for n,q in queries.items():
        if not q['coverage']['complete_model_coverage']or q['candidate_union']!=inverse['candidates'][n]['candidate_union']or q['model_matching_state_ids']!=inverse['candidates'][n]['model_matching_state_ids']:raise ValueError('Reusable query differs from exhaustive aggregation')
    checks=[];witness_keys=set()
    for row in old['rows']:witness_keys.add(signature(f32(row['control']['raw_f32_bits'])))
    for row in native['rows']:
        if not row['target_match_expectations_agree']or not row['model_writer_sha256_match']or row['observer_plain_writer_half_bit_mismatches']or row['native_nonfinite_components']or not all(row['logical_interface_matches'].values()):raise ValueError('Original boundary failure must remain unresolved')
        if any(v['half_bit_mismatches']for v in row['point']['observations'].values()):raise ValueError('Boundary model point mismatch')
        c=row['control'];witness_keys.add(tuple(c['key']));checks.append({'raw_f32_bits':c['raw_f32_bits'],'raw_f32_hex':c['raw_f32_hex'],'raw_f32':c['raw_f32'],'state_id':c['state_id'],'reasons':c['reasons'],'actual_target_matches':row['target_matches'],'logical_interface_matches':row['logical_interface_matches']})
    matched_ids={v for q in queries.values()for v in q['model_matching_state_ids']};witness_ids=[s['id']for s in p['states']if tuple(s['key'])in witness_keys]
    result={'scope':__doc__,'input_sha256':{f.name:sha(f)for f in [plan_file,inverse_file,native_file,platform_file,point3_file,prior_native]},'complete_model_finite_domain':inverse['coverage'],'returned_candidates':{n:{'candidate_union':q['candidate_union'],'interface_classes':q['candidate_interface_classes'],'model_matching_state_ids':q['model_matching_state_ids'],'found_f32_population':q['found_f32_population']}for n,q in queries.items()},'original_boundary_checks':checks,'original_host_signature_ids_with_finite_witnesses':witness_ids,'all_model_candidate_signature_ids_have_original_witness':matched_ids.issubset(witness_ids),'original_host_all146_states_exhaustively_verified':False,'new_original_kernel_calls':native['total_original_kernel_calls'],'new_raw_controls':len(native['rows']),'cost':{'independent_full_point_model_search_states':inverse['model_forward_evaluations'],'model_search_elapsed_seconds_sum':inverse['model_search_elapsed_seconds_sum'],'extra_boundary_point_model_calls':native['new_model_forward_calls'],'query_new_forward_calls':0,'original_prefix_calls':native['prefix_original_calls'],'original_main_observed_and_plain_calls':native['new_main_original_calls']},'unknown_scope':['positive canonical f32 above3/8 and negative zero not searched','original GPU and UI mapping not verified','unknown-source finished-photo inverse not addressed','RichSat whole-set zero denominator outer enclosure retained independently','nine consumer CPU cache breakpoints and old neutral12+24 unknowns retained'],'unique_parameter_returned':False,'full_photo_inverse_verified':False};output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');print(json.dumps({'witness_ids':witness_ids,'candidate_ids':sorted(matched_ids),'new_raw_controls':len(checks),'original_kernel_calls':native['total_original_kernel_calls'],'model_domain_complete':True,'original_host_domain_exhaustive':False}));return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('plan',type=Path);p.add_argument('inverse',type=Path);p.add_argument('native',type=Path);p.add_argument('platform_query',type=Path);p.add_argument('point3_query',type=Path);p.add_argument('prior_native',type=Path);p.add_argument('output',type=Path);a=p.parse_args();check(a.plan,a.inverse,a.native,a.platform_query,a.point3_query,a.prior_native,a.output)
