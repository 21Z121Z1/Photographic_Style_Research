"""New phase using S25's already persisted compiler inputs/products.

The failed initial all-observation acceptance remains failed. This narrower
phase checks the selected writer path and reports every unselected bright bit
difference, after a static proof and first-arithmetic diagnostic. No numeric
tolerance or candidate budget is changed; any other difference still stops.
"""
from pathlib import Path
import argparse,ctypes,json,re,hashlib
import numpy as np
from baseline_archive import Archive,sha,encoded
from baseline_field3 import functions,uses
from context_color_api import identity,load
from native_color_boundaries import upstream,render
from native_complete_check import bits,comparisons
from complete_fixture import decode
from complete_forward import forward
from active_color import Color,replace_color
from color_inverse import f32

ROOT=Path(__file__).parent


def selection_proof(a,base,diagnostic):
    d=load(diagnostic)
    if d['first_observed_checkpoint_divergence']['SSA']!=137 or any(d['observer_stability_half_bit_mismatches'].values()):raise ValueError('Stable first-arithmetic witness required')
    s=next(s for s in d['stages']if s['SSA']==137)
    if s['native_bits']!=d['one_round_candidates']['SSA137_one_round_half_bits']:raise ValueError('One-round diagnostic does not match')
    if base.params.view('u4')[0]!=0:raise ValueError('Only fixed cast0 selected path')
    body=functions(a.path('inputs/4-main-observed.ll').read_text())['psrMainFull'];expected={223:'getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 0',224:'load i32, ptr addrspace(1) %223',235:'getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 0',236:'load i32, ptr addrspace(1) %235',245:'phi i32 [ %224, %220 ], [ %236, %227 ]',401:'icmp eq i32 %245, 16',404:'select fast <3 x i1> %403, <3 x half> %400, <3 x half> %393'};hashes={}
    for ssa,pattern in expected.items():
        line=next(l for l in body.splitlines()if l.startswith('  %'+str(ssa)+' ='))
        if not line.startswith('  %'+str(ssa)+' = '+pattern):raise ValueError('Selected-path static contract changed')
        hashes[str(ssa)]=hashlib.sha256(line.encode()).hexdigest()
    for l in uses(body,'%400'):
        if not (l.startswith('  %400 =')or l.startswith('  %404 =')or l.startswith('%obs_')):raise ValueError('Untracked bright result consumer')
    return {'context_sha256':a.manifest()['context_sha256'],'cast_raw0_on_both_phi_paths':True,'bright_selected_only_for_cast16':True,'current_SSA404_uses_skin393':True,'unselected_bright_differences_not_accepted_as_bit_matches':True,'actual_instruction_sha256':hashes,'diagnostic_sha256':sha(diagnostic),'first_arithmetic_SSA137_one_round_candidate_matches':True,'does_not_prove_all_bright_differences_have_one_cause':True}


def run(private,initial_receipt,controls_file,diagnostic,phase_name,output,precision_file):
    if output.exists():raise FileExistsError(output)
    if not re.fullmatch(r'[a-z0-9-]+',phase_name):raise ValueError('Simple unique new phase')
    a=Archive(private);m=a.manifest();old=load(initial_receipt);base=decode(load(a.path('context/context.json')));products=old['compiled_products']
    if sha(a.path('prepared.private.json'))!=old['private_manifest_sha256']:raise ValueError('Original manifest mismatch')
    a.verify(products);proof=selection_proof(a,base,diagnostic);controls=load(controls_file)['controls']
    if not 1<=len(controls)<=8 or any(not 0<=c['raw_f32_bits']<=0x3ec00000 for c in controls):raise ValueError('Bounded new controls only')
    for n in ['native_color_boundaries.py','native_active_color.py','native_guided_check.py']:
        if sha(ROOT/n)!=m['source_sha256'][n]:raise ValueError('Loaded ABI runner dependency changed')
    ident=identity(a.path('context/context.json'),precision_file)
    phase=Archive(a.root/'phases'/phase_name,create=True)
    for f in ROOT.glob('*.py'):phase.input('generators/'+f.name,f.read_bytes(),'actual phase source snapshot')
    for n,p in [('controls.json',controls_file),('diagnostic.json',diagnostic),('initial.json',initial_receipt),('base-manifest.json',a.path('prepared.private.json')),('precision.json',precision_file)]:phase.input('bindings/'+n,p.read_bytes(),'exact phase binding')
    from dataclasses import asdict
    phase_m=phase.seal({'scope':__doc__,'original_private_manifest_sha256':sha(a.path('prepared.private.json')),'original_products':products,'context_identity':asdict(ident),'selection_proof':proof,'no_new_compilation':True});checks=[a.proof('phase-'+phase_name+'-before-load',products)];lib=ctypes.CDLL(str(a.path('artifacts/chain.dylib')));plain=ctypes.CDLL(str(a.path('artifacts/plain.dylib')));generated=upstream(lib,base);prefix={n:bits(v)for n,v in generated['native'].items()};prefix_diff=sum(int(np.count_nonzero(np.array(prefix[n],dtype='u2')!=np.array(old['prefix_native_half_bits'][n],dtype='u2')))for n in prefix)
    result={'scope':__doc__,'phase':phase_name,'identity':asdict(ident),'controls_sha256':sha(controls_file),'initial_receipt_sha256':sha(initial_receipt),'original_private_manifest_sha256':sha(a.path('prepared.private.json')),'phase_manifest_sha256':sha(phase_m),'phase_private_storage_relative_to_task':str(phase.root.relative_to(ROOT.parents[1].parent)),'selection_proof':proof,'compiled_products_reused_unchanged':products,'new_compilations':0,'prefix_native_half_bits':prefix,'prefix_bit_mismatches_vs_first_run':prefix_diff,'prefix_original_calls':generated['calls'],'main_original_calls':0,'total_original_calls':generated['calls'],'point_model_calls':0,'rows':[],'proofs':checks,'status':'in_progress','all_internal_observations_bit_exact':False}
    def save():output.write_bytes(encoded(result))
    save()
    if prefix_diff:raise ValueError('Regenerated original prefix changed; receipt retained')
    for i,c in enumerate(controls):
        checks.append(a.proof('phase-'+phase_name+'-before-'+str(i),products));context=replace_color(base,Color(f32(c['raw_f32_bits'])));native,calls,observer=render(lib,plain,context,generated,m['generated_metadata'][-1]);result['main_original_calls']+=calls;result['total_original_calls']+=calls;row={'control':c,'observer_plain_writer_bit_mismatches':observer,'native_nonfinite_components':sum(int(np.count_nonzero(~np.isfinite(v)))for v in native.values()),'native_half_bits':{n:bits(v)for n,v in native.items()if n not in generated['native']}};result['rows'].append(row);save();row['point']=comparisons(native,forward(context,point=True));result['point_model_calls']+=1;row['unselected_bright_bit_mismatches']=row['point']['observations']['bright400']['half_bit_mismatches'];row['selected_path_half_bit_mismatches']=sum(v['half_bit_mismatches']for n,v in row['point']['observations'].items()if n!='bright400');checks.append(a.proof('phase-'+phase_name+'-after-'+str(i),products));save()
        if observer or row['native_nonfinite_components']or not row['point']['writer_known']or row['point']['pixel_unknowns']or row['selected_path_half_bit_mismatches']:raise AssertionError('Selected writer path differs; stop with witness, no nearest/budget changes')
    checks.append(a.proof('phase-'+phase_name+'-after-run',products));result['phase_sealed_inputs_verified']=phase.verify();result['status']='selected_writer_matches_with_unselected_bright_differences_preserved';phase.write('run-result.private.json',encoded(result),mode=0o400);result['phase_private_result_sha256']=sha(phase.path('run-result.private.json'));save();print(json.dumps({'phase':phase_name,'controls':len(controls),'original_calls':result['total_original_calls'],'selected_path_bit_mismatches':sum(r['selected_path_half_bit_mismatches']for r in result['rows']),'unselected_bright_bit_mismatches':sum(r['unselected_bright_bit_mismatches']for r in result['rows'])}));return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('private',type=Path);p.add_argument('initial',type=Path);p.add_argument('controls',type=Path);p.add_argument('diagnostic',type=Path);p.add_argument('phase');p.add_argument('output',type=Path);p.add_argument('precision',type=Path);a=p.parse_args();run(a.private,a.initial,a.controls,a.diagnostic,a.phase,a.output,a.precision)
