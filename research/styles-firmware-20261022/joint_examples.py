"""Prepare and audit joint examples using saved v3 rows, no forward calls."""
from pathlib import Path
import argparse,json
from baseline_archive import sha,encoded
from context_color_api import BoundCatalog,Target,strict_bits,load
from joint_color_api import SharedField3
from dataclasses import asdict

ROOT=Path(__file__).parent;E=ROOT/'evidence'


def put(path,data):
    with path.open('xb')as f:f.write(encoded(data))


def prepare():
    source={'first':('complete-context-s15a.json','first-context-catalog-v3-s26c.json'),'second':('second-context-s25a.json','context-catalog-s25e.json')};handles={};targets={};planned=[E/f'joint-target-{side}-{i}-s27a.json'for side,i in [('first',7),('second',7),('first',0),('second',0),('second',93)]]+[E/f'joint-request-{case}-s27a.json'for case in ['state7','platform','incompatible']]+[E/'joint-example-plan-s27a.json']
    if any(p.exists()for p in planned):raise FileExistsError('All example files must be new')
    for side,(context,catalog)in source.items():
        h=BoundCatalog(E/context,E/'model-precision-v3-s25c6.json',E/'color-partition-s22a.json',E/catalog,sha(E/catalog));ident,m,p,rows=h.checked();handles[side]=(h,ident,rows)
    for side,i in [('first',7),('second',7),('first',0),('second',0),('second',93)]:
        h,ident,rows=handles[side];path=E/f'joint-target-{side}-{i}-s27a.json';t=Target(ident,h.expected_catalog_sha256,strict_bits(rows[i]['writer_half_bits']));put(path,t.record());targets[side+':'+str(i)]={'file':path.name,'sha256':sha(path),'source_state_id':i,'evidence_origin':'existing conditional model catalog row; no new forward/host output','catalog_sha256':h.expected_catalog_sha256}
    examples={}
    for name,pairs in [('state7',[('first',7),('second',7)]),('platform',[('first',0),('second',0)]),('incompatible',[('first',7),('second',93)])]:
        observations=[]
        for side,i in pairs:
            h,ident,rows=handles[side];observations.append({'name':side,'context':h.context_file.name,'precision':h.precision_file.name,'partition':h.partition_file.name,'catalog':h.catalog_file.name,'catalog_sha256':h.expected_catalog_sha256,'target':targets[side+':'+str(i)]['file']})
        file=E/f'joint-request-{name}-s27a.json';put(file,{'schema':'psr-shared-field3-request-v1','shared_parameter':asdict(SharedField3(True)),'observations':observations});examples[name]={'request':file.name,'request_sha256':sha(file),'existing_model_target_rows':pairs}
    put(E/'joint-example-plan-s27a.json',{'scope':__doc__,'targets':targets,'examples':examples,'explicit_shared_raw_parameter_declaration':asdict(SharedField3(True)),'two_existing_contexts_only':True,'new_forward_or_kernel_calls':0,'targets_are_model_only':True});print(json.dumps({'model_only_target_files':5,'joint_requests':3,'new_forward_or_kernel_calls':0}));return examples


def audit(output):
    if output.exists():raise FileExistsError(output)
    results={n:load(E/f'joint-result-{n}-s27b2.json')for n in ['state7','platform','incompatible']};a=results['state7'];z=results['platform'];bad=results['incompatible']
    assert [o['query']['model_matching_state_ids']for o in a['observations']]==[[7,8,9],[7]]
    assert a['confirmed_joint_interface_state_ids']==[7]and a['confirmed_model_f32_population']==a['possible_f32_population']==860159 and a['unresolved_joint_f32_population']==0
    assert a['information']['joint_equal_to_single_possible_sets']==['second']and a['information']['extra_population_reduction_beyond_smallest_single']==0 and not a['information']['strictly_smaller_than_every_single_possible_set']
    assert not a['possible_joint_candidates'][0]['lower_closed']and not a['possible_joint_candidates'][0]['upper_closed']
    assert z['confirmed_joint_interface_state_ids']==[0,1]and z['confirmed_model_f32_population']==z['possible_f32_population']==1018499073 and not z['unique_parameter_claim']
    assert not bad['possible_joint_candidates']and bad['all_individual_possible_sets_nonempty']and not bad['single_target_invalidity_claim']and not bad['nearest_fallback_used']
    assert all(r['new_forward_or_original_kernel_calls']==0 and r['joint_class_acceptance']=='model_only'for r in results.values())
    assert all(o['catalog_provenance']['mode']=='exact accepted full catalog SHA'for r in results.values()for o in r['observations'])
    data={'scope':'audit of three saved joint API examples with pinned accepted-catalog provenance; interval algebra only','result_sha256':{n:sha(E/f'joint-result-{n}-s27b2.json')for n in results},'state7':{'first_matching_states':[7,8,9],'second_matching_states':[7],'joint_matching_states':[7],'first_f32_population':a['observations'][0]['known_f32_population'],'joint_f32_population':860159,'joint_equals_stronger_second':True,'extra_gain_beyond_second':0},'platform':{'joint_matching_states':[0,1],'joint_f32_population':1018499073,'multiple_solutions':True},'incompatible_pair':{'each_target_individually_has_model_candidates':True,'joint_candidates_empty':True,'individual_target_invalidity_claim':False,'nearest_fallback':False},'accepted_full_catalogs_pinned':True,'evidence_grade':'model_only; no joint original host experiment','new_model_forward_or_original_kernel_calls':0};put(output,data);print(json.dumps(data));return data


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);s=p.add_subparsers(dest='action',required=True);s.add_parser('prepare');q=s.add_parser('audit');q.add_argument('output',type=Path);a=p.parse_args();prepare()if a.action=='prepare'else audit(a.output)
