"""One full-size public-repository photograph, unchanged SDR + explicit RGB map.

Transport test only: the target is defined directly from decoded SDR, without
claiming global/local/semantic inversion or a scene reference. No S82 data used.
"""
from pathlib import Path
import os,sys,json,hashlib,subprocess,shutil,math,io,tarfile,platform
import numpy as np
import pillow_heif
import PyOpenColorIO as ocio
from PIL import Image,ImageDraw
sys.path.insert(0,str(Path.cwd()))
from tools.heif_dump import parse_heif,_payload_from_item_extents
from iso_splice import replace_map,tmap_metadata

R=Path.cwd();D=R/'research/hdr-native';W=Path(os.environ['W']);O=W/'out';PRIVATE=W/'private';ENC=W/'encrypted';CASE=W/'case';CASE.mkdir();ROWS=32
SOURCE=R/'research/vm-native/samples/IMG_2600.HEIC';SOURCE_SHA='63872222783e757a41a41337b48875e1172e68ace0f6e411db999c77b027a4d0';Y=np.array([.2289745641,.6917385218,.0792869141],'f8')
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(path,obj):
    with Path(path).open('x')as f:json.dump(obj,f,indent=2,allow_nan=False);f.write('\n')
def command(args,log,timeout=1200):
    with Path(log).open('x')as f:p=subprocess.run(list(map(str,args)),stdout=f,stderr=subprocess.STDOUT,timeout=timeout)
    if p.returncode:raise RuntimeError('Native command failed; inspect '+Path(log).name)
def ev_rows(top,stop,h,w):
    u=(np.arange(w,dtype='f8')+.5)/w;v=(np.arange(top,stop,dtype='f8')+.5)/h
    return np.stack([np.broadcast_to(3*u,(stop-top,w)),np.broadcast_to((-.5+2*v)[:,None],(stop-top,w)),np.broadcast_to(2*(1-u),(stop-top,w))],-1)
assert platform.system()=='Darwin'and subprocess.check_output(['sw_vers','-buildVersion'],text=True).strip()=='26A434'
assert sha(SOURCE)==SOURCE_SHA and shutil.disk_usage(W).free>5_000_000_000
files=[D/x for x in ['run_hdr_s86.py','carrier_readback_s85.m','read_sdr_s44.m','hdr_headroom_s29.m','iso_splice.py']]+[R/'tools/heif_dump.py']
freeze={'readback_storage_rule':'CI bounds_y=H-storage_top-block_height; S80 prior native allocation evidence; same-source full/blocked control required before target comparison','S84_erratum':'Full ImageIO integer SDR equality remains valid; mixed-layout HDR/gain/CI metrics and native preview panels are unqualified, retained and superseded by S85.','os_build':'26A434','image_version':os.environ.get('ImageVersion'),'source_sha256':{str(p.relative_to(R)):sha(p)for p in files},'photo':'IMG_2600','photo_SHA256':SOURCE_SHA,'scope':'New full-size original-photograph carrier test; no scene/global/local/semantic inverse or artistic HDR claim. No S82 inputs, release, session secret or private-key transfer.','formula':'Same pre-existing S31 RGB opposing stress target: EV=[3u,-.5+2v,2(1-u)], H=float32(S*exp2(EV)), u/v pixel centers on original stored canvas.','gain_range_EV':[-.5,3.],'bits':[10],'codec':'pillow-heif1.3.0/libheif/x265, lossless, YCbCr matrix6,4:4:4, one encoder thread','quantization':'round((EV+.5)/3.5*(2^bits-1));16-bit input high bits for10-bit encoding as in frozenS31','metadata':'Reuse existing source ISO tmap/base/gain graph; replace only gain root and tmap payload with frozenS31 serializer. Preserve all primary descendants/properties.','headrooms':[1,2,8],'ImageIO_SDR_gate':'Explicit DecodeToSDR full integer raster equality and identical format/ICC, active bytes only; maximum decoded-pixel difference0','legacy_original_thresholds_report_only':{'linear_abs':1e-5,'PSNR_peak1_db':60,'relative_max':1e-3},'EV_diagnostic_positive_luma_floor':1e-6,'EV_quantile_precision':'full-frame positive-luma EV errors stored as float32 for exact quantiles of that file; maximum computed in float64','private_preview_cipher_max_bytes':160000,'all_pixel_outputs_encrypted_if_uploaded':True,'full_carrier_archive':'Not uploaded/downloaded in this bounded prototype; only fileSHA and reproducible source. Final deliverable remains pending.','engineering_accepted':False,'A_phase_complete':False,'acceptance_complete':False}
freeze['S86_change']='Use the pre-existing S32 matrix6/10-bit codec path on one real full-size source; keep S31 target and S85 qualified reader unchanged. Smaller preview only, no tolerance change.'
freeze['baseline_matrix0_run_id']=39408560663
freeze['reader_same_source_control_evidence']='S85 run39408560663 layout.json full/blocked exact0; same reader source SHA below; fresh same-source control remains enabled.'
save(O/'freeze.json',freeze);freeze_sha=sha(O/'freeze.json')
flags=['clang','-O2','-fobjc-arc','-framework','Foundation','-framework','CoreImage','-framework','ImageIO','-framework','Metal','-framework','CoreGraphics']
for name,source in [('source','read_sdr_s44.m'),('oracle','carrier_readback_s85.m')]:command(flags+[D/source,'-o',W/name],O/(name+'-build.log'),300)
command([W/'source',SOURCE,CASE],O/'source.log');facts=json.loads((CASE/'source.json').read_text());w,h=facts['width'],facts['height'];assert(w,h)==(5712,4284)
command([W/'oracle','--layout',SOURCE,CASE,O/'layout.json'],O/'layout.log',900);layout=json.loads((O/'layout.json').read_text());assert layout['layout_qualified'],'Reader not qualified; do not interpret carrier metrics'
save(O/'source-facts.json',facts);base=np.memmap(CASE/'original-sdr.f32',mode='r',dtype='<f4',shape=(h,w,4));base_sha=sha(CASE/'original-sdr.f32')
original=SOURCE.read_bytes();parsed=parse_heif(original);tone=next(x for x in parsed['items'].values()if x['item_type']=='tmap');ref=next(x for x in parsed['references']if x['type']=='dimg'and x['from_item_id']==tone['item_id']);assert ref['to_item_ids'][0]==parsed['primary_item_id']
save(O/'source-container.json',{'primary_id':parsed['primary_item_id'],'primary_type':parsed['items'][str(parsed['primary_item_id'])]['item_type'],'dimensions':parsed['items'][str(parsed['primary_item_id'])]['dimensions'],'tmap_id':tone['item_id'],'tmap_dimensions':tone['dimensions'],'gain_id':ref['to_item_ids'][1],'gain_dimensions':parsed['items'][str(ref['to_item_ids'][1])]['dimensions'],'items':len(parsed['items']),'all_existing_payloads_unchanged_before_test':True})
pillow_heif.options.DECODE_THREADS=1;pillow_heif.options.SAVE_HDR_TO_12_BIT=False
save(O/'versions.json',{'python':platform.python_version(),'numpy':np.__version__,'pillow_heif':pillow_heif.__version__,'libheif':pillow_heif.libheif_version(),'encoder_info':pillow_heif.libheif_info(),'OpenColorIO':ocio.__version__})
cfg=ocio.Config.CreateFromBuiltinConfig('cg-config-v2.2.0_aces-v1.3_ocio-v2.4');cfg_sha=hashlib.sha256(cfg.serialize().encode()).hexdigest();assert cfg_sha=='5aefc668796eabb1902b9593340496231758eceaec18ce290e12901042bd4440'
cpu=cfg.getProcessor('Linear P3-D65','sRGB - Display','ACES 1.0 - SDR Video',ocio.TRANSFORM_DIR_FORWARD).getDefaultCPUProcessor();preview_checks=[];preview_cards=[];display={'config':'cg-config-v2.2.0_aces-v1.3_ocio-v2.4','config_sha256':cfg_sha,'source':'Linear P3-D65','display':'sRGB - Display','view':'ACES 1.0 - SDR Video','exposure_ev':0,'scope':'Transport stress only, not a proposed HDR look'}
py=np.floor((np.arange(96)+.5)*h/96).astype(int);px=np.floor((np.arange(128)+.5)*w/128).astype(int)
def preview(rgb,name):
    before=hashlib.sha256(np.ascontiguousarray(rgb).tobytes()).hexdigest();v=np.array(rgb,'f4',order='C',copy=True);assert np.isfinite(v).all();cpu.apply(ocio.PackedImageDesc(v,v.shape[1],v.shape[0],3));im=Image.fromarray(np.rint(np.clip(v,0,1)*255).astype('u1'));after=hashlib.sha256(np.ascontiguousarray(rgb).tobytes()).hexdigest();assert before==after;preview_checks.append({'name':name,'before_sha256':before,'after_sha256':after});preview_cards.append((name,im))
preview(base[py[:,None],px[None,:],:3],'original SDR')
u=(px+.5)/w;v=(py+.5)/h;sample_ev=np.stack([np.broadcast_to(3*u,(96,128)),np.broadcast_to((-.5+2*v)[:,None],(96,128)),np.broadcast_to(2*(1-u),(96,128))],-1);preview((base[py[:,None],px[None,:],:3]*np.exp2(sample_ev)).astype('f4'),'RGB stress goal')

class ErrorState:
    def __init__(self,folder,name):
        self.path=folder/(name+'-EV.f32');self.file=self.path.open('xb');self.maxabs=0.;self.maxrel=0.;self.sse=0.;self.components=0;self.evs=0;self.evmax=0.;self.nonfinite=0;self.excluded=0
    def add(self,actual,reference):
        a=np.asarray(actual,'f8');b=np.asarray(reference,'f8');finite=np.isfinite(a)&np.isfinite(b);self.nonfinite+=int((~finite).sum());d=abs(a-b);good=finite.all(-1)
        if good.any():z=d[good];self.maxabs=max(self.maxabs,float(z.max()));self.maxrel=max(self.maxrel,float((z/np.maximum(abs(b[good]),1e-6)).max()));self.sse+=float(np.square(z).sum());self.components+=z.size
        ya=a@Y;yb=b@Y;m=good&(ya>0)&(yb>1e-6);ev=abs(np.log2(ya[m]/yb[m]));self.excluded+=int((~m).sum());self.evs+=len(ev)
        if ev.size:self.evmax=max(self.evmax,float(ev.max()));self.file.write(ev.astype('<f4').tobytes())
    def finish(self):
        self.file.close();q=np.memmap(self.path,mode='r',dtype='<f4')if self.evs else np.empty(0,'f4');quant=np.quantile(q,[.5,.95,.99])if self.evs else[None]*3
        r={'max_abs':self.maxabs,'max_relative_floor_1e6':self.maxrel,'PSNR_peak1_dB':-10*math.log10(self.sse/self.components)if self.sse else'inf','components':self.components,'nonfinite_components':self.nonfinite,'EV_valid_pixels':self.evs,'EV_excluded_pixels':self.excluded,'EV_abs_median':float(quant[0])if self.evs else None,'EV_abs_p95':float(quant[1])if self.evs else None,'EV_abs_p99':float(quant[2])if self.evs else None,'EV_abs_max_f64':self.evmax}
        del q;self.path.unlink();return r

results=[];failure=None
try:
    for bits in freeze['bits']:
        folder=CASE/('bit'+str(bits));folder.mkdir();out=folder/'native';out.mkdir();levels=2**bits-1;dtype='u1'if bits==8 else'<u2';codes=np.memmap(folder/'input-codes.bin',mode='w+',dtype=dtype,shape=(h,w,3))
        for top in range(0,h,ROWS):
            stop=min(h,top+ROWS);ev=ev_rows(top,stop,h,w);q=np.rint((ev+.5)/3.5*levels).astype(dtype);codes[top:stop]=q if bits==8 else q<<6
        codes.flush();enc=folder/'gain.heic';im=pillow_heif.from_bytes('RGB'if bits==8 else'RGB;16',(w,h),codes.tobytes());im.save(enc,quality=-1,chroma=444,matrix_coefficients=6,enc_params={'preset':'fast','x265:pools':'1','x265:frame-threads':'1'});del im,codes
        eh=parse_heif(enc.read_bytes());ep=eh['items'][str(eh['primary_item_id'])];assert ep['item_type']=='hvc1','Encoded full gain is not direct HEVC; inspect graph before extending splice';assert ep['hvcC']['bit_depth_luma']==bits and ep['hvcC']['chroma_format']==3;assert ep['colr']['matrix_coefficients']==6,'Actual encoded matrix does not match S86 codec choice'
        carrier,identity=replace_map(original,enc.read_bytes(),tmap_metadata(-.5,3,0,3));path=folder/'carrier.heic';path.write_bytes(carrier);new=parse_heif(carrier);changed={tone['item_id'],ref['to_item_ids'][1]};unchanged=0
        for item in parsed['items'].values():
            if item['item_id']in changed:continue
            assert _payload_from_item_extents(original,item)==_payload_from_item_extents(carrier,new['items'][str(item['item_id'])]);unchanged+=1
        row={'bits':bits,'shape':[h,w,3],'identity':identity,'all_old_non_gain_tmap_payloads_preserved':unchanged,'encoded_gain_hvcC':ep['hvcC'],'encoded_gain_colr':ep['colr'],'carrier_bytes':len(carrier),'carrier_sha256':sha(path),'encoded_gain_sha256':sha(enc),'completed':False};results.append(row)
        del carrier,new
        command([W/'oracle',SOURCE,path,out],O/('bit'+str(bits)+'-native.log'),1800);native=json.loads((out/'native.json').read_text());save(O/('bit'+str(bits)+'-native.json'),native);assert native['success']
        decoded={name:np.memmap(out/spec['file'],dtype='<f4',mode='r',shape=(h,w,4))for name,spec in native['files'].items()};head={e['headroom']:np.memmap(out/e['file'],dtype='<f4',mode='r',shape=(h,w,4))for e in native['headrooms']}
        states={name:ErrorState(folder,name)for name in ['encoded_vs_defined_target','quantization_only','codec_provider_additional','CI_SDR_vs_original',*[f'headroom{hr}_native_equation'for hr in head]]};auxmax=0.;source_nonpositive=0
        for top in range(0,h,ROWS):
            stop=min(h,top+ROWS);s=base[top:stop,:,:3].astype('f8');ev=ev_rows(top,stop,h,w);qnorm=np.rint((ev+.5)/3.5*levels)/levels;ideal=(s*np.exp2(ev)).astype('f4').astype('f8');quant=s*np.exp2(-.5+3.5*qnorm);g=decoded['gain'][top:stop,:,:3].astype('f8');actual=decoded['HDR'][top:stop,:,:3];auxmax=max(auxmax,float(abs(g-qnorm).max()));source_nonpositive+=int(((s@Y)<=1e-6).sum())
            states['encoded_vs_defined_target'].add(actual,ideal);states['quantization_only'].add(quant,ideal);states['codec_provider_additional'].add(actual,quant);states['CI_SDR_vs_original'].add(decoded['SDR'][top:stop,:,:3],s)
            for hr,arr in head.items():weight=math.log2(hr)/3;expected=s*np.exp2(weight*(-.5+3.5*g));states[f'headroom{hr}_native_equation'].add(arr[top:stop,:,:3],expected)
        row['metrics']={name:state.finish()for name,state in states.items()};row['native_gain_code_max_abs_vs_uploaded_quantized_code']=auxmax;row['quantization_RGB_EV_bound']=3.5/(2*levels);row['source_luma_le_1e6_pixels']=source_nonpositive;row['ImageIO_full_SDR']=native['ImageIO_full_SDR'];row['actual_headrooms']=[e['headroom']for e in native['headrooms']];row['completed']=True
        m=row['metrics']['encoded_vs_defined_target'];row['old_strict_target_gate']=m['nonfinite_components']==0 and m['components']==h*w*3 and m['max_relative_floor_1e6']<=1e-3 and m['max_abs']<=1e-5 and(m['PSNR_peak1_dB']=='inf'or m['PSNR_peak1_dB']>=60)
        preview(decoded['HDR'][py[:,None],px[None,:],:3],'native '+str(bits)+'bit')
        del decoded,head;save(O/('bit'+str(bits)+'-analysis.json'),row);shutil.rmtree(folder)
except BaseException as exc:
    failure=exc;save(O/'failure.json',{'type':type(exc).__name__,'message':str(exc),'no_new_S82_input_or_secret':True})
finally:
    assert sha(SOURCE)==SOURCE_SHA and sha(CASE/'original-sdr.f32')==base_sha and sha(O/'freeze.json')==freeze_sha
    for p in files:assert sha(p)==freeze['source_sha256'][str(p.relative_to(R))]
    report={'os_build':'26A434','image_version':os.environ.get('ImageVersion'),'freeze_sha256':freeze_sha,'source_original_SHA_unchanged':True,'original_decoded_SDR_SHA_unchanged':True,'photo':'IMG_2600','shape':[h,w,3],'real_photos':1,'new_holdouts':0,'full_resolution':True,'rows':results,'display':display,'preview_input_checks':preview_checks,'all_completed':failure is None and len(results)==1 and all(r['completed']for r in results),'actual_scene_or_inverse_verified':False,'layout_qualification':layout,'global_local_semantic_inverse_changed':False,'S82_people_input_or_transport_used':False,'new_input_secret_or_release':False,'full_carrier_retained_after_job':False,'engineering_accepted':False,'A_phase_complete':False,'acceptance_complete':False};save(O/'analysis.json',report)
    if preview_cards:
        sheet=Image.new('RGB',(2*128,2*122),'white');draw=ImageDraw.Draw(sheet)
        for i,(name,im)in enumerate(preview_cards):x=(i%2)*128;y=(i//2)*122;sheet.paste(im,(x,y));draw.text((x+3,y+99),name,fill='black')
        sheet.save(PRIVATE/'carrier-transport-contact.png',optimize=True);save(PRIVATE/'meaning.json',{'scope':freeze['scope'],'display':display,'interpretation':'RGB opposing stress target checks transport; these are not proposed HDR looks, independent LTM removal or scene recovery previews.'})
        save(PRIVATE/'manifest.json',{'run_id':os.environ['GITHUB_RUN_ID'],'commit':os.environ['GITHUB_SHA'],'os_build':'26A434','people_results_encrypted':True,'files':[{'path':p.name,'size':p.stat().st_size,'sha256':sha(p)}for p in sorted(PRIVATE.iterdir())if p.is_file()]})
        with tarfile.open(W/'previews.tar.gz','w:gz')as t:t.add(PRIVATE,arcname='out')
        command(['gpg','--batch','--trust-model','always','--recipient','28E62F64A29764C2F2AEBF5D5B6B1C101E5F5ABA','--encrypt','--output',ENC/'previews.tar.gz.gpg',W/'previews.tar.gz'],O/'preview-encrypt.log',120);cipher=ENC/'previews.tar.gz.gpg';assert cipher.stat().st_size<160000;save(O/'encrypted-inventory.json',{'file':cipher.name,'size':cipher.stat().st_size,'sha256':sha(cipher),'plaintext_uploaded':False,'full_carrier_or_pixel_arrays_uploaded':False})
if failure:raise failure
print(json.dumps({'full_resolution_photos':1,'bit_depths_completed':[r['bits']for r in results],'ImageIO_SDR_max0':[r['ImageIO_full_SDR']['decoded_sdr_max0_verified']for r in results],'engineering_accepted':False}))
