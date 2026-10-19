"""Runner-only finite information-loss certificate for a float32 offset gain map.

This diagnoses a representation limit, not the whole consumer or its 33 points.
No photographed pixels, encrypted input, original inverse fitting or new mask.
"""
from pathlib import Path
from fractions import Fraction
import os,sys,json,hashlib,subprocess,struct,math
import numpy as np
W=Path(os.environ['W']);O=W/'out';T=W/'temporary';T.mkdir();D=Path('research/hdr-native')
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,v):p.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def bits(x):return struct.unpack('<I',struct.pack('<f',x))[0]
assert sys.platform=='darwin' and subprocess.check_output(['sw_vers','-buildVersion'],text=True).strip()=='26A434'
freeze={'scope':'Finite synthetic collision of target HDR values after float32 logmap and normalized texture; not a full-domain shader interval or real-photo counterfactual','os_build':'26A434','source':.125,'offset':.03125,'log_min':-8,'log_max':8,'target_grid':'10001 float32 values linearly spanning 1e-7 through 6e-7; group by both float32 log2 map and normalized code bits, choose first disjoint original-gate target intervals before native output','native_headrooms':[1,1.25,2,4,8],'unchanged_gate':{'relative_max':1e-3,'relative_denominator_floor':1e-6,'linear_max_abs':1e-5,'PSNR_peak1_db_min':60},'no_fit_to_native_output':True,'source_sha256':{p.name:sha(p) for p in [D/'run_hdr_s50.py',D/'offset_collision_s50.m',D/'hdr_headroom_s29.m']},'photos_used':False,'original_masks_changed':False,'original_frozen_files_changed':False}
save(O/'formula-freeze.json',freeze);frozen_sha=sha(O/'formula-freeze.json');S=freeze['source'];offset=freeze['offset'];lo=freeze['log_min'];hi=freeze['log_max']
groups={};FLOOR=Fraction.from_float(1e-6);GATE=Fraction.from_float(1e-3);pair=None
for value in np.linspace(1e-7,6e-7,10001,dtype='f8').astype('f4'):
    H=float(value);lg=np.float32(np.log2((np.float64(H)+offset)/(S+offset)));code=np.float32((np.float64(lg)-lo)/(hi-lo));key=(bits(lg),bits(code));groups.setdefault(key,[]).append((H,float(lg),float(code)))
for values in groups.values():
    a,b=values[0],values[-1];A=Fraction.from_float(a[0]);B=Fraction.from_float(b[0]);da=max(abs(A),FLOOR);db=max(abs(B),FLOOR)
    if B-A>GATE*(da+db):pair=(a,b,da,db);break
assert pair is not None,'No finite collision certified; do not announce an information bound'
a,b,da,db=pair;A=Fraction.from_float(a[0]);B=Fraction.from_float(b[0]);bound=(B-A)/(da+db)
cert={'targets':[{'float32':v[0],'target_bits':f'{bits(v[0]):08x}','stored_log2_float32':v[1],'stored_log2_bits':f'{bits(v[1]):08x}','normalized_code_float32':v[2],'normalized_code_bits':f'{bits(v[2]):08x}'} for v in [a,b]],'source':S,'common_offset':offset,'same_float32_logmap':bits(a[1])==bits(b[1]),'same_native_normalized_texture_code':bits(a[2])==bits(b[2]),'target_gate_intervals':[[str(A-GATE*da),str(A+GATE*da)],[str(B-GATE*db),str(B+GATE*db)]],'target_gate_intervals_disjoint':A+GATE*da<B-GATE*db,'minimax_relative_lower_bound_exact':str(bound),'minimax_relative_lower_bound':float(bound),'original_relative_gate':1e-3,'proof':'For identical source, metadata and stored gain, any single-valued reconstruction returns one value. Disjoint allowed target intervals imply at least one target fails the unchanged gate; lower bound=(H2-H1)/(d1+d2). This does not require a pow/fast-math error contract.','full_domain_consumer_certified':False,'skin_33_tight_hulls_certified':False,'native_observation_pending':True}
assert cert['same_float32_logmap'] and cert['same_native_normalized_texture_code'] and cert['target_gate_intervals_disjoint'] and bound>GATE
save(O/'finite-collision-certificate.json',cert)
def metadata(base_offset,gain_min,gain_max):
    channel=''.join('<rdf:li rdf:parseType="Resource">'+''.join(f'<h:{k}>{v:.9f}</h:{k}>' for k,v in [('GainMapMin',gain_min),('GainMapMax',gain_max),('Gamma',1),('BaseOffset',base_offset),('AlternateOffset',base_offset)])+'</rdf:li>' for _ in range(3))
    return '<x:xmpmeta xmlns:x="adobe:ns:meta/"><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"><rdf:Description xmlns:HDRToneMap="http://ns.apple.com/HDRToneMap/1.0/"><HDRToneMap:Version>1</HDRToneMap:Version><HDRToneMap:BaseHeadroom>0</HDRToneMap:BaseHeadroom><HDRToneMap:AlternateHeadroom>3</HDRToneMap:AlternateHeadroom><HDRToneMap:ChannelMetadata><rdf:Seq>'+channel.replace('h:','HDRToneMap:')+'</rdf:Seq></HDRToneMap:ChannelMetadata><HDRToneMap:BaseColorIsWorkingColor>True</HDRToneMap:BaseColorIsWorkingColor></rdf:Description></rdf:RDF></x:xmpmeta>'
cases=[]
for tag,o,mn,mx in [('common-offset',offset,lo,hi),('zero-offset-control',0.,-40.,8.)]:
    mp=T/(tag+'.xml');mp.write_text(metadata(o,mn,mx))
    for n,v in enumerate([a,b]):
        H=v[0];lg=v[1] if o else float(np.float32(np.log2(np.float64(H)/S)));code=float(np.float32((np.float64(lg)-mn)/(mx-mn)))
        cases.append({'id':tag+('-low' if n==0 else '-high'),'source':S,'target':H,'offset':o,'gain_min':mn,'gain_max':mx,'logmap_float32':lg,'gain_code':code,'metadata_file':str(mp),'temporary_output':str(T)})
save(T/'inputs.json',{'cases':cases});public_cases=[{k:v for k,v in c.items() if k not in ['temporary_output','metadata_file']} for c in cases];save(O/'input-scalars.json',public_cases)
flags=['clang','-O2','-fobjc-arc','-framework','Foundation','-framework','CoreImage','-framework','ImageIO','-framework','Metal','-framework','CoreGraphics']
with (O/'build.log').open('w') as log:subprocess.run(flags+[str(D/'offset_collision_s50.m'),'-o',str(W/'native')],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
with (O/'native.log').open('w') as log:subprocess.run([str(W/'native'),str(T/'inputs.json'),str(O/'native.json')],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
native=json.loads((O/'native.json').read_text());assert native['AppleFamily4'];lookup={x['id']:x for x in native['rows']};rows=[]
for c in cases:
    nr=lookup[c['id']];sweep=[]
    for sample in nr['headrooms']:
        raw=T/sample['file'];assert sha(raw)==sample['output_sha256'];v=np.fromfile(raw,dtype='<f4').reshape(8,8,4)[...,:3].astype('f8');weight=math.log2(sample['headroom'])/3
        code=c['gain_code'];trans=0. if code==0 else math.copysign(max(abs(code),1e-6),code);ev=c['gain_min']+(c['gain_max']-c['gain_min'])*trans
        expected=(S+c['offset'])*2**(weight*ev)-c['offset'];delta=abs(v-expected);target=c['target'] if sample['headroom']==8 else expected;error=abs(v-target);mse=float(np.square(error).mean());relative=float((error/max(abs(target),1e-6)).max());absolute=float(error.max());psnr=-10*math.log10(mse) if mse else 'inf'
        sweep.append({'headroom':sample['headroom'],'output_sha256':sample['output_sha256'],'first_RGB':[float(x) for x in v[0,0]],'nonfinite_components':int((~np.isfinite(v)).sum()),'stored_code_formula_max_abs':float(delta.max()),'stored_code_formula_max_relative':float((delta/max(abs(expected),1e-6)).max()),'target_at_full_else_formula':target,'target_max_abs':absolute,'target_max_relative':relative,'PSNR_peak1_db':psnr,'original_target_gate':relative<=1e-3 and absolute<=1e-5 and (psnr=='inf' or psnr>=60),'unencoded_h1_source_max_abs':float(abs(v-S).max()) if sample['headroom']==1 else None})
    rows.append({'id':c['id'],'native_input_facts':{k:nr[k] for k in ['source_texture_sha256','gain_texture_sha256','metadata_sha256']},'headrooms':sweep})
first,second=rows[:2];sameinputs=first['native_input_facts']==second['native_input_facts'];sameoutputs=all(x['output_sha256']==y['output_sha256'] for x,y in zip(first['headrooms'],second['headrooms']));assert sameinputs and sameoutputs
cert['native_observation_pending']=False;cert['native_identical_input_and_output_SHA']=True;save(O/'finite-collision-certificate.json',cert)
assert sha(O/'formula-freeze.json')==frozen_sha
analysis={'os_build':'26A434','image_version':os.environ.get('ImageVersion'),'synthetic_only':True,'photos_used':False,'formula_freeze_sha256':frozen_sha,'finite_collision_certificate_sha256':sha(O/'finite-collision-certificate.json'),'same_common_offset_native_inputs':sameinputs,'same_common_offset_native_outputs_all_headrooms':sameoutputs,'minimax_relative_lower_bound':float(bound),'rows':rows,'scope':'Finite positive near-zero example for this exact float32 representation. Native input collision is not a full-domain PSO/texture/fast/nonfinite proof, nor an attribution of all S47 photo failures. No original masks/gates or target photograph changed.','acceptance_complete':False,'A_phase_complete':False}
save(O/'analysis-s50.json',analysis);print(json.dumps({'completed':True,'minimax_relative_lower_bound':float(bound),'native_same_inputs_outputs':sameinputs and sameoutputs,'original_relative_gate':1e-3,'all_full_target_gates':[r['headrooms'][-1]['original_target_gate'] for r in rows],'acceptance_complete':False}))
