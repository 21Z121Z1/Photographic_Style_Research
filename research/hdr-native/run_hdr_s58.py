"""Conditional finite-half normalizer inference; not a native camera certificate.

The ordered reference tail is frozen in S55. This run adds a complete finite
positive binary16 normalizer enumeration, not new fitting of consumer pixels.
"""
from pathlib import Path
import ast,base64,hashlib,json,os,re,subprocess,sys,zipfile
import numpy as np
from lightmap_model_s55 import A,B,INV255
D=Path('research/hdr-native');W=Path(os.environ['W']);O=W/'out';F=np.float32;H=np.float16
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,j):
    with Path(p).open('x')as f:json.dump(j,f,indent=2,allow_nan=False);f.write('\n')
assert sys.platform=='darwin'and subprocess.check_output(['sw_vers','-buildVersion'],text=True).strip()=='26A434'
freeze={'os_build':'26A434','image_version':os.environ.get('ImageVersion'),'model_sha256':sha(D/'lightmap_model_s55.py'),'script_sha256':sha(D/'run_hdr_s58.py'),'declared_normalizer_bits':[1,0x7bff],'domain':'all finite positive binary16, source-ordered IEEE reference only','unknowns_not_covered':['actual camera production binding','native fast-math reassociation for untested inputs','negative zero nonfinite normalizers','full image or 33-skin-point inverse'],'old_models_or_masks_changed':False,'new_native_histogram_dispatches':0}
save(O/'formula-freeze-s58.json',freeze);freeze_sha=sha(O/'formula-freeze-s58.json')
desc=json.loads((D/'transport-input-s56.json').read_text());cipher=W/'input-maps.gpg';assert sha(cipher)==desc['cipher_sha256']
key=os.environ.pop('HDR_S55_INPUT_SESSION');assert key.split(':',1)[0]=='9.2';rd,wr=os.pipe();os.write(wr,key.encode()+b'\n');os.close(wr)
try:
    with (W/'private/maps.json').open('xb')as out,(W/'secure/decrypt.log').open('xb')as err:p=subprocess.run(['gpg','--batch','--override-session-key-fd',str(rd),'--status-fd','2','--decrypt',str(cipher)],pass_fds=(rd,),stdout=out,stderr=err,timeout=120)
finally:os.close(rd);del key
events=re.findall(rb'\[GNUPG:\] ([A-Z_]+)',(W/'secure/decrypt.log').read_bytes())
transport={'returncode':p.returncode,'events':[x.decode()for x in events],'plaintext_sha256_matches':sha(W/'private/maps.json')==desc['plaintext_sha256'],'plaintext_size_matches':(W/'private/maps.json').stat().st_size==desc['plaintext_bytes'],'raw_log_uploaded':False}
save(O/'transport-check-s58.json',transport);assert p.returncode==0 and b'DECRYPTION_OKAY'in events and transport['plaintext_sha256_matches']and transport['plaintext_size_matches']
payload=json.loads((W/'private/maps.json').read_text());inputs=[]
for sample in payload['samples']:
    for name in ['c','d']:
        entry=sample['buffers'][name];raw=base64.b64decode(entry['base64'],validate=True);assert hashlib.sha256(raw).hexdigest()==entry['sha256']and len(raw)==2048
        vals=np.frombuffer(raw,'<f2');assert np.isfinite(vals).all()and (vals>0).all();codes,counts=np.unique(vals.view('<u2'),return_counts=True)
        inputs.append((sample['photo'],name,codes,counts,entry['sha256']))
# A normalizer from imageReduction is stored half->float. The GTC normalizer
# is also half before float extension. This is conditional on that provenance.
axis=np.arange(0x7c00,dtype='<u2');norms=axis.view('<f2').astype('<f4');p50=(np.arange(256,dtype='<f4')*INV255).astype('<f4')
codebook=np.empty((0x7c00,256),dtype='<u2')
with np.errstate(all='ignore'):
    for lo in range(0,0x7c00,256):
        hi=min(lo+256,0x7c00);product=((norms[lo:hi,None]*A).astype('<f4')*p50[None,:]).astype('<f4');inner=(product+B).astype('<f4').astype('<f2')
        codebook[lo:hi]=((inner.astype('<f4')+F(1.2)).astype('<f4')*F(.29412)).astype('<f4').astype('<f2').view('<u2')
assert np.all(codebook[:,1:]>=codebook[:,:-1])
# New exhaustive reference object also contains all prior native finite probes.
archive=D/'evidence/s56/native-text-artifact.zip';assert sha(archive)=='f2674fa102e47d3115efcb7ee3ff11553f5e1b84de6775d15ec2a2f9a7d7c046'
with zipfile.ZipFile(archive)as z:
    manifest=json.loads(z.read('manifest.json'));files={x['path']:x for x in manifest['files']};raw=z.read('native-histogram-s56.json');assert hashlib.sha256(raw).hexdigest()==files['native-histogram-s56.json']['sha256'];native=json.loads(raw)
tree=ast.parse((D/'run_hdr_s56.py').read_text());nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='gtc_normalizer'];assert len(nodes)==1
import math
exec(compile(ast.Module(body=nodes,type_ignores=[]),str(D/'run_hdr_s56.py'),'exec'),globals())
cases=json.loads((D/'cases-s55.json').read_text())['cases'];native_checks=0
for case,row in zip(cases,native['rows'],strict=True):
    assert row['id']==case['id']
    for out,norm,hist in [('c',case['ltm_max'],0),('d',gtc_normalizer(case['lin_max'],case['base_gain'],case['baseline_exposure'],case['curve']),7)]:
        bits=int(np.asarray([norm],dtype='<f2').view('<u2')[0]);bucket=int(round(row['local_p50_p98_by_histogram_index'][hist][0]*255));assert int(codebook[bits,bucket])==row[out+'_bits'];native_checks+=1
rows=[]
for photo,name,codes,counts,input_sha in inputs:
    feasible=np.zeros(0x7c00,dtype=np.uint8);max_compatible=0
    for bits in range(1,0x7c00):
        row=codebook[bits];positions=np.searchsorted(row,codes);matched=(positions<256)&(row[np.minimum(positions,255)]==codes);covered=int(counts[matched].sum());max_compatible=max(max_compatible,covered)
        if covered==1024:feasible[bits]=1
    indices=np.flatnonzero(feasible);packed=np.packbits(feasible,bitorder='little').tobytes()
    item={'photo':photo,'map':name,'input_map_sha256':input_sha,'map_elements':1024,'distinct_observed_codes':len(codes),'complete_positive_half_domain_tested':31743,'reference_codebook_sha256':hashlib.sha256(codebook.tobytes()).hexdigest(),'feasible_normalizer_count':len(indices),'max_exact_compatible_elements_any_single_M':max_compatible,'required_compatible_elements':1024,'normalizer_choice_fitted_or_injected':False,'feasible_M_bitset_axis':'bit i corresponds to positive half bits i, bit0 excluded, little bit order','feasible_M_bitset_base64':base64.b64encode(packed).decode(),'feasible_M_bitset_sha256':hashlib.sha256(packed).hexdigest(),'full_native_or_camera_certificate':False}
    if len(indices):item.update({'normalizer_min':float(norms[indices[0]]),'normalizer_max':float(norms[indices[-1]]),'normalizer_min_bits':int(indices[0]),'normalizer_max_bits':int(indices[-1])})
    rows.append(item)
save(O/'finite-half-normalizer-analysis-s58.json',{'scope':freeze['domain'],'rows':rows,'normalizers_per_map':31743,'histogram_indices_per_normalizer':256,'codebook_cells_including_zero_diagnostic':int(codebook.size),'prior_native_output_components_checked':native_checks,'prior_native_cases_reexecuted':0,'full_native_camera_certificate':False,'no_spatial_real_data_published':True,'no_new_photo_pixel_processing':True})
assert sha(O/'formula-freeze-s58.json')==freeze_sha
save(O/'analysis-s58.json',{'os_build':'26A434','image_version':os.environ.get('ImageVersion'),'map_contexts':len(rows),'all_declared_positive_half_reference_normalizers_enumerated':True,'maps_with_nonempty_conditional_M_set':sum(x['feasible_normalizer_count']>0 for x in rows),'all_538_prior_native_components_in_new_reference_codebook':native_checks==538,'native_camera_binding_proven':False,'native_fast_math_full_domain_proven':False,'old_masks_thresholds_models_changed':False,'A_phase_complete':False,'acceptance_complete':False,'formula_freeze_sha256':freeze_sha})
print(json.dumps({'map_contexts':len(rows),'conditional_feasible_sets':[{'photo':x['photo'],'map':x['map'],'candidate_count':x['feasible_normalizer_count'],'max_compatible_elements':x['max_exact_compatible_elements_any_single_M']}for x in rows]}))
