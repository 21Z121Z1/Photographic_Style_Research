"""S33 compile/static-check a read-only wrapper, then one same-thread call.

Never sets FPCR or selects another thread. No retry on non-RN or failed binding.
The original f32 function is unchanged; half conversions belong to this wrapper.
"""
from pathlib import Path
import argparse,ctypes,hashlib,json,re,subprocess,threading,time
from baseline_archive import Archive,encoded,sha,compiler_identity
from context_color_api import load

R=Path(__file__).parent
E=R/'evidence'
REPO=R.parents[1]
COMPILER=Path('/opt/homebrew/opt/llvm/bin/clang')
OBJDUMP=COMPILER.with_name('llvm-objdump')


class Report(ctypes.Structure):
    _fields_=[('fpcr_before',ctypes.c_uint64),('fpcr_after',ctypes.c_uint64),
              ('thread_before',ctypes.c_uint64),('thread_after',ctypes.c_uint64),
              ('self_before',ctypes.c_uint64),('self_after',ctypes.c_uint64),
              ('input_single_bits',ctypes.c_uint32),('output_single_bits',ctypes.c_uint32),
              ('input_half_bits',ctypes.c_uint16),('output_half_bits',ctypes.c_uint16),
              ('original_call_count',ctypes.c_uint32),('thread_query_before',ctypes.c_int32),('thread_query_after',ctypes.c_int32)]
assert ctypes.sizeof(Report)==72


def prepare(private,output):
    if output.exists():raise FileExistsError(output)
    old=load(E/'sqrt-static-s32a.json')
    original=Archive(REPO.parent/old['private_storage_relative_to_task'],repo=REPO)
    identity=original.verify();assert identity['sealed_manifest_sha256']==old['private_manifest_sha256']
    a=Archive(private,create=True,repo=REPO)
    for n in ['fpcr_read_call.c','fpcr_binding.py']:
        a.input('inputs/'+n,(R/n).read_bytes(),'exact new read-only wrapper/source')
    a.input('inputs/sealed-trace.dylib',original.path('inputs/reused-trace.dylib').read_bytes(),'unchanged existing S25 product')
    plan={'input_half_bits':0x3880,'input_value_rational':[9,16],
          'selection_reason':'predeclared exact normal square9/16; sqrt3/4 avoids inexact/trap side effects; this is an FPCR binding, not a precision stress batch',
          'original_symbol':'psr_sqrt_scalar','original_symbol_image_offset':0x15908,
          'original_product_sha256':old['product_sha256'],'original_call_budget':1,
          'no_FPCR_writes_or_mode_switch':True,'same_thread_native_read_call_read':True,
          'half_conversions':'new wrapper; old sealed half helper not executed',
          'historical_state_or_other_threads_certified':False}
    a.input('binding/call-input.json',encoded(plan),'frozen one-call input before compilation')
    compiler=compiler_identity(a,COMPILER);objdump_sha=sha(OBJDUMP.resolve())
    a.seal({'scope':__doc__,'compiler':compiler,'objdump_sha256':objdump_sha,'plan':plan,
            'S32_static_sha256':sha(E/'sqrt-static-s32a.json')})
    pre=a.proof('before-compile')
    product=a.path('artifacts/read-call.dylib');product.parent.mkdir()
    command=[str(COMPILER),'-target','arm64-apple-macos27.0','-std=c17','-O0','-frounding-math','-ffp-contract=off',
             '-Wall','-Wextra','-Werror','-v','-dynamiclib',str(a.path('inputs/fpcr_read_call.c')),'-o',str(product)]
    begin=time.perf_counter();p=subprocess.run(command,capture_output=True,timeout=30)
    out=a.write('logs/compile.stdout',p.stdout);err=a.write('logs/compile.stderr',p.stderr)
    post=a.proof('after-compile')
    cmd={'argv_redacted':a.redact(command),'argv_sha256':hashlib.sha256(encoded(command)).hexdigest(),
         'exit_code':p.returncode,'stdout_sha256':sha(out),'stderr_sha256':sha(err),
         'seconds':time.perf_counter()-begin,'compiler_sha256':compiler['sha256']}
    a.write('commands/compile.private.json',encoded({**cmd,'actual_argv':command}),mode=0o400)
    if p.returncode:raise RuntimeError('Reader compile failed; sources/logs retained, no call attempted')
    assert sha(COMPILER.resolve())==compiler['sha256']
    record={'name':'artifacts/read-call.dylib','sha256':sha(product),'bytes':product.stat().st_size}
    dis=subprocess.run([str(OBJDUMP),'--disassemble','--no-show-raw-insn',str(product)],capture_output=True,timeout=15)
    stdout=a.write('logs/disassembly.stdout',dis.stdout);stderr=a.write('logs/disassembly.stderr',dis.stderr)
    if dis.returncode:raise RuntimeError('Static reader inspection failed; no call attempted')
    text=dis.stdout.decode();assert not re.search(r'\bmsr\s+FPCR\b',text,re.I),'FPCR write found: do not load/call'
    body=re.search(r'^[0-9a-f]+ <_psr_fpcr_read_call>:\n(.*?)(?=\n[0-9a-f]+ <|\Z)',text,re.M|re.S)[1]
    lines=[l for l in body.splitlines()if re.match(r'\s*[0-9a-f]+:',l)]
    reads=[i for i,l in enumerate(lines)if re.search(r'\bmrs\s+[^,]+, FPCR\b',l,re.I)]
    assert len(reads)==2,'Need exactly two FPCR reads in single native function'
    window=lines[reads[0]+1:reads[1]]
    calls=[l for l in window if re.search(r'\b(?:bl|blr|blraa|blrab)\b',l)]
    assert len(calls)==1 and re.search(r'\bblr\b',calls[0]),'Critical window must contain one direct synchronous function-pointer call only'
    call_index=window.index(calls[0])
    assert any(re.search(r'\bfcvt\s+s\d+, h\d+',l)for l in window[:call_index]),'Input conversion not inside read boundary'
    assert any(re.search(r'\bfcvt\s+h\d+, s\d+',l)for l in window[call_index+1:]),'Output conversion not inside read boundary'
    assert sha(OBJDUMP.resolve())==objdump_sha
    proof=a.proof('after-static-before-load',{record['name']:record})
    d={'status':'compiled_and_statically_verified_read_only_wrapper_not_yet_called',
       'private_storage_relative_to_task':str(a.root.relative_to(REPO.parent)),
       'private_manifest_sha256':sha(a.path('prepared.private.json')),'plan':plan,
       'wrapper_source_sha256':sha(a.path('inputs/fpcr_read_call.c')),'wrapper_product':record,
       'original_product_sha256':sha(a.path('inputs/sealed-trace.dylib')),
       'compiler':compiler,'compile_command':cmd,'proofs':[pre,post,proof],
       'disassembly_stdout_sha256':sha(stdout),'disassembly_stderr_sha256':sha(stderr),
       'FPCR_writing_instructions':0,'FPCR_read_instructions':2,'critical_window_function_calls':1,
       'critical_window_instruction_sha256':hashlib.sha256(encoded(window)).hexdigest(),
       'input_and_output_FCVT_inside_same_two_MRS_boundary':True,
       'thread_queries_outside_FPCR_boundary':True,'original_calls_completed':0,'new_compilations':1}
    assert d['original_product_sha256']==plan['original_product_sha256']
    a.write('prepared-result.private.json',encoded(d),mode=0o400);output.write_bytes(encoded(d))
    print(json.dumps({'status':d['status'],'MRS':2,'FPCR_writes':0,'critical_calls':1,'native_calls':0,'compilations':1}));return d


class DlInfo(ctypes.Structure):
    _fields_=[('fname',ctypes.c_char_p),('base',ctypes.c_void_p),('sname',ctypes.c_char_p),('saddr',ctypes.c_void_p)]


def run(prepared_file,output):
    if output.exists():raise FileExistsError(output)
    prepared=load(prepared_file);a=Archive(REPO.parent/prepared['private_storage_relative_to_task'],repo=REPO)
    products={prepared['wrapper_product']['name']:prepared['wrapper_product']}
    assert a.verify(products)['sealed_manifest_sha256']==prepared['private_manifest_sha256']
    if a.path('run-started.private.json').exists():raise RuntimeError('One-call run already started; do not repeat uncertain or completed call')
    a.write('run-started.private.json',encoded({'prepared_sha256':sha(prepared_file),'maximum_original_calls':1}),mode=0o400)
    pre=a.proof('before-load-and-call',products)
    original=ctypes.CDLL(str(a.path('inputs/sealed-trace.dylib')))
    function=getattr(original,prepared['plan']['original_symbol'])
    address=ctypes.cast(function,ctypes.c_void_p).value
    loader=ctypes.CDLL(None);dladdr=loader.dladdr;dladdr.argtypes=[ctypes.c_void_p,ctypes.POINTER(DlInfo)];dladdr.restype=ctypes.c_int
    info=DlInfo()
    if not dladdr(address,ctypes.byref(info)):raise RuntimeError('Cannot bind called symbol to sealed image; no call attempted')
    actual_path=Path(info.fname.decode()).resolve();expected_path=a.path('inputs/sealed-trace.dylib').resolve()
    offset=address-info.base
    assert actual_path==expected_path and sha(actual_path)==prepared['original_product_sha256']
    assert offset==prepared['plan']['original_symbol_image_offset']and info.saddr==address
    a.write('loaded-symbol.private.json',encoded({'address':address,'base':info.base,'symbol_address':info.saddr,
                                                 'symbol':info.sname.decode(),'offset':offset,'actual_path':str(actual_path)}),mode=0o400)
    wrapper=ctypes.CDLL(str(a.path(prepared['wrapper_product']['name'])))
    call=wrapper.psr_fpcr_read_call;call.argtypes=[ctypes.c_void_p,ctypes.c_uint16,ctypes.POINTER(Report)];call.restype=ctypes.c_int
    report=Report();before_thread=threading.get_native_id()
    rc=call(address,prepared['plan']['input_half_bits'],ctypes.byref(report))
    after_thread=threading.get_native_id()
    raw=a.write('run/report.bin',bytes(report),mode=0o400)
    same_thread=bool(report.thread_query_before==report.thread_query_after==0 and
                     report.thread_before==report.thread_after==before_thread==after_thread and
                     report.self_before==report.self_after)
    same_fpcr=report.fpcr_before==report.fpcr_after
    rmode_before=(report.fpcr_before>>22)&3;rmode_after=(report.fpcr_after>>22)&3
    certificate=load(E/'sqrt-domain-certificate-s32c.json')
    expected=next(r for r in certificate['rows']if r['input_half_bits']==prepared['plan']['input_half_bits'])
    exact_output=(report.output_single_bits==expected['correctly_RN_single_sqrt_bits']and report.output_half_bits==expected['RN_single_to_half_bits'])
    status='bound_current_same_thread_RN_primitive_call'if(rc==0 and same_thread and same_fpcr and rmode_before==rmode_after==0 and report.original_call_count==1 and exact_output)else'current_binding_not_established_preserve_no_retry'
    post=a.proof('after-call',products)
    d={'status':status,'prepared_sha256':sha(prepared_file),'private_storage_relative_to_task':prepared['private_storage_relative_to_task'],
       'private_manifest_sha256':prepared['private_manifest_sha256'],'raw_report_sha256':sha(raw),
       'original_product_sha256':prepared['original_product_sha256'],'wrapper_product_sha256':prepared['wrapper_product']['sha256'],
       'resolved_symbol':info.sname.decode(),'resolved_image_offset':offset,'symbol_image_SHA_and_offset_verified':True,
       'native_return_code':rc,'original_primitive_calls':report.original_call_count,'wrapper_calls':1,
       'FPCR_before_uint64':report.fpcr_before,'FPCR_after_uint64':report.fpcr_after,
       'FPCR_before_hex':f'0x{report.fpcr_before:016x}','FPCR_after_hex':f'0x{report.fpcr_after:016x}',
       'RMode_before':rmode_before,'RMode_after':rmode_after,'FPCR_unchanged':same_fpcr,
       'native_thread_before':report.thread_before,'native_thread_after':report.thread_after,
       'python_native_thread_before':before_thread,'python_native_thread_after':after_thread,
       'pthread_self_before_after_equal':report.self_before==report.self_after,
       'pthread_self_identity_sha256':hashlib.sha256(report.self_before.to_bytes(8,'little')).hexdigest(),
       'same_thread_binding':same_thread,
       'input_half_bits':report.input_half_bits,'input_single_bits':report.input_single_bits,
       'output_single_bits':report.output_single_bits,'output_half_bits':report.output_half_bits,
       'matches_exact_S32_certificate':exact_output,'certificate_sha256':sha(E/'sqrt-domain-certificate-s32c.json'),
       'FPCR_writes_or_mode_changes':0,'half_conversions_are_new_wrapper_not_old_half_helper':True,
       'historical_runs_other_threads_GPU_or_pipeline_certified':False,'new_compilations_in_run_phase':0,'proofs':[pre,post]}
    a.write('run/result.private.json',encoded(d),mode=0o400);output.write_bytes(encoded(d))
    print(json.dumps({'status':status,'FPCR_before':d['FPCR_before_hex'],'FPCR_after':d['FPCR_after_hex'],
                      'RMode':[rmode_before,rmode_after],'same_thread':same_thread,'original_calls':report.original_call_count,
                      'output_matches':exact_output,'FPCR_writes':0}));return d


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['prepare','run']);p.add_argument('first',type=Path);p.add_argument('second',type=Path)
    x=p.parse_args()
    if x.mode=='prepare':prepare(x.first,x.second)
    else:run(x.first,x.second)
