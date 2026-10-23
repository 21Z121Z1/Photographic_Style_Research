"""S33 close the saved tail-branch stub identity using Mach-O metadata only."""
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
    prepared=load(E/'fpcr-prepared-s33a.json');previous=load(E/'pow-static-s33e.json')
    a=Archive(REPO.parent/prepared['private_storage_relative_to_task'],repo=REPO)
    products={prepared['wrapper_product']['name']:prepared['wrapper_product']}
    assert a.verify(products)['sealed_manifest_sha256']==prepared['private_manifest_sha256']
    dis=a.path('static-pow/disassembly.stdout');assert sha(dis)==previous['disassembly_stdout_sha256']
    body=re.search(r'^[0-9a-f]+ <_psr_pow_scalar>:\n(.*?)(?=\n[0-9a-f]+ <|\Z)',dis.read_text(),re.M|re.S)[1]
    branch=re.findall(r'^\s*([0-9a-f]+):\s+b\s+0x([0-9a-f]+)\b',body,re.M)
    assert len(branch)==1
    address,target=branch[0];own=a.write('pow-stub/source.py',Path(__file__).read_bytes(),mode=0o400)
    pre=a.proof('before-pow-stub-read',products);tool_sha=sha(TOOL.resolve())
    command=[str(TOOL),'--macho','--indirect-symbols','--bind','--lazy-bind','--dylibs-used',str(a.path('inputs/sealed-trace.dylib'))]
    a.write('pow-stub/command.private.json',encoded({'actual_argv':command,'tool_sha256':tool_sha}),mode=0o400)
    p=subprocess.run(command,capture_output=True,timeout=15)
    out=a.write('pow-stub/metadata.stdout',p.stdout);err=a.write('pow-stub/metadata.stderr',p.stderr)
    if p.returncode:raise RuntimeError('Static metadata unavailable; preserve, no execution fallback')
    lines=p.stdout.decode().splitlines()
    # The disassembler's nearest-symbol annotation for the branch can name an
    # unrelated undefined symbol. Require the actual stub-address table row.
    rows=[l for l in lines if re.search(r'\b0*'+target+r'\b',l,re.I)]
    match=[l for l in rows if re.search(r'\b_powf\b',l)]
    post=a.proof('after-pow-stub-read',products);assert sha(TOOL.resolve())==tool_sha
    d={'status':'static_tail_branch_stub_resolved_to_powf'if len(match)==1 else'static_tail_branch_stub_unresolved',
       'product_sha256':previous['product_sha256'],'prior_static_sha256':sha(E/'pow-static-s33e.json'),
       'inspector_sha256':sha(own),'tool_sha256':tool_sha,'private_storage_relative_to_task':prepared['private_storage_relative_to_task'],
       'tail_branch_image_address':'0x'+address,'stub_image_address':'0x'+target,
       'stub_row_count':len(rows),'matching_powf_rows':len(match),
       'stub_row_sha256':[hashlib.sha256(l.encode()).hexdigest()for l in rows],
       'bound_stub_symbol':'_powf'if len(match)==1 else None,
       'disassembler_nearest_symbol_annotation_not_used_as_import_identity':True,
       'metadata_stdout_sha256':sha(out),'metadata_stderr_sha256':sha(err),'proofs':[pre,post],
       'actual_dynamic_powf_image_version_or_execution_measured':False,
       'next_gap':'Runtime dyld-resolved powf image/version and its per-input rounding error are unbound. The half-to-f32 powf-to-half chain cannot inherit the sqrt finite-domain rounding theorem or this one sqrt RN observation.',
       'new_original_calls':0,'new_compilations':0,'static_metadata_invocations':1}
    a.write('pow-stub/result.private.json',encoded(d),mode=0o400);output.write_bytes(encoded(d))
    print(json.dumps({'status':d['status'],'tail_branch':d['tail_branch_image_address'],'stub':d['stub_image_address'],
                      'symbol':d['bound_stub_symbol'],'native_calls':0}));return d


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path);run(p.parse_args().output)
