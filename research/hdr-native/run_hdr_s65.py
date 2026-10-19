"""Diagnose scalar c-map disagreements, not a camera or scene inverse.

Reuse S56/S59 native codebooks and S63 captures. Only one previously untested
normalizer receives new synthetic native controls. No photographs are rendered.
"""
from pathlib import Path
import contextlib,hashlib,io,json,os,re,struct,subprocess,sys,tarfile,zipfile
import numpy as np
R=Path.cwd();D=R/'research/hdr-native';W=Path(os.environ['W']);O=W/'out';PRIVATE=W/'private'
sys.path[:0]=[str(R),str(R/'research/vm-native'),str(D)]
from extract_inputs import extract
from lightmap_model_s55 import encode_tail,INV255
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,j):
    with Path(p).open('x')as f:json.dump(j,f,indent=2,allow_nan=False);f.write('\n')
assert sys.platform=='darwin'and subprocess.check_output(['sw_vers','-buildVersion'],text=True).strip()=='26A434'
assert sha('/System/Library/PrivateFrameworks/CMImaging.framework/Versions/A/Resources/default.metallib')=='16a8a119e3e0ae1649d32b2bbc8ea9136cb757a8d1f3eb451025821901edff11'
archive=W/'S63.zip';assert sha(archive)=='77d121caf0eb5a095107fc412a215c6da5946ac0ab94b008a55575da7a4ae153'
with zipfile.ZipFile(archive)as z:
    m=json.loads(z.read('manifest.json'));assert m['run_id']=='39324317293'and m['commit']=='be2f2605c7a14ff0366adef87738c8c3122c0f3b'
    for x in m['files']:assert hashlib.sha256(z.read(x['path'])).hexdigest()==x['sha256']
    inv=json.loads(z.read('encrypted-inventory-s63.json'));cipher=z.read(inv['file']);assert hashlib.sha256(cipher).hexdigest()==inv['cipher_sha256']
    summaries={json.loads(z.read(n))['photo']:json.loads(z.read(n))for n in z.namelist()if n.endswith('-summary.json')}
    with(PRIVATE/'capture.gpg').open('xb')as f:f.write(cipher)
observed=json.loads((D/'evidence/s65/observed-codebooks.json').read_text());old=observed['tables'];NEW_M=.9912109375
assert summaries['IMG_2608']['basic_stats']['main_min_max_avg'][1]==NEW_M
assert all(x['basic_stats']['main_min_max_avg'][1]==1 for n,x in summaries.items()if n!='IMG_2608')
cases=[{'id':'new-normalizer/'+str(k),'main_left':float(np.float32(np.float32(NEW_M)*np.float32(k/256))),'main_right':float(np.float32(np.float32(NEW_M)*np.float32(k/256))),'linear_left':k/256,'linear_right':k/256,'curve':'scaled-identity','curve_scale':1,'ltm_max':NEW_M,'lin_max':1,'base_gain':1,'baseline_exposure':1,'person':0,'skin':0}for k in range(256)]
save(PRIVATE/'cases.json',{'cases':cases})
freeze={'os_build':'26A434','image_version':os.environ.get('ImageVersion'),'source_S63_run':'39324317293','source_S63_ZIP_sha256':sha(archive),'observed_codebooks_sha256':sha(D/'evidence/s65/observed-codebooks.json'),'new_native_cases':256,'new_native_normalizer':NEW_M,'new_M_is_measured_S63_reconstruction_stat_not_file_fit':True,'reused_M1_run':'39308719398','reused_original_conditional_scale_run':'39312021801','source_sha256':{p.name:sha(p)for p in[D/'run_hdr_s65.py',D/'histogram_probe_s59.m',D/'lightmap_model_s55.py']},'all_five_photos_previously_seen':'No new five-photo/heldout inverse acceptance claimed','native_photo_stats_or_pixel_rendering_repeated':False,'old_thresholds_masks_unchanged':True,'decomposition_orders':['change_normalizer_at_native_bucket_then_bucket_at_file_normalizer','change_bucket_at_native_normalizer_then_normalizer_at_file_bucket'],'not_physical_global_local_operator_decomposition':True}
save(O/'diagnostic-freeze-s65.json',freeze);frozen_sha=sha(O/'diagnostic-freeze-s65.json')
# Check encrypted input before doing new native work; private archive key absent.
key=os.environ.pop('HDR_S65_S63_SESSION');assert key.split(':',1)[0]=='9.2';rd,wr=os.pipe();os.write(wr,key.encode()+b'\n');os.close(wr)
try:
    with(PRIVATE/'captures.tar.gz').open('xb')as out,(PRIVATE/'decrypt.log').open('xb')as err:q=subprocess.run(['gpg','--batch','--override-session-key-fd',str(rd),'--status-fd','2','--decrypt',str(PRIVATE/'capture.gpg')],pass_fds=(rd,),stdout=out,stderr=err,timeout=120)
finally:os.close(rd);del key
events=[x.decode()for x in re.findall(rb'\[GNUPG:\] ([A-Z_]+)',(PRIVATE/'decrypt.log').read_bytes())];ok=sha(PRIVATE/'captures.tar.gz')==inv['plaintext_tar_sha256']
save(O/'transport-check-s65.json',{'returncode':q.returncode,'events':events,'plaintext_tar_SHA_matches':ok,'archive_private_key_on_runner':False});assert q.returncode==0 and'DECRYPTION_OKAY'in events and ok
expected={x['path']:x for x in inv['plaintext_members']};captures={}
with tarfile.open(PRIVATE/'captures.tar.gz','r:gz')as t:
    for member in t:
        assert member.isfile()and member.size<60000;raw=t.extractfile(member).read()
        if member.name=='manifest.json':continue
        assert member.name in expected and len(raw)==expected[member.name]['size']and hashlib.sha256(raw).hexdigest()==expected[member.name]['sha256'];captures[member.name]=raw
assert set(captures)==set(expected)
with(O/'native-build.log').open('x')as f:subprocess.run(['clang','-O2','-fobjc-arc','-framework','Foundation','-framework','Metal',str(D/'histogram_probe_s59.m'),'-o',str(W/'probe')],stdout=f,stderr=subprocess.STDOUT,check=True,timeout=180)
with(O/'native-driver.log').open('x')as f:q=subprocess.run([str(W/'probe'),str(PRIVATE/'cases.json'),str(O/'native-new-scale-s65.json')],stdout=f,stderr=subprocess.STDOUT,timeout=600)
assert q.returncode==0,'New control failed; inspect native checkpoint, do not repeat old cases'
native=json.loads((O/'native-new-scale-s65.json').read_text());assert native['completed']and native['PSO']['original_host_object']and len(native['rows'])==256
new_table={};tail_diff=0
for case,row in zip(cases,native['rows'],strict=True):
    assert row[0]==case['id']and row[5];k=int(round(row[3]*255));assert 0<=k<=255 and k not in new_table;new_table[k]=row[1]
    pred=np.asarray([encode_tail(NEW_M,np.float32(np.float32(k)*INV255))],dtype='<f2').view('<u2')[0];tail_diff+=int(pred)!=row[1]
assert set(new_table)==set(range(256))
tables={1.:old['native_main_M1']['codes_by_bucket'],NEW_M:[new_table[k]for k in range(256)]}
def inverse(table):
    d={}
    for k,code in enumerate(table):d.setdefault(code,[]).append(k)
    return d
def floats(table):return np.asarray(table,dtype='<u2').view('<f2').astype('f8')
photos={'IMG_2600':R/'research/vm-native/samples/IMG_2600.HEIC','IMG_2604':R/'research/vm-native/samples/IMG_2604.HEIC','IMG_2608':R/'research/vm-native/samples/IMG_2608.HEIC','IMG_0032':R/'Apple_Native_Samples/IMG_0032.HEIC','IMG_0033':R/'Apple_Native_Samples/IMG_0033.HEIC'}
rows=[]
for photo,path in photos.items():
    x=summaries[photo];assert x['completed']and x['host']['SRL_before_stats']==0 and x['host']['input_textures_SHA_unchanged'];M=x['basic_stats']['main_min_max_avg'][1]
    current=np.frombuffer(captures[photo+'/c.f16'],dtype='<u2');assert len(current)==1024
    tab=tables[M];ci=inverse(tab);possible=[ci.get(int(b),[])for b in current];unique=np.array([len(s)==1 for s in possible]);row={'photo':photo,'native_M_measured':M,'samples':1024,'native_codebook_M':M,'native_codebook_full_buckets':256,'native_code_unique_elements':int(unique.sum()),'native_code_uncovered_elements':sum(len(s)==0 for s in possible),'native_code_ambiguous_elements':sum(len(s)>1 for s in possible),'only_encoding_tail_preimages_not_scene_pixels':True}
    if photo in old:
        case=PRIVATE/photo;case.mkdir()
        with contextlib.redirect_stdout(io.StringIO()):extract(path,case)
        original_path=case/'keyc.bin';assert sha(original_path)==x['maps']['c']['original_sha256'];original=np.fromfile(original_path,dtype='<u2');assert original.shape==current.shape
        ot=old[photo]['codes_by_bucket'];oi=inverse(ot);op=[oi.get(int(b),[])for b in original];valid=unique&np.array([len(s)==1 for s in op]);idx=np.flatnonzero(valid)
        nk=np.array([possible[i][0]for i in idx]);ok=np.array([op[i][0]for i in idx]);tv=floats(tab);ov=floats(ot);actual=current.view('<f2').astype('f8')[idx];target=original.view('<f2').astype('f8')[idx]
        scale_first=tv[nk]-ov[nk];bucket_after=ov[nk]-ov[ok];bucket_first=tv[nk]-tv[ok];scale_after=tv[ok]-ov[ok]
        assert np.array_equal(tv[nk],actual)and np.array_equal(ov[ok],target)
        remap_bits=np.asarray(ot,dtype='<u2')[nk];interaction=scale_first-scale_after
        row.update({'file_M_conditionally_inferred_not_camera_measurement':old[photo]['normalizer'],'resolved_pair_elements':len(idx),'unresolved_pair_elements':int((~valid).sum()),'same_histogram_bucket_elements':int((nk==ok).sum()),'different_histogram_bucket_elements':int((nk!=ok).sum()),'bucket_delta_MAE':float(abs(nk-ok).mean()),'bucket_delta_max_abs':int(abs(nk-ok).max()),'scale_only_counterfactual_different_codes':int((remap_bits!=original[idx]).sum()),'scale_only_counterfactual_max_abs':float(abs(ov[nk]-target).max()),'original_native_code_max_abs':float(abs(actual-target).max()),'normalizer_first_MAE':float(abs(scale_first).mean()),'bucket_second_MAE':float(abs(bucket_after).mean()),'bucket_first_MAE':float(abs(bucket_first).mean()),'normalizer_second_MAE':float(abs(scale_after).mean()),'interaction_max_abs':float(abs(interaction).max()),'both_order_additive_identity_max_abs':max(float(abs(scale_first+bucket_after-(actual-target)).max()),float(abs(bucket_first+scale_after-(actual-target)).max())),'diagnostic_coordinate_identity_unchanged':True,'no_spatial_counterfactual_published_or_installed':True,'not_camera_EV_or_physical_global_local_split':True})
    else:row['original_file_bucket_decomposition']='Not inferred for these photos: no previously authenticated conditional file-scale codebook'
    rows.append(row)
save(O/'bucket-decomposition-s65.json',{'rows':rows,'scope':'c only; discrete encoding tail and fixed measured native M; file M remains conditional S58/S59','original_c_d_maps_or_inverse_changed':False,'scale_only_counterfactual_is_diagnostic_not_scene_inverse':True,'no_spatial_arrays_published':True,'no_new_holdout_or_full_native_roundtrip_claim':True})
save(O/'analysis-s65.json',{'os_build':'26A434','image_version':os.environ.get('ImageVersion'),'new_native_cases':256,'new_native_scale':NEW_M,'all_new_buckets_observed':True,'reference_tail_different_components':tail_diff,'old_native_cases_reexecuted':0,'photograph_pixel_or_stats_regenerations':0,'five_captures_reused':5,'all_five_c_map_codes_have_unique_native_codebook_preimage':all(x['native_code_unique_elements']==1024 for x in rows),'normalizer_only_explains_three_file_maps':all(x.get('scale_only_counterfactual_different_codes',0)==0 for x in rows),'formula_freeze_sha256':frozen_sha,'full_camera_binding_or_scene_inverse_proven':False,'A_phase_complete':False,'acceptance_complete':False,'old_masks_thresholds_unchanged':True})
assert sha(O/'diagnostic-freeze-s65.json')==frozen_sha
print(json.dumps({'new_native_scale_controls':256,'native_photo_regenerations':0,'old_native_cases_repeated':0,'camera_binding_proven':False}))
