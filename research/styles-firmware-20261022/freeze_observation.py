"""Freeze S28 artificial measurement contract/rules before matching results."""
from pathlib import Path
import argparse,json
from baseline_archive import sha,encoded
from context_color_api import load
from joint_color_api import V3,FIELD,ACCEPTED
from observation_ulps import geometry

ROOT=Path(__file__).parent;E=ROOT/'evidence'


def freeze():
    contract_file=E/'observation-error-contract-s28a.json';plan_file=E/'observation-experiment-plan-s28a.json'
    if contract_file.exists()or plan_file.exists():raise FileExistsError('Frozen contract/plan cannot be overwritten')
    precision=load(E/'model-precision-v3-s25c6.json');assert sha(E/'model-precision-v3-s25c6.json')==V3
    contexts={'first':'complete-context-s15a.json','second':'second-context-s25a.json'};masks={sha(E/name):geometry(E/name)for name in contexts.values()}
    contract={'schema':'psr-artificial-written-RGB-half-step1-v1','precision_contract_sha256':V3,'field_definition':FIELD,'RGB_half_rank_budget':1,'alpha_bit_exact':True,'unwritten_bit_exact':True,'distance':'absolute difference of finite binary16 total-order encoding ranks; away from signed zero this is adjacent-half ULP count','signed_zero_policy':'-0 and +0 are consecutive distinct ranks; dataset predicted written RGB must be strictly positive, so experiment comparisons use ordinary positive half ULPs','positive_written_RGB_preflight_required_for_every_known_state':True,'finite_only_no_saturation_or_clipping':True,'contexts':masks,'writer_geometry_source_sha256':sha(ROOT/'output_writer.py'),'writer_geometry_source_matches_v3':sha(ROOT/'output_writer.py')==precision['model_source_sha256']['output_writer.py'],'artificial_measurement_contract':True,'JPEG_HEIC_GPU_error_model':False,'original_exact_acceptance_threshold_modified':False,'model_numerical_error_budgets_modified':False,'joint_shared_raw_parameter_declaration_required':True}
    contract_file.write_bytes(encoded(contract));p=load(E/'color-partition-s22a.json');controls=load(E/'scene-selection-s25a.json')['target_controls'];cases=[{'id':'platform','state_id':0,'truth_raw_f32_bits':0},{'id':'state7','state_id':7,'truth_raw_f32_bits':p['states'][7]['representative_f32_bits']},{'id':'active_A','state_id':17,'truth_raw_f32_bits':controls[0]['raw_f32_bits']},{'id':'active_B','state_id':122,'truth_raw_f32_bits':controls[1]['raw_f32_bits']}]
    for c in cases:assert next(x[3]for x in p['cells']if x[1]<=c['truth_raw_f32_bits']<=x[2])==c['state_id']
    plan={'scope':__doc__,'contract_sha256':sha(contract_file),'precision_sha256':V3,'contexts':contexts,'accepted_catalogs':ACCEPTED,'partition_sha256':sha(E/'color-partition-s22a.json'),'cases':cases,'primary_patterns':['identity','first_rgb_plus1','first_rgb_minus1','checker_rgb_pm1','first_rgb_plus2','first_alpha_plus1','first_unwritten_rgb_plus1'],'admissible_patterns':['identity','first_rgb_plus1','first_rgb_minus1','checker_rgb_pm1'],'negative_patterns':['first_rgb_plus2','first_alpha_plus1','first_unwritten_rgb_plus1'],'perturbation_rule':'first means lexicographic destination(y,x,component), RGB components0/1/2; checker sign +1 iff(y+x+c)even else-1; rules never read truth raw or matching results','all_one_component_rule':'for every case in listed order, every context in first/second order, all36 writtenRGB coordinates lexicographic and directions[-1,+1], change exactly one half rank step; scan every state/all components','minimality_objective':'nonzero admissible perturbation lexicographic(L0 changed components,Linfinity half steps); any failure at(1,1)is globally minimal for this discrete nonzero objective','joint_pairs':[['identity','identity'],['first_rgb_plus1','first_rgb_plus1'],['first_rgb_plus1','identity'],['identity','first_rgb_minus1'],['checker_rgb_pm1','checker_rgb_pm1'],['first_rgb_plus1','first_rgb_minus1'],['first_alpha_plus1','identity'],['first_rgb_plus2','identity']],'pairwise_ambiguity_rule':'all10585 i<j interface-state pairs; error boxes overlap iff exact zones identical and each writtenRGB prediction distance<=2; choose lexicographically first new joint-overlap pair not exact-equal in both contexts; construct common observation from per-component interval lower bound','joint_scope':'same post-scene field3 raw, fixed known source/auxiliary contexts; caller assumption explicit','no_new_forward_or_original_kernel_calls':True,'contract_frozen_before_any_target_perturbation_or_match_scan':True}
    plan_file.write_bytes(encoded(plan));print(json.dumps({'error_contract_sha256':sha(contract_file),'plan_sha256':sha(plan_file),'cases':[c['id']for c in cases],'tolerated_exact_component_counts':[[d['RGB_component_count'],d['exact_component_count']]for d in masks.values()],'new_forward_or_kernel_calls':0}));return plan


if __name__=='__main__':freeze()
