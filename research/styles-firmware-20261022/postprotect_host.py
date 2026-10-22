"""Original main SSA502..566 control flow, explicit original upstream inputs."""
import hashlib,re
from leaf_host import build as original_build,MATH_C


def build(source,names=None):
    main=re.search(r'^define[^\n]*@renderFinalAdjustments[^\n]+\{\n.*?^}',source,re.M|re.S)[0]
    original=re.search(r'^  %502 = .*?^  %566 = [^\n]+',main,re.M|re.S)[0]
    external={'501':'rgb','476':'color','17':'params','18':'stats','51':'is_null'}
    body=re.sub(r'%(\d+)',lambda m:'%'+external.get(m[1],'v'+m[1]),original)
    body=re.sub(r'^(\d+):',lambda m:'v'+m[1]+':',body,flags=re.M)
    body=re.sub(r', !(?:tbaa|alias.scope|noalias) !\d+','',body);body=re.sub(r' #\d+','',body)
    helper='define fastcc <3 x half> @psrPostProtect(<3 x half> %rgb,<3 x half> %color,ptr addrspace(1) %params,ptr addrspace(1) %stats,i1 %is_null){\nv382:\n'+body+'\nret <3 x half> %v566\n}'
    ir,functions=original_build(source,['psrPostProtect'],extra_functions=helper,emit_wrappers=False)
    w=['define void @psr_leaf_0(ptr %input,ptr %texture,ptr %output){']
    for i in range(12):w += [f'%p{i}=getelementptr float,ptr %input,i64 {i}',f'%f{i}=load float,ptr %p{i}']
    for base,name in [(0,'rgb'),(3,'color')]:
        for i in range(3):w += [f'%{name}h{i}=fptrunc float %f{base+i} to half',f'%{name}{i}=insertelement <3 x half> '+('poison'if i==0 else f'%{name}{i-1}')+f',half %{name}h{i},i32 {i}']
    w += ['%is_null=fcmp oeq float %f6,0.0','%params=alloca %struct.SSRParams,align 16','store %struct.SSRParams zeroinitializer,ptr %params','%params1=addrspacecast ptr %params to ptr addrspace(1)','%stats=alloca %struct.SSRStats,align 4','store %struct.SSRStats zeroinitializer,ptr %stats','%stats1=addrspacecast ptr %stats to ptr addrspace(1)']
    for i in range(2):w += [f'%cp{i}=getelementptr %struct.SSRParams,ptr %params,i64 0,i32 9,i32 {19+i}',f'store float %f{7+i},ptr %cp{i}']
    for i in range(3):w += [f'%sp{i}=getelementptr %struct.SSRStats,ptr %stats,i64 0,i32 1,i64 {2+i},i32 4',f'store float %f{9+i},ptr %sp{i}']
    w += ['%r=call fastcc <3 x half> @psrPostProtect(<3 x half> %rgb2,<3 x half> %color2,ptr addrspace(1) %params1,ptr addrspace(1) %stats1,i1 %is_null)']
    for i in range(3):w += [f'%o{i}=extractelement <3 x half> %r,i32 {i}',f'%of{i}=fpext half %o{i} to float',f'%op{i}=getelementptr float,ptr %output,i64 {i}',f'store float %of{i},ptr %op{i}']
    w += ['ret void','}']
    return ir+'\n'+'\n'.join(w)+'\n',{'parent_main_sha256':hashlib.sha256(main.encode()).hexdigest(),'original_SSA502_566_sha256':hashlib.sha256(original.encode()).hexdigest(),'external_SSA_mapping':external,'entry_predecessor_preserved':'382','metadata_and_call_attributes_removed':True,'arithmetic_and_control_flow_changed':False,'included_function_text_sha256':functions}
