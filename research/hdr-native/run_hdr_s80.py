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
spec={'native_selector_targets':targets['optimized_selector_stubs'],'ordered_stats':True}
with(W/'meta-spec.json').open('x')as f:json.dump(spec,f)
files=[D/n for n in['probe_consumer_ci_s80.m','ci_trace_s77.inc','ci_status_s80.inc','stats_context_s79.inc','analyze_ci_s77.py','run_hdr_s80.py','probe_consumer_roi_s73.m','probe_consumer_bindings_s72.m','probe_headroom_s66.m']]
files +=[D/'evidence/s75/native-targets.json',D/'evidence/s75/source-flow.json']
resources=[]
for p in[Path('/System/Library/PrivateFrameworks/CMImaging.framework/Resources/default.metallib'),Path('/System/Library/PrivateFrameworks/CMImaging.framework/Versions/A/Resources/default.metallib')]:
    if p.is_file():resources.append({'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'binary_not_uploaded':True})
recipe={'probe_version':'S80','S75_failed_before_native':{'run_id':39387345347,'artifact_id':12248270752,'reason':'SDK lacks NSValue valueWithCGRect constructor declaration; portable valueWithBytes/getValue used only for observer geometry storage'},'os_build':'26A434','image_version':os.environ.get('ImageVersion'),'source_sha256':{str(p):sha(p)for p in files},'derived_prefix_sha256':{p.name:sha(p)for p in[W/'consumer_cpu_prefix_s73.inc',W/'consumer_cpu_prefix_s75.inc']},'resources':resources,'test_plan_frozen_before_compile_and_native':'S80 freezes ordered S79 synthetic stats profile, original type2, full-size skin/sky and low-resolution person, unchanged GTC/maps/main/linear inputs. Three declared geometries full/tile/translated each A/A. Correct only observer quoted-field encoding normalization, verify native CGRect/CGSize size/alignment before read. Compare whole vs translated bytes, and report both predeclared vertical-row crop hypotheses for tile, each with independent input-texture match; never select output-best hypothesis. No original shader/math/return/check/residency change.','scope':'S80 actual original type2 geometry and finite sampling diagnostic, canonical original stats from fixed synthetic profile. Original A/A gates maintained. No photo/camera/scene/33-point global certificate and no old model change.','CPU_layout_contract':'CPU format/bytesPerRow/baseAddress are not used to interpret unsynchronized Metal textures. Actual MTL pixelFormat/extent recorded; blit stride separate.','API_sources':['https://developer.apple.com/documentation/coreimage/ciimageprocessorinput','https://developer.apple.com/documentation/coreimage/ciimageprocessorkernel','https://developer.apple.com/documentation/coreimage/ciimageprocessorkernel/synchronizeinputs','https://developer.apple.com/documentation/coreimage/ciimageprocessoroutput/metalcommandbuffer'],'gates':{'A_to_A_original_half_bytes':'exact','CI_float_gate_max_abs':1e-5,'CI_float_gate_PSNR_dB':60,'old_1e_3_masks_and_full_domain_unchanged':True},'A_phase_complete':False,'acceptance_complete':False}
save('recipe.json',recipe)
with(O/'build.log').open('x')as log:
    subprocess.run(['clang','-I',str(D),'-I',str(W),'-O2','-fobjc-arc','-fblocks','-framework','Foundation','-framework','CoreFoundation','-framework','CoreGraphics','-framework','CoreImage','-framework','Metal',str(D/'probe_consumer_ci_s80.m'),'-o',str(W/'probe')],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240)
def run(mode,spec_path,timeout,output=None,tag=None):
    output=O if output is None else output;tag=mode if tag is None else tag
    with(O/(tag+'.log')).open('x')as log:
        proc=subprocess.Popen([str(W/'probe'),mode,str(spec_path),str(output)],stdout=log,stderr=subprocess.STDOUT)
        try:return proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            # An observation timeout is not process termination: inspect SAME handle.
            live=proc.poll()is None
            save(tag+'-timeout.json',{'pid':proc.pid,'still_live_on_same_handle':live,'observation_timeout_seconds':timeout,'not_restarted':True})
            if live:
                with(O/(tag+'-live-stack.log')).open('x')as stack:
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
sizes=[(64,48),(16,12),(64,48),(64,48),(16,12),(32,24),(256,1),(32,32),(32,32)]
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
                q=1. if i==1 and x>=w//2 else 1. if i==2 and y>=h//2 else 1. if i==3 and (x//16+y//16)%2 else 0. if i in[1,2,3]else 1. if i==5 else x/(w-1)if i==6 else .7+.05*u if i==7 else .9+.05*v
                rgb=[q]*3;a=q if alpha_only else 1.
                if alpha_only:rgb=[0.,0.,0.]
            values.extend([*rgb,a])
    raw=struct.pack('<'+'f'*len(values),*values);name=f'input-{i}.rgba32f'
    with(I/name).open('xb')as f:f.write(raw)
    fixtures.append({'index':i,'file':name,'width':w,'height':h,'dtype':'<f4','channels':4,'sha256':hashlib.sha256(raw).hexdigest(),'original_requested_CIFormat_symbol':fmt_name,'source_alpha_only_contract_used':alpha_only})
base=[[0.,0.,float(w),float(h)]for w,h in sizes]
shift=[[128.*w/64,128.*h/48,float(w),float(h)]if i<=5 else[0.,0.,float(w),float(h)]for i,(w,h)in enumerate(sizes)]
geometries=[('full',base,[0.,0.,64.,48.]),('tile',base,[12.,8.,24.,20.]),('translated',shift,[128.,128.,64.,48.])]
cases=[{'id':f'{name}_lm{int(light)}_r{repeat}','geometry':name,'repeat':repeat,'extents':rects,'render':render,'useLightMap':light}for light in[True]for name,rects,render in geometries for repeat in[0,1]]
base_args={'useStyleEngine':True,'baseGain':1.,'faceBasedGlobalExposureBoostRatio':1.,'cast':0,'intensity':1.,'tone':.35,'color':0.,'srlCurveParameter':0.,'brightnessValue':0.,'tuningType':0,'sceneType':0}
resolved={s['unslid']:s.get('selector')for s in meta['optimized_selectors']}
scalar_value=8. if resolved.get('0x1d00b7bd0')in['setInputGainMapHeadroom:','setGainMapHeadroom:']else 1.
evaluation={**spec,'input_directory':str(I),'fixtures':fixtures,'cases':cases,'base_args':base_args,'extra_scalar_value':scalar_value}
with(W/'eval-spec.json').open('x')as f:json.dump(evaluation,f,separators=(',',':'))
save('freeze.json',{'recipe_sha256':sha(O/'recipe.json'),'metadata_sha256':sha(O/'metadata.json'),'fixtures':fixtures,'cases':cases,'base_args':base_args,'extra_scalar_control':{**meta['extra_scalar_key'],'setter_binding':resolved.get('0x1d00b7bd0'),'value':scalar_value,'controlled_synthetic_value_not_physical_calibration':True},'stats_present_explicit_processing_type2':True,'synthetic_stats_only_not_actual_photo_context':True,'frozen_before_actual_CI_evaluation':True})

import runpy
helpers=runpy.run_path(str(D/'analyze_ci_s77.py'));analyze=helpers['analyze'];values=helpers['values'];metrics=helpers['metrics']
save('spatial-plan.json',{'frozen_before_oracle':True,'ordered_stats':True,'same_S79_fixtures':True,'tile_bounds':[12,8,24,20],'storage_row_crop_hypotheses':[8,20],'input_crop_matches_are_diagnostics_not_a_universal_orientation_contract':True,'no_output_best_hypothesis_selection':True,'A_phase_complete':False,'acceptance_complete':False})
rc=run('evaluate',W/'eval-spec.json',240)
native=json.loads((O/'native.json').read_text())if(O/'native.json').is_file()else{}
audit=analyze(O)if native else{}
callbacks=native.get('callbacks',[]);rows=native.get('cases',[]);lookup={r['case']:r for r in rows}
def blob(item):
    raw=(O/item['file']).read_bytes();assert hashlib.sha256(raw).hexdigest()==item['sha256'];return raw
def crop(raw,w,x,y,cw,ch,bpp):return b''.join(raw[((y+j)*w+x)*bpp:((y+j)*w+x+cw)*bpp]for j in range(ch))
spatial=[]
if 'full_lm1_r0'in lookup:
    full=lookup['full_lm1_r0'];fcb=callbacks[full['callback_range'][0]]
    if'translated_lm1_r0'in lookup:
        shifted=lookup['translated_lm1_r0'];scb=callbacks[shifted['callback_range'][0]]
        spatial.append({'comparison':'whole_vs_translated','CI_float':metrics(values(O,full['CI_output']),values(O,shifted['CI_output'])),'original_half_byte_exact':blob(fcb['output_readback'])==blob(scb['output_readback']),'input0_half_byte_exact':blob(fcb['inputs'][0])==blob(scb['inputs'][0])})
    if'tile_lm1_r0'in lookup:
        tile=lookup['tile_lm1_r0'];tcb=callbacks[tile['callback_range'][0]]
        for y in[8,20]:
            fbytes=crop(blob(fcb['output_readback']),64,12,y,24,20,8);tbytes=blob(tcb['output_readback'])
            a=[x[0]for x in struct.iter_unpack('<e',fbytes)];b=[x[0]for x in struct.iter_unpack('<e',tbytes)]
            rgb_a=[v for i,v in enumerate(a)if i%4<3];rgb_b=[v for i,v in enumerate(b)if i%4<3]
            spatial.append({'comparison':'whole_crop_vs_tile','storage_row_start':y,'independent_input0_crop_byte_exact':crop(blob(fcb['inputs'][0]),64,12,y,24,20,8)==blob(tcb['inputs'][0]),'native_half_bytes_equal':fbytes==tbytes,'native_RGB_metrics':metrics(rgb_a,rgb_b),'hypothesis_not_selected_by_output_error':True})
geometry=[]
for record in native.get('original_status_methods',[]):
    if record['selector']not in['process','_checkROISpecification']:continue
    for when in['state_before','state_after']:
        items=[r for r in record.get(when,{}).get('ivars',[])if 'canonical_type'in r]
        geometry.append({'case':record['case'],'method':record['selector'],'when':when,'geometric_ivars':len(items),'all_ABI_sizes_and_alignments_verified':all(r['measured_size']in[16,32]and r['measured_alignment']==8 for r in items)})
missing=[{'case':r['case'],'input':i}for r in callbacks for i,t in enumerate(r.get('inputs',[]))if'file'not in t]
missing +=[{'case':r['case'],'output':True}for r in callbacks if'file'not in r.get('output_readback',{})]
aa=audit.get('A_to_A',[])
summary={**audit,'native_returncode':rc,'expected_cases':6,'geometry_capture':geometry,'spatial_diagnostics':spatial,'missing_readbacks':missing,'capture_limit':native.get('compute_capture_limit_reached',False),'stats_SHA_unchanged':bool(rows)and all(r.get('stats_SHA_unchanged',False)for r in rows),'original_stats_roundtrip':native.get('synthetic_stats_context',{}).get('global90_and_extended2_f32_original_roundtrip_exact',False),'new_photos':0,'A_phase_complete':False,'acceptance_complete':False}
summary['all_AA_original_half_exact']=len(aa)==3 and all(r['original_half_byte_exact']for r in aa)
summary['all_AA_float_original_gate']=len(aa)==3 and all(r['finite']and r['max_abs']<=1e-5 and(r['PSNR_dB']=='Infinity'or r['PSNR_dB']>=60)for r in aa)
summary['geometry_readback_ABI_complete']=len(geometry)>0 and all(r['geometric_ivars']>0 and r['all_ABI_sizes_and_alignments_verified']for r in geometry)
summary['finite_nonzero_original_RGB']=bool(audit.get('populations',[]))and all(r['nonfinite']==0 and r['RGB_nonzero']>0 for r in audit.get('populations',[])if r['buffer']=='original_MTL_output')
summary['finite_synthetic_CI_capture_gate']=rc==0 and len(rows)==6 and len(callbacks)==6 and all(r.get('original_return')is True for r in callbacks)and not missing and summary['stats_SHA_unchanged']and summary['all_AA_original_half_exact']and summary['all_AA_float_original_gate']and summary['geometry_readback_ABI_complete']and summary['finite_nonzero_original_RGB']and summary.get('renderFinalAdjustments_dispatches_observed',0)>=6 and not summary['capture_limit']
save('analysis.json',summary);print(json.dumps({k:v for k,v in summary.items()if k not in['populations','status_returns','A_to_A','geometry_capture']}));sys.exit(0 if summary['finite_synthetic_CI_capture_gate']else rc if rc else 1)
