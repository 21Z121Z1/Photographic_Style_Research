"""Complete original AIR7 kernel, actual source sampling and both write paths.

Only host intrinsic implementations and an ABI wrapper are added. Original
function text/FP attributes and constant flags' original loads are preserved.
"""
import hashlib,json,re
from pathlib import Path
from air_alpha import canonicalize
from guided_host import shims as texture_shims,C_SOURCE as TEXTURE_C
from leaf_host import shims as math_shims,MATH_C

C_SOURCE=MATH_C+'\n'+TEXTURE_C+r'''
float psr_fullsample(void*raw,uint64_t sampler,float u,float v,int lane){
 if(sampler!=34901797601053257ULL)return psr_gsample(raw,sampler,u,v,lane);
 uint32_t*h=raw;float*a=(float*)(h+4);if(lane!=0)return lane==3?1.f:0.f;
 float q=fminf(fmaxf(u-.5f,0),h[0]-1);uint32_t i=(uint32_t)floorf(q),j=i+1<h[0]?i+1:i;
 return a[i*h[2]]+(a[j*h[2]]-a[i*h[2]])*(q-i);
}
'''


def sample_shim():
    s=['declare float @psr_fullsample(ptr,i64,float,float,i32)','define internal {<4 x half>,i8} @air.sample_texture_2d.v4f16(ptr addrspace(1) %p,ptr addrspace(2) %s,<2 x float> %xy,i1 %a,<2 x i32> %o,i1 %b,float %c,float %d,i32 %e){','%ptr=addrspacecast ptr addrspace(1) %p to ptr','%bits=load i64,ptr addrspace(2) %s','%u=extractelement <2 x float> %xy,i32 0','%v=extractelement <2 x float> %xy,i32 1']
    for i in range(4):s += [f'%f{i}=call float @psr_fullsample(ptr %ptr,i64 %bits,float %u,float %v,i32 {i})',f'%h{i}=fptrunc float %f{i} to half',f'%r{i}=insertelement <4 x half> '+('poison'if i==0 else f'%r{i-1}')+f',half %h{i},i32 {i}']
    s += ['%r=insertvalue {<4 x half>,i8} zeroinitializer,<4 x half> %r3,0','ret {<4 x half>,i8} %r','}'];return '\n'.join(s)


def direct_write_shim():
    s=['define internal void @air.write_texture_2d.i16.v4f16(ptr addrspace(1) %p,<2 x i16> %xy,<4 x half> %v,i16 %a,i32 %b){','%ptr=addrspacecast ptr addrspace(1) %p to ptr','%x=extractelement <2 x i16> %xy,i32 0','%y=extractelement <2 x i16> %xy,i32 1']
    for i in range(4):s += [f'%h{i}=extractelement <4 x half> %v,i32 {i}',f'%f{i}=fpext half %h{i} to float',f'call void @psr_gwrite(ptr %ptr,i16 %x,i16 %y,i32 {i},float %f{i})']
    return '\n'.join([*s,'ret void','}'])


def build(source,*,observe=False):
    expected=json.loads((Path(__file__).parent/'evidence/precomputed-links.json').read_text())['producer_canonical_sha256']
    if hashlib.sha256(canonicalize(source)[0].encode()).hexdigest()!=expected:raise ValueError('Exact AIR7 required')
    functions={m[1]:m[0]for m in re.finditer(r'^define[^\n]*@([^ (]+)\([^\n]+\{\n.*?^}',source,re.M|re.S)};selected={'createLTMGainMap'};pending=list(selected)
    while pending:
        for n in re.findall(r'@(_Z[^ (]+)\(',functions[pending.pop()]):
            if n not in selected:selected.add(n);pending.append(n)
    bodies=[functions[n]for n in sorted(selected)]
    if observe:
        root=bodies.index(functions['createLTMGainMap']);body=bodies[root]
        for offset,ssa in enumerate([24,34,37,96,121,203,205]):
            line=next(x for x in body.splitlines()if x.startswith(f'  %{ssa} ='));trace=[]
            for lane in range(3):
                i=offset*3+lane;trace += [f'%obs_h{i}=extractelement <3 x half> %{ssa},i32 {lane}',f'%obs_f{i}=fpext half %obs_h{i} to float',f'%obs_p{i}=getelementptr [21 x float],ptr @psr_producer_trace,i32 0,i32 {i}',f'store float %obs_f{i},ptr %obs_p{i}']
            body=body.replace(line,line+'\n'+'\n'.join(trace))
        bodies[root]=body
    used=set(re.findall(r'@(air\.[^ (]+)\(','\n'.join(bodies)));base=texture_shims()+'\n'+sample_shim()+'\n'+direct_write_shim();defined=set(re.findall(r'^define[^\n]*@([^ (]+)\(',base,re.M))
    defs=dict(re.findall(r'^!(\d+) = (.*)$',source,re.M));ids=set(re.findall(r'!(\d+)','\n'.join(bodies)));pending=list(ids)
    while pending:
        for n in re.findall(r'!(\d+)',defs[pending.pop()]):
            if n not in ids:ids.add(n);pending.append(n)
    attrs=set(re.findall(r'#(\d+)','\n'.join(bodies)));types=re.findall(r'^%[^\n]+ = type [^\n]+',source,re.M);image_type=re.search(r'^(%[^\n]+) = type \{ ptr addrspace\(4\) \}',source,re.M)[1]
    globals_=re.findall(r'^@__air_sampler_state[^\n]+',source,re.M)+['@_ZL17useSrlBeforeStats = internal addrspace(2) global i8 0','@_ZL13useImageBlock = internal addrspace(2) global i8 0']
    w=['define void @psr_produce(ptr %primary,ptr %linear,ptr %curve,ptr %matte,ptr %bg,ptr %fg,ptr %management,ptr %params,ptr %srl,i8 %use_srl,i8 %imageblock,i16 %x,i16 %y){']
    for n in ['primary','linear','curve','matte','bg','fg','params']:w += [f'%{n}1=addrspacecast ptr %{n} to ptr addrspace(1)']
    for n in ['management','srl']:w += [f'%{n}2=addrspacecast ptr %{n} to ptr addrspace(2)']
    w += ['store i8 %use_srl,ptr addrspace(2) @_ZL17useSrlBeforeStats','store i8 %imageblock,ptr addrspace(2) @_ZL13useImageBlock','%xy0=insertelement <2 x i16> poison,i16 %x,i32 0','%xy=insertelement <2 x i16> %xy0,i16 %y,i32 1',f'call void @createLTMGainMap({image_type} zeroinitializer,ptr addrspace(1) %primary1,ptr addrspace(2) %srl2,ptr addrspace(1) %linear1,ptr addrspace(1) %curve1,ptr addrspace(1) %matte1,ptr addrspace(1) %bg1,ptr addrspace(1) %fg1,ptr addrspace(2) %management2,ptr addrspace(1) %params1,<2 x i16> %xy,<2 x i16> zeroinitializer)','ret void','}']
    math=re.sub(r'^define ', 'define internal ',math_shims(used-defined),flags=re.M)
    ir='\n'.join([*types,*globals_,*(['@psr_producer_trace = global [21 x float] zeroinitializer']if observe else[]),*bodies,base,math,'\n'.join(w),*[re.search(r'^attributes #'+n+r' = .*$',source,re.M)[0]for n in attrs],*[f'!{n} = {defs[n]}'for n in sorted(ids,key=int)]])+'\n'
    return ir,{'canonical_sha256':expected,'original_functions_sha256':{n:hashlib.sha256(functions[n].encode()).hexdigest()for n in sorted(selected)},'original_functions_modified':'observation stores in root only'if observe else False,'observed_SSA':[24,34,37,96,121,203,205]if observe else[],'original_arithmetic_predicates_and_FP_attributes_changed':False,'source_sampling_and_original_write_paths_included':True,'host_imageblock_threads':1,'normalized_sampler':'v3 quantized-linear half, CPU assumption','GTC_pixel_sampler':'existing ideal pixel-linear CPU assumption','specialization_flags':'original global loads, supplied exact i8 values set by wrapper'}
