"""Extract original outer arithmetic; replace only BW477 by a supplied vector."""
import hashlib,re
from leaf_host import build as original_build,MATH_C


def build(source):
    main=re.search(r'^define[^\n]*@renderFinalAdjustments[^\n]+\{\n.*?^}',source,re.M|re.S)[0]
    original=re.search(r'^  %414 = .*?^  %492 = [^\n]+',main,re.M|re.S)[0]
    bw_line=next(x for x in original.splitlines()if x.startswith('  %477 ='))
    body=original.replace(bw_line+'\n','')
    external={'413':'rgb','398':'highlight','96':'person','385':'person_f','218':'parameter2','245':'cast_type','17':'params','477':'bw'}
    body=re.sub(r'%(\d+)',lambda m:'%'+external.get(m[1],'v'+m[1]),body)
    body=re.sub(r', !(?:tbaa|alias.scope|noalias) !\d+','',body);body=re.sub(r' #\d+','',body)
    trace=[]
    for i in range(3):trace += [f'%tonal_h{i}=extractelement <3 x half> %v468,i32 {i}',f'%tonal_f{i}=fpext half %tonal_h{i} to float',f'%tonal_p{i}=getelementptr [3 x float],ptr @psr_outer_tonal,i32 0,i32 {i}',f'store float %tonal_f{i},ptr %tonal_p{i}']
    line=next(x for x in body.splitlines()if x.startswith('  %v468 ='));body=body.replace(line,line+'\n'+'\n'.join(trace))
    helper='define fastcc <3 x half> @psrOuter(<3 x half> %rgb,<3 x half> %highlight,half %person,float %person_f,float %parameter2,i32 %cast_type,ptr addrspace(1) %params,<3 x half> %bw){\n'+body+'\nret <3 x half> %v492\n}'
    ir,functions=original_build(source,['psrOuter'],extra_functions=helper,emit_wrappers=False)
    wrapper=['define void @psr_outer(ptr %input,ptr %output){']
    for i in range(16):wrapper += [f'%p{i}=getelementptr float,ptr %input,i64 {i}',f'%f{i}=load float,ptr %p{i}']
    for base,name in [(0,'rgb'),(3,'hi'),(13,'bw')]:
        for i in range(3):wrapper += [f'%{name}h{i}=fptrunc float %f{base+i} to half',f'%{name}{i}=insertelement <3 x half> '+('poison'if i==0 else f'%{name}{i-1}')+f',half %{name}h{i},i32 {i}']
    wrapper += ['%person=fptrunc float %f6 to half','%person_f=fpext half %person to float','%cast=fptoui float %f12 to i32','%tuning=fptoui float %f11 to i32','%params=alloca %struct.SSRParams,align 16','store %struct.SSRParams zeroinitializer,ptr %params','%params1=addrspacecast ptr %params to ptr addrspace(1)']
    for path,value,ty in [('i32 17','%tuning','i32'),('i32 10,i32 65','%f8','float'),('i32 4','%f9','float'),('i32 5','%f10','float')]:
        index=len(wrapper);wrapper += [f'%q{index}=getelementptr %struct.SSRParams,ptr %params,i64 0,{path}',f'store {ty} {value},ptr %q{index}']
    wrapper += ['%r=call fastcc <3 x half> @psrOuter(<3 x half> %rgb2,<3 x half> %hi2,half %person,float %person_f,float %f7,i32 %cast,ptr addrspace(1) %params1,<3 x half> %bw2)']
    for i in range(3):wrapper += [f'%o{i}=extractelement <3 x half> %r,i32 {i}',f'%of{i}=fpext half %o{i} to float',f'%op{i}=getelementptr float,ptr %output,i64 {i}',f'store float %of{i},ptr %op{i}']
    wrapper += ['ret void','}']
    return '@psr_outer_tonal = global [3 x float] zeroinitializer\n'+ir+'\n'+'\n'.join(wrapper)+'\n',{'parent_main_sha256':hashlib.sha256(main.encode()).hexdigest(),'original_SSA414_492_sha256':hashlib.sha256(original.encode()).hexdigest(),'BW477_call_removed_sha256':hashlib.sha256(bw_line.encode()).hexdigest(),'external_SSA_mapping':external,'SSA477_is_explicit_input_not_algorithm_model':True,'metadata_and_call_attributes_removed':True,'additional_observation_stores':'SSA468 full RGB','other_arithmetic_or_predicates_changed':False,'included_function_text_sha256':functions}
