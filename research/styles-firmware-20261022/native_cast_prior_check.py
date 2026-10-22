"""Compare original cast arithmetic and full conversion leaf in a C ABI.

The 556B interpolation/strength block is unchanged, including its two ADRPs:
owned assembly padding keeps the original relative code/constant-page layout.
The complete 152B conversion leaf is also unchanged. ObjC table selection,
allocation, iOS library loading, Metal and original frame context are excluded.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import tempfile
import numpy as np
from cast_prior import CastControls,CastTable,interpolate


def words(path,start,end,expected):
    rows=[(int(a,16),int(w,16))for a,w in re.findall(r'^([0-9a-f]+): ([0-9a-f]{8})\s',path.read_text(),re.M)if start<=int(a,16)<end]
    raw=b''.join(struct.pack('<I',w)for _,w in rows)
    if [a for a,_ in rows]!=list(range(start,end,4)) or hashlib.sha256(raw).hexdigest()!=expected:raise ValueError('Reviewed source block changed')
    return raw


def check(private: Path,selection: Path,output: Path) -> dict:
    if output.exists():raise FileExistsError(output)
    root=Path(__file__).resolve().parent;e=root/'evidence/cache-methods-24A446';manifest=json.loads((e/'manifest.json').read_text())
    a=next(r for r in manifest['methods']if r['file']=='prior-main.asm.txt');b=next(r for r in manifest['methods']if r['file']=='prior-conversion.asm.txt')
    source=e/a['file'];rows=[(int(x,16),int(w,16))for x,w in re.findall(r'^([0-9a-f]+): ([0-9a-f]{8})\s',source.read_text(),re.M)]
    body=b''.join(struct.pack('<I',w)for addr,w in rows if 0x1d42ed848<=addr<0x1d42eda74)
    if len(body)!=556:raise ValueError('Arithmetic block span')
    # Whole containing method is the source anchor, not an invented new hash.
    words(source,int(a['first_address'],16),int(a['end_exclusive'],16),a['instructions_sha256'])
    conv=words(e/b['file'],int(b['first_address'],16),int(b['end_exclusive'],16),b['instructions_sha256'])
    if len(conv)!=152:raise ValueError('Complete conversion leaf span')
    lines=lambda raw:'\n'.join(f'.long 0x{int.from_bytes(raw[i:i+4],"little"):08x}'for i in range(0,len(raw),4))+'\n'
    asm='''.text
.p2align 2
.globl _psr_prior_interp
_psr_prior_interp:
sub sp, sp, #0xc0
stp x21, x30, [sp, #0xa0]
str d8, [sp, #0x90]
str x2, [sp, #0x98]
ldr s0, [x0]
str q0, [sp, #0x10]
ldr s1, [x0, #4]
str q1, [sp]
ldr s8, [x0, #8]
ldr s3, [x0, #12]
str q3, [sp, #0x20]
ldr s0, [x0, #16]
str q0, [sp, #0x30]
ldr s0, [x0, #20]
dup v0.4s, v0.s[0]
str q0, [sp, #0x50]
mov x21, x1
b _psr_prior_body
.p2align 12
_psr_prior_page:
.space 0x848
_psr_prior_body:
'''+lines(body)+'''
ldr x0, [sp, #0x98]
ldp q0, q1, [sp, #0x60]
ldr q2, [sp, #0x80]
stp q0, q1, [x0]
str q2, [x0, #0x20]
ldr d8, [sp, #0x90]
ldp x21, x30, [sp, #0xa0]
add sp, sp, #0xc0
ret
.space 0x1f6ca0-(.-_psr_prior_page)
_psr_prior_constants:
.long 0x3f7fffff,0x3f7fffff,0x3f7fffff,0x00000000,0x00040004,0x00000001
.p2align 2
.globl _psr_prior_convert
_psr_prior_convert:
'''+lines(conv)
    c=r'''
#include <stdint.h>
#include <stdio.h>
typedef float F4 __attribute__((vector_size(16)));
typedef struct{F4 a,b,c;} Matrix;
typedef struct{float controls[6];uint32_t mono;float table[600];} Input;
extern void psr_prior_interp(const float*,const float*,float*);
extern Matrix psr_prior_convert(const float*,uint32_t);
int main(void){Input in;float memory[12];uint64_t fpcr=0;
__asm__ volatile("msr fpcr, %0" : : "r"(fpcr));
if(sizeof(Input)!=2428||sizeof(Matrix)!=48)return 3;
while(fread(&in,sizeof(in),1,stdin)==1){
 psr_prior_interp(in.controls,in.table,memory);
 Matrix out=psr_prior_convert(memory,in.mono);
 if(fwrite(memory,48,1,stdout)!=1||fwrite(&out,48,1,stdout)!=1)return 2;
}return feof(stdin)?0:4;}
'''
    meta=json.loads(selection.read_text());rng=np.random.default_rng(0xED848);cases=[]
    banks=[]
    for digest in sorted(meta['unique_tables']):
        raw=(private/(digest+'.f32')).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=digest:raise ValueError('Private actual table changed')
        banks.append((digest,CastTable(np.frombuffer(raw,dtype='<f4').reshape(5,5,2,3,4))))
    synthetic=rng.uniform(-2,2,size=(5,5,2,3,4)).astype('f4');banks.append(('synthetic_random',CastTable(synthetic)))
    for bank,table in banks:
        axes=[(-1,-1,0),(1,1,1),(-2,2,-1),(2,-2,2),(-.5,0,.5),(.5,.5,.5)]
        axes += [tuple(map(float,rng.uniform([-1,-1,0],[1,1,1])))for _ in range(8)]
        for n,axis in enumerate(axes):
            for mono in (False,True):
                strength=[0.,1.,.375,-.5,1.5][n%5]
                ctl=CastControls(*axis,strength);model=interpolate(ctl,table,monochrome=mono)
                base=np.float32(1/3)if mono else np.float32(1);h=np.float32(1/3)if mono else np.float32(0)
                packed=np.r_[ctl.array(),base,h].astype('<f4').tobytes()+struct.pack('<I',mono)+table.values.astype('<f4').tobytes()
                cases.append(({'bank':bank,'controls':list(axis)+[strength],'monochrome':mono},packed,model))
    payload=b''.join(p for _,p,_ in cases)
    with tempfile.TemporaryDirectory(prefix='psr-cast-prior-')as t:
        work=Path(t);(work/'body.S').write_text(asm);(work/'main.c').write_text(c)
        subprocess.run(['xcrun','clang','-arch','arm64','-O2','-fno-fast-math',str(work/'main.c'),str(work/'body.S'),'-o',str(work/'check')],check=True,capture_output=True,timeout=60)
        nm=subprocess.check_output(['/opt/homebrew/opt/llvm/bin/llvm-nm',str(work/'check')],text=True)
        symbols={name:int(addr,16)for addr,name in re.findall(r'^([0-9a-f]+) [a-zA-Z] (_psr_prior_(?:page|body|constants))$',nm,re.M)}
        if symbols['_psr_prior_body']-symbols['_psr_prior_page']!=0x848 or symbols['_psr_prior_constants']-symbols['_psr_prior_page']!=0x1f6ca0 or symbols['_psr_prior_page']%4096:
            raise ValueError('Original ADRP relative layout was not preserved')
        native=subprocess.run([str(work/'check')],input=payload,capture_output=True,check=True,timeout=60)
        actual=np.frombuffer(native.stdout,dtype='<f4').reshape(len(cases),2,3,4);bad=[0,0];rows=[]
        for i,(tag,_,model)in enumerate(cases):
            mb=int(np.count_nonzero(actual[i,0].view('u4')!=model.memory_vectors.view('u4')))
            cb=int(np.count_nonzero(actual[i,1].view('u4')!=model.output_coefficients.view('u4')))
            bad[0]+=mb;bad[1]+=cb;rows.append({**tag,'interpolation_bit_mismatches':mb,'conversion_bit_mismatches':cb})
        report={'scope':__doc__,'hardware_reference':'iPhone17,3','image_build':'24A446','framework_uuid':meta['framework_uuid'],
                'original_arithmetic_bytes':556,'original_arithmetic_sha256':hashlib.sha256(body).hexdigest(),'original_conversion_bytes':152,'original_conversion_sha256':b['instructions_sha256'],
                'original_instruction_words_patched':0,'original_ADRP_layout_preserved':True,'host_symbol_relative_offsets':{k:hex(v-symbols['_psr_prior_page'])for k,v in symbols.items()},
                'actual_private_tables':len(banks)-1,'synthetic_tables':1,'records':len(cases),'values_per_stage':len(cases)*12,
                'interpolation_bit_mismatches':bad[0],'conversion_bit_mismatches':bad[1],
                'payload_sha256':hashlib.sha256(payload).hexdigest(),'native_output_sha256':hashlib.sha256(native.stdout).hexdigest(),
                'harness_C_sha256':hashlib.sha256(c.encode()).hexdigest(),'harness_assembly_sha256':hashlib.sha256(asm.encode()).hexdigest(),'host_executable_sha256':hashlib.sha256((work/'check').read_bytes()).hexdigest(),
                'model_sha256':hashlib.sha256((root/'cast_prior.py').read_bytes()).hexdigest(),'checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'fpcr':0,'iOS_library_loaded':False,'native_GPU_executed':False,'original_frame_context':False,'raw_tables_uploaded':False,'rows':rows}
        output.write_text(json.dumps(report,indent=2)+'\n')
        if any(bad):raise AssertionError(f'Original arithmetic differs: {bad}; receipt retained')
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('private',type=Path);p.add_argument('selection',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args();r=check(a.private,a.selection,a.output);print(json.dumps({k:r[k]for k in ['records','values_per_stage','interpolation_bit_mismatches','conversion_bit_mismatches']}))
