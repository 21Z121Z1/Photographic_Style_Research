"""Explicit known-target RGB gains, 8/10/12-bit direct HEVC, unchanged SDR.

Synthetic only. No inverse/scene/photographic accuracy is inferred.
"""
from pathlib import Path
import os,subprocess,json,hashlib,math,sys,zipfile,io,xml.etree.ElementTree as ET
sys.path.insert(0,str(Path('.').resolve()))
import numpy as np
import pillow_heif
from PIL import Image
from render_contract import apply_decoded_map,iso_scale
from analyze_hdr_s29 import metric
from iso_splice import replace_map,tmap_metadata
W=Path(os.environ['W']);O=W/'out';O.mkdir(exist_ok=True);D=Path('research/hdr-native');sys.path.insert(0,str(Path('.').resolve()))
from tools.heif_dump import parse_heif
assert subprocess.check_output(['sw_vers','-buildVersion'],text=True).strip()=='26A434'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
freeze={'os_build':'26A434','source_files':{p.name:sha(p) for p in [D/'run_hdr_s31.py',D/'iso_oracle_s31.m',D/'iso_splice.py',D/'render_contract.py']},'target_policy':'H=S*2^creative_EV(p,c), no camera or scene claim; S is original native-decoded SDR, can include zero or signed components','min_EV':-.5,'max_EV':3.,'gamma':1,'offsets':0,'capacity_min_log2':0,'capacity_max_log2':3,'gain_code':'round(((EV+.5)/3.5)*(2^bits-1))','zero_black':'S=H=0 remains0 for any finite gain; ratio unidentifiable but target is known','native_formula_gate':{'max_abs':1e-5,'PSNR_peak1_db_min':60},'encoded_target_gate':{'max_relative':1e-3,'PSNR_peak1_db_min':60},'SDR_max0':True,'synthetic_only':True}
(O/'formula-freeze.json').write_text(json.dumps(freeze,indent=2)+'\n')
(O/'versions.json').write_text(json.dumps({'numpy':np.__version__,'pillow_heif':pillow_heif.__version__,'libheif':pillow_heif.libheif_version(),'encoder_info':getattr(pillow_heif,'libheif_info',lambda:{})()},indent=2,default=str)+'\n')
with (O/'build.log').open('w') as log:subprocess.run(['clang','-O2','-fobjc-arc','-framework','Foundation','-framework','CoreImage','-framework','ImageIO','-framework','Metal','-framework','CoreGraphics',str(D/'iso_oracle_s31.m'),'-o',str(W/'oracle')],stdout=log,stderr=subprocess.STDOUT,check=True)
up=W/'S29.zip';assert sha(up)=='1183b4878cbdf6c8c5aa7c2dac6f4332c2575f959398bd28299fcc87d4f8c81c'
pillow_heif.options.DECODE_THREADS=1;rows=[]
with zipfile.ZipFile(up) as z:
 for name in ['gray-expansion','rgb-opposing','nearblack-highlight','flat-HDR','edge-HDR']:
  p=O/name;p.mkdir();template=p/'template.heic';template.write_bytes(z.read('native/'+name+'/dual.heic'));inp=p/'source';inp.mkdir()
  with (inp/'native.log').open('w') as f:subprocess.run([W/'oracle',template,inp,'inspect'],stdout=f,stderr=subprocess.STDOUT,check=True)
  facts=json.loads((inp/'native.json').read_text());w=facts['width'];h=facts['height'];base=np.fromfile(inp/'original-sdr.f32',dtype='<f4').reshape(h,w,4)[...,:3].astype('f8');u=np.broadcast_to((np.arange(w)+.5)/w,(h,w));v=np.broadcast_to(((np.arange(h)+.5)/h)[:,None],(h,w))
  if name=='gray-expansion':ev=np.repeat((3*u)[...,None],3,-1)
  elif name=='rgb-opposing':ev=np.stack([3*u,-.5+2*v,2*(1-u)],-1)
  elif name=='nearblack-highlight':ev=np.repeat((3*u**.25)[...,None],3,-1)
  elif name=='flat-HDR':ev=np.full((h,w,3),3.)
  else:ev=np.repeat(np.where(u<.5,2.,1.)[...,None],3,-1)
  target=(base*np.exp2(ev)).astype('f4').astype('f8');code=(ev+.5)/3.5;np.save(p/'target.npy',target.astype('f4'));np.save(p/'log2-gain.npy',ev.astype('f4'));target=np.load(p/'target.npy').astype('f8')
  # npy is diagnostic generated synthetic data, never a real-photo output.
  for bits in [8,10,12]:
   out=p/f'bit{bits}';out.mkdir();levels=2**bits-1;q=np.rint(code*levels).astype('u2' if bits>8 else 'u1');qnorm=q.astype('f8')/levels
   if bits==8:im=pillow_heif.from_bytes('RGB',(w,h),q.tobytes())
   else:
    pillow_heif.options.SAVE_HDR_TO_12_BIT=bits==12
    # ;16 input is shifted by16-bitdepth on encode, per pinned source. Store
    # each desired code in those high bits; verify actual hvcC and decoder.
    raw=(q.astype('u2')<<(16-bits)).astype('<u2');im=pillow_heif.from_bytes('RGB;16',(w,h),raw.tobytes())
   buf=io.BytesIO();im.save(buf,quality=-1,chroma=444,matrix_coefficients=0,enc_params={'preset':'fast','x265:pools':'1','x265:frame-threads':'1'});encoded=buf.getvalue();(out/'encoded-gain.heic').write_bytes(encoded);eh=parse_heif(encoded);ei=eh['items'][str(eh['primary_item_id'])];assert ei['hvcC']['bit_depth_luma']==bits and ei['hvcC']['chroma_format']==3
   carrier,identity=replace_map(template.read_bytes(),encoded,tmap_metadata(-.5,3,0,3));(out/'carrier.heic').write_bytes(carrier)
   with (out/'native.log').open('w') as f:rc=subprocess.run([W/'oracle',template,out,'compare',out/'carrier.heic'],stdout=f,stderr=subprocess.STDOUT).returncode
   row={'case':name,'bits':bits,'encoder':'libheif/x265 lossless RGB matrix0 4:4:4','identity':identity,'gain_hvcC':ei['hvcC'],'carrier_sha256':hashlib.sha256(carrier).hexdigest(),'native_returncode':rc,'native':json.loads((out/'native.json').read_text())};rows.append(row)
   if rc:continue
   def load(n):return np.fromfile(out/n,dtype='<f4').reshape(h,w,4)[...,:3].astype('f8')
   native=load('decoded-hdr.f32');gain=load('decoded-gain.f32');sdr=load('decoded-sdr.f32');quantized=base*np.exp2(-.5+3.5*qnorm)
   row['quantization_only']=metric(quantized,target);row['codec_native_additional']=metric(native,quantized);row['native_HDR_vs_defined_target']=metric(native,target);row['native_decoded_gain_vs_integer_code_max_abs']=float(abs(gain-qnorm).max());row['SDR_native_max_abs']=float(abs(sdr-base).max());row['headrooms']=[]
   for sweep in row['native']['headrooms']:
    hr=sweep['headroom'];expected=apply_decoded_map(base,gain,inverse_gamma=1,gain_min=-.5,gain_max=3,scale=iso_scale(hr,capacity_min_log2=0,capacity_max_log2=3),offset_sdr=0,offset_hdr=0);row['headrooms'].append({'headroom':hr,'reference_vs_native':metric(expected,load(sweep['file']))})
   e=row['native_HDR_vs_defined_target'];row['encoded_target_gate']=e['max_relative']<=1e-3 and (e['PSNR_peak1_db']=='inf' or e['PSNR_peak1_db']>=60)
report={'os_build':'26A434','scope':'5synthetic pairs, not5photos or physical scene recovery','formula_freeze_sha256':sha(O/'formula-freeze.json'),'rows':rows,'acceptance_complete':False}
(O/'analysis-s31.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');print(json.dumps({'native_success_count':sum(r['native_returncode']==0 for r in rows),'requests':len(rows),'passed_target_cases':{str(bits):sum(r.get('encoded_target_gate',False) for r in rows if r['bits']==bits) for bits in [8,10,12]},'acceptance_complete':False}))
