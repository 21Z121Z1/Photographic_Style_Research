"""Original scalar-map PSO on synthetic tiles, plus encrypted map compatibility.

Never uploads spatial values from real maps. Existing consumer captures are
not assumed to contain the camera's original statistical context.
"""
from pathlib import Path
import base64,hashlib,json,math,os,re,struct,subprocess,sys
import numpy as np
from lightmap_model_s55 import encode_tail,decode_bucket_set,A,B,INV255
R=Path.cwd();D=R/'research/hdr-native';W=Path(os.environ['W']);O=W/'out';PRIVATE=W/'private';SECURE=W/'secure'
assert sys.platform=='darwin' and subprocess.check_output(['sw_vers','-buildVersion'],text=True).strip()=='26A434'
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,j):
    with Path(p).open('x')as f:json.dump(j,f,indent=2,allow_nan=False);f.write('\n')
cases_path=D/'cases-s55.json';cases=json.loads(cases_path.read_text())['cases']
frozen={'source_modules_sha256':{p.name:sha(p)for p in[D/'run_hdr_s56.py',D/'histogram_probe_s56.m',D/'lightmap_model_s55.py',cases_path]},
    'cases':len(cases),'os_build':'26A434','image_version':os.environ.get('ImageVersion'),
    'scope':'Manual synthetic dispatch of the original host-retained histogram PSO, not the original full host process or native iOS camera',
    'model':'AIR0002 writer tail from quantized p50 plus explicit global normalizer; original gates/masks unchanged',
    'new_real_photograph_pixel_processing':False,'raw_maps_encrypted_in_transit':True,
    'source_AIR_sha256':sha(D/'evidence/s55/local-histogram-source.ll')}
save(O/'formula-freeze-s56.json',frozen);freeze_sha=sha(O/'formula-freeze-s56.json')

# S55 already exported AIR0/1; do not repeat extraction. Installed library
# identity is still checked before the original host-retained PSO executes.
lib=Path('/System/Library/PrivateFrameworks/CMImaging.framework/Versions/A/Resources/default.metallib')
lib_sha=sha(lib);assert lib_sha=='16a8a119e3e0ae1649d32b2bbc8ea9136cb757a8d1f3eb451025821901edff11'

with (O/'native-build.log').open('x')as log:
    subprocess.run(['clang','-O2','-fobjc-arc','-framework','Foundation','-framework','Metal',str(D/'histogram_probe_s56.m'),'-o',str(W/'native-histogram')],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
with (O/'native-driver.log').open('x')as log:
    rc=subprocess.run([str(W/'native-histogram'),str(cases_path),str(O/'native-histogram-s56.json')],stdout=log,stderr=subprocess.STDOUT,timeout=600).returncode
save(O/'native-status-s56.json',{'returncode':rc,'source_modules_sha256':frozen['source_modules_sha256']})
assert rc==0,'Read native checkpoint/exception before revising or repeating.'
native=json.loads((O/'native-histogram-s56.json').read_text());assert native['completed'] and len(native['rows'])==len(cases)
assert native['PSO']['original_host_object'] and not native['full_host_dispatch'] and native['AppleFamily4']
assert native['SRL_flag']['value']==0 and native['SRL_flag']['written']is False
F=np.float32;H=np.float16

def gtc_normalizer(linmax,base,exposure,curve,table=None):
    u=H(H(F(linmax)*F(base))*H(exposure));u=H(min(float(u),1))
    if table is None:
        values=np.linspace(0,1,256,dtype='f4');values=values*values if curve=='square' else values;table=values.astype('f2')
    x=F(H(u*H(len(table)-1)))
    lo=min(max(int(math.floor(float(x))),0),len(table)-1);hi=min(lo+1,len(table)-1);w=F(x-F(lo))
    return float(H(F(F(table[lo])+F(F(F(table[hi])-F(table[lo]))*w))))

predictions=[]
for case,row in zip(cases,native['rows'],strict=True):
    assert row['id']==case['id'] and row['inputs_and_external_context_SHA_unchanged']
    pc=float(row['local_p50_p98_by_histogram_index'][0][0]);pd=float(row['local_p50_p98_by_histogram_index'][7][0])
    dn=gtc_normalizer(case['lin_max'],case['base_gain'],case['baseline_exposure'],case['curve'])
    ch=int(np.asarray([encode_tail(case['ltm_max'],pc)],dtype='<f2').view('<u2')[0]);dh=int(np.asarray([encode_tail(dn,pd)],dtype='<f2').view('<u2')[0])
    cp=float(np.asarray([ch],dtype='<u2').view('<f2')[0]);dp=float(np.asarray([dh],dtype='<u2').view('<f2')[0])
    predictions.append({'id':case['id'],'c_native_bits':row['c_bits'],'d_native_bits':row['d_bits'],'c_predicted_bits':ch,'d_predicted_bits':dh,'c_bit_exact':ch==row['c_bits'],'d_bit_exact':dh==row['d_bits'],
        'tail_max_abs':max(abs(cp-row['c']),abs(dp-row['d'])) if 'c'in row and 'd'in row else None,
        'native_p50':[pc,pd],'d_normalizer_reference':dn,'c_bucket_candidates':decode_bucket_set(row['c_bits'],case['ltm_max']),'d_bucket_candidates':decode_bucket_set(row['d_bits'],dn)})
save(O/'synthetic-analysis-s56.json',{'ordered_reference_not_fitted':True,'cases':predictions,'half_bit_exact_cases':sum(x['c_bit_exact']and x['d_bit_exact']for x in predictions),'required_cases':len(predictions),'half_gate_passed':all(x['c_bit_exact']and x['d_bit_exact']for x in predictions),'max_abs':max((x['tail_max_abs']for x in predictions if x['tail_max_abs']is not None),default=None),'nonfinite_tail_cases':sum(x['tail_max_abs']is None for x in predictions),'no_full_pipeline_claim':True})

# Transport is encrypted even for the tiny real scalar maps. Key is scoped to
# this cipher only, never the archival private key. Nothing spatial is public.
desc=json.loads((D/'transport-input-s56.json').read_text());cipher=W/'input-maps.gpg';assert sha(cipher)==desc['cipher_sha256']
key=os.environ.pop('HDR_S55_INPUT_SESSION');readfd,writefd=os.pipe();os.write(writefd,key.encode()+b'\n');os.close(writefd)
plaintext=PRIVATE/'maps-input.json'
try:
    with plaintext.open('xb')as output,(SECURE/'decrypt.log').open('xb')as error:
        p=subprocess.run(['gpg','--batch','--override-session-key-fd',str(readfd),'--status-fd','2','--decrypt',str(cipher)],pass_fds=(readfd,),stdout=output,stderr=error,timeout=120)
finally:os.close(readfd);del key
events=re.findall(rb'\[GNUPG:\] ([A-Z_]+)',(SECURE/'decrypt.log').read_bytes());assert p.returncode==0 and b'GOODMDC'in events and b'DECRYPTION_OKAY'in events
assert sha(plaintext)==desc['plaintext_sha256'] and plaintext.stat().st_size==desc['plaintext_bytes']
payload=json.loads(plaintext.read_text());real=[]
for sample in payload['samples']:
    arrays={}
    for name,entry in sample['buffers'].items():
        raw=base64.b64decode(entry['base64'],validate=True);assert hashlib.sha256(raw).hexdigest()==entry['sha256'];arrays[name]=raw
    assert len(arrays['c'])==len(arrays['d'])==2048 and len(arrays['stats'])==10640 and len(arrays['params'])==672 and len(arrays['gtc'])==512
    stats=np.frombuffer(arrays['stats'],'<f4');params=np.frombuffer(arrays['params'],'<f4');table=np.frombuffer(arrays['gtc'],'<f2');cm=float(stats[10632//4]);lm=float(stats[10620//4]);base=float(params[6]);exp=float(params[7])
    conditions=bool(np.isfinite([cm,lm,base,exp]).all()and cm>0 and lm>0 and base>0 and exp>0)
    summary={'photo':sample['photo'],'classification':'已验证数值: compatibility against captured consumer context only; not same-frame camera production',
        'source_capture_run':payload['source_capture_run'],'camera_statistics_binding_verified':False,'consumer_context_positive_finite':conditions,'buffers_sha256':{n:v['sha256']for n,v in sample['buffers'].items()},'spatial_values_or_bucket_grids_published':False}
    if conditions:
        dn=gtc_normalizer(lm,base,exp,'captured',table)
        summary['normalizers']={'captured_consumer_ltm_max':cm,'captured_consumer_lin_max':lm,'base_gain':base,'baseline_exposure':exp,'d_max_proxy_reference':dn}
        summary['maps']={}
        for name,norm in [('c',cm),('d',dn)]:
            vals=np.frombuffer(arrays[name],'<f2');bits=vals.view('<u2');domain=bool(np.isfinite(vals).all()and np.isfinite(norm)and norm>0)
            item={'finite_map_values':bool(np.isfinite(vals).all()),'domain_supported':domain,'map_elements':len(vals)}
            if domain:
                unique=np.unique(bits);sets={int(code):decode_bucket_set(int(code),norm)for code in unique};counts=[len(sets[int(b)])for b in bits]
                reference=np.asarray([encode_tail(norm,F(F(k)*INV255))for k in range(256)],dtype='<f2').astype('f8');dist=np.min(np.abs(vals.astype('f8')[:,None]-reference[None,:]),axis=1)
                proxy=(vals.astype('f8')/.29412-1.2-float(B))/float(A)
                item.update({'exact_code_compatible_elements':sum(n>0 for n in counts),'unique_bucket_elements':sum(n==1 for n in counts),'ambiguous_bucket_elements':sum(n>1 for n in counts),'incompatible_elements':sum(n==0 for n in counts),'nearest_reference_max_abs':float(dist.max()),'nearest_reference_MAE':float(dist.mean()),'decoded_proxy_quantiles':np.quantile(proxy,[0,.5,1]).tolist(),'proxy_is_not_scene_radiance':True})
            summary['maps'][name]=item
    real.append(summary)
save(O/'real-map-compatibility-s56.json',{'photos':real,'photos_with_scalar_metadata':len(real),'no_new_real_photo_pixel_processing':True,'producer_identity_not_proven':True,'not_full_inverse_accuracy':True,'decrypt_events':[x.decode()for x in events],'plaintext_sha256_verified':True})
assert sha(O/'formula-freeze-s56.json')==freeze_sha
save(O/'analysis-s56.json',{'os_build':'26A434','image_version':os.environ.get('ImageVersion'),'metallib_sha256':lib_sha,'native_synthetic_cases':len(predictions),'new_real_scalar_map_contexts':len(real),'original_half_gate_passed_for_tail':all(x['c_bit_exact']and x['d_bit_exact']for x in predictions),'original_external_context_SHA_unchanged':True,'reference_model_fitted':False,'old_models_or_masks_changed':False,'native_iOS_camera_executed':False,'physical_scene_inverse_certified':False,'A_phase_complete':False,'acceptance_complete':False,'formula_freeze_sha256':freeze_sha})
print(json.dumps({'synthetic_cases':len(predictions),'tail_half_bit_exact_cases':sum(x['c_bit_exact']and x['d_bit_exact']for x in predictions),'real_map_metadata_contexts':len(real),'no_spatial_real_data_uploaded':True}))
