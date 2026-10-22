"""Compare the conditional prior model with original AIR recompiled for CPU.

Only target-independent arithmetic kernels AIR108/109 are compiled. This is
neither the original GPU binary nor original iOS CPU machine code. The target
triple is overridden by clang; full original AIR text and bitcode stay private.
"""
from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import tempfile
import numpy as np

from air_alpha import canonicalize
from style_prior import SystemLayout, PriorFactors, lhs_updates, rhs_updates


def sha(raw):return hashlib.sha256(raw).hexdigest()


def check(air_scratch: Path, alpha_receipt: Path, output: Path, clang: str) -> dict:
    if output.exists():raise FileExistsError(output)
    alpha=json.loads(alpha_receipt.read_text());sources=[]
    for index in (108,109):
        path=air_scratch/'ios'/f'{index:04d}.ll.txt';raw=path.read_bytes()
        row=next(r for r in alpha['module_pairs'] if r['ios_index']==index)
        if sha(canonicalize(raw.decode())[0].encode())!=row['ios_canonical_sha256']:
            raise ValueError('Private AIR no longer matches verified iOS resource receipt')
        sources.append({'index':index,'private_air_sha256':sha(raw),'canonical_sha256':row['ios_canonical_sha256']})
    result={'scope':__doc__,'source_metallib_sha256':alpha['ios_metallib_sha256'],'sources':sources,
            'clang_version':subprocess.check_output([clang,'--version'],text=True).splitlines()[0],
            'source_model_sha256':sha(Path(__file__).with_name('style_prior.py').read_bytes()),
            'checker_sha256':sha(Path(__file__).read_bytes()),'cases':[],
            'native_GPU_verified':False,'original_iOS_CPU_code_executed':False,
            'sample_or_library_access':False,'original_SIMD_reduction_certified':False}
    with tempfile.TemporaryDirectory(prefix='psr-prior-ir-') as t:
        libpath=Path(t)/'prior.dylib';cmd=[clang,'-target','arm64-apple-macos27.0','-Wno-override-module','-dynamiclib','-x','ir',*[str(air_scratch/'ios'/f'{i:04d}.ll.txt') for i in (108,109)],'-o',str(libpath)]
        subprocess.run(cmd,check=True,capture_output=True,timeout=60)
        result['compiled_library_sha256']=sha(libpath.read_bytes())
        disassembly=subprocess.check_output([str(Path(clang).with_name('llvm-objdump')),'-d',str(libpath)],text=True)
        result['host_compilation_fmadd_instruction_count']=disassembly.count('\tfmadd\t')
        result['host_disassembly_sha256']=sha(disassembly.encode())
        lib=ctypes.CDLL(str(libpath));lhs=getattr(lib,'StyleEngineCreateLinearSystem::AddPriorToLHS');rhs=getattr(lib,'StyleEngineCreateLinearSystem::AddPriorToRHS')
        ptr=ctypes.c_void_p
        lhs.argtypes=[ptr,ptr,ptr,ptr,ctypes.c_uint16];rhs.argtypes=[ptr,ptr,ptr,ptr,ptr,ctypes.c_uint16]
        lhs.restype=rhs.restype=None
        rng=np.random.default_rng(0x24A446)
        layouts=[SystemLayout(p,s,w) for p in (4,7,10) for s in (1,7,31) for w in (1,2,5)]
        layouts += [SystemLayout(int(rng.choice([4,7,10])),int(rng.integers(1,65)),int(rng.integers(1,6))) for _ in range(128)]
        for case,layout in enumerate(layouts):
            factors=PriorFactors(*rng.uniform(2**-9,32,size=3));scales=rng.uniform(0,4,size=3*layout.weight_plane_count).astype('f4');prior=rng.uniform(-1,1,size=12).astype('f4')
            params=ctypes.create_string_buffer(struct.pack('<4I',layout.polynomial_count,0,layout.system_size,layout.weight_plane_count)+bytes(48))
            factors_=factors.array()
            for name,fn,updates in [('lhs',lhs,lhs_updates(layout,np.arange(layout.polynomial_count*layout.weight_plane_count*2),factors,scales)),('rhs',rhs,rhs_updates(layout,np.arange(24*layout.weight_plane_count),factors,scales,prior))]:
                buffer=rng.uniform(-1,1,size=int(updates.offsets.max())+1).astype('f4');expected=updates.apply(buffer);actual=buffer.copy()
                gids=np.arange(len(updates.offsets))
                for gid in gids:
                    args=[ctypes.addressof(params),actual.ctypes.data,factors_.ctypes.data]
                    if name=='rhs':args.append(prior.ctypes.data)
                    args.extend([scales.ctypes.data,int(gid)]);fn(*args)
                diff=np.abs(actual.astype('f8')-expected.astype('f8'))
                # Conservative finite-normal-input rounding allowance for three
                # f32 arithmetic operations vs fast contraction, per write.
                u=2**-24;gamma=3*u/(1-3*u)
                allowance=np.zeros(len(actual),dtype='f8')
                # Absolute product, not rounded/cancelled final result.
                if name=='lhs':
                    group=np.where(gids%layout.polynomial_count==0,0,np.where(gids%layout.polynomial_count>3,2,1));plane=(gids//layout.polynomial_count)%layout.weight_plane_count
                    product=np.abs(scales.reshape(-1,3)[plane,group].astype('f8')*factors_[group].astype('f8'))
                else:
                    group=(gids%12>2).astype('i8');plane=(gids//12)%layout.weight_plane_count
                    product=np.abs(factors_[group].astype('f8')*scales.reshape(-1,3)[plane,group].astype('f8')*prior[gids%12].astype('f8'))
                allowance[updates.offsets]=gamma*(np.abs(buffer[updates.offsets].astype('f8'))+product)+3*2**-126
                bad=int(np.count_nonzero(diff>allowance))
                result['cases'].append({'case':case,'layout':layout.__dict__,'side':name,'writes':len(gids),'buffer_values_checked':len(actual),
                                        'bit_mismatches':int(np.count_nonzero(actual.view('u4')!=expected.view('u4'))),
                                        'max_absolute_error':float(diff.max()),'rounding_bound_violations':bad,
                                        'input_sha256':sha(buffer.tobytes()+params.raw+factors_.tobytes()+scales.tobytes()+prior.tobytes()),'actual_sha256':sha(actual.tobytes())})
        result['layout_cases']=len(layouts);result['kernel_cases']=len(result['cases'])
        for key in ['writes','buffer_values_checked','bit_mismatches','rounding_bound_violations']:
            result[key]=sum(r[key] for r in result['cases'])
        result['max_absolute_error']=max(r['max_absolute_error'] for r in result['cases'])
        output.write_text(json.dumps(result,indent=2)+'\n')
        if result['rounding_bound_violations']:raise AssertionError('Rounding allowance failed; receipt retained')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('air_scratch',type=Path);p.add_argument('alpha_receipt',type=Path);p.add_argument('output',type=Path);p.add_argument('--clang',default='/opt/homebrew/opt/llvm/bin/clang')
    a=p.parse_args();r=check(a.air_scratch,a.alpha_receipt,a.output,a.clang)
    print(json.dumps({k:r[k] for k in ['layout_cases','kernel_cases','writes','buffer_values_checked','bit_mismatches','rounding_bound_violations','max_absolute_error']}))
