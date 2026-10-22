"""S24 NEW traceable host baseline; never reconstructed historical S21/S22.

prepare persists exact compiler input bytes and dependencies before compilation.
run reads those sealed files, rechecks hashes after compile and execution, and
uses only the existing eight raw boundary controls. No146-state model rerun.
"""
import argparse,ctypes,hashlib,json,os,platform,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
from baseline_archive import Archive,sha,encoded,compiler_identity,compile_saved
from baseline_field3 import check as field3_check
from air7_full_host import build as producer_build,C_SOURCE
from guided_host import build as guided_build
from native_active_color import build_main
from native_color_boundaries import upstream,render
from native_complete_check import bits,comparisons
from complete_fixture import decode
from complete_forward import forward
from active_color import Color,replace_color
from color_inverse import f32,signature
from select_active_color import CONTEXT_SHA

ROOT=Path(__file__).parent;REPO=ROOT.parents[1]
COMPILER=Path('/opt/homebrew/opt/llvm/bin/clang')
OTOOL=Path('/usr/bin/otool')
COMPILE_SETS={'chain':['inputs/0-producer.ll','inputs/1-guided-coeff.ll','inputs/2-guided-filter.ll','inputs/3-guided-apply.ll','inputs/4-main-observed.ll','inputs/shim.c'],'plain':['inputs/plain-main.ll','inputs/shim.c']}
AIR_NAMES=['0007.ll.txt','0090.ll.txt','0091.ll.txt','0092.ll.txt','0010.ll.txt']
load=lambda p:json.loads(p.read_text())
dump=lambda p,d:p.write_text(json.dumps(d,separators=(',',':'),allow_nan=False)+'\n')


def validate_private_location(path):
    path=Path(path)
    if path.parent.resolve()!=(REPO.parent/'psr-private-baselines').resolve()or path.parent.is_symlink()or path.is_symlink():raise ValueError('Use a new run under this task private psr-private-baselines directory')
    return path


def catalog_reuse():
    e=ROOT/'evidence';v=load(e/'verification-s22.json');changed=[]
    for name,h in v['current_source_sha256'].items():
        if name=='bound_validation.py':continue
        if sha(ROOT/name)!=h:changed.append(name)
    if changed:raise ValueError('Catalog computational source changed; do not reuse search: '+','.join(changed))
    names=['complete-context-s15a.json','color-partition-s22a.json','color-inverse-s22c.json','color-boundaries-s22c.json','native-active-s21c.json','native-boundaries-s22d.json']
    for p in sorted(e.glob('scan-[0-9][0-9][0-9]-s22b.json')):names.append(p.name)
    hashes={}
    for name in names:
        actual=sha(e/name)
        expected=CONTEXT_SHA if name=='complete-context-s15a.json'else v['evidence_sha256'].get(name)
        if name=='native-active-s21c.json':expected=load(e/'verification-s21.json')['evidence_sha256'][name]
        if expected is None or actual!=expected:raise ValueError('Catalog/context input identity changed: '+name)
        hashes[name]=actual
    plan=load(e/'color-boundaries-s22c.json');inverse=load(e/'color-inverse-s22c.json')
    if len(plan['controls'])!=8 or not inverse['coverage']['complete_model_coverage']or inverse['model_forward_evaluations']!=146:raise ValueError('Only existing complete catalog and eight controls')
    return {'unchanged_computational_source_files':len(v['current_source_sha256'])-1,'source_exception':'bound_validation.py stage input bookkeeping only','source_hashes':{n:h for n,h in v['current_source_sha256'].items()if n!='bound_validation.py'},'input_hashes':hashes,'existing_model_states':146,'new_search_forward_calls':0,'boundary_controls':8,'source_and_input_identity_all_match':True}


def prepare(source_dir,private_path,public_output):
    if public_output.exists():raise FileExistsError(public_output)
    validate_private_location(private_path);archive=Archive(private_path,create=True,repo=REPO);reuse=catalog_reuse();sources={p.name:sha(p)for p in sorted(ROOT.glob('*.py'))}
    for name in sources:archive.input('generators/'+name,(ROOT/name).read_bytes(),'exact generator/model source snapshot')
    air_hashes={}
    for name in AIR_NAMES:
        path=source_dir/name;air_hashes[name]=sha(path);archive.input('source-air/'+name,path.read_bytes(),'existing matched source AIR snapshot')
    texts={name:archive.path('source-air/'+name).read_text()for name in AIR_NAMES};units=[];metadata=[]
    ir,m=producer_build(texts['0007.ll.txt'],observe=True);units.append(ir);metadata.append(m)
    for i in range(3):ir,m=guided_build(texts[AIR_NAMES[1+i]],i);units.append(ir);metadata.append(m)
    ir,main_meta=build_main(texts['0010.ll.txt'],True);units.append(ir);metadata.append(main_meta);plain,plain_meta=build_main(texts['0010.ll.txt'],False)
    ir_names=COMPILE_SETS['chain'][:-1]
    for name,text in zip(ir_names,units):archive.input(name,text.encode('utf8'),'actual new host IR compiler input')
    archive.input('inputs/plain-main.ll',plain.encode('utf8'),'actual new plain main compiler input');archive.input('inputs/shim.c',C_SOURCE.encode('utf8'),'actual new C shim compiler input')
    for name in reuse['input_hashes']:archive.input('context/'+name,(ROOT/'evidence'/name).read_bytes(),'exact known source/context/catalog input')
    paths={'producer':archive.path(ir_names[0]),'guided':[archive.path(n)for n in ir_names[1:4]],'main':archive.path(ir_names[4]),'plain':archive.path('inputs/plain-main.ll')};contract=field3_check(paths);archive.input('contracts/field3.json',encoded(contract),'fresh dependency audit of actual persisted host files')
    compiler=compiler_identity(archive,COMPILER)
    if not OTOOL.is_file():raise FileNotFoundError('Existing Mach-O inspection tool required')
    details={'scope':'S24 NEW RUN; not historical S21/S22 replacement','run_id':archive.root.name,'prepared_utc':datetime.now(timezone.utc).isoformat(),'base_git_HEAD':subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),'hardware_source':'iPhone17,3','firmware_build':'24A446','internal_bundle_class':'SmartStyleV1 / CMISmartStyleProcessorV1','compiler_target':'arm64-apple-macos27.0','python':sys.version,'numpy':np.__version__,'host':{'system':platform.system(),'release':platform.release(),'machine':platform.machine(),'macOS':platform.mac_ver()[0]},'python_hashseed':os.environ.get('PYTHONHASHSEED','unset'),'compiler':compiler,'inspection_tool':{'path':str(OTOOL),'sha256':sha(OTOOL)},'compile_sets':COMPILE_SETS,'source_sha256':sources,'AIR_sha256':air_hashes,'generated_metadata':metadata,'plain_metadata':plain_meta,'catalog_reuse':reuse,'field3_contract':contract,'historical_producer_IR_identity_inherited':False}
    manifest=archive.seal(details);proof=archive.proof('prepared-inputs');result={'scope':'new S24 prepared compiler inputs; no compilation or original kernel call yet','run_id':archive.root.name,'private_storage_relative_to_task':str(archive.root.relative_to(REPO.parent)),'private_manifest_sha256':sha(manifest),'actual_compiler_inputs':{n:archive.records[n]for n in [*ir_names,'inputs/plain-main.ll','inputs/shim.c']},'all_private_input_file_hashes':archive.records,'compiler':compiler,'host':details['host'],'python_hashseed':details['python_hashseed'],'source_sha256':sources,'AIR_sha256':air_hashes,'new_field3_contract':contract,'catalog_reuse':reuse,'input_proof':proof,'private_bytes_at_prepare':archive.capacity()['used_bytes'],'new_original_kernel_calls':0,'new_model_forward_calls':0,'historical_module_equality_claim':False};dump(public_output,result);print(json.dumps({'run_id':result['run_id'],'private_manifest_sha256':result['private_manifest_sha256'],'persisted_compiler_inputs':7,'private_bytes':result['private_bytes_at_prepare'],'field3_contract':contract['all_checks_pass'],'catalog_reused_without_search':True}));return result


def inspect_product(archive,name,label,expected_tool):
    if sha(OTOOL)!=expected_tool:raise RuntimeError('Mach-O inspection tool identity changed')
    args=[str(OTOOL),'-L',str(archive.path(name))];p=subprocess.run(args,capture_output=True,timeout=15);out=archive.write('logs/'+label+'-dependencies.stdout',p.stdout);err=archive.write('logs/'+label+'-dependencies.stderr',p.stderr)
    if p.returncode:raise RuntimeError('Cannot inspect compiled dependencies; logs retained')
    return {'argv_redacted':archive.redact(args),'stdout_sha256':sha(out),'stderr_sha256':sha(err),'dependencies_redacted':p.stdout.decode(errors='replace').replace(str(archive.root),'<private_run>').splitlines()[1:]}


def run(private_path,prepared_file,public_output):
    if public_output.exists():raise FileExistsError(public_output)
    validate_private_location(private_path);archive=Archive(private_path,repo=REPO);m=archive.manifest();prepared=load(prepared_file)
    if sha(archive.path('prepared.private.json'))!=prepared['private_manifest_sha256']or m['run_id']!=prepared['run_id']:raise ValueError('Prepared private manifest identity mismatch')
    current={p.name:sha(p)for p in sorted(ROOT.glob('*.py'))}
    if current!=m['source_sha256']:raise ValueError('Source set/bytes changed after prepare; do not regenerate in this run')
    reuse=catalog_reuse()
    if reuse!=m['catalog_reuse']:raise ValueError('Catalog identity changed after prepare')
    archive.verify();proofs=[archive.proof('before-compilation')];products={};commands=[];rows=[];result={'scope':'S24 NEW traceable baseline; persistent exact compiler inputs; same eight S22 boundary controls only','run_id':m['run_id'],'private_storage_relative_to_task':prepared['private_storage_relative_to_task'],'private_manifest_sha256':prepared['private_manifest_sha256'],'prepared_public_sha256':sha(prepared_file),'actual_compiler_inputs':prepared['actual_compiler_inputs'],'source_sha256':current,'AIR_sha256':m['AIR_sha256'],'compiler':m['compiler'],'new_field3_contract':m['field3_contract'],'catalog_reuse':reuse,'historical_S21_S22_IR_difference':'still unknown; no historical whole-module equality inherited','commands':commands,'compiled_products':products,'input_and_product_proofs':proofs,'rows':rows,'prefix_original_calls':0,'main_original_calls':0,'total_completed_original_kernel_calls':0,'new_model_forward_calls':0,'new_146_state_search_calls':0,'status':'in_progress','cost_complete':False,'GPU_or_UI_or_unknown_source_inverse_verified':False};dump(public_output,result)
    try:
        for label,files in m['compile_sets'].items():
            record=compile_saved(archive,COMPILER,files,'artifacts/'+label+'.dylib',label);commands.append(record);products[record['product']['name']]={k:v for k,v in record['product'].items()if k!='name'};record['dependencies']=inspect_product(archive,record['product']['name'],label,m['inspection_tool']['sha256']);dump(public_output,result)
        if sha(COMPILER.resolve())!=m['compiler']['sha256']:raise RuntimeError('Compiler changed after compile')
        proofs.append(archive.proof('compiled-before-load',products));lib=ctypes.CDLL(str(archive.path('artifacts/chain.dylib')));plain=ctypes.CDLL(str(archive.path('artifacts/plain.dylib')));proofs.append(archive.proof('after-load-before-kernels',products));base=decode(load(archive.path('context/complete-context-s15a.json')));plan=load(archive.path('context/color-boundaries-s22c.json'));old=load(archive.path('context/native-boundaries-s22d.json'));target_source=load(archive.path('context/native-active-s21c.json'));goals={n:np.array(target_source['rows'][i]['native_half_bits']['writer'],dtype='u2')for n,i in [('platform',1),('point3',3)]};catalog={}
        for name in reuse['input_hashes']:
            if name.startswith('scan-'):
                for row in load(archive.path('context/'+name))['rows']:catalog[row['state_id']]=row
        generated=upstream(lib,base);result['prefix_original_calls']=generated['calls'];result['total_completed_original_kernel_calls']=generated['calls'];result['prefix_native_half_bits']={n:bits(a)for n,a in generated['native'].items()};result['prefix_bit_mismatches_vs_saved_S22']=sum(int(np.count_nonzero(a.astype('f2').view('u2')!=np.array(old['prefix_native_half_bits'][n],dtype='u2')))for n,a in generated['native'].items());proofs.append(archive.proof('after-prefix',products));dump(public_output,result)
        if result['prefix_bit_mismatches_vs_saved_S22']:raise AssertionError('New prefix differs; stop before further kernels')
        for index,control in enumerate(plan['controls']):
            proofs.append(archive.proof('before-control-'+str(index),products));context=replace_color(base,Color(f32(control['raw_f32_bits'])));native,calls,observer=render(lib,plain,context,generated,m['generated_metadata'][-1]);result['main_original_calls']+=calls;result['total_completed_original_kernel_calls']+=calls;row={'control':control,'main_original_calls':calls,'observer_plain_writer_half_bit_mismatches':observer,'native_nonfinite_components':sum(int(np.count_nonzero(~np.isfinite(a)))for a in native.values()),'native_half_bits':{n:bits(a)for n,a in native.items()if n not in generated['native']}};rows.append(row);dump(public_output,result)
            reference={**old['prefix_native_half_bits'],**old['rows'][index]['native_half_bits']};row['half_bit_mismatches_vs_saved_S22']={n:int(np.count_nonzero(np.asarray(a,dtype='f2').view('u2')!=np.array(reference[n],dtype='u2')))for n,a in native.items()};row['model_catalog_writer_half_bit_mismatches']=int(np.count_nonzero(native['writer'].view('u2')!=np.array(catalog[control['state_id']]['writer_half_bits'],dtype='u2')));row['target_matches']={n:bool(np.array_equal(native['writer'].view('u2'),g))for n,g in goals.items()};row['target_match_expectations_agree']=row['target_matches']==control['expected_matches'];row['logical_field3_matches']={'half357':bool(np.all(native['color_half357']==np.float16(f32(control['raw_f32_bits'])))),'gain364':bool(np.all(native['color_gain364'].astype('f2').view('u2')==control['key'][1])),'protect384':bool(np.all(native['color_protect384'].astype('f2').view('u2')==control['key'][2]))};row['point']=comparisons(native,forward(context,point=True));result['new_model_forward_calls']+=1;proofs.append(archive.proof('after-control-'+str(index),products));dump(public_output,result)
            if observer or row['native_nonfinite_components']or any(row['half_bit_mismatches_vs_saved_S22'].values())or row['model_catalog_writer_half_bit_mismatches']or not row['target_match_expectations_agree']or not all(row['logical_field3_matches'].values())or not row['point']['writer_known']or row['point']['pixel_unknowns']or any(v['half_bit_mismatches']for v in row['point']['observations'].values())or sum(v['components']for v in row['point']['observations'].values())!=1938:raise AssertionError('New baseline differs; stop, preserve inputs, do not alter candidate budget')
        proofs.append(archive.proof('after-run-final',products))
        if sha(COMPILER.resolve())!=m['compiler']['sha256']:raise RuntimeError('Compiler identity changed during run')
        result.update(status='passed_new_finite_boundary_baseline',cost_complete=True,private_bytes_after_run=archive.capacity()['used_bytes'],candidate_budget_changed=False,original_host_all146_states_exhaustively_verified=False,other140_states_still_not_exhaustively_host_verified=True);archive.write('run-result.private.json',encoded(result),mode=0o400);result['private_result_sha256']=sha(archive.path('run-result.private.json'));dump(public_output,result)
    except Exception as ex:
        result.update(status='failed_new_baseline_inputs_and_logs_retained',error_type=type(ex).__name__,error=str(ex).replace(str(archive.root),'<private_run>').replace(str(REPO),'<repo>'));dump(public_output,result);archive.write('failure.private.json',encoded(result),mode=0o400);raise
    print(json.dumps({'run_id':m['run_id'],'status':result['status'],'controls':len(rows),'prefix_calls':result['prefix_original_calls'],'main_calls':result['main_original_calls'],'original_kernel_calls':result['total_completed_original_kernel_calls'],'model_catalog_writer_mismatches':sum(v['model_catalog_writer_half_bit_mismatches']for v in rows),'point_half_bit_mismatches':sum(v['half_bit_mismatches']for row in rows for v in row['point']['observations'].values()),'retained_private_bytes':result['private_bytes_after_run']}));return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);s=p.add_subparsers(dest='action',required=True);q=s.add_parser('prepare');q.add_argument('source_dir',type=Path);q.add_argument('private_path',type=Path);q.add_argument('output',type=Path);q=s.add_parser('run');q.add_argument('private_path',type=Path);q.add_argument('prepared',type=Path);q.add_argument('output',type=Path);a=p.parse_args()
    if a.action=='prepare':prepare(a.source_dir,a.private_path,a.output)
    else:run(a.private_path,a.prepared,a.output)
