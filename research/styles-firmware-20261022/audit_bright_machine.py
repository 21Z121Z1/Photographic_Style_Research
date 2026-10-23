"""Read-only targeted disassembly of the already authenticated S25 host helper."""
from pathlib import Path
import argparse,json,re,subprocess
from baseline_archive import Archive,encoded,sha
from context_color_api import load

R=Path(__file__).parent
E=R/'evidence'
REPO=R.parents[1]
TOOL=Path('/opt/homebrew/opt/llvm/bin/llvm-objdump')
NM=TOOL.with_name('llvm-nm')


def run(private,output):
    if output.exists():raise FileExistsError(output)
    trace=load(E/'bright-traces-s29b.json')
    original=Archive(REPO.parent/trace['private_storage_relative_to_task'],repo=REPO)
    proof=original.verify()
    a=Archive(private,create=True,repo=REPO)
    binary=a.input('inputs/reused-trace.dylib',original.path('inputs/reused-trace.dylib').read_bytes(),'existing compiled S25 host artifact')
    a.input('sources/audit_bright_machine.py',Path(__file__).read_bytes(),'actual static audit source')
    hashes={str(p):sha(p)for p in [TOOL.resolve(),NM.resolve()]}
    a.seal({'scope':__doc__,'tool_sha256':hashes,'source_archive_manifest_sha256':proof['sealed_manifest_sha256'],'new_compilations':0,'new_native_calls':0})
    pre=a.proof('before-static-read')
    nm=subprocess.run([str(NM),'--defined-only',str(binary)],capture_output=True,timeout=15)
    a.write('logs/nm.stdout',nm.stdout);a.write('logs/nm.stderr',nm.stderr)
    if nm.returncode:raise RuntimeError('Symbol read failed; logs retained')
    symbols=[line.split()[-1]for line in nm.stdout.decode().splitlines()if 'renderBrightAndContrast'in line]
    if len(symbols)!=1:raise ValueError('Exactly one saved bright host symbol required')
    command=[str(TOOL),'--disassemble','--no-show-raw-insn','--disassemble-symbols='+symbols[0],str(binary)]
    dis=subprocess.run(command,capture_output=True,timeout=15)
    stdout=a.write('logs/bright-disassembly.stdout',dis.stdout);stderr=a.write('logs/bright-disassembly.stderr',dis.stderr)
    if dis.returncode:raise RuntimeError('Disassembly failed; logs retained')
    lines=dis.stdout.decode().splitlines()
    instructions=[line for line in lines if re.match(r'\s*[0-9a-f]+:',line)]
    fused=[{'relative_instruction_line':i,'address':line.split(':',1)[0].strip(),
            'mnemonic':line.split(':',1)[1].strip().split()[0],
            'instruction_text_sha256':__import__('hashlib').sha256(line.encode()).hexdigest()}
           for i,line in enumerate(instructions)if re.search(r'\b(fmla|fmadd|fmls|fmsub)\b',line)]
    post=a.proof('after-static-read')
    assert all(sha(Path(p))==h for p,h in hashes.items())
    d={'scope':__doc__,'symbol':symbols[0],'source_product_sha256':sha(binary),
       'private_storage_relative_to_task':str(a.root.relative_to(REPO.parent)),
       'private_manifest_sha256':sha(a.path('prepared.private.json')),
       'disassembly_stdout_sha256':sha(stdout),'stderr_sha256':sha(stderr),
       'instruction_count':len(instructions),'fused_instruction_summaries':fused,
       'SSA137_instruction_mapping':'not inferred from mere FMA presence; targeted dependency mapping still required',
       'tool_identity':{Path(p).name:h for p,h in hashes.items()},'proofs':[pre,post],
       'new_native_calls':0,'new_compilations':0,'GPU_verified':False}
    a.write('result.private.json',encoded(d),mode=0o400);output.write_bytes(encoded(d))
    print(json.dumps({'instruction_count':len(instructions),'fused_instructions':len(fused),'new_native_calls':0}))
    return d


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('private',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args();run(a.private,a.output)
