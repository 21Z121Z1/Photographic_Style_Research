"""Prepare separate, bounded semantic diagnostics on the macOS runner.

Frozen model and V7 sources are read without modification. No lattice search,
candidate selection, or renewed bit-exact optimization is performed.
"""
from pathlib import Path
import hashlib,json,sys
src=Path('research/vm-native/runner');out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True)
original=(src/'oracle_replay_v7.inc').read_text()
loss=original[original.index('static float R3Loss('):original.index('// Generic RGB half-lattice')]
solver=original[original.index('static void V2Inverse('):original.index('static void OracleReplayV2(')]
solver=solver.replace('V2Inverse(', 'SemanticInverse(').replace('(saved?0:3)','(saved?0:1)').replace('iteration<48','iteration<24')
line=' V7PointPolish(q,call,snap,ps,input,bestX,best,bestSq,eligible,n,target,dir);'
assert solver.count(line)==1;solver=solver.replace(line,' // No half-code lattice search: this stage records remaining residuals.')
solver=solver.replace('V7: own previous recovery; contiguous R/G half-code grids with native B-band bisection as a proposal heuristic, then full retained-Apple-pipeline verification; all failures retained','S5: one output-derived seed, 24 bounded log-RGB LM iterations, native Apple oracle; no lattice search; all failures retained')
(out/'semantic_inverse_s5.inc').write_text(loss+solver)
model=(src/'consumer-structured-v8.metal').read_text()
needle='v393=f26(v392,v353,v95,v350);'
assert model.count(needle)==1
model=model.replace(needle,needle+'\nuint si=uint(v21.y)*v14.get_width()+uint(v21.x);\ndbg[si*3]=float4(float3(v392),1);\ndbg[si*3+1]=float4(float3(v393),1);\ndbg[si*3+2]=float4(float(v95),float(v350),float(v96),0);')
(out/'semantic_stage_s5.metal').write_text(model)
rows={str(p.name):hashlib.sha256(p.read_bytes()).hexdigest() for p in [src/'oracle_replay_v7.inc',src/'consumer-structured-v8.metal',out/'semantic_inverse_s5.inc',out/'semantic_stage_s5.metal']}
(out/'generated-source-sha256.json').write_text(json.dumps(rows,indent=2)+'\n')
