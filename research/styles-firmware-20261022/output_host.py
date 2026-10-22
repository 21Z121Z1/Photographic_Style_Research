"""Original main568..600 with supplied RGB/gain/CCM and exact two enums."""
import hashlib,re
from leaf_host import build as original_build,MATH_C


def build(source):
    main=re.search(r'^define[^\n]*@renderFinalAdjustments[^\n]+\{\n.*?^}',source,re.M|re.S)[0]
    original=re.search(r'^568:.*?^  %600 = [^\n]+',main,re.M|re.S)[0]
    external={'138':'is_code6','218':'parameter2','176':'reference_gain','16':'management','567':'rgb'}
    body=re.sub(r'%(\d+)',lambda m:'%'+external.get(m[1],'v'+m[1]),original);body=re.sub(r'^(\d+):',lambda m:'v'+m[1]+':',body,flags=re.M)
    body=re.sub(r', !(?:tbaa|alias.scope|noalias) !\d+','',body);body=re.sub(r' #\d+','',body)
    helper='define void @psrOutput(<3 x half> %rgb,half %reference_gain,float %parameter2,i1 %is_code6,ptr addrspace(2) %management,ptr %output){\nv565:\nbr i1 %is_code6,label %v568,label %v575\n'+body
    for base,name in [(0,'v600'),(3,'v597')]:
        for i in range(3):helper+=f'\n%o{base+i}=extractelement <3 x half> %{name},i32 {i}\n%of{base+i}=fpext half %o{base+i} to float\n%op{base+i}=getelementptr float,ptr %output,i64 {base+i}\nstore float %of{base+i},ptr %op{base+i}'
    helper+='\n%gf=fpext half %v577 to float\n%gp=getelementptr float,ptr %output,i64 6\nstore float %gf,ptr %gp\nret void\n}'
    ir,functions=original_build(source,['psrOutput'],extra_functions=helper,emit_wrappers=False)
    w=['define void @psr_output(ptr %input,ptr %output){']
    for i in range(16):w += [f'%p{i}=getelementptr float,ptr %input,i64 {i}',f'%f{i}=load float,ptr %p{i}']
    for i in range(3):w += [f'%h{i}=fptrunc float %f{i} to half',f'%v{i}=insertelement <3 x half> '+('poison'if i==0 else f'%v{i-1}')+f',half %h{i},i32 {i}']
    w += ['%gain=fptrunc float %f3 to half','%input_code=fptoui float %f5 to i32','%is6=icmp eq i32 %input_code,6','%outcode=fptoui float %f15 to i32','%m=alloca %struct.SSRColorManagement.159,align 16','store %struct.SSRColorManagement.159 zeroinitializer,ptr %m','%m2=addrspacecast ptr %m to ptr addrspace(2)']
    for col in range(3):
        for row in range(3):
            i=3*col+row;w += [f'%mp{i}=getelementptr %struct.SSRColorManagement.159,ptr %m,i64 0,i32 3,i32 2,i32 0,i64 {col},i64 {row}',f'store float %f{6+i},ptr %mp{i}']
    w += ['%codeptr=getelementptr %struct.SSRColorManagement.159,ptr %m,i64 0,i32 3,i32 0','store i32 %outcode,ptr %codeptr','call void @psrOutput(<3 x half> %v2,half %gain,float %f4,i1 %is6,ptr addrspace(2) %m2,ptr %output)','ret void','}']
    return ir+'\n'+'\n'.join(w)+'\n',{'parent_main_sha256':hashlib.sha256(main.encode()).hexdigest(),'original_SSA568_600_sha256':hashlib.sha256(original.encode()).hexdigest(),'external_SSA_mapping':external,'arithmetic_or_control_flow_changed':False,'metadata_and_call_attributes_removed':True,'included_function_text_sha256':functions,'independent_observations':['output600','linear597','gain577']}
