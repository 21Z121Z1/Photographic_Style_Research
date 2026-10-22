"""Compare all 40 negative-Tone coefficients against original AIR on host CPU.

Reuses the already explicit C math shims; pow has an assumed 4u host allowance.
There is no Apple GPU fast_pow/denormal or original-photo certification here.
Only new negative branches execute, not the accepted positive-Tone batch.
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
from native_positive_tone_check import SHIMS
from negative_tone import ToneStats,NegativeToneContext,coefficients


def buffers(tone: float,context: NegativeToneContext):
    p=np.zeros(672//4,dtype='f4');s=np.zeros(10640//4,dtype='f4')
    p.view('u4')[0]=context.cast_code;p[2]=tone;p[7]=context.semantic_reference_field7
    p[0xac//4:0xac//4+66]=context.tone_tuning
    p[648//4]=context.scene_brightness;p.view('u4')[652//4]=context.scene_code
    p[656//4]=context.blend_low;p[660//4]=context.blend_high;p[664//4]=context.foreground_modulation_input
    slots=[(0,4),(1,4),(5,4),(6,4),(5,6),(6,6),(9,5),(9,6)]
    vals=list(context.stats.__dict__.values())
    for (slot,field),value in zip(slots,vals):s[(10240+36*slot+4*field)//4]=value
    s[10608//4]=vals[-1]
    return p,s


def check(private_air: Path,receipt: Path,output: Path) -> dict:
    if output.exists():raise FileExistsError(output)
    record=json.loads(receipt.read_text());text=private_air.read_text()
    if hashlib.sha256(canonicalize(text)[0].encode()).hexdigest()!=record['canonical_sha256']:raise ValueError('Source AIR changed')
    rng=np.random.default_rng(0xA446267);cases=[]
    for scene in (0,2,3,4,5,6,7,8,99):
        for tone in (-1.,-.5,-2**-24):
            for blend in (-1.,0.,.5,1.,2.):
                tun=np.linspace(.01,.66,66,dtype='f4');tun[29]=1;tun[30]=-1
                stats=ToneStats(.4,.5,.08,.06,.003,.05,.02,.008,blend)
                cases.append((tone,NegativeToneContext(stats,tuple(map(float,tun)),scene,14,.1,0.,1.,2.,.5),'structured'))
    for _ in range(256):
        tun=rng.uniform(0,1,size=66).astype('f4');tun[29]=.8;tun[30]=-.8
        stats=ToneStats(*map(float,rng.uniform(0,1,size=8)),float(rng.uniform(-1,2)))
        cases.append((float(rng.uniform(-1,-.0001)),NegativeToneContext(stats,tuple(map(float,tun)),int(rng.choice([0,2,3,4,5,6,7,8])),int(rng.choice([0,13,14])),float(rng.uniform(-1,1)),-.25,.75,float(rng.uniform(1,2.2)),float(rng.uniform(.1,2))),'random_holdout'))
    # Explicit zero masks/empty histogram summaries, not silently dropped.
    cases.append((-.5,NegativeToneContext(ToneStats(*([0.]*9)),tuple([0.]*66),blend_low=-1,blend_high=1),'zero_stats'))
    root=Path(__file__).resolve().parent;inputs=hashlib.sha256();rows=[];native_values=[]
    with tempfile.TemporaryDirectory(prefix='psr-negative-tone-')as t:
        w=Path(t);(w/'shims.c').write_text(SHIMS);libpath=w/'negative.dylib'
        subprocess.run(['/opt/homebrew/opt/llvm/bin/clang','-target','arm64-apple-macos27.0','-Wno-override-module','-dynamiclib','-x','ir',str(private_air),'-x','c',str(w/'shims.c'),'-fno-fast-math','-o',str(libpath)],check=True,capture_output=True,timeout=60)
        lib=ctypes.CDLL(str(libpath));fn=lib.RenderingParamsFromStats;fn.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_uint16,ctypes.c_uint16];fn.restype=None
        for index,(tone,context,kind)in enumerate(cases):
            p,s=buffers(tone,context);inputs.update(p.tobytes()+s.tobytes());model=coefficients(tone,context)
            for group in (0,1,2):fn(p.ctypes.data,s.ctypes.data,group,0)
            actual=p[488//4:648//4].copy();native_values.append(actual)
            expected=model.values();diff=abs(actual.astype('f8')-expected)
            bits=int(np.count_nonzero(actual.view('u4')!=expected.astype('f4').view('u4')))
            bad=int(np.count_nonzero(diff>model.host_f32_absolute_allowance))
            rows.append({'index':index,'kind':kind,'tone':tone,'scene_code':context.scene_code,'cast_code':context.cast_code,
                         'bit_mismatches_vs_rounded_continuous_center':bits,'max_absolute_error':float(diff.max()),
                         'allowance_violations':bad,'max_allowance':float(model.host_f32_absolute_allowance.max()),
                         'max_fraction_of_allowance':float(np.max(diff/np.maximum(model.host_f32_absolute_allowance,1e-300)))})
        result={'scope':__doc__,'hardware_reference':'iPhone17,3','image_build':'24A446','source_metallib_sha256':record['source_metallib_sha256'],'source_AIR_canonical_sha256':record['canonical_sha256'],
                'model_sha256':hashlib.sha256((root/'negative_tone.py').read_bytes()).hexdigest(),'checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'shim_source_sha256':hashlib.sha256(SHIMS.encode()).hexdigest(),'temporary_host_library_sha256':hashlib.sha256(libpath.read_bytes()).hexdigest(),
                'records':len(cases),'kernel_calls':len(cases)*3,'coefficient_values':len(cases)*40,
                'bit_mismatches_vs_rounded_continuous_center':sum(r['bit_mismatches_vs_rounded_continuous_center']for r in rows),
                'max_absolute_error':max(r['max_absolute_error']for r in rows),'allowance_violations':sum(r['allowance_violations']for r in rows),
                'max_fraction_of_allowance':max(r['max_fraction_of_allowance']for r in rows),'input_sha256':inputs.hexdigest(),'native_output_sha256':hashlib.sha256(np.asarray(native_values,dtype='f4').tobytes()).hexdigest(),
                'source_field_offsets':{'BG':488,'FG':556,'semantic':620,'stats_field4':10608},
                'host_pow_allowance_is_an_assumption_not_GPU_proof':True,'native_GPU_executed':False,'iOS_library_loaded':False,'photo_inputs':0,'positive_batch_repeated':False,'rows':rows}
        output.write_text(json.dumps(result,indent=2)+'\n')
        if result['allowance_violations']:raise AssertionError('Negative-Tone allowance violations; receipt retained')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('private_air',type=Path);p.add_argument('receipt',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args();r=check(a.private_air,a.receipt,a.output);print(json.dumps({k:r[k]for k in ['records','coefficient_values','bit_mismatches_vs_rounded_continuous_center','max_absolute_error','allowance_violations','max_fraction_of_allowance']}))
