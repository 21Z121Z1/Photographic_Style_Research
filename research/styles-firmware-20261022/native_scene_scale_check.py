"""New 68B original CPU scene-scaling block only, not an iOS library run."""
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
from tone_interface import RendererControls,ResolvedSceneType,scale_controls


def check(output: Path):
    if output.exists():raise FileExistsError(output)
    root=Path(__file__).resolve().parent;e=root/'evidence/render-follow-24A446';m=json.loads((e/'manifest.json').read_text())
    method=next(r for r in m['methods']if r['file']=='render-static-parameters.asm.txt')
    words=[(int(a,16),int(w,16))for a,w in re.findall(r'^([0-9a-f]+): ([0-9a-f]{8})\s',(e/method['file']).read_text(),re.M)]
    assert hashlib.sha256(b''.join(struct.pack('<I',w)for _,w in words)).hexdigest()==method['instructions_sha256']
    selected=[w for a,w in words if 0x1d42f2328<=a<0x1d42f236c];raw=b''.join(struct.pack('<I',w)for w in selected)
    if len(raw)!=68:raise ValueError('Complete scene-scale branch block required')
    assembly='''.text
.p2align 2
.globl _psr_scene_scale
_psr_scene_scale:
sub sp,sp,#64
stp x24,x27,[sp]
stp d8,d9,[sp,#16]
str d10,[sp,#32]
mov x24,x1
mov w27,w2
ldr s8,[x0]
ldr s9,[x0,#4]
ldr s10,[x0,#8]
mov w0,w2
'''+''.join(f'.long 0x{w:08x}\n'for w in selected)+'''
str s8,[x3]
str s9,[x3,#4]
str s10,[x3,#8]
ldr d10,[sp,#32]
ldp d8,d9,[sp,#16]
ldp x24,x27,[sp]
add sp,sp,#64
ret
'''
    source=r'''
#include <stdint.h>
#include <stdio.h>
typedef struct{float user[3];uint32_t scene;float params[168];} Input;
extern void psr_scene_scale(const float*,const float*,uint32_t,float*);
int main(void){Input in;float out[3];while(fread(&in,sizeof(in),1,stdin)==1){psr_scene_scale(in.user,in.params,in.scene,out);if(fwrite(out,12,1,stdout)!=1)return 2;}return feof(stdin)?0:3;}
'''
    rng=np.random.default_rng(0x2328);payload=[];expected=[]
    for scene in (0,3,21,4,0xffffffff):
        for n in range(16):
            controls=RendererControls(*map(float,rng.uniform([0,-1,-1],[1,1,1])))
            tun=rng.uniform(-1,1,size=66).astype('f4');p=np.zeros(168,dtype='f4');p[43:109]=tun
            result=scale_controls(controls,ResolvedSceneType(scene),tuple(tun))
            payload.append(controls.array().astype('<f4').tobytes()+struct.pack('<I',scene)+p.astype('<f4').tobytes())
            expected.append([result.intensity,result.tone,result.color])
    data=b''.join(payload)
    with tempfile.TemporaryDirectory(prefix='psr-scene-scale-')as t:
        w=Path(t);(w/'block.S').write_text(assembly);(w/'main.c').write_text(source)
        subprocess.run(['xcrun','clang','-arch','arm64',str(w/'main.c'),str(w/'block.S'),'-o',str(w/'check')],check=True,capture_output=True,timeout=60)
        native=subprocess.run([str(w/'check')],input=data,capture_output=True,check=True,timeout=30)
        actual=np.frombuffer(native.stdout,dtype='<f4').reshape(-1,3);bad=int(np.count_nonzero(actual.view('u4')!=np.asarray(expected,dtype='f4').view('u4')))
        r={'scope':__doc__,'hardware_reference':'iPhone17,3','build':'24A446','original_start':'0x1d42f2328','original_bytes':68,'original_instruction_words_patched':0,
           'original_sha256':hashlib.sha256(raw).hexdigest(),'records':len(payload),'values':len(payload)*3,'bit_mismatches':bad,
           'checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'interface_model_sha256':hashlib.sha256((root/'tone_interface.py').read_bytes()).hexdigest(),
           'input_sha256':hashlib.sha256(data).hexdigest(),'native_output_sha256':hashlib.sha256(native.stdout).hexdigest(),'host_executable_sha256':hashlib.sha256((w/'check').read_bytes()).hexdigest(),
           'iOS_library_loaded':False,'GPU_executed':False,'scene_classifier_executed':False,'accepted_native_batches_repeated':False}
        output.write_text(json.dumps(r,indent=2)+'\n')
        if bad:raise AssertionError('Scene scaling differs; receipt retained')
        return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path);r=check(p.parse_args().output)
    print(json.dumps({k:r[k]for k in ['records','values','bit_mismatches']}))
