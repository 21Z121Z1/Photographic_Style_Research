"""Full original BW root with internal observation stores, unchanged arithmetic."""
import re
from leaf_host import build as original_build,MATH_C


def build(source):
    ir,functions=original_build(source,['renderBWAdjustmentsByCastType'])
    start=ir.index('define internal fastcc <3 x half> @_Z29renderBWAdjustmentsByCastType');end=ir.index('\n}',start)+2;body=ir[start:end]
    for index,ssa in enumerate([12,67]):
        line=re.search(r'^  %'+str(ssa)+r' = [^\n]+',body,re.M)[0];extra=[]
        for i in range(3):extra += [f'%bw_h{ssa}_{i}=extractelement <3 x half> %{ssa},i32 {i}',f'%bw_f{ssa}_{i}=fpext half %bw_h{ssa}_{i} to float',f'%bw_p{ssa}_{i}=getelementptr [6 x float],ptr @psr_bw_trace,i32 0,i32 {index*3+i}',f'store float %bw_f{ssa}_{i},ptr %bw_p{ssa}_{i}']
        body=body.replace(line,line+'\n'+'\n'.join(extra))
    ir='@psr_bw_trace = global [6 x float] zeroinitializer\n'+ir[:start]+body+ir[end:]
    # Observation stores must not retain the original root's read-only summary.
    # Preserve every floating-point attribute; change only memory effects.
    group=re.search(r'unnamed_addr #(\d+) \{',body)[1]
    line=re.search(r'^attributes #'+group+r' = .*$',ir,re.M)[0]
    if'memory(read)'not in line:raise ValueError('Expected original BW read-only memory summary')
    ir=ir.replace(line,line.replace('memory(read)','memory(readwrite)'))
    return ir,functions
