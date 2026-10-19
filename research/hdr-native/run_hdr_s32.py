"""Single fixture: locate matrix/bit-depth mismatch, no fitted inverse model."""
from pathlib import Path
import os,sys,subprocess,json,hashlib,zipfile,io
sys.path.insert(0,str(Path('.').resolve()))
import numpy as np,pillow_heif
from tools.heif_dump import parse_heif
from iso_splice import replace_map,tmap_metadata
from render_contract import apply_decoded_map,iso_scale
from analyze_hdr_s29 import metric
W=Path(os.environ['W']);O=W/'out';O.mkdir(exist_ok=True);D=Path('research/hdr-native');up=W/'S31.zip'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert subprocess.check_output(['sw_vers','-buildVersion'],text=True).strip()=='26A434'
upstream_sha=os.environ.get('S31_ARCHIVE_SHA256','f4d90ac39646f813aae1bba6044167e1e2af03a8aab3c4d1575f337f8b918cdd');assert len(upstream_sha)==64 and sha(up)==upstream_sha
(O/'upstream-archive.json').write_text(json.dumps({'sha256':upstream_sha,'artifact_id':os.environ.get('S31_ARTIFACT_ID'),'parent_stage':'s31'},indent=2)+'\n')
(O/'freeze.json').write_text(json.dumps({'scope':'Readback operator diagnosis; no inverse, scene or five-photo claim','source_sha256':{p.name:sha(p) for p in [D/'run_hdr_s32.py',D/'raw_gain_s32.m',D/'iso_oracle_s31.m',D/'iso_splice.py']},'matrices':[1,6],'bits':[8,10,12],'gain_min_EV':-.5,'gain_max_EV':3,'gamma':1,'offset':0,'capacity_log2':3,'old_thresholds_unchanged':True,'comparison_rule':'Direct storage-order code comparison; flipped-array diagnostic reported separately and never silently selected'},indent=2)+'\n')
flags=['clang','-O2','-fobjc-arc','-framework','Foundation','-framework','CoreImage','-framework','ImageIO','-framework','Metal','-framework','CoreGraphics']
for name,source in [('oracle','iso_oracle_s31.m'),('raw','raw_gain_s32.m')]:
 with (O/(name+'-build.log')).open('w') as f:subprocess.run(flags+[str(D/source),'-o',str(W/name)],stdout=f,stderr=subprocess.STDOUT,check=True)
with zipfile.ZipFile(up) as z:
 manifest=json.loads(z.read('manifest.json'));assert manifest['synthetic_only'] and manifest['photos_used'] is False and manifest['os_build']=='26A434'
 template=O/'template.heic';template.write_bytes(z.read('rgb-opposing/template.heic'));b=z.read('rgb-opposing/source/original-sdr.f32')
base=np.frombuffer(b,dtype='<f4').reshape(128,256,4)[...,:3].astype('f8');h,w=base.shape[:2];u=np.broadcast_to((np.arange(w)+.5)/w,(h,w));v=np.broadcast_to(((np.arange(h)+.5)/h)[:,None],(h,w));ev=np.stack([3*u,-.5+2*v,2*(1-u)],-1);code=(ev+.5)/3.5;target=(base*np.exp2(ev)).astype('f4').astype('f8');rows=[];pillow_heif.options.DECODE_THREADS=1
for matrix in [1,6]:
 for bits in [8,10,12]:
  p=O/f'matrix{matrix}-bit{bits}';p.mkdir();levels=2**bits-1;q=np.rint(code*levels).astype('u1' if bits==8 else 'u2');qn=q.astype('f8')/levels;pillow_heif.options.SAVE_HDR_TO_12_BIT=bits==12
  raw=q.tobytes() if bits==8 else (q.astype('u2')<<(16-bits)).astype('<u2').tobytes();im=pillow_heif.from_bytes('RGB' if bits==8 else 'RGB;16',(w,h),raw);buf=io.BytesIO();im.save(buf,quality=-1,chroma=444,matrix_coefficients=matrix,enc_params={'preset':'fast','x265:pools':'1','x265:frame-threads':'1'});encoded=buf.getvalue();file=p/'encoded-gain.heic';file.write_bytes(encoded);parsed=parse_heif(encoded);item=parsed['items'][str(parsed['primary_item_id'])];assert item['hvcC']['bit_depth_luma']==bits
  decoded=pillow_heif.open_heif(encoded,convert_hdr_to_8bit=False,hdr_to_16bit=False);rgb=np.asarray(decoded[decoded.primary_index]).astype('f8')/levels
  carrier,identity=replace_map(template.read_bytes(),encoded,tmap_metadata(-.5,3,0,3));(p/'carrier.heic').write_bytes(carrier)
  with (p/'raw.log').open('w') as f:subprocess.run([W/'raw',file,p],stdout=f,stderr=subprocess.STDOUT,check=True)
  with (p/'oracle.log').open('w') as f:rc=subprocess.run([W/'oracle',template,p,'compare',p/'carrier.heic'],stdout=f,stderr=subprocess.STDOUT).returncode
  r={'matrix':matrix,'bits':bits,'native_returncode':rc,'native':json.loads((p/'native.json').read_text()),'primary_readback':json.loads((p/'primary-readback.json').read_text()),'identity':identity,'hvcC':item['hvcC'],'colr':item.get('colr'),'libheif_vs_integer_code_max_abs':float(abs(rgb-qn).max())};rows.append(r)
  def load(n):return np.fromfile(p/n,dtype='<f4').reshape(h,w,4)[...,:3].astype('f8')
  if r['primary_readback']['CIImage_present']:r['native_primary_vs_integer_code_max_abs']=float(abs(load('gain-primary-raw.f32')-qn).max())
  if rc:continue
  gain=load('decoded-gain.f32');full=load('decoded-hdr.f32');r['native_aux_vs_integer_code_max_abs']=float(abs(gain-qn).max());r['native_aux_vs_libheif_max_abs']=float(abs(gain-rgb).max());r['native_aux_vertical_flip_vs_integer_code_max_abs']=float(abs(gain[::-1]-qn).max());r['native_HDR_vs_target']=metric(full,target);r['SDR_native_max_abs']=float(abs(load('decoded-sdr.f32')-base).max());r['headrooms']=[]
  for sw in r['native']['headrooms']:
   hr=sw['headroom'];expected=apply_decoded_map(base,gain,inverse_gamma=1,gain_min=-.5,gain_max=3,scale=iso_scale(hr,capacity_min_log2=0,capacity_max_log2=3),offset_sdr=0,offset_hdr=0);r['headrooms'].append({'headroom':hr,'reference_vs_native':metric(expected,load(sw['file']))})
(O/'analysis-s32.json').write_text(json.dumps({'os_build':'26A434','scope':'Single synthetic RGB fixture, matrix and bit-depth readback diagnosis only','rows':rows,'acceptance_complete':False},indent=2,allow_nan=False)+'\n');print(json.dumps({'requests':len(rows),'native_success_count':sum(r['native_returncode']==0 for r in rows),'acceptance_complete':False}))
