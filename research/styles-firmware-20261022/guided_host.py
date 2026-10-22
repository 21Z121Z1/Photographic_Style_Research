"""Original matched guided kernels on CPU, with explicit one-thread imageblocks.

Texture sampling is a declared CPU R16/RGB(A)16 model: 1/256 weights and half
tie-up rounding reused from guided_reference_v3, not a measured iOS sampler.
One host kernel invocation is one threadgroup of size1, so its barrier is a
valid single-thread synchronization; imageblock stores/writes remain real.
"""
import hashlib,re
from air_alpha import canonicalize

EXPECTED=['34ac3948d377627c1e99ad1ac806f899c35203fc1caa4c6008adb31c238b08c0','e76f3b835980bdee9706ab859c8e140715e4f816e480c4a3461806635b38bfbb','a2aed1d6d9c4d7d03744e5a822662f776ca1bcdb4f3428d3c2d66e14a09e2323']
NAMES=['CMIGuidedFilterCalculateCoefficients','CMIGuidedFilterFilterCoefficients','CMIGuidedFilterApplyCoefficients']

C_SOURCE=r'''
#include <stdint.h>
#include <math.h>
float psr_gsample(void *raw,uint64_t sampler,float u,float v,int lane){
 uint32_t *h=raw;int w=h[0],height=h[1],c=h[2];float *a=(float*)(h+4);
 if(lane>=c)return lane==3?1.f:0.f;
 int normalized=sampler==34901797601020489ULL;
 float x=normalized?u*w-.5f:u-.5f,y=normalized?v*height-.5f:v-.5f;
 int ix=(int)floorf(x),iy=(int)floorf(y);float fx=nearbyintf((x-ix)*256.f)/256.f,fy=nearbyintf((y-iy)*256.f)/256.f;
 int x0=ix<0?0:ix>=w?w-1:ix,x1=ix+1<0?0:ix+1>=w?w-1:ix+1;
 int y0=iy<0?0:iy>=height?height-1:iy,y1=iy+1<0?0:iy+1>=height?height-1:iy+1;
 float q00=a[(y0*w+x0)*c+lane],q10=a[(y0*w+x1)*c+lane],q01=a[(y1*w+x0)*c+lane],q11=a[(y1*w+x1)*c+lane];
 float top=fmaf(q10-q00,fx,q00),bot=fmaf(q11-q01,fx,q01),value=fmaf(bot-top,fy,top);
 _Float16 rounded=(_Float16)value;union{_Float16 f;uint16_t u;}bits={rounded};
 if(isfinite((float)rounded)&&value>(float)rounded){bits.u+=bits.u&0x8000?-1:1;float up=(float)bits.f;if((double)value==((double)rounded+up)*.5)return up;}
 return (float)rounded;
}
void psr_gwrite(void *raw,uint16_t x,uint16_t y,int lane,float value){uint32_t*h=raw;if(x>=h[0]||y>=h[1]||lane>=h[2])return;float*a=(float*)(h+4);a[(y*h[0]+x)*h[2]+lane]=(float)(_Float16)value;}
'''


def shims():
    s=['@psr_block = internal global [8 x half] zeroinitializer,align 8','declare float @psr_gsample(ptr,i64,float,float,i32)','declare void @psr_gwrite(ptr,i16,i16,i32,float)']
    for name,offset in [('width',0),('height',1)]:s += [f'define internal i32 @air.get_{name}_texture_2d(ptr addrspace(1) %p,i32 %lod){{\n%q=getelementptr i32,ptr addrspace(1) %p,i32 {offset}\n%n=load i32,ptr addrspace(1) %q\nret i32 %n\n}}']
    s += ['define internal float @air.convert.f.f32.u.i32(i32 %a){\n%v=uitofp i32 %a to float\nret float %v\n}','define internal float @air.convert.f.f32.s.i16(i16 %a){\n%v=sitofp i16 %a to float\nret float %v\n}','define internal <2 x float> @air.convert.f.v2f32.u.v2i16(<2 x i16> %a){\n%v=uitofp <2 x i16> %a to <2 x float>\nret <2 x float> %v\n}','define internal <4 x half> @air.convert.f.v4f16.f.v4f32(<4 x float> %a){\n%v=fptrunc <4 x float> %a to <4 x half>\nret <4 x half> %v\n}','define internal i1 @air.all.v2i1(<2 x i1> %a){\n%x=extractelement <2 x i1> %a,i32 0\n%y=extractelement <2 x i1> %a,i32 1\n%r=and i1 %x,%y\nret i1 %r\n}','define internal void @air.wg.barrier(i32 %a,i32 %b,i32 %c){\nret void\n}','define internal ptr addrspace(4) @air.imageblock_data(<2 x i16> %local,i32 %a,i16 %b){\n%p=addrspacecast ptr @psr_block to ptr addrspace(4)\nret ptr addrspace(4) %p\n}']
    sample=['define internal {<4 x float>,i8} @air.sample_texture_2d.v4f32(ptr addrspace(1) %p,ptr addrspace(2) %sampler,<2 x float> %uv,i1 %a,<2 x i32> %o,i1 %b,float %c,float %d,i32 %e){','%ptr=addrspacecast ptr addrspace(1) %p to ptr','%bits=load i64,ptr addrspace(2) %sampler','%x=extractelement <2 x float> %uv,i32 0','%y=extractelement <2 x float> %uv,i32 1']
    for i in range(4):sample += [f'%s{i}=call float @psr_gsample(ptr %ptr,i64 %bits,float %x,float %y,i32 {i})',f'%v{i}=insertelement <4 x float> '+('poison'if i==0 else f'%v{i-1}')+f',float %s{i},i32 {i}']
    sample += ['%r=insertvalue {<4 x float>,i8} zeroinitializer,<4 x float> %v3,0','ret {<4 x float>,i8} %r','}'];s.append('\n'.join(sample))
    write=['define internal void @air.write_imageblock_slice_to_texture_2d.i16.v4f16(ptr addrspace(1) %target,ptr addrspace(4) %block,i1 %a,<2 x i16> %b,<2 x i16> %c,<2 x i16> %grid,i16 %d,i1 %e,i32 %f){','%ptr=addrspacecast ptr addrspace(1) %target to ptr','%v=load <4 x half>,ptr addrspace(4) %block,align 8','%x=extractelement <2 x i16> %grid,i32 0','%y=extractelement <2 x i16> %grid,i32 1']
    for i in range(4):write += [f'%h{i}=extractelement <4 x half> %v,i32 {i}',f'%f{i}=fpext half %h{i} to float',f'call void @psr_gwrite(ptr %ptr,i16 %x,i16 %y,i32 {i},float %f{i})']
    write+=['ret void','}'];s.append('\n'.join(write));return '\n'.join(s)


def build(source,index):
    canonical,provenance=canonicalize(source);digest=hashlib.sha256(canonical.encode()).hexdigest()
    if digest!=EXPECTED[index]:raise ValueError('Exact matched guided module required')
    name=NAMES[index];body=re.search(r'^define void @'+name+r'[^\n]+\{\n.*?^}',source,re.M|re.S)[0]
    types='\n'.join(re.findall(r'^%[^\n]+ = type [^\n]+',source,re.M));image_type=re.search(r'^(%[^\n]+) = type \{ ptr addrspace\(4\) \}',source,re.M)[1]
    wrapper=[f'define void @psr_guided_{index}(ptr %t0,ptr %t1,ptr %t2,ptr %t3,ptr %r,ptr %eps,ptr %single,i16 %x,i16 %y){{']
    for i in range(4):wrapper += [f'%p{i}=addrspacecast ptr %t{i} to ptr addrspace(1)']
    wrapper += ['%r2=addrspacecast ptr %r to ptr addrspace(2)','%eps2=addrspacecast ptr %eps to ptr addrspace(2)','%single2=addrspacecast ptr %single to ptr addrspace(2)','%g0=insertelement <2 x i16> poison,i16 %x,i32 0','%g=insertelement <2 x i16> %g0,i16 %y,i32 1']
    args=image_type+' zeroinitializer,'+','.join(f'ptr addrspace(1) %p{i}'for i in range(4))
    if index==0:args+=',ptr addrspace(2) %r2,ptr addrspace(2) %eps2,ptr addrspace(2) %single2'
    elif index==1:args+=',ptr addrspace(2) %r2'
    args+=',<2 x i16> %g,<2 x i16> zeroinitializer'
    if index==2:args+=',<2 x i16> <i16 1,i16 1>'
    wrapper += [f'call void @{name}({args})','ret void','}']
    globals_='\n'.join(re.findall(r'^@__air_sampler_state[^\n]+',source,re.M));attrs='\n'.join(re.findall(r'^attributes #[^\n]+',source,re.M));metadata='\n'.join(re.findall(r'^!\d+ = [^\n]+',source,re.M))
    ir='\n'.join([types,globals_,body,shims(),'\n'.join(wrapper),attrs,metadata])+'\n'
    return ir,{'canonical_sha256':digest,'provenance':provenance,'original_complete_kernel_sha256':hashlib.sha256(body.encode()).hexdigest(),'original_kernel_modified':False,'one_thread_per_imageblock':True,'sampler_assumption':'reused v3 1/256 weights, half tie-up','native_GPU':False}
