"""Worst-case practical transport diagnosis: fixed display, luminance,10/12bit.

No scene/tone/semantic model is changed. Exact pixels stay encrypted.
"""
from pathlib import Path
import ast,json,hashlib,subprocess,sys,os,math,tarfile,shutil
import numpy as np
import pillow_heif
from PIL import Image,ImageDraw
R=Path.cwd();D=R/'research/hdr-native';W=Path(os.environ['W']);O=W/'out';PRIVATE=W/'private';ENC=W/'encrypted';sys.path[:0]=[str(R),str(D)]
from tools.heif_dump import parse_heif
from iso_splice import replace_map
Y=np.array([.2289745641,.6917385218,.0792869141]);ROWS=32
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,x):
 with Path(p).open('x')as f:json.dump(x,f,indent=2,allow_nan=False);f.write('\n')
def call(args,log):
 with Path(log).open('x')as f:subprocess.run(list(map(str,args)),stdout=f,stderr=subprocess.STDOUT,check=True,timeout=1800)
def histogram_q(hist,p):
 return int(np.searchsorted(np.cumsum(hist),math.ceil(p*int(hist.sum()))))if hist.sum()else None
def hist_summary(hist):
 return {'n':int(hist.sum()),'p50':histogram_q(hist,.5),'p95':histogram_q(hist,.95),'p99':histogram_q(hist,.99),'max':int(np.flatnonzero(hist)[-1])if hist.sum()else None}
class Bins:
 def __init__(self,folder):
  self.edges=[-math.inf,0,1e-6,1e-5,1e-4,1e-3,1e-2,.1,1,math.inf];self.rows=[]
  for i in range(9):
   p=folder/('brightness-'+str(i)+'.f32');self.rows.append({'file':p,'out':p.open('xb'),'pixels':0,'positive_EV':0,'actual_nonpositive':0,'reference_nonpositive':0,'EV_max':0.})
 def add(self,a,b):
  ya=np.asarray(a,'f8')@Y;yb=np.asarray(b,'f8')@Y;assert np.isfinite(ya).all()and np.isfinite(yb).all()
  indices=np.searchsorted(self.edges[1:],yb,side='left')
  for i,r in enumerate(self.rows):
   m=indices==i;r['pixels']+=int(m.sum());r['actual_nonpositive']+=int((m&(ya<=0)).sum());r['reference_nonpositive']+=int((m&(yb<=0)).sum());good=m&(ya>0)&(yb>0);v=abs(np.log2(ya[good]/yb[good]));r['positive_EV']+=len(v)
   if len(v):r['EV_max']=max(r['EV_max'],float(v.max()));r['out'].write(v.astype('<f4').tobytes())
 def finish(self):
  result=[]
  for i,r in enumerate(self.rows):
   r['out'].close();v=np.memmap(r['file'],dtype='<f4',mode='r')if r['positive_EV']else None;q=np.quantile(v,[.5,.95,.99]).tolist()if v is not None else[None]*3
   result.append({'reference_Y_interval':[str(self.edges[i]),str(self.edges[i+1])],'pixels':r['pixels'],'positive_EV_pixels':r['positive_EV'],'actual_nonpositive':r['actual_nonpositive'],'reference_nonpositive':r['reference_nonpositive'],'EV_abs_median_p95_p99':q,'EV_abs_max_f64':r['EV_max']if r['positive_EV']else None});del v;r['file'].unlink()
  return result
def view_metrics(actual,reference,cpu,folder,tag):
 h,w=reference.shape[:2];va=np.memmap(folder/(tag+'-actual.u8'),dtype='u1',mode='w+',shape=(h,w,3));vb=np.memmap(folder/(tag+'-reference.u8'),dtype='u1',mode='w+',shape=(h,w,3));hist=np.zeros(256,'i8');sse=0.;same=True;checks=0
 for top in range(0,h,ROWS):
  end=min(h,top+ROWS)
  for a,out in [(actual,va),(reference,vb)]:
   src=np.array(a[top:end,:,:3],dtype='f4',copy=True);before=hashlib.sha256(src.tobytes()).hexdigest();x=src.copy();cpu.apply(__import__('PyOpenColorIO').PackedImageDesc(x,w,end-top,3));assert np.isfinite(x).all();out[top:end]=np.rint(np.clip(x,0,1)*255).astype('u1');same&=before==hashlib.sha256(src.tobytes()).hexdigest();checks+=1
  diff=va[top:end].astype('i2')-vb[top:end].astype('i2');hist+=np.bincount(abs(diff).max(-1).ravel(),minlength=256);sse+=float(np.square(diff.astype('f8')).sum())
 va.flush();vb.flush();grad=np.zeros(511,'i8');edge=np.zeros_like(grad);lap=np.zeros(2041,'i8')
 for top in range(0,h,ROWS):
  end=min(h,top+ROWS);a=va[top:end].astype('i4');b=vb[top:end].astype('i4');d=a-b;dg=np.diff(d,axis=1);ref=np.diff(b,axis=1);v=abs(dg).max(-1);grad+=np.bincount(v.ravel(),minlength=511);selected=abs(ref).max(-1)>=4;edge+=np.bincount(v[selected],minlength=511)
  last=min(end,h-1)
  if last>top:
   da=va[top+1:last+1].astype('i4')-va[top:last].astype('i4');db=vb[top+1:last+1].astype('i4')-vb[top:last].astype('i4');v=abs(da-db).max(-1);grad+=np.bincount(v.ravel(),minlength=511);edge+=np.bincount(v[abs(db).max(-1)>=4],minlength=511)
  lo=max(top,1);hi=min(end,h-1)
  if hi>lo:
   def curvature(q):return q[lo:hi,2:].astype('i4')+q[lo:hi,:-2].astype('i4')+q[lo-1:hi-1,1:-1].astype('i4')+q[lo+1:hi+1,1:-1].astype('i4')-4*q[lo:hi,1:-1].astype('i4')
   v=abs(curvature(va)-curvature(vb)).max(-1);lap+=np.bincount(v.ravel(),minlength=2041)
 assert same
 ys=np.floor((np.arange(120)+.5)*h/120).astype(int);xs=np.floor((np.arange(160)+.5)*w/160).astype(int);aa=np.array(va[ys[:,None],xs[None,:]],copy=True);bb=np.array(vb[ys[:,None],xs[None,:]],copy=True)
 result={'display_pixel_max_RGB_code_error':hist_summary(hist),'pixel_counts_error_gt_codes':{str(k):int(hist[k+1:].sum())for k in [0,1,2,4,8,16]},'pixel_fractions_error_gt_codes':{str(k):float(hist[k+1:].sum()/hist.sum())for k in[0,1,2,4,8,16]},'PSNR_peak255_dB':-10*math.log10(sse/(h*w*3*255**2))if sse else'inf','gradient_error_codes_all':hist_summary(grad),'gradient_error_codes_at_reference_edges_ge4':hist_summary(edge),'laplacian_error_codes_all':hist_summary(lap),'preview_copy_SHA_checks':checks,'all_preview_input_SHA_equal':same,'scope':'Fixed neutral ACES SDR view of both endpoints, not real HDR display acceptance. Edge/curvature statistics are proxies, not certified halo visibility. Threshold cuts are diagnostics, not new acceptance gates.'}
 del va,vb
 for suffix in ['actual','reference']:(folder/(tag+'-'+suffix+'.u8')).unlink()
 return result,aa,bb
assert subprocess.check_output(['sw_vers','-buildVersion'],text=True).strip()=='26A434'
case=next(c for c in json.loads((D/'inputs-s89.json').read_text())['cases']if c['photo']=='IMG_2600')
tree=ast.parse((D/'run_hdr_s89.py').read_text());defs=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in['bindings','derive_case']];ns={'ast':ast,'json':json,'hashlib':hashlib,'D':D};exec(compile(ast.Module(body=defs,type_ignores=[]),'S89-derivation-functions-only','exec'),ns);driver,helper,binding=ns['derive_case'](case);prefix=driver.split('codes=np.memmap',1)[0];ast.parse(prefix)
sources=['run_hdr_s90.py','run_hdr_s89.py','run_hdr_s88.py','rebuild_master_s88.py','run_hdr_s42.py','run_hdr_s47.py','render_intent_s44.py','carrier_readback_s87.m','carrier_case_s87.py','iso_splice.py','inputs-s89.json']
freeze={'OS_build':'26A434','image_version':os.environ.get('ImageVersion'),'photo':'IMG_2600','role':'Worst-case development diagnosis selected from S89; not holdout','source_sha256':{str((D/f).relative_to(R)):sha(D/f)for f in sources},'prefix_sha256':hashlib.sha256(prefix.encode()).hexdigest(),'binding':binding,'source_math':'S89->S88 exact prefix before encoding, frozen S42 input rebuild and S44/S47 target. M/target/offset/range identical for10/12bit. New display/statistics only; no semantic or tone inverse change.','variants':[10,12],'codec_rule':'matrix6/4:4:4 lossless; high bits of uint16; actual hvcC bitdepth required. Stop unsupported12bit, do not reinterpret as10.','fixed_display':'Same pinned cg-config-v2.2.0_aces-v1.3_ocio-v2.4, ACES1.0 SDR Video,LinearP3-D65->sRGB,0EV; clip only resulting display view, never source arrays.','diagnostic_code_cuts':[0,1,2,4,8,16],'diagnostic_brightness_edges':['-inf',0,1e-6,1e-5,1e-4,1e-3,1e-2,.1,1,'inf'],'headrooms':[1,2,8],'predeclared_hypothesis':'12bit nominal gain step is(hi-lo)/4095 versus/1023. Actual codec/provider precision and display improvement require measurement; not bit-exact research.','full_carrier_or_master_archival':False,'public_max_bytes':500000,'private_cipher_max_bytes':2000000,'engineering_accepted':False,'A_phase_complete':False,'acceptance_complete':False}
save(O/'suite-freeze.json',freeze);frozen=sha(O/'suite-freeze.json');(W/'rebuild.py').write_text(helper);os.environ.update(HDR_S89_CASE_JSON=json.dumps(case),HDR_S89_REBUILD=str(W/'rebuild.py'));p={};exec(compile(prefix,'S88-prefix-before-gain-encoding','exec'),p)
folder=p['folder'];s=p['s'];target=p['target'];h,w=p['h'],p['w'];rotation=p['k'];sr=np.rot90(s[...,:3],k=rotation);hr=np.rot90(target,k=rotation);lr=np.rot90(p['lg'],k=rotation);height,width=hr.shape[:2];lo,hi=p['lo'],p['hi'];off=p['off'];encoded_off=p['encoded_off'];cpu=p['g']['cpu'];source=p['source'];original=p['original'];baseline=p['before_pixels'];libinfo=getattr(pillow_heif,'libheif_info',lambda:{'unavailable':True})();save(O/'codec-versions.json',{'pillow_heif':pillow_heif.__version__,'libheif':libinfo})
call(['clang','-O2','-fobjc-arc','-framework','Foundation','-framework','CoreImage','-framework','ImageIO','-framework','Metal','-framework','CoreGraphics',D/'carrier_readback_s87.m','-o',W/'oracle'],O/'oracle-build.log');node=next(n for n in ast.parse((D/'carrier_case_s87.py').read_text()).body if isinstance(n,ast.ClassDef)and n.name=='ErrorState');results=[]
try:
 for bits in [10,12]:
  vdir=folder/('bits'+str(bits));vdir.mkdir();private=PRIVATE/('bits'+str(bits));private.mkdir();row={'bits':bits,'completed':False};results.append(row);levels=2**bits-1;codes=np.memmap(vdir/'codes.u16',dtype='<u2',mode='w+',shape=(h,w,3))
  for top in range(0,h,ROWS):end=min(h,top+ROWS);codes[top:end]=np.rint((p['lg'][top:end]-lo)/(hi-lo)*levels).astype('u2')<<(16-bits)
  codes.flush();pillow_heif.options.SAVE_HDR_TO_12_BIT=bits==12;im=pillow_heif.from_bytes('RGB;16',(w,h),codes.tobytes());enc=vdir/'gain.heic';im.save(enc,quality=-1,chroma=444,matrix_coefficients=6,enc_params={'preset':'fast','x265:pools':'1','x265:frame-threads':'1'});del im;ep=parse_heif(enc.read_bytes());ep=ep['items'][str(ep['primary_item_id'])];row['actual_hvcC']=ep['hvcC'];row['actual_colr']=ep['colr'];assert ep['hvcC']['bit_depth_luma']==bits and ep['hvcC']['chroma_format']==3 and ep['colr']['matrix_coefficients']==6
  data,identity=replace_map(original,enc.read_bytes(),p['meta']);carrier=vdir/'carrier.heic';carrier.write_bytes(data);del data;row.update(carrier_sha256=sha(carrier),carrier_bytes=carrier.stat().st_size,identity=identity,gain_nominal_step_EV=(hi-lo)/levels);native_dir=vdir/'native';native_dir.mkdir();call([W/'oracle',source,carrier,native_dir],O/('native-'+str(bits)+'.log'));native=json.loads((native_dir/'native.json').read_text());save(O/('native-'+str(bits)+'.json'),native);assert native['success']and native['ImageIO_full_SDR']['decoded_sdr_max0_verified'];read=lambda spec:np.memmap(native_dir/spec['file'],dtype='<f4',mode='r',shape=(height,width,4));actual=read(native['files']['HDR']);gain=read(native['files']['gain']);heads={q['headroom']:read(q)for q in native['headrooms']};cr=np.rot90(codes,k=rotation);scope={'np':np,'math':math,'Y':Y,'PRIVATE':private,'save':save};exec(compile(ast.Module(body=[node],type_ignores=[]),'S87-original-ErrorState','exec'),scope);states={tag:scope['ErrorState'](vdir,tag)for tag in['total','quantization','codec_provider','native_actual_gain_equation']};bins=Bins(vdir)
  for top in range(0,height,ROWS):
   end=min(height,top+ROWS);b=sr[top:end].astype('f8');H=hr[top:end].astype('f8');l=lr[top:end].astype('f8');q=(cr[top:end]>>(16-bits)).astype('f8')/levels;quant=(b+encoded_off)*np.exp2(lo+(hi-lo)*q)-encoded_off;rational=(b+encoded_off)*np.exp2(l)-encoded_off;a=actual[top:end,:,:3];g=gain[top:end,:,:3].astype('f8');states['total'].add(a,H);states['quantization'].add(quant,rational);states['codec_provider'].add(a,quant);states['native_actual_gain_equation'].add(a,(b+encoded_off)*np.exp2(lo+(hi-lo)*g)-encoded_off);bins.add(a,H)
  row['metrics']={k:v.finish()for k,v in states.items()};row['brightness_bins']=bins.finish();row['SDR_max0']=True;row['display']={};sheet=Image.new('RGB',(480,432),'white');draw=ImageDraw.Draw(sheet);native_hashes_before={q['file']:sha(native_dir/q['file'])for q in native['headrooms']}
  for i,head in enumerate([1,2,8]):
   ideal_path=vdir/('ideal-h'+str(head)+'.f32');ideal=np.memmap(ideal_path,dtype='<f4',mode='w+',shape=(height,width,3))
   for top in range(0,height,ROWS):
    end=min(height,top+ROWS);b=sr[top:end].astype('f8');H=hr[top:end].astype('f8');ideal[top:end]=((b+off)*np.exp2(math.log2(head)/3*np.log2((H+off)/(b+off)))-off).astype('f4')
   ideal.flush();metric,aa,bb=view_metrics(heads[head],ideal,cpu,vdir,'h'+str(head));row['display'][str(head)]=metric;diff=np.clip(abs(aa.astype('i2')-bb.astype('i2'))*8,0,255).astype('u1')
   for j,(label,img)in enumerate([('ideal',bb),('native',aa),('diff x8',diff)]):sheet.paste(Image.fromarray(img),(j*160,i*144));draw.text((j*160+2,i*144+123),str(bits)+'b h'+str(head)+' '+label,fill='black')
   del ideal;ideal_path.unlink()
  sheet.save(private/'contact.png');assert native_hashes_before=={q['file']:sha(native_dir/q['file'])for q in native['headrooms']};assert baseline=={f:sha(folder/f)for f in baseline};assert sha(source)==case['source_sha256'];row['source_and_native_inputs_SHA_unchanged']=True;row['completed']=True;save(O/('analysis-'+str(bits)+'.json'),row)
  for name in ['codes','cr','actual','gain','heads','states','bins','a']:globals().pop(name,None)
  shutil.rmtree(vdir)
except Exception as error:
 save(O/'failure.json',{'type':type(error).__name__,'message':str(error),'completed_bits':[r['bits']for r in results if r['completed']],'source_math_or_gates_changed':False})
finally:
 save(O/'analysis.json',{'OS_build':'26A434','image_version':os.environ.get('ImageVersion'),'source_commit':os.environ['GITHUB_SHA'],'rows':results,'completed':len(results)==2 and all(r['completed']for r in results),'scope':freeze,'M_S_H_SHA_baseline':baseline,'engineering_accepted':False,'A_phase_complete':False,'acceptance_complete':False});assert sha(O/'suite-freeze.json')==frozen
save(PRIVATE/'manifest.json',{'run_id':os.environ['GITHUB_RUN_ID'],'commit':os.environ['GITHUB_SHA'],'os_build':'26A434','people_results_encrypted':True,'files':[{'path':str(q.relative_to(PRIVATE)),'size':q.stat().st_size,'sha256':sha(q)}for q in sorted(PRIVATE.rglob('*'))if q.is_file()]})
with tarfile.open(W/'previews.tar.gz','w:gz')as tar:tar.add(PRIVATE,arcname='out')
call(['gpg','--batch','--trust-model','always','--recipient','28E62F64A29764C2F2AEBF5D5B6B1C101E5F5ABA','--encrypt','--output',ENC/'previews.tar.gz.gpg',W/'previews.tar.gz'],O/'encrypt.log');cipher=ENC/'previews.tar.gz.gpg';save(O/'encrypted-inventory.json',{'files':[{'file':cipher.name,'size':cipher.stat().st_size,'sha256':sha(cipher)}],'full_new_carrier_master_archived':False,'plaintext_uploaded':False});assert cipher.stat().st_size<2000000
print(json.dumps({'completed_bits':[r['bits']for r in results if r['completed']],'A_phase_complete':False}));sys.exit(0 if len(results)==2 and all(r['completed']for r in results)else 1)
