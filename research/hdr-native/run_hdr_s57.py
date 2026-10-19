"""Reuse S56, complete encrypted real-map compatibility, test original global PSO.

This does not render photographs or claim to invert the camera pipeline.
"""
from pathlib import Path
import ast,base64,hashlib,json,math,os,re,struct,subprocess,sys,zipfile
import numpy as np
from lightmap_model_s55 import encode_tail,decode_bucket_set,A,B,INV255
D=Path('research/hdr-native');W=Path(os.environ['W']);O=W/'out';PRIVATE=W/'private';SECURE=W/'secure'
F=np.float32;H=np.float16
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,j):
    with Path(p).open('x')as f:json.dump(j,f,indent=2,allow_nan=False);f.write('\n')
assert sys.platform=='darwin'and subprocess.check_output(['sw_vers','-buildVersion'],text=True).strip()=='26A434'
lib=Path('/System/Library/PrivateFrameworks/CMImaging.framework/Versions/A/Resources/default.metallib')
assert sha(lib)=='16a8a119e3e0ae1649d32b2bbc8ea9136cb757a8d1f3eb451025821901edff11'
freeze={'os_build':'26A434','image_version':os.environ.get('ImageVersion'),'metallib_sha256':sha(lib),'source_sha256':{p.name:sha(p)for p in[D/'run_hdr_s57.py',D/'global_gain_probe_s57.m',D/'global-gain-cases-s57.json',D/'lightmap_model_s55.py']},'old_269_native_histogram_cases_repeated':False,'new_image_rendering':False,'new_real_scalar_metadata_contexts':3,'old_thresholds_masks_models_unchanged':True,'input_cipher_sha256':sha(W/'input-maps.gpg')}
save(O/'formula-freeze-s57.json',freeze);frozen_sha=sha(O/'formula-freeze-s57.json')
# Read already captured native rows; never rerun or silently replace them.
oldzip=W/'s56-evidence.zip';assert sha(oldzip)=='f2674fa102e47d3115efcb7ee3ff11553f5e1b84de6775d15ec2a2f9a7d7c046'
with zipfile.ZipFile(oldzip)as z:
    manifest=json.loads(z.read('manifest.json'));assert manifest['run_id']=='39308719398'and manifest['commit']=='7b7b4725b26187e16ac0b8809a67d311e0ce681b'
    files={x['path']:x for x in manifest['files']}
    reused={}
    for name in ['native-histogram-s56.json','synthetic-analysis-s56.json']:
        raw=z.read(name);assert hashlib.sha256(raw).hexdigest()==files[name]['sha256'];reused[name]=json.loads(raw)
native=reused['native-histogram-s56.json'];syn=reused['synthetic-analysis-s56.json'];assert native['completed']and syn['half_gate_passed']and len(native['rows'])==269
save(O/'reuse-s56.json',{'run':'39308719398','artifact':'12214318554','zip_sha256':sha(oldzip),'verified_files':{n:files[n]['sha256']for n in reused},'native_cases_repeated':0,'prior_half_exact_cases':syn['half_bit_exact_cases']})
# Reuse the frozen normalizer reference alone, not the S56 executable module.
tree=ast.parse((D/'run_hdr_s56.py').read_text());nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='gtc_normalizer'];assert len(nodes)==1
exec(compile(ast.Module(body=nodes,type_ignores=[]),str(D/'run_hdr_s56.py'),'exec'),globals())
desc=json.loads((D/'transport-input-s56.json').read_text());cipher=W/'input-maps.gpg';assert sha(cipher)==desc['cipher_sha256']
key=os.environ.pop('HDR_S55_INPUT_SESSION');assert key.split(':',1)[0]=='9.2'
readfd,writefd=os.pipe();os.write(writefd,key.encode()+b'\n');os.close(writefd);plaintext=PRIVATE/'maps-input.json'
try:
    with plaintext.open('xb')as out,(SECURE/'decrypt.log').open('xb')as err:
        p=subprocess.run(['gpg','--batch','--override-session-key-fd',str(readfd),'--status-fd','2','--decrypt',str(cipher)],pass_fds=(readfd,),stdout=out,stderr=err,timeout=120)
finally:os.close(readfd);del key
events=re.findall(rb'\[GNUPG:\] ([A-Z_]+)',(SECURE/'decrypt.log').read_bytes())
receipt={'returncode':p.returncode,'events':[x.decode()for x in events],'plaintext_sha256_matches':sha(plaintext)==desc['plaintext_sha256'],'plaintext_size_matches':plaintext.stat().st_size==desc['plaintext_bytes'],'complete_algorithm_prefix':'9.2','private_archive_key_on_runner':False,'raw_decrypt_log_uploaded':False}
save(O/'transport-check-s57.json',receipt)
assert p.returncode==0 and b'DECRYPTION_OKAY'in events and receipt['plaintext_sha256_matches']and receipt['plaintext_size_matches']
payload=json.loads(plaintext.read_text());real=[]
for sample in payload['samples']:
    arrays={}
    for name,entry in sample['buffers'].items():
        raw=base64.b64decode(entry['base64'],validate=True);assert hashlib.sha256(raw).hexdigest()==entry['sha256'];arrays[name]=raw
    assert len(arrays['c'])==len(arrays['d'])==2048 and len(arrays['stats'])==10640 and len(arrays['params'])==672 and len(arrays['gtc'])==512
    stats=np.frombuffer(arrays['stats'],'<f4');params=np.frombuffer(arrays['params'],'<f4');table=np.frombuffer(arrays['gtc'],'<f2');cm=float(stats[10632//4]);lm=float(stats[10620//4]);base=float(params[6]);exp=float(params[7])
    conditions=bool(np.isfinite([cm,lm,base,exp]).all()and cm>0 and lm>0 and base>0 and exp>0)
    summary={'photo':sample['photo'],'source_capture_run':payload['source_capture_run'],'camera_statistics_binding_verified':False,'consumer_context_positive_finite':conditions,'buffers_sha256':{n:v['sha256']for n,v in sample['buffers'].items()},'spatial_values_or_bucket_grids_published':False,'maps':{}}
    dn=gtc_normalizer(lm,base,exp,'captured',table)if conditions else None
    summary['normalizers']={'captured_consumer_ltm_max':cm,'captured_consumer_lin_max':lm,'base_gain':base,'baseline_exposure':exp,'d_max_proxy_reference':dn}
    for name,norm in [('c',cm),('d',dn)]:
        vals=np.frombuffer(arrays[name],'<f2');bits=vals.view('<u2');domain=bool(norm is not None and np.isfinite(vals).all()and np.isfinite(norm)and norm>0)
        item={'finite_map_values':bool(np.isfinite(vals).all()),'domain_supported':domain,'map_elements':len(vals)}
        if domain:
            unique=np.unique(bits);sets={int(code):decode_bucket_set(int(code),norm)for code in unique};counts=[len(sets[int(b)])for b in bits]
            reference=np.asarray([encode_tail(norm,F(F(k)*INV255))for k in range(256)],dtype='<f2').astype('f8');dist=np.min(np.abs(vals.astype('f8')[:,None]-reference[None,:]),axis=1)
            proxy=(vals.astype('f8')/.29412-1.2-float(B))/float(A)
            item.update({'exact_code_compatible_elements':sum(n>0 for n in counts),'unique_bucket_elements':sum(n==1 for n in counts),'ambiguous_bucket_elements':sum(n>1 for n in counts),'incompatible_elements':sum(n==0 for n in counts),'nearest_reference_max_abs':float(dist.max()),'nearest_reference_MAE':float(dist.mean()),'decoded_proxy_quantiles':np.quantile(proxy,[0,.5,1]).tolist(),'proxy_is_not_scene_radiance':True})
        summary['maps'][name]=item
    real.append(summary)
save(O/'real-map-compatibility-s57.json',{'photos':real,'photos_with_scalar_metadata':len(real),'context_role':'captured consumer, not same-frame camera production','no_new_real_photo_pixel_processing':True,'not_full_inverse_accuracy':True})
# Global operator is a separate native PSO; no histogram dispatch is repeated.
with (O/'native-build.log').open('x')as log:subprocess.run(['clang','-O2','-fobjc-arc','-framework','Foundation','-framework','Metal',str(D/'global_gain_probe_s57.m'),'-o',str(W/'global-gain-probe')],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
with (O/'native-driver.log').open('x')as log:rc=subprocess.run([str(W/'global-gain-probe'),str(D/'global-gain-cases-s57.json'),str(O/'native-global-gain-s57.json')],stdout=log,stderr=subprocess.STDOUT,timeout=300).returncode
assert rc==0,'Inspect native checkpoint before revising or repeating'
n=json.loads((O/'native-global-gain-s57.json').read_text());assert n['completed']and n['PSO']['original_host_object']
cases=json.loads((D/'global-gain-cases-s57.json').read_text())['cases'];comparisons=[]
for c,row in zip(cases,n['rows'],strict=True):
    assert row['id']==c['id']and row['stats_SHA_unchanged']and row['outside_gain_changed_bytes']==0
    with np.errstate(all='ignore'):ref=F(F(c['avg_main'])/F(F(c['exposure'])*F(c['avg_linear'])))
    item={'id':c['id'],'declared_positive_finite_domain':c['domain']=='positive_finite','reference_finite':bool(np.isfinite(ref)),'native_finite':row['finite'],'native_bits':row['output_bits'],'reference_bits':int(np.asarray([ref],dtype='<f4').view('<u4')[0]),'out_of_contract_probe_only':c['domain']!='positive_finite'}
    if np.isfinite(ref)and row['finite']:item.update({'max_abs':abs(row['output']-float(ref)),'relative_error':abs(row['output']-float(ref))/max(abs(float(ref)),1e-30)})
    comparisons.append(item)
positive=[x for x in comparisons if x['declared_positive_finite_domain']]
save(O/'global-gain-analysis-s57.json',{'cases':comparisons,'positive_finite_cases':len(positive),'finite_domain_max_abs':max(x.get('max_abs',float('inf'))for x in positive),'finite_domain_max_relative':max(x.get('relative_error',float('inf'))for x in positive),'original_fast_math_pipeline':True,'synthetic_dispatch_only':True,'not_physical_exposure_calibration':True,'invalid_domain_probes_are_not_contract_proof':True})
assert sha(O/'formula-freeze-s57.json')==frozen_sha
save(O/'analysis-s57.json',{'os_build':'26A434','image_version':os.environ.get('ImageVersion'),'prior_native_histogram_cases_repeated':0,'prior_half_bit_exact_cases':syn['half_bit_exact_cases'],'real_metadata_contexts':len(real),'new_original_global_PSO_cases':len(cases),'all_external_buffers_unchanged_except_global_gain':True,'new_real_photo_pixel_processing':False,'old_models_masks_thresholds_changed':False,'camera_native_execution':False,'A_phase_complete':False,'acceptance_complete':False,'formula_freeze_sha256':frozen_sha})
print(json.dumps({'reused_native_cases':269,'real_metadata_contexts':len(real),'global_native_cases':len(cases),'new_real_photo_pixel_processing':False}))
