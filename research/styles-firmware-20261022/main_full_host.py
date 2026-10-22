"""Complete original AIR10 entry, recursive helpers and original direct writer.

Observations are independent stores immediately after each original SSA, not
helper replacements. The wrapper fixes one-thread groups and direct output;
imageblock alternatives remain in the original function but are not selected.
"""
import hashlib,re
from native_semantic_tone_check import fragment
from leaf_host import shims as math_shims
from guided_host import shims as texture_shims
from air7_full_host import sample_shim,direct_write_shim,C_SOURCE
from main_pre393_host import OBSERVATIONS as PRE

OBSERVATIONS=PRE[:10]+[('precomputed335',335,3)]+PRE[10:]+[(n,i,3)for n,i in [('skin393',393),('highlight394',394),('highlight398',398),('bright400',400),('selected404',404),('neutral408',408),('warm409',409),('selective413',413),('tonal468',468),('BW_input472',472),('color476',476),('BW477',477),('mixed492',492),('haze493',493),('selected501',501),('protect566',566),('channel567',567),('linear597',597),('output600',600)]]


def build(source,*,observe=True):
    fragment(source);functions={m[1]:m[0]for m in re.finditer(r'^define[^\n]*@([^ (]+)\([^\n]+\{\n.*?^}',source,re.M|re.S)};main=functions['renderFinalAdjustments'];header=main.splitlines()[0].replace('@renderFinalAdjustments','@psrMainFull');end=header.rfind(')');header=header[:end]+',ptr %observations'+header[end:];body=header+'\n'+main.split('\n',1)[1];offset=0
    for name,ssa,n in OBSERVATIONS:
        trace=[]
        for i in range(n):
            j=offset+i
            if n==3:trace += [f'%obs_h{j}=extractelement <3 x half> %{ssa},i32 {i}']
            value=f'%obs_h{j}'if n==3 else f'%{ssa}'
            trace += [f'%obs_f{j}=fpext half {value} to float',f'%obs_p{j}=getelementptr float,ptr %observations,i64 {j}',f'store float %obs_f{j},ptr %obs_p{j}']
        if observe:
            lines=body.splitlines();i=next(i for i,x in enumerate(lines)if x.startswith(f'  %{ssa} ='))
            if ' = phi 'in lines[i]:
                while i+1<len(lines)and ' = phi 'in lines[i+1]:i+=1
            lines[i+1:i+1]=trace;body='\n'.join(lines)
        offset+=n
    selected=set();pending=re.findall(r'@(_Z[^ (]+)\(',body)
    while pending:
        n=pending.pop()
        if n in selected:continue
        selected.add(n);pending+=re.findall(r'@(_Z[^ (]+)\(',functions[n])
    bodies=[body,*[functions[n]for n in sorted(selected)]];used=set(re.findall(r'@(air\.[^ (]+)\(','\n'.join(bodies)))
    base=texture_shims()+'\n'+sample_shim()+'\n'+direct_write_shim()+'''\ndefine internal i1 @air.is_null_texture_2d(ptr addrspace(1) %p){
%r=icmp eq ptr addrspace(1) %p,null
ret i1 %r
}
define internal <2 x i16> @air.min.u.v2i16(<2 x i16> %a,<2 x i16> %b){
%c=icmp ult <2 x i16> %a,%b
%r=select <2 x i1> %c,<2 x i16> %a,<2 x i16> %b
ret <2 x i16> %r
}'''
    defined=set(re.findall(r'^define[^\n]*@([^ (]+)\(',base,re.M));math=re.sub(r'^define ', 'define internal ',math_shims(used-defined),flags=re.M)
    definitions=dict(re.findall(r'^!(\d+) = (.*)$',source,re.M));ids=set(re.findall(r'!(\d+)','\n'.join(bodies)));pending=list(ids)
    while pending:
        for n in re.findall(r'!(\d+)',definitions[pending.pop()]):
            if n not in ids:ids.add(n);pending.append(n)
    attrs=set(re.findall(r'#(\d+)','\n'.join(bodies)));types=re.findall(r'^%[^\n]+ = type [^\n]+',source,re.M);image_type=re.search(r'^(%[^\n]+) = type \{ ptr addrspace\(4\) \}',source,re.M)[1];globals_=re.findall(r'^@__air_sampler_state[^\n]+',source,re.M)+['@_ZL13useSrlVersion = internal addrspace(2) global i32 0','@_ZL13useImageBlock = internal addrspace(2) global i8 0']
    w=['define void @psr_main_full(ptr %textures,ptr %target,ptr %management,ptr %params,ptr %stats,ptr %roi,ptr %srl,i32 %version,i16 %x,i16 %y,ptr %observations){']
    for i in range(13):w += [f'%tp{i}=getelementptr ptr,ptr %textures,i64 {i}',f'%t{i}=load ptr,ptr %tp{i}',f'%a{i}=addrspacecast ptr %t{i} to ptr addrspace(1)']
    for name in ['management','roi','srl']:w += [f'%{name}2=addrspacecast ptr %{name} to ptr addrspace(2)']
    for name in ['params','stats','target']:w += [f'%{name}1=addrspacecast ptr %{name} to ptr addrspace(1)']
    w += ['store i32 %version,ptr addrspace(2) @_ZL13useSrlVersion','store i8 0,ptr addrspace(2) @_ZL13useImageBlock','%xy0=insertelement <2 x i16> poison,i16 %x,i32 0','%xy=insertelement <2 x i16> %xy0,i16 %y,i32 1']
    args=[image_type+' zeroinitializer']+[f'ptr addrspace(1) %a{i}'for i in range(13)]+['ptr addrspace(1) %target1','ptr addrspace(1) null','ptr addrspace(2) %management2','ptr addrspace(1) %params1','ptr addrspace(1) %stats1','ptr addrspace(2) %roi2','ptr addrspace(2) %srl2','<2 x i16> %xy','<2 x i16> zeroinitializer','<2 x i16> <i16 1,i16 1>','ptr %observations']
    w += ['call void @psrMainFull('+','.join(args)+')','ret void','}'];llvm_used=set(re.findall(r'@(llvm\.[^ (]+)\(','\n'.join(bodies)));decls=[re.sub(r' #\d+\s*$','',s)for s in source.splitlines()if s.startswith('declare ')and any('@'+n+'('in s for n in llvm_used)]
    ir='\n'.join([*types,*globals_,*bodies,*decls,base,math,'\n'.join(w),*[re.search(r'^attributes #'+n+r' = .*$',source,re.M)[0]for n in attrs],*[f'!{n} = {definitions[n]}'for n in sorted(ids,key=int)]])+'\n'
    return ir,{'original_complete_main_sha256':hashlib.sha256(main.encode()).hexdigest(),'original_helpers_sha256':{n:hashlib.sha256(functions[n].encode()).hexdigest()for n in sorted(selected)},'original_arithmetic_predicates_and_FP_attrs_modified':False,'changes':'root ABI/name; immediate observation stores'if observe else'root ABI/name only','observations':OBSERVATIONS if observe else[],'observation_float_count':offset,'direct_writer_in_original_main':True,'threadgroup_size':[1,1],'host_sampler_contract':'v3 normalized half; ideal pixel GTC; explicit CPU assumptions'}
