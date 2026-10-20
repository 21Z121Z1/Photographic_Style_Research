"""Runner-only real-input domain comparisons; no inverse/physical-truth claim."""
from pathlib import Path
import hashlib,json,zlib,functools
import numpy as np
import PyOpenColorIO as ocio
from PIL import Image,ImageDraw
Y=np.array([.228974564,.691738522,.079286914],'f8');SHAPE=(4284,5712)
_CHECKS=[]
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,v):p.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def image(p,hw=SHAPE,dtype='<f4',channels=4):
    assert p.stat().st_size==hw[0]*hw[1]*channels*np.dtype(dtype).itemsize
    return np.memmap(p,mode='r',dtype=dtype,shape=(*hw,channels))
@functools.lru_cache(maxsize=1)
def processor():
    cfg=ocio.Config.CreateFromBuiltinConfig('cg-config-v2.2.0_aces-v1.3_ocio-v2.4');digest=hashlib.sha256(cfg.serialize().encode()).hexdigest();assert digest=='5aefc668796eabb1902b9593340496231758eceaec18ce290e12901042bd4440'
    return cfg.getProcessor('Linear P3-D65','sRGB - Display','ACES 1.0 - SDR Video',ocio.TRANSFORM_DIR_FORWARD).getDefaultCPUProcessor()
def display(a):
    before=hashlib.sha256(a.tobytes()).hexdigest();v=np.array(a,'f4',order='C',copy=True);processor().apply(ocio.PackedImageDesc(v,v.shape[1],v.shape[0],3));after=hashlib.sha256(a.tobytes()).hexdigest();assert before==after;_CHECKS.append({'before':before,'after':after});return np.rint(np.clip(v,0,1)*255).astype('u1')
def summary(parts):
    if not parts or not sum(a.size for a in parts):return {'n':0,'p50':None,'p99':None,'max':None}
    a=np.concatenate(parts);return {'n':int(a.size),'p50':float(np.quantile(a,.5)),'p99':float(np.quantile(a,.99)),'max':float(a.max())}
def analyze_case(label,tone,folder,calls,facts,out,private):
    source=image(folder/'primary_input.f32');result=image(folder/'renderer.f32');maximum=0.;sse=0.;nf=0;different=0;half_different=0;ev=[];hist=np.zeros(256,'u8')
    for top in range(0,SHAPE[0],32):
        a=np.array(source[top:top+32,:,:3],'f4',copy=True);b=np.array(result[top:top+32,:,:3],'f4',copy=True);d=b.astype('f8')-a
        maximum=max(maximum,float(abs(d).max()));sse+=float((d*d).sum());nf+=int((~np.isfinite(b)).sum());different+=int((a!=b).any(-1).sum());half_different+=int((a.astype('f2')!=b.astype('f2')).any(-1).sum())
        ya=a@Y;yb=b@Y;good=np.isfinite(a).all(-1)&np.isfinite(b).all(-1)&(ya>1/255)&(yb>0)
        ev.append(abs(np.log2(yb[good]/ya[good])).astype('f4'));codes=abs(display(a).astype('i2')-display(b).astype('i2')).max(-1);hist+=np.bincount(codes.ravel(),minlength=256).astype('u8')
    row={'label':label,'tone':tone,'canvas':list(SHAPE),'consumer_input_domain':'Original decoded HEIC S'if label.startswith('original')else'Frozen native Neutrino key1 reverse R, stored half then exactly widened f32','default_use_style_engine_before_override':facts.get('default_use_style_engine_before_override'),'forced_use_style_engine':False,'input_vs_output':{'scope':'Observable consumer output compared with its own input, not reconstruction/scene error','pixels':SHAPE[0]*SHAPE[1],'changed_float_RGB_pixels':different,'changed_after_half_cast_RGB_pixels':half_different,'RGB_max_abs':maximum,'PSNR_peak1_dB':'inf'if sse==0 else float(-10*np.log10(sse/(SHAPE[0]*SHAPE[1]*3))),'nonfinite_output_RGB':nf,'abs_luma_EV':summary(ev),'ACES_p99_pixel_Linf_codes':int(np.searchsorted(np.cumsum(hist),np.ceil(hist.sum()*.99))),'ACES_max_codes':int(np.flatnonzero(hist)[-1])},'native_processes':len(calls['processes']),'native_final_calls':len(calls['calls']),'camera_baked_semantics_identified':False,'key1_not_isolated_skin_factor':True}
    pictures=[(label+' input',np.array(source[::10,::10,:3],'f4',copy=True)),(label+' consumer',np.array(result[::10,::10,:3],'f4',copy=True))]
    regions=[r for r in calls['calls']if r.get('region_reference_available')and r.get('all_original_textures_and_buffers_unchanged')]
    cover=np.zeros(SHAPE,'u1');ci_max=0.;ci_nf=0;ops={k:{'active_pixels':0,'max_abs_RGB':0.,'nonfinite_components':0,'outside_target_byte_changes':0,'files':[]}for k in ['skin-color','skin-brightness','skin-both']};smalls={k:np.array(result[::10,::10,:3],'f4',copy=True)for k in ops};matte={'raw_texels':0,'positive_raw_texels':0,'zero_raw_texels':0,'nonfinite_raw_texels':0,'raw_texel_grid_is_not_internal_sampled_matte':True}
    for native in regions:
        x,y,w,h=map(int,native['CI_owner']['output_region']);top=SHAPE[0]-y-h
        assert 0<=x<x+w<=SHAPE[1]and 0<=top<top+h<=SHAPE[0]and native['output_shape']==[h,w]
        cover[top:top+h,x:x+w]+=1;p=folder/'semantic-full'/('dispatch-'+str(native['serial']));b=image(p/'native.f16',(h,w),'<f2')
        assert native['native_hydration']['half_differing_components']==0
        skin=image(p/'binding11-skin.f16',(h,w),'<f2',1)
        for sy in range(0,h,32):
            a=np.array(b[sy:sy+32,:,:3],'f4',copy=True);c=np.array(result[top+sy:top+min(sy+32,h),x:x+w,:3],'f4',copy=True);ci_max=max(ci_max,float(abs(a-c).max()));ci_nf+=int((~np.isfinite(c)).sum());m=np.asarray(skin[sy:sy+32,:,0]);matte['raw_texels']+=m.size;matte['positive_raw_texels']+=int((m>0).sum());matte['zero_raw_texels']+=int((m==0).sum());matte['nonfinite_raw_texels']+=int((~np.isfinite(m)).sum())
        for trial in native['trials']:
            name=trial['operator']
            if name not in ops:continue
            n=image(p/trial['file'],(h,w),'<f2');o=ops[name];o['outside_target_byte_changes']+=trial['changed_bytes_outside_target'];o['files'].append({'serial':native['serial'],'file':trial['file'],'native_alias':trial['same_as_original_bytes'],'sha256':sha(p/trial['file'])})
            for sy in range(0,h,32):
                stop=min(sy+32,h);a=np.array(b[sy:stop,:,:3],'f4',copy=True);c=np.array(n[sy:stop,:,:3],'f4',copy=True);o['active_pixels']+=int((a!=c).any(-1).sum());o['max_abs_RGB']=max(o['max_abs_RGB'],float(abs(a-c).max()));o['nonfinite_components']+=int((~np.isfinite(c)).sum())
                gy=np.arange(top+sy,top+stop);gx=np.arange(x,x+w);my=gy%10==0;mx=gx%10==0
                if my.any()and mx.any():smalls[name][(gy[my]//10)[:,None],gx[mx]//10]=c[my][:,mx]
            del n
        del b,skin
    complete=bool(regions)and bool(np.all(cover==1));row['native_owner_coverage']={'complete':complete,'owners':len(regions),'minimum':int(cover.min()),'maximum':int(cover.max()),'uncovered_pixels':int((cover==0).sum()),'overlapped_pixels':int((cover>1).sum()),'native_CI_RGB_max_abs':ci_max if regions else None,'nonfinite_CI_RGB':ci_nf,'no_callback_is_not_automatically_identity':True}
    row['parameter_only_controls']=ops;row['raw_skin_binding']=matte
    if regions:assert complete and ci_max<=1e-5 and ci_nf==0,'Incomplete owner/native-CI proof; retain failure evidence'
    if complete:
        for name,a in smalls.items():pictures.append((label+' '+name,a))
    else:
        # No captured final dispatch (e.g. true native bypass): retain actual full
        # output, not merely its hash or a preview. This new file is encrypted.
        path=folder/'whole-output.f16.zlib';comp=zlib.compressobj(6)
        with path.open('xb')as f:
            for top in range(0,SHAPE[0],32):f.write(comp.compress(np.asarray(result[top:top+32],dtype='<f2').tobytes()))
            f.write(comp.flush())
        save(Path(str(path)+'.json'),{'shape':[*SHAPE,4],'dtype':'<f2','compression':'zlib','sha256':sha(path),'source':'Actual CI whole output, not a synthetic identity','reason':'No complete native-final owner reference available'})
    save(out/(label+'-analysis.json'),row);del source,result,cover
    return row,pictures
def finish(rows,pictures,out,private):
    cols=4;cw=450;ch=630;sheet=Image.new('RGB',(cols*cw,((len(pictures)+cols-1)//cols)*ch),'white');draw=ImageDraw.Draw(sheet)
    for i,(label,a)in enumerate(pictures):
        im=Image.fromarray(np.rot90(display(a),3));im.thumbnail((450,600));x=(i%cols)*cw;y=(i//cols)*ch;sheet.paste(im,(x,y));draw.text((x+4,y+603),label,fill='black')
    sheet.save(private/'real-input-domain-ACES.png');save(private/'preview-input-SHA-checks.json',{'all_unchanged':True,'checks':_CHECKS})
    save(out/'analysis.json',{'os_build':'26A434','photo':'IMG_2810','cases':rows,'source_chain':'Original S -> frozen native Neutrino key1 reverse R -> separately observed consumer(Tone0/+0.35); tested chain is not Photos UI ordering proof','display':{'view':'ACES 1.0 - SDR Video','source':'Linear P3-D65','display':'sRGB - Display','exposure_EV':0,'config_SHA256':'5aefc668796eabb1902b9593340496231758eceaec18ce290e12901042bd4440'},'preview_input_SHA_count':len(_CHECKS),'preview_input_SHA_all_unchanged':True,'preview_SHA_ledger_file_SHA256':sha(private/'preview-input-SHA-checks.json'),'no_inverse_or_precision_hunt':True,'new_camera_semantic_truth_or_ImageIO_SDR_test':False,'original_j_final_EV_identified':False,'A_phase_complete':False,'engineering_accepted':False,'acceptance_complete':False})
