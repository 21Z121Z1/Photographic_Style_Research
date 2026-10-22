"""Run the complete 40B leaf with synthetic object fields in an owned C ABI.

The unchanged branch and return have no PC-relative data, ObjC, GPU or library
calls. This tests this scalar only, never an actual iOS object or photo pipeline.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import platform
import re
import struct
import subprocess
import tempfile
import numpy as np
from srl_parameter import adjust_parameter


def check(output: Path) -> dict:
    if platform.system()!='Darwin' or platform.machine()!='arm64':raise RuntimeError('Requires Apple Silicon macOS')
    if output.exists():raise FileExistsError(output)
    root=Path(__file__).resolve().parent;evidence=root/'evidence/cache-follow-24A446'
    row=next(r for r in json.loads((evidence/'manifest.json').read_text())['methods']if r['file']=='metal-srl-adjust.asm.txt')
    text=(evidence/row['file']).read_text();words=[int(w,16)for w in re.findall(r'^1d433f[0-9a-f]+: ([0-9a-f]{8})\s',text,re.M)]
    raw=b''.join(struct.pack('<I',w)for w in words)
    if len(raw)!=40 or hashlib.sha256(raw).hexdigest()!=row['instructions_sha256']:raise ValueError('Verified leaf changed')
    asm='.text\n.p2align 2\n.globl _psr_srl_parameter\n_psr_srl_parameter:\n'+'\n'.join(f'.long 0x{w:08x}'for w in words)+'\n'
    source=r'''
#include <stdint.h>
#include <stdio.h>
#include <string.h>
extern float psr_srl_parameter(const void *);
int main(void){
  uint32_t pair[2]; unsigned char object[0x5a4]={0}; uint64_t fpcr=0;
  __asm__ volatile("msr fpcr, %0" : : "r"(fpcr));
  while(fread(pair,4,2,stdin)==2){
    memcpy(object+0x598,pair,4);memcpy(object+0x5a0,pair+1,4);
    float out=psr_srl_parameter(object);if(fwrite(&out,4,1,stdout)!=1)return 2;
  }return feof(stdin)?0:3;
}
'''
    curves=[0xff800000,0xbf800000,0x80000000,0,1,0x00800000,0x3e800000,0x3f000000,0x3f7fffff,0x3f800000,0x40000000,0x7f800000,0x7fc00000,0x7f800001]
    adjustments=[0,1,2,2**24-1,2**24,2**32-1]
    pairs=[(c,a)for c in curves for a in adjustments]
    rng=np.random.default_rng(0x5985a0)
    pairs += [(int(rng.integers(0,2**32,dtype='u4')),int(rng.integers(0,2**32,dtype='u4')))for _ in range(4096)]
    payload=b''.join(struct.pack('<II',*p)for p in pairs)
    expected=np.array([adjust_parameter(np.array([c],dtype='u4').view('f4')[0],a)for c,a in pairs],dtype='<f4')
    with tempfile.TemporaryDirectory(prefix='psr-srl-parameter-')as t:
        work=Path(t);(work/'leaf.S').write_text(asm);(work/'main.c').write_text(source)
        subprocess.run(['xcrun','clang','-arch','arm64','-O2',str(work/'main.c'),str(work/'leaf.S'),'-o',str(work/'check')],check=True,capture_output=True,timeout=60)
        native=subprocess.run([str(work/'check')],input=payload,capture_output=True,check=True,timeout=30)
        actual=np.frombuffer(native.stdout,dtype='<u4');wanted=expected.view('<u4')
        if len(actual)!=len(wanted):raise ValueError('Short native result')
        mismatch=int(np.count_nonzero(actual!=wanted))
        result={'scope':__doc__,'hardware_reference':'iPhone17,3','firmware_build':'24A446','framework_uuid':'0A9BC064-A4BC-330E-861A-C70A637B14B3',
                'original_leaf_start':row['first_address'],'original_leaf_bytes':40,'original_leaf_sha256':row['instructions_sha256'],
                'records':len(pairs),'structured_records':84,'random_raw_f32_and_u32_records':4096,'bit_mismatches':mismatch,'fpcr':0,
                'nonfinite_input_records':sum(not np.isfinite(np.array([c],dtype='u4').view('f4')[0])for c,_ in pairs),
                'synthetic_input_sha256':hashlib.sha256(payload).hexdigest(),'native_output_sha256':hashlib.sha256(native.stdout).hexdigest(),
                'model_sha256':hashlib.sha256((root/'srl_parameter.py').read_bytes()).hexdigest(),'checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'harness_C_sha256':hashlib.sha256(source.encode()).hexdigest(),'harness_assembly_sha256':hashlib.sha256(asm.encode()).hexdigest(),
                'host_executable_sha256':hashlib.sha256((work/'check').read_bytes()).hexdigest(),
                'native_GPU_executed':False,'iOS_library_loaded':False,'whole_camera_or_SRL_gain_verified':False,'photo_inputs':0}
        output.write_text(json.dumps(result,indent=2)+'\n')
        if mismatch:raise AssertionError('Original leaf differs; receipt retained')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path);r=check(p.parse_args().output)
    print(json.dumps({k:r[k]for k in ['records','nonfinite_input_records','bit_mismatches']}))
