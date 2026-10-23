"""S33 static-only next powf dependency boundary; no loading or execution."""
from pathlib import Path
import argparse,hashlib,json,re,subprocess
from baseline_archive import Archive,encoded,sha
from context_color_api import load

R=Path(__file__).parent
E=R/'evidence'
REPO=R.parents[1]
TOOL=Path('/opt/homebrew/opt/llvm/bin/llvm-objdump')


def run(output):
    if output.exists():raise FileExistsError(output)
    s=load(E/'sqrt-static-s32a.json');p=load(E/'fpcr-prepared-s33a.json')
    old=Archive(REPO.parent/s['private_storage_relative_to_task'],repo=REPO)
    assert old.verify()['sealed_manifest_sha256']==s['private_manifest_sha256']
    a=Archive(REPO.parent/p['private_storage_relative_to_task'],repo=REPO)
    products={p['wrapper_product']['name']:p['wrapper_product']};a.verify(products)
    own=a.write('static-pow/source.py',Path(__file__).read_bytes(),mode=0o400)
    before=a.proof('before-pow-static-read',products);tool_sha=sha(TOOL.resolve())
    text=old.path('inputs/trace.ll').read_text()
    functions={m[1]:m[0]for m in re.finditer(r'^define[^\n]*@([^ (]+)\([^\n]+\{\n.*?^}',text,re.M|re.S)}
    bright=next(v for n,v in functions.items()if'renderBrightAndContrast'in n)
    calls=[l.strip()for l in bright.splitlines()if'@air.pow.'in l]
    scalar=functions['air.pow.f16'];vector=functions['air.pow.v3f16']
    assert scalar.count('fpext half')==2 and '@psr_pow_scalar'in scalar and 'fptrunc float'in scalar
    assert vector.count('call half @air.pow.f16')==3
    cfn=re.search(r'float\s+psr_pow_scalar\([^}]+\}',old.path('inputs/shim.c').read_text())[0]
    assert 'powf(a,b)'in cfn
    binary=a.path('inputs/sealed-trace.dylib');assert sha(binary)==s['product_sha256']
    command=[str(TOOL),'--disassemble','--no-show-raw-insn',
             '--disassemble-symbols=_air.pow.f16,_air.pow.v3f16,_psr_pow_scalar',str(binary)]
    a.write('static-pow/command.private.json',encoded({'actual_argv':command,'tool_sha256':tool_sha}),mode=0o400)
    result=subprocess.run(command,capture_output=True,timeout=15)
    out=a.write('static-pow/disassembly.stdout',result.stdout);err=a.write('static-pow/disassembly.stderr',result.stderr)
    if result.returncode:raise RuntimeError('Static pow read failed; retain logs, no native retry')
    bodies={m[1]:m[2]for m in re.finditer(r'^[0-9a-f]+ <([^>]+)>:\n(.*?)(?=\n[0-9a-f]+ <|\Z)',result.stdout.decode(),re.M|re.S)}
    assert set(['_air.pow.f16','_air.pow.v3f16','_psr_pow_scalar'])<=bodies.keys()
    targets=re.findall(r'\bbl\s+[^<]*<([^>]+)>',bodies['_psr_pow_scalar'])
    # Do not guess the dyld implementation, its identity, or its accuracy.
    after=a.proof('after-pow-static-read',products);old.verify();assert sha(TOOL.resolve())==tool_sha
    d={'status':'static_pow_dependency_located_not_executed','product_sha256':sha(binary),
       'IR_sha256':sha(old.path('inputs/trace.ll')),'shim_C_sha256':sha(old.path('inputs/shim.c')),
       'static_inspector_sha256':sha(own),'tool_sha256':tool_sha,
       'private_storage_relative_to_task':p['private_storage_relative_to_task'],
       'disassembly_stdout_sha256':sha(out),'disassembly_stderr_sha256':sha(err),
       'bright_pow_calls':[{'SSA':int(re.match(r'%(\d+)',l)[1]),'line_sha256':hashlib.sha256(l.encode()).hexdigest()}for l in calls],
       'IR_chain':'bright air.pow.v3f16 -> three air.pow.f16; two half operands fpext to float -> psr_pow_scalar -> fptrunc half',
       'C_implementation':'powf(a,b), subject to actual compiled call target',
       'C_function_sha256':hashlib.sha256(cfn.encode()).hexdigest(),
       'machine_function_sha256':{n:hashlib.sha256(v.encode()).hexdigest()for n,v in bodies.items()},
       'machine_psr_pow_scalar_call_targets':targets,
       'new_original_calls':0,'new_compilations':0,'static_objdump_invocations':1,'proofs':[before,after],
       'next_gap':'External powf implementation/version and per-input f32 error relative to half midpoint are not bound. Current FPCR reading for sqrt does not certify any powf call or historical state; sqrt parity theorem cannot establish transcendental pow accuracy.',
       'powf_executed_or_accuracy_certified':False,'generic_bright_cast16_multiple_fields_unblocked':False}
    a.write('static-pow/result.private.json',encoded(d),mode=0o400);output.write_bytes(encoded(d))
    print(json.dumps({'status':d['status'],'bright_SSA':[r['SSA']for r in d['bright_pow_calls']],
                      'machine_targets':targets,'native_calls':0,'compilations':0}));return d


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path);run(p.parse_args().output)
