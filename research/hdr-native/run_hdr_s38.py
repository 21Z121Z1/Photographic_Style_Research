"""Runner-only full-size Apple RGB-map candidates, with independent HDR intent.

These are conditional thumbnail projections, not a certified capture ISP inverse.
Global-only inversion is a declared supplied-GTC hypothesis. Existing semantic
inverses stay separate. All pixel outputs/previews are encrypted before upload.
"""
from pathlib import Path
import os,sys,json,hashlib,subprocess,math,struct,shutil,zlib,tarfile,platform
import numpy as np
from PIL import Image,ImageDraw
import PyOpenColorIO as ocio
import OpenEXR,Imath
REPO=Path.cwd();D=REPO/'research/hdr-native';W=Path(os.environ['W']);O=W/'out';PRIVATE=W/'private';ENC=W/'encrypted'
for p in [O,PRIVATE,ENC]:p.mkdir(exist_ok=True)
sys.path.insert(0,str(REPO));sys.path.insert(0,str(REPO/'research/vm-native'));sys.path.insert(0,str(D))
from extract_inputs import extract
import guided_reference_v3 as guided
from render_contract import gain_from_pair
Y=np.array([.2289745641,.6917385218,.0792869141]);ROWS=32
PHOTOS=[('IMG_2600','development',REPO/'research/vm-native/samples/IMG_2600.HEIC'),('IMG_2604','development',REPO/'research/vm-native/samples/IMG_2604.HEIC'),('IMG_2608','development',REPO/'research/vm-native/samples/IMG_2608.HEIC'),('IMG_0032','new-recipe-holdout',REPO/'Apple_Native_Samples/IMG_0032.HEIC'),('IMG_0033','new-recipe-holdout',REPO/'Apple_Native_Samples/IMG_0033.HEIC')]
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,v):p.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def run(args,log,timeout=900):
 with Path(log).open('w') as f:r=subprocess.run(list(map(str,args)),stdout=f,stderr=subprocess.STDOUT,timeout=timeout)
 if r.returncode:raise RuntimeError(f'{Path(str(args[0])).name} exited{r.returncode}; inspect {Path(log).name}')
def room(extra):
 if shutil.disk_usage(W).free<4_000_000_000+extra:raise RuntimeError('Runner free-space guard: keep4GB plus declared working allowance')
assert subprocess.check_output(['sw_vers','-buildVersion'],text=True).strip()=='26A434'
cfg=ocio.Config.CreateFromBuiltinConfig('cg-config-v2.2.0_aces-v1.3_ocio-v2.4');cpu=cfg.getProcessor('Linear P3-D65','sRGB - Display','ACES 1.0 - SDR Video',ocio.TRANSFORM_DIR_FORWARD).getDefaultCPUProcessor()
display={'config':'cg-config-v2.2.0_aces-v1.3_ocio-v2.4','config_sha256':hashlib.sha256(cfg.serialize().encode()).hexdigest(),'source':'Linear P3-D65','display':'sRGB - Display','view':'ACES 1.0 - SDR Video','exposure_ev':0,'orientation':'Original stored canvas, transform from native metadata for previews only'}
sources=[D/x for x in ['source_s37.m','ltm_materialize_s38.m','unencoded_s37.m','run_hdr_s38.py','guided_reference_v3.py','render_contract.py']]+[REPO/'research/vm-native/runner'/x for x in ['Styles_full_v3.m','encoder_capture_v2.inc','guided_oracle_v3.m']]
freeze={'os_build':'26A434','source_sha256':{str(p.relative_to(REPO)):sha(p) for p in sources},'photos':[{'id':n,'role':role,'source_sha256':sha(p)} for n,role,p in PHOTOS],'holdout_scope':'These two photos were used in older scalar-guide studies; withheld from this new RGB-map recipe until this immutable source was frozen. No photograph tunes this recipe.','native_rgb_map':{'host':'original prepareToProcess:2 + _processLTMGainMap','radius':1,'epsilon':float(np.float32(.001)),'guide':'full-resolution native inverse-key1 source in linearP3, four half lanes','SRL_before_stats':False,'transfer':0,'CCM':'identity as in previous controlled captured input space','inputImageThumbnailTexture':'nil: original host samples full inputImageTexture at linear-grid centers'},'exposure_policy':'E=2^-max(0,ceil(log2(max positive native thumbnail RGB))); power of two, shared both branches; prevent create-kernel upperclip then undo E for relative master','local_only_candidate':'A * nativeGF(GTC(min(E*X,1))/sample(A)); retains supplied curve, unknown equivalence to baked producer','global_only_candidate':'supplied GTC^-1(A)/E on strict finite interior only; hypothetical producer order/domain, never certified full global inverse','both_candidate':'half(A * nativeGF(min(E*X,1)/sample(A))/E), RGB guide epsilon .001; no area renormalization, no log-gain filtering','HDR_render':'Separate intent: H=scene_candidate * 8/(8+P3_Y(scene_candidate)); relative units, no nit calibration','transport':'Actual saved/reopened float32 log2 RGB EXR sidecar, offset0, positive-component mask separately reported; native unencoded headrooms1,1.25,2,4,8; no HEIF encoding pass inferred','precision_gates_unchanged':{'half':'bit-exact when declared','float_max_abs':1e-5,'PSNR_peak1_db_min':60,'relative_max':1e-3},'display':display,'scope':'Full-size conditional master/render candidates; physical scene/semantic/33point gates unchanged','acceptance_complete':False}
save(O/'formula-freeze.json',freeze);frozen_sha=sha(O/'formula-freeze.json')
native_library=Path('/System/Library/PrivateFrameworks/CMImaging.framework/Versions/A/Resources/default.metallib')
assert sha(native_library)=='16a8a119e3e0ae1649d32b2bbc8ea9136cb757a8d1f3eb451025821901edff11'
save(O/'native-library.json',{'path':str(native_library),'sha256':sha(native_library),'source_binary_UUID':'3CCD434E-B1E0-3F14-8EF6-E29D58379BE8','source_binary_sha256':'40868a2bc375526c2de6f378c2012420e91830bdb9e16e4cbb20662822b11c3e','source_binary_provenance':'Existing26A434 extraction run39051942415, no new Apple binary upload'})
save(O/'versions.json',{'python':platform.python_version(),'numpy':np.__version__,'OpenEXR':getattr(OpenEXR,'__version__','unknown'),'OpenColorIO':ocio.__version__,'image_version':os.environ.get('ImageVersion'),'initial_free_bytes':shutil.disk_usage(W).free})
flags=['clang','-O2','-g','-fobjc-arc','-framework','Foundation','-framework','CoreImage','-framework','CoreMedia','-framework','ImageIO','-framework','Metal','-framework','CoreGraphics','-lz']
for name,src in [('source','source_s37.m'),('map','ltm_materialize_s38.m'),('headroom','unencoded_s37.m')]:run(flags+[D/src,'-o',W/name],O/(name+'-build.log'))
def load_render(root,spec,name):
 shape=tuple(spec['shape']);path=root/spec['file']
 if spec.get('compression')=='zlib':
  dest=root/(name+'.f16');dec=zlib.decompressobj()
  with path.open('rb') as f,dest.open('xb') as out:
   while b:=f.read(1<<20):out.write(dec.decompress(b))
   out.write(dec.flush())
  assert dec.eof and dest.stat().st_size==np.prod(shape)*2;return np.memmap(dest,dtype='<f2',mode='r',shape=shape),dest
 return np.memmap(path,dtype=spec['dtype'],mode='r',shape=shape),path
def tohalf(source,dest):
 shape=source.shape;out=np.memmap(dest,dtype='<f2',mode='w+',shape=shape)
 for t in range(0,shape[0],ROWS):out[t:t+ROWS]=source[t:t+ROWS]
 out.flush();del out
 return np.memmap(dest,dtype='<f2',mode='r',shape=shape)
def exact_area_accumulate(out,tile,top,fullshape):
 h,w=fullshape;th,tw=out.shape[:2];sx=w/tw;sy=h/th;edges=np.linspace(0,w,tw+1);ix=np.floor(edges).astype(int);fx=edges-ix;v=np.asarray(tile,'f8');prefix=np.concatenate([np.zeros((len(v),1,3)),np.cumsum(v,axis=1)],axis=1);integral=prefix[:,ix]+v[:,np.minimum(ix,w-1)]*fx[None,:,None];horizontal=np.diff(integral,axis=1)/sx;ys=np.arange(top,top+len(v));t0=np.minimum((ys/sy).astype(int),th-1);t1=np.minimum(((ys+1)/sy).astype(int),th-1);w0=np.minimum(ys+1,(t0+1)*sy)-ys;w1=1-w0;np.add.at(out,t0,horizontal*w0[:,None,None]/sy);np.add.at(out,t1,horizontal*w1[:,None,None]/sy)
def anchor_metrics(actual,target):
 a=actual@Y;b=np.asarray(target,'f8')@Y;mask=np.isfinite(a)&np.isfinite(b)&(a>0)&(b>0);ev=np.log2(a[mask]/b[mask]);return {'positive_anchor_pixels':int(mask.sum()),'all_anchor_pixels':int(mask.size),'mean_abs_EV':float(abs(ev).mean()) if ev.size else None,'p99_abs_EV':float(np.quantile(abs(ev),.99)) if ev.size else None,'max_abs_EV':float(abs(ev).max()) if ev.size else None,'scope':'Area diagnostic, not an enforced constraint and not RAW truth'}
def global_inverse_hypothesis(a,table,E):
 q=np.asarray(a,dtype='f2');v=q.astype('f8');previous=np.nextafter(q,np.float16(-np.inf)).astype('f8');following=np.nextafter(q,np.float16(np.inf)).astype('f8');cell_lo=(previous+v)*.5;cell_hi=(following+v)*.5;grid=np.linspace(0,1,len(table));answer=np.interp(v,table,grid)/E;low=cell_lo<=table[0];high=cell_hi>=table[-1];nonfinite=~np.isfinite(v);flat=np.zeros(v.shape,bool)
 for z in np.unique(table[:-1][np.diff(table)==0]):flat|=(cell_lo<=z)&(cell_hi>=z)
 invalid=low|high|nonfinite|flat;answer[invalid]=np.nan
 return answer,{'curve_low_clamp_components':int(low.sum()),'curve_high_clamp_components':int(high.sum()),'curve_plateau_components':int(flat.sum()),'nonfinite_components':int(nonfinite.sum()),'valid_components':int((~invalid).sum())}
def exr_write(path,array,metadata,*,unitless=False):
 h,w=array.shape[:2];dtype='<f4' if unitless else '<f2';pixeltype=Imath.PixelType(Imath.PixelType.FLOAT if unitless else Imath.PixelType.HALF);header=OpenEXR.Header(w,h);header['channels']={c:Imath.Channel(pixeltype) for c in 'RGB'};header['comments']=json.dumps(metadata,sort_keys=True).encode()
 if not unitless:header['chromaticities']=Imath.Chromaticities(Imath.V2f(.68,.32),Imath.V2f(.265,.69),Imath.V2f(.15,.06),Imath.V2f(.3127,.3290))
 f=OpenEXR.OutputFile(str(path),header)
 for t in range(0,h,ROWS):
  b=array[t:t+ROWS];f.writePixels({c:np.ascontiguousarray(b[...,i],dtype=dtype).tobytes() for i,c in enumerate('RGB')},len(b))
 f.close();r=OpenEXR.InputFile(str(path));bad=0
 for i,c in enumerate('RGB'):
  for t in range(0,h,ROWS):
   v=np.frombuffer(r.channel(c,pixeltype,t,min(t+ROWS,h)-1),dtype=dtype).reshape(-1,w);bad+=int(np.count_nonzero(v.view('u4' if unitless else 'u2')!=np.asarray(array[t:t+len(v),:,i],dtype=dtype).view('u4' if unitless else 'u2')))
 r.close();assert bad==0
 return {'path':path.name,'size':path.stat().st_size,'sha256':sha(path),'readback_different_storage_components':bad,'dtype':dtype,'unit':'log2 RGB ratio (EV), no color-space tag' if unitless else 'relative linearP3; scene candidate only'}
def preview(v,path,orientation):
 before=hashlib.sha256(np.ascontiguousarray(v).tobytes()).hexdigest();x=np.array(v[...,:3],dtype='f4',order='C',copy=True);x[~np.isfinite(x)]=0;cpu.apply(ocio.PackedImageDesc(x,x.shape[1],x.shape[0],3));im=Image.fromarray(np.rint(np.clip(x,0,1)*255).astype('u1'));op={2:Image.Transpose.FLIP_LEFT_RIGHT,3:Image.Transpose.ROTATE_180,4:Image.Transpose.FLIP_TOP_BOTTOM,5:Image.Transpose.TRANSPOSE,6:Image.Transpose.ROTATE_270,7:Image.Transpose.TRANSVERSE,8:Image.Transpose.ROTATE_90}.get(orientation)
 if op is not None:im=im.transpose(op)
 im.save(path);after=hashlib.sha256(np.ascontiguousarray(v).tobytes()).hexdigest();assert before==after
 return {'file':path.name,'input_before_sha256':before,'input_after_sha256':after,'source_unchanged':True,'nonfinite_preview_replacement':'black for display only; masks retained separately'},im
def metadata(lo,hi):
 ch=''.join('<rdf:li rdf:parseType="Resource">'+''.join(f'<h:{k}>{v:.9f}</h:{k}>' for k,v in [('GainMapMin',lo),('GainMapMax',hi),('Gamma',1),('BaseOffset',0),('AlternateOffset',0)])+'</rdf:li>' for _ in range(3))
 return f'<x:xmpmeta xmlns:x="adobe:ns:meta/"><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"><rdf:Description xmlns:HDRToneMap="http://ns.apple.com/HDRToneMap/1.0/"><HDRToneMap:Version>1</HDRToneMap:Version><HDRToneMap:BaseHeadroom>0</HDRToneMap:BaseHeadroom><HDRToneMap:AlternateHeadroom>3</HDRToneMap:AlternateHeadroom><HDRToneMap:ChannelMetadata><rdf:Seq>{ch.replace("h:","HDRToneMap:")}</rdf:Seq></HDRToneMap:ChannelMetadata><HDRToneMap:BaseColorIsWorkingColor>True</HDRToneMap:BaseColorIsWorkingColor></rdf:Description></rdf:RDF></x:xmpmeta>'
results=[]
for photo,role,source in PHOTOS:
 case=W/photo;case.mkdir();private=PRIVATE/photo;private.mkdir();full=case/'publish';full.mkdir();row={'photo':photo,'role':role,'scope':'New full-size conditional RGB-map recipe, not a verified camera global/local/semantic inverse','completed':False};results.append(row)
 try:
  room(2_000_000_000);assert sha(O/'formula-freeze.json')==frozen_sha
  extract(source,case);run([W/'source',source,case],O/(photo+'-source.log'),1200);facts=json.loads((case/'source-facts.json').read_text());row['source_facts']={k:v for k,v in facts.items() if k not in ['frozen_decode','Apple_Log_parameters']};row['orientation']=facts['frozen_decode']['orientation']
  a,apath=load_render(case,facts['frozen_decode']['unstyled'],'unstyled_raw');linear,lp=load_render(case,facts['linear_native'],'linear_raw');h,w=a.shape[:2];assert (h,w)==tuple(facts['original_sdr_float32']['shape'][:2]);row['shape']=[h,w,3]
  if a.dtype!=np.dtype('<f2'):a=tohalf(a,case/'main.f16');apath=case/'main.f16'
  else:shutil.copyfile(apath,case/'main.f16');a=np.memmap(case/'main.f16',dtype='<f2',mode='r',shape=a.shape)
  linear_reference=linear;linear=tohalf(linear,case/'linear.f16');assert np.isfinite(linear[...,:3]).all();row['thumbnail_float32_to_native_half_max_abs']=float(abs(linear[...,:3].astype('f4')-linear_reference[...,:3].astype('f4')).max());peak=float(linear[...,:3].max());E=2.**(-max(0,math.ceil(math.log2(max(peak,1.)))));row['relative_exposure_E']=E;row['native_linear_thumbnail_peak']=peak
  curve,cp=load_render(case,facts['gtc_native'],'gtc_raw');table=np.array(curve[...,:1],dtype='<f2',copy=True);assert table.shape[0]==1 and table.shape[1]==256 and np.isfinite(table).all() and np.all(np.diff(table.reshape(-1).astype('f4'))>=0);table.tofile(case/'gtc.f16')
  fixture={k:{'file':k+'.f16','dtype':'<f2','shape':list(v.shape)} for k,v in [('main',a),('linear',linear),('gtc',table)]};save(case/'fixture.json',fixture);color=bytearray(320)
  for start in range(0,320,80):
   for c in range(3):struct.pack_into('<f',color,start+16+16*c+4*c,1.)
  (case/'color.bin').write_bytes(color);scene=np.memmap(case/'scene_candidate.f16',dtype='<f2',mode='w+',shape=(h,w,3));sdr=np.memmap(case/facts['original_sdr_float32']['file'],dtype='<f4',mode='r',shape=(h,w,4));baseline_hashes={'main':sha(case/'main.f16'),'SDR_float32':sha(case/facts['original_sdr_float32']['file']),'thumbnail':sha(case/'linear.f16')}
  step=max(1,math.ceil(max(h,w)/640));ys=np.arange(0,h,step);xs=np.arange(0,w,step);previews={'SDR':np.array(sdr[ys[:,None],xs[None,:],:3],copy=True),'inverse-key1':np.array(a[ys[:,None],xs[None,:],:3],copy=True)};gprev,gmask=global_inverse_hypothesis(a[ys[:,None],xs[None,:],:3],table.reshape(-1),E);previews['global-only-hypothesis']=gprev
  row['map_variants']=[];area_scene=np.zeros(linear.shape[:2]+(3,),'f8');area_bilinear=np.zeros_like(area_scene)
  for tag,weight in [('both-candidate',0.),('local-only-GTC-retained-candidate',1.)]:
   params=bytearray(672)
   for off,val in [(24,1.),(28,1.),(628,E),(632,E),(636,weight)]:struct.pack_into('<f',params,off,val)
   (case/'params.bin').write_bytes(params);dest=case/('native-'+tag);dest.mkdir();run([W/'map',case,dest,'host'],O/(photo+'-'+tag+'.log'),900);native=json.loads((dest/'native.json').read_text());assert native['host_preconditions_verified'] and native['dispatch_count']==7 and len(native['guided_calls'])==2;assert all(c['radius']==1 and c['epsilon']==float(np.float32(.001)) and c['guide_size']==[h,w] for c in native['guided_calls']);spec=native['textures']['bg-full'];q=np.memmap(dest/spec['file'],dtype=spec['dtype'],mode='r',shape=tuple(spec['shape']));ss=native['textures']['bg-small'];small=np.memmap(dest/ss['file'],dtype=ss['dtype'],mode='r',shape=tuple(ss['shape']));qfg=native['textures']['fg-full'];assert qfg['sha256']==spec['sha256'];assert native['params_SHA_before']==native['params_SHA_after'];assert native['textures']['main']['sha256']==baseline_hashes['main']
   localprev=a[ys[:,None],xs[None,:],:3].astype('f4')*q[ys[:,None],xs[None,:],:3].astype('f4')/(E if weight==0 else 1);previews[tag]=localprev
   m={'tag':tag,'radius':1,'epsilon':float(np.float32(.001)),'guided_calls':native['guided_calls'],'dispatches':native['dispatch_count'],'source_texture_unchanged':True,'params_unchanged':True,'full_bg_fg_SHA_equal':True,'full_bg_sha256':spec['sha256'],'small_bg_sha256':ss['sha256'],'coefficient_materialization':'Original host GPU; coefficient textures traced but not duplicated to disk','candidate_negative_components':0,'candidate_nonfinite_components':0,'gain_gradient_max_EV':0.,'gain_laplacian_max_EV':0.}
   for top in range(0,h,ROWS):
    stop=min(h,top+ROWS);at=a[top:stop,:,:3].astype('f4');qt=q[top:stop,:,:3].astype('f4');v=at*qt/(E if weight==0 else 1);m['candidate_negative_components']+=int((v<0).sum());m['candidate_nonfinite_components']+=int((~np.isfinite(v)).sum());halo_lo=max(top-1,0);halo_hi=min(stop+1,h);qh=q[halo_lo:halo_hi,:,:3].astype('f4');valid=(qh>0)&np.isfinite(qh);ev=np.where(valid,np.log2(np.where(valid,qh,1)),np.nan);dx=abs(np.diff(ev[top-halo_lo:stop-halo_lo],axis=1));dy=abs(np.diff(ev,axis=0)[top-halo_lo:min(stop,h-1)-halo_lo]);finite=np.concatenate([dx[np.isfinite(dx)],dy[np.isfinite(dy)]]);m['gain_gradient_max_EV']=max(m['gain_gradient_max_EV'],float(finite.max()) if finite.size else 0.)
    lap=ev[1:-1,:-2]+ev[1:-1,2:]+ev[:-2,1:-1]+ev[2:,1:-1]-4*ev[1:-1,1:-1];lap=lap[max(top,1)-halo_lo-1:min(stop,h-1)-halo_lo-1];finite=abs(lap[np.isfinite(lap)]);m['gain_laplacian_max_EV']=max(m['gain_laplacian_max_EV'],float(finite.max()) if finite.size else 0.)
    if weight==0:
     scene[top:stop]=v.astype('f2');exact_area_accumulate(area_scene,scene[top:stop].astype('f4'),top,(h,w));ux=(np.arange(w,dtype='f4')[None,:]+np.float32(.5))/np.float32(w);uy=(np.arange(top,stop,dtype='f4')[:,None]+np.float32(.5))/np.float32(h);bilinear=guided.normalized_sample(small,ux,uy)[...,:3];exact_area_accumulate(area_bilinear,at*bilinear/E,top,(h,w))
   row['map_variants'].append(m);del q,small;shutil.rmtree(dest)
  scene.flush();row['native_RGB_anchor']=anchor_metrics(area_scene,linear_reference[...,:3]);row['same_Apple_small_q_bilinear_anchor']=anchor_metrics(area_bilinear,linear_reference[...,:3]);row['anchor_reference']='Native Apple Log float32 output before GPU half storage cast';row['old_2048_bilinear_area_comparison_complete']=False
  lg=np.memmap(case/'log2_rgb_gain.f32',dtype='<f4',mode='w+',shape=(h,w,3));mask=np.memmap(case/'positive_pair_mask.u8',dtype='u1',mode='w+',shape=(h,w));target=np.memmap(case/'HDR_target.f32',dtype='<f4',mode='w+',shape=(h,w,3));counts={'near_black_source_pixels':0,'nonfinite_master_pixels':0,'negative_master_components':0,'positive_ratio_pixels':0,'all_pixels':h*w};gmin=0.;gmax=0.;savedmaxrel=0.;savedmaxabs=0.;storagerel=0.;global_masks={}
  for top in range(0,h,ROWS):
   stop=min(h,top+ROWS);v=scene[top:stop].astype('f8');luma=v@Y;den=8+luma;H=v*np.divide(8,den,out=np.full_like(den,np.nan),where=den>0)[...,None];target[top:stop]=H.astype('f4');H=target[top:stop].astype('f8');pair=gain_from_pair(sdr[top:stop,:,:3],H,offset_sdr=0,offset_hdr=0);good=pair['positive_ratio_mask'];values=np.where(good[...,None],pair['log2_gain'],0).astype('f4');lg[top:stop]=values;mask[top:stop]=good;counts['positive_ratio_pixels']+=int(good.sum());counts['near_black_source_pixels']+=int(np.any(a[top:stop,:,:3]<=np.float16(1/255),-1).sum());counts['nonfinite_master_pixels']+=int((~np.isfinite(v).all(-1)).sum());counts['negative_master_components']+=int((v<0).sum());gmin=min(gmin,float(values.min()));gmax=max(gmax,float(values.max()));_,gm=global_inverse_hypothesis(a[top:stop,:,:3],table.reshape(-1),E)
   for k,val in gm.items():global_masks[k]=global_masks.get(k,0)+val
  lg.flush();mask.flush();target.flush();del lg;lg=np.memmap(case/'log2_rgb_gain.f32',dtype='<f4',mode='r',shape=(h,w,3))
  for top in range(0,h,ROWS):
   stop=min(h,top+ROWS);good=mask[top:stop].astype(bool);recon=sdr[top:stop,:,:3].astype('f8')*np.exp2(lg[top:stop].astype('f8'));H=target[top:stop].astype('f8');e=abs(recon-H)[good]
   if e.size:savedmaxabs=max(savedmaxabs,float(e.max()));savedmaxrel=max(savedmaxrel,float((e/np.maximum(abs(H[good]),1e-12)).max()))
  row['masks']=counts;row['global_only_conditional_masks']=global_masks;row['global_only_inverse_scope']='Hypothesis of supplied monotone GTC application; no native fast-math envelope or full producer domain proof; endpoint/flat outputs omitted, no camera EV confidence interval claimed';row['actual_saved_float32_log_gain_reconstruction']={'max_abs':savedmaxabs,'max_relative':savedmaxrel,'positive_pixels':counts['positive_ratio_pixels'],'scope':'Actual file reopen of a supplied pair, not an inverse metric'}
  row['EXRs']=[exr_write(full/'scene_candidate_linear_P3.exr',scene,{'photo':photo,'status':'hypothesis relative scene master','formula_freeze_sha256':frozen_sha,'Apple_Log_unchanged':True,'native_rgb_epsilon':float(np.float32(.001))}),exr_write(full/'log2_RGB_gain.exr',lg,{'photo':photo,'status':'supplied HDR target transport, not ISP inverse','formula_freeze_sha256':frozen_sha,'offset_sdr':0,'offset_hdr':0,'source_primaries':'linear Display P3','positive_pair_mask':'positive_pair_mask.npy'},unitless=True)]
  np.save(full/'positive_pair_mask.npy',np.asarray(mask,dtype=bool));save(full/'meaning.json',{'photo':photo,'scene_candidate':'Relative linearP3 hypothesis; key1 reversed, native RGB thumbnail projection, semantic/texture/production curves not certified','gain_map':'float32 log2 RGB ratio, offset0; valid only under supplied positive_pair_mask','HDR_target_definition':freeze['HDR_render'],'SDR':'Original HEIC bytes not included or changed; no encoded carrier produced','formula_freeze_sha256':frozen_sha})
  # Seal completed files before subsequent native transport diagnostics, so
  # a later failure does not destroy already produced/reopened deliverables.
  with tarfile.open(case/'full.tar.gz','w:gz') as t:t.add(full,arcname='full')
  run(['gpg','--batch','--trust-model','always','--recipient','28E62F64A29764C2F2AEBF5D5B6B1C101E5F5ABA','--encrypt','--output',ENC/(photo+'-full.tar.gz.gpg'),case/'full.tar.gz'],O/(photo+'-encrypt.log'))
  row['encrypted_full']={'file':photo+'-full.tar.gz.gpg','size':(ENC/(photo+'-full.tar.gz.gpg')).stat().st_size,'sha256':sha(ENC/(photo+'-full.tar.gz.gpg'))}
  pp=previews['both-candidate'];previews['independent-HDR-render']=pp*8/(8+pp@Y)[...,None];row['preview_checks']=[];images=[]
  for name,v in previews.items():check,im=preview(v,private/(name+'.png'),row['orientation']);row['preview_checks'].append(check);im.thumbnail((240,320));images.append((name,im))
  sheet=Image.new('RGB',(len(images)*240,352),'white');draw=ImageDraw.Draw(sheet)
  for i,(name,im) in enumerate(images):sheet.paste(im,(i*240,0));draw.text((i*240+2,324),name,fill='black')
  sheet.save(private/'contact.private.png');row['source_SHA_after_previews']={'main':sha(case/'main.f16'),'SDR_float32':sha(case/facts['original_sdr_float32']['file']),'thumbnail':sha(case/'linear.f16')};row['source_SHA_before_previews']=baseline_hashes;assert baseline_hashes==row['source_SHA_after_previews']
  lo=math.floor(gmin*16)/16;hi=max(math.ceil(gmax*16)/16,lo+1/16);save(case/'headroom.json',{'width':w,'height':h,'gain_min_EV':lo,'gain_max_EV':hi,'source_file':str(case/facts['original_sdr_float32']['file']),'gain_file':str(case/'log2_rgb_gain.f32'),'mask_file':str(case/'positive_pair_mask.u8')});(case/'headroom.xml').write_text(metadata(lo,hi));run([W/'headroom',case,O/(photo+'-headroom.json')],O/(photo+'-headroom.log'),900);row['native_headroom']=json.loads((O/(photo+'-headroom.json')).read_text());row['original_photo_sha256_after']=sha(source);assert row['original_photo_sha256_after']==next(p['source_sha256'] for p in freeze['photos'] if p['id']==photo)
  row['completed']=True;row['actual_encoded_carrier_pass']=False;row['physical_scene_inverse_verified']=False
 except Exception as error:
  row['failure']=str(error)
  for p in case.rglob('*exception*.json'):
   row.setdefault('native_exceptions',[]).append(json.loads(p.read_text()))
 finally:
  assert sha(O/'formula-freeze.json')==frozen_sha
  for p,hsh in freeze['source_sha256'].items():assert sha(REPO/p)==hsh
  save(O/'analysis-s38.json',{'os_build':'26A434','image_version':os.environ.get('ImageVersion'),'formula_freeze_sha256':frozen_sha,'rows':results,'display':display,'native_full_size_completed':sum(r['completed'] for r in results),'A_phase_complete':False,'physical_scene_recovery_complete':False,'encoded_HDR_target_accepted':False,'acceptance_complete':False})
  # Only this job's own temporary working copies; originals are repo read-only.
  for key in ['a','linear','linear_reference','curve','scene','sdr','lg','mask','target']:
   if key in globals():del globals()[key]
  shutil.rmtree(case)
# Preview manifest can be verified without keeping any full pixel arrays.
manifest={'run_id':os.environ['GITHUB_RUN_ID'],'commit':os.environ['GITHUB_SHA'],'os_build':'26A434','people_results_encrypted':True,'files':[]}
for p in sorted(PRIVATE.rglob('*')):
 if p.is_file():manifest['files'].append({'path':str(p.relative_to(PRIVATE)),'size':p.stat().st_size,'sha256':sha(p)})
save(PRIVATE/'manifest.json',manifest)
with tarfile.open(W/'previews.tar.gz','w:gz') as t:t.add(PRIVATE,arcname='out')
run(['gpg','--batch','--trust-model','always','--recipient','28E62F64A29764C2F2AEBF5D5B6B1C101E5F5ABA','--encrypt','--output',ENC/'previews.tar.gz.gpg',W/'previews.tar.gz'],O/'preview-encrypt.log')
save(O/'encrypted-inventory.json',{'files':[{'file':p.name,'size':p.stat().st_size,'sha256':sha(p)} for p in sorted(ENC.glob('*.gpg'))],'plaintext_uploaded':False,'photos_inputs':'Only existing repository samples; no new plaintext photo upload','temporary_input_secret_created':False})
print(json.dumps({'native_full_size_completed':sum(r['completed'] for r in results),'holdouts_completed':sum(r['completed'] and r['role']=='new-recipe-holdout' for r in results),'acceptance_complete':False}))
sys.exit(0 if len(results)==5 and all(r['completed'] for r in results) else 1)
