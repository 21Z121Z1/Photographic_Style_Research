"""S96 full-frame native semantic references and bounded retained-PSO tiling.

All image work is macOS-runner-only. This constructs the reference needed for
the practical inverse, not a new inverse or proof of camera-debaked semantics.
"""
from pathlib import Path
import hashlib,json,os,resource,subprocess,sys,tarfile
import numpy as np
from PIL import Image,ImageDraw
import PyOpenColorIO as ocio

R=Path.cwd();D=R/'research/hdr-native';W=Path(os.environ['W']);O=W/'out';PRIVATE=W/'private';ENC=W/'encrypted';OLD=R/'research/vm-native/runner'
PLAN=json.loads((D/'inputs_s96.json').read_text())
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
sources=[Path(__file__).resolve(),D/'semantic_fullframe_s96.m',D/'observer_prerequisites_s96.inc',D/'encoder_capture_s96.inc',D/'s96_observer_binding.json',D/'semantic_fullframe_s95.m',D/'semantic_strength_s82.py',OLD/'native_filter_probe.m',OLD/'encoder_capture_v2.inc',OLD/'replay_helpers_v7.inc',OLD/'consumer-structured-v8.metal']
save(O/'S96-observer-binding.json', json.loads((D/'s96_observer_binding.json').read_text()))
save(O/'freeze.json',{'plan':PLAN,'source_SHA':{str(p.relative_to(R)):sha(p)for p in sources},'scope':'Original5712x4284 native consumer; real PI owner rectangles must cover all24470208 pixels once; no single physical framebuffer assumption; forward references only, no inverse','no_changes_to_frozen_models':True,'old_gates_not_relabelled':True,'engineering_accepted':False})
cipher=W/'input.gpg';photo=W/'IMG_2810.HEIC'
assert command(['gh','api','-H','Accept: application/octet-stream',f"repos/21Z121Z1/Photographic_Style_Research/releases/assets/{PLAN['input_asset_id']}"],cipher)==0
assert cipher.stat().st_size==PLAN['cipher_bytes']and sha(cipher)==PLAN['cipher_sha256']
key=os.environ.pop('SEMANTIC_S96_INPUT_SESSION').encode();rd,wr=os.pipe()
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
exe=W/'semantic-s96'
flags=['clang','-fobjc-arc','-O2','-I'+str(OLD),'-I'+str(GEN),'-framework','Foundation','-framework','CoreImage','-framework','CoreMedia','-framework','ImageIO','-framework','Metal','-Wl,-undefined,dynamic_lookup']
assert command(flags+[D/'semantic_fullframe_s96.m',D/'observer_prerequisites_s96.inc',D/'encoder_capture_s96.inc',D/'s96_observer_binding.json',D/'semantic_fullframe_s95.m','-o',exe],O/'build.log')==0
folder=PRIVATE/'full-frame'
rc=command([exe,photo,RES,folder],O/'native.log',{'XD_TONE_MAX_EDGE':'5712','XD_TONE_THUMB_MODE':'native-stage-mirror','XD_TONE_BIAS':'.35'},timeout=2400)
calls_path=folder/'semantic-full/native-calls.json'
assert calls_path.exists(),'No completed native callback; inspect native.log'
calls=json.loads(calls_path.read_text());save(O/'native-calls.json',calls)
save(O/'native-execution.json',{'returncode':rc,'source_unscaled':True,'requested_canvas':[4284,5712],'calls':len(calls['calls']),'region_reference_count':sum(bool(x.get('region_reference_available'))for x in calls['calls']),'inverse_executed':False,'native_child_peak_RSS_bytes_macOS':resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss})
regions=[c for c in calls['calls']if c.get('region_reference_available')and c.get('all_original_textures_and_buffers_unchanged')]
assert rc==0 and calls['processes'] and all(x['original_process_return']==0 for x in calls['processes']), 'Original native process failed; inspect nested guided returns and allocator events'
assert regions and len(regions)==len(calls['calls']),'Unproven final owner layout or hydration; census does not certify the full photo'
assert all(x['native_hydration']['half_differing_components']==0 for x in regions)
shape=(4284,5712);scratch=W/'comparison';scratch.mkdir();paths={};assembling=[]
def rgba(path,dtype='<f2',hw=shape):
    assert path.stat().st_size==hw[0]*hw[1]*4*np.dtype(dtype).itemsize
    return np.memmap(path,dtype=dtype,mode='r',shape=(*hw,4))
coverage=np.zeros(shape,'u1');owners=[]
for native in regions:
    x,y,w,h=native['CI_owner']['output_region'];assert all(float(v).is_integer()for v in[x,y,w,h]);x,y,w,h=map(int,[x,y,w,h]);top=shape[0]-y-h
    assert 0<=x<x+w<=shape[1]and 0<=top<top+h<=shape[0]and native['output_shape']==[h,w]
    coverage[top:top+h,x:x+w]+=1;owners.append((native,x,top,w,h))
assert np.all(coverage==1),'Owner rectangles must cover each original pixel exactly once; no hidden holes/overlap'
save(O/'owner-coverage.json',{'source_canvas':list(shape),'pixels':int(coverage.size),'owner_regions':len(owners),'minimum_coverage':int(coverage.min()),'maximum_coverage':int(coverage.max()),'uncovered_pixels':int((coverage==0).sum()),'overlapped_pixels':int((coverage>1).sum()),'coordinate_rule_frozen':'Top-left y=H-(CI_y+CI_h), based on prior S91 native bitmap ramp; no flip selected by image errors'})
del coverage
for op in['original','skin-color','skin-brightness','skin-both']:
    rp=scratch/(op+'-reference.f16');tp=scratch/(op+'-stitched.f16');ref=np.memmap(rp,mode='w+',dtype='<f2',shape=(*shape,4));tile=np.memmap(tp,mode='w+',dtype='<f2',shape=(*shape,4));sse=0.;bits=0;maximum=0.;nf=0;proof=[]
    for native,x,top,w,h in owners:
        folder_region=folder/'semantic-full'/('dispatch-'+str(native['serial']));src=folder_region/('native.f16'if op=='original'else op+'.f16');tr=folder_region/(op+'-stitched.f16');a=rgba(src,hw=(h,w));b=rgba(tr,hw=(h,w))
        for row in range(0,h,128):
            stop=min(row+128,h);ref[top+row:top+stop,x:x+w]=a[row:stop];tile[top+row:top+stop,x:x+w]=b[row:stop]
        trial=next(z for z in native['trials']if z['operator']==op);sse+=sum(z['metrics']['SSE_RGB']for z in trial['patches']);bits+=trial['tile_half_differing_components'];nf+=trial['tile_nonfinite_components'];maximum=max(maximum,trial['tile_max_abs']);proof.append({'serial':native['serial'],'CI_owner':native['CI_owner'],'parameter_changes':trial['changes'],'outside_target_bytes':trial['changed_bytes_outside_target'],'source_SHA256':sha(src),'temporary_stitched_SHA256':sha(tr)})
        del a,b
        tr.unlink() # New per-run comparison copy; native source is retained.
    ref.flush();tile.flush();del ref,tile;paths[op]=(rp,tp)
    assembling.append({'operator':op,'tile_max_abs':maximum,'tile_half_differing_components':bits,'tile_nonfinite_components':nf,'tile_PSNR_peak1_dB':'inf'if sse==0 else float(-10*np.log10(sse/(shape[0]*shape[1]*3))),'owner_proofs':proof})
native={'trials':assembling};p=scratch;base=rgba(paths['original'][0]);ci=rgba(folder/'renderer.f32','<f4');color_max=0.;ci_nf=0;ci_nonzero=0;native_nonzero=0;ci_sse=0.
for y in range(0,shape[0],128):
    a=np.array(base[y:y+128,:,:3],'f4',copy=True);b=np.array(ci[y:y+128,:,:3],'f4',copy=True);delta=a.astype('f8')-b
    color_max=max(color_max,float(np.max(abs(delta))));ci_sse+=float(np.sum(delta*delta));ci_nf+=int((~np.isfinite(b)).sum());ci_nonzero+=int(np.count_nonzero(b));native_nonzero+=int(np.count_nonzero(a))
color_psnr='inf'if ci_sse==0 else float(-10*np.log10(ci_sse/(shape[0]*shape[1]*3)))
qualified=color_max<=1e-5 and ci_nf==0 and ci_nonzero>0 and native_nonzero>0 and(color_psnr=='inf'or color_psnr>=60)
save(O/'native-CI-fullframe.json',{'max_abs':color_max,'PSNR_peak1_dB':color_psnr,'CI_nonfinite_RGB':ci_nf,'CI_nonzero_RGB':ci_nonzero,'native_nonzero_RGB':native_nonzero,'pixels':shape[0]*shape[1],'qualified':qualified})
cfg=ocio.Config.CreateFromBuiltinConfig('cg-config-v2.2.0_aces-v1.3_ocio-v2.4');cpu=cfg.getProcessor('Linear P3-D65','sRGB - Display','ACES 1.0 - SDR Video',ocio.TRANSFORM_DIR_FORWARD).getDefaultCPUProcessor()
Y=np.array([.228974564,.691738522,.079286914],'f8');preview_checks=[]
def display(a):
    before=hashlib.sha256(a.tobytes()).hexdigest();x=np.array(a,'f4',order='C',copy=True)
    cpu.apply(ocio.PackedImageDesc(x,x.shape[1],x.shape[0],3))
    after=hashlib.sha256(a.tobytes()).hexdigest();assert before==after
    preview_checks.append({'before':before,'after':after})
    return np.rint(np.clip(x,0,1)*255).astype('u1')
def stats(v):
    if not v:return {'n':0,'p50':None,'p95':None,'p99':None,'max':None}
    x=np.concatenate(v)
    if not x.size:return {'n':0,'p50':None,'p95':None,'p99':None,'max':None}
    return {'n':int(x.size),'p50':float(np.quantile(x,.5)),'p95':float(np.quantile(x,.95)),'p99':float(np.quantile(x,.99)),'max':float(x.max())}
rows=[];pictures=[]
for trial in native['trials']:
    op=trial['operator'];ref=rgba(paths[op][0]);tile=rgba(paths[op][1])
    before_hash=sha(paths[op][0]);hist=np.zeros(256,dtype='u8');ev=[];ev_excluded=0;gradient_max=0.;seam_max=0.;seam_sum=0.;seam_count=0;nf=0
    for y in range(0,shape[0],128):
        end=min(shape[0],y+128);aa=np.array(tile[y:end,:,:3],'f4',copy=True);bb=np.array(ref[y:end,:,:3],'f4',copy=True)
        nf+=int((~np.isfinite(aa)).sum());codes=np.max(abs(display(aa).astype('i2')-display(bb).astype('i2')),axis=-1)
        hist+=np.bincount(codes.ravel(),minlength=256).astype('u8')
        ya=aa@Y;yb=bb@Y;eligible=np.isfinite(ya)&np.isfinite(yb)&(yb>1/255)&(ya>0);ev_excluded+=int((~eligible).sum());ev.append(abs(np.log2(ya[eligible]/yb[eligible])).astype('f4'))
        # Include the next row so the vertical strip boundaries are measured.
        top=min(shape[0],end+1);delta=(np.array(tile[y:top,:,:3],'f8')-np.array(ref[y:top,:,:3],'f8'))@Y
        gx=np.diff(delta[:end-y],axis=1);gy=np.diff(delta,axis=0)
        gradient_max=max(gradient_max,float(np.max(abs(gx))),float(np.max(abs(gy))))
        sx=abs(gx[:,511::512]);global_y=np.arange(y,y+gy.shape[0]);sy=abs(gy[(global_y+1)%384==0])
        for z in[sx,sy]:
            if z.size:seam_max=max(seam_max,float(z.max()));seam_sum+=float(z.sum());seam_count+=z.size
    assert sha(paths[op][0])==before_hash
    cum=np.cumsum(hist);n=int(cum[-1]);maxcode=int(np.flatnonzero(hist)[-1]);p99=int(np.searchsorted(cum,np.ceil(n*.99)))
    psnr=trial['tile_PSNR_peak1_dB'];psnr_ok=psnr=='inf'or psnr>=PLAN['practical_patch_gate']['PSNR_peak1_min_dB']
    practical=qualified and trial['tile_max_abs']<=PLAN['practical_patch_gate']['linear_max_abs']and psnr_ok and p99<=PLAN['practical_patch_gate']['ACES_p99_pixel_Linf_codes']and maxcode<=PLAN['practical_patch_gate']['ACES_max_codes']and nf==0
    strict_float=trial['tile_max_abs']<=1e-5 and(psnr=='inf'or psnr>=60)and nf==0
    row={'operator':op,'native_trial':trial,'whole_reference_SHA256':before_hash,'stitched_SHA256':sha(paths[op][1]),'full_frame_pixels':n,'ACES_p99_pixel_Linf_codes':p99,'ACES_max_codes':maxcode,'ACES_pixels_gt1':int(hist[2:].sum()),'ACES_pixels_gt4':int(hist[5:].sum()),'EV_Y_threshold_reference_gt1_over255':stats(ev),'EV_excluded_pixels':ev_excluded,'gradient_error_max':gradient_max,'regular_tile_boundary_gradient_max':seam_max,'regular_tile_boundary_gradient_mean':seam_sum/seam_count if seam_count else None,'regular_tile_boundary_gradient_count':seam_count,'nonfinite_output_RGB':nf,'new_practical_patch_gate':practical,'old_float_gate':strict_float,'old_half_bit_exact':trial['tile_half_differing_components']==0,'no_inverse_claim':True}
    rows.append(row);save(O/'analysis-checkpoint.json',{'rows':rows,'full_frame_native_reference':True,'inverse_executed':False})
    if qualified:
        small=np.array(ref[::10,::10,:3],'f4',copy=True)
        image=Image.fromarray(display(small));image=Image.fromarray(np.rot90(np.asarray(image),3));image.thumbnail((450,600));pictures.append((op,image))
    # These are this run's reproducible temporary comparison arrays; originals,
    # native reference arrays and historical outputs are never removed.
    del tile
    paths[op][1].unlink()

# Three exact native conditional controls are retained at original resolution.
# Their 0.5 ACES previews are independent of the original photograph baseline.
if qualified:
    primary=rgba(folder/'primary_input.f32','<f4');s=np.array(primary[::10,::10,:3],'f4',copy=True);im=Image.fromarray(np.rot90(display(s),3));im.thumbnail((450,600));pictures.insert(0,('Original SDR',im))
    for op in['skin-color','skin-brightness','skin-both']:
        neutral=rgba(paths[op][0]);b=np.array(base[::10,::10,:3],'f4',copy=True);o=np.array(neutral[::10,::10,:3],'f4',copy=True)
        q=apply(b,b,o,.5)['rgb'];im=Image.fromarray(np.rot90(display(q),3));im.thumbnail((450,600));pictures.append((op+' native-oracle 50%',im))
    sheet=Image.new('RGB',(450*4,630*2),'white');draw=ImageDraw.Draw(sheet)
    for i,(label,im)in enumerate(pictures):
        x=(i%4)*450;y=(i//4)*630;sheet.paste(im,(x,y));draw.text((x+5,y+603),label,fill='black')
    sheet.save(PRIVATE/'fullframe-native-semantic-ACES-contact.png')
assert all(x['before']==x['after']for x in preview_checks)
controls_nonzero={op:sum(z['difference_from_original']['half_differing_components'] for region in regions for z in region['trials'] if z['operator']==op)>0 for op in ['skin-color','skin-brightness','skin-both']}
summary={'native_target_controls_nonzero':controls_nonzero,'assembly_coverage_complete':True,'os_build':'26A434','image_version':os.environ.get('ImageVersion'),'source_canvas':list(shape),'native_full_frame_reference':qualified,'full_original_frame_pixels':shape[0]*shape[1],'photo_count':1,'rows':rows,'native_CI_P3_max_abs':color_max,'native_CI_P3_PSNR_peak1_dB':color_psnr,'native_owner_regions':len(owners),'native_CI_P3_nonfinite':ci_nf,'native_CI_P3_qualified':qualified,'preview_input_SHA_checks':preview_checks,'display':{'view':'ACES 1.0 - SDR Video','source':'Linear P3-D65','display':'sRGB - Display','exposure_EV':0,'config_SHA256':hashlib.sha256(cfg.serialize().encode()).hexdigest()},'all_new_practical_patch_gates_pass':all(r['new_practical_patch_gate']for r in rows)and all(controls_nonzero.values()),'inverse_executed':False,'camera_baked_semantics_restored':False,'face_body_actual_EV_identified':False,'frozen_models_or_old_thresholds_changed':False,'engineering_accepted':False,'A_phase_complete':False,'acceptance_complete':False}
save(O/'analysis.json',summary)
# CI comparison arrays are regenerable and deliberately not archived a second
# time. Preserve their hashes; only new per-run temporary copies are removed.
discard=[]
for name in['primary_input.f32','renderer.f32','thumbnail_input.f32']:
    path=folder/name
    if path.exists():discard.append({'path':str(path.relative_to(PRIVATE)),'bytes':path.stat().st_size,'sha256':sha(path)});path.unlink()
save(PRIVATE/'temporary-comparison-array-hashes.json',{'purpose':'Avoid duplicate large evidence outputs; original native reference arrays retained. These files were generated in this run only.','files':discard})
save(PRIVATE/'manifest.json',{'run_id':os.environ['GITHUB_RUN_ID'],'commit':os.environ['GITHUB_SHA'],'os_build':'26A434','files':[{'path':str(p.relative_to(PRIVATE)),'size':p.stat().st_size,'sha256':sha(p)}for p in sorted(PRIVATE.rglob('*'))if p.is_file()]})
with tarfile.open(W/'private.tar.gz','w:gz')as tar:tar.add(PRIVATE,arcname='out')
assert command(['gpg','--batch','--trust-model','always','--recipient','28E62F64A29764C2F2AEBF5D5B6B1C101E5F5ABA','--output',ENC/'results.tar.gz.gpg','--encrypt',W/'private.tar.gz'],O/'encrypt.log')==0
save(O/'encrypted-inventory.json',{'file':'results.tar.gz.gpg','bytes':(ENC/'results.tar.gz.gpg').stat().st_size,'sha256':sha(ENC/'results.tar.gz.gpg'),'plaintext_uploaded':False})
print(json.dumps({'full_frame_native_reference':qualified,'pixels':shape[0]*shape[1],'operator_comparisons':len(rows),'new_practical_patch_gates_pass':summary['all_new_practical_patch_gates_pass'],'inverse_executed':False,'A_phase_complete':False}))
