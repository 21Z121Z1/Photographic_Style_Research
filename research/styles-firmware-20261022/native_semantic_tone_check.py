"""Original complete semantic helper recompiled with explicit host texture shims.

Original helper text/metadata are retained; external AIR intrinsics get declared
host definitions. Ideal float linear/clamp texture interpolation is a shim,
not original GPU sampler execution. New unit only, no accepted batch reruns.
"""
from __future__ import annotations
import argparse,ctypes,hashlib,json,re,subprocess,tempfile
from pathlib import Path
import numpy as np
from air_alpha import canonicalize
from semantic_tone import Curve1D,SemanticInputs,forward_half,forward_set,EPS


SAMPLER_C=r'''
#include <stdint.h>
#include <math.h>
float psr_sample(const void *texture,float coordinate){
 uint32_t n=*(const uint32_t*)texture;const float *p=(const float*)((const char*)texture+4);
 float q=fminf(fmaxf(coordinate-.5f,0),n-1);uint32_t i=(uint32_t)floorf(q),j=i+1<n?i+1:i;
 return p[i]+(p[j]-p[i])*(q-i);
}
'''
SHIM_IR=r'''
define i32 @air.get_width_texture_2d(ptr addrspace(1) %p,i32 %lod){
 %n=load i32,ptr addrspace(1) %p
 ret i32 %n
}
define half @air.convert.f.f16.u.i32(i32 %n){
 %x=uitofp i32 %n to half
 ret half %x
}
define <3 x half> @air.mix.v3f16(<3 x half> %a,<3 x half> %b,<3 x half> %w){
 %d=fsub fast <3 x half> %b,%a
 %p=fmul fast <3 x half> %d,%w
 %v=fadd fast <3 x half> %a,%p
 ret <3 x half> %v
}
define <3 x half> @air.fmin.v3f16(<3 x half> %a,<3 x half> %b){
 %c=fcmp olt <3 x half> %a,%b
 %v=select <3 x i1> %c,<3 x half> %a,<3 x half> %b
 ret <3 x half> %v
}
declare float @psr_sample(ptr,float)
define { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) %p,ptr addrspace(2) %sampler,<2 x float> %xy,i1 %a,<2 x i32> %off,i1 %b,float %c,float %d,i32 %e){
 %u=extractelement <2 x float> %xy,i32 0
 %t=addrspacecast ptr addrspace(1) %p to ptr
 %f=call float @psr_sample(ptr %t,float %u)
 %h=fptrunc float %f to half
 %v=insertelement <4 x half> zeroinitializer,half %h,i32 0
 %r=insertvalue {<4 x half>,i8} zeroinitializer,<4 x half> %v,0
 ret {<4 x half>,i8} %r
}
'''


def fragment(source: str):
    root=Path(__file__).resolve().parent;record=json.loads((root/'evidence/tone-field-links.json').read_text())
    if hashlib.sha256(canonicalize(source)[0].encode()).hexdigest()!=record['consumer_AIR_canonical_sha256']:raise ValueError('Exact AIR10 required')
    m=next(m for m in re.finditer(r'^define[^\n]*?@([^ (]+)\([^\n]+\{\n',source,re.M)if 'renderSemanticToneAdjustments'in m[1]);end=source.index('\n}',m.end())+2;body=source[m.start():end]
    expected=next(r for r in record['consumer_functions']if r['name']==m[1])['function_text_sha256']
    if hashlib.sha256(body.encode()).hexdigest()!=expected:raise ValueError('Complete original helper changed')
    definitions=dict(re.findall(r'^!(\d+) = (.*)$',source,re.M));ids=set(re.findall(r'!(\d+)',body));pending=list(ids)
    while pending:
        n=pending.pop()
        for other in re.findall(r'!(\d+)',definitions[n]):
            if other not in ids:ids.add(other);pending.append(other)
    attrs=set(re.findall(r'#(\d+)',body));attribute_lines=[]
    for n in attrs:attribute_lines.append(re.search(r'^attributes #'+n+r' = .*$',source,re.M)[0])
    types=re.search(r'^%struct.SSRSemanticToneAdjustment = .*$',source,re.M)[0]
    sampler=re.search(r'^@__air_sampler_state = .*$',source,re.M)[0]
    wrapper=['define void @psr_semantic(ptr %input,ptr %params,ptr %tex,ptr %output){']
    for n in range(7):wrapper += [f'%p{n}=getelementptr float,ptr %input,i64 {n}',f'%f{n}=load float,ptr %p{n}',f'%h{n}=fptrunc float %f{n} to half']
    for group,base in [('x',0),('r',3)]:
        wrapper += [f'%{group}0=insertelement <3 x half> poison,half %h{base},i32 0',f'%{group}1=insertelement <3 x half> %{group}0,half %h{base+1},i32 1',f'%{group}=insertelement <3 x half> %{group}1,half %h{base+2},i32 2']
    wrapper += ['%pp=addrspacecast ptr %params to ptr addrspace(1)','%tp=addrspacecast ptr %tex to ptr addrspace(1)',f'%out=call fastcc <3 x half> @{m[1]}(<3 x half> %x,<3 x half> %r,half %h6,ptr addrspace(1) %tp,ptr addrspace(1) %pp)']
    for n in range(3):wrapper += [f'%o{n}=extractelement <3 x half> %out,i32 {n}',f'%of{n}=fpext half %o{n} to float',f'%op{n}=getelementptr float,ptr %output,i64 {n}',f'store float %of{n},ptr %op{n}']
    wrapper += ['ret void','}']
    text='\n'.join([types,sampler,body,SHIM_IR,'\n'.join(wrapper),*attribute_lines,*[f'!{n} = {definitions[n]}'for n in sorted(ids,key=int)]])+'\n'
    return text,expected


def check(private_air: Path,output: Path):
    if output.exists():raise FileExistsError(output)
    ir,function_sha=fragment(private_air.read_text());rng=np.random.default_rng(0x5976);cases=[]
    for n in [2,17,256]:
        samples=np.linspace(0,1,n)**1.2;curve=Curve1D(tuple(samples),'supplied helper working RGB/GTC coordinate')
        for weight in [0.,.3,1.]:
            for rgb,ref in [([0,0,0],[.1,.2,.3]),([.2,.4,.8],[.25,.5,1]),([1,1,1],[2,1,.5]),([.01,.02,.03],[2**-10,EPS,.1])]:
                for values in [[1,1,1,1,1,1,1],[.6,.8,.8,1.2,.7,.5,.9]]:
                    cases.append((SemanticInputs(tuple(rgb),tuple(ref),weight,curve),np.asarray(values,dtype='f4'),'structured'))
    for _ in range(64):
        n=17;curve=Curve1D(tuple(np.linspace(0,1,n)**rng.uniform(.7,1.5)),'supplied helper working RGB/GTC coordinate')
        inp=SemanticInputs(tuple(rng.uniform(0,1,3)),tuple(rng.uniform(.05,1,3)),float(rng.uniform(0,1)),curve)
        cases.append((inp,rng.uniform(.2,1.3,7).astype('f4'),'random_holdout'))
    rows=[];inputs_hash=hashlib.sha256();outputs=[]
    with tempfile.TemporaryDirectory(prefix='psr-semantic-helper-')as t:
        w=Path(t);(w/'fragment.ll').write_text(ir);(w/'sampler.c').write_text(SAMPLER_C);libpath=w/'semantic.dylib'
        compile_result=subprocess.run(['/opt/homebrew/opt/llvm/bin/clang','-target','arm64-apple-macos27.0','-Wno-override-module','-dynamiclib',str(w/'fragment.ll'),str(w/'sampler.c'),'-o',str(libpath)],capture_output=True,text=True,timeout=60)
        if compile_result.returncode:raise RuntimeError(compile_result.stderr[:6000])
        lib=ctypes.CDLL(str(libpath));fn=lib.psr_semantic;fn.argtypes=[ctypes.c_void_p]*4;fn.restype=None
        for index,(inp,p,kind)in enumerate(cases):
            x,ref,person=inp.arrays();data=np.r_[x,ref,person].astype('f4');n=len(inp.curve.red_samples)
            tex=np.r_[np.array([n],dtype='u4').view('f4'),np.asarray(inp.curve.red_samples,dtype='f4')];out=np.zeros(3,dtype='f4')
            inputs_hash.update(data.tobytes()+p.tobytes()+tex.tobytes());fn(data.ctypes.data,p.ctypes.data,tex.ctypes.data,out.ctypes.data)
            model=forward_half(inp,p).astype('f4');bounds=forward_set(inp,p,p);diff=abs(out.astype('f8')-model)
            covered=bool(np.all(out>=bounds.lower)and np.all(out<=bounds.upper));outputs.append(out.copy())
            rows.append({'index':index,'kind':kind,'width':n,'bit_mismatches_half':int(np.count_nonzero(out.astype('f2').view('u2')!=model.astype('f2').view('u2'))),'max_absolute_error':float(diff.max()),'set_allowance_covered':covered})
    r={'scope':__doc__,'hardware_reference':'iPhone17,3','build':'24A446','original_helper_text_sha256':function_sha,'original_helper_body_modified':False,
       'host_fragment_sha256':hashlib.sha256(ir.encode()).hexdigest(),'sampler_C_sha256':hashlib.sha256(SAMPLER_C.encode()).hexdigest(),'model_sha256':hashlib.sha256((Path(__file__).parent/'semantic_tone.py').read_bytes()).hexdigest(),'checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
       'records':len(cases),'RGB_values':len(cases)*3,'bit_mismatches_half':sum(r['bit_mismatches_half']for r in rows),'max_absolute_error':max(r['max_absolute_error']for r in rows),'set_allowance_violations':sum(not r['set_allowance_covered']for r in rows),
       'input_sha256':inputs_hash.hexdigest(),'native_output_sha256':hashlib.sha256(np.asarray(outputs,dtype='f4').tobytes()).hexdigest(),
       'ideal_host_sampler_is_assumption':True,'half_2u_operation_allowance_is_assumption':True,'GPU_executed':False,'original_frame_context':False,'accepted_batches_repeated':False,'rows':rows}
    output.write_text(json.dumps(r,indent=2)+'\n')
    if r['set_allowance_violations']:raise AssertionError('Semantic host result outside declared allowance; receipt retained')
    return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('private_air',type=Path);p.add_argument('output',type=Path);a=p.parse_args();r=check(a.private_air,a.output)
    print(json.dumps({k:r[k]for k in ['records','RGB_values','bit_mismatches_half','max_absolute_error','set_allowance_violations']}))
