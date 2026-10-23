"""First-scene saved host replay and comparison of two SAME-v3 catalogs.

No original kernel invocation, no changed controls or domain. Historical raw
host outputs remain immutable; any discrepancy is saved before stopping.
"""
from pathlib import Path
from dataclasses import asdict
import argparse,json,time
import numpy as np
from baseline_archive import sha,encoded
from context_color_api import identity,BoundCatalog,Target,strict_bits,load
from complete_fixture import decode
from complete_forward import forward
from active_color import Color,replace_color
from color_inverse import f32,digest,runs,Domain
from native_complete_check import comparisons

ROOT=Path(__file__).parent;E=ROOT/'evidence'


def replay(context,precision,s21,s24,output):
    if output.exists():raise FileExistsError(output)
    ident=identity(context,precision);v21=load(E/'verification-s21.json');v24=load(E/'verification-s24.json')
    if sha(s21)!=v21['evidence_sha256'][s21.name]or sha(s24)!=v24['evidence_sha256'][s24.name]:raise ValueError('Exact saved original outputs required')
    old=load(s21);baseline=load(s24);base=decode(load(context));selected=[]
    for i,row in enumerate(old['rows']):selected.append((s21.name,i,row['control']['raw_f32_bits'],row['native_half_bits']))
    for i,row in enumerate(baseline['rows']):selected.append((s24.name,i,row['control']['raw_f32_bits'],{**baseline['prefix_native_half_bits'],**row['native_half_bits']}))
    if len(selected)!=13 or len({s[2]for s in selected})!=13:raise ValueError('Only the existing thirteen distinct finite first-scene controls')
    result={'scope':__doc__,'identity':asdict(ident),'saved_original_sha256':{f.name:sha(f)for f in [s21,s24]},'precision_contract_sha256':sha(precision),'native_calls':0,'new_point_calls':0,'rows':[],'status':'in_progress'}
    def save():output.write_bytes(encoded(result))
    save();begin=time.perf_counter()
    for receipt,index,raw,arrays in selected:
        native={n:np.array(a,dtype='u2').view('f2')for n,a in arrays.items()};point=forward(replace_color(base,Color(f32(raw))),point=True);cmp=comparisons(native,point);different={};row={'saved_receipt':receipt,'saved_row':index,'raw_f32_bits':raw,'point':cmp,'point_observation_sha256':{n:digest(v.lo.astype('f2'))for n,v in point.observations.items()}};result['rows'].append(row);result['new_point_calls']+=1
        for name,m in cmp['observations'].items():
            if not m['half_bit_mismatches']:continue
            model=point.observations[name].lo.astype('f2');actual=native[name];actual=actual[...,0]if actual.shape==model.shape+(1,)else actual;different[name]={'native_half_bits':actual.view('u2').tolist(),'model_half_bits':model.view('u2').tolist(),'first_differing_index':np.argwhere(actual.view('u2')!=model.view('u2'))[0].tolist()}
        row['differences']=different;result['elapsed_seconds']=time.perf_counter()-begin;save()
        if different or not cmp['writer_known']or cmp['pixel_unknowns']:
            result['status']='failed_first_saved_v3_replay_difference';save();raise AssertionError('Saved first-scene v3 discrepancy retained; no catalog scan authorized yet')
    result['status']='passed_thirteen_saved_first_scene_v3_points';result['all_point_half_bit_mismatches']=0;result['whole_contexts_not_GPU_proofs']=True;save();print(json.dumps({'status':result['status'],'point_calls':13,'native_calls':0,'half_bit_mismatches':0,'elapsed_seconds':result['elapsed_seconds']}));return result


def compare(first_context,second_context,precision,partition,first_catalog,second_catalog,replay_file,output):
    if output.exists():raise FileExistsError(output)
    replay_data=load(replay_file)
    if replay_data['status']!='passed_thirteen_saved_first_scene_v3_points'or replay_data['precision_contract_sha256']!=sha(precision):raise ValueError('Saved first-scene replay must pass under this exact precision')
    first=BoundCatalog(first_context,precision,partition,first_catalog,sha(first_catalog));second=BoundCatalog(second_context,precision,partition,second_catalog,sha(second_catalog));one,ma,p,ra=first.checked();two,mb,pb,rb=second.checked()
    if one.precision_contract_sha256!=two.precision_contract_sha256 or len(ra)!=146 or len(rb)!=146 or not all(x['writer_known']for x in [*ra.values(),*rb.values()]):raise ValueError('Two complete exact SAME-precision146 catalogs required')
    def groups(rows):
        g={}
        for i,r in rows.items():g.setdefault(r['writer_sha256'],[]).append(i)
        return sorted((sorted(ids)for ids in g.values()),key=lambda ids:ids[0])
    ga,gb=groups(ra),groups(rb);class_a={i:ids for ids in ga for i in ids};class_b={i:ids for ids in gb for i in ids};changed=[i for i in range(146)if class_a[i]!=class_b[i]];queried={};queries={}
    for label,handle,rows in [('first',first,ra),('second',second,rb)]:
        ident=one if label=='first'else two;path=first_catalog if label=='first'else second_catalog
        for i in [0,1,17,93,122]:
            t=Target(ident,sha(path),strict_bits(rows[i]['writer_half_bits']));q=handle.query(t);queries[label+':'+str(i)]=q;queried[label+':'+str(i)]={'model_matching_state_ids':q['model_matching_state_ids'],'candidate_union':q['candidate_union'],'population':q['found_f32_population']}
    rejects={}
    for label,handle,other,path in [('first_catalog_with_second_target',first,two,first_catalog),('second_catalog_with_first_target',second,one,second_catalog)]:
        try:handle.query(Target(other,sha(path),strict_bits(ra[17]['writer_half_bits'])))
        except ValueError as ex:rejects[label]=str(ex)
        else:raise AssertionError('Cross-context target unexpectedly accepted')
    # All146 class equivalence relationships are compared, not inferred only
    # from the ten example queries. Each contains exact writer bit arrays.
    first_pairs={(i,j)for i in range(146)for j in range(i+1,146)if ra[i]['writer_half_bits']==ra[j]['writer_half_bits']};second_pairs={(i,j)for i in range(146)for j in range(i+1,146)if rb[i]['writer_half_bits']==rb[j]['writer_half_bits']}
    result={'scope':'same-v3 comparison of two fixed synthetic146-state catalogs, no native calls or universal injectivity proof','precision_contract_sha256':sha(precision),'identities':{'first':asdict(one),'second':asdict(two)},'catalog_sha256':{'first':sha(first_catalog),'second':sha(second_catalog)},'fresh_first_catalog':True,'old_S22_catalog_relabelled':False,'first_scene_replay_sha256':sha(replay_file),'unique_writer_counts':{'first':len(ga),'second':len(gb)},'collision_groups':{'first':[x for x in ga if len(x)>1],'second':[x for x in gb if len(x)>1]},'all146_classes_compared':True,'changed_class_state_ids':changed,'cross_state_collision_pairs_first':sorted(first_pairs),'cross_state_collision_pairs_second':sorted(second_pairs),'added_pairs':sorted(second_pairs-first_pairs),'removed_pairs':sorted(first_pairs-second_pairs),'same_state_writer_arrays_differ_between_contexts':sum(ra[i]['writer_half_bits']!=rb[i]['writer_half_bits']for i in range(146)),'example_queries':queried,'cross_context_target_rejections':rejects,'context_swap_rejected':True,'new_model_or_native_calls':0,'universal_scene_inverse_proved':False,'UI_or_unknown_source_inverse_proved':False}
    output.write_bytes(encoded(result));print(json.dumps({'unique_writers':result['unique_writer_counts'],'collisions':result['collision_groups'],'changed_classes':changed,'same_state_different_writers':result['same_state_writer_arrays_differ_between_contexts'],'cross_context_rejected':True}));return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);s=p.add_subparsers(dest='action',required=True);q=s.add_parser('replay');q.add_argument('context',type=Path);q.add_argument('precision',type=Path);q.add_argument('s21',type=Path);q.add_argument('s24',type=Path);q.add_argument('output',type=Path);q=s.add_parser('compare');q.add_argument('first_context',type=Path);q.add_argument('second_context',type=Path);q.add_argument('precision',type=Path);q.add_argument('partition',type=Path);q.add_argument('first_catalog',type=Path);q.add_argument('second_catalog',type=Path);q.add_argument('replay',type=Path);q.add_argument('output',type=Path);a=p.parse_args()
    if a.action=='replay':replay(a.context,a.precision,a.s21,a.s24,a.output)
    else:compare(a.first_context,a.second_context,a.precision,a.partition,a.first_catalog,a.second_catalog,a.replay,a.output)
