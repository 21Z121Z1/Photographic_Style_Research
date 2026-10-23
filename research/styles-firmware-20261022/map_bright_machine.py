"""Tie trace SSA132/134..138 stores to exact saved-host machine dependencies."""
from pathlib import Path
import argparse,hashlib,json,re
from baseline_archive import encoded,sha
from bright_low_host import PROFILE,PRODUCT_SHA
from context_color_api import load

R=Path(__file__).parent
E=R/'evidence'
REPO=R.parents[1]


def run(output):
    if output.exists():raise FileExistsError(output)
    audit=load(E/'bright-machine-s29d.json')
    assembly=REPO.parent/audit['private_storage_relative_to_task']/'logs/bright-disassembly.stdout'
    assert sha(assembly)==audit['disassembly_stdout_sha256'] and audit['source_product_sha256']==PRODUCT_SHA
    lines={int(m[1],16):m[2].strip()for line in assembly.read_text().splitlines()
           if(m:=re.match(r'\s*([0-9a-f]+):\s+(.*)',line))}
    # Addresses are scoped to the pinned dylib above. Check opcode, registers,
    # trace offsets and spill/reload, rather than mere presence of FMA.
    needed={0xc848:r'adrp\s+x8,.*<_psr_trace_bright>',0xc84c:r'add\s+x8, x8, #0x0',
            0xc850:r'stur\s+x8, \[x29, #-0x50\]',
            0xcf0c:r'bl\s+.*<_air.mix.v3f16>',0xcf14:r'stur\s+d0, \[x29, #-0xd8\]',
            0xcf58:r'ldur\s+d0, \[x29, #-0xd8\]',
            0xcf84:r'movi.4h\s+v2, #0x4c, lsl #8',0xcf88:r'fmul.4h\s+v7, v0, v2',
            0xcfb4:r'movi.4h\s+v5, #0xca, lsl #8',0xcfb8:r'fmla.4h\s+v5, v2, v0',
            0xcfe4:r'fmul.4h\s+v7, v5, v0',
            0xd010:r'movi.4h\s+v2, #0x44, lsl #8',0xd014:r'fmla.4h\s+v2, v0, v5',
            0xd040:r'fmul.4h\s+v5, v2, v0'}
    for address,pattern in needed.items():assert re.fullmatch(pattern,lines[address]),hex(address)
    detail=load(E/'bright-detail-s25c.json')
    metadata=load(REPO.parent/detail['private_storage_relative_to_task']/'prepared.private.json')['metadata']
    offsets={ssa:offset*4 for ssa,ty,n,offset in metadata['probes']['bright']['layout']}
    stores={132:[0xcf24,0xcf30,0xcf3c],134:[0xcf98,0xcfa4,0xcfb0],
            135:[0xcfc8,0xcfd4,0xcfe0],136:[0xcff4,0xd000,0xd00c],
            137:[0xd024,0xd030,0xd03c],138:[0xd050,0xd05c,0xd068]}
    for ssa,addresses in stores.items():
        for lane,address in enumerate(addresses):
            offset=offsets[ssa]+lane*4
            assert re.fullmatch(r'str\s+s\d+, \[x8, #0x'+format(offset,'x')+r'\]',lines[address]),(ssa,hex(address))
    # No calls or vector0/vector5 redefinitions in the asserted operand lifetime.
    interval={a:s for a,s in lines.items()if 0xcf58<a<0xd014}
    forbidden_v0=[hex(a)for a,s in interval.items()if re.match(r'\S+\s+(?:v0(?:\.|,)|[dsh]0,)',s)]
    forbidden_v5=[hex(a)for a,s in interval.items()if a>0xcfb8 and re.match(r'\S+\s+(?:v5(?:\.|,)|[dsh]5,)',s)]
    assert not forbidden_v0 and not forbidden_v5 and not any(re.match(r'b(?:l|r)\b',s)for s in interval.values())
    d={'scope':__doc__,'product_sha256':PRODUCT_SHA,'source_disassembly_sha256':sha(assembly),
       'symbol':audit['symbol'],'absolute_virtual_addresses_scoped_to_exact_dylib':True,
       'SSA132_register':'v0 restored from the same spill as original mix return',
       'SSA135_register':'v5 = half-FMA(half16, square132, half-12); half0xca00 is -12',
       'SSA136_register':'rounded half product is observed separately; not used as input to SSA137 machine FMA',
       'SSA137_register':'v2 = half-FMA(square132, multiplier135, half4)',
       'SSA138_register':'half multiply SSA137*square132',
       'trace_store_byte_offsets':{str(s):offsets[s]for s in stores},
       'SSA135_FMA_address':'0xcfb8','SSA137_FMA_address':'0xd014',
       'machine_instruction_window_sha256':hashlib.sha256(encoded({hex(a):s for a,s in lines.items()if 0xcf58<=a<=0xd06c})).hexdigest(),
       'asserted_instruction_text_sha256':{hex(a):hashlib.sha256(lines[a].encode()).hexdigest()for a in needed},
       'register_lifetimes_checked_no_calls_or_operand_overwrites':True,
       'leaf_profile':PROFILE,'leaf_source_sha256':sha(R/'bright_low_host.py'),
       'leaf_domain':'exact half3 square132 in [1/16,1]; RN-even assumption; no upstream or complete-bright certification',
       'rounding_mode':'RN-even assumed; FPCR was not measured',
       'normality_reason':'16*x is exact and finite; 16*x-12 has minimum nonzero half magnitude at least2^-7; product with x>=2^-4 at least2^-11; 4+(16*x-12)*x has real minimum1.75 and remains positive normal under these half roundings; all outputs bounded finite',
       'SSA135_fusion_effect':'scaling a half by16 is exact on this domain, so separate134+135 and fused135 agree;137 can differ because135*x is rounded in136',
       'original_GPU_or_unobserved_SSA_full_graph_proof':False,'new_original_calls':0,'new_compilations':0}
    output.write_bytes(encoded(d));print(json.dumps({'mapped135':'0xcfb8','mapped137':'0xd014','trace137_offset':offsets[137],
                                                     'node_domain':'half3 [1/16,1], RN assumption','new_original_calls':0}))
    return d


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path);run(p.parse_args().output)
