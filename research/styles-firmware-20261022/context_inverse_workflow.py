"""Reusable CLI for a bound catalog and control-blind exact target queries."""
from pathlib import Path
from dataclasses import asdict
import argparse,json
import numpy as np
from baseline_archive import sha,encoded
from context_color_api import BoundCatalog,Target,Identity,identity,strict_bits,seal_catalog,load


def solve(context,precision,partition,catalog,target_file,output):
    if output.exists():raise FileExistsError(output)
    d=load(target_file);target=Target(Identity(**d['identity']),d['catalog_sha256'],strict_bits(d['writer_half_bits']));handle=BoundCatalog(context,precision,partition,catalog,d['catalog_sha256']);result=handle.query(target);result['target_file_sha256']=sha(target_file);output.write_bytes(encoded(result));return result


def export_and_query(context,precision,partition,catalog,natives,output_dir):
    ident=identity(context,precision);names=['A','B'];results={}
    for name,file in zip(names,natives):
        native=load(file)
        if native['identity']['complete_context_sha256']!=sha(context):raise ValueError('Native target context mismatch')
        # No raw control is copied or supplied to the solver.
        bits=strict_bits(native['rows'][0]['native_half_bits']['writer']);target=Target(ident,sha(catalog),bits);t=output_dir/f'blind-target-{name}-s25e.json'
        if t.exists():raise FileExistsError(t)
        t.write_bytes(encoded(target.record()));results[name]=solve(context,precision,partition,catalog,t,output_dir/f'query-{name}-s25e.json')
    return results


def contains(result,raw):return any(i['first_f32_bits']<=raw<=i['last_f32_bits']for i in result['candidate_union'])


def analyze_and_boundaries(context,precision,partition,catalog,selection_file,query_files,output,boundary_output):
    if output.exists()or boundary_output.exists():raise FileExistsError(output)
    h=BoundCatalog(context,precision,partition,catalog,sha(catalog));ident,m,p,rows=h.checked();queries={n:load(f)for n,f in zip(['A','B'],query_files)};selection=load(selection_file);truth={n:c['raw_f32_bits']for n,c in zip(['A','B'],selection['target_controls'])}
    for n,q in queries.items():
        if q['identity']!=asdict(ident)or q['catalog_sha256']!=sha(catalog)or not q['coverage']['complete_model_coverage']:raise ValueError('Complete bound query required before candidate boundary selection')
        if not contains(q,truth[n]):raise AssertionError('True control not in exact candidates; preserve query, no nearest fallback')
    def state(raw):return next(c[3]for c in p['cells']if c[1]<=raw<=c[2])
    old_rows={}
    for f in sorted(output.parent.glob('scan-[0-9][0-9][0-9]-s22b.json')):
        for r in load(f)['rows']:old_rows[r['state_id']]=r
    def groups(records):
        g={}
        for i,r in records.items():
            if r['writer_known']:g.setdefault(r['writer_sha256'],[]).append(i)
        return sorted((sorted(ids)for ids in g.values()if len(ids)>1),key=lambda a:a[0])
    facts={}
    for name in queries:
        i=state(truth[name]);old_equiv=sorted(j for j,r in old_rows.items()if r['writer_sha256']==old_rows[i]['writer_sha256']);target=np.array(rows[i]['writer_half_bits'],dtype='u2');zero=np.array(rows[0]['writer_half_bits'],dtype='u2');facts[name]={'true_control_f32_bits':truth[name],'interface_state':i,'true_control_in_blind_candidates':True,'new_candidate_union':queries[name]['candidate_union'],'new_matching_states':queries[name]['model_matching_state_ids'],'old_context_matching_states_for_same_interface_state_writer':old_equiv,'writer_nonzero_effect_vs_new_scene_state0_half_components':int(np.count_nonzero(target!=zero))}
    old_bits={c['raw_f32_bits']for c in load(output.parent/'color-boundaries-s22c.json')['controls']};used=set(truth.values());controls={};omitted=[]
    for name,q in queries.items():
        for interval in q['candidate_union']:
            lo,hi=interval['first_f32_bits'],interval['last_f32_bits']
            for raw,kind in [(lo-1,'outside-lower-neighbor'),(lo,'first-included'),(hi,'last-included'),(hi+1,'outside-upper-neighbor')]:
                if not 0<=raw<=0x3ec00000 or raw in used or raw in old_bits:omitted.append({'target':name,'raw_f32_bits':raw,'kind':kind,'reason':'outside fixed domain or already executed target or old S22 boundary'});continue
                controls.setdefault(raw,{'id':'boundary-'+str(len(controls)),'raw_f32_bits':raw,'roles':[]})['roles'].append({'target':name,'kind':kind})
    if not 1<=len(controls)<=8:raise ValueError('Necessary new boundary controls exceed frozen budget; no silent truncation')
    for c in controls.values():
        i=state(c['raw_f32_bits']);c.update(state_id=i,expected_model_writer_sha256=rows[i]['writer_sha256'],expected_target_matches={n:contains(q,c['raw_f32_bits'])for n,q in queries.items()})
    data={'scope':'second independent synthetic scene, model collision analysis and necessary boundary plan; truth checked only after blind queries','identity':asdict(ident),'catalog_sha256':sha(catalog),'preselection_sha256':sha(selection_file),'facts':facts,'new_collision_groups':groups(rows),'old_context_historical_collision_groups':groups(old_rows),'new_unique_writer_outputs':len({r['writer_sha256']for r in rows.values()}),'old_unique_writer_outputs':len({r['writer_sha256']for r in old_rows.values()}),'scene_only_causal_comparison':False,'precision_caveat':'S25 uses explicit corrected final code3 powf profile; old S22 catalog retains old precision. Different context outputs/candidate groups are descriptive; no all-state cross-precision equivalence is claimed.','query_true_control_inputs':False,'universal_scene_invertibility_proved':False,'new_native_or_model_calls':0}
    output.write_bytes(encoded(data));boundary_output.write_bytes(encoded({'scope':'frozen rule applied after complete blind queries; no target mutation or old boundary rerun','identity':asdict(ident),'catalog_sha256':sha(catalog),'analysis_sha256':sha(output),'controls':list(controls.values()),'omitted':omitted,'maximum_controls':8,'original_calls_not_yet_run':True}));print(json.dumps({'true_controls_included':True,'facts':facts,'collision_groups':data['new_collision_groups'],'boundaries':len(controls)}));return data


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);s=p.add_subparsers(dest='action',required=True);q=s.add_parser('seal');q.add_argument('context',type=Path);q.add_argument('precision',type=Path);q.add_argument('partition',type=Path);q.add_argument('output',type=Path);q.add_argument('chunks',nargs='+',type=Path);q=s.add_parser('solve');q.add_argument('context',type=Path);q.add_argument('precision',type=Path);q.add_argument('partition',type=Path);q.add_argument('catalog',type=Path);q.add_argument('target',type=Path);q.add_argument('output',type=Path);a=p.parse_args()
    if a.action=='seal':seal_catalog(a.context,a.precision,a.partition,a.chunks,a.output)
    else:solve(a.context,a.precision,a.partition,a.catalog,a.target,a.output)
