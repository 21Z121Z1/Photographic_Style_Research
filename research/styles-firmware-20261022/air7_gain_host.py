"""Compile original AIR7 SSA99..205; no original shader binary is exported."""
import hashlib,json,re
from pathlib import Path
from air_alpha import canonicalize
from leaf_host import shims,MATH_C


def build(source):
    expected=json.loads((Path(__file__).parent/'evidence/precomputed-links.json').read_text())['producer_canonical_sha256']
    if hashlib.sha256(canonicalize(source)[0].encode()).hexdigest()!=expected:raise ValueError('Exact matched AIR7 required')
    main=re.search(r'^define void @createLTMGainMap[^\n]+\{\n.*?^}',source,re.M|re.S)[0]
    original=re.search(r'^  %99 = .*?^  %205 = [^\n]+',main,re.M|re.S)[0]
    external={'8':'management','9':'params','4':'curve','96':'reference','98':'linear'}
    body=re.sub(r'%(\d+)',lambda m:'%'+external.get(m[1],'v'+m[1]),original)
    body=re.sub(r', !(?:tbaa|alias.scope|noalias) !\d+','',body);body=re.sub(r' #\d+','',body)
    helper='define void @psrGain(<3 x half> %reference,<4 x half> %linear,ptr addrspace(2) %management,ptr addrspace(1) %params,ptr addrspace(1) %curve,ptr %output){\n'+body
    for base,name in [(0,'v203'),(3,'v205'),(6,'v121')]:
        for i in range(3):helper+=f'\n%o{base+i}=extractelement <3 x half> %{name},i32 {i}\n%of{base+i}=fpext half %o{base+i} to float\n%op{base+i}=getelementptr float,ptr %output,i64 {base+i}\nstore float %of{base+i},ptr %op{base+i}'
    helper+='\nret void\n}'
    w=['define void @psr_gain(ptr %input,ptr %curve,ptr %output){']
    for i in range(23):w += [f'%p{i}=getelementptr float,ptr %input,i64 {i}',f'%f{i}=load float,ptr %p{i}']
    for base,name,n in [(0,'ref',3),(3,'linear',4)]:
        for i in range(n):w += [f'%{name}h{i}='+('fptrunc float %f'+str(base+i)+' to half'if i<3 else'fadd half 0xH0000,0xH0000'),f'%{name}{i}=insertelement <{n} x half> '+('poison'if i==0 else f'%{name}{i-1}')+f',half %{name}h{i},i32 {i}']
    w += ['%m=alloca %struct.SSRColorManagement.159,align 16','store %struct.SSRColorManagement.159 zeroinitializer,ptr %m','%m2=addrspacecast ptr %m to ptr addrspace(2)','%params=alloca %struct.SSRParams,align 16','store %struct.SSRParams zeroinitializer,ptr %params','%params1=addrspacecast ptr %params to ptr addrspace(1)','%curve1=addrspacecast ptr %curve to ptr addrspace(1)']
    for column in range(3):
        for row in range(3):
            i=column*3+row;w += [f'%mp{i}=getelementptr %struct.SSRColorManagement.159,ptr %m,i64 0,i32 1,i32 2,i32 0,i64 {column},i64 {row}',f'store float %f{6+i},ptr %mp{i}']
    w += ['%scale=getelementptr %struct.SSRParams,ptr %params,i64 0,i32 6','store float %f15,ptr %scale']
    for i in range(7):w += [f'%sp{i}=getelementptr %struct.SSRParams,ptr %params,i64 0,i32 15,i32 {i}',f'store float %f{16+i},ptr %sp{i}']
    w += ['call void @psrGain(<3 x half> %ref2,<4 x half> %linear3,ptr addrspace(2) %m2,ptr addrspace(1) %params1,ptr addrspace(1) %curve1,ptr %output)','ret void','}']
    types='\n'.join(re.findall(r'^%[^\n]+ = type [^\n]+',source,re.M));sampler=re.search(r'^@__air_sampler_state = [^\n]+',source,re.M)[0];used=set(re.findall(r'@(air\.[^ (]+)\(',helper))
    ir='\n'.join([types,sampler,helper,'\n'.join(w),shims(used)])+'\n'
    return ir,{'AIR7_canonical_sha256':expected,'main_function_sha256':hashlib.sha256(main.encode()).hexdigest(),'original_SSA99_205_sha256':hashlib.sha256(original.encode()).hexdigest(),'external_SSA_mapping':external,'arithmetic_or_sampler_calls_changed':False,'metadata_call_attributes_removed':True,'outputs':['BG203','FG205','working121'],'upstream_SRL_transfer_CCM0_and_2D_samples_included':False}
