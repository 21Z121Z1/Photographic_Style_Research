"""Original writer instructions with a checked phased CPU imageblock scheduler.

All nonleaders run first, then the leader. Nonleaders have no post-barrier
memory reads; the copy asserts every active writer has reached the barrier.
This models the relevant happens-before edge, not a native GPU workgroup.
"""
import hashlib,re
from native_semantic_tone_check import fragment

C_SOURCE=r'''
#include <stdint.h>
#include <string.h>
static _Float16 tile[32*32*4];
static uint32_t expected,arrived;
uint32_t psr_writer_errors,psr_writer_pixels,psr_writer_copies;
void psr_writer_begin(uint32_t n){memset(tile,0,sizeof(tile));expected=n;arrived=0;psr_writer_errors=psr_writer_pixels=psr_writer_copies=0;}
void *psr_writer_ptr(uint16_t x,uint16_t y){if(x>=32||y>=32){psr_writer_errors++;return tile;}return tile+(y*32+x)*4;}
void psr_writer_barrier(void){arrived++;}
void psr_writer_store(void *raw,uint16_t x,uint16_t y,int lane,float value){uint32_t*h=raw;float*a=(float*)(h+4);if(x>=h[0]||y>=h[1]||h[2]!=4){psr_writer_errors++;return;}a[(y*h[0]+x)*4+lane]=(float)(_Float16)value;if(lane==0)psr_writer_pixels++;}
void psr_writer_copy(void*raw,void*block,uint16_t sx,uint16_t sy,uint16_t w,uint16_t h,uint16_t dx,uint16_t dy){
 psr_writer_copies++;if(arrived!=expected){psr_writer_errors++;return;}
 _Float16*p=block;for(uint32_t y=0;y<h;y++)for(uint32_t x=0;x<w;x++)for(int c=0;c<4;c++)psr_writer_store(raw,(uint16_t)(dx+x),(uint16_t)(dy+y),c,(float)p[((sy+y)*32+sx+x)*4+c]);
}
'''


def shims():
    s=['declare ptr @psr_writer_ptr(i16,i16)','declare void @psr_writer_barrier()','declare void @psr_writer_store(ptr,i16,i16,i32,float)','declare void @psr_writer_copy(ptr,ptr,i16,i16,i16,i16,i16,i16)','define internal ptr addrspace(4) @air.imageblock_data(<2 x i16> %local,i32 %a,i16 %b){\n%x=extractelement <2 x i16> %local,i32 0\n%y=extractelement <2 x i16> %local,i32 1\n%p=call ptr @psr_writer_ptr(i16 %x,i16 %y)\n%r=addrspacecast ptr %p to ptr addrspace(4)\nret ptr addrspace(4) %r\n}','define internal void @air.wg.barrier(i32 %a,i32 %b,i32 %c){\ncall void @psr_writer_barrier()\nret void\n}','define internal i1 @air.all.v2i1(<2 x i1> %a){\n%x=extractelement <2 x i1> %a,i32 0\n%y=extractelement <2 x i1> %a,i32 1\n%r=and i1 %x,%y\nret i1 %r\n}','define internal <2 x i16> @air.min.u.v2i16(<2 x i16> %a,<2 x i16> %b){\n%c=icmp ult <2 x i16> %a,%b\n%r=select <2 x i1> %c,<2 x i16> %a,<2 x i16> %b\nret <2 x i16> %r\n}']
    d=['define internal void @air.write_texture_2d.i16.v4f16(ptr addrspace(1) %target,<2 x i16> %grid,<4 x half> %v,i16 %a,i32 %b){','%p=addrspacecast ptr addrspace(1) %target to ptr','%x=extractelement <2 x i16> %grid,i32 0','%y=extractelement <2 x i16> %grid,i32 1']
    for i in range(4):d += [f'%h{i}=extractelement <4 x half> %v,i32 {i}',f'%f{i}=fpext half %h{i} to float',f'call void @psr_writer_store(ptr %p,i16 %x,i16 %y,i32 {i},float %f{i})']
    s.append('\n'.join([*d,'ret void','}']))
    c=['define internal void @air.write_imageblock_slice_to_texture_2d.i16.v4f16(ptr addrspace(1) %target,ptr addrspace(4) %block,i1 %a,<2 x i16> %source,<2 x i16> %size,<2 x i16> %dest,i16 %b,i1 %c,i32 %d){','%p=addrspacecast ptr addrspace(1) %target to ptr','%bp=addrspacecast ptr addrspace(4) %block to ptr']
    for name,v in [('s','source'),('n','size'),('d','dest')]:
        for i in range(2):c += [f'%{name}{i}=extractelement <2 x i16> %{v},i32 {i}']
    c += ['call void @psr_writer_copy(ptr %p,ptr %bp,i16 %s0,i16 %s1,i16 %n0,i16 %n1,i16 %d0,i16 %d1)','ret void','}'];s.append('\n'.join(c));return '\n'.join(s)


def build(source):
    fragment(source);main=re.search(r'^define[^\n]*@renderFinalAdjustments[^\n]+\{\n.*?^}',source,re.M|re.S)[0];address=re.search(r'^  %25 = .*?^  %27 = [^\n]+',main,re.M|re.S)[0];writer=main[main.index('  %601 ='):main.rfind('\n}')];original=address+'\n'+writer
    body=re.sub(r'%(\d+)',lambda m:'%v'+m[1],original);body=re.sub(r'^(\d+):',lambda m:'v'+m[1]+':',body,flags=re.M);helper='define void @psrWriter(<3 x half> %v600,ptr addrspace(1) %v14,ptr addrspace(2) %v19,<2 x i16> %v21,<2 x i16> %v22,<2 x i16> %v23) #2 {\nv575:\n'+body+'\n}'
    defs=dict(re.findall(r'^!(\d+) = (.*)$',source,re.M));ids=set(re.findall(r'!(\d+)',helper));pending=list(ids)
    while pending:
        for n in re.findall(r'!(\d+)',defs[pending.pop()]):
            if n not in ids:ids.add(n);pending.append(n)
    attrs=set(re.findall(r'#(\d+)',helper));types=re.findall(r'^%[^\n]+ = type [^\n]+',source,re.M)
    w=['define void @psr_write(ptr %rgb,ptr %target,ptr %roi,ptr %coords,i8 %imageblock){']
    for i in range(3):w += [f'%rp{i}=getelementptr float,ptr %rgb,i64 {i}',f'%rf{i}=load float,ptr %rp{i}',f'%rh{i}=fptrunc float %rf{i} to half',f'%r{i}=insertelement <3 x half> '+('poison'if i==0 else f'%r{i-1}')+f',half %rh{i},i32 {i}']
    for i,name in enumerate(['grid','local','size']):w += [f'%cp{i}=getelementptr <2 x i16>,ptr %coords,i64 {i}',f'%{name}=load <2 x i16>,ptr %cp{i},align 2']
    w += ['%t1=addrspacecast ptr %target to ptr addrspace(1)','%roi2=addrspacecast ptr %roi to ptr addrspace(2)','store i8 %imageblock,ptr addrspace(2) @_ZL13useImageBlock','call void @psrWriter(<3 x half> %r2,ptr addrspace(1) %t1,ptr addrspace(2) %roi2,<2 x i16> %grid,<2 x i16> %local,<2 x i16> %size)','ret void','}']
    attributes=[];changed={}
    for n in attrs:
        line=re.search(r'^attributes #'+n+r' = .*$',source,re.M)[0]
        # Host diagnostic counters are global. Conservatively widen only
        # intrinsic memory summaries, retaining every original FP attribute.
        if 'memory(argmem: readwrite)'in line:changed[n]='memory(argmem: readwrite) -> memory(readwrite)';line=line.replace('memory(argmem: readwrite)','memory(readwrite)')
        elif 'memory(read)'in line:changed[n]='memory(read) -> memory(readwrite)';line=line.replace('memory(read)','memory(readwrite)')
        attributes.append(line)
    ir='\n'.join([*types,'@_ZL13useImageBlock = internal addrspace(2) global i8 0',helper,shims(),'\n'.join(w),*attributes,*[f'!{n} = {defs[n]}'for n in sorted(ids,key=int)]])+'\n'
    return ir,{'parent_main_sha256':hashlib.sha256(main.encode()).hexdigest(),'original25_27_sha256':hashlib.sha256(address.encode()).hexdigest(),'original601_618_sha256':hashlib.sha256(writer.encode()).hexdigest(),'original_arithmetic_predicates_and_FP_attrs_changed':False,'only_SSA_alpha_renamed':True,'host_diagnostic_memory_summaries_widened':changed,'phased_scheduler':'all nonleaders first, then leader; copy requires all active barrier arrivals','tile_storage_pitch':32,'source_RGBA_alpha':1,'renderEdge_field2_byte_offset':8,'outputOffset_field12_byte_offset':160,'texture_storage_contract':'explicit RGBA16Float115 only; no other output encoding claim','original_GPU_executed':False}
