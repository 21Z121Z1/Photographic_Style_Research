"""Replay frozen original-host outputs; classify one known-source control only."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from complete_fixture import decode
from complete_forward import forward
from native_complete_check import comparisons
from active_color import Color


def decode_native(row):return {n:np.array(v,dtype='u2').view('f2')for n,v in row['native_half_bits'].items()}
def difference(a,b):return {'different_half_components':int(np.count_nonzero(a.view('u2')!=b.view('u2'))),'max_absolute_difference':float(np.max(abs(a.astype('f8')-b.astype('f8'))))}


def check(context_file,native_file,contract_file,output):
    if output.exists():raise FileExistsError(output)
    contexts=json.loads(context_file.read_text());native=json.loads(native_file.read_text());contract=json.loads(contract_file.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    if native['contexts_sha256']!=sha(context_file)or native['contract_sha256']!=sha(contract_file):raise ValueError('Paired exact inputs/host receipt required')
    rows=[];images=[];points=[]
    for c,n in zip(contexts['rows'],native['rows']):
        a=decode_native(n);images.append(a);point=forward(decode(c['context']),point=True);comparison=comparisons(a,point);points.append(comparison);control=c['control'];extra={}
        for key,value in [('color_half357',control['half357']),('color_gain364',control['gain364'])]:extra[key]=bool(np.all(a[key]==np.float16(value)))
        rows.append({'control':control,'point':comparison,'control_diagnostics_match':extra,'native_effect_vs_raw_zero':{k:difference(images[0][k],v)for k,v in a.items()},'nonzero_effect_at_writer':difference(images[0]['writer'],a['writer'])['different_half_components']>0})
    pairs=[]
    for i in range(len(rows)):
        for j in range(i+1,len(rows)):
            diff={k:difference(v,images[j][k])for k,v in images[i].items()};same=diff['writer']['different_half_components']==0;pairs.append({'indices':[i,j],'raw_f32_values':[rows[i]['control']['raw_f32'],rows[j]['control']['raw_f32']],'classification':'indistinguishable_at_saved_host_writer'if same else'distinguishable_at_saved_host_writer','differences':diff,'all_scientific_RGB_intermediates_equal':all(v['different_half_components']==0 for k,v in diff.items()if k not in ['color_half357','color_gain364','color_protect384']),'unique_parameter_recovery_proved':False})
    # The only auxiliary relation: same upstream3x4 source at active color.3.
    active_index=next(i for i,v in enumerate(rows)if v['control']['raw_f32_bits']==int(np.float32(.3).view('u4')));c=decode(contexts['rows'][active_index]['context']);sets={}
    for shared in [False,True]:
        result=forward(c,point=False,shared_semantic=shared);sets['shared'if shared else'independent']=comparisons(images[active_index],result)
    subset=sets['shared'];r={'scope':__doc__,'context_sha256':sha(context_file),'native_sha256':sha(native_file),'contract_sha256':sha(contract_file),'new_original_host_calls':0,'rows':rows,'pairs':pairs,'equivalent_raw_half_interval':contract['half_bin'],'positive_gain_one_plateau':contract['plateau'],'conditional_inverse_status':{'known_source_and_auxiliary_context':True,'control':'post-scene raw color byte12 only','distinguishable':'raw0 vs raw.3, and other reported unequal finite pairs','nonidentifiable':'two distinct half controls .01/.02 and raw.3/next-f32 witnesses; declared interface intervals','unproved':'maximal equivalence classes, injectivity after quotienting, other controls/contexts, original GPU, unknown-source finished-photo inverse','finite_difference_or_fit_is_uniqueness_proof':False},'auxiliary_shared_semantic':{'active_context_index':active_index,'default_backend_changed':False,'only_relation':'same reference196,BG/FG gain branch and person96 atprecomputed335','results':sets,'writer_set_really_generated':subset['writer_known'],'independent_vs_shared_widths':{k:{side:sets[side]['observations'].get(k,{}).get('max_width')for side in ['independent','shared']}for k in ['precomputed335','semantic347','BG352','FG354','saturated374','output392','warm409']},'whole_set_verified':False},'old_neutral_selective_unknown12_and_internal24_preserved':True,'nine_consumer_cache_breakpoint_preserved':True,'original_GPU_or_real_frame_verified':False}
    output.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n');print(json.dumps({'point_mismatches':[sum(v['half_bit_mismatches']for v in p['observations'].values())for p in points],'native_writer_nonzero_components':[v['native_effect_vs_raw_zero']['writer']['different_half_components']for v in rows],'writer_equal_pairs':sum(p['classification'].startswith('indistinguishable')for p in pairs),'auxiliary_widths':r['auxiliary_shared_semantic']['independent_vs_shared_widths'],'auxiliary_first_unknown':{k:v['first_unknown']for k,v in sets.items()}}))
    if any(v['half_bit_mismatches']for p in points for v in p['observations'].values())or any(not v for row in rows for v in row['control_diagnostics_match'].values()):raise AssertionError('Point mismatch; complete receipt retained')
    if any(not v.get('range_covered',True)for v in subset['observations'].values()):raise AssertionError('Shared semantic set misses original native; receipt retained')
    return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('contexts',type=Path);p.add_argument('native',type=Path);p.add_argument('contract',type=Path);p.add_argument('output',type=Path);a=p.parse_args();check(a.contexts,a.native,a.contract,a.output)
