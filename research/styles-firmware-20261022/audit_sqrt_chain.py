"""S32 saved SSA133 IR/C/machine chain audit, zero native execution."""
from pathlib import Path
import argparse,hashlib,json,re,subprocess
from baseline_archive import Archive,encoded,sha
from context_color_api import load

R=Path(__file__).parent
E=R/'evidence'
REPO=R.parents[1]
TOOL=Path('/opt/homebrew/opt/llvm/bin/llvm-objdump')
NM=TOOL.with_name('llvm-nm')


def run(private,output):
    if output.exists():raise FileExistsError(output)
    detail=load(E/'bright-detail-s25c.json')
    old=Archive(REPO.parent/detail['private_storage_relative_to_task'],repo=REPO)
    old_proof=old.verify(detail['products'])
    assert old_proof['sealed_manifest_sha256']==detail['private_manifest_sha256']
    a=Archive(private,create=True,repo=REPO)
    for old_name,new_name in [('inputs/trace.ll','inputs/trace.ll'),('inputs/shim.c','inputs/shim.c'),
                              ('artifacts/trace.dylib','inputs/reused-trace.dylib')]:
        a.input(new_name,old.path(old_name).read_bytes(),'exact existing S25 input/product, no recompile')
    a.input('sources/audit_sqrt_chain.py',Path(__file__).read_bytes(),'actual static audit source')
    tools={str(p.resolve()):sha(p.resolve())for p in [TOOL,NM]}
    a.seal({'scope':__doc__,'prior_manifest_sha256':detail['private_manifest_sha256'],
            'prior_compiler_command':detail['command'],'tool_sha256':tools})
    before=a.proof('before-static-read')
    text=a.path('inputs/trace.ll').read_text();functions={m[1]:m[0]for m in re.finditer(r'^define[^\n]*@([^ (]+)\([^\n]+\{\n.*?^}',text,re.M|re.S)}
    bright=next(body for name,body in functions.items()if'renderBrightAndContrast'in name)
    ssa133=next(l for l in bright.splitlines()if re.match(r'\s*%133 =',l))
    scalar=functions['air.sqrt.f16'];vector=functions['air.sqrt.v3f16']
    assert '@air.sqrt.v3f16'in ssa133
    assert 'fpext half'in scalar and '@psr_sqrt_scalar'in scalar and 'fptrunc float'in scalar
    assert vector.count('call half @air.sqrt.f16')==3
    c=a.path('inputs/shim.c').read_text();c_fn=re.search(r'float\s+psr_sqrt_scalar\([^}]+\}',c)[0]
    assert 'sqrtf('in c_fn
    binary=a.path('inputs/reused-trace.dylib')
    nm=subprocess.run([str(NM),'--defined-only',str(binary)],capture_output=True,timeout=15)
    a.write('logs/nm.stdout',nm.stdout);a.write('logs/nm.stderr',nm.stderr)
    if nm.returncode:raise RuntimeError('Symbol read failed; retained')
    wanted=['_air.sqrt.f16','_air.sqrt.v3f16','_psr_sqrt_scalar']
    found={s:next((l.split()[-1]for l in nm.stdout.decode().splitlines()if l.split()[-1]==s),None)for s in wanted}
    if not all(found.values()):raise ValueError('Required sealed sqrt symbols unavailable; do not infer implementation')
    cmd=[str(TOOL),'--disassemble','--no-show-raw-insn','--disassemble-symbols='+','.join(wanted),str(binary)]
    p=subprocess.run(cmd,capture_output=True,timeout=15)
    dis=a.write('logs/sqrt-disassembly.stdout',p.stdout);err=a.write('logs/sqrt-disassembly.stderr',p.stderr)
    if p.returncode:raise RuntimeError('Targeted disassembly failed; retained')
    groups={};current=None
    for line in p.stdout.decode().splitlines():
        label=re.match(r'^[0-9a-f]+ <([^>]+)>:',line)
        if label:current=label[1];groups[current]=[]
        elif current and re.match(r'\s*[0-9a-f]+:',line):groups[current].append(line.strip())
    if set(wanted)-groups.keys():raise ValueError('Selected sqrt machine body missing')
    def summary(symbol):
        lines=groups[symbol]
        return {'machine_body_sha256':hashlib.sha256(encoded(lines)).hexdigest(),'instruction_count':len(lines),
                'instructions':[{'address':l.split(':',1)[0],'mnemonic':l.split(':',1)[1].strip().split()[0],
                                 'line_sha256':hashlib.sha256(l.encode()).hexdigest()}for l in lines],
                'call_targets':re.findall(r'\bbl\s+[^<]*<([^>]+)>','\n'.join(lines))}
    sc='\n'.join(groups['_psr_sqrt_scalar']);hf='\n'.join(groups['_air.sqrt.f16']);vf='\n'.join(groups['_air.sqrt.v3f16'])
    fsqrt=re.findall(r'^\s*([0-9a-f]+):\s+fsqrt\s+s\d+,\s*s\d+\s*$',sc,re.M)
    extension=re.findall(r'^\s*([0-9a-f]+):\s+fcvt\s+s\d+,\s*h\d+\s*$',hf,re.M)
    truncation=re.findall(r'^\s*([0-9a-f]+):\s+fcvt\s+h\d+,\s*s\d+\s*$',hf,re.M)
    direct=bool(len(fsqrt)==1 and not re.search(r'\bbl\b',sc))
    half_chain=bool(extension and truncation and '<_psr_sqrt_scalar>'in hf)
    vector_chain=len(re.findall(r'\bbl\s+[^<]*<_air.sqrt.f16>',vf))==3
    after=a.proof('after-static-read');old.verify(detail['products'])
    assert all(sha(Path(p))==h for p,h in tools.items())
    d={'scope':__doc__,'product_sha256':sha(binary),'trace_IR_sha256':sha(a.path('inputs/trace.ll')),
       'shim_C_sha256':sha(a.path('inputs/shim.c')),'SSA133_line_sha256':hashlib.sha256(ssa133.encode()).hexdigest(),
       'scalar_IR_sha256':hashlib.sha256(scalar.encode()).hexdigest(),'vector_IR_sha256':hashlib.sha256(vector.encode()).hexdigest(),
       'C_function_sha256':hashlib.sha256(c_fn.encode()).hexdigest(),
       'IR_chain':'SSA133 -> air.sqrt.v3f16 -> three scalar air.sqrt.f16 -> exact half-to-f32 extension -> psr_sqrt_scalar -> f32-to-half truncation',
       'C_source_implementation':'sqrtf(a), subject to actual compilation',
       'machine_functions':{s:summary(s)for s in wanted},
       'psr_sqrt_scalar_is_direct_f32_FSQRT_no_libm_call':direct,
       'f32_FSQRT_addresses':fsqrt,'half_to_f32_FCVT_addresses':extension,'f32_to_half_FCVT_addresses':truncation,
       'half_machine_extension_call_truncation_confirmed':half_chain,'vector_three_scalar_calls_confirmed':vector_chain,
       'local_chain_FPCR_write_detected':bool(re.search(r'\bmsr\s+FPCR\b',sc+'\n'+hf+'\n'+vf,re.I)),
       'FPCR_runtime_state_measured':False,'architecture_RN_accuracy_is_separate_premise':True,
       'original_GPU_or_iOS_execution':False,'new_native_calls':0,'new_compilations':0,
       'prior_binary_and_inputs_unchanged':True,'prior_manifest_sha256':detail['private_manifest_sha256'],
       'private_storage_relative_to_task':str(a.root.relative_to(REPO.parent)),
       'private_manifest_sha256':sha(a.path('prepared.private.json')),'proofs':[before,after],
       'disassembly_stdout_sha256':sha(dis),'disassembly_stderr_sha256':sha(err),
       'tool_sha256':{Path(p).name:h for p,h in tools.items()}}
    a.write('result.private.json',encoded(d),mode=0o400);output.write_bytes(encoded(d))
    print(json.dumps({'direct_f32_FSQRT':direct,'half_extension_and_truncation':half_chain,
                      'three_lanes':vector_chain,'fsqrt_addresses':fsqrt,'new_native_calls':0,'FPCR_measured':False}))
    return d


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('private',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args();run(a.private,a.output)
