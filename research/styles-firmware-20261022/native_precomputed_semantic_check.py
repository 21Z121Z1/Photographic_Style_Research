"""New block290 arithmetic/sampling only, SSA-alpha-renamed for host wrapping.

Original opcodes/constants/metadata are retained. A normalized CPU bilinear
clamp sampler is explicit; no original GPU, guided-filter producer or photo.
"""
import argparse,ctypes,hashlib,json,re,subprocess,tempfile
from pathlib import Path
import numpy as np
from native_semantic_tone_check import fragment,SHIM_IR
from precomputed_semantic import Texture2D,PrecomputedInputs,forward_half,forward_set

SAMPLER_C=r'''
#include <stdint.h>
#include <math.h>
float psr_sample2d(const void *p,float u,float v,int channel){
 const uint32_t *n=p;const float *a=(const float*)((const char*)p+8);uint32_t w=n[0],h=n[1];
 float x=fminf(fmaxf(u*w-.5f,0),w-1),y=fminf(fmaxf(v*h-.5f,0),h-1);
 uint32_t i=(uint32_t)floorf(x),j=(uint32_t)floorf(y),ii=i+1<w?i+1:i,jj=j+1<h?j+1:j;
 float fx=x-i,fy=y-j,t=a[(j*w+i)*3+channel],b=a[(jj*w+i)*3+channel];
 t=t+(a[(j*w+ii)*3+channel]-t)*fx;b=b+(a[(jj*w+ii)*3+channel]-b)*fx;return t+(b-t)*fy;
}
'''


def build(source):
    fragment(source)  # SHA only, never executes the accepted helper batch.
    start=source.index('  %291 =');end=source.index('  br label %344',start);original=source[start:end]
    body=re.sub(r'%(\d+)',lambda m:'%v'+m[1],original)
    helper='define <3 x half> @psr_block(ptr addrspace(1) %v6,ptr addrspace(1) %v7,ptr addrspace(2) %v19,<2 x float> %v29,ptr addrspace(1) %v17,ptr addrspace(1) %v246,<3 x half> %v196,half %v96,float %v251,float %v255){\n'+body+'ret <3 x half> %v335\n}'
    # Keep only metadata/attribute closure reached by the original block.
    defs=dict(re.findall(r'^!(\d+) = (.*)$',source,re.M));ids=set(re.findall(r'!(\d+)',body));pending=list(ids)
    while pending:
        for n in re.findall(r'!(\d+)',defs[pending.pop()]):
            if n not in ids:ids.add(n);pending.append(n)
    attrs=set(re.findall(r'#(\d+)',body));types=re.findall(r'^%[^\n]+ = type [^\n]+$',source,re.M)
    sampler=re.search(r'^@__air_sampler_state\.3 = .*$',source,re.M)[0]
    shim=['declare float @psr_sample2d(ptr,float,float,i32)','define { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) %p,ptr addrspace(2) %s,<2 x float> %xy,i1 %a,<2 x i32> %off,i1 %b,float %c,float %d,i32 %e){','%u=extractelement <2 x float> %xy,i32 0','%v=extractelement <2 x float> %xy,i32 1','%t=addrspacecast ptr addrspace(1) %p to ptr']
    for n in range(3):shim += [f'%f{n}=call float @psr_sample2d(ptr %t,float %u,float %v,i32 {n})',f'%h{n}=fptrunc float %f{n} to half',f'%x{n}=insertelement <4 x half> '+('zeroinitializer'if n==0 else f'%x{n-1}')+f',half %h{n},i32 {n}']
    shim += ['%r=insertvalue {<4 x half>,i8} zeroinitializer,<4 x half> %x2,0','ret {<4 x half>,i8} %r','}']
    wrapper=['define void @psr_precomputed(ptr %input,ptr %params,ptr %roi,ptr %t6,ptr %t7,ptr %output){']
    # input = centered grid floats [0:2], reference [2:5], person[5].
    for n in range(6):wrapper += [f'%p{n}=getelementptr float,ptr %input,i64 {n}',f'%f{n}=load float,ptr %p{n}']
    wrapper += ['%xy0=insertelement <2 x float> poison,float %f0,i32 0','%xy=insertelement <2 x float> %xy0,float %f1,i32 1']
    for n in range(2,6):wrapper += [f'%h{n}=fptrunc float %f{n} to half']
    wrapper += ['%r0=insertelement <3 x half> poison,half %h2,i32 0','%r1=insertelement <3 x half> %r0,half %h3,i32 1','%rgb=insertelement <3 x half> %r1,half %h4,i32 2','%pp=addrspacecast ptr %params to ptr addrspace(1)','%rp=addrspacecast ptr %roi to ptr addrspace(2)','%s6=addrspacecast ptr %t6 to ptr addrspace(1)','%s7=addrspacecast ptr %t7 to ptr addrspace(1)','%sp=getelementptr i8,ptr addrspace(1) %pp,i64 620','%hp=getelementptr float,ptr addrspace(1) %sp,i64 5','%hr=load float,ptr addrspace(1) %hp','%fp=getelementptr float,ptr addrspace(1) %sp,i64 6','%fhr=load float,ptr addrspace(1) %fp','%out=call <3 x half> @psr_block(ptr addrspace(1) %s6,ptr addrspace(1) %s7,ptr addrspace(2) %rp,<2 x float> %xy,ptr addrspace(1) %pp,ptr addrspace(1) %sp,<3 x half> %rgb,half %h5,float %hr,float %fhr)']
    for n in range(3):wrapper += [f'%o{n}=extractelement <3 x half> %out,i32 {n}',f'%of{n}=fpext half %o{n} to float',f'%op{n}=getelementptr float,ptr %output,i64 {n}',f'store float %of{n},ptr %op{n}']
    wrapper += ['ret void','}']
    ir='\n'.join([*types,sampler,helper,SHIM_IR.split('declare float @psr_sample')[0],'\n'.join(shim),'\n'.join(wrapper),*[re.search(r'^attributes #'+n+r' = .*$',source,re.M)[0]for n in attrs],*[f'!{n} = {defs[n]}'for n in sorted(ids,key=int)]])+'\n'
    return ir,hashlib.sha256(original.encode()).hexdigest()


def check(source: Path,output: Path):
    if output.exists():raise FileExistsError(output)
    ir,original_sha=build(source.read_text());rng=np.random.default_rng(0x290);cases=[]
    for size in [(1,1),(2,3),(5,4)]:
        h,w=size;tex6=Texture2D(rng.uniform(.4,1.6,size=(h,w,3)),'supplied BG/FG gain working domain');tex7=Texture2D(rng.uniform(.4,1.6,size=(h,w,3)),'supplied BG/FG gain working domain')
        for grid in [(0,0),(1,2),(7,5)]:
            for weight in [0.,.3,1.]:
                roi=(1/w,1/h,0,0);roi7=(1/w,1/h,-.15,.1)
                cases.append((PrecomputedInputs(grid,tex6,tex7,roi,roi7,(.25,.5,.75),weight),np.array([.6,.8,1,1,1,.5,.9],dtype='f4')))
    rows=[];input_hash=hashlib.sha256();outputs=[]
    with tempfile.TemporaryDirectory(prefix='psr-precomputed-')as t:
        d=Path(t);(d/'block.ll').write_text(ir);(d/'sampler.c').write_text(SAMPLER_C);libpath=d/'block.dylib'
        c=subprocess.run(['/opt/homebrew/opt/llvm/bin/clang','-target','arm64-apple-macos27.0','-Wno-override-module','-dynamiclib',str(d/'block.ll'),str(d/'sampler.c'),'-o',str(libpath)],capture_output=True,text=True,timeout=60)
        if c.returncode:raise RuntimeError(c.stderr[:5000])
        lib=ctypes.CDLL(str(libpath));fn=lib.psr_precomputed;fn.argtypes=[ctypes.c_void_p]*6
        for index,(inp,values)in enumerate(cases):
            data=np.r_[np.array(inp.grid,dtype='f4')+.5,np.array(inp.reference_rgb,dtype='f2').astype('f4'),np.float16(inp.person_weight)].astype('f4');params=np.zeros(168,dtype='f4');params[155:162]=values
            # Actual SSRRenderROI schema: field5 byte48, field6 byte64.
            # The first three ushort2 fields occupy 12B, then float4 alignment.
            roi=np.zeros(44,dtype='f4');roi[12:16]=inp.roi_field5;roi[16:20]=inp.roi_field6
            textures=[]
            for texture in [inp.texture6,inp.texture7]:
                h,w,_=texture.values.shape;textures.append(np.r_[np.array([w,h],dtype='u4').view('f4'),texture.values.astype('f4').ravel()])
            out=np.zeros(3,dtype='f4');args=[data,params,roi,*textures,out];input_hash.update(b''.join(x.tobytes()for x in args[:-1]));fn(*(x.ctypes.data for x in args))
            point=forward_half(inp,values);bounds=forward_set(inp,values,values);outputs.append(out.copy())
            rows.append({'index':index,'shape':list(inp.texture6.values.shape),'grid':list(inp.grid),'person':inp.person_weight,'half_bit_mismatches':int(np.count_nonzero(out.astype('f2').view('u2')!=point.view('u2'))),'max_absolute_error':float(np.max(abs(out.astype('f8')-point))),'range_covered':bool(np.all(out>=bounds.lower)and np.all(out<=bounds.upper))})
    r={'scope':__doc__,'original_block_text_sha256':original_sha,'original_SSA_only_alpha_renamed':True,'records':len(rows),'RGB_values':3*len(rows),'half_bit_mismatches':sum(x['half_bit_mismatches']for x in rows),'max_absolute_error':max(x['max_absolute_error']for x in rows),'range_violations':sum(not x['range_covered']for x in rows),'input_sha256':input_hash.hexdigest(),'native_output_sha256':hashlib.sha256(np.asarray(outputs,dtype='f4').tobytes()).hexdigest(),'model_sha256':hashlib.sha256((Path(__file__).parent/'precomputed_semantic.py').read_bytes()).hexdigest(),'checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'GPU_executed':False,'guided_filter_producer_executed':False,'fallback_or_mids_batch_repeated':False,'rows':rows}
    output.write_text(json.dumps(r,indent=2)+'\n')
    if r['range_violations']:raise AssertionError('Precomputed branch outside explicit set allowance; receipt retained')
    return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('output',type=Path);a=p.parse_args();r=check(a.source,a.output);print(json.dumps({k:r[k]for k in ['records','RGB_values','half_bit_mismatches','max_absolute_error','range_violations']}))
