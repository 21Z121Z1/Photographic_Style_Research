"""Original Apple CPU scalar headroom pair; separate from pixel GTM/LTM."""
from pathlib import Path
import hashlib,json,math,os,struct,subprocess,sys
R=Path.cwd();D=R/'research/hdr-native';W=Path(os.environ['W']);O=W/'out'
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,j):
    with Path(p).open('x')as f:json.dump(j,f,indent=2,allow_nan=False);f.write('\n')
def F(x):return struct.unpack('<f',struct.pack('<f',x))[0]
assert sys.platform=='darwin'and subprocess.check_output(['sw_vers','-buildVersion'],text=True).strip()=='26A434'
freeze={'os_build':'26A434','image_version':os.environ.get('ImageVersion'),'source_sha256':{p.name:sha(p)for p in[D/'probe_headroom_s66.m',D/'run_hdr_s66.py',D/'evidence/s66/headroom-and-input-source.txt']},'helper_addresses':['0x2333c8994','0x2333c89fc','0x2333c8a64'],'literal_addresses':['0x233559bf8','0x233559c00'],'style_branches':['factory-default','LongGray'],'tones':[-1,0,1],'headrooms':[0,.25,.5,1,1.25,2,4,8,16,64],'scope':'CPU scalar only; no pixel/GTM/LTM/semantic inverse gate claim','original_pipeline_caller_binding_unknown':True,'old_masks_thresholds_unchanged':True}
save(O/'formula-freeze-s66.json',freeze);frozen_sha=sha(O/'formula-freeze-s66.json')
with(O/'build.log').open('x')as f:subprocess.run(['clang','-O2','-fobjc-arc','-Wno-deprecated-declarations','-framework','Foundation',str(D/'probe_headroom_s66.m'),'-o',str(W/'probe')],stdout=f,stderr=subprocess.STDOUT,check=True,timeout=180)
with(O/'native.log').open('x')as f:p=subprocess.run([str(W/'probe'),str(O/'native-headroom-s66.json')],stdout=f,stderr=subprocess.STDOUT,timeout=180)
assert p.returncode==0,'Inspect native/ABI checkpoint before revising or repeating'
j=json.loads((O/'native-headroom-s66.json').read_text());assert j['completed']and len(j['rows'])==60
qf=j['literal_exponents']['forward'];qi=j['literal_exponents']['inverse'];rows=[]
for x in j['rows']:
    h=x['input'];a=x['forward'];b=x['inverse_of_forward'];back=x['inverse_direct'];assert all(isinstance(v,(int,float))and math.isfinite(v)for v in [h,a,b,back]);on=x['cast_is_LongGray_pointer']
    fa=F(math.pow(h,qf))if on else F(h);fb=F(math.pow(h,qi))if on else F(h)
    rows.append({'style':x['style'],'tone':x['tone'],'headroom':h,'forward_abs_error_vs_source_literal_model':abs(a-fa),'inverse_abs_error_vs_source_literal_model':abs(back-fb),'native_roundtrip_abs_error':abs(b-h),'native_roundtrip_relative_error':abs(b-h)/h if h>0 else None,'flag_helper':x['flag_helper'],'style_fields_unchanged':x['style_fields_unchanged']})
invariance=[]
for style in freeze['style_branches']:
    for h in freeze['headrooms']:
        group=[x for x in j['rows']if x['style']==style and x['input']==h];assert len(group)==3
        invariance.append(len({(x['forward_bits'],x['inverse_direct_bits'])for x in group})==1)
summary={'os_build':'26A434','image_version':os.environ.get('ImageVersion'),'native_scalar_cases':60,'literal_exponents':j['literal_exponents'],'forward_inverse_exponent_product':qf*qi,'max_forward_model_abs':max(x['forward_abs_error_vs_source_literal_model']for x in rows),'max_inverse_model_abs':max(x['inverse_abs_error_vs_source_literal_model']for x in rows),'max_native_roundtrip_abs':max(x['native_roundtrip_abs_error']for x in rows),'max_positive_native_roundtrip_relative':max(x['native_roundtrip_relative_error']for x in rows if x['native_roundtrip_relative_error']is not None),'helper_tone_invariant_for_all_tested_values':all(invariance),'flag_helper_false_for_all_tested_values':all(not x['flag_helper']for x in rows),'style_fields_unchanged':all(x['style_fields_unchanged']for x in rows),'only_helper_branch_and_finite_test_values_verified':True,'no_complete_headroom_domain_contract':True,'no_photograph_pixel_operator_or_Metal_PSO_executed':True,'original_pipeline_caller_binding_proven':False,'no_pixel_GTM_LTM_or_j_inverse_inferred':True,'formula_freeze_sha256':frozen_sha,'A_phase_complete':False,'acceptance_complete':False}
save(O/'scalar-validation-s66.json',{'rows':rows,'summary':summary});save(O/'analysis-s66.json',summary)
assert sha(O/'formula-freeze-s66.json')==frozen_sha
print(json.dumps({'scalar_cases':60,'max_forward_model_abs':summary['max_forward_model_abs'],'max_inverse_model_abs':summary['max_inverse_model_abs'],'max_native_roundtrip_relative':summary['max_positive_native_roundtrip_relative'],'pixel_inverse_gate_pass_inferred':False}))
