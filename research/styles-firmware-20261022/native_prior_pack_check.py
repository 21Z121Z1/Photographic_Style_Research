"""Only the new enqueue matrix-packing loop, unchanged original 60B.

Synthetic object storage and output are supplied by a C ABI. No accepted cast,
positive Tone, SRL or prior arithmetic batch is rerun by this checker.
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


def check(output: Path) -> dict:
    if output.exists():raise FileExistsError(output)
    root=Path(__file__).resolve().parent;e=root/'evidence/cache-follow-24A446'
    m=json.loads((e/'manifest.json').read_text());method=next(r for r in m['methods']if r['file']=='engine-create-enqueue.asm.txt')
    words=[(int(a,16),int(w,16))for a,w in re.findall(r'^([0-9a-f]+): ([0-9a-f]{8})\s',(e/method['file']).read_text(),re.M)]
    allraw=b''.join(struct.pack('<I',w)for _,w in words)
    if hashlib.sha256(allraw).hexdigest()!=method['instructions_sha256']:raise ValueError('Containing method changed')
    selected=[w for a,w in words if 0x1d42e66cc<=a<0x1d42e6708];raw=b''.join(struct.pack('<I',w)for w in selected)
    if len(raw)!=60:raise ValueError('Complete packing loop span')
    assembly='''.text
.p2align 2
.globl _psr_pack
_psr_pack:
stp x29,x30,[sp,#-32]!
str x21,[sp,#16]
mov x21,x0
add x29,x1,#0x90
mov x8,#0
'''+''.join(f'.long 0x{w:08x}\n'for w in selected)+'''
ldr x21,[sp,#16]
ldp x29,x30,[sp],#32
ret
'''
    source=r'''
#include <stdint.h>
#include <stdio.h>
#include <string.h>
extern void psr_pack(const void*,void*);
int main(void){uint32_t in[12],out[12];unsigned char object[0x1c0]={0};
while(fread(in,48,1,stdin)==1){memcpy(object+0x190,in,48);psr_pack(object,out);if(fwrite(out,48,1,stdout)!=1)return 2;}return feof(stdin)?0:3;}
'''
    rng=np.random.default_rng(0x66CC);data=np.r_[np.arange(12,dtype='u4')[None,:],np.full((1,12),0x7fc00000,dtype='u4'),rng.integers(0,2**32,size=(32,12),dtype='u4')]
    expected=data.reshape(-1,3,4).transpose(0,2,1).copy().reshape(-1,12)
    with tempfile.TemporaryDirectory(prefix='psr-prior-pack-')as t:
        w=Path(t);(w/'pack.S').write_text(assembly);(w/'main.c').write_text(source)
        subprocess.run(['xcrun','clang','-arch','arm64',str(w/'main.c'),str(w/'pack.S'),'-o',str(w/'check')],check=True,capture_output=True,timeout=60)
        native=subprocess.run([str(w/'check')],input=data.astype('<u4').tobytes(),capture_output=True,check=True,timeout=30)
        actual=np.frombuffer(native.stdout,dtype='<u4').reshape(-1,12);bad=int(np.count_nonzero(actual!=expected))
        result={'scope':__doc__,'hardware_reference':'iPhone17,3','build':'24A446','original_start':'0x1d42e66cc','original_bytes':60,'original_sha256':hashlib.sha256(raw).hexdigest(),
                'original_instruction_words_patched':0,'records':len(data),'uint32_values':int(data.size),'bit_mismatches':bad,
                'input_sha256':hashlib.sha256(data.tobytes()).hexdigest(),'native_output_sha256':hashlib.sha256(native.stdout).hexdigest(),
                'host_executable_sha256':hashlib.sha256((w/'check').read_bytes()).hexdigest(),'checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'iOS_library_loaded':False,'GPU_executed':False,'original_photos_used':False}
        output.write_text(json.dumps(result,indent=2)+'\n')
        if bad:raise AssertionError('Packing loop mismatch; receipt retained')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path);r=check(p.parse_args().output)
    print(json.dumps({k:r[k]for k in ['records','uint32_values','bit_mismatches']}))
