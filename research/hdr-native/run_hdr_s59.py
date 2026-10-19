"""Original histogram PSO at six S58 candidate scales, 256 buckets each.

Native finite candidate compatibility is separate from full-domain scale
uniqueness under the ordered reference, and from camera production identity.
"""
from pathlib import Path
import base64,hashlib,json,os,re,subprocess,sys
import numpy as np
from lightmap_model_s55 import encode_tail,INV255
D=Path('research/hdr-native');W=Path(os.environ['W']);O=W/'out';F=np.float32;H=np.float16
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,j):
    with Path(p).open('x')as f:json.dump(j,f,indent=2,allow_nan=False);f.write('\n')
assert sys.platform=='darwin'and subprocess.check_output(['sw_vers','-buildVersion'],text=True).strip()=='26A434'
lib=Path('/System/Library/PrivateFrameworks/CMImaging.framework/Versions/A/Resources/default.metallib');assert sha(lib)=='16a8a119e3e0ae1649d32b2bbc8ea9136cb757a8d1f3eb451025821901edff11'
spec=json.loads((D/'candidate-scales-s59.json').read_text());cases=[]
for photo in spec['photos']:
    for k in range(256):
        cases.append({'id':photo['photo']+'/'+str(k),'main_left':float(F(F(photo['c_normalizer'])*F(k/256))),'main_right':float(F(F(photo['c_normalizer'])*F(k/256))),'linear_left':k/256,'linear_right':k/256,'curve':'scaled-identity','curve_scale':photo['d_normalizer'],'ltm_max':photo['c_normalizer'],'lin_max':1,'base_gain':1,'baseline_exposure':1,'person':0,'skin':0})
save(W/'private/synthetic-cases.json',{'cases':cases})
freeze={'os_build':'26A434','image_version':os.environ.get('ImageVersion'),'metallib_sha256':sha(lib),'source_sha256':{p.name:sha(p)for p in[D/'run_hdr_s59.py',D/'histogram_probe_s59.m',D/'candidate-scales-s59.json',D/'lightmap_model_s55.py']},'candidate_scales_inferred_on_same_samples':True,'not_heldout_validation':True,'native_synthetic_cases':len(cases),'frozen_cases_sha256':sha(W/'private/synthetic-cases.json'),'source_S58_run':'39311415530','scope':'Original host-retained stats PSO; new synthetic bindings, candidate normals; not camera or full host execution','old_269_native_cases_repeated':False}
save(O/'formula-freeze-s59.json',freeze);frozen_sha=sha(O/'formula-freeze-s59.json')
with (O/'native-build.log').open('x')as log:subprocess.run(['clang','-O2','-fobjc-arc','-framework','Foundation','-framework','Metal',str(D/'histogram_probe_s59.m'),'-o',str(W/'histogram-probe')],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
with (O/'native-driver.log').open('x')as log:rc=subprocess.run([str(W/'histogram-probe'),str(W/'private/synthetic-cases.json'),str(O/'native-candidate-codebooks-s59.json')],stdout=log,stderr=subprocess.STDOUT,timeout=600).returncode
assert rc==0,'Read native checkpoint before revising or repeating'
native=json.loads((O/'native-candidate-codebooks-s59.json').read_text());assert native['completed']and native['PSO']['original_host_object']and len(native['rows'])==768
codebooks={};different=0
for case,row in zip(cases,native['rows'],strict=True):
    assert row[0]==case['id']and row[5];photo=case['id'].split('/')[0]
    for name,norm,idx,pindex in [('c',case['ltm_max'],1,3),('d',case['curve_scale'],2,4)]:
        bucket=int(round(row[pindex]*255));assert 0<=bucket<=255
        table=codebooks.setdefault((photo,name),{});bits=int(row[idx]);assert bucket not in table or table[bucket]==bits;table[bucket]=bits
        pred=int(np.asarray([encode_tail(norm,F(F(bucket)*INV255))],dtype='<f2').view('<u2')[0]);different+=pred!=bits
coverage={p+'/'+name:len(table)for(p,name),table in codebooks.items()}
assert all(n==256 for n in coverage.values()),'New native codebook missing bucket; no unobserved code inferred'
# Original encrypted scalar maps, still no photograph/image rendering.
desc=json.loads((D/'transport-input-s56.json').read_text());cipher=W/'input-maps.gpg';assert sha(cipher)==desc['cipher_sha256'];key=os.environ.pop('HDR_S55_INPUT_SESSION');assert key.split(':',1)[0]=='9.2';rd,wr=os.pipe();os.write(wr,key.encode()+b'\n');os.close(wr)
try:
    with (W/'private/maps.json').open('xb')as out,(W/'secure/decrypt.log').open('xb')as err:p=subprocess.run(['gpg','--batch','--override-session-key-fd',str(rd),'--status-fd','2','--decrypt',str(cipher)],pass_fds=(rd,),stdout=out,stderr=err,timeout=120)
finally:os.close(rd);del key
events=re.findall(rb'\[GNUPG:\] ([A-Z_]+)',(W/'secure/decrypt.log').read_bytes());receipt={'returncode':p.returncode,'events':[x.decode()for x in events],'plaintext_sha256_matches':sha(W/'private/maps.json')==desc['plaintext_sha256'],'plaintext_size_matches':(W/'private/maps.json').stat().st_size==desc['plaintext_bytes']};save(O/'transport-check-s59.json',receipt)
assert p.returncode==0 and b'DECRYPTION_OKAY'in events and receipt['plaintext_sha256_matches']and receipt['plaintext_size_matches']
payload=json.loads((W/'private/maps.json').read_text());rows=[]
for sample in payload['samples']:
    for name in ['c','d']:
        entry=sample['buffers'][name];raw=base64.b64decode(entry['base64'],validate=True);assert hashlib.sha256(raw).hexdigest()==entry['sha256'];bits=np.frombuffer(raw,'<u2');table=codebooks[(sample['photo'],name)];inverse={}
        for k,code in table.items():inverse.setdefault(code,[]).append(k)
        count=np.asarray([len(inverse.get(int(code),[]))for code in bits]);rows.append({'photo':sample['photo'],'map':name,'native_histogram_buckets_covered':len(table),'encoded_map_elements':len(bits),'native_code_compatible_elements':int((count>0).sum()),'unique_bucket_elements':int((count==1).sum()),'ambiguous_bucket_elements':int((count>1).sum()),'uncovered_elements':int((count==0).sum()),'input_map_sha256':entry['sha256'],'spatial_values_or_bucket_grids_published':False,'not_scene_pixel_preimages':True})
save(O/'candidate-native-compatibility-s59.json',{'rows':rows,'new_native_cases':768,'native_codebook_buckets':coverage,'reference_tail_different_components':different,'required_half_different_components':0,'half_gate_passed_for_this_tail':different==0,'all_encoded_map_elements_have_native_code_preimage':all(x['uncovered_elements']==0 for x in rows),'original_input_context_SHA_unchanged':True,'candidate_scale_native_compatibility_only':True,'global_scale_uniqueness_still_reference_conditional':True,'camera_production_identity_proven':False,'not_scene_linear_reconstruction':True})
assert sha(O/'formula-freeze-s59.json')==frozen_sha
save(O/'analysis-s59.json',{'os_build':'26A434','image_version':os.environ.get('ImageVersion'),'original_host_PSO':True,'new_native_cases':768,'all_six_256_bucket_codebooks_observed':True,'old_native_269_cases_repeated':False,'full_host_or_camera_executed':False,'new_photograph_pixel_processing':False,'native_compatibility_of_S58_candidate_scales':all(x['uncovered_elements']==0 for x in rows),'native_half_tail_gate_passed':different==0,'old_models_thresholds_masks_changed':False,'A_phase_complete':False,'acceptance_complete':False,'formula_freeze_sha256':frozen_sha})
print(json.dumps({'native_cases':768,'tail_different_components':different,'compatible_map_elements':sum(x['native_code_compatible_elements']for x in rows),'map_elements':sum(x['encoded_map_elements']for x in rows)}))
