"""S100 runner: original S99 experiment with source resources prepared first.

No optimization, precision hunt, camera inverse or new parameter identification.
Original HEIC, frozen source_s37 and all preexisting models are read-only.
"""
from pathlib import Path
import hashlib,json,os,resource,subprocess,sys,tarfile,zlib
import numpy as np
R=Path.cwd();D=R/'research/hdr-native';OLD=R/'research/vm-native/runner';W=Path(os.environ['W']);O=W/'out';PRIVATE=W/'private';ENC=W/'encrypted'
PLAN=json.loads((D/'inputs_s100.json').read_text())
sys.path[:0]=[str(R),str(R/'research/vm-native'),str(D)]
from extract_inputs import extract
from tools.heif_dump import parse_heif
from heif_standalone import standalone
from domain_analysis_s99 import analyze_case,finish
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,v):p.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def command(args,log,env=None,timeout=1800):
    with log.open('w')as f:return subprocess.run(list(map(str,args)),stdout=f,stderr=subprocess.STDOUT,env=dict(os.environ,**(env or {})),timeout=timeout).returncode
assert subprocess.check_output(['sw_vers','-buildVersion'],text=True).strip()=='26A434'
sources=[D/'s100_binding.json',D/'run_semantic_s99.py',Path(__file__).resolve(),D/'domain_analysis_s99.py',D/'semantic_domain_s99.m',D/'s99_binding.json',D/'source_s37.m',OLD/'Styles_full_v3.m',OLD/'native_filter_probe.m',D/'semantic_fullframe_s96.m',D/'s96_observer_binding.json',D/'observer_prerequisites_s96.inc',D/'encoder_capture_s96.inc',OLD/'replay_helpers_v7.inc',OLD/'consumer-structured-v8.metal']
save(O/'freeze.json',{'plan':PLAN,'source_SHA':{str(p.relative_to(R)):sha(p)for p in sources},'scope':'Actual native key1-reverse R and original S, separate Tone0 consumer contexts plus R Tone+.35 control. No inverse or original-camera semantic accuracy claim.','A_phase_complete':False,'engineering_accepted':False})
save(O/'S99-binding.json',json.loads((D/'s99_binding.json').read_text()))
save(O/'S100-binding.json',json.loads((D/'s100_binding.json').read_text()))
save(O/'S96-observer-binding.json',json.loads((D/'s96_observer_binding.json').read_text()))
cipher=W/'input.gpg';photo=W/'IMG_2810.HEIC'
assert command(['gh','api','-H','Accept: application/octet-stream',f"repos/21Z121Z1/Photographic_Style_Research/releases/assets/{PLAN['input_asset_id']}"],cipher)==0
assert cipher.stat().st_size==PLAN['cipher_bytes']and sha(cipher)==PLAN['cipher_sha256']
key=os.environ.pop('SEMANTIC_S100_INPUT_SESSION').encode();rd,wr=os.pipe()
with(W/'input-decrypt.log').open('wb')as log:
    p=subprocess.Popen(['gpg','--batch','--override-session-key-fd',str(rd),'--status-fd','2','--output',str(photo),'--decrypt',str(cipher)],pass_fds=(rd,),stdout=log,stderr=log);os.close(rd);os.write(wr,key+b'\n');os.close(wr);del key
    assert p.wait(timeout=120)==0
assert photo.stat().st_size==PLAN['source_bytes']and sha(photo)==PLAN['source_sha256']
os.environ.pop('GH_TOKEN',None);cipher.unlink()
RES=W/'resources';extract(photo,RES);data=photo.read_bytes();h=parse_heif(data)
for target,suffix in {'inputSubjectMatteImage':'semanticpersonmatte','inputSkinMatteImage':'semanticskinmatte','inputSkyMatteImage':'semanticskymatte','inputGainMapImage':'hdrgainmap'}.items():
    found=[i for i in h['items'].values()if i.get('aux_type','').endswith(suffix)];assert len(found)==1
    (RES/(target+'.heic')).write_bytes(standalone(data,found[0]['item_id']))
del data
GEN=W/'generated';GEN.mkdir();original=(OLD/'native_filter_probe.m').read_text();derived=original
replacements=[('if(w*h>2000000)','if(w*h>32000000)'),('for(NSNumber *engine in @[@NO,@YES])','for(NSNumber *engine in @[@NO])'),('facts[@"defaults"]=defaults;', 'facts[@"defaults"]=defaults; @try{facts[@"default_use_style_engine_before_override"]=[filter valueForKey:@"useStyleEngine"]?:NSNull.null;}@catch(NSException*e){facts[@"default_use_style_engine_observation_error"]=e.name;}')]
for a,b in replacements:assert derived.count(a)==1;derived=derived.replace(a,b)
(GEN/'native_filter_probe_s99.m').write_text(derived)
save(O/'derived-binding.json',{'original_source_SHA256':hashlib.sha256(original.encode()).hexdigest(),'derived_source_SHA256':hashlib.sha256(derived.encode()).hexdigest(),'exact_replacements':[{'old':a,'new':b}for a,b in replacements],'no_ROI_or_downscale_override':True})
(O/'native-filter-derived.txt').write_text(derived)
flags=['clang','-fobjc-arc','-O2','-I'+str(OLD),'-I'+str(GEN),'-framework','Foundation','-framework','CoreImage','-framework','CoreMedia','-framework','ImageIO','-framework','Metal','-framework','CoreGraphics','-lz','-Wl,-undefined,dynamic_lookup']
assert command(flags+[D/'source_s37.m','-o',W/'source'],O/'source-build.log')==0
assert command(flags+[D/'semantic_domain_s99.m','-o',W/'domain'],O/'native-build.log')==0
SRC=PRIVATE/'native-key1-source';extract(photo,SRC)
required=['styles.plist','linear.heic','delta.heic']
assert SRC.is_dir()and all((SRC/n).is_file()and sha(SRC/n)==sha(RES/n)for n in required)
save(O/'source-prerequisites.json',{'directory_prepared':True,'same_resources_as_original_extract':{n:sha(SRC/n)for n in required},'source_s37_byte_unchanged':True,'existing_S42_S89_residency_compatibility_flag':'VM_DISABLE_RESIDENCY_SETS=1','native_pixel_model_changed':False})
rc=command([W/'source',photo,SRC],O/'source-native.log',{'VM_DISABLE_RESIDENCY_SETS':'1'},timeout=2400)
if(SRC/'source-exception.json').exists():save(O/'source-exception.json',json.loads((SRC/'source-exception.json').read_text()))
assert rc==0,'Frozen source failed after prerequisites prepared; inspect source-native.log and source-exception.json before another run'
facts=json.loads((SRC/'source-facts.json').read_text());spec=facts['frozen_decode']['unstyled'];assert tuple(spec['shape'])==(4284,5712,4)and spec['dtype']=='<f2'and spec['compression']=='zlib'
save(O/'source-facts.json',facts)
raw=W/'reverse-input.f16';dec=zlib.decompressobj()
with(SRC/spec['file']).open('rb')as f,raw.open('xb')as dst:
    while b:=f.read(1<<20):dst.write(dec.decompress(b))
    dst.write(dec.flush())
assert dec.eof and raw.stat().st_size==4284*5712*8
a=np.memmap(raw,mode='r',dtype='<f2',shape=(4284,5712,4));override=W/'reverse-input.f32';b=np.memmap(override,mode='w+',dtype='<f4',shape=a.shape)
for top in range(0,4284,32):b[top:top+32]=a[top:top+32]
b.flush();del a,b
save(O/'key1-bridge.json',{'raw_canvas':[4284,5712],'source_s37_SHA256':sha(D/'source_s37.m'),'native_unstyled_spec':spec,'native_half_input_SHA256':sha(raw),'widened_f32_input_SHA256':sha(override),'widening':'Exact binary16 to float32, no exposure/tone/matte adjustment; original native half storage separately retained','not_scene_master':True,'key1_full_style_not_isolated_semantics':True})
summary=[];all_images=[];discard=[]
for label,primary,tone in [('original-tone0',None,0.),('key1-reverse-tone0',override,0.),('key1-reverse-tone035',override,.35)]:
    folder=PRIVATE/label;env={'XD_TONE_MAX_EDGE':'5712','XD_TONE_THUMB_MODE':'native-stage-mirror','XD_TONE_BIAS':str(tone)}
    if primary:env.update(XD_TONE_PRIMARY_F32=str(primary),XD_TONE_PRIMARY_WIDTH='5712',XD_TONE_PRIMARY_HEIGHT='4284')
    rc=command([W/'domain',photo,RES,folder],O/(label+'-native.log'),env,timeout=2400)
    census=folder/'semantic-full/native-calls.json';assert census.exists(),'Expected census even if native output bypasses renderer'
    calls=json.loads(census.read_text());save(O/(label+'-native-calls.json'),calls)
    report=folder/'facts.json';assert report.exists(),'Native filter facts missing; read log before any retry'
    native_facts=json.loads(report.read_text());save(O/(label+'-filter-report.json'),native_facts)
    row,pictures=analyze_case(label,tone,folder,calls,native_facts,O,PRIVATE)
    row.update(returncode=rc,native_child_peak_RSS_bytes_macOS=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss)
    summary.append(row);all_images.extend(pictures);save(O/'analysis-checkpoint.json',{'cases':summary,'A_phase_complete':False})
    assert rc==0 and all(p['original_process_return']==0 for p in calls['processes'])
    for name in ['primary_input.f32','renderer.f32','thumbnail_input.f32']:
        p=folder/name
        if p.exists():discard.append({'path':str(p.relative_to(PRIVATE)),'bytes':p.stat().st_size,'sha256':sha(p)});p.unlink()
finish(summary,all_images,O,PRIVATE)
original_exact=SRC/'original_sdr_exact.f32'
if original_exact.exists():discard.append({'path':str(original_exact.relative_to(PRIVATE)),'bytes':original_exact.stat().st_size,'sha256':sha(original_exact)});original_exact.unlink()
save(PRIVATE/'temporary-comparison-array-hashes.json',{'files':discard,'reason':'Only this-run duplicate comparison arrays removed after metrics. Full native source half/zlib, reference owners, neutral outputs, raw skin bindings and non-rendered bypass results retained. Original HEIC and historical outputs unchanged.'})
save(PRIVATE/'manifest.json',{'run_id':os.environ['GITHUB_RUN_ID'],'commit':os.environ['GITHUB_SHA'],'os_build':'26A434','files':[{'path':str(p.relative_to(PRIVATE)),'size':p.stat().st_size,'sha256':sha(p)}for p in sorted(PRIVATE.rglob('*'))if p.is_file()]})
with tarfile.open(W/'private.tar.gz','w:gz')as t:t.add(PRIVATE,arcname='out')
assert command(['gpg','--batch','--trust-model','always','--recipient','28E62F64A29764C2F2AEBF5D5B6B1C101E5F5ABA','--output',ENC/'results.tar.gz.gpg','--encrypt',W/'private.tar.gz'],O/'encrypt.log')==0
save(O/'encrypted-inventory.json',{'file':'results.tar.gz.gpg','bytes':(ENC/'results.tar.gz.gpg').stat().st_size,'sha256':sha(ENC/'results.tar.gz.gpg'),'plaintext_uploaded':False})
print(json.dumps({'completed':True,'cases':len(summary),'no_inverse_or_precision_hunt':True,'A_phase_complete':False}))
