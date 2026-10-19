"""Read captured S63 only: colour-management fields and frozen D4 diagnostics.

No native image regeneration, no changes to authoritative geometry/model/gates.
"""
from pathlib import Path
import contextlib,hashlib,io,json,math,os,re,struct,subprocess,sys,tarfile,zipfile
import numpy as np
R=Path.cwd();D=R/'research/hdr-native';W=Path(os.environ['W']);O=W/'out'
sys.path[:0]=[str(R),str(R/'research/vm-native')]
from extract_inputs import extract
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,j):
    with Path(p).open('x')as f:json.dump(j,f,indent=2,allow_nan=False);f.write('\n')
assert sys.platform=='darwin'and subprocess.check_output(['sw_vers','-buildVersion'],text=True).strip()=='26A434'
archive=W/'S63.zip';assert sha(archive)=='77d121caf0eb5a095107fc412a215c6da5946ac0ab94b008a55575da7a4ae153'
with zipfile.ZipFile(archive)as z:
    names=z.namelist();manifest=json.loads(z.read('manifest.json'));assert manifest['run_id']=='39324317293'and manifest['commit']=='be2f2605c7a14ff0366adef87738c8c3122c0f3b'
    for entry in manifest['files']:assert hashlib.sha256(z.read(entry['path'])).hexdigest()==entry['sha256']
    cipher=z.read(next(n for n in names if n.endswith('.gpg')));inventory=json.loads(z.read('encrypted-inventory-s63.json'));summaries={json.loads(z.read(n))['photo']:json.loads(z.read(n))for n in names if n.endswith('-summary.json')}
    with (W/'private/input.gpg').open('xb')as f:f.write(cipher)
key=os.environ.pop('HDR_S64_S63_SESSION');rd,wr=os.pipe();os.write(wr,key.encode()+b'\n');os.close(wr)
try:
    with (W/'private/captures.tar.gz').open('xb')as out,(W/'private/decrypt.log').open('xb')as err:q=subprocess.run(['gpg','--batch','--override-session-key-fd',str(rd),'--status-fd','2','--decrypt',str(W/'private/input.gpg')],pass_fds=(rd,),stdout=out,stderr=err,timeout=120)
finally:os.close(rd);del key
events=[x.decode()for x in re.findall(rb'\[GNUPG:\] ([A-Z_]+)',(W/'private/decrypt.log').read_bytes())]
save(O/'decrypt-check-s64.json',{'returncode':q.returncode,'events':events,'private_archive_key_on_runner':False,'plaintext_tar_sha256_matches':sha(W/'private/captures.tar.gz')==inventory['plaintext_tar_sha256']})
assert q.returncode==0 and 'DECRYPTION_OKAY'in events and sha(W/'private/captures.tar.gz')==inventory['plaintext_tar_sha256']
expected={x['path']:x for x in inventory['plaintext_members']};capture={}
with tarfile.open(W/'private/captures.tar.gz','r:gz')as t:
    for member in t:
        assert member.isfile()and member.size<60000
        raw=t.extractfile(member).read()
        if member.name=='manifest.json':continue
        assert member.name in expected and hashlib.sha256(raw).hexdigest()==expected[member.name]['sha256']
        capture[member.name]=raw
assert set(capture)==set(expected)
transforms={'identity':lambda a:a,'flip_y':lambda a:np.flip(a,0),'flip_x':lambda a:np.flip(a,1),'rot90':lambda a:np.rot90(a,1),'rot180':lambda a:np.rot90(a,2),'rot270':lambda a:np.rot90(a,3),'transpose':lambda a:a.T,'anti_transpose':lambda a:np.flip(a.T,(0,1))}
save(O/'diagnostic-freeze-s64.json',{'os_build':'26A434','source_S63_run':'39324317293','source_S63_zip_sha256':sha(archive),'source_script_sha256':sha(D/'analyze_stats_s64.py'),'transforms':list(transforms),'authoritative_geometry_unchanged':True,'no_native_photo_or_stats_regenerated':True,'no_exposure_colour_or_numeric_coefficient_fitting':True,'development':['IMG_2600','IMG_2604','IMG_2608'],'holdouts':['IMG_0032','IMG_0033'],'selection_scope':'discrete geometry hypothesis only, no original gate passing inferred','old_masks_thresholds_models_unchanged':True})
def color_schema(raw):
    assert len(raw)==320;fields={}
    for group,name in enumerate(['inputImage','inputLinearImage','inputMasks','outputImage']):
        base=80*group;matrix=[list(struct.unpack_from('<3f',raw,base+16+col*16))for col in range(3)];bits=[list(struct.unpack_from('<3I',raw,base+16+col*16))for col in range(3)];assert all(math.isfinite(x)for col in matrix for x in col)
        fields[name]={'transfer_enum':struct.unpack_from('<i',raw,base)[0],'CCM_columns':matrix,'CCM_f32_bits':bits,'useVELuma_byte':raw[base+64]}
    return fields
old=json.loads((D/'evidence/s64/original-consumer-color.json').read_text());colour=[]
for photo in summaries:
    raw=capture[photo+'/color.bin'];current=color_schema(raw);row={'photo':photo,'source_native_capture_run':'39324317293','source_color_sha256':hashlib.sha256(raw).hexdigest(),'native_fields':current,'actual_interpretation_names_require_AIR_enum_mapping':True}
    if photo in old['photos']:
        prior=old['photos'][photo];row.update({'old_consumer_run':'39055408205','old_consumer_color_sha256':prior['sha256'],'all_320_bytes_equal':prior['sha256']==row['source_color_sha256'],'active_semantic_fields_equal':prior['fields']==current,'old_consumer_fields':prior['fields']})
    colour.append(row)
save(O/'color-context-s64.json',{'photos':colour,'no_spatial_arrays_published':True,'not_camera_colour_calibration':True})
photos={'IMG_2600':R/'research/vm-native/samples/IMG_2600.HEIC','IMG_2604':R/'research/vm-native/samples/IMG_2604.HEIC','IMG_2608':R/'research/vm-native/samples/IMG_2608.HEIC','IMG_0032':R/'Apple_Native_Samples/IMG_0032.HEIC','IMG_0033':R/'Apple_Native_Samples/IMG_0033.HEIC'}
rows=[];selected=None;rule_sha=None
for index,photo in enumerate(photos):
    if index==3:
        totals={name:sum(x['MAE']for x in rows if x['transform']==name)for name in transforms};selected=min(totals,key=totals.get)
        save(O/'geometry-hypothesis-freeze-s64.json',{'development_joint_MAE_sums':totals,'selected_hypothesis':selected,'scope':'best development D4 hypothesis, not authenticated file binding','heldout_values_used_before_freeze':False,'original_acceptance_geometry_changed':False});rule_sha=sha(O/'geometry-hypothesis-freeze-s64.json')
    case=W/'private'/photo;case.mkdir()
    with contextlib.redirect_stdout(io.StringIO()):extract(photos[photo],case)
    for name in ['c','d']:
        path=case/('key'+name+'.bin');assert sha(path)==summaries[photo]['maps'][name]['original_sha256'];original=np.fromfile(path,dtype='<f2').reshape(32,32);native=np.frombuffer(capture[photo+'/'+name+'.f16'],dtype='<f2').reshape(32,32);assert np.isfinite(native).all()and np.isfinite(original).all()
        for transform,fn in transforms.items():
            actual=fn(native);diff=actual.astype('f8')-original.astype('f8');rows.append({'photo':photo,'role':'development'if index<3 else'geometry-diagnostic-holdout','map':name,'transform':transform,'different_half_codes':int((actual.view('<u2')!=original.view('<u2')).sum()),'max_abs':float(abs(diff).max()),'MAE':float(abs(diff).mean()),'samples':1024,'authoritative_identity_retained':True})
    if index>=3:assert sha(O/'geometry-hypothesis-freeze-s64.json')==rule_sha
save(O/'geometry-diagnostics-s64.json',{'rows':rows,'selected_development_hypothesis':selected,'selected_scope':'data-derived geometry hypothesis only','selected_hypothesis_half_bit_exact_for_all':all(x['different_half_codes']==0 for x in rows if x['transform']==selected),'identity_half_bit_exact_for_all':all(x['different_half_codes']==0 for x in rows if x['transform']=='identity'),'no_geometry_or_threshold_or_mask_changed':True,'no_spatial_real_arrays_published':True})
save(O/'analysis-s64.json',{'os_build':'26A434','image_version':os.environ.get('ImageVersion'),'captured_photos_reused':5,'native_image_operations_reexecuted':0,'selected_geometry_hypothesis':selected,'not_full_native_camera_binding':True,'A_phase_complete':False,'acceptance_complete':False})
print(json.dumps({'reused_photos':5,'native_reexecuted':0,'geometry_hypothesis':selected,'full_camera_binding_proven':False}))
