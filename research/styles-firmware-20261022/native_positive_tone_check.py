"""Compare positive Tone's theta9/10 against original AIR recompiled for CPU.

AIR math intrinsics used by unrelated outputs receive explicit host C shims.
The two certified target SSA chains use only f32 multiply/subtract, no shim.
This is a coefficient check, not original GPU execution or pixel validation.
"""
from __future__ import annotations
import argparse
import ctypes
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import numpy as np
from air_alpha import canonicalize
from positive_tone_skin import coefficients


SHIMS=r'''
#include <math.h>
float psr_max(float a,float b) __asm__("_air.fast_fmax.f32");
float psr_min(float a,float b) __asm__("_air.fast_fmin.f32");
float psr_pow(float a,float b) __asm__("_air.fast_pow.f32");
float psr_mix(float a,float b,float t) __asm__("_air.mix.f32");
float psr_clamp(float a,float lo,float hi) __asm__("_air.fast_clamp.f32");
float psr_max(float a,float b){return fmaxf(a,b);}
float psr_min(float a,float b){return fminf(a,b);}
float psr_pow(float a,float b){return powf(a,b);}
float psr_mix(float a,float b,float t){return a+(b-a)*t;}
float psr_clamp(float a,float lo,float hi){return fminf(fmaxf(a,lo),hi);}
'''


def check(private_air: Path,receipt: Path,output: Path) -> dict:
    if output.exists():raise FileExistsError(output)
    record=json.loads(receipt.read_text());text=private_air.read_text()
    if hashlib.sha256(canonicalize(text)[0].encode()).hexdigest()!=record['canonical_sha256']:
        raise ValueError('Original AIR identity changed')
    root=Path(__file__).resolve().parent;clang='/opt/homebrew/opt/llvm/bin/clang'
    rng=np.random.default_rng(0x11A446)
    tones=np.r_[np.array([0,1e-12,.1,.25,.4,.5,.6,.8,1],dtype='f4'),rng.uniform(0,1,size=1024).astype('f4')]
    actual=[];expected=[];input_hash=hashlib.sha256()
    with tempfile.TemporaryDirectory(prefix='psr-tone-skin-')as t:
        work=Path(t);libpath=work/'render.dylib';(work/'shims.c').write_text(SHIMS)
        subprocess.run([clang,'-target','arm64-apple-macos27.0','-Wno-override-module','-dynamiclib','-x','ir',str(private_air),'-x','c',str(work/'shims.c'),'-fno-fast-math','-o',str(libpath)],check=True,capture_output=True,timeout=60)
        lib=ctypes.CDLL(str(libpath));fn=lib.RenderingParamsFromStats
        fn.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_uint16,ctypes.c_uint16];fn.restype=None
        for tone in tones:
            params=np.zeros(672//4,dtype='f4');stats=np.zeros(10640//4,dtype='f4')
            params.view('u4')[0]=rng.integers(0,17);params[2]=tone
            # Unrelated foreground fields depend on these; theta9/10 don't.
            params[(0xac+11*4)//4]=rng.uniform(0,1)
            stats[:]=rng.uniform(.001,1,size=len(stats)).astype('f4')
            input_hash.update(params.tobytes()+stats.tobytes())
            fn(params.ctypes.data,stats.ctypes.data,1,0)
            actual.append(params[[592//4,596//4]].copy())
            p=coefficients(float(tone));expected.append([p.theta9,p.theta10])
        a=np.asarray(actual,dtype='f4');e=np.asarray(expected,dtype='f4');diff=abs(a.astype('f8')-e.astype('f8'))
        td=tones.astype('f8');u=2**-24;gamma=3*u/(1-3*u)
        bound=gamma*np.stack([2.75*td+3.75*td*td,.20829999446868896*td*td+.708299994468689*td],axis=1)+3*2**-126
        violations=int(np.count_nonzero(diff>bound))
        result={'scope':__doc__,'hardware_reference':'iPhone17,3','image_build':'24A446','source_metallib_sha256':record['source_metallib_sha256'],
                'source_payload_sha256':record['payload_sha256'],'source_AIR_canonical_sha256':record['canonical_sha256'],
                'model_sha256':hashlib.sha256((root/'positive_tone_skin.py').read_bytes()).hexdigest(),
                'checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'explicit_C_shims_sha256':hashlib.sha256(SHIMS.encode()).hexdigest(),
                'temporary_host_library_sha256':hashlib.sha256(libpath.read_bytes()).hexdigest(),
                'target_fields':{'SSRParams.tone_offset':8,'SSRFGAdjustment_offset':556,'theta9_offset':592,'theta10_offset':596},
                'records':len(tones),'coefficient_values':int(a.size),'bit_mismatches':int(np.count_nonzero(a.view('u4')!=e.view('u4'))),
                'max_absolute_error':float(diff.max()),'rounding_bound_violations':violations,
                'per_field_max_absolute_error':diff.max(axis=0).tolist(),'synthetic_input_sha256':input_hash.hexdigest(),
                'host_output_sha256':hashlib.sha256(a.tobytes()).hexdigest(),'coefficient_domain':'supplied, already scene-scaled SSRParams tone in [0,1]',
                'target_theta9_theta10_depend_on_host_pow_shim':False,'unrelated_AIR_outputs_certified':False,
                'native_GPU_executed':False,'photo_inputs':0,'unique_camera_inverse_verified':False}
        output.write_text(json.dumps(result,indent=2)+'\n')
        if violations:raise AssertionError('Coefficient rounding allowance failed; receipt retained')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('private_air',type=Path);p.add_argument('receipt',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args();r=check(a.private_air,a.receipt,a.output)
    print(json.dumps({k:r[k]for k in ['records','coefficient_values','bit_mismatches','max_absolute_error','rounding_bound_violations']}))
