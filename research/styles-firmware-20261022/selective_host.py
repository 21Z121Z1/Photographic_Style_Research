"""Root wrapper plus explicitly four-channel variant of existing 2D host shim."""
import re
from leaf_host import build as original_build,MATH_C
from native_precomputed_semantic_check import SAMPLER_C


def build(source):
    ir,functions=original_build(source,['renderSelectiveColorAdjustments'])
    shim=['declare float @psr_sample2d(ptr,float,float,i32)','define {<4 x half>,i8} @air.sample_texture_2d.v4f16(ptr addrspace(1) %p,ptr addrspace(2) %s,<2 x float> %xy,i1 %a,<2 x i32> %o,i1 %b,float %c,float %d,i32 %e){','%u=extractelement <2 x float> %xy,i32 0','%v=extractelement <2 x float> %xy,i32 1','%t=addrspacecast ptr addrspace(1) %p to ptr']
    for n in range(4):shim += [f'%f{n}=call float @psr_sample2d(ptr %t,float %u,float %v,i32 {n})',f'%h{n}=fptrunc float %f{n} to half',f'%x{n}=insertelement <4 x half> '+('zeroinitializer'if n==0 else f'%x{n-1}')+f',half %h{n},i32 {n}']
    shim += ['%r=insertvalue {<4 x half>,i8} zeroinitializer,<4 x half> %x3,0','ret {<4 x half>,i8} %r','}']
    ir,count=re.subn(r'^define \{<4 x half>,i8\} @air.sample_texture_2d.v4f16[^\n]+\{\n.*?^}', '\n'.join(shim),ir,flags=re.M|re.S)
    if count!=1:raise ValueError('Exactly one original host sample shim must be replaced')
    c=SAMPLER_C.replace('*3+channel','*4+channel')
    assert c.count('*4+channel')==4
    return ir,functions,MATH_C+c
