"""Runner-only bounds audit. No new pixel solver or old bit-exact fitting."""
from pathlib import Path
import sys,json,struct,hashlib,math,csv
import numpy as np
from unicorn import Uc,UC_ARCH_ARM64,UC_MODE_ARM
from unicorn.arm64_const import *
S,O=map(Path,sys.argv[1:]);O.mkdir(exist_ok=True);SRC=Path('research/semantic-styles')
native=json.loads((O.parent/'native-format.json').read_text());assert native['largest_finite_half_abs']==65504 and native['finite_half_bit_patterns']==63488
meta=json.loads((SRC/'evidence/producer-j-downstream-s18.json').read_text());block=meta['mixed_vector_block'];raw=bytes.fromhex(block['instruction_bytes_le']);assert hashlib.sha256(raw).hexdigest()==block['sha256']
start=int(block['start'],16);end=int(block['end_exclusive'],16)
u=Uc(UC_ARCH_ARM64,UC_MODE_ARM);u.mem_map(start&~4095,4096);u.mem_write(start,raw);u.mem_map(0x30000000,0x20000)
u.reg_write(UC_ARM64_REG_CPACR_EL1,3<<20);u.reg_write(UC_ARM64_REG_FPCR,0)
bits=lambda f:struct.unpack('<I',struct.pack('<f',f))[0]
F=np.float32;rng=np.random.default_rng(2026101901);cases=[]
def emulate(base,target,weight):
    n=len(base);fp=0x3001f000;config=0x3001e000;pa,pb,pw=0x30000000,0x30008000,0x30010000
    u.mem_write(pa,base.tobytes());u.mem_write(pb,target.tobytes());u.mem_write(pw,struct.pack('<f',weight));u.mem_write(fp-0xa0,struct.pack('<Q',config));u.mem_write(config+0x18,struct.pack('<I',n))
    for reg,v in [(UC_ARM64_REG_FP,fp),(UC_ARM64_REG_X19,pa),(UC_ARM64_REG_X8,pb),(UC_ARM64_REG_X20,pw),(UC_ARM64_REG_X22,0)]:u.reg_write(reg,v)
    u.reg_write(UC_ARM64_REG_S9,bits(1.));u.emu_start(start,end,count=10000)
    return np.frombuffer(bytes(u.mem_read(pa,n*4)),'f4').copy()
for n in [1,3,8,9,16,17,32,65,129]:
    for w in [0.,.05,.1953125,.5,1.]:
        for same in [False,True]:
            a=rng.uniform(0,2,n).astype('f4');b=a.copy() if same else rng.uniform(0,2,n).astype('f4');p=emulate(a,b,F(w));t=F(F(1)-F(w));expected=np.empty(n,'f4');vector_end=n//8*8
            for i in range(n):
                m=F(F(w)*b[i]);expected[i]=F(F(t*a[i])+m) if i<vector_end else F(float(t)*float(a[i])+float(m))
            cases.append({'count':n,'weight':w,'same_vectors':same,'ARM_vs_declared_f32_max_abs':float(abs(p-expected).max()),'different_f32_components':int(np.count_nonzero(p.view('u4')!=expected.view('u4'))),'output_change_max_abs':float(abs(p-a).max()),'real_affine_max_abs_rounding_error':float(abs(p.astype('f8')-((1-w)*a.astype('f8')+w*b.astype('f8'))).max())})
assert all(c['different_f32_components']==0 for c in cases)
# Private per-point envelopes. The broad global interval follows storage type
# only; it is not a certified hull conditional on F(x)=y, and Inf/NaN remain
# separate unknown reachability, not silently dropped from a mask.
audit=json.loads((S/'diagnostics/s17-audit.json').read_text());points=json.loads((S/'diagnostics/per-point-classification.private.json').read_text());witness=json.loads((S/'diagnostics/all-impossibility-witnesses.private.json').read_text())
y_by={p['point']:p['y_actual_identical'] for p in witness};M=65504.;small=2**-24;bounds=[];rows=[]
weights=np.array([.22897456,.69173852,.07928691]);weights=weights/weights.sum()
for p in points:
    joint=p['operations'][2]
    if joint['estimate_relative_error_against_oracle']<=1e-3:continue
    assert joint['relative_minimax_global_lower_bound']>1e-3
    y=float(np.dot(y_by[p['point']],weights));lo=math.log2(y/M);hi=math.log2(y/small)
    row={'point':p['point'],'actual_output_luma':y,'finite_RGB_storage_outer_lower':[-M]*3,'finite_RGB_storage_outer_upper':[M]*3,'finite_positive_RGB_only_log2_Y_over_F0_EV_outer':[lo,hi],'finite_positive_RGB_condition_not_proved_globally':True,'Inf_NaN_reachability':'unknown','tight_global_hull':None,'local_union_lower':joint['finite_union_lower'],'local_union_upper':joint['finite_union_upper'],'native_witness_relative_minimax_lower_bound':joint['relative_minimax_global_lower_bound'],'not_a_camera_scene_interval':True}
    bounds.append(row);rows.append({'point':row['point'],'finite_rgb_min':-M,'finite_rgb_max':M,'conditional_positive_rgb_EV_min':lo,'conditional_positive_rgb_EV_max':hi,'tight_global_hull_certified':False,'nonfinite_reachability':'unknown'})
assert len(bounds)==33
with (O/'skin33-global-outer.private.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(O/'skin33-global-outer.private.json').write_text(json.dumps(bounds,indent=2)+'\n')
# Analytic sensitivity in a deliberately stated *pixel-mixture hypothesis*.
# This is not asserted to be allocateTone or the actual Apple pixel model.
beta=25/128
sensitivity=[]
for ratio in [0.,.25,.5,1.,2.,4.,5.,128/25,8.,16.]:
    denominator=1-beta*ratio
    sensitivity.append({'T_over_observed_assumed':ratio,'w0_assumed':0.,'delta_weight_bound':beta,'hypothesized_inverse_formula':'P0=(P-beta*T)/(1-beta) at maximum weight','maximum_EV_if_brightening_and_positive':math.log2((1-beta)/denominator) if denominator>0 and ratio>=1 else None,'finite_upper_lost_at_nonpositive_inverse_lower_bound':denominator<=0,'actual_Apple_pixel_mapping_verified':False})
report={'os_build_native_format':'26A434','producer_code_build':'24A446 user-provided provenance; not sample-matching firmware','source_run':39162555357,'new_native_pixel_search':False,'old_precision_gates_modified':False,'native_half_format':native,'finite_input_pattern_cube_count':63488**3,'skin33':{'points':33,'all_have_impossibility_witness':True,'finite_output_storage_outer':[-M,M],'tight_global_hull_certified':False,'nonfinite_reachability':'unknown','conditional_positive_RGB_EV_envelope_min':min(r['conditional_positive_rgb_EV_min'] for r in rows),'conditional_positive_RGB_EV_envelope_max':max(r['conditional_positive_rgb_EV_max'] for r in rows),'changes_to_original_acceptance_mask':0,'threshold':1e-3},'j_downstream':{'instruction_start':block['start'],'instruction_end':block['end_exclusive'],'instruction_sha256':block['sha256'],'synthetic_cases':len(cases),'different_f32_components':sum(c['different_f32_components'] for c in cases),'max_real_affine_rounding_error':max(c['real_affine_max_abs_rounding_error'] for c in cases),'verified_formula':'Working vector V(w)=(1-w)*B+w*T. Original ARM loop uses separate mul/add in vector chunks and FMA in scalar tail. Not a final pixel gain.','real_affine_weight_change_bound':'|DeltaV[k]| <= 0.1953125*|T[k]-B[k]| for Delta w in[0,0.1953125], all other vectors fixed.','runtime_target_buffer':'0x27994b2d0 is mutable __common, populated from selected face histogram; static zeros are not a captured frame.','downstream_break':'allocateTone consumes the changed vector alongside histograms, tuning and other constraints; quantile/division, max/min, scaleToFitRange and interpolation follow. No certified final-pixel Lipschitz bound from j alone.','final_pixel_EV_interval_identified':False,'actual_face_matting_identified':False},'explicit_pixel_mixture_hypothesis_only':sensitivity,'case_rows':cases,'preview_reused_without_changes':audit['preview_integrity'],'scope':'Representation-only outer bounds and a short producer ARM block replay. No claim of global tight inverse hull or real-camera amplitude.'}
(O/'s18-bounds.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
