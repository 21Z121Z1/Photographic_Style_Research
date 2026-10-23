"""S32 full-domain cell-certificate and sealed-machine identity audit."""
from pathlib import Path
import argparse,hashlib,json,re,subprocess
from baseline_archive import Archive,encoded,sha
from context_color_api import load
from sqrt_double_round import FIRST,LAST,COUNT,verify_row

R=Path(__file__).parent
E=R/'evidence'
REPO=R.parents[1]


def verify(output):
    if output.exists():raise FileExistsError(output)
    file=E/'sqrt-domain-certificate-s32c.json';c=load(file);static=load(E/'sqrt-static-s32a.json')
    assert c['input_count']==COUNT==2047 and c['domain_half_bits']==[FIRST,LAST]
    assert [r['input_half_bits']for r in c['rows']]==list(range(FIRST,LAST+1))
    assert c['input_encoding_order_sha256']==hashlib.sha256(b''.join(i.to_bytes(2,'little')for i in range(FIRST,LAST+1))).hexdigest()
    assert all(verify_row(r)for r in c['rows'])
    assert c['counterexamples']==[]and c['counterexample_count']==0 and c['single_to_half_midpoint_hits']==0
    assert not c['float_or_libm_used_for_mathematics']and not c['actual_FPCR_or_GPU_verified']
    assert static['psr_sqrt_scalar_is_direct_f32_FSQRT_no_libm_call']
    assert static['half_machine_extension_call_truncation_confirmed']and static['vector_three_scalar_calls_confirmed']
    assert static['f32_FSQRT_addresses']==['15914']and not static['local_chain_FPCR_write_detected']
    assert not static['FPCR_runtime_state_measured']and not static['original_GPU_or_iOS_execution']
    archive=Archive(REPO.parent/static['private_storage_relative_to_task'],repo=REPO)
    proof=archive.verify();assert proof['sealed_manifest_sha256']==static['private_manifest_sha256']
    assert sha(archive.path('inputs/reused-trace.dylib'))==static['product_sha256']
    dis=archive.path('logs/sqrt-disassembly.stdout');assert sha(dis)==static['disassembly_stdout_sha256']
    text=dis.read_text()
    for address,pattern in [('15914',r'fsqrt\s+s0, s0'),('15608',r'fcvt\s+s0, h0'),('15610',r'fcvt\s+h0, s0')]:
        assert re.search(r'\b'+address+r':\s+'+pattern+r'\s*$',text,re.M)
    oldmachine=load(E/'bright-machine-s29d.json')
    assert oldmachine['source_product_sha256']==static['product_sha256']
    root=REPO.parent/oldmachine['private_storage_relative_to_task']/'logs/bright-disassembly.stdout'
    assert sha(root)==oldmachine['disassembly_stdout_sha256']
    rootline=next(l for l in root.read_text().splitlines()if re.search(r'\bcf40:\s+bl\s+[^<]*<_air.sqrt.v3f16>',l))
    # Saved native evidence remains two observations at one unique selected
    # input, not 2047 host executions.
    by_input={r['input_half_bits']:r for r in c['rows']};old=load(E/'bright-residual-attribution-s29c.json');calibration=[]
    for key,p in old['unique_points'].items():
        roots=next(s['host_bits']for s in p['corrected_stages']if s['SSA']==133)
        for channel,(x,h)in enumerate(zip(p['native132_half_bits'],roots)):
            if FIRST<=x<=LAST:
                assert by_input[x]['ideal_half_sqrt_bits']==h
                calibration.append({'input_key':key,'channel':channel,'input_half_bits':x,'saved_native133_half_bits':h})
    assert len(calibration)==2 and len({r['input_half_bits']for r in calibration})==1
    for n,h in c['source_sha256'].items():assert sha(R/n)==h
    assert c['plan_sha256']==sha(E/'sqrt-domain-plan-s32b.json')
    previous=load(E/'verification-s31.json')
    assert [n for n,h in previous['current_source_sha256'].items()if sha(R/n)!=h]==['bound_validation.py']
    assert all(sha(E/n)==h for n,h in previous['evidence_sha256'].items())
    precision=load(E/'model-precision-v3-s25c6.json')
    assert len(precision['model_source_sha256'])==243 and all(sha(R/n)==h for n,h in precision['model_source_sha256'].items())
    bindings={}
    for name in ['static-binding-s32a','freeze-binding-s32b','certificate-binding-s32c','test-binding-s32d']:
        b=load(E/(name+'.json'));pre=E/(name+'.pre.json');log=E/(name+'.log')
        assert b['exit_code']==0 and b['source_unchanged_during_command']and b['inputs_unchanged_during_command']
        assert sha(pre)==b['pre_run_binding_sha256']and sha(log)==b['log_sha256']
        bindings[name]={'pre_sha256':sha(pre),'post_sha256':sha(E/(name+'.json')),'log_sha256':sha(log),'elapsed_seconds':b['elapsed_seconds']}
    pre=load(E/'certificate-binding-s32c.pre.json');assert pre['input_sha256_before_execution']['sqrt-domain-plan-s32b.json']==c['plan_sha256']
    tests=re.search(r'Ran (\d+) tests in ([\d.]+)s\n\nOK',(E/'test-binding-s32d.log').read_text());assert tests and int(tests[1])==11
    assert not subprocess.check_output(['git','diff','--name-only','HEAD','--',str(E)],cwd=REPO,text=True).strip()
    for f in E.glob('*s32*'):
        if f.is_file():
            assert b'\0'not in f.read_bytes()and re.search(rb'/Users/[A-Za-z0-9._-]+/',f.read_bytes())is None
            if f.suffix=='.json':load(f)
    d={'status':'passed_complete_selected_sqrt_double_rounding_and_static_implementation_audit',
       'base_HEAD':subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),
       'branch':subprocess.check_output(['git','branch','--show-current'],cwd=REPO,text=True).strip(),
       'version':['iPhone17,3','24A446','SmartStyleV1','CMISmartStyleProcessorV1'],
       'certificate_sha256':sha(file),'complete_input_domain':[FIRST,LAST],'input_count':COUNT,
       'mathematical_double_rounding_counterexamples':0,'single_result_half_midpoint_hits':0,
       'mathematical_assumptions':'correct RN-even binary32 sqrt followed by RN-even binary16 conversion',
       'proof_scope':'one sqrt primitive and declared finite input domain only',
       'sealed_binary_identity':{'product_sha256':static['product_sha256'],'trace_IR_sha256':static['trace_IR_sha256'],
                                 'shim_C_sha256':static['shim_C_sha256'],'private_manifest_sha256':static['private_manifest_sha256']},
       'actual_static_chain':{'SSA133_root_call':'0xcf40 -> air.sqrt.v3f16',
                              'root_call_line_sha256':hashlib.sha256(rootline.encode()).hexdigest(),
                              'half_extension':'0x15608 FCVT s0,h0 exact on this domain',
                              'single_sqrt':'0x15914 FSQRT s0,s0; no external sqrtf/libm call',
                              'half_conversion':'0x15610 FCVT h0,s0',
                              'vector_lanes':'three scalar calls, independently'},
       'runtime_precision_grade':'sealed hardware instruction path identified; equality is conditional on architectural RN behavior, active FPCR RN and successful completion, not measured runtime accuracy',
       'actual_FPCR_measured':False,'original_GPU_or_iOS_verified':False,
       'normal_finite_domain_no_flush_dependency':True,
       'existing_host_calibration':calibration,'existing_host_unique_selected_inputs':1,
       'architecture_reference_index':{
          'FSQRT':'https://developer.arm.com/documentation/ddi0487/mc/-Part-C-The-AArch64-Instruction-Set/-Chapter-C7-A64-Advanced-SIMD-and-floating-point-Instruction-Descriptions/-C7-2-Alphabetical-list-of-A64-Advanced-SIMD-and-floating-point-instructions/-C7-2-199-FSQRT--scalar-?lang=en',
          'FCVT':'https://developer.arm.com/documentation/ddi0487/mc/-Part-C-The-AArch64-Instruction-Set/-Chapter-C3-A64-Instruction-Set-Overview/-C3-8-Data-processing---SIMD-and-floating-point/-C3-8-4-Floating-point-conversion?lang=en',
          'FPCR':'https://developer.arm.com/documentation/ddi0487/mb/-Part-C-The-AArch64-Instruction-Set/-Chapter-C5-The-A64-System-Instruction-Class/-C5-2-Special-purpose-registers/-C5-2-8-FPCR--Floating-point-Control-Register',
          'retrieval_grade':'official search excerpts/index available; dynamic full pseudocode/page body not independently read; links are not a measured implementation proof'},
       'tests':{'count':11,'seconds':float(tests[2]),'result':'OK',
                'all2047_independent_midpoint_cell_checks':True,
                'outside_half_input_real_counterexample_prevents_generalization':True},
       'cost':{'exact_domain_rows_generated':2047,'audit_cell_certificate_checks':2047,
               'test_extra_row_regenerations':2,'new_original_CPU_or_GPU_calls':0,
               'new_helper_or_full_model_calls':0,'new_native_compilations':0,
               'static_nm_invocations':1,'static_targeted_objdump_invocations':1},
       'v3_S29_to31_sources_profiles_evidence_unchanged':True,'default_sqrt_or_bright_model_updated':False,
       'pre_execution_bindings':bindings,
       'current_source_sha256':{f.name:sha(f)for f in sorted(R.glob('*.py'))},
       'document_sha256':{n:sha(R/n)for n in ['PROGRESS-S32.zh-CN.md','README.zh-CN.md']},
       'evidence_sha256':{f.name:sha(f)for f in sorted(E.glob('*s32*'))if f.is_file()},
       'remaining':['active FPCR RN state and runtime implementation accuracy not measured',
                    'ISA conformance is an explicit premise; official dynamic pseudocode not fully retrieved',
                    'no generic libm/GPU sqrt accuracy or all-pipeline equality claim',
                    'powf/generic bright/cast16/multiple free fields not expanded',
                    'old set unknowns/nine-field missing-cache bridge/historicalIR/UI/real same-frame/IMG_2810 build/unknown-source inverse remain']}
    output.write_bytes(encoded(d));print(json.dumps({'status':d['status'],'inputs':2047,'counterexamples':0,
                                                    'actual_chain':'FSQRT f32 + FCVT half','FPCR_measured':False,
                                                    'tests':11,'new_native_calls':0}))
    return d


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path);verify(p.parse_args().output)
