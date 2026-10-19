"""New full-size host stats trace, reusing frozen reverse-key1/Apple Log inputs.

This is a controlled reconstruction-domain experiment, not camera execution.
All raw spatial outputs and native logs are sealed; only aggregates are public.
"""
from pathlib import Path
import ast,contextlib,hashlib,io,json,math,os,shutil,struct,subprocess,sys,tarfile,zlib
import numpy as np
R=Path.cwd();D=R/'research/hdr-native';W=Path(os.environ['W']);O=W/'out';PRIVATE=W/'private';EVID=PRIVATE/'evidence';EVID.mkdir()
sys.path[:0]=[str(R),str(R/'research/vm-native')]
from extract_inputs import extract,parse_heif,standalone
PHOTOS=[('IMG_2600','development',R/'research/vm-native/samples/IMG_2600.HEIC'),('IMG_2604','development',R/'research/vm-native/samples/IMG_2604.HEIC'),('IMG_2608','development',R/'research/vm-native/samples/IMG_2608.HEIC'),('IMG_0032','stats-operator-holdout',R/'Apple_Native_Samples/IMG_0032.HEIC'),('IMG_0033','stats-operator-holdout',R/'Apple_Native_Samples/IMG_0033.HEIC')]
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,j):
    with Path(p).open('x')as f:json.dump(j,f,indent=2,allow_nan=False);f.write('\n')
def run(args,log,timeout=900):
    with log.open('x')as f:return subprocess.run(list(map(str,args)),stdout=f,stderr=subprocess.STDOUT,timeout=timeout).returncode
assert sys.platform=='darwin'and subprocess.check_output(['sw_vers','-buildVersion'],text=True).strip()=='26A434'
assert sha('/System/Library/PrivateFrameworks/CMImaging.framework/Versions/A/Resources/default.metallib')=='16a8a119e3e0ae1649d32b2bbc8ea9136cb757a8d1f3eb451025821901edff11'
freeze={'os_build':'26A434','image_version':os.environ.get('ImageVersion'),'scope':'Original process with prepare1 on frozen native reverse-key1/AppleLog P3 source, original stored GTC/baseGain/exposure; not camera or Photos UI equivalence','holdout_scope':'0032/33 used in older studies; not used to choose this new stats trace before source freeze','photos':[{'id':n,'role':role,'sha256':sha(p)}for n,role,p in PHOTOS],'source_sha256':{p.name:sha(p)for p in[D/'run_hdr_s60.py',D/'stats_host_s60.m',D/'source_s60.m',D/'source_s37.m',R/'research/vm-native/runner/Styles_full_v3.m']},'processing_type':1,'original_small_maps_removed_from_new_generator_input_only':True,'original_metadata_files_changed':False,'raw_outputs_encrypted':True,'new_forward_or_scene_accuracy_gate_pass_inferred':False}
save(O/'formula-freeze-s60.json',freeze);freeze_sha=sha(O/'formula-freeze-s60.json')
flags=['clang','-O2','-Wno-deprecated-declarations','-fobjc-arc','-framework','Foundation','-framework','CoreImage','-framework','CoreMedia','-framework','ImageIO','-framework','Metal','-framework','CoreGraphics','-lz']
for name,file in [('source','source_s60.m'),('stats','stats_host_s60.m')]:assert run(flags+[D/file,'-o',W/name],O/(name+'-build.log'),240)==0,'Native compile prerequisite failed'
def load(case,spec,name):
    shape=tuple(spec['shape']);p=case/spec['file'];dtype=spec['dtype']
    if spec.get('compression')=='zlib':
        q=case/(name+'.decoded');dec=zlib.decompressobj()
        with p.open('rb')as src,q.open('xb')as dst:
            while data:=src.read(65536):dst.write(dec.decompress(data))
            dst.write(dec.flush())
        p=q
    return np.memmap(p,dtype=dtype,mode='r',shape=shape)
def half_copy(case,a,name,red=False):
    shape=a.shape[:2]+((1,)if red else(a.shape[2],));p=case/(name+'.f16');out=np.memmap(p,dtype='<f2',mode='w+',shape=shape)
    for top in range(0,len(a),32):out[top:top+32]=a[top:top+32,...,:1]if red else a[top:top+32]
    out.flush();del out;return {'file':p.name,'shape':list(shape),'dtype':'<f2','sha256':sha(p)}
results=[];failed=None
for name,role,photo in PHOTOS:
    case=PRIVATE/name;case.mkdir();out=EVID/name;out.mkdir();row={'photo':name,'role':role,'source_sha256':sha(photo),'completed':False};results.append(row)
    try:
        assert shutil.disk_usage(W).free>4_000_000_000+1_500_000_000
        with contextlib.redirect_stdout(io.StringIO()):extract(photo,case)
        data=photo.read_bytes();container=parse_heif(data);choices={'inputSubjectMatteImage':['semanticpersonmatte'],'inputSkinMatteImage':['semanticskinmattev2','semanticskinmatte'],'inputSkyMatteImage':['semanticskymatte']}
        row['auxiliary_mattes']={}
        for key,suffixes in choices.items():
            found=[]
            for suffix in suffixes:
                found=[v for v in container['items'].values()if v.get('aux_type','').endswith(suffix)]
                if found:break
            if found:
                assert len(found)==1
                raw=standalone(data,found[0]['item_id']);p=case/(key+'.heic');p.write_bytes(raw);row['auxiliary_mattes'][key]={'item_id':found[0]['item_id'],'sha256':sha(p),'decoding':'native RawImage, no display transform'}
        del data,container
        rc=run([W/'source',photo,case],out/'source-native.log',1200);row['source_returncode']=rc;assert rc==0,'Frozen source preparation failed'
        facts=json.loads((case/'source-facts.json').read_text());a=load(case,facts['frozen_decode']['unstyled'],'main');linear=load(case,facts['linear_native'],'linear');curve=load(case,facts['gtc_native'],'gtc');row['shape']=list(a.shape)
        fixture={'main':half_copy(case,a,'main'),'linear':half_copy(case,linear,'linear'),'gtc':half_copy(case,curve,'gtc',True),'base_gain':facts['native_properties']['baseGain'],'baseline_exposure':facts['native_properties']['baselineExposure'],'mattes':{}}
        assert all(isinstance(fixture[k],(int,float))and math.isfinite(fixture[k])and fixture[k]>0 for k in ['base_gain','baseline_exposure'])
        matte_facts=json.loads((case/'matte-facts.json').read_text());binding={'inputSubjectMatteImage':'inputPersonMaskTexture','inputSkinMatteImage':'inputSkinMaskTexture','inputSkyMatteImage':'inputSkyMaskTexture'}
        for key,description in matte_facts.items():fixture['mattes'][binding[key]]=half_copy(case,load(case,description,key),key,True)
        save(case/'stats-fixture.json',fixture);save(out/'fixture.json',fixture)
        rc=run([W/'stats',case,out],out/'stats-native.log',900);row['stats_returncode']=rc
        host=json.loads((out/'host.json').read_text())if(out/'host.json').exists()else {};row['host']={k:v for k,v in host.items()if k not in ['mattes_provided','exception_reason']}
        assert rc==0 and host.get('completed'),'Original stats process incomplete; inspect encrypted checkpoint/native stack'
        assert host['input_textures_SHA_unchanged']and host['SRL_before_stats']==0,'Input/SRL domain differs; no scalar-codebook claim'
        stats=np.fromfile(out/'_statsBuf.bin',dtype='<f4');params=np.fromfile(out/'_paramsBuf.bin',dtype='<f4');assert len(stats)*4==10640 and len(params)*4==672
        row['basic_stats']={'linear_min_max_avg':stats[10616//4:10628//4].astype(float).tolist(),'main_min_max_avg':stats[10628//4:10640//4].astype(float).tolist()};assert np.isfinite(list(row['basic_stats'].values())).all()
        row['global_context']={'metadata_base_gain':fixture['base_gain'],'metadata_baseline_exposure':fixture['baseline_exposure'],'native_base_gain':float(params[6]),'native_baseline_exposure':float(params[7]),'no_mean_alignment_claim_unless_native_update_seen':True}
        row['maps']={}
        for key in ['c','d']:
            original=np.fromfile(case/('key'+key+'.bin'),dtype='<f2');actual=np.fromfile(out/(key+'.f16'),dtype='<f2');assert original.shape==actual.shape==(1024,)
            finite=np.isfinite(actual)&np.isfinite(original);error=actual.astype('f8')-original.astype('f8');item={'samples':1024,'finite_samples':int(finite.sum()),'different_half_codes':int((actual.view('<u2')!=original.view('<u2')).sum()),'max_abs':float(abs(error[finite]).max())if finite.any()else None,'MAE':float(abs(error[finite]).mean())if finite.any()else None,'original_sha256':sha(case/('key'+key+'.bin')),'generated_sha256':sha(out/(key+'.f16')),'original_metadata_unchanged':True}
            row['maps'][key]=item
        layouts={}
        for filename,shape,dtype in [('c.f16',[32,32,1],'<f2'),('d.f16',[32,32,1],'<f2'),('_paramsBuf.bin',[672],'SSRParams mixed bytes'),('_statsBuf.bin',[10640],'SSRStats mixed u32/f32 bytes'),('color.bin',[320],'SSRColorManagement mixed bytes'),('ROI.bin',[176],'SSRRenderROI mixed bytes')]:
            p=out/filename
            if p.exists():layouts[filename]={'shape':shape,'dtype':dtype,'bytes':p.stat().st_size,'sha256':sha(p)}
        save(out/'capture-layouts.json',layouts);row['capture_layouts']=layouts;row['completed']=True
        del a,linear,curve,stats,params
    except Exception as error:
        row['failure_class']=type(error).__name__;row['failure_stage']='Read encrypted checkpoint/log; no retry or other photos after failure';failed=name
    finally:
        save(O/(name+'-summary.json'),row)
        # Keep only small new stats evidence, never full-size source pixels.
        shutil.rmtree(case)
    if failed:break
assert sha(O/'formula-freeze-s60.json')==freeze_sha
members=[]
for p in sorted(EVID.rglob('*')):
    if p.is_file():members.append({'path':str(p.relative_to(EVID)),'size':p.stat().st_size,'sha256':sha(p)})
assert sum(x['size']for x in members)<250000
save(EVID/'manifest.json',{'members':members,'scope':'small stats/maps/native logs only; no source photograph pixels','os_build':'26A434'})
tarpath=PRIVATE/'evidence.tar.gz'
with tarfile.open(tarpath,'w:gz')as tar:
    for p in sorted(EVID.rglob('*')):
        if p.is_file():tar.add(p,arcname=str(p.relative_to(EVID)),recursive=False)
cipher=O/'stats-captures-s60.tar.gz.gpg'
with (PRIVATE/'encrypt.log').open('x')as log:subprocess.run(['gpg','--batch','--trust-model','always','--recipient','28E62F64A29764C2F2AEBF5D5B6B1C101E5F5ABA','--output',str(cipher),'--encrypt',str(tarpath)],stdout=log,stderr=log,check=True,timeout=120)
assert cipher.stat().st_size<120000
save(O/'encrypted-inventory-s60.json',{'file':cipher.name,'cipher_bytes':cipher.stat().st_size,'cipher_sha256':sha(cipher),'plaintext_tar_sha256':sha(tarpath),'plaintext_members':members,'archive_private_key_on_runner':False,'public_spatial_outputs':False})
save(O/'analysis-s60.json',{'os_build':'26A434','image_version':os.environ.get('ImageVersion'),'full_size_photos_completed':sum(x['completed']for x in results),'planned_photos':5,'first_failed_photo':failed,'original_stats_process_not_direct_shader_dispatch':True,'camera_production_identity_proven':False,'no_old_operator_validation_repeated':True,'A_phase_complete':False,'acceptance_complete':False,'formula_freeze_sha256':freeze_sha})
print(json.dumps({'completed_photos':sum(x['completed']for x in results),'failed_photo':failed,'raw_captures_encrypted':True}))
if failed:sys.exit(5)
