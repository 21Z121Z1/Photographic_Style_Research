"""S98 full original-frame conditional semantic inverse; macOS runner only.

Existing S93 solver, complete real CI owners, no new patch sampling or precision
hunt. Camera-baked parameter identifiability and physical truth remain unproven.
"""
from pathlib import Path
import hashlib,json,os,resource,subprocess,sys,tarfile
import numpy as np
from PIL import Image,ImageDraw
import PyOpenColorIO as ocio

R=Path.cwd();D=R/'research/hdr-native';W=Path(os.environ['W']);O=W/'out';PRIVATE=W/'private';ENC=W/'encrypted';OLD=R/'research/vm-native/runner'
PLAN=json.loads((D/'inputs_s98.json').read_text())
sys.path.insert(0,str(R));sys.path.insert(0,str(R/'research/vm-native'));sys.path.insert(0,str(D))
from extract_inputs import extract
from tools.heif_dump import parse_heif
from heif_standalone import standalone
from semantic_strength_s82 import apply

def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,o):p.write_text(json.dumps(o,indent=2,allow_nan=False)+'\n')
def command(args,log,env=None,timeout=1800):
    with log.open('w')as f:return subprocess.run(list(map(str,args)),stdout=f,stderr=subprocess.STDOUT,env=dict(os.environ,**(env or {})),timeout=timeout).returncode
assert subprocess.check_output(['sw_vers','-buildVersion'],text=True).strip()=='26A434'
sources=[D/'s98_binding.json',D/'semantic_fullframe_s98.m',D/'fullframe_analysis_s98.py',D/'evidence/s93/run/S93-inverse-include.txt',D/'run_semantic_s97.py',D/'s97_driver_binding.json',D/'run_semantic_s96.py',Path(__file__).resolve(),D/'semantic_fullframe_s96.m',D/'observer_prerequisites_s96.inc',D/'encoder_capture_s96.inc',D/'s96_observer_binding.json',D/'semantic_fullframe_s95.m',D/'semantic_strength_s82.py',OLD/'native_filter_probe.m',OLD/'encoder_capture_v2.inc',OLD/'replay_helpers_v7.inc',OLD/'consumer-structured-v8.metal']
save(O/'S98-binding.json',json.loads((D/'s98_binding.json').read_text()))
save(O/'S97-driver-binding.json',json.loads((D/'s97_driver_binding.json').read_text()))
save(O/'S96-observer-binding.json', json.loads((D/'s96_observer_binding.json').read_text()))
save(O/'freeze.json',{'plan':PLAN,'source_SHA':{str(p.relative_to(R)):sha(p)for p in sources},'scope':'Original5712x4284 native consumer; real PI owner rectangles must cover all24470208 pixels once; no single physical framebuffer assumption; full conditional inverse using unchanged S93 solver','no_changes_to_frozen_models':True,'old_gates_not_relabelled':True,'engineering_accepted':False})
cipher=W/'input.gpg';photo=W/'IMG_2810.HEIC'
assert command(['gh','api','-H','Accept: application/octet-stream',f"repos/21Z121Z1/Photographic_Style_Research/releases/assets/{PLAN['input_asset_id']}"],cipher)==0
assert cipher.stat().st_size==PLAN['cipher_bytes']and sha(cipher)==PLAN['cipher_sha256']
key=os.environ.pop('SEMANTIC_S98_INPUT_SESSION').encode();rd,wr=os.pipe()
with(W/'input-decrypt.log').open('wb')as f:
    p=subprocess.Popen(['gpg','--batch','--override-session-key-fd',str(rd),'--status-fd','2','--output',str(photo),'--decrypt',str(cipher)],pass_fds=(rd,),stdout=f,stderr=f)
    os.close(rd);os.write(wr,key+b'\n');os.close(wr);del key
    assert p.wait(timeout=120)==0
assert photo.stat().st_size==PLAN['source_bytes']and sha(photo)==PLAN['source_sha256']
os.environ.pop('GH_TOKEN',None);cipher.unlink()
RES=W/'resources';extract(photo,RES);data=photo.read_bytes();h=parse_heif(data)
for target,suffix in {'inputSubjectMatteImage':'semanticpersonmatte','inputSkinMatteImage':'semanticskinmatte','inputSkyMatteImage':'semanticskymatte','inputGainMapImage':'hdrgainmap'}.items():
    found=[i for i in h['items'].values()if i.get('aux_type','').endswith(suffix)]
    assert len(found)==1
    (RES/(target+'.heic')).write_bytes(standalone(data,found[0]['item_id']))
del data
GEN=W/'generated';GEN.mkdir()
original=(OLD/'native_filter_probe.m').read_text();derived=original
replacements=[('if(w*h>2000000)','if(w*h>32000000)'),('for(NSNumber *engine in @[@NO,@YES])','for(NSNumber *engine in @[@NO])')]
for before,after in replacements:
    assert derived.count(before)==1;derived=derived.replace(before,after)
assert derived!=original
(GEN/'native_filter_probe_s96.m').write_text(derived)
save(O/'derived-binding.json',{'original_source_SHA256':hashlib.sha256(original.encode()).hexdigest(),'derived_source_SHA256':hashlib.sha256(derived.encode()).hexdigest(),'exact_replacements':[{'old':a,'new':b}for a,b in replacements],'no_ROI_or_downscale_override':True,'source_read_only':True})
(O/'native-filter-derived.txt').write_text(derived)
exe=W/'semantic-s98'
flags=['clang','-fobjc-arc','-O2','-I'+str(OLD),'-I'+str(GEN),'-framework','Foundation','-framework','CoreImage','-framework','CoreMedia','-framework','ImageIO','-framework','Metal','-Wl,-undefined,dynamic_lookup']
assert command(flags+[D/'semantic_fullframe_s98.m','-o',exe],O/'build.log')==0
folder=PRIVATE/'full-frame'
rc=command([exe,photo,RES,folder],O/'native.log',{'XD_TONE_MAX_EDGE':'5712','XD_TONE_THUMB_MODE':'native-stage-mirror','XD_TONE_BIAS':'.35','VM_EXACT_INVERSE_LIMIT':'7000000'},timeout=3300)
calls_path=folder/'semantic-full/native-calls.json'
assert calls_path.exists(),'No completed native callback; inspect native.log'
calls=json.loads(calls_path.read_text());save(O/'native-calls.json',calls)
save(O/'native-execution.json',{'returncode':rc,'source_unscaled':True,'requested_canvas':[4284,5712],'calls':len(calls['calls']),'region_reference_count':sum(bool(x.get('region_reference_available'))for x in calls['calls']),'inverse_executed':True,'native_child_peak_RSS_bytes_macOS':resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss})
regions=[c for c in calls['calls']if c.get('region_reference_available')and c.get('all_original_textures_and_buffers_unchanged')]
assert rc==0 and calls['processes'] and all(x['original_process_return']==0 for x in calls['processes']), 'Original native process failed; inspect nested guided returns and allocator events'
assert regions and len(regions)==len(calls['calls']),'Unproven final owner layout or hydration; census does not certify the full photo'
assert all(x['native_hydration']['half_differing_components']==0 for x in regions)
from fullframe_analysis_s98 import analyze
summary=analyze(PLAN,folder,calls,O,PRIVATE,W)
discard=[]
for name in['primary_input.f32','renderer.f32','thumbnail_input.f32']:
    path=folder/name
    if path.exists():
        discard.append({'path':str(path.relative_to(PRIVATE)),'bytes':path.stat().st_size,'sha256':sha(path)});path.unlink()
save(PRIVATE/'temporary-comparison-array-hashes.json',{'purpose':'Only new per-run reproducible CI comparison arrays removed after assessment; all native references, effective recovered half inputs, raw masks, relative residuals and estimated-neutral outputs preserved. Historical archives/originals unchanged.','files':discard})
save(PRIVATE/'manifest.json',{'run_id':os.environ['GITHUB_RUN_ID'],'commit':os.environ['GITHUB_SHA'],'os_build':'26A434','files':[{'path':str(p.relative_to(PRIVATE)),'size':p.stat().st_size,'sha256':sha(p)}for p in sorted(PRIVATE.rglob('*'))if p.is_file()]})
with tarfile.open(W/'private.tar.gz','w:gz')as tar:tar.add(PRIVATE,arcname='out')
assert command(['gpg','--batch','--trust-model','always','--recipient','28E62F64A29764C2F2AEBF5D5B6B1C101E5F5ABA','--output',ENC/'results.tar.gz.gpg','--encrypt',W/'private.tar.gz'],O/'encrypt.log')==0
save(O/'encrypted-inventory.json',{'file':'results.tar.gz.gpg','bytes':(ENC/'results.tar.gz.gpg').stat().st_size,'sha256':sha(ENC/'results.tar.gz.gpg'),'plaintext_uploaded':False})
print(json.dumps({'full_original_frame_inverse_executed':True,'pixels':summary['full_original_frame_pixels'],'selected_practical_gates_pass':summary['all_selected_practical_gates_pass'],'old_roundtrip_gate_pass':summary['roundtrip']['old_1e3_gate_pass'],'A_phase_complete':False}))
