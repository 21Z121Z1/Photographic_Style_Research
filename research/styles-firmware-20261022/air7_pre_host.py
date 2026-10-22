"""Original AIR7 preprocessing, replacing only explicit sampled inputs/FC load."""
import hashlib,json,re
from pathlib import Path
from air_alpha import canonicalize
from leaf_host import shims,MATH_C


def build(source):
    expected=json.loads((Path(__file__).parent/'evidence/precomputed-links.json').read_text())['producer_canonical_sha256']
    if hashlib.sha256(canonicalize(source)[0].encode()).hexdigest()!=expected:raise ValueError('Matched AIR7 required')
    main=re.search(r'^define void @createLTMGainMap[^\n]+\{\n.*?^}',source,re.M|re.S)[0];original=re.search(r'^  %25 = .*?^  %96 = [^\n]+',main,re.M|re.S)[0]
    removed=re.search(r'^  %28 = .*?^  %30 = [^\n]+\n',original,re.M|re.S)[0]
    first=original.splitlines()[0];body=original.replace(removed,'').replace(first,'  %25 = zext i1 %use_srl to i8')
    external={'24':'rgb','30':'matte','2':'srl','8':'management'}
    body=re.sub(r'%(\d+)',lambda m:'%'+external.get(m[1],'v'+m[1]),body);body=re.sub(r'^(\d+):',lambda m:'v'+m[1]+':',body,flags=re.M);body=re.sub(r', !(?:tbaa|alias.scope|noalias|range) !\d+','',body);body=re.sub(r' #\d+','',body)
    helper='define void @psrPre(<3 x half> %rgb,half %matte,ptr addrspace(2) %srl,ptr addrspace(2) %management,i1 %use_srl,ptr %output){\nv12:\n'+body
    for base,name in [(0,'v96'),(3,'v37'),(6,'v34')]:
        for i in range(3):helper+=f'\n%o{base+i}=extractelement <3 x half> %{name},i32 {i}\n%of{base+i}=fpext half %o{base+i} to float\n%op{base+i}=getelementptr float,ptr %output,i64 {base+i}\nstore float %of{base+i},ptr %op{base+i}'
    helper+='\nret void\n}'
    definitions={m[1]:m[0]for m in re.finditer(r'^define[^\n]*@([^ (]+)\([^\n]+\{\n.*?^}',source,re.M|re.S)};pending=re.findall(r'@(_Z[^ (]+)\(',helper);selected=set()
    while pending:
        n=pending.pop()
        if n in selected:continue
        selected.add(n);pending+=re.findall(r'@(_Z[^ (]+)\(',definitions[n])
    functions=[definitions[n]for n in sorted(selected)];used=set(re.findall(r'@(air\.[^ (]+)\(','\n'.join([helper,*functions])));attrs=set(re.findall(r'#(\d+)','\n'.join(functions)));attribute_lines=[re.search(r'^attributes #'+n+r' = .*$',source,re.M)[0]for n in attrs]
    w=['define void @psr_gain(ptr %input,ptr %unused,ptr %output){']
    for i in range(17):w += [f'%p{i}=getelementptr float,ptr %input,i64 {i}',f'%f{i}=load float,ptr %p{i}']
    for i in range(3):w += [f'%h{i}=fptrunc float %f{i} to half',f'%v{i}=insertelement <3 x half> '+('poison'if i==0 else f'%v{i-1}')+f',half %h{i},i32 {i}']
    w += ['%matte=fptrunc float %f3 to half','%srl2=addrspacecast ptr %p4 to ptr addrspace(2)','%use=fcmp une float %f5,0.0','%code=fptoui float %f6 to i32','%mode=fcmp une float %f16,0.0','%mode8=zext i1 %mode to i8','%m=alloca %struct.SSRColorManagement.159,align 16','store %struct.SSRColorManagement.159 zeroinitializer,ptr %m','%m2=addrspacecast ptr %m to ptr addrspace(2)','%cp=getelementptr %struct.SSRColorManagement.159,ptr %m,i64 0,i32 0,i32 0','store i32 %code,ptr %cp','%modeptr=getelementptr %struct.SSRColorManagement.159,ptr %m,i64 0,i32 0,i32 3','store i8 %mode8,ptr %modeptr']
    for col in range(3):
        for row in range(3):
            i=col*3+row;w += [f'%mp{i}=getelementptr %struct.SSRColorManagement.159,ptr %m,i64 0,i32 0,i32 2,i32 0,i64 {col},i64 {row}',f'store float %f{7+i},ptr %mp{i}']
    w += ['call void @psrPre(<3 x half> %v2,half %matte,ptr addrspace(2) %srl2,ptr addrspace(2) %m2,i1 %use,ptr %output)','ret void','}'];types='\n'.join(re.findall(r'^%[^\n]+ = type [^\n]+',source,re.M));ir='\n'.join([types,helper,*functions,shims(used),'\n'.join(w),*attribute_lines])+'\n'
    return ir,{'AIR7_canonical_sha256':expected,'original_main_sha256':hashlib.sha256(main.encode()).hexdigest(),'original_SSA25_96_sha256':hashlib.sha256(original.encode()).hexdigest(),'removed_matte_sample28_30_sha256':hashlib.sha256(removed.encode()).hexdigest(),'function_constant_load25_replaced_by':'zext supplied exact bool to i8','external_SSA_mapping':external,'other_arithmetic_predicates_unchanged':True,'original_helpers_sha256':{n:hashlib.sha256(definitions[n].encode()).hexdigest()for n in selected},'observations':['reference96','linear37','postSRL34'],'2D_sampling_included':False}
