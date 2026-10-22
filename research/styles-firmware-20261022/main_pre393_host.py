"""Original main entry through392 plus original recursive helpers, with probes."""
import hashlib,re
from native_semantic_tone_check import fragment
from leaf_host import shims as math_shims
from guided_host import shims as texture_shims
from air7_full_host import sample_shim,C_SOURCE

OBSERVATIONS=[('source38',38,3),('skin95',95,1),('person96',96,1),('SRL134',134,3),('linear137',137,3),('gain176',176,1),('reference196',196,3),('guide211',211,1),('guide214',214,1),('working286',286,3),('semantic347',347,3),('guide350',350,1),('BG352',352,3),('FG354',354,3),('saturated374',374,3),('color_mix389',389,1),('output392',392,3)]


def build(source):
    fragment(source);functions={m[1]:m[0]for m in re.finditer(r'^define[^\n]*@([^ (]+)\([^\n]+\{\n.*?^}',source,re.M|re.S)};main=functions['renderFinalAdjustments'];prefix=main[:main.index('  %393 =')];header=prefix.splitlines()[0];header=header.replace('@renderFinalAdjustments','@psrMainPre');end=header.rfind(')');header=header[:end]+',ptr %observations'+header[end:];body=header+'\n'+prefix.split('\n',1)[1];offset=0
    for name,ssa,n in OBSERVATIONS:
        for i in range(n):
            j=offset+i
            if n==3:body+=f'\n%obs_h{j}=extractelement <3 x half> %{ssa},i32 {i}'
            value=f'%obs_h{j}'if n==3 else f'%{ssa}'
            body+=f'\n%obs_f{j}=fpext half {value} to float\n%obs_p{j}=getelementptr float,ptr %observations,i64 {j}\nstore float %obs_f{j},ptr %obs_p{j}'
        offset+=n
    body+='\nret void\n}';selected=set();pending=re.findall(r'@(_Z[^ (]+)\(',body)
    while pending:
        n=pending.pop()
        if n in selected:continue
        selected.add(n);pending+=re.findall(r'@(_Z[^ (]+)\(',functions[n])
    helpers=[functions[n]for n in sorted(selected)];bodies=[body,*helpers];used=set(re.findall(r'@(air\.[^ (]+)\(','\n'.join(bodies)));base=texture_shims()+'\n'+sample_shim()+'\ndefine internal i1 @air.is_null_texture_2d(ptr addrspace(1) %p){\n%r=icmp eq ptr addrspace(1) %p,null\nret i1 %r\n}';defined=set(re.findall(r'^define[^\n]*@([^ (]+)\(',base,re.M));math=re.sub(r'^define ', 'define internal ',math_shims(used-defined),flags=re.M)
    definitions=dict(re.findall(r'^!(\d+) = (.*)$',source,re.M));ids=set(re.findall(r'!(\d+)','\n'.join(bodies)));pending=list(ids)
    while pending:
        for n in re.findall(r'!(\d+)',definitions[pending.pop()]):
            if n not in ids:ids.add(n);pending.append(n)
    attrs=set(re.findall(r'#(\d+)','\n'.join(bodies)));types=re.findall(r'^%[^\n]+ = type [^\n]+',source,re.M);image_type=re.search(r'^(%[^\n]+) = type \{ ptr addrspace\(4\) \}',source,re.M)[1];globals_=re.findall(r'^@__air_sampler_state[^\n]+',source,re.M)+['@_ZL13useSrlVersion = internal addrspace(2) global i32 0']
    w=['define void @psr_main_pre(ptr %textures,ptr %management,ptr %params,ptr %stats,ptr %roi,ptr %srl,i32 %version,i16 %x,i16 %y,ptr %observations){']
    for i in range(13):w += [f'%tp{i}=getelementptr ptr,ptr %textures,i64 {i}',f'%t{i}=load ptr,ptr %tp{i}',f'%a{i}=addrspacecast ptr %t{i} to ptr addrspace(1)']
    for name in ['management','roi','srl']:w += [f'%{name}2=addrspacecast ptr %{name} to ptr addrspace(2)']
    for name in ['params','stats']:w += [f'%{name}1=addrspacecast ptr %{name} to ptr addrspace(1)']
    w += ['store i32 %version,ptr addrspace(2) @_ZL13useSrlVersion','%xy0=insertelement <2 x i16> poison,i16 %x,i32 0','%xy=insertelement <2 x i16> %xy0,i16 %y,i32 1']
    # Original args1..13 are textures0..12; readnone args5/15 and output14
    # remain null only where they are never referenced before393.
    args=[image_type+' zeroinitializer']+[f'ptr addrspace(1) %a{i}'for i in range(13)]+['ptr addrspace(1) null','ptr addrspace(1) null','ptr addrspace(2) %management2','ptr addrspace(1) %params1','ptr addrspace(1) %stats1','ptr addrspace(2) %roi2','ptr addrspace(2) %srl2','<2 x i16> %xy','<2 x i16> zeroinitializer','<2 x i16> <i16 1,i16 1>','ptr %observations']
    w += ['call void @psrMainPre('+','.join(args)+')','ret void','}'];llvm_used=set(re.findall(r'@(llvm\.[^ (]+)\(','\n'.join(bodies)));decls=[re.sub(r' #\d+\s*$','',s)for s in source.splitlines()if s.startswith('declare ')and any('@'+n+'('in s for n in llvm_used)]
    ir='\n'.join([*types,*globals_,*bodies,*decls,base,math,'\n'.join(w),*[re.search(r'^attributes #'+n+r' = .*$',source,re.M)[0]for n in attrs],*[f'!{n} = {definitions[n]}'for n in sorted(ids,key=int)]])+'\n'
    return ir,{'original_main_sha256':hashlib.sha256(main.encode()).hexdigest(),'original_main_prefix_through392_sha256':hashlib.sha256(prefix.encode()).hexdigest(),'original_helpers_sha256':{n:hashlib.sha256(functions[n].encode()).hexdigest()for n in sorted(selected)},'original_arithmetic_predicates_and_FP_attrs_modified':False,'changes':'root ABI/name, truncate after392, independent observation stores','observations':OBSERVATIONS,'observation_float_count':offset,'host_sampler_contract':'same declared v3 normalized half/GTC ideal pixel-linear asS14B'}
