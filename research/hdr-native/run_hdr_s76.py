"""Actual original CI execution. Small synthetic sources; no shader/math override."""
from pathlib import Path
import datetime,hashlib,json,math,os,struct,subprocess,sys
D=Path('research/hdr-native');W=Path(os.environ['W']);O=W/'out';I=W/'in';I.mkdir()
assert subprocess.check_output(['sw_vers','-buildVersion'],text=True).strip()=='26A434'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb')as f:
        while b:=f.read(1048576):h.update(b)
    return h.hexdigest()
def save(name,obj):
    with(O/name).open('x')as f:json.dump(obj,f,separators=(',',':'),allow_nan=False);f.write('\n')
parent=(D/'probe_consumer_bindings_s72.m').read_text();(W/'consumer_cpu_prefix_s73.inc').write_text(parent[:parent.index('int main(int argc,char**argv)')])
parent=(D/'probe_consumer_roi_s73.m').read_text();(W/'consumer_cpu_prefix_s75.inc').write_text(parent[:parent.index('int main(int argc,char**argv)')])
targets=json.loads((D/'evidence/s75/native-targets.json').read_text())
spec={'native_selector_targets':targets['optimized_selector_stubs']}
with(W/'meta-spec.json').open('x')as f:json.dump(spec,f)
files=[D/n for n in['probe_consumer_ci_s76.m','ci_trace_s75.inc','run_hdr_s76.py','probe_consumer_roi_s73.m','probe_consumer_bindings_s72.m','probe_headroom_s66.m']]
files +=[D/'evidence/s75/native-targets.json',D/'evidence/s75/source-flow.json']
resources=[]
for p in[Path('/System/Library/PrivateFrameworks/CMImaging.framework/Resources/default.metallib'),Path('/System/Library/PrivateFrameworks/CMImaging.framework/Versions/A/Resources/default.metallib')]:
    if p.is_file():resources.append({'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'binary_not_uploaded':True})
recipe={'probe_version':'S76','S75_failed_before_native':{'run_id':39387345347,'artifact_id':12248270752,'reason':'SDK lacks NSValue valueWithCGRect constructor declaration; portable valueWithBytes/getValue used only for observer geometry storage'},'os_build':'26A434','image_version':os.environ.get('ImageVersion'),'source_sha256':{str(p):sha(p)for p in files},'derived_prefix_sha256':{p.name:sha(p)for p in[W/'consumer_cpu_prefix_s73.inc',W/'consumer_cpu_prefix_s75.inc']},'resources':resources,'test_plan_frozen_before_compile_and_native':'Three finite geometries full/tile/translated, useLightMap false/true, exact A-to-A repeat. Original CI apply/process and return preserved; nil stats explicitly selects type3. Original flags and table bound before controls. No residency or math override. Fixed tone+.35/base1/j1 and other declared arguments; no original photo.','scope':'Original CI allocation + controlled native forward oracle, not five-photo acceptance, original stats-present type2, 33-point global hull, scene recovery or physical j EV.','CPU_layout_contract':'CPU format/bytesPerRow/baseAddress are not used to interpret unsynchronized Metal textures. Actual MTL pixelFormat/extent recorded; blit stride separate.','API_sources':['https://developer.apple.com/documentation/coreimage/ciimageprocessorinput','https://developer.apple.com/documentation/coreimage/ciimageprocessorkernel','https://developer.apple.com/documentation/coreimage/ciimageprocessorkernel/synchronizeinputs','https://developer.apple.com/documentation/coreimage/ciimageprocessoroutput/metalcommandbuffer'],'gates':{'A_to_A_original_half_bytes':'exact','CI_float_gate_max_abs':1e-5,'CI_float_gate_PSNR_dB':60,'old_1e_3_masks_and_full_domain_unchanged':True},'A_phase_complete':False,'acceptance_complete':False}
save('recipe.json',recipe)
with(O/'build.log').open('x')as log:
    subprocess.run(['clang','-I',str(D),'-I',str(W),'-O2','-fobjc-arc','-fblocks','-framework','Foundation','-framework','CoreFoundation','-framework','CoreGraphics','-framework','CoreImage','-framework','Metal',str(D/'probe_consumer_ci_s76.m'),'-o',str(W/'probe')],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240)
def run(mode,spec_path,timeout):
    with(O/(mode+'.log')).open('x')as log:
        proc=subprocess.Popen([str(W/'probe'),mode,str(spec_path),str(O)],stdout=log,stderr=subprocess.STDOUT)
        try:return proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            # An observation timeout is not process termination: inspect SAME handle.
            live=proc.poll()is None
            save(mode+'-timeout.json',{'pid':proc.pid,'still_live_on_same_handle':live,'observation_timeout_seconds':timeout,'not_restarted':True})
            if live:
                with(O/(mode+'-live-stack.log')).open('x')as stack:
                    try:subprocess.run(['lldb','-b','-p',str(proc.pid),'-o','thread backtrace all','-o','process detach','-o','quit'],stdout=stack,stderr=subprocess.STDOUT,timeout=35)
                    except subprocess.TimeoutExpired:stack.write('\nLLDB observation timed out; target not presumed stopped.\n')
                if proc.poll()is None:
                    proc.terminate()
                    try:proc.wait(timeout=10)
                    except subprocess.TimeoutExpired:proc.kill();proc.wait(timeout=10)
            return proc.returncode if proc.returncode is not None else 124
rc=run('metadata',W/'meta-spec.json',120)
if rc:save('analysis.json',{'metadata_returncode':rc,'native_evaluation_started':False,'A_phase_complete':False,'acceptance_complete':False});sys.exit(rc)
meta_doc=json.loads((O/'metadata.json').read_text());assert meta_doc['completed'];meta=meta_doc['metadata']
assert len(meta['input_formats'])==9
assert {r['selector']:bool(r['value'])for r in meta['flags']}=={'outputIsOpaque':True,'synchronizeInputs':False,'allowPartialOutputRegion':True,'allowCompressedInputsAndOutputs':False}
assert meta['process_ABI']=='B48@0:8@16@24@32^@40'
sizes=[(64,48),(16,12),(16,12),(16,12),(16,12),(32,24),(256,1),(32,32),(32,32)]
fixtures=[]
for i,(w,h)in enumerate(sizes):
    fmt_name=meta['input_formats'][i]['global_symbol'].get('name','unknown')
    alpha_only=any(tag in fmt_name for tag in['FormatA8','FormatA16','FormatAh','FormatAf'])
    values=[]
    for y in range(h):
        for x in range(w):
            u=(x+.5)/w;v=(y+.5)/h
            if i==0:rgb=[.16+.35*u,.13+.33*v,.12+.24*(u+v)/2];a=1.
            elif i==4:rgb=[.04+.5*u,.05+.4*v,.03+.45*(u+v)/2];a=1.
            else:
                q=1. if i==1 and x>=w//2 else 1. if i==2 and y>=h//2 else 1. if i==3 and (x//4+y//4)%2 else 0. if i in[1,2,3]else 1. if i==5 else x/(w-1)if i==6 else .7+.05*u if i==7 else .9+.05*v
                rgb=[q]*3;a=q if alpha_only else 1.
                if alpha_only:rgb=[0.,0.,0.]
            values.extend([*rgb,a])
    raw=struct.pack('<'+'f'*len(values),*values);name=f'input-{i}.rgba32f'
    with(I/name).open('xb')as f:f.write(raw)
    fixtures.append({'index':i,'file':name,'width':w,'height':h,'dtype':'<f4','channels':4,'sha256':hashlib.sha256(raw).hexdigest(),'original_requested_CIFormat_symbol':fmt_name,'source_alpha_only_contract_used':alpha_only})
base=[[0.,0.,float(w),float(h)]for w,h in sizes]
shift=[[128.*w/64,128.*h/48,float(w),float(h)]if i<=5 else[0.,0.,float(w),float(h)]for i,(w,h)in enumerate(sizes)]
geometries=[('full',base,[0.,0.,64.,48.]),('tile',base,[12.,8.,24.,20.]),('translated',shift,[128.,128.,64.,48.])]
cases=[{'id':f'{name}_lm{int(light)}_r{repeat}','geometry':name,'repeat':repeat,'extents':rects,'render':render,'useLightMap':light}for light in[True,False]for name,rects,render in geometries for repeat in[0,1]]
base_args={'useStyleEngine':True,'baseGain':1.,'faceBasedGlobalExposureBoostRatio':1.,'cast':0,'intensity':1.,'tone':.35,'color':0.,'srlCurveParameter':0.,'brightnessValue':0.,'tuningType':0,'sceneType':0}
resolved={s['unslid']:s.get('selector')for s in meta['optimized_selectors']}
scalar_value=8. if resolved.get('0x1d00b7bd0')in['setInputGainMapHeadroom:','setGainMapHeadroom:']else 1.
evaluation={**spec,'input_directory':str(I),'fixtures':fixtures,'cases':cases,'base_args':base_args,'extra_scalar_value':scalar_value}
with(W/'eval-spec.json').open('x')as f:json.dump(evaluation,f,separators=(',',':'))
save('freeze.json',{'recipe_sha256':sha(O/'recipe.json'),'metadata_sha256':sha(O/'metadata.json'),'fixtures':fixtures,'cases':cases,'base_args':base_args,'extra_scalar_control':{**meta['extra_scalar_key'],'setter_binding':resolved.get('0x1d00b7bd0'),'value':scalar_value,'controlled_synthetic_value_not_physical_calibration':True},'stats_absent_explicit_processing_type3':True,'original_stats_present_type2_not_claimed':True,'frozen_before_actual_CI_evaluation':True})
rc=run('evaluate',W/'eval-spec.json',240)
native=json.loads((O/'native.json').read_text())if(O/'native.json').exists()else{}
analysis={'native_returncode':rc,'native_completed':native.get('completed',False),'new_photos':0,'shader_or_residency_override':False,'A_phase_complete':False,'acceptance_complete':False,'original_stats_present_type2_validated':False,'full_33_point_C01_C05_certified':False}
if rc==0:
    assert native['metadata']==meta
    callbacks=native['callbacks'];rows=native['cases'];analysis['cases_completed']=len(rows);analysis['callback_count']=len(callbacks);analysis['compute_dispatch_count']=len(native['dispatches'])
    analysis['all_original_returns_yes']=all(r.get('original_return')is True for r in callbacks)
    analysis['all_source_bytes_SHA_unchanged']=all(r['source_RGBAf_SHA_unchanged']for r in rows)
    missing=[]
    for n,r in enumerate(callbacks):
        for i,item in enumerate(r.get('inputs',[])):
            if'file'not in item:missing.append({'callback':n,'input':i,'error':item.get('capture_error','missing readback')})
        if'file'not in r.get('output_readback',{}):missing.append({'callback':n,'output':True,'error':r.get('output_readback',{}).get('capture_error',r.get('readbacks_not_encoded','missing readback'))})
    analysis['missing_readbacks']=missing
    def floats(file):
        raw=(O/file).read_bytes();assert len(raw)%4==0;return list(struct.unpack('<'+'f'*(len(raw)//4),raw))
    def compare(a,b):
        assert len(a)==len(b)
        if not all(math.isfinite(x)and math.isfinite(y)for x,y in zip(a,b)):return{'finite':False,'max_abs':None,'PSNR_dB':None}
        maximum=max(abs(x-y)for x,y in zip(a,b));mse=sum((x-y)**2 for x,y in zip(a,b))/len(a)
        return{'finite':True,'max_abs':maximum,'PSNR_dB':'Infinity'if mse==0 else-10*math.log10(mse)}
    lookup={r['case']:r for r in rows};aa=[]
    for light in[True,False]:
        for geometry,_,_ in geometries:
            a=lookup[f'{geometry}_lm{int(light)}_r0'];b=lookup[f'{geometry}_lm{int(light)}_r1']
            comparison=compare(floats(a['CI_output']['file']),floats(b['CI_output']['file']))
            ar=callbacks[slice(*a['callback_range'])];br=callbacks[slice(*b['callback_range'])]
            half_equal=len(ar)==len(br)and all(x.get('output_readback',{}).get('dtype')==y.get('output_readback',{}).get('dtype')=='<f2'and x['output_readback'].get('sha256')==y['output_readback'].get('sha256')for x,y in zip(ar,br))
            aa.append({'geometry':geometry,'useLightMap':light,**comparison,'native_half_readback_byte_exact':half_equal})
    analysis['A_to_A']=aa;analysis['all_A_to_A_half_exact']=all(r['native_half_readback_byte_exact']for r in aa)
    analysis['all_A_to_A_CI_float_gate']=all(r['finite']and r['max_abs']<=1e-5 and(r['PSNR_dB']=='Infinity'or r['PSNR_dB']>=60)for r in aa)
    case_flags={r['id']:r['useLightMap']for r in cases}
    analysis['stats_setter_counts_by_callback']=[{'case':r['case'],'useLightMap':case_flags[r['case']],'ByStatsType':sum(s['selector']=='setInputStatisticsByStatsType:'for s in r.get('setters',[])),'ByStatsKey':sum(s['selector']=='setInputStatisticsByStatsKey:'for s in r.get('setters',[]))}for r in callbacks]
    analysis['stats_branch_observed']=all((r['ByStatsType']>=1 and r['ByStatsKey']>=1)if r['useLightMap']else(r['ByStatsType']==0 and r['ByStatsKey']==0)for r in analysis['stats_setter_counts_by_callback'])
    analysis['capture_gate_passed']=len(rows)==12 and bool(callbacks)and analysis['all_original_returns_yes']and analysis['all_source_bytes_SHA_unchanged']and not missing and analysis['all_A_to_A_half_exact']and analysis['all_A_to_A_CI_float_gate']and analysis['stats_branch_observed']and not native.get('setter_capture_limit',False)and not native.get('compute_capture_limit_reached',False)
save('analysis.json',analysis)
print(json.dumps({k:v for k,v in analysis.items()if k not in['A_to_A','missing_readbacks','stats_setter_counts_by_callback']}))
sys.exit(rc if rc else 0 if analysis.get('capture_gate_passed',False)else 1)
