"""Runner-only full-frame conditional inverse assessment; no camera truth claim."""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image,ImageDraw
import PyOpenColorIO as ocio
from semantic_strength_s82 import apply

Y=np.array([.228974564,.691738522,.079286914],'f8')
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,v):p.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def image(p,hw,dtype='<f2',channels=4):
    assert p.stat().st_size==hw[0]*hw[1]*channels*np.dtype(dtype).itemsize
    return np.memmap(p,mode='r',dtype=dtype,shape=(*hw,channels))
def stats(parts):
    n=sum(a.size for a in parts)
    if not n:return {'n':0,'p50':None,'p95':None,'p99':None,'max':None}
    a=np.concatenate(parts)
    return {'n':n,'p50':float(np.quantile(a,.5)),'p95':float(np.quantile(a,.95)),'p99':float(np.quantile(a,.99)),'max':float(a.max())}
def merge(items):
    out=[]
    for lo,hi in sorted(set(items)):
        if out and lo<=out[-1][1]:out[-1]=(out[-1][0],max(hi,out[-1][1]))
        else:out.append((lo,hi))
    return out
def seams(owners,shape):
    vertical={};horizontal={}
    for _,x,top,w,h,_ in owners:
        for u in[x,x+w]:
            if 0<u<shape[1]:vertical.setdefault(u,[]).append((top,top+h))
        for v in[top,top+h]:
            if 0<v<shape[0]:horizontal.setdefault(v,[]).append((x,x+w))
    return ({k:merge(v)for k,v in vertical.items()},{k:merge(v)for k,v in horizontal.items()})
def gradient_metrics(path,shape,lines):
    a=np.memmap(path,mode='r',dtype='<f4',shape=shape);maximum=0.;smax=0.;ssum=0.;count=0;nf=0
    vertical,horizontal=lines
    for row in range(0,shape[0],128):
        stop=min(row+128,shape[0]);v=np.array(a[row:min(stop+1,shape[0])],'f8',copy=True)
        gx=np.diff(v[:stop-row],axis=1);gy=np.diff(v,axis=0);nf+=int((~np.isfinite(gx)).sum()+(~np.isfinite(gy)).sum())
        if gx.size:maximum=max(maximum,float(np.max(abs(gx))))
        if gy.size:maximum=max(maximum,float(np.max(abs(gy))))
        for x,ranges in vertical.items():
            for lo,hi in ranges:
                lo=max(row,lo);hi=min(stop,hi)
                if hi>lo:
                    z=abs(gx[lo-row:hi-row,x-1]);smax=max(smax,float(z.max()));ssum+=float(z.sum());count+=z.size
        for y,ranges in horizontal.items():
            if row<=y-1<row+gy.shape[0]:
                for lo,hi in ranges:
                    z=abs(gy[y-1-row,lo:hi]);smax=max(smax,float(z.max()));ssum+=float(z.sum());count+=z.size
    del a
    return {'all_adjacency_gradient_error_max':maximum,'actual_CI_owner_seam_gradient_error_max':smax,'actual_CI_owner_seam_gradient_error_mean':ssum/count if count else None,'actual_CI_owner_seam_edge_count':count,'nonfinite_gradients':nf,'scope':'Actual owner edges, deduplicated; this solve introduces no512x384 subpatches.'}

def analyze(plan,folder,calls,out,private,work):
    shape=(4284,5712);total=shape[0]*shape[1];owners=[];cover=np.zeros(shape,'u1');scratch=work/'comparison';scratch.mkdir()
    for row in calls['calls']:
        assert row.get('inverse_available') and row['all_original_textures_and_buffers_unchanged']
        x,y,w,h=map(int,row['CI_owner']['output_region']);top=shape[0]-y-h
        assert 0<=x<x+w<=shape[1]and 0<=top<top+h<=shape[0]and row['source_shape']==row['output_shape']==[h,w]
        assert row['inverse']['pixels']==w*h and row['inverse']['full_frame'] and row['effective_input_roundtrip_replay']['half_differing_components']==0
        p=folder/'semantic-full'/('dispatch-'+str(row['serial']));owners.append((row,x,top,w,h,p));cover[top:top+h,x:x+w]+=1
    assert np.all(cover==1),'Every original pixel must have one complete native owner inverse'
    save(out/'owner-coverage.json',{'pixels':total,'owner_regions':len(owners),'minimum_coverage':int(cover.min()),'maximum_coverage':int(cover.max()),'uncovered_pixels':int((cover==0).sum()),'overlapped_pixels':int((cover>1).sum()),'coordinate_rule_frozen':'Top-left y=H-(CI_y+CI_h); unchanged S97 native/CI-verified rule'})
    del cover
    lines=seams(owners,shape);save(out/'actual-owner-seams.json',{'vertical':lines[0],'horizontal':lines[1],'selection':'Owner geometry only, before inverse-effect errors; no output gating'})
    ci=image(folder/'renderer.f32',shape,'<f4');cm=0.;cnf=0;csse=0.;cnonzero=0;bnf=0;eligible_n=0;failed=0;maxrel=0.;rt_nf=0;mask_disagreement=0
    inverse_rows=[]
    for native,x,top,w,h,p in owners:
        b=image(p/'native.f16',(h,w));rt=image(p/'native-inverse-roundtrip.f16',(h,w));mask=image(p/'native-inverse-eligible.u8',(h,w),'u1',1);n=0;f=0;mr=0.
        for y in range(0,h,64):
            stop=min(y+64,h);bb=np.array(b[y:stop,:,:3],'f4',copy=True);cc=np.array(ci[top+y:top+stop,x:x+w,:3],'f4',copy=True);rr=np.array(rt[y:stop,:,:3],'f4',copy=True);e=np.asarray(mask[y:stop,:,0],bool)
            delta=bb.astype('f8')-cc;cm=max(cm,float(np.max(abs(delta))));csse+=float(np.sum(delta*delta));cnf+=int((~np.isfinite(cc)).sum());bnf+=int((~np.isfinite(bb)).sum());cnonzero+=int(np.count_nonzero(cc));rt_nf+=int((~np.isfinite(rr)).sum())
            predefined=np.isfinite(bb).all(-1)&(bb>1/255).all(-1);mask_disagreement+=int((e!=predefined).sum())
            relative=np.max(abs(rr.astype('f8')-bb)/np.maximum(abs(bb),1e-6),axis=-1);bad=e&((relative>1e-3)|(~np.isfinite(rr).all(-1)))
            n+=int(e.sum());f+=int(bad.sum());mr=max(mr,float(np.max(relative[e]))if e.any()else 0.)
        eligible_n+=n;failed+=f;maxrel=max(maxrel,mr);inverse_rows.append({'serial':native['serial'],'eligible_pixels':n,'failed_eligible_pixels':f,'max_relative_error_in_old_mask':mr,'original_solver_record':native['inverse'],'original_input_domain_held_aside':native['held_aside_original_input_domain']})
        del b,rt,mask
    assert mask_disagreement==0,'Legacy RGB eligible mask must not change'
    qualified=cm<=1e-5 and cnf==bnf==0 and cnonzero>0 and(csse==0 or -10*np.log10(csse/(total*3))>=60)
    save(out/'native-CI-fullframe.json',{'max_abs':cm,'nonfinite_CI_RGB':cnf,'nonfinite_reference_RGB':bnf,'nonzero_CI_RGB':cnonzero,'PSNR_peak1_dB':'inf'if csse==0 else float(-10*np.log10(csse/(total*3))),'pixels':total,'qualified':qualified})
    save(out/'inverse-roundtrip.json',{'pixels':total,'eligible_pixels':eligible_n,'coverage':eligible_n/total,'failed_eligible_pixels':failed,'max_relative_error_in_old_mask':maxrel,'nonfinite_roundtrip_RGB':rt_nf,'mask_disagreement_pixels':mask_disagreement,'old_1e3_gate_pass':qualified and failed==0 and rt_nf==0,'owner_records':inverse_rows,'no_unique_inverse_or_camera_truth_claim':True})
    assert qualified,'Captured native outputs must match the full CI rendering before effect assessment'
    del ci
    cfg=ocio.Config.CreateFromBuiltinConfig('cg-config-v2.2.0_aces-v1.3_ocio-v2.4');cfgsha=hashlib.sha256(cfg.serialize().encode()).hexdigest();assert cfgsha=='5aefc668796eabb1902b9593340496231758eceaec18ce290e12901042bd4440'
    cpu=cfg.getProcessor('Linear P3-D65','sRGB - Display','ACES 1.0 - SDR Video',ocio.TRANSFORM_DIR_FORWARD).getDefaultCPUProcessor();preview_checks=[]
    def display(a):
        before=hashlib.sha256(a.tobytes()).hexdigest();v=np.array(a,'f4',order='C',copy=True);cpu.apply(ocio.PackedImageDesc(v,v.shape[1],v.shape[0],3));after=hashlib.sha256(a.tobytes()).hexdigest();assert before==after;preview_checks.append({'before':before,'after':after});return np.rint(np.clip(v,0,1)*255).astype('u1')
    rows=[];pictures=[];output_records=[];smallshape=((shape[0]+9)//10,(shape[1]+9)//10,3)
    for operator in['skin-color','skin-brightness','skin-both']:
        for strength in plan['practical_strengths']:
            hist=np.zeros(256,'u8');active_hist=np.zeros(256,'u8');qh=np.zeros(256,'u8');ev=[];active_ev=[];chroma=[];active_chroma=[];excluded=0;chroma_excluded=0;nf=0;zero=0.;outside_n=0;outside_max=0.;valid=0;oracle_valid=0;qgain=0.;qabs=0.;sse=0.;edge_path=scratch/(operator+'-'+str(strength)+'-luma-error.f32');err=np.memmap(edge_path,mode='w+',dtype='<f4',shape=shape)
            small=np.empty(smallshape,'f4')if strength==.5 else None;small_oracle=np.empty(smallshape,'f4')if strength==.5 else None
            for native,x,top,w,h,p in owners:
                b=image(p/'native.f16',(h,w));rt=image(p/'native-inverse-roundtrip.f16',(h,w));estimate=image(p/(operator+'-estimate.f16'),(h,w));oracle=image(p/(operator+'.f16'),(h,w));stored=None
                if strength==.5:
                    gainpath=p/(operator+'-strength0.5-loggain.f16');stored=np.memmap(gainpath,mode='w+',dtype='<f2',shape=(h,w,3));validpath=p/(operator+'-strength0.5-ratio-valid.u8');stored_valid=np.memmap(validpath,mode='w+',dtype='u1',shape=(h,w))
                step=min(64,max(1,262144//w))
                for y in range(0,h,step):
                    stop=min(y+step,h);bb=np.array(b[y:stop,:,:3],'f4',copy=True);rr=np.array(rt[y:stop,:,:3],'f4',copy=True);ee=np.array(estimate[y:stop,:,:3],'f4',copy=True);oo=np.array(oracle[y:stop,:,:3],'f4',copy=True)
                    result=apply(bb,rr,ee,strength);expected=apply(bb,bb,oo,strength);ideal=result['rgb'];target=expected['rgb'];actual=ideal
                    valid+=int(result['ratio_valid'].sum());oracle_valid+=int(expected['ratio_valid'].sum())
                    if strength==.5:
                        packed=result['log2_gain'].astype('<f2');stored[y:stop]=packed;stored_valid[y:stop]=result['ratio_valid'];actual=(bb.astype('f8')*np.exp2(packed.astype('f8'))).astype('f4');qgain=max(qgain,float(np.max(abs(packed.astype('f8')-result['log2_gain']))));qabs=max(qabs,float(np.max(abs(actual.astype('f8')-ideal))))
                        qcodes=np.max(abs(display(actual).astype('i2')-display(ideal).astype('i2')),axis=-1);qh+=np.bincount(qcodes.ravel(),minlength=256).astype('u8')
                    if strength==0:zero=max(zero,float(np.max(abs(actual-bb))))
                    finite=np.isfinite(actual).all(-1)&np.isfinite(target).all(-1);nf+=int((~np.isfinite(actual)).sum());difference=actual.astype('f8')-target;sse+=float(np.sum(difference*difference))
                    codes=np.max(abs(display(actual).astype('i2')-display(target).astype('i2')),axis=-1);hist+=np.bincount(codes.ravel(),minlength=256).astype('u8');active=(oo!=bb).any(-1);active_hist+=np.bincount(codes[active].ravel(),minlength=256).astype('u8')
                    ya=actual@Y;yo=target@Y;good=finite&(ya>0)&(yo>1/255);excluded+=int((~good).sum());ev.append(abs(np.log2(ya[good]/yo[good])).astype('f4'));ag=good&active;active_ev.append(abs(np.log2(ya[ag]/yo[ag])).astype('f4'))
                    sa=actual.sum(-1,dtype='f8');so=target.sum(-1,dtype='f8');cg=finite&(actual.min(-1)>=0)&(target.min(-1)>=0)&(sa>3/255)&(so>3/255);chroma_excluded+=int((~cg).sum());chroma.append(np.max(abs(actual[cg]/sa[cg,None]-target[cg]/so[cg,None]),axis=-1).astype('f4'));acg=cg&active;active_chroma.append(np.max(abs(actual[acg]/sa[acg,None]-target[acg]/so[acg,None]),axis=-1).astype('f4'))
                    outside=(oo==bb).all(-1);outside_n+=int(outside.sum())
                    if outside.any():outside_max=max(outside_max,float(np.max(abs(actual[outside]-bb[outside]))))
                    err[top+y:top+stop,x:x+w]=ya-yo
                    if strength==.5:
                        gy=np.arange(top+y,top+stop);gx=np.arange(x,x+w);my=gy%10==0;mx=gx%10==0
                        if my.any()and mx.any():small[(gy[my]//10)[:,None],gx[mx]//10]=actual[my][:,mx];small_oracle[(gy[my]//10)[:,None],gx[mx]//10]=target[my][:,mx]
                if strength==.5:
                    stored.flush();stored_valid.flush();del stored,stored_valid
                    metadata={'shape':[h,w,3],'dtype':'<f2','space':'RGB log2 correction in native/CI-verified linear P3','baseline':'native.f16','strength':strength,'operator':operator,'CI_owner':native['CI_owner']['output_region'],'sha256':sha(gainpath),'ratio_mask_sha256':sha(validpath),'ratio_mask_shape':[h,w],'ratio_mask_dtype':'u1','reconstruction':'RGB = baseline_RGB * exp2(loggain); mask false has loggain zero; preserve signed baseline','not_final_HDR_container':True};save(Path(str(gainpath)+'.json'),metadata);output_records.append(metadata)
                del b,rt,estimate,oracle
            err.flush();del err;grad=gradient_metrics(edge_path,shape,lines);edge_path.unlink()
            cum=np.cumsum(hist);count=int(cum[-1]);assert count==total;p99=int(np.searchsorted(cum,np.ceil(count*.99)));maxcode=int(np.flatnonzero(hist)[-1]);estat=stats(ev);cstat=stats(chroma);gate=plan['practical_inverse_gate']
            active_estat=stats(active_ev);active_cstat=stats(active_chroma);active_count=int(active_hist.sum());active_p99=int(np.searchsorted(np.cumsum(active_hist),np.ceil(active_count*.99)))if active_count else None
            active_pass=(active_p99<=gate['ACES_p99_pixel_Linf_codes_max']and active_estat['p99']is not None and active_estat['p99']<=gate['EV_luma_p99_max'])if active_count else outside_max==0
            passed=estat['p99']is not None and estat['p99']<=gate['EV_luma_p99_max']and p99<=gate['ACES_p99_pixel_Linf_codes_max']and maxcode<=gate['ACES_max_codes_max']and nf==0 and grad['nonfinite_gradients']==0 and(strength!=0 or zero==0)and active_pass
            row={'operator':operator,'strength':strength,'pixels':count,'practical_gate':passed,'selected_delivery':strength==.5,'delivery':'Actual stored-half loggain reconstruction'if strength==.5 else'Unquantized sensitivity/identity only','EV':estat,'EV_excluded_pixels':excluded,'ACES_p99_pixel_Linf_codes':p99,'ACES_max_codes':maxcode,'ACES_pixels_gt1':int(hist[2:].sum()),'ACES_pixels_gt4':int(hist[5:].sum()),'PSNR_peak1_dB':'inf'if sse==0 else float(-10*np.log10(sse/(total*3))),'normalized_RGB_ratio_error':cstat,'normalized_RGB_excluded_pixels':chroma_excluded,'nonfinite_RGB':nf,'ratio_valid_pixels':valid,'oracle_ratio_valid_pixels':oracle_valid,'zero_strength_RGB_max':zero if strength==0 else None,'oracle_zero_effect_pixels':outside_n,'oracle_zero_effect_region_max_actual_change':outside_max,'zero_effect_region_is_not_a_matte_or_new_mask':True,'half_loggain_transport':{'loggain_max_abs_EV_error':qgain,'RGB_max_abs_error':qabs,'ACES_max_codes':int(np.flatnonzero(qh)[-1])if qh.any()else None},'gradient':grad,'old_1e3_gate_unchanged':True,'camera_baked_parameter_or_scene_truth_identified':False}
            row['native_effect_active_region']={'pixels':active_count,'EV':active_estat,'EV_excluded_pixels':active_count-active_estat['n'],'ACES_p99_pixel_Linf_codes':active_p99,'normalized_RGB_ratio_error':active_cstat,'practical_gate':active_pass,'selection':'Native neutral_RGB != native original_RGB before strength; diagnostic and acceptance region, not a new legacy mask or output gate'}
            rows.append(row);save(out/'analysis-checkpoint.json',{'rows':rows,'inverse_roundtrip_failures_retained':failed,'engineering_accepted':False})
            if strength==.5:
                for label,array in[(operator+' estimate50%',small),(operator+' native50%',small_oracle)]:
                    im=Image.fromarray(np.rot90(display(array),3));im.thumbnail((450,600));pictures.append((label,im))
    primary=image(folder/'primary_input.f32',shape,'<f4');im=Image.fromarray(np.rot90(display(np.array(primary[::10,::10,:3],'f4',copy=True)),3));im.thumbnail((450,600));pictures.insert(0,('Original SDR (fixedACES preview)',im));del primary
    sheet=Image.new('RGB',(1800,1260),'white');draw=ImageDraw.Draw(sheet)
    for i,(label,im)in enumerate(pictures):
        x=(i%4)*450;y=(i//4)*630;sheet.paste(im,(x,y));draw.text((x+5,y+603),label,fill='black')
    sheet.save(private/'semantic-inverse-fullframe-ACES.png')
    assert all(c['before']==c['after']for c in preview_checks)
    checks_path=private/'preview-input-SHA-checks.json';save(checks_path,{'checks':preview_checks,'all_unchanged':True})
    summary={'os_build':'26A434','canvas':list(shape),'photo_count':1,'full_original_frame_pixels':total,'complete_native_reference':qualified,'complete_owner_inverse_executed':True,'roundtrip':{'old_mask_coverage':eligible_n/total,'failed_eligible_pixels':failed,'max_relative_error_in_old_mask':maxrel,'old_1e3_gate_pass':failed==0 and rt_nf==0},'rows':rows,'selected_strength':.5,'all_selected_practical_gates_pass':all(r['practical_gate']for r in rows if r['strength']==.5),'zero_strength_identity_all':all(r['zero_strength_RGB_max']==0 for r in rows if r['strength']==0),'preview_input_SHA_check_count':len(preview_checks),'preview_input_SHA_all_unchanged':True,'private_preview_SHA_checks_file_SHA256':sha(checks_path),'display':{'view':'ACES 1.0 - SDR Video','source':'Linear P3-D65','display':'sRGB - Display','exposure_EV':0,'config_SHA256':cfgsha},'output_corrections':output_records,'old_masks_or_thresholds_changed':False,'original_SDR_modified':False,'no_new_ImageIO_container_test':True,'face_body_actual_EV_identified':False,'physical_scene_accuracy_unverified':True,'camera_baked_semantics_restored':False,'engineering_accepted':False,'A_phase_complete':False,'acceptance_complete':False}
    save(out/'analysis.json',summary)
    return summary
