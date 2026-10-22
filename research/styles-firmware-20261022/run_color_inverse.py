"""Enumerate, exhaustively scan and invert one frozen known-source color family."""
import argparse,hashlib,json,time
from pathlib import Path
import numpy as np
from active_color import Color,replace_color
from color_inverse import Domain,f32,u32,cell,signature,partition,verify_partition,runs,digest
from complete_fixture import decode
from complete_forward import forward
from select_active_color import CONTEXT_SHA

sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text())


def dump(path,data):path.write_text(json.dumps(data,separators=(',',':'),allow_nan=False)+'\n')
def targets(native):
    rows=load(native)['rows'];return {name:np.array(rows[index]['native_half_bits']['writer'],dtype='u2').view('f2')for name,index in [('platform',1),('point3',3)]}


def enumerate_domain(contract,output):
    if output.exists():raise FileExistsError(output)
    c=load(contract)
    if not c['all_checks_pass']or c['control']!='SSRParams field3 byte12, post-scene f32; no UI mapping':raise ValueError('Audited S21 color interface required')
    start=time.perf_counter();d=Domain();cells,states=partition(d);proof=verify_partition(d,cells,states)
    out={'scope':'finite domain chosen before reading target writer; exact raw half-cell cover and compressed logical interface states','domain':d.record(),'contract_sha256':sha(contract),'cell_columns':['half_bits','first_f32_bits','last_f32_bits','signature_id'],'cells':cells,'states':states,'coverage':proof,'elapsed_seconds':time.perf_counter()-start,'new_native_calls':0,'outside_domain_searched':False};dump(output,out);print(json.dumps({'coverage':proof,'elapsed_seconds':out['elapsed_seconds']}));return out


def validate_plan(p):
    d=Domain(p['domain']['first_f32_bits'],p['domain']['last_f32_bits']);return d,verify_partition(d,p['cells'],p['states'])


def scan(plan_file,context_file,native_file,start,count,output):
    if output.exists():raise FileExistsError(output)
    if type(start)is not int or type(count)is not int or start<0 or not 1<=count<=16:raise ValueError('At most16 states per bounded model run')
    p=load(plan_file);validate_plan(p)
    if sha(context_file)!=CONTEXT_SHA:raise ValueError('Exact known S15 raw source and auxiliary inputs required')
    base=decode(load(context_file));goal=targets(native_file);selected=p['states'][start:start+count]
    if not selected:raise ValueError('Empty scan not accepted')
    result={'scope':'fresh full conditional point-model evaluation per interface state; target bytes used only for comparison, not forward lookup','plan_sha256':sha(plan_file),'base_context_sha256':CONTEXT_SHA,'native_targets_sha256':sha(native_file),'start':start,'requested_count':count,'rows':[],'new_original_host_calls':0,'point_is_set_acceptance':False};dump(output,result);begin=time.perf_counter()
    for s in selected:
        control=Color(f32(s['representative_f32_bits']));t=time.perf_counter();r=forward(replace_color(base,control),point=True);row={'state_id':s['id'],'representative_f32_bits':s['representative_f32_bits'],'key':list(signature(control.raw)),'pixel_unknowns':r.pixel_unknowns,'internal_unknowns':r.internal_unknowns,'writer_known':r.writer is not None,'model_elapsed_seconds':time.perf_counter()-t}
        if r.writer is not None:
            a=r.writer.output.pixels.lo.astype('f2');row.update(writer_sha256=digest(a),writer_half_bits=a.view('u2').tolist(),matches={n:bool(np.array_equal(a.view('u2'),b.view('u2')))for n,b in goal.items()},different_half_components={n:int(np.count_nonzero(a.view('u2')!=b.view('u2')))for n,b in goal.items()})
        result['rows'].append(row);result['elapsed_seconds']=time.perf_counter()-begin;dump(output,result)
    print(json.dumps({'start':start,'states':len(result['rows']),'unknown':sum(not v['writer_known']for v in result['rows']),'matches':{n:[v['state_id']for v in result['rows']if v.get('matches',{}).get(n)]for n in goal},'elapsed_seconds':result['elapsed_seconds']}));return result


def aggregate(plan_file,context_file,native_file,chunks,output,boundary_output):
    if output.exists()or boundary_output.exists():raise FileExistsError(output)
    p=load(plan_file);domain,coverage=validate_plan(p);goal=targets(native_file);seen={};chunk_hashes={}
    for file in chunks:
        data=load(file)
        if data['plan_sha256']!=sha(plan_file)or data['base_context_sha256']!=CONTEXT_SHA or data['native_targets_sha256']!=sha(native_file):raise ValueError('Incompatible search chunk')
        expected=list(range(data['start'],min(data['start']+data['requested_count'],len(p['states']))))
        if not 1<=data['requested_count']<=16 or [v['state_id']for v in data['rows']]!=expected:raise ValueError('Chunk state coverage differs from requested bounded slice')
        chunk_hashes[file.name]=sha(file)
        for row in data['rows']:
            i=row['state_id']
            if type(i)is not int or not 0<=i<len(p['states']):raise ValueError('State ID outside finite domain')
            if i in seen:raise ValueError('Duplicate state evaluation')
            state=p['states'][i]
            if row['key']!=state['key']or row['representative_f32_bits']!=state['representative_f32_bits']:raise ValueError('State representative/key altered')
            if row['writer_known']:
                a=np.array(row['writer_half_bits'],dtype='u2').view('f2')
                if digest(a)!=row['writer_sha256']or any(row['matches'][n]!=np.array_equal(a.view('u2'),g.view('u2'))for n,g in goal.items()):raise ValueError('Writer matching ledger inconsistent')
            seen[i]=row
    all_ids=set(range(len(p['states'])));missing=sorted(all_ids-seen.keys());unknown=sorted(i for i,r in seen.items()if not r['writer_known']);complete=not missing and not unknown
    candidates={};native=load(native_file);old_witnesses={}
    for index,row in enumerate(native['rows']):old_witnesses.setdefault(signature(np.float32(row['control']['raw_f32'])),[]).append(index)
    for name in goal:
        matching={i for i,r in seen.items()if r.get('matches',{}).get(name)};classes=[]
        for i in sorted(matching):
            state=p['states'][i];witnesses=[j for j in old_witnesses.get(tuple(state['key']),[])if np.array_equal(np.array(native['rows'][j]['native_half_bits']['writer'],dtype='u2'),goal[name].view('u2'))]
            classes.append({'state_id':i,'key':state['key'],'intervals':runs(domain,p['cells'],{i}),'proved_equivalence':'within each signature under the audited logical half/f32 control interface; half-cell raw preimages exact under IEEE RN-even','writer_match':'fresh independent point model exact full writer bytes','existing_original_host_witness_rows':witnesses,'original_GPU_proved':False})
        candidates[name]={'target_writer_sha256':digest(goal[name]),'model_matching_state_ids':sorted(matching),'candidate_interface_classes':classes,'candidate_union':runs(domain,p['cells'],matching),'all_found_f32_population':sum(s['f32_population']for s in p['states']if s['id']in matching),'complete_model_search_within_domain':complete,'unique_parameter':False,'maximal_final_writer_equivalence_over_all_nonnegative_f32':False}
    point3_cell=cell(int(np.float16(.3).view('u2')),domain)
    def contains(name,bits):return any(v['first_f32_bits']<=bits<=v['last_f32_bits']for v in candidates[name]['candidate_union'])
    if complete and(not contains('platform',u32(.01))or not contains('platform',u32(.02))or not contains('point3',point3_cell['first_f32_bits'])or not contains('point3',point3_cell['last_f32_bits'])):raise AssertionError('Required multiple preimages omitted')
    result={'scope':'bounded known-source inversion prototype returning equivalence candidates, not a unique estimate','plan_sha256':sha(plan_file),'base_context_sha256':sha(context_file),'native_targets_sha256':sha(native_file),'domain':domain.record(),'coverage':dict(coverage,searched_interface_states=len(seen),missing_state_ids=missing,unknown_state_ids=unknown,complete_model_coverage=complete),'chunks_sha256':chunk_hashes,'model_forward_evaluations':len(seen),'model_search_elapsed_seconds_sum':sum(load(f)['elapsed_seconds']for f in chunks),'candidates':candidates,'required_point3_half_cell':point3_cell,'required_platform_raw_bits':[u32(.01),u32(.02)],'not_searched':{'canonical_nonnegative_above_domain':{'first_f32_bits':domain.last_bits+1,'last_f32_bits':0x7f7fffff},'negative_zero_bits':0x80000000,'negative_controls':'excluded by chosen nonnegative domain','UI_parameters_unknown_source_and_original_GPU':'outside task contract'},'RichSat_set_zero_denominator_outer_enclosure':'retained independently; point exhaustive search is not set-domain acceptance','new_original_host_calls':0,'actual_original_host_exhaustive_over_domain':False};dump(output,result)
    if not complete:raise ValueError('Incomplete model search; partial candidate result retained; no original boundary plan')
    proposed={};old_raw={int(r['control']['raw_f32_bits'])for r in native['rows']}
    def add(bits,reason):
        if not domain.first_bits<=bits<=domain.last_bits or bits in old_raw:return
        proposed.setdefault(bits,[]).append(reason)
    for name,c in candidates.items():
        for span in c['candidate_union']:
            for bits,label in [(span['first_f32_bits'],'first included'),(span['last_f32_bits'],'last included'),(span['first_f32_bits']-1,'adjacent below'),(span['last_f32_bits']+1,'adjacent above')]:add(bits,name+': '+label)
    zero_edge=cell(0,domain)['last_f32_bits'];add(zero_edge,'zero-half-bin last f32');add(zero_edge+1,'zero-half-bin adjacent positive half')
    proposed_keys={signature(f32(b))for b in proposed}
    for name,c in candidates.items():
        for i in c['model_matching_state_ids']:
            state=p['states'][i]
            if tuple(state['key'])not in old_witnesses and tuple(state['key'])not in proposed_keys:add(state['representative_f32_bits'],name+': candidate signature without original witness')
    if len(proposed)>16:raise ValueError('More than16 necessary boundary controls; do not silently expand original run')
    checks=[]
    for bits,reasons in sorted(proposed.items()):
        key=list(signature(f32(bits)));state_id=next(s['id']for s in p['states']if s['key']==key);checks.append({'raw_f32_bits':bits,'raw_f32_hex':f'0x{bits:08x}','raw_f32':float(f32(bits)),'state_id':state_id,'key':key,'reasons':reasons,'expected_matches':{n:contains(n,bits)for n in goal},'expected_writer_sha256':seen[state_id]['writer_sha256']})
    boundary={'scope':'necessary matched/unmatched model-boundary controls after complete finite search; old five raw values are not rerun','inverse_sha256':sha(output),'plan_sha256':sha(plan_file),'base_context_sha256':CONTEXT_SHA,'native_targets_sha256':sha(native_file),'complete_model_coverage_before_native':True,'controls':checks,'existing_raw_controls_reused':sorted(old_raw),'original_GPU_verified':False};dump(boundary_output,boundary)
    print(json.dumps({'coverage':result['coverage'],'matching_states':{n:v['model_matching_state_ids']for n,v in candidates.items()},'candidate_unions':{n:v['candidate_union']for n,v in candidates.items()},'necessary_new_native_controls':len(checks)}));return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='action',required=True)
    q=sub.add_parser('enumerate');q.add_argument('contract',type=Path);q.add_argument('output',type=Path)
    q=sub.add_parser('scan');q.add_argument('plan',type=Path);q.add_argument('context',type=Path);q.add_argument('native',type=Path);q.add_argument('start',type=int);q.add_argument('count',type=int);q.add_argument('output',type=Path)
    q=sub.add_parser('aggregate');q.add_argument('plan',type=Path);q.add_argument('context',type=Path);q.add_argument('native',type=Path);q.add_argument('output',type=Path);q.add_argument('boundary',type=Path);q.add_argument('chunks',nargs='+',type=Path);a=p.parse_args()
    if a.action=='enumerate':enumerate_domain(a.contract,a.output)
    elif a.action=='scan':scan(a.plan,a.context,a.native,a.start,a.count,a.output)
    else:aggregate(a.plan,a.context,a.native,a.chunks,a.output,a.boundary)
