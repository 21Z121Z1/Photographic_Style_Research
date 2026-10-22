"""Durable NEW original-AIR host witnesses for a bound synthetic context.

prepare seals actual seven compiler inputs and all sources/context/controls.
run compiles only those files, regenerates the prefix, records every internal
observation before independent comparison and fails on any real discrepancy.
"""
from pathlib import Path
from dataclasses import asdict
from datetime import datetime,timezone
import argparse,ctypes,json,os,platform,sys
import numpy as np
from baseline_archive import Archive,sha,encoded,compiler_identity,compile_saved
from baseline_field3 import check as field3_check
from traceable_color_baseline import validate_private_location,COMPILE_SETS,AIR_NAMES,COMPILER,OTOOL,inspect_product
from air7_full_host import build as producer_build,C_SOURCE
from guided_host import build as guided_build
from native_active_color import build_main
from native_color_boundaries import upstream,render
from native_complete_check import bits,comparisons
from complete_fixture import decode
from complete_forward import forward
from active_color import Color,replace_color
from color_inverse import f32,signature
from context_color_api import identity,load

ROOT=Path(__file__).parent;REPO=ROOT.parents[1]


def prepare(source_dir,context_file,precision_file,controls_file,private,output,bindings=()):
    if output.exists():raise FileExistsError(output)
    ident=identity(context_file,precision_file);precision=load(precision_file);plan=load(controls_file);controls=plan.get('controls',plan.get('target_controls'))
    if not isinstance(controls,list)or not 1<=len(controls)<=8:raise ValueError('One to eight preselected controls required')
    if len({c['raw_f32_bits']for c in controls})!=len(controls):raise ValueError('Duplicate raw controls')
    if any(type(c['raw_f32_bits'])is not int or not 0<=c['raw_f32_bits']<=0x3ec00000 for c in controls):raise ValueError('Fixed canonical nonnegative domain only')
    validate_private_location(private);a=Archive(private,create=True,repo=REPO);sources={p.name:sha(p)for p in sorted(ROOT.glob('*.py'))}
    for n in sources:a.input('generators/'+n,(ROOT/n).read_bytes(),'exact source snapshot')
    for n in AIR_NAMES:
        if sha(source_dir/n)!=precision['source_AIR_sha256'][n]:raise ValueError('AIR identity mismatch')
        a.input('source-air/'+n,(source_dir/n).read_bytes(),'matched existing source AIR')
    metadata=[];units=[];ir,m=producer_build(a.path('source-air/0007.ll.txt').read_text(),observe=True);units.append(ir);metadata.append(m)
    for i in range(3):ir,m=guided_build(a.path('source-air/'+AIR_NAMES[1+i]).read_text(),i);units.append(ir);metadata.append(m)
    ir,m=build_main(a.path('source-air/0010.ll.txt').read_text(),True);units.append(ir);metadata.append(m);plain,plain_meta=build_main(a.path('source-air/0010.ll.txt').read_text(),False)
    for n,text in zip(COMPILE_SETS['chain'][:-1],units):a.input(n,text.encode(),'actual new compiler host IR')
    a.input('inputs/plain-main.ll',plain.encode(),'actual plain compiler host IR');a.input('inputs/shim.c',C_SOURCE.encode(),'actual compiler shim')
    for n,p in [('context.json',context_file),('precision.json',precision_file),('controls.json',controls_file)]:a.input('context/'+n,p.read_bytes(),'exact predeclared context/precision/controls')
    for f in bindings:a.input('bindings/'+f.name,f.read_bytes(),'bound candidate/catalog evidence; not a forward input')
    contract=field3_check({'producer':a.path(COMPILE_SETS['chain'][0]),'guided':[a.path(n)for n in COMPILE_SETS['chain'][1:4]],'main':a.path(COMPILE_SETS['chain'][4]),'plain':a.path('inputs/plain-main.ll')})
    if contract!=precision['field3_contract']:raise ValueError('Fresh actual file contract differs from declared precision identity; stop')
    a.input('contracts/field3.json',encoded(contract),'fresh actual-file static contract')
    compiler=compiler_identity(a,COMPILER);details={'scope':__doc__,'run_id':a.root.name,'prepared_utc':datetime.now(timezone.utc).isoformat(),'identity':asdict(ident),'context_sha256':sha(context_file),'precision_sha256':sha(precision_file),'controls_sha256':sha(controls_file),'controls':controls,'source_sha256':sources,'AIR_sha256':precision['source_AIR_sha256'],'generated_metadata':metadata,'plain_metadata':plain_meta,'field3_contract':contract,'compiler':compiler,'inspection_tool':{'path':str(OTOOL),'sha256':sha(OTOOL)},'compile_sets':COMPILE_SETS,'python':sys.version,'numpy':np.__version__,'python_hashseed':os.environ.get('PYTHONHASHSEED'),'host':{'macOS':platform.mac_ver()[0],'machine':platform.machine(),'release':platform.release()},'historical_S21_S22_identity_inherited':False}
    manifest=a.seal(details);proof=a.proof('prepared');inputs={n:a.records[n]for n in [*COMPILE_SETS['chain'],'inputs/plain-main.ll']};result={k:details[k]for k in ['run_id','identity','context_sha256','precision_sha256','controls_sha256','controls','source_sha256','AIR_sha256','field3_contract','compiler','host','python_hashseed']};result.update(scope='new sealed context baseline; no original calls yet',private_storage_relative_to_task=str(a.root.relative_to(REPO.parent)),private_manifest_sha256=sha(manifest),actual_compiler_inputs=inputs,sealed_file_hashes=a.records,proof=proof,new_native_or_model_calls=0);output.write_bytes(encoded(result));print(json.dumps({'run_id':a.root.name,'sealed_files':len(a.records),'actual_compiler_inputs':len(inputs),'context_sha256':sha(context_file)}));return result


def run(private,prepared_file,output):
    if output.exists():raise FileExistsError(output)
    validate_private_location(private);a=Archive(private,repo=REPO);m=a.manifest();p=load(prepared_file)
    if sha(a.path('prepared.private.json'))!=p['private_manifest_sha256']:raise ValueError('Private manifest changed')
    if {f.name:sha(f)for f in ROOT.glob('*.py')}!=m['source_sha256']:raise ValueError('Source set/bytes changed after preparation')
    if asdict(identity(a.path('context/context.json'),a.path('context/precision.json')))!=m['identity']:raise ValueError('Context precision mismatch')
    result={'scope':__doc__,'run_id':m['run_id'],'identity':m['identity'],'private_manifest_sha256':p['private_manifest_sha256'],'private_storage_relative_to_task':p['private_storage_relative_to_task'],'prepared_sha256':sha(prepared_file),'actual_compiler_inputs':p['actual_compiler_inputs'],'compiler':m['compiler'],'compiled_products':{},'commands':[],'proofs':[a.proof('before-compile')],'prefix_original_calls':0,'main_original_calls':0,'total_original_calls':0,'new_point_model_calls':0,'rows':[],'status':'in_progress','intermediate_outputs_supplied':False,'GPU_or_UI_inverse':False}
    def save():output.write_bytes(encoded(result))
    save()
    try:
        for label,files in COMPILE_SETS.items():
            record=compile_saved(a,COMPILER,files,'artifacts/'+label+'.dylib',label);result['commands'].append(record);result['compiled_products'][record['product']['name']]={k:v for k,v in record['product'].items()if k!='name'};record['dependencies']=inspect_product(a,record['product']['name'],label,m['inspection_tool']['sha256']);save()
        products=result['compiled_products'];result['proofs'].append(a.proof('before-load',products));lib=ctypes.CDLL(str(a.path('artifacts/chain.dylib')));plain=ctypes.CDLL(str(a.path('artifacts/plain.dylib')));result['proofs'].append(a.proof('after-load',products));base=decode(load(a.path('context/context.json')));generated=upstream(lib,base);result['prefix_original_calls']=result['total_original_calls']=generated['calls'];result['prefix_native_half_bits']={n:bits(v)for n,v in generated['native'].items()};result['proofs'].append(a.proof('after-prefix',products));save()
        for i,c in enumerate(m['controls']):
            result['proofs'].append(a.proof('before-control-'+str(i),products));context=replace_color(base,Color(f32(c['raw_f32_bits'])));native,calls,observer=render(lib,plain,context,generated,m['generated_metadata'][-1]);result['main_original_calls']+=calls;result['total_original_calls']+=calls;row={'control':c,'calls':calls,'observer_plain_writer_bit_mismatches':observer,'native_nonfinite_components':sum(int(np.count_nonzero(~np.isfinite(v)))for v in native.values()),'native_half_bits':{n:bits(v)for n,v in native.items()if n not in generated['native']}};result['rows'].append(row);save()
            expected=signature(f32(c['raw_f32_bits']));row['logical_color_interface_matches']=bool(np.all(native['color_half357'].astype('f2').view('u2')==np.float16(f32(c['raw_f32_bits'])).view('u2'))and np.all(native['color_gain364'].astype('f2').view('u2')==expected[1])and np.all(native['color_protect384'].astype('f2').view('u2')==expected[2]));row['point']=comparisons(native,forward(context,point=True));result['new_point_model_calls']+=1;result['proofs'].append(a.proof('after-control-'+str(i),products));save()
            if observer or row['native_nonfinite_components']or not row['logical_color_interface_matches']or not row['point']['writer_known']or row['point']['pixel_unknowns']or any(v['half_bit_mismatches']for v in row['point']['observations'].values()):raise AssertionError('Original/model mismatch; preserve first witness and stop, no budget changes')
        result['proofs'].append(a.proof('after-run',products))
        if sha(COMPILER.resolve())!=m['compiler']['sha256']:raise ValueError('Compiler changed')
        result['status']='passed_finite_new_context_host_witnesses';a.write('run-result.private.json',encoded(result),mode=0o400);result['private_result_sha256']=sha(a.path('run-result.private.json'));result['private_bytes']=a.capacity()['used_bytes'];save()
    except Exception as ex:
        result.update(status='failed_saved_original_model_comparison',error_type=type(ex).__name__,error=str(ex).replace(str(a.root),'<private_run>'));save();a.write('failure.private.json',encoded(result),mode=0o400);raise
    print(json.dumps({'run_id':m['run_id'],'status':result['status'],'controls':len(result['rows']),'original_calls':result['total_original_calls'],'point_calls':result['new_point_model_calls'],'point_bit_mismatches':sum(v['half_bit_mismatches']for row in result['rows']for v in row['point']['observations'].values())}));return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);s=p.add_subparsers(dest='action',required=True);q=s.add_parser('prepare');q.add_argument('source_dir',type=Path);q.add_argument('context',type=Path);q.add_argument('precision',type=Path);q.add_argument('controls',type=Path);q.add_argument('private',type=Path);q.add_argument('output',type=Path);q.add_argument('--binding',action='append',type=Path,default=[]);q=s.add_parser('run');q.add_argument('private',type=Path);q.add_argument('prepared',type=Path);q.add_argument('output',type=Path);a=p.parse_args()
    if a.action=='prepare':prepare(a.source_dir,a.context,a.precision,a.controls,a.private,a.output,a.binding)
    else:run(a.private,a.prepared,a.output)
