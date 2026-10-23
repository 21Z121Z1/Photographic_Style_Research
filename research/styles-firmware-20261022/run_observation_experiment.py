"""S28 fixed-rule observation robustness using only existing catalog arrays."""
from pathlib import Path
from dataclasses import asdict
import argparse,json,time
import numpy as np
from baseline_archive import sha,encoded
from context_color_api import BoundCatalog,Target,load
from joint_color_api import SharedField3,compatible
from observation_ulps import Catalog,perturb,ranks,from_ranks,digest_bits,joint

ROOT=Path(__file__).parent;E=ROOT/'evidence'


def contains(intervals,bits):return any(x['first_f32_bits']<=bits<=x['last_f32_bits']for x in intervals)


def score_truth(result,raw):
    for mode in ['exact','tolerance']:
        result[mode]['truth_retained_in_known']=contains(result[mode]['known_candidates'],raw);result[mode]['truth_possible']=contains(result[mode]['possible_candidates'],raw)
    return result


def pairwise(tables,partition):
    if any(t.ids!=list(range(146))for t in tables.values()):raise ValueError('Complete existing tables required for exhaustive pair diagnostic')
    same={};overlap={};center={};distances={}
    for side,t in tables.items():
        rgb=t.prediction_ranks[:,t.mask];d=np.abs(rgb[:,None,:]-rgb[None,:,:]).max(axis=2);zone=t.arrays[:,~t.mask];e=np.all(zone[:,None,:]==zone[None,:,:],axis=2);same[side]=e&(d==0);overlap[side]=e&(d<=2);center[side]=e&(d<=1);distances[side]=d
    exact_joint=same['first']&same['second'];overlap_joint=overlap['first']&overlap['second'];pairs=[(i,j)for i in range(146)for j in range(i+1,146)];new=[(i,j)for i,j in pairs if overlap_joint[i,j]and not exact_joint[i,j]];candidate=new[0]if new else None;witness=None
    if candidate is not None:
        i,j=candidate;observations={};scans=[]
        for side,t in tables.items():
            a=t.arrays[i];b=t.arrays[j];k=ranks(a).copy();ka=ranks(a);kb=ranks(b);k[t.mask]=np.maximum(ka[t.mask]-1,kb[t.mask]-1);obs=from_ranks(k);assert np.array_equal(a[~t.mask],b[~t.mask])and np.all(abs(ranks(obs)[t.mask]-ka[t.mask])<=1)and np.all(abs(ranks(obs)[t.mask]-kb[t.mask])<=1);scan=t.scan(Target(t.identity,t.handle.expected_catalog_sha256,obs),diagnostics=True);assert i in scan['tolerance']['known_state_ids']and j in scan['tolerance']['known_state_ids'];scans.append(scan);observations[side]={'observed_half_bits':obs.tolist(),'prediction_max_half_steps_between_pair':int(distances[side][i,j]),'observation_max_steps_to_first':int(abs(ranks(obs)[t.mask]-ka[t.mask]).max()),'observation_max_steps_to_second':int(abs(ranks(obs)[t.mask]-kb[t.mask]).max()),'scan':scan}
        joined=joint(scans,'tolerance',shared_parameter=SharedField3(True));raws=[partition['states'][n]['representative_f32_bits']for n in candidate];assert all(contains(joined['known_candidates'],raw)for raw in raws);witness={'state_pair':list(candidate),'raw_f32_bits':raws,'raw_f32_values':[float(np.array(raw,dtype='u4').view('f4'))for raw in raws],'rule':'lexicographically first non-exact joint-overlap pair; common per-component observation is lower endpoint of intersection of two radius1 rank boxes','observations':observations,'joint_tolerance':joined,'both_raw_parameters_retained':True,'is_fixed_rule_cohort':False,'is_constructed_ambiguity_witness':True}
    raw01=int(np.float32(.01).view('u4'));assert next(c[3]for c in partition['cells']if c[1]<=raw01<=c[2])==1
    exact_pair={'state_pair':[0,1],'raw_f32_bits':[0,raw01],'raw_f32_values':[0.,float(np.float32(.01))],'each_context_writer_half_bits_identical':{side:bool(np.array_equal(t.arrays[0],t.arrays[1]))for side,t in tables.items()}}
    assert all(exact_pair['each_context_writer_half_bits_identical'].values())
    return {'scope':'all10585 distinct-state pairs; prediction-center distance<=1 differs from two radius1 observation boxes overlapping at distance<=2','pair_count':len(pairs),'exact_joint_collision_pairs':[list(p)for p in pairs if exact_joint[p]],'single_scene_center_compatible_pair_counts':{s:sum(bool(m[p])for p in pairs)for s,m in center.items()},'single_scene_radius1_box_overlap_pair_counts':{s:sum(bool(m[p])for p in pairs)for s,m in overlap.items()},'joint_radius1_box_overlap_pairs':[list(p)for p in pairs if overlap_joint[p]],'new_nonexact_joint_overlap_pairs':[list(p)for p in new],'new_nonexact_joint_overlap_count':len(new),'exact_indistinguishable_parameter_pair':exact_pair,'constructed_measurement_ambiguity_witness':witness,'tolerance_relation_not_claimed_equivalence_or_transitive':True,'new_forward_or_kernel_calls':0}


def run(output):
    if output.exists():raise FileExistsError(output)
    plan_file=E/'observation-experiment-plan-s28a.json';error_file=E/'observation-error-contract-s28a.json';plan=load(plan_file);error=load(error_file)
    if sha(error_file)!=plan['contract_sha256']:raise ValueError('Frozen observation contract changed')
    partition=load(E/'color-partition-s22a.json');tables={}
    for side,context in plan['contexts'].items():
        context_sha=sha(E/context);filename,expected=plan['accepted_catalogs'][context_sha];h=BoundCatalog(E/context,E/'model-precision-v3-s25c6.json',E/'color-partition-s22a.json',E/filename,expected);tables[side]=Catalog(h,error_file)
    compatible([t.contract for t in tables.values()]);assert all(t.ids==list(range(146))for t in tables.values());input_files=[plan_file,error_file,E/'color-partition-s22a.json',E/'model-precision-v3-s25c6.json',*[t.handle.catalog_file for t in tables.values()],*[t.handle.context_file for t in tables.values()]]
    for t in tables.values():input_files.extend(t.handle.catalog_file.parent/part['name']for part in load(t.handle.catalog_file)['chunks'])
    source_inputs={f.name:sha(f)for f in input_files}
    result={'scope':__doc__,'status':'in_progress','plan_sha256':sha(plan_file),'observation_error_contract_sha256':sha(error_file),'source_inputs_sha256':source_inputs,'source_sha256':{n:sha(ROOT/n)for n in ['observation_ulps.py','run_observation_experiment.py','freeze_observation.py']},'preflight':{s:{'identity':asdict(t.identity),'mask_RGB_components':int(t.mask.sum()),'mask_exact_components':int((~t.mask).sum()),'all146_states_finite_positive_written_RGB':True,'written_RGB_min':float(t.arrays[:,t.mask].view('f2').min()),'written_RGB_max':float(t.arrays[:,t.mask].view('f2').max()),'written_alpha_and_unwritten_initial_storage_verified':True}for s,t in tables.items()},'cases':[],'single_component_enumeration':[],'minimal_exact_failure':None,'new_forward_or_kernel_calls':0,'evidence_grade':'model_only; artificial measurement tolerance, not JPEG/HEIC/GPU','original_exact_acceptance_unchanged':True,'table_observation_scans':0}
    def save():output.write_bytes(encoded(result))
    save();begin=time.perf_counter()
    for case in plan['cases']:
        raw=case['truth_raw_f32_bits'];case_data={'case':case,'scenes':{},'joint_comparisons':[]}
        for side,t in tables.items():
            original=t.arrays[case['state_id']];scans={};scene={'original_model_writer_half_bits':original.tolist(),'original_model_writer_sha256':digest_bits(original),'patterns':{}}
            for pattern in plan['primary_patterns']:
                obs,change=perturb(original,t.mask,pattern);scan=t.scan(Target(t.identity,t.handle.expected_catalog_sha256,obs),diagnostics=True);result['table_observation_scans']+=1;legacy=t.handle.query(Target(t.identity,t.handle.expected_catalog_sha256,obs));assert legacy['model_matching_state_ids']==scan['exact']['known_state_ids'];score_truth(scan,raw);scans[pattern]=scan;scene['patterns'][pattern]={'perturbation':change,'observed_half_bits':obs.tolist(),'scan':scan,'legacy_exact_API_same_matches':True}
                if change['within_artificial_contract']:assert scan['tolerance']['truth_retained_in_known']
            case_data['scenes'][side]=scene
        for first,second in plan['joint_pairs']:
            scans=[case_data['scenes']['first']['patterns'][first]['scan'],case_data['scenes']['second']['patterns'][second]['scan']];entry={'patterns':[first,second]}
            for mode in ['exact','tolerance']:
                joined=joint(scans,mode,shared_parameter=SharedField3(True));joined['truth_retained_in_known']=contains(joined['known_candidates'],raw);joined['truth_possible']=contains(joined['possible_candidates'],raw);entry[mode]=joined
            case_data['joint_comparisons'].append(entry)
        result['cases'].append(case_data);save();print(json.dumps({'completed_case':case['id'],'primary_table_scans':result['table_observation_scans']}),flush=True)
    for case in plan['cases']:
        for side,t in tables.items():
            original=t.arrays[case['state_id']];base_ranks=ranks(original)
            for coordinate in np.argwhere(t.mask):
                key=tuple(map(int,coordinate))
                for delta in [-1,1]:
                    k=base_ranks.copy();k[key]+=delta;obs=from_ranks(k);scan=t.scan(Target(t.identity,t.handle.expected_catalog_sha256,obs));result['table_observation_scans']+=1;raw=case['truth_raw_f32_bits'];score_truth(scan,raw);assert scan['tolerance']['truth_retained_in_known'];summary={'case':case['id'],'scene':side,'coordinate':list(key),'delta_half_steps':delta,'observed_writer_sha256':scan['observed_writer_sha256'],'exact_match_bitmap':scan['exact_match_bitmap'],'tolerance_match_bitmap':scan['tolerance_match_bitmap'],'exact_state_ids':scan['exact']['known_state_ids'],'tolerance_state_ids':scan['tolerance']['known_state_ids'],'exact_population':scan['exact']['known_population'],'tolerance_population':scan['tolerance']['known_population'],'truth_retained_exact':scan['exact']['truth_retained_in_known'],'truth_retained_tolerance':True};result['single_component_enumeration'].append(summary)
                    if result['minimal_exact_failure']is None and not scan['exact']['known_state_ids']:
                        result['minimal_exact_failure']={'selection':'first failure in frozen case/context/coordinate/direction order','case':case,'scene':side,'coordinate':list(key),'delta_half_steps':delta,'observed_half_bits':obs.tolist(),'original_half_bits':original.tolist(),'L0_changed_components':1,'Linfinity_half_steps':1,'original_exact_match_nonempty':True,'scan':scan,'minimality':'any nonzero finite-rank perturbation has at least one changed component and at least one rank step; baseline zero perturbation matched'}
        save()
    result['pairwise_ambiguity']=pairwise(tables,partition)
    if result['pairwise_ambiguity']['constructed_measurement_ambiguity_witness']is not None:result['table_observation_scans']+=2
    assert result['minimal_exact_failure']is not None
    for name,h in source_inputs.items():assert sha(E/name)==h
    for name,h in result['source_sha256'].items():assert sha(ROOT/name)==h
    result.update(status='completed_fixed_artificial_observation_experiment',elapsed_seconds=time.perf_counter()-begin,all_input_files_unchanged=True,state_observation_checks=result['table_observation_scans']*146,component_constraints_checked=result['table_observation_scans']*146*120);save();print(json.dumps({'status':result['status'],'primary_scans':56,'single_component_perturbations':len(result['single_component_enumeration']),'minimum_failure':{'case':result['minimal_exact_failure']['case']['id'],'scene':result['minimal_exact_failure']['scene'],'coordinate':result['minimal_exact_failure']['coordinate'],'delta':result['minimal_exact_failure']['delta_half_steps']},'new_joint_ambiguity_pairs':result['pairwise_ambiguity']['new_nonexact_joint_overlap_count'],'new_forward_or_kernel_calls':0}));return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path);a=p.parse_args();run(a.output)
