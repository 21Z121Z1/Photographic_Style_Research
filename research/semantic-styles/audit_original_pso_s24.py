"""Low-memory evidence/prerequisite audit. This is NOT an interval interpreter."""
from pathlib import Path
import json,re,hashlib,argparse,shutil
p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('s24_run');p.add_argument('output',type=Path);a=p.parse_args();R=a.root;D=R/'semantic-20261018';P=R/'repo';O=a.output;O.mkdir(exist_ok=False)
def read(path):return json.loads(path.read_text())
def sha(path):
 with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def ev(path,line=2):return {'file':str(path.relative_to(R)),'sha256':sha(path),'line':line}
def put(name,obj):
 with (O/name).open('x') as f:f.write(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
b22=D/'runs/39215197180/selected/out';b24=D/'runs'/a.s24_run/'selected/out';n22=read(b22/'native/s22-results.json');n24=read(b24/'native/s22-results.json');extra=read(b24/'native/s23-original-extra.json');sam=read(b24/'native/s23-samplers.json');back=read(b24/'backend-text/backend-inspection.json');cap=read(b24/'capture-text/capture-inspection.json')
for run,n in [('39215197180',n22),(a.s24_run,n24)]:
 assert n['original_creation_observed'] and not n['context_mismatches']
 assert n['fresh_vs_S5']['half_differing_components']==n['hydration']['half_differing_components']==0
 assert n['archive_attempt']['recreated_vs_retained_original']['half_differing_components']==0
 assert not n['archive_attempt']['recreated_is_original_object']
events=read(b22/'native/creation-events.json');matched=[x for x in events if x.get('kind')=='pso_creation' and x.get('returned_object')==n22['retained_pipeline_object']];assert len(matched)==1 and matched[0]['target']
assert matched[0]['api']=='newComputePipelineStateWithDescriptor:options:reflection:error:' and matched[0]['options']==0
assert any('FigMetalContext computePipelineStateFor:constants:additionalPipelineOptions:reflection:' in x for x in matched[0]['callstack'])
assert n22['retained_pipeline_class']=='AppleParavirtComputePipelineState'
assert extra['unwrapped_pipeline_class']=='AppleParavirtComputePipelineState'
assert extra['capture']['started'] and extra['capture']['stopped']
assert sam['unique_finite_half_patterns_in_texture']==63488
assert sam['const_vs_runtime_half_differences']==0
pre=P/'research/vm-native/model-v10/0010.ll';post=b22/'backend-text/original-derived.binary-001.ll';t=post.read_text();u=pre.read_text();src=ev(pre,30);dst=ev(post,23)
assert sha(post)=='08c83b323327b365d0521f9b75bb963d7cf9dc4034318c08fa3f646774f6beb5'
post24=b24/'backend-text/original-derived.binary-001.ll';assert sha(post)==sha(post24)
def scan(text):
 scope='';pow_sites=[];samplers={};fast={}
 for ln,line in enumerate(text.splitlines(),1):
  if line.startswith('define '):
   m=re.search(r'@([^ (]+)\(',line);scope=m.group(1) if m else ''
  if line=='}':scope=''
  if 'call ' in line and re.search(r'@air\.(?:pow|powr)\.(?:v[0-9]+)?f16\(',line):pow_sites.append({'line':ln,'function':scope,'intrinsic':re.search(r'@(air\.[^(]+)',line).group(1)})
  m=re.match(r'(@__air_sampler_state[^ ]*) = .*constant (?:\[2 x i64\] \[)?i64 (-?\d+)',line)
  if m:samplers[m[1]]={'value_u64':int(m[2])%(1<<64),'value_hex':f'{int(m[2])%(1<<64):016x}','line':ln}
  for op in ['fadd','fsub','fmul','fdiv','fcmp']:
   if re.search(r'\b'+op+r' fast\b',line):fast[op]=fast.get(op,0)+1
 return {'half_pow_sites':pow_sites,'samplers':samplers,'fast_instruction_counts':fast,'explicit_fma_intrinsics':len(re.findall(r'call[^\n]*@(?:air\.(?:fast_)?fma\.|llvm\.fma\.|llvm\.fmuladd\.)',text)),'compile_fast_math_enable':'air.compile.fast_math_enable' in text,'compile_denorms_disable':'air.compile.denorms_disable' in text}
old=scan(u);new=scan(t);assert new['half_pow_sites'] and new['compile_fast_math_enable'] and new['compile_denorms_disable']
own={}
for row in back['air']:
 if row['container']!='sampler-runtime.binary.metallib':continue
 path=b24/'backend-text'/row['text_file'];ir=path.read_text();names=re.findall(r'define void @([^ (]+)\(',ir)
 for name in names:own[name]={'samplers':scan(ir)['samplers'],'file':ev(path,1)}
mapping={}
for name,info in new['samplers'].items():
 hits=[]
 for kernel,row in own.items():
  if any(v['value_u64']==info['value_u64'] for v in row['samplers'].values()):hits.append(kernel)
 mapping[name]={'encoded':info,'matching_own_explicit_declarations':hits}
assert 'norm_linear' in mapping['@__air_sampler_state.3']['matching_own_explicit_declarations']
reason=[
 {'id':'C01','met':False,'missing':'Numerical/bit semantics for remaining half pow/powr in the actual final original PSO, or an all-admitted-input elimination certificate. Post-specialization AIR still contains calls; generic MSL table has no required half-pow numerical row. Independent helpers are not an inlined-original certificate.'},
 {'id':'C02','met':False,'missing':'Authenticated final original PSO backend implementation / sound allowed-rewrite enclosure (reassociation, contraction/FMA, reciprocal/approximation, RN/RTZ/FTZ). Archive AIR and matching one-frame outputs do not identify final machine operations. Capture containers/streams examined here have no decoded and authenticated final ISA.'},
 {'id':'C03','met':False,'missing':'Coverage proof for all feasible F/F0 paths including divisors, pow domains, overflow, nonfinite intermediate values and derived texture coordinates. No finite output/error guarantee for unresolved paths; no new mask exclusions.'},
 {'id':'C04','met':False,'missing':'Global enclosure for sample coordinates/LOD, format conversion, filter rounding and every admitted texel/neighbor combination in the original full program. Matching sampler declaration and center-pattern tests are partial evidence only; no per-pixel spatial independence theorem.'},
 {'id':'C05','met':False,'missing':'Complete declared-domain coverage or a proof-producing branch/exclusion certificate. No full enumeration occurred. Unexamined values/neighbor assignments remain unresolved, not excluded.'}
]
pts=read(D/'runs/39162555357/selected/out/diagnostics/per-point-classification.private.json');points=[];private=[]
for row in pts:
 op=next(x for x in row['operations'] if x['operator']=='skin-both')
 if op['estimate_relative_error_against_oracle']<=.001:continue
 ident=f'skin33_{len(points)+1:03d}'
 pub={'case_id':ident,'classification':'runner','tight_global_lower':None,'tight_global_upper':None,'finite_output_storage_outer_only':{'lower':[-65504]*3,'upper':[65504]*3,'condition':'F0 at this pixel is finite; NOT a tight feasible-set interval'},'nonfinite_alternatives':'unknown','finite_error_upper_bound':None,'full_domain_coverage_certified':False,'unproved_conditions':[x['id'] for x in reason],'original_point_threshold':.001,'original_mask_changed':False}
 points.append(pub);private.append({'case_id':ident,'point':row['point'],'prior_local_finite_union_lower':op['finite_union_lower'],'prior_local_finite_union_upper':op['finite_union_upper'],'nonuniqueness_lower_bound':op['relative_minimax_global_lower_bound']})
assert len(points)==33
put('skin33-uncertified-outer-s24.json',{'status':'UNCERTIFIED_GLOBAL_TIGHT_HULL','point_count':33,'full_declared_domain':'Every finite half RGB assignment to the captured main-image texture (alpha fixed), original external textures/parameters/ROI fixed, all variable neighbors included unless independently excluded. F(X)=original complete captured Y; project F0(X) at the original33 points. No camera-validity prior added.','points':points})
put('skin33-private-crosswalk-s24.json',private)
summary={'phase':'S22-S24','os_build':'26A434','native_runs':['39215197180','39216068165','39216507072',a.s24_run],'matched_original_creation':{k:matched[0][k] for k in ['api','options','descriptor','callstack']},'original_native_result':ev(b22/'native/s22-results.json'),'capture_native_result':ev(b24/'native/s22-results.json'),'original_AIR':src,'original_PSO_function_archive_AIR':dst,'post_specialization_AIR':new,'original_pre_specialization_summary':old,'actual_function_creation':extra['function_creation'],'actual_function_constant_limit':'Only observed explicit setters/copies are recorded. Do not interpret a missing index as an observed default. A non-specialized or archive-folded branch is not an MTLMathMode observation.','sampler_literal_matches':mapping,'own_sampler_sources':own,'sampler_native_control':sam,'GPU_capture':extra['capture'],'capture_inspection':ev(b24/'capture-text/capture-inspection.json'),'original_math_mode_claim':'Precompiled original: AIR fast-math/denorm flags and per-instruction fast observed. No original MTLCompileOptions mathMode numeric value observed; PSO descriptor carries no source compile options. Do not borrow the helper or CI source compileOptions.','archive_reconstruction_limit':'Copy of observed descriptor and exact original MTLFunction; recreated PSO is a distinct object. FailOnBinaryArchiveMiss API succeeded and captured-frame outputs match; no all-domain backend equivalence certificate.','failure_conditions':reason,'certification_decision':'REFUSED_MISSING_ORIGINAL_BACKEND_CONTRACT_AND_FULL_DOMAIN_COVERAGE','whole_consumer_global_tight_hull_certified':False,'certified_tight_points':0,'uncertified_points':33,'original_acceptance_mask_changed':False,'original_mask_pixels':186949,'threshold_max_relative':.001,'remaining_skin_failures':[6,27,33],'new_inverse_fitting_or_new_preview':False,'A_phase_complete':False,'acceptance_complete':False}
put('consumer-contract-audit-s24.json',summary)
print(json.dumps({'matched_original_PSO_creation':True,'post_specialization_half_pow_sites':len(new['half_pow_sites']),'sampler_matches':{k:v['matching_own_explicit_declarations'] for k,v in mapping.items()},'certified_tight_points':0,'uncertified_points':33,'A_phase_complete':False,'root_free_bytes':shutil.disk_usage(R).free}))
