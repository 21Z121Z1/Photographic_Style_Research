"""Bounded original AIR90 final f32 checkpoints; no inner-loop replacements."""
import hashlib,re
from guided_host import build as original_build,NAMES

CHECKPOINTS=[('sum_p',43),('sum_i',42),('sum_ip',41),('sum_ii',40),('mean_p',47),('mean_i',48),('mean_ip',49),('mean_ii',50),('cov',52),('epsilon_plus_mii',56),('var',58),('a_f32',59),('b_f32',61)]


def build(source):
    ir,meta=original_build(source,0);body=re.search(r'^define void @'+NAMES[0]+r'[^\n]+\{\n.*?^}',ir,re.M|re.S)[0];changed=body
    # Sums are phi nodes: place all sum probes after the last phi in block38.
    groups={44:CHECKPOINTS[:4]}
    for pair in CHECKPOINTS[4:]:groups[pair[1]]=[pair]
    for anchor,pairs in groups.items():
        lines=changed.splitlines();i=next(i for i,x in enumerate(lines)if x.startswith(f'  %{anchor} ='));extra=[]
        for name,ssa in pairs:
            index=next(j for j,v in enumerate(CHECKPOINTS)if v[0]==name)
            for lane in range(4):
                j=index*4+lane;extra += [f'%trace_v{j}=extractelement <4 x float> %{ssa},i32 {lane}',f'%trace_p{j}=getelementptr [52 x float],ptr @psr_guided_trace,i32 0,i32 {j}',f'store float %trace_v{j},ptr %trace_p{j}']
        lines[i+1:i+1]=extra;changed='\n'.join(lines)
    ir='@psr_guided_trace = global [52 x float] zeroinitializer\n'+ir.replace(body,changed)
    meta.update(trace_CHECKPOINTS=CHECKPOINTS,trace_only_original_final_f32_SSA=True,trace_body_sha256=hashlib.sha256(changed.encode()).hexdigest(),original_kernel_modified='independent stores only; must compare coefficient output against saved witness')
    return ir,meta
