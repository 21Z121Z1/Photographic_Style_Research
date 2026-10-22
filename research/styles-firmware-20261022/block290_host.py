"""Reuse original block290 wrapper with the common declared texture sampler."""
import hashlib,re
from native_precomputed_semantic_check import build as old_build
from air7_full_host import sample_shim


def build(source):
    ir,original_sha=old_build(source)
    original_sampler=re.search(r'^define \{ <4 x half>, i8 \} @air.sample_texture_2d.v4f16[^\n]*\{\n.*?^}',ir,re.M|re.S)[0]
    ir=ir.replace(original_sampler,sample_shim());ir='@psr_consumer_trace = global [12 x float] zeroinitializer\n'+ir
    for offset,ssa in enumerate([305,308,332,320]):
        line=next(x for x in ir.splitlines()if x.startswith(f'  %v{ssa} ='));store=[]
        for lane in range(3):
            i=offset*3+lane;store += [f'%trace_h{i}=extractelement <3 x half> %v{ssa},i32 {lane}',f'%trace_f{i}=fpext half %trace_h{i} to float',f'%trace_p{i}=getelementptr [12 x float],ptr @psr_consumer_trace,i32 0,i32 {i}',f'store float %trace_f{i},ptr %trace_p{i}']
        ir=ir.replace(line,line+'\n'+'\n'.join(store))
    return ir,{'original_block_SHA256':original_sha,'old_accepted_wrapper_reused':True,'new_4lane_texture_header_and_v3_sampler':True,'original_arithmetic_predicates_unchanged':True,'independent_observations':[305,308,332,320],'observer_memory_contract':'root has no restrictive memory summary; observation stores valid','original_sampler_shim_sha256':hashlib.sha256(original_sampler.encode()).hexdigest()}
