"""Reconnect original BW477 call to full BW root; share identical IR units."""
import hashlib,re
from outer_cast_host import build as outer_build,MATH_C
from bw_host import build as bw_build


def units(ir):
    lines=ir.splitlines();result={};i=0
    while i<len(lines):
        line=lines[i]
        if not line.strip():i+=1;continue
        if line.startswith('define '):
            end=i+1
            while lines[end]!='}':end+=1
            body='\n'.join(lines[i:end+1]);key='function:'+re.search(r'@([^ (]+)',line)[1];i=end+1
        else:
            body=line;key='function:'+re.search(r'@([^ (]+)',line)[1]if line.startswith('declare ')else line.split(' = ')[0]if' = 'in line else line;i+=1
        if key in result and result[key]!=body:raise ValueError('Conflicting module unit '+key)
        result[key]=body
    return result


def build(source):
    outer,metadata=outer_build(source);bw,functions=bw_build(source);a=units(outer);b=units(bw)
    del a['function:psr_outer'];del b['function:psr_leaf_0']
    root=a['function:psrOuter'];old='<3 x half> %bw)'
    if root.count(old)!=1:raise ValueError('Exact conditional root signature required')
    root=root.replace(old,'half %guide,ptr addrspace(1) %whites)',1)
    line=next(x for x in source.splitlines()if x.startswith('  %477 ='))
    mapping={'477':'bw','350':'guide','96':'person','4':'whites','472':'v472','17':'params'}
    call=re.sub(r'%(\d+)',lambda m:'%'+mapping[m[1]],line);call=re.sub(r' #\d+','',call)
    insert=next(x for x in root.splitlines()if x.startswith('  %v478 ='));root=root.replace(insert,call+'\n'+insert)
    a['function:psrOuter']=root
    for key,value in b.items():
        if key in a and a[key]!=value:raise ValueError('Original/shared helper conflict '+key)
        a[key]=value
    w=['define void @psr_outer_bw(ptr %input,ptr %whites,ptr %output){']
    for i in range(16):w += [f'%p{i}=getelementptr float,ptr %input,i64 {i}',f'%f{i}=load float,ptr %p{i}']
    for base,name in [(0,'rgb'),(3,'hi')]:
        for i in range(3):w += [f'%{name}h{i}=fptrunc float %f{base+i} to half',f'%{name}{i}=insertelement <3 x half> '+('poison'if i==0 else f'%{name}{i-1}')+f',half %{name}h{i},i32 {i}']
    w += ['%person=fptrunc float %f6 to half','%person_f=fpext half %person to float','%guide=fptrunc float %f13 to half','%cast245=fptoui float %f12 to i32','%cast0=fptoui float %f14 to i32','%tuning=fptoui float %f11 to i32','%params=alloca %struct.SSRParams,align 16','store %struct.SSRParams zeroinitializer,ptr %params','%params1=addrspacecast ptr %params to ptr addrspace(1)','%whites1=addrspacecast ptr %whites to ptr addrspace(1)']
    for i,(path,value,ty)in enumerate([('i32 0','%cast0','i32'),('i32 17','%tuning','i32'),('i32 2','%f7','float'),('i32 10,i32 20','%f15','float'),('i32 10,i32 65','%f8','float'),('i32 4','%f9','float'),('i32 5','%f10','float')]):w += [f'%q{i}=getelementptr %struct.SSRParams,ptr %params,i64 0,{path}',f'store {ty} {value},ptr %q{i}']
    w += ['%r=call fastcc <3 x half> @psrOuter(<3 x half> %rgb2,<3 x half> %hi2,half %person,float %person_f,float %f7,i32 %cast245,ptr addrspace(1) %params1,half %guide,ptr addrspace(1) %whites1)']
    for i in range(3):w += [f'%o{i}=extractelement <3 x half> %r,i32 {i}',f'%of{i}=fpext half %o{i} to float',f'%op{i}=getelementptr float,ptr %output,i64 {i}',f'store float %of{i},ptr %op{i}']
    w += ['ret void','}'];ir='\n'.join(a.values())+'\n'+'\n'.join(w)+'\n'
    metadata.update(SSA477_is_explicit_input_not_algorithm_model=False,original_BW477_call_restored=True,restored_call_text_sha256=hashlib.sha256(call.encode()).hexdigest(),original_BW_functions_sha256=functions,internal_observations=['outer tonal468','BW stark12','BW tonal67'])
    return ir,metadata
