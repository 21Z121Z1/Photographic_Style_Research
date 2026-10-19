"""Fail closed on missing numeric contracts; never label a local fit global.

This is a prerequisite audit, not an interval interpreter. Syntactic call-graph
reachability includes every branch; it must not be called runtime coverage.
No image arrays, per-person data or native shader modifications are involved.
"""
import argparse,collections,hashlib,json,re
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('air',type=Path);ap.add_argument('spec_notes',type=Path);ap.add_argument('capabilities',type=Path);ap.add_argument('output',type=Path);a=ap.parse_args()
def read(p):return json.loads(p.read_text())
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
spec=read(a.spec_notes);cap=read(a.capabilities);lines=a.air.read_text().splitlines()
functions={};current=None
for n,line in enumerate(lines,1):
 if line.startswith('define '):
  current=re.search(r'@([^ (]+)\(',line).group(1);functions[current]={'first_line':n,'body':[],'calls':[]}
 if current:
  functions[current]['body'].append((n,line))
  if 'call ' in line:
   m=re.search(r'@([^ (]+)\(',line)
   if m:functions[current]['calls'].append((n,m.group(1)))
  if line=='}':current=None
assert 'renderFinalAdjustments' in functions
pending=['renderFinalAdjustments'];reachable=set()
while pending:
 f=pending.pop()
 if f in reachable:continue
 reachable.add(f);pending.extend(c for _,c in functions[f]['calls'] if c in functions)
intr=collections.defaultdict(list);fast_ops=collections.Counter()
for f in sorted(reachable):
 for n,c in functions[f]['calls']:
  if c.startswith('air.'):intr[c].append({'line':n,'function':f})
 for n,line in functions[f]['body']:
  m=re.search(r'\b(fadd|fsub|fmul|fdiv|frem|fneg|fcmp) fast\b',line)
  if m:fast_ops[m.group(1)]+=1
assert 'air.compile.fast_math_enable' in '\n'.join(lines) and 'air.compile.denorms_disable' in '\n'.join(lines)
assert any(k.startswith('air.pow.') and 'f16' in k for k in intr)
assert cap['original_metallib_sha256']=='16a8a119e3e0ae1649d32b2bbc8ea9136cb757a8d1f3eb451025821901edff11'
categories={
 'half_pow_missing_numeric_row':{'intrinsics':[k for k in intr if re.search(r'^air\.powr?\..*f16$',k)],'status':'unsupported_for_tight_certification','note':'Table8.3 does not list these operations. Constant folding/dead-branch removal requires its own proof; not all syntactic occurrences are active in captured context.'},
 'fp32_fast_pow':{'intrinsics':[k for k in intr if k.startswith('air.fast_pow.')],'status':'conditional_contract','note':'Positive-domain log2/exp2 envelope exists; no whole-consumer enclosure or domain proof implemented.'},
 'half_atan2_sqrt_trig':{'intrinsics':[k for k in intr if re.search(r'^air\.(atan2|sqrt|sin|cos)\..*f16$',k)],'status':'hardware_precondition_reported' if cap['families']['Apple4'] else 'hardware_precondition_not_reported','note':'Individual Table8.3 contracts do not freeze rewriting, rounding mode or intermediate FTZ.'},
 'mix_dot_and_basic_arithmetic':{'intrinsics':[k for k in intr if k.startswith(('air.mix.','air.dot.'))],'status':'lowering_enclosure_missing','note':'Do not assign a one-ULP contract to a multi-operation shader or silently assume the listed AIR order survives.'},
 'texture_samples':{'intrinsics':[k for k in intr if k.startswith('air.sample_texture')],'status':'sound_value_footprint_enclosure_missing','note':'Must include format conversion, finite coordinates, edge/LOD/footprint and variable main-image neighbors unless independently excluded.'}}
failure=[
 {'id':'C01','condition':'Bound every relevant half pow/powr, or prove it absent/constant under captured bindings','met':False},
 {'id':'C02','condition':'Sound actual-backend or allowed-rewrite enclosure, including rounding/FTZ/reciprocal/FMA','met':False},
 {'id':'C03','condition':'Prove all feasible F/F0 paths avoid undefined operations, or include their full uncertainty','met':False},
 {'id':'C04','condition':'Sound texture and spatial-dependency enclosure on all admitted values','met':False},
 {'id':'C05','condition':'Cover the complete declared domain; no unexamined boxes/branches treated as impossible','met':False}]
result={'os_build':'26A434','source_air':{'file':str(a.air),'sha256':sha(a.air),'language_version':'Metal4.1','metadata_lines':[6374,6375,6376,6391,6392,6393,6394]},'spec_notes_sha256':sha(a.spec_notes),'capability_sha256':sha(a.capabilities),'scope':'Syntactic reachable superset and certification prerequisites only. No pixel inference, interval pruning or full-domain certification was performed.','entry':'renderFinalAdjustments','reachable_helpers_count':len(reachable)-1,'intrinsic_call_sites':sum(map(len,intr.values())),'intrinsic_kinds':len(intr),'fast_instruction_counts':dict(fast_ops),'intrinsics':dict(sorted(intr.items())),'categories':categories,'native_half_hardware_gate_reported':cap['families']['Apple4'],'failure_conditions':failure,'certification_decision':'REFUSED_MISSING_CONTRACT_AND_COVERAGE','whole_consumer_global_tight_hull_certified':False,'remaining_skin33_global_interval':'No new tight interval; finite-format conditional outer remains[-65504,65504], nonfinite alternatives unknown.','per_pixel_3D_reduction_globally_certified':False,'original_acceptance_mask_changed':False,'threshold_max_relative':.001,'A_phase_complete':False,'not_a_proof_of_mathematical_impossibility':'A fixed native finite-domain enumeration or a future sound backend/domain proof could still bound the set. Existing ambiguity witnesses already refute a uniform1e-3 point guarantee.'}
with a.output.open('x') as f:f.write(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['reachable_helpers_count','intrinsic_call_sites','intrinsic_kinds','certification_decision','whole_consumer_global_tight_hull_certified']}))
