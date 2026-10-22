"""Only the remaining 38 positive/zero AIR11 fields, recompiled on host CPU.

The accepted FG9/10 checks and all cast/SRL/prior/negative batches are excluded.
Original AIR executes all stores; comparison masks exclude those two fields.
Host pow allowance is an assumption, not Apple GPU fast_pow certification.
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
from positive_tone import PositiveToneStats,PositiveToneContext,coefficients
from negative_tone import h

NEW_FIELDS=np.array([i for i in range(40)if i not in (17+9,17+10)])


def buffers(tone: float,c: PositiveToneContext):
    p=np.zeros(672//4,dtype='f4');s=np.zeros(10640//4,dtype='f4')
    p.view('u4')[0]=c.cast_code;p[2]=tone;p[7]=c.baseline_exposure_field7
    p[172//4:436//4]=c.tone_tuning;p[648//4]=c.scene_brightness;p.view('u4')[652//4]=c.tuning_type
    for (slot,field),value in zip([(0,6),(5,6),(6,5)],c.stats.__dict__.values()):s[(10240+36*slot+4*field)//4]=value
    return p,s


def check(private_air: Path,receipt: Path,output: Path) -> dict:
    if output.exists():raise FileExistsError(output)
    record=json.loads(receipt.read_text())
    if record['canonical_sha256']!='5ca4d2dce19c7e8825f0608b04d3637ddf05f3eb507f33430670617624c02c53':raise ValueError('Exact reviewed AIR required')
    if hashlib.sha256(canonicalize(private_air.read_text())[0].encode()).hexdigest()!=record['canonical_sha256']:raise ValueError('Original AIR changed')
    rng=np.random.default_rng(0xA446194);tones=[0.,-0.,2**-126,2**-24,1.]
    for t in (h('3FD99999A0000000'),.5,.5**(1/.75),h('3FDBDB8CE0000000')**(1/h('3FF3333340000000'))):
        q=np.float32(t);tones.extend(map(float,[np.nextafter(q,np.float32(-np.inf)),q,np.nextafter(q,np.float32(np.inf))]))
    cases=[]
    for scene in (0,2,3,4,5,6,7,8,99):
        for n,tone in enumerate(tones):
            tun=np.linspace(.01,.66,66,dtype='f4');tun[29]=1;tun[30]=-1
            c=PositiveToneContext(PositiveToneStats(.4,.003,.05),tuple(map(float,tun)),scene,[0,13,14][n%3],.1,.5)
            cases.append((tone,c,'structured_boundary'))
    for _ in range(256):
        tun=rng.uniform(-.25,1,size=66).astype('f4');tun[29]=.8;tun[30]=-.8
        c=PositiveToneContext(PositiveToneStats(*map(float,rng.uniform(0,1,size=3))),tuple(map(float,tun)),int(rng.choice([0,2,3,4,5,6,7,8])),int(rng.choice([0,13,14])),float(rng.uniform(-1,1)),float(rng.uniform(.1,2)))
        cases.append((float(rng.uniform(0,1)),c,'random_holdout'))
    root=Path(__file__).resolve().parent;inputs=hashlib.sha256();rows=[];outputs=[]
    with tempfile.TemporaryDirectory(prefix='psr-positive-blocks-')as t:
        w=Path(t);(w/'shims.c').write_text(SHIMS);libpath=w/'positive.dylib'
        subprocess.run(['/opt/homebrew/opt/llvm/bin/clang','-target','arm64-apple-macos27.0','-Wno-override-module','-dynamiclib','-x','ir',str(private_air),'-x','c',str(w/'shims.c'),'-fno-fast-math','-o',str(libpath)],check=True,capture_output=True,timeout=60)
        lib=ctypes.CDLL(str(libpath));fn=lib.RenderingParamsFromStats;fn.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_uint16,ctypes.c_uint16];fn.restype=None
        for index,(tone,c,kind)in enumerate(cases):
            p,s=buffers(tone,c);inputs.update(p.tobytes()+s.tobytes());model=coefficients(tone,c)
            for group in (0,1,2):fn(p.ctypes.data,s.ctypes.data,group,0)
            actual=p[488//4:648//4].copy()[NEW_FIELDS];expected=model.values()[NEW_FIELDS];allowance=model.host_f32_absolute_allowance[NEW_FIELDS]
            outputs.append(actual);diff=abs(actual.astype('f8')-expected)
            rows.append({'index':index,'kind':kind,'tone':tone,'tuning_type':c.tuning_type,'cast_code':c.cast_code,
                         'bit_mismatches_vs_rounded_center':int(np.count_nonzero(actual.view('u4')!=expected.astype('f4').view('u4'))),
                         'max_absolute_error':float(diff.max()),'allowance_violations':int(np.count_nonzero(diff>allowance)),
                         'max_fraction_of_allowance':float(np.max(diff/np.maximum(allowance,1e-300))),
                         'branch_union_allowance_used':bool(np.max(allowance)>.01)})
        r={'scope':__doc__,'hardware_reference':'iPhone17,3','image_build':'24A446','source_AIR_canonical_sha256':record['canonical_sha256'],
           'model_sha256':hashlib.sha256((root/'positive_tone.py').read_bytes()).hexdigest(),'checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           'reused_interval_source_sha256':hashlib.sha256((root/'negative_tone.py').read_bytes()).hexdigest(),
           'reused_skin_source_sha256':hashlib.sha256((root/'positive_tone_skin.py').read_bytes()).hexdigest(),
           'shim_source_sha256':hashlib.sha256(SHIMS.encode()).hexdigest(),'temporary_host_library_sha256':hashlib.sha256(libpath.read_bytes()).hexdigest(),
           'records':len(cases),'kernel_calls':len(cases)*3,'new_fields_per_case':38,'coefficient_values_compared':len(cases)*38,
           'excluded_flat_fields':[26,27],'bit_mismatches_vs_rounded_center':sum(x['bit_mismatches_vs_rounded_center']for x in rows),
           'max_absolute_error':max(x['max_absolute_error']for x in rows),'allowance_violations':sum(x['allowance_violations']for x in rows),
           'max_fraction_of_allowance':max(x['max_fraction_of_allowance']for x in rows),'branch_union_cases':sum(x['branch_union_allowance_used']for x in rows),
           'max_error_without_branch_union':max(x['max_absolute_error']for x in rows if not x['branch_union_allowance_used']),
           'input_sha256':inputs.hexdigest(),'native_output_sha256':hashlib.sha256(np.asarray(outputs,dtype='f4').tobytes()).hexdigest(),
           'accepted_native_batches_repeated':False,'host_pow_allowance_is_assumption':True,'native_GPU_executed':False,'iOS_library_loaded':False,'photo_inputs':0,'rows':rows}
        output.write_text(json.dumps(r,indent=2)+'\n')
        if r['allowance_violations']:raise AssertionError('Positive-block allowance failure; receipt retained')
        return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('private_air',type=Path);p.add_argument('receipt',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args();r=check(a.private_air,a.receipt,a.output);print(json.dumps({k:v for k,v in r.items()if k in ['records','coefficient_values_compared','bit_mismatches_vs_rounded_center','max_absolute_error','allowance_violations','branch_union_cases','max_error_without_branch_union']}))
