"""Runner-only practical semantic controls from immutable native observations.

No new preimage search, native precision fitting, or S15/S16 oracle-selected
patch is used. Native counterfactuals are held references, never solver inputs.
"""
from pathlib import Path
import hashlib,json,os,platform,shutil,subprocess,tarfile,zipfile,math,csv
import numpy as np
import PyOpenColorIO as ocio
from PIL import Image,ImageDraw
from semantic_strength_s82 import apply

D=Path('research/hdr-native');W=Path(os.environ['W']);O=W/'out';PRIVATE=W/'private';ENC=W/'encrypted'
PLAN=json.loads((D/'inputs_s82.json').read_text());H,WIDTH,_=PLAN['shape'];OPS=['skin-color','skin-brightness','skin-both']
Y=np.array([.22897456,.69173852,.07928691],'f8')
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,obj):
    with Path(p).open('x')as f:json.dump(obj,f,indent=2,allow_nan=False);f.write('\n')
def command(args,log,*,env=None,timeout=300):
    with Path(log).open('x')as f:r=subprocess.run(list(map(str,args)),env=env,stdout=f,stderr=subprocess.STDOUT,timeout=timeout)
    if r.returncode:raise RuntimeError('Subprocess failed; inspect '+Path(log).name)
def image(p,channels=4,dtype='<f2'):
    a=np.fromfile(p,dtype=dtype).reshape(H,WIDTH,channels)
    return a[...,:3].astype('f4')
assert platform.system()=='Darwin' and subprocess.check_output(['sw_vers','-buildVersion'],text=True).strip()=='26A434'
assert PLAN['total_input_transfer_bytes']==110814893<1_000_000_000
assert shutil.disk_usage(W).free>3_000_000_000
sources=[D/n for n in ['run_hdr_s82.py','semantic_strength_s82.py','inputs_s82.json']]
freeze={'scope':PLAN['scope'],'os_build':'26A434','image_version':os.environ.get('ImageVersion'),'input_plan':PLAN,'source_sha256':{str(p):sha(p)for p in sources},'recipe':'C=y+(F_neutral(xhat)-F(xhat)); positive RGB ratio g=log2(C/y), result=y*exp2(alpha*g). Preserve y outside the explicit ratio domain. No matte resize/smoothing, global/local/texture/tone change or curve fit.','strength_scope':'Output-effect interpolation; not the Apple theta interpolation or a measured camera amplitude.','oracle_scope':'Original frozen consumer only-theta9/10 zeroing; expected oracle arrays are comparison-only.','legacy_thresholds_not_reclassified_as_passed':True,'default_strength':.5,'precision_research':False,'full_resolution_or_five_photos_pass':False,'global_local_inverse_combined':False}
save(O/'freeze.json',freeze);freeze_sha=sha(O/'freeze.json')
keys={c['stage']:os.environ.pop(c['session_env']).encode()for c in PLAN['cases']}
roots={};verification=[]
for c in PLAN['cases']:
    assert sha(O/'freeze.json')==freeze_sha
    folder=W/c['stage'];folder.mkdir();root=folder/'selected';root.mkdir();zip_path=folder/c['asset']
    command(['gh','release','download',PLAN['release_tag'],'--repo','21Z121Z1/Photographic_Style_Research','--pattern',c['asset'],'--dir',folder],W/(c['stage']+'-download.log'),timeout=600)
    assert zip_path.stat().st_size==c['ZIP_bytes']and sha(zip_path)==c['ZIP_sha256']
    wanted={x['path']:x for x in c['selected_files']}
    with zipfile.ZipFile(zip_path)as z:
        assert c['cipher_member']in z.namelist()
        with z.open(c['cipher_member'])as f:assert hashlib.file_digest(f,'sha256').hexdigest()==c['cipher_sha256']
        readfd,writefd=os.pipe();session=keys.pop(c['stage']);tar_path=folder/'plain.tar.gz'
        with (folder/'private-gpg-stderr.log').open('xb')as err,tar_path.open('xb')as output:
            child_env=os.environ.copy();child_env.pop('GH_TOKEN',None)
            p=subprocess.Popen(['gpg','--batch','--override-session-key-fd',str(readfd),'--status-fd','2','--decrypt'],pass_fds=(readfd,),stdin=subprocess.PIPE,stdout=output,stderr=err,env=child_env)
            os.close(readfd);os.write(writefd,session+b'\n');os.close(writefd);del session
            with z.open(c['cipher_member'])as source:shutil.copyfileobj(source,p.stdin,1<<16)
            p.stdin.close();rc=p.wait(timeout=120)
        events=[x.split()[1]for x in(folder/'private-gpg-stderr.log').read_text(errors='replace').splitlines()if x.startswith('[GNUPG:] ')]
        assert rc==0 and 'DECRYPTION_OKAY'in events
    actual={};manifest=None
    with tarfile.open(tar_path,'r:gz')as tar:
        for m in tar:
            if m.isdir():continue
            assert m.isfile() and m.size<512_000_000
            name=Path(m.name);assert name.parts[0]=='out'and not name.is_absolute()and'..'not in name.parts
            rel=str(name.relative_to('out'));assert rel not in actual
            h=hashlib.sha256();buf=bytearray()if rel=='manifest.json'else None
            output=None
            if rel in wanted:
                target=root/rel;target.parent.mkdir(parents=True,exist_ok=True);output=target.open('xb')
            with tar.extractfile(m)as f:
                while block:=f.read(1<<20):
                    h.update(block)
                    if output:output.write(block)
                    if buf is not None:buf.extend(block)
            if output:output.close()
            actual[rel]={'size':m.size,'sha256':h.hexdigest()}
            if rel=='manifest.json':
                assert h.hexdigest()==c['manifest_sha256'];manifest=json.loads(buf)
    assert manifest is not None and len({r['path']for r in manifest['files']})==len(manifest['files'])
    assert set(actual)=={r['path']for r in manifest['files']}|{'manifest.json'}
    for row in manifest['files']:assert actual[row['path']]=={'size':row['size'],'sha256':row['sha256']}
    for name,row in wanted.items():assert actual[name]=={'size':row['size'],'sha256':row['sha256']}and sha(root/name)==row['sha256']
    verification.append({'stage':c['stage'],'original_run':c['original_run_id'],'ZIP_bytes':c['ZIP_bytes'],'ZIP_sha256':c['ZIP_sha256'],'cipher_sha256':c['cipher_sha256'],'manifest_sha256':c['manifest_sha256'],'all_manifest_members_verified':len(manifest['files']),'selected_files':len(wanted),'GPG_returncode':rc,'GPG_status_event_names_only':events,'old_polluted_face_body_arrays_used':False})
    roots[c['stage']]=root
    zip_path.unlink();tar_path.unlink()
assert not keys
os.environ.pop('GH_TOKEN',None)
save(O/'input-verification.json',verification)

# Synthetic robustness checks concern only this new strength control.
b=np.array([[1.,2.,4.],[0.,1.,2.],[-1.,1.,2.],[.1,.2,.3]],'f4');f=b.copy();n=b.copy();n[0]*=2;n[3]*=.5
for x in [b,f,n]:x.flags.writeable=False
zero=apply(b,f,n,0);mid=apply(b,f,n,.5);end=apply(b,f,n,1)
assert np.array_equal(zero['rgb'].view('u4'),b.view('u4'))
assert np.allclose(mid['rgb'][0],b[0]*math.sqrt(2),rtol=1e-7)
assert np.array_equal(mid['rgb'][1:3],b[1:3])and np.array_equal(end['rgb'][[0,3]],n[[0,3]])
bad=b.copy();bad[0,0]=np.nan;q=apply(bad,f,n,.5);assert not q['ratio_valid'][0]and np.isnan(q['rgb'][0,0])
save(O/'strength-controls.json',{'identity_bit_exact':True,'known_geometric_midpoint':True,'nonpositive_preserved':True,'nonfinite_context_explicit':True,'readonly_inputs_supported':True,'scope':'Control of custom interpolation only; no new native or camera inverse validation'})

P=roots['s5']/'consumer-toneP035/semantic';S=roots['s8']/'native'
base=image(P/'native.f16');renderer=image(roots['s5']/'consumer-toneP035/renderer.f32',dtype='<f4')
color_error=float(np.max(abs(renderer.astype('f8')-base)))
assert np.isfinite(base).all()and color_error<=1e-5,'Captured output space not qualified for existing fixed ACES preview'
native=json.loads((P/'results.json').read_text());context=json.loads((S/'s8-context.json').read_text());rt=image(S/'new-roundtrip.f16')
assert native['native_hydration']['half_differing_components']==0 and context['context_mismatches']==[]and context['fresh_native_vs_S5']['half_differing_components']==0
assert context['original_input_used_as_seed']is False
assert len(native['trials'])==3 and all(x['changed_bytes_outside_target']==0 for x in native['trials'])
eligible=np.fromfile(S/'original-eligible.u8','u1').reshape(H,WIDTH).astype(bool)
assert np.array_equal(eligible,np.isfinite(base).all(-1)&(base>1/255).all(-1))and eligible.sum()==186949
matte=np.fromfile(P/'texture-11.bin','<f2').reshape(H,WIDTH).astype('f8');pad=np.pad(matte,1,mode='edge')
mx=np.maximum.reduce([pad[a:a+H,b:b+WIDTH]for a in range(3)for b in range(3)])
mn=np.minimum.reduce([pad[a:a+H,b:b+WIDTH]for a in range(3)for b in range(3)])
footprint=mx>0;edge=(mx-mn)>1/255;background=~footprint
cfg=ocio.Config.CreateFromBuiltinConfig('cg-config-v2.2.0_aces-v1.3_ocio-v2.4');cfg_sha=hashlib.sha256(cfg.serialize().encode()).hexdigest();assert cfg_sha==PLAN['display_config_sha256']
cpu=cfg.getProcessor('Linear P3-D65','sRGB - Display','ACES 1.0 - SDR Video',ocio.TRANSFORM_DIR_FORWARD).getDefaultCPUProcessor()
display={'config':'cg-config-v2.2.0_aces-v1.3_ocio-v2.4','config_sha256':cfg_sha,'source':'Linear P3-D65','display':'sRGB - Display','view':'ACES 1.0 - SDR Video','exposure_ev':0,'orientation':'Existing irot3 capture; rotate90 clockwise for display only'}
preview_checks=[];cards=[];roi_cards=[]
def preview(rgb,label):
    before=hashlib.sha256(np.ascontiguousarray(rgb).tobytes()).hexdigest();x=np.array(rgb,'f4',order='C',copy=True);assert np.isfinite(x).all()
    cpu.apply(ocio.PackedImageDesc(x,x.shape[1],x.shape[0],3));im=Image.fromarray(np.rot90(np.rint(np.clip(x,0,1)*255).astype('u1'),3))
    after=hashlib.sha256(np.ascontiguousarray(rgb).tobytes()).hexdigest();assert before==after
    preview_checks.append({'name':label,'before_sha256':before,'after_sha256':after})
    return im
def summary(values):
    z=np.asarray(values,'f8');z=z[np.isfinite(z)]
    if not z.size:return {'count':0,'median':None,'p95':None,'p99':None,'max':None}
    return {'count':int(z.size),'median':float(np.median(z)),'p95':float(np.quantile(z,.95)),'p99':float(np.quantile(z,.99)),'max':float(z.max())}
def metrics(a,b,region):
    finite=np.isfinite(a).all(-1)&np.isfinite(b).all(-1);m=region&finite;d=abs(a.astype('f8')-b);lum_a=a@Y;lum_b=b@Y;evmask=m&(lum_a>0)&(lum_b>0)
    rgbrel=np.max(d/np.maximum(abs(b),1e-12),-1)
    ca=a/np.maximum(np.sum(a,axis=-1,keepdims=True),1e-12);cb=b/np.maximum(np.sum(b,axis=-1,keepdims=True),1e-12)
    return {'requested_region_pixels':int(region.sum()),'finite_pixels':int(m.sum()),'finite_coverage_of_frame':float(m.mean()),'nonfinite_in_requested_region':int((region&~finite).sum()),'max_abs':float(d[m].max())if m.any()else None,'RGB_relative_error':summary(rgbrel[m]),'EV_abs_error':summary(abs(np.log2(lum_a[evmask]/lum_b[evmask]))),'EV_excluded_nonpositive_luma':int((m&~evmask).sum()),'chromaticity_max_abs_vs_oracle':float(abs(ca-cb)[m].max())if m.any()else None,'PSNR_peak1_dB':float(-10*np.log10(np.mean(d[m]**2)))if m.any()and d[m].any()else'inf','legacy_gt_1e3_pixels_diagnostic_only':int((m&(rgbrel>1e-3)).sum())}
def gradients(loggain):
    v=loggain@Y;gx=np.diff(v,axis=1);gy=np.diff(v,axis=0);ex=edge[:,1:]|edge[:,:-1];ey=edge[1:]|edge[:-1]
    lap=v[1:-1,2:]+v[1:-1,:-2]+v[2:,1:-1]+v[:-2,1:-1]-4*v[1:-1,1:-1]
    return {'RGB_weighted_log_gain_gradient_EV_on_matte_edge':summary(np.r_[abs(gx[ex]),abs(gy[ey])]),'RGB_weighted_log_gain_laplacian_EV_on_matte_edge':summary(abs(lap[edge[1:-1,1:-1]])),'scope':'Spatial discontinuity proxies of the chosen log-RGB correction; not a certified halo visibility score or luminance EV field'}

# Choose ROI by the unchanged captured matte, before inspecting correction error.
locations=np.argwhere(edge);assert len(locations)>0
roi_centers=[locations[len(locations)//3],locations[2*len(locations)//3]]
rows=[];endpoints=[];private_masks={};source_hashes_before={str(p.relative_to(W)):sha(p)for root in roots.values()for p in root.rglob('*')if p.is_file()}
for op in OPS:
    neutral=image(S/(op+'-new-neutral.f16'));oracle=image(P/(op+'-removed-oracle.f16'))
    # Candidate construction sees only observed target and recovered evaluations.
    # Oracle is held aside for comparison and identical strength interpolation.
    observed_change=np.any(oracle!=base,axis=-1);previous=None;shots={}
    for strength in PLAN['strengths']:
        q=apply(base,rt,neutral,strength)
        expected=apply(base,base,oracle,strength)
        rgb=q['rgb'];good=q['ratio_valid'];loggain=q['log2_gain']
        assert np.isfinite(rgb).all()and not np.shares_memory(rgb,base)
        background_change=float(np.max(abs(rgb[background]-base[background])))if background.any()else 0
        assert background_change==0,'Correction changed pixels outside frozen skin sampling support'
        if strength==0:assert np.array_equal(rgb.view('u4'),base.view('u4'))
        if previous is not None:
            delta=rgb.astype('f8')-previous.astype('f8');direction=neutral.astype('f8')-rt
            assert not np.any((delta*direction<-1e-10)&good[...,None]),'Output strength is not monotone'
        previous=rgb.copy()
        restored=rgb.astype('f8')*np.exp2(-loggain);restored[~good]=rgb[~good]
        row={'operator':op,'strength':strength,'shape':[H,WIDTH,3],'ratio_valid_pixels':int(good.sum()),'ratio_valid_coverage':float(good.mean()),'preserved_outside_ratio_domain_pixels':int((~good).sum()),'candidate_nonpositive_pixels':int(q['candidate_nonpositive'].sum()),'base_nonpositive_pixels':int(q['base_nonpositive'].sum()),'nonfinite_context_pixels':int(q['nonfinite_context'].sum()),'background_pixels':int(background.sum()),'background_max_abs_change':background_change,'native_oracle_changed_pixels':int(observed_change.sum()),'all_frame':metrics(rgb,expected['rgb'],np.ones((H,WIDTH),bool)),'legacy_eligible':metrics(rgb,expected['rgb'],eligible),'skin_footprint_eligible':metrics(rgb,expected['rgb'],eligible&footprint),'native_affected_eligible':metrics(rgb,expected['rgb'],eligible&observed_change),'correction_log2_RGB_abs_EV':summary(abs(loggain[good]).ravel()),'chosen_transform_roundtrip_max_abs':float(abs(restored.astype('f4')-base).max()),**gradients(loggain)}
        rows.append(row)
        if strength in [0,.5,1]:shots[strength]=preview(rgb,op+'-'+str(strength))
        if strength in [.5,1]:
            for i,(cy,cx)in enumerate(roi_centers):
                x=max(0,min(WIDTH-64,int(cx)-32));y=max(0,min(H-64,int(cy)-32));crop=preview(rgb[y:y+64,x:x+64],f'{op}-{strength}-ROI{i}')
                if op=='skin-both':roi_cards.append((strength,i,crop))
        if strength==.5:private_masks[op+'_ratio_invalid']=~good
        if strength==1:
            endpoints.append({'operator':op,'reference':'Original unchanged native zero-parameter counterfactual, including nonpositive components; not the interpolated reference','all_finite_frame':metrics(rgb,oracle,np.ones((H,WIDTH),bool)),'legacy_eligible':metrics(rgb,oracle,eligible),'native_affected_eligible':metrics(rgb,oracle,eligible&observed_change),'native_changed_pixels_outside_ratio_domain':int((observed_change&~good).sum()),'outside_ratio_domain_max_abs_native_change':float(abs(oracle[~good]-base[~good]).max())if(~good).any()else 0})
    cards.append((op,shots))

sheet=Image.new('RGB',(3*192,3*280),'white');draw=ImageDraw.Draw(sheet)
for r,(op,shots)in enumerate(cards):
    for c,s in enumerate([0,.5,1]):
        im=shots[s].copy();im.thumbnail((192,256));sheet.paste(im,(c*192,r*280));draw.text((c*192+3,r*280+258),f'{op}  {int(100*s)}%',fill='black')
sheet.save(PRIVATE/'skin-strength-contact.png',optimize=True)
roi_sheet=Image.new('RGB',(2*128,2*152),'white');draw=ImageDraw.Draw(roi_sheet)
for strength,index,im in roi_cards:
    col=0 if strength==.5 else 1;roi_sheet.paste(im.resize((128,128),Image.Resampling.NEAREST),(col*128,index*152));draw.text((col*128+3,index*152+130),f'ROI{index} {int(100*strength)}%',fill='black')
roi_sheet.save(PRIVATE/'skin-both-ROI-contact.png',optimize=True)
np.savez_compressed(PRIVATE/'ratio-domain-masks.npz',**private_masks)
save(PRIVATE/'meaning.json',{'scope':PLAN['scope'],'display':display,'rows':'skin-color / skin-brightness / joint removal','columns':'0%,50%,100% of output-effect log-RGB correction; not Apple parameter values','ROI_selection':'Two fixed order-statistic locations from unchanged captured matte edge before correction-error inspection','ROI_centers_native_yx':[x.tolist()for x in roi_centers],'0_percent':'Same native tone+.35 consumer baseline. This is not an original SDR versus scene comparison.','model_limit':'One384x512 IMG2810 consumer capture, not full original resolution, calibrated j, camera-ground-truth skin, texture removal or combined GTM/LTM inverse.'})
source_hashes_after={str(p.relative_to(W)):sha(p)for root in roots.values()for p in root.rglob('*')if p.is_file()};assert source_hashes_before==source_hashes_after and sha(O/'freeze.json')==freeze_sha
report={'os_build':'26A434','image_version':os.environ.get('ImageVersion'),'freeze_sha256':freeze_sha,'scope':PLAN['scope'],'capture':'IMG_2810, native consumer tone+.35, type/context from original S5/S8','shape':[H,WIDTH,3],'photo_count':1,'new_holdouts':0,'full_original_resolution':False,'new_native_pixel_execution':False,'new_preimage_search':False,'oracle_error_selected_S15_S16_patch_used':False,'native_output_vs_CI_linear_P3_max_abs':color_error,'native_target_parameter_only_controls':native['trials'],'same_native_context':True,'input_files_before_after_SHA_unchanged':True,'input_source_hashes':source_hashes_before,'display':display,'preview_input_checks':preview_checks,'rows':rows,'unmodified_native_endpoint_comparisons':endpoints,'separate_GTM_LTM_unchanged':True,'LinearThumbnail_Apple_Log_unchanged':True,'old_face_body_polluted_metrics_used':False,'face_body_actual_EV_identified':False,'legacy_inverse_proof_or_mask_changed':False,'engineering_accepted':False,'visual_review':'pending; encrypted contacts only, no appearance claim from scalar metrics','physical_scene_verified':False,'A_phase_complete':False,'acceptance_complete':False}
save(O/'analysis.json',report)
save(O/'versions.json',{'python':platform.python_version(),'numpy':np.__version__,'OpenColorIO':ocio.__version__,'image_version':os.environ.get('ImageVersion')})
save(PRIVATE/'manifest.json',{'run_id':os.environ['GITHUB_RUN_ID'],'commit':os.environ['GITHUB_SHA'],'os_build':'26A434','people_results_encrypted':True,'files':[{'path':p.name,'size':p.stat().st_size,'sha256':sha(p)}for p in sorted(PRIVATE.iterdir())if p.is_file()]})
with tarfile.open(W/'previews.tar.gz','w:gz')as tar:tar.add(PRIVATE,arcname='out')
command(['gpg','--batch','--trust-model','always','--recipient','28E62F64A29764C2F2AEBF5D5B6B1C101E5F5ABA','--encrypt','--output',ENC/'previews.tar.gz.gpg',W/'previews.tar.gz'],O/'preview-encrypt.log')
cipher=ENC/'previews.tar.gz.gpg';assert cipher.stat().st_size<PLAN['private_cipher_max_bytes']
save(O/'encrypted-inventory.json',{'file':cipher.name,'size':cipher.stat().st_size,'sha256':sha(cipher),'plaintext_uploaded':False,'contains':'PNG contact previews and ratio-domain masks, no full images/new EXR/native shader'})
print(json.dumps({'completed':True,'capture_pixels':H*WIDTH,'operators':len(OPS),'strengths':len(PLAN['strengths']),'new_native_search':False,'encrypted_preview_bytes':cipher.stat().st_size,'engineering_accepted':False}))
