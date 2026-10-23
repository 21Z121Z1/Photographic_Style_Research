"""S33 read-only audit of one saved call; never compiles or loads native code."""
from pathlib import Path
import argparse,ctypes,hashlib,json,re,subprocess
from baseline_archive import Archive,encoded,sha
from context_color_api import load
from fpcr_binding import Report

R=Path(__file__).parent
E=R/'evidence'
REPO=R.parents[1]


def check_report(raw,record,plan,expected):
    """Check saved ABI data independently of the driver's success label."""
    if len(raw)!=72:raise ValueError('Wrong raw report ABI size')
    p=Report.from_buffer_copy(raw)
    if p.thread_query_before or p.thread_query_after:raise ValueError('Thread query failed')
    tids=[p.thread_before,p.thread_after,record['python_native_thread_before'],record['python_native_thread_after']]
    if not tids[0]or len(set(tids))!=1 or p.self_before!=p.self_after:raise ValueError('Not the same thread')
    if p.fpcr_before!=p.fpcr_after or ((p.fpcr_before>>22)&3)!=0:raise ValueError('Current RN binding not established')
    if p.original_call_count!=1 or record['wrapper_calls']!=1:raise ValueError('One-call budget violated')
    if p.input_half_bits!=plan['input_half_bits']or p.input_single_bits!=0x3f100000:raise ValueError('Frozen input changed')
    if p.output_single_bits!=expected['correctly_RN_single_sqrt_bits']or p.output_half_bits!=expected['RN_single_to_half_bits']:
        raise ValueError('Actual output does not match mathematical row')
    for name in ['input_half_bits','input_single_bits','output_half_bits','output_single_bits',
                 'original_call_count','fpcr_before','fpcr_after','thread_before','thread_after']:
        public={'original_call_count':'original_primitive_calls','fpcr_before':'FPCR_before_uint64',
                'fpcr_after':'FPCR_after_uint64','thread_before':'native_thread_before','thread_after':'native_thread_after'}.get(name,name)
        if getattr(p,name)!=record[public]:raise ValueError('Public/raw mismatch: '+name)
    if hashlib.sha256(p.self_before.to_bytes(8,'little')).hexdigest()!=record['pthread_self_identity_sha256']:
        raise ValueError('pthread identity hash mismatch')
    if not record['same_thread_binding']or not record['FPCR_unchanged']or record['RMode_before']!=0 or record['RMode_after']!=0:
        raise ValueError('Misreported binding')
    if record['native_return_code']!=0:raise ValueError('Native wrapper returned error')
    return p


def check_window(disassembly):
    """Read actual saved instructions, not source-order assumptions."""
    if re.search(r'\bmsr\s+FPCR\b',disassembly,re.I):raise ValueError('FPCR write in wrapper product')
    m=re.search(r'^[0-9a-f]+ <_psr_fpcr_read_call>:\n(.*?)(?=\n[0-9a-f]+ <|\Z)',disassembly,re.M|re.S)
    if not m:raise ValueError('Wrapper body missing')
    lines=[l for l in m[1].splitlines()if re.match(r'\s*[0-9a-f]+:',l)]
    reads=[i for i,l in enumerate(lines)if re.search(r'\bmrs\s+[^,]+, FPCR\b',l,re.I)]
    if len(reads)!=2:raise ValueError('Exactly two reads required')
    window=lines[reads[0]+1:reads[1]]
    calls=[i for i,l in enumerate(window)if re.search(r'\b(?:bl|blr|blraa|blrab)\b',l)]
    if len(calls)!=1 or not re.search(r'\bblr\b',window[calls[0]]):raise ValueError('One synchronous indirect call required')
    k=calls[0]
    if sum(bool(re.search(r'\bfcvt\s+s\d+, h\d+',l))for l in window[:k])!=1:raise ValueError('Input FCVT outside boundary')
    if sum(bool(re.search(r'\bfcvt\s+h\d+, s\d+',l))for l in window[k+1:])!=1:raise ValueError('Output FCVT outside boundary')
    address=lambda l:'0x'+re.match(r'\s*([0-9a-f]+):',l)[1]
    input_fcvt=next(l for l in window[:k]if re.search(r'\bfcvt\s+s\d+, h\d+',l))
    output_fcvt=next(l for l in window[k+1:]if re.search(r'\bfcvt\s+h\d+, s\d+',l))
    return {'critical_instruction_sha256':hashlib.sha256(encoded(window)).hexdigest(),
            'MRS_count':2,'critical_call_count':1,'FPCR_write_count':0,
            'addresses':{'MRS_before':address(lines[reads[0]]),'input_FCVT':address(input_fcvt),
                         'BLR':address(window[k]),'output_FCVT':address(output_fcvt),'MRS_after':address(lines[reads[1]])}}


def saved_binding(name):
    b=load(E/(name+'.json'));pre=E/(name+'.pre.json');log=E/(name+'.log')
    assert b['exit_code']==0 and b['source_unchanged_during_command']and b['inputs_unchanged_during_command']
    assert sha(pre)==b['pre_run_binding_sha256']and sha(log)==b['log_sha256']
    return {'pre_sha256':sha(pre),'post_sha256':sha(E/(name+'.json')),'log_sha256':sha(log),'seconds':b['elapsed_seconds']}


def resolve_stub_rows(metadata,target):
    """Compare parsed addresses, including 0x and leading zeroes, in __stubs."""
    rows=[];in_stubs=False
    for line in metadata.splitlines():
        if line.startswith('Indirect symbols for '):
            in_stubs='(__TEXT,__stubs)'in line
        m=re.fullmatch(r'\s*0x([0-9a-fA-F]+)\s+(\d+)\s+(\S+)\s*',line)
        if in_stubs and m and int(m[1],16)==target:
            rows.append({'symbol':m[3],'index':int(m[2]),'row_sha256':hashlib.sha256(line.encode()).hexdigest()})
    return rows


def verify(output):
    if output.exists():raise FileExistsError(output)
    prepared=load(E/'fpcr-prepared-s33a.json');current=load(E/'fpcr-current-run-s33b.json')
    a=Archive(REPO.parent/prepared['private_storage_relative_to_task'],repo=REPO)
    products={prepared['wrapper_product']['name']:prepared['wrapper_product']}
    assert a.verify(products)['sealed_manifest_sha256']==prepared['private_manifest_sha256']==current['private_manifest_sha256']
    assert current['prepared_sha256']==sha(E/'fpcr-prepared-s33a.json')
    assert current==load(a.path('run/result.private.json'))and prepared==load(a.path('prepared-result.private.json'))
    assert sha(a.path('inputs/fpcr_read_call.c'))==sha(R/'fpcr_read_call.c')==prepared['wrapper_source_sha256']
    assert sha(a.path('inputs/fpcr_binding.py'))==sha(R/'fpcr_binding.py')
    plan=load(a.path('binding/call-input.json'));assert plan==prepared['plan']
    assert plan['input_half_bits']==0x3880 and plan['original_call_budget']==1 and plan['no_FPCR_writes_or_mode_switch']
    marker=load(a.path('run-started.private.json'))
    assert marker=={'prepared_sha256':current['prepared_sha256'],'maximum_original_calls':1}
    raw=a.path('run/report.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()==current['raw_report_sha256']
    certificate=load(E/'sqrt-domain-certificate-s32c.json')
    expected=next(r for r in certificate['rows']if r['input_half_bits']==plan['input_half_bits'])
    p=check_report(raw,current,plan,expected)
    assert p.fpcr_before==p.fpcr_after==0 and p.output_single_bits==0x3f400000 and p.output_half_bits==0x3a00
    assert current['status']=='bound_current_same_thread_RN_primitive_call'
    dis=a.path('logs/disassembly.stdout');assert sha(dis)==prepared['disassembly_stdout_sha256']
    assert sha(a.path('logs/disassembly.stderr'))==prepared['disassembly_stderr_sha256']
    window=check_window(dis.read_text());assert window['critical_instruction_sha256']==prepared['critical_window_instruction_sha256']
    symbol=load(a.path('loaded-symbol.private.json'))
    assert symbol['address']==symbol['symbol_address']and symbol['address']-symbol['base']==symbol['offset']==0x15908
    assert Path(symbol['actual_path']).resolve()==a.path('inputs/sealed-trace.dylib').resolve()
    assert symbol['symbol']==current['resolved_symbol']==plan['original_symbol']=='psr_sqrt_scalar'
    static=load(E/'sqrt-static-s32a.json')
    assert sha(a.path('inputs/sealed-trace.dylib'))==current['original_product_sha256']==static['product_sha256']
    assert current['wrapper_product_sha256']==prepared['wrapper_product']['sha256']
    old_archive=Archive(REPO.parent/static['private_storage_relative_to_task'],repo=REPO)
    assert old_archive.verify()['sealed_manifest_sha256']==static['private_manifest_sha256']
    old_dis=old_archive.path('logs/sqrt-disassembly.stdout');assert sha(old_dis)==static['disassembly_stdout_sha256']
    leaf=re.search(r'^[0-9a-f]+ <_psr_sqrt_scalar>:\n(.*?)(?=\n[0-9a-f]+ <|\Z)',old_dis.read_text(),re.M|re.S)[1]
    assert re.search(r'\b15914:\s+fsqrt\s+s0, s0\s*$',leaf,re.M)
    assert not re.search(r'\b(?:bl|blr|msr)\b',leaf)
    assert static['psr_sqrt_scalar_is_direct_f32_FSQRT_no_libm_call']
    command=load(a.path('commands/compile.private.json'))
    assert hashlib.sha256(encoded(command['actual_argv'])).hexdigest()==prepared['compile_command']['argv_sha256']
    assert str(a.path('inputs/fpcr_read_call.c'))in command['actual_argv']and '-frounding-math'in command['actual_argv']
    assert command['exit_code']==0 and prepared['new_compilations']==1 and current['new_compilations_in_run_phase']==0
    assert sha(a.path('logs/compile.stdout'))==command['stdout_sha256']and sha(a.path('logs/compile.stderr'))==command['stderr_sha256']
    assert sha(Path(prepared['compiler']['resolved_path']))==prepared['compiler']['sha256']
    for proof in prepared['proofs']+current['proofs']:
        f=a.path('proofs/'+proof['name']+'.json');d=load(f)
        assert sha(f)==proof['sha256']and d['all_SHA_match']and d['sealed_manifest_sha256']==prepared['private_manifest_sha256']
    assert current['half_conversions_are_new_wrapper_not_old_half_helper']
    assert not current['historical_runs_other_threads_GPU_or_pipeline_certified']
    previous=load(E/'verification-s32.json')
    assert [n for n,h in previous['current_source_sha256'].items()if sha(R/n)!=h]==['bound_validation.py']
    assert all(sha(E/n)==h for n,h in previous['evidence_sha256'].items())
    v3=load(E/'model-precision-v3-s25c6.json')
    assert len(v3['model_source_sha256'])==243 and all(sha(R/n)==h for n,h in v3['model_source_sha256'].items())
    architecture=load(E/'architecture-s33c.json')
    assert architecture['body_read_independently_of_search_snippets']and architecture['historical_S32_retrieval_record_not_rewritten']
    assert {x['id']for x in architecture['records']}=={'FPCR','RN','FCVT','FPSqrt'}
    assert all(x['url'].startswith('https://support.arm.com/documentation/')and len(x['short_quote'].split())<=25 for x in architecture['records'])
    pow_static=load(E/'pow-static-s33e.json');pow_stub=load(E/'pow-stub-s33f.json')
    assert pow_static['new_original_calls']==pow_stub['new_original_calls']==0
    assert pow_static['new_compilations']==pow_stub['new_compilations']==0
    assert pow_static['product_sha256']==pow_stub['product_sha256']==current['original_product_sha256']
    assert sha(a.path('static-pow/disassembly.stdout'))==pow_static['disassembly_stdout_sha256']
    assert sha(a.path('static-pow/source.py'))==pow_static['static_inspector_sha256']
    assert sha(a.path('pow-stub/source.py'))==pow_stub['inspector_sha256']
    assert sha(a.path('pow-stub/metadata.stdout'))==pow_stub['metadata_stdout_sha256']
    metadata=a.path('pow-stub/metadata.stdout').read_text()
    rows=resolve_stub_rows(metadata,int(pow_stub['stub_image_address'],16))
    assert len(rows)==1 and rows[0]['symbol']=='_powf'and rows[0]['index']==136
    assert pow_stub['tail_branch_image_address']=='0x15904'and pow_stub['stub_image_address']=='0x16244'
    assert pow_stub['status']=='static_tail_branch_stub_unresolved'and pow_stub['stub_row_count']==0
    # Preserve the original unresolved receipt. Its regex failed to account
    # for the "0x" prefix, rather than proving the saved table lacks this row.
    pow_followup={'tail_branch_image_address':'0x15904','stub_image_address':'0x16244',
                  'resolved_stub_symbol':'_powf','stub_row':rows[0],
                  'initial_parser_unresolved_receipt_preserved':True,
                  'initial_parser_issue':'word boundary before zero-padded hex digits does not match after0x; fixed by integer address parsing',
                  'corrected_by_saved_metadata_replay_no_additional_tools_or_native_calls':True,
                  'runtime_powf_image_version_accuracy_or_FPCR_not_measured':True,
                  'next_gap':pow_stub['next_gap']}
    bindings={n:saved_binding(n)for n in ['prepare-binding-s33a','run-binding-s33b','test-binding-s33d',
                'pow-binding-s33e','pow-stub-binding-s33f','test-pow-binding-s33g']}
    for label in ['prepare-binding-s33a','run-binding-s33b']:
        pre=load(E/(label+'.pre.json'))
        assert pre['source_sha256_before_execution']['fpcr_binding.py']==sha(R/'fpcr_binding.py')
        assert pre['explicit_input_sha256_before_execution'][str(R.relative_to(REPO)/'fpcr_read_call.c')]==sha(R/'fpcr_read_call.c')
    tests=re.search(r'Ran (\d+) tests in ([\d.]+)s\n\nOK',(E/'test-binding-s33d.log').read_text());assert tests
    pow_tests=re.search(r'Ran (\d+) tests in ([\d.]+)s\n\nOK',(E/'test-pow-binding-s33g.log').read_text());assert pow_tests
    test_count=int(tests[1])+int(pow_tests[1])
    for f in E.glob('*s33*'):
        if f.is_file():
            assert b'\0'not in f.read_bytes()and re.search(rb'/Users/[A-Za-z0-9._-]+/',f.read_bytes())is None
            if f.suffix=='.json':load(f)
    d={'status':'passed_current_single_thread_RN_binding_only',
       'base_HEAD':subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),
       'branch':subprocess.check_output(['git','branch','--show-current'],cwd=REPO,text=True).strip(),
       'version':['iPhone17,3','24A446','SmartStyleV1','CMISmartStyleProcessorV1'],
       'measurement':{k:current[k]for k in ['FPCR_before_hex','FPCR_after_hex','RMode_before','RMode_after',
          'same_thread_binding','native_thread_before','native_thread_after','input_half_bits','input_single_bits',
          'output_single_bits','output_half_bits','original_primitive_calls','FPCR_writes_or_mode_changes']},
       'binding':{'sealed_original_product_sha256':current['original_product_sha256'],'original_entry_image_offset':'0x15908',
                  'original_FSQRT_image_offset':'0x15914','new_wrapper_product_sha256':current['wrapper_product_sha256'],
                  'private_manifest_sha256':current['private_manifest_sha256'],'raw_report_sha256':current['raw_report_sha256'],
                  'compiler':prepared['compiler'],'saved_static_window':window,
                  'input_product_source_hashes_unchanged':True,'half_FCVT_owner':'new wrapper; original half helper not executed'},
       'architecture_sources_sha256':sha(E/'architecture-s33c.json'),
       'architecture_grade':'official rendered page bodies read; short excerpts/paraphrases retained; hardware ISA conformance remains a premise',
       'mathematical_certificate_sha256':sha(E/'sqrt-domain-certificate-s32c.json'),
       'mathematical_certificate_recomputed_this_round':False,
       'current_RN_gap_closed':True,'historical_S25_S29_FPCR_retroactively_certified':False,
       'other_threads_or_original_GPU_iOS_or_full_pipeline_verified':False,
       'new_v4_or_default_model_change':False,'cast16_multiple_free_fields_still_prohibited':True,
       'v3_243_sources_and_old_evidence_unchanged':True,
       'tests':{'count':test_count,'report_tests':int(tests[1]),'saved_stub_parser_tests':int(pow_tests[1]),
                'seconds':float(tests[2])+float(pow_tests[2]),'result':'OK','native_calls_in_tests':0},
       'cost':{'new_native_wrapper_compilations':1,'original_primitive_calls':1,'full_kernel_or_helper_or_pipeline_calls':0,
               'original_product_recompilations':0,'new_wrapper_static_objdump_invocations':1,'all2047_domain_native_reruns':0,
               'targeted_pow_static_objdump_invocations':1,'pow_MachO_metadata_invocations':1,'pow_execution_calls':0},
       'static_pow_followup':pow_followup,
       'pre_execution_bindings':bindings,
       'current_source_sha256':{f.name:sha(f)for f in sorted(R.glob('*.py'))},
       'C_source_sha256':sha(R/'fpcr_read_call.c'),
       'document_sha256':{n:sha(R/n)for n in ['PROGRESS-S33.zh-CN.md','README.zh-CN.md']},
       'evidence_sha256':{f.name:sha(f)for f in sorted(E.glob('*s33*'))if f.is_file()},
       'remaining':['one exact normal primitive input is an FPCR boundary observation, not full-domain runtime accuracy testing',
                    'historical FPCR/other threads/original GPU/iOS/full pipeline unchanged unknown',
                    'powf/generic bright/cast16/multiple free fields not expanded',
                    'old set unknowns/nine-field missing-cache bridge/historicalIR/UI/real same-frame/IMG_2810 build/unknown-source inverse remain']}
    output.write_bytes(encoded(d));print(json.dumps({'status':d['status'],'FPCR':[0,0],'RMode':[0,0],
                                                    'same_thread':True,'original_calls':1,'tests':test_count,'audit_native_calls':0}))
    return d


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path);verify(p.parse_args().output)
