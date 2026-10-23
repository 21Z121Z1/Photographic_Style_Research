"""Joint candidates for EXPLICITLY shared same raw field3, two known scenes.

Only existing accepted v3 context families are supported. This intersects
verified catalog results; it does not evaluate a model or original kernel.
"""
from dataclasses import dataclass,asdict,replace
from pathlib import Path
import argparse,json
import numpy as np
from baseline_archive import sha,encoded
from context_color_api import BoundCatalog,Target,Identity,strict_bits,load
from bright137_witness import require_inverse_scope
from raw_f32_sets import Interval,normalize,intersection,intersect_all,difference,population,records,same_members,LAST

FIELD='post-scene SSRParams.color field3 byte12 raw f32'
V3='9358741644914631950a72161b25967ba9c433400d1faf3dbb4267db1fb036da'
CONTEXTS=frozenset({'ffae597ca79f92447a2bdae45bbc007450be27ae9165bef78d0e6b3cb0932b11','37d3385222f3f42988d79dbbe5db89c3147c6988f5c0b7ef9ff10bab97031be6'})
VERSION=('iPhone17,3','24A446','SmartStyleV1','CMISmartStyleProcessorV1',0)
ACCEPTED={
 'ffae597ca79f92447a2bdae45bbc007450be27ae9165bef78d0e6b3cb0932b11':('first-context-catalog-v3-s26c.json','6c49f76d35aef61b1c6c4bf432aa5d24e72b343e6e15fe9f351914e80a29b6ce'),
 '37d3385222f3f42988d79dbbe5db89c3147c6988f5c0b7ef9ff10bab97031be6':('context-catalog-s25e.json','5e943c91fe441c55c4fd9bd023daf74cbe5db3afbe4365b5cdc727960bfe5ba6')}


@dataclass(frozen=True)
class SharedField3:
    same_raw_f32_across_contexts:bool
    field_definition:str=FIELD

    def __post_init__(self):
        if type(self.same_raw_f32_across_contexts)is not bool:raise TypeError('Explicit boolean shared-RAW declaration required')
        if not self.same_raw_f32_across_contexts:raise ValueError('Caller must affirm the SAME post-scene field3 raw f32, not merely common UI settings')
        if self.field_definition!=FIELD:raise ValueError('Only the explicitly defined post-scene field3 raw parameter may be shared')


@dataclass(frozen=True)
class Observation:
    name:str
    catalog:BoundCatalog
    target:Target

    def __post_init__(self):
        if type(self.name)is not str or not self.name.strip()or len(self.name)>80:raise ValueError('Short nonempty unique observation label required')
        if not isinstance(self.catalog,BoundCatalog)or not isinstance(self.target,Target):raise TypeError('Bound catalog and typed context-specific target required')


@dataclass(frozen=True)
class Contract:
    version:tuple
    precision_sha256:str
    domain:tuple
    field_definition:str
    partition_sha256:str


def compatible(contracts):
    if not contracts or any(not isinstance(c,Contract)for c in contracts):raise TypeError('Verified contracts required')
    first=contracts[0]
    if any(c.version!=first.version for c in contracts):raise ValueError('Different build/internal/ABI versions cannot share this joint catalog contract')
    if any(c.domain!=first.domain for c in contracts):raise ValueError('Different raw parameter domains cannot be silently intersected')
    if any(c.field_definition!=first.field_definition for c in contracts):raise ValueError('Different parameter field definitions')
    if any(c.precision_sha256!=first.precision_sha256 for c in contracts):raise ValueError('Different model precision contracts')
    if any(c.partition_sha256!=first.partition_sha256 for c in contracts):raise ValueError('Different interface partitions')
    if first.version!=VERSION or first.precision_sha256!=V3 or first.domain!=(0,LAST)or first.field_definition!=FIELD:raise ValueError('Only the already accepted v3/field3/canonical+0..3/8 scope is supported')
    return first


def _binding(observation):
    h=observation.catalog;ident,manifest,plan,rows=h.checked();p=load(h.precision_file)
    if ident.complete_context_sha256 not in CONTEXTS:raise ValueError('Scene scope is limited to the two existing frozen contexts')
    context=load(h.context_file);require_inverse_scope(int(np.array(context['raw_f32_bits']['params'],dtype='u4')[0]),frozenset({3}))
    contract=Contract((ident.hardware,ident.build,ident.bundle,ident.processor_class,ident.main_version_argument),ident.precision_contract_sha256,(p['domain']['first_f32_bits'],p['domain']['last_f32_bits']),p['free_parameter'],sha(h.partition_file))
    filename,expected=ACCEPTED[ident.complete_context_sha256]
    if h.expected_catalog_sha256==expected:mode='exact accepted full catalog SHA'
    else:
        baseline=replace(h,catalog_file=Path(__file__).parent/'evidence'/filename,expected_catalog_sha256=expected).checked()[3]
        for i,row in rows.items():
            if row['writer_known']and any(row[k]!=baseline[i][k]for k in ['key','representative_f32_bits','writer_half_bits','writer_sha256']):raise ValueError('Partial known rows must equal existing accepted catalog rows; new writer injection is outside this API scope')
        mode='partial: known rows exactly match accepted full catalog; only omissions/unknowns allowed'
    provenance={'mode':mode,'accepted_full_catalog_sha256':expected,'known_rows_verified':sum(r['writer_known']for r in rows.values()),'unknown_state_ids':sorted(i for i,r in rows.items()if not r['writer_known']),'missing_state_ids':sorted(set(range(146))-rows.keys()),'new_model_rows_accepted':False}
    return ident,contract,provenance


def solve_joint(observations:tuple,*,shared_parameter:SharedField3):
    if not isinstance(shared_parameter,SharedField3):raise TypeError('Explicit SharedField3 declaration is mandatory')
    if type(observations)is not tuple or not 2<=len(observations)<=8 or any(not isinstance(o,Observation)for o in observations):raise TypeError('Two to eight typed observations of the supported frozen contexts required')
    if len({o.name for o in observations})!=len(observations):raise ValueError('Observation labels must be unique')
    bindings=[_binding(o)for o in observations];common=compatible([c for i,c,p in bindings]);distinct={i.complete_context_sha256 for i,c,p in bindings}
    if len(distinct)<2:raise ValueError('At least two distinct supported frozen contexts are required')
    singles=[];known=[];possible=[]
    for o,(ident,c,provenance)in zip(observations,bindings):
        q=o.catalog.query(o.target)
        if q['domain']['first_f32_bits']!=common.domain[0]or q['domain']['last_f32_bits']!=common.domain[1]:raise ValueError('Query domain changed after contract validation')
        k=normalize(Interval.read(d)for d in q['candidate_union']);u=normalize(Interval.read(d)for d in q['unresolved_possible_union']);p=normalize((*k,*u));known.append(k);possible.append(p);singles.append({'name':o.name,'identity':asdict(ident),'catalog_sha256':o.catalog.expected_catalog_sha256,'catalog_provenance':provenance,'target_writer_sha256':__import__('hashlib').sha256(o.target.writer_half_bits.tobytes()).hexdigest(),'query':q,'known_model_candidates':records(k),'possible_candidates_including_unresolved':records(p),'known_f32_population':population(k),'possible_f32_population':population(p),'coverage_complete':q['coverage']['complete_model_coverage']})
    confirmed=intersect_all(known);allowed=intersect_all(possible);unresolved=difference(allowed,confirmed);count=population(allowed);confirmed_count=population(confirmed);smallest=min(population(p)for p in possible)
    if not allowed:status='no_common_raw_parameter_candidate_in_the_declared_model_domain'
    elif unresolved:status='possible_joint_candidates_with_unresolved_catalog_regions'
    else:status='exact_joint_model_candidate_set'
    equal=[o.name for o,p in zip(observations,possible)if same_members(p,allowed)];state_ids=set(singles[0]['query']['model_matching_state_ids'])
    for s in singles[1:]:state_ids.intersection_update(s['query']['model_matching_state_ids'])
    return {'schema':'psr-joint-known-context-field3-v1','status':status,'shared_parameter_declaration':asdict(shared_parameter),'shared_raw_parameter_is_caller_assumption_not_inferred':True,'contract':asdict(common),'distinct_supported_contexts':len(distinct),'observations':singles,'confirmed_model_joint_candidates':records(confirmed),'confirmed_model_f32_population':confirmed_count,'confirmed_joint_interface_state_ids':sorted(state_ids),'state_ids_are_display_only_raw_intervals_are_primary':True,'possible_joint_candidates':records(allowed),'possible_f32_population':count,'unresolved_joint_candidates':records(unresolved),'unresolved_joint_f32_population':population(unresolved),'all_single_catalogs_complete':all(s['coverage_complete']for s in singles),'joint_unresolved_region_empty':not unresolved,'missing_unknown_never_treated_as_excluded':True,'all_individual_possible_sets_nonempty':all(bool(p)for p in possible),'information':{'joint_equal_to_single_possible_sets':equal,'reduction_from_each_single_possible_population':{o.name:population(p)-count for o,p in zip(observations,possible)},'extra_population_reduction_beyond_smallest_single':smallest-count,'strictly_smaller_than_every_single_possible_set':bool(allowed)and not equal,'information_gain_interpretation_applicable':bool(allowed),'no_extra_elimination_beyond_equal_single_inputs':bool(equal)},'evidence_levels':{'interval_algebra':'exact raw f32 set operations and populations; retained binary real endpoints/closure','single_matches':'verified existing conditional point-model catalog rows only; partial coverage disclosed','shared_parameter':'explicit caller declaration, not a firmware/UI equivalence finding','joint_original_host_witness':'not supplied or promoted by this API','GPU_UI_or_unknown_source_inverse':'unverified'},'joint_class_acceptance':'model_only','single_target_invalidity_claim':False,'nearest_fallback_used':False,'unique_parameter_claim':False,'new_forward_or_original_kernel_calls':0,'joint_API_source_sha256':sha(Path(__file__)),'raw_interval_source_sha256':sha(Path(__file__).with_name('raw_f32_sets.py'))}


def solve_request(request_file:Path,output_file:Path):
    if output_file.exists():raise FileExistsError(output_file)
    data=load(request_file)
    if data.get('schema')!='psr-shared-field3-request-v1':raise ValueError('Explicit joint request schema required')
    if 'shared_parameter'not in data:raise ValueError('Mandatory explicit shared raw parameter declaration missing')
    declaration=SharedField3(**data['shared_parameter']);observations=[];files={request_file:sha(request_file)}
    for row in data['observations']:
        paths={n:(request_file.parent/row[n]).resolve()for n in ['context','precision','partition','catalog','target']};files.update({p:sha(p)for p in paths.values()});t=load(paths['target']);target=Target(Identity(**t['identity']),t['catalog_sha256'],strict_bits(t['writer_half_bits']));h=BoundCatalog(paths['context'],paths['precision'],paths['partition'],paths['catalog'],row['catalog_sha256'])
        for part in load(paths['catalog'])['chunks']:
            if Path(part['name']).name!=part['name']:raise ValueError('Catalog-relative chunk name required')
            path=paths['catalog'].parent/part['name'];files[path]=sha(path)
        observations.append(Observation(row['name'],h,target))
    result=solve_joint(tuple(observations),shared_parameter=declaration)
    if any(sha(p)!=h for p,h in files.items()):raise ValueError('Joint request/input files changed during solve')
    result.update(request_sha256=files[request_file],file_inputs_sha256={str(i)+':'+p.name:h for i,(p,h)in enumerate(files.items())},input_files_unchanged_during_solve=True);output_file.write_bytes(encoded(result));print(json.dumps({'status':result['status'],'confirmed_population':result['confirmed_model_f32_population'],'possible_population':result['possible_f32_population'],'equal_to_single':result['information']['joint_equal_to_single_possible_sets'],'new_forward_or_kernel_calls':0}));return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('request',type=Path);p.add_argument('output',type=Path);a=p.parse_args();solve_request(a.request,a.output)
