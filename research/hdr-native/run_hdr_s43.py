"""New codec candidate, fixed S31 opposing RGB target. Synthetic transport only."""
from pathlib import Path
import os,sys,json,hashlib,subprocess,zipfile,shlex,math
import numpy as np
sys.path.insert(0,str(Path('.').resolve()))
from tools.heif_dump import parse_heif
from iso_splice_av1_s43 import replace_map,tmap_metadata
from analyze_hdr_s29 import metric
from render_contract import apply_decoded_map,iso_scale
D=Path('research/hdr-native');W=Path(os.environ['W']);O=W/'out';up=W/'S29.zip'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,v):p.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def command(argv,log):
 with log.open('w') as f:return subprocess.run([str(x) for x in argv],stdout=f,stderr=subprocess.STDOUT,timeout=240).returncode
assert subprocess.check_output(['sw_vers','-buildVersion'],text=True).strip()=='26A434'
assert sha(up)==os.environ['S29_ARCHIVE_SHA256']
freeze={'os_build':'26A434','scope':'Fixed synthetic RGB target only, AV1 native provider and mixed-item transport experiment; no format-conformance or physical/photographic inverse claim','source_sha256':{str(p):sha(p) for p in [D/x for x in ['run_hdr_s43.py','avif_codec_s43.c','iso_splice_av1_s43.py','iso_splice.py','decode_layers_s33.m','iso_oracle_s31.m','hdr_headroom_s29.m','render_contract.py']]},'upstream_artifact_id':os.environ['S29_ARTIFACT_ID'],'upstream_SHA256':sha(up),'fixed_target':'Same S31 rgb-opposing EV=[3u,-.5+2v,2(1-u)], full original source SDR from retained S29 carrier','gain_range_EV':[-.5,3.],'bits':[10,12],'matrices':[0,6],'range':'full','encoder':'AOM lossless, one active thread, 4:4:4','header':'Actual installed libavif header SHA retained, public API used without native-output fit','ftyp_policy':'Preserve original HEVC-base container ftyp, never mislabel primary as AV1; mixed codec native compatibility must be measured','original_thresholds_unchanged':{'linear_abs':1e-5,'PSNR_db':60,'target_relative':1e-3},'all_inverse_masks_unchanged':True}
save(O/'freeze.json',freeze)
prefix=Path(subprocess.check_output(['brew','--prefix','libavif'],text=True).strip());header=prefix/'include/avif/avif.h';save(O/'library-version.json',{'brew_libavif':subprocess.check_output(['brew','list','--versions','libavif'],text=True).strip(),'header_sha256':sha(header),'API_reference':'https://github.com/AOMediaCodec/libavif/blob/main/include/avif/avif.h','numpy':np.__version__})
flags=shlex.split(subprocess.check_output(['pkg-config','--cflags','--libs','libavif'],text=True));assert command(['clang','-O2','-std=c11',D/'avif_codec_s43.c','-o',W/'codec']+flags,O/'codec-build.log')==0
obj=['clang','-O2','-fobjc-arc','-framework','Foundation','-framework','CoreImage','-framework','ImageIO','-framework','Metal','-framework','CoreGraphics']
for name,file in [('layers','decode_layers_s33.m'),('oracle','iso_oracle_s31.m')]:assert command(obj+[D/file,'-o',W/name],O/(name+'-build.log'))==0
with zipfile.ZipFile(up) as z:
 m=json.loads(z.read('manifest.json'));assert m['synthetic_only'] and not m['photos_used'] and m['os_build']=='26A434';name='native/rgb-opposing/dual.heic';b=z.read(name);assert hashlib.sha256(b).hexdigest()==next(x['sha256'] for x in m['files'] if x['path']==name);template=O/'template.heic';template.write_bytes(b)
source=O/'source';source.mkdir();assert command([W/'oracle',template,source,'inspect'],source/'native.log')==0
facts=json.loads((source/'native.json').read_text());w,h=facts['width'],facts['height'];assert (w,h)==(256,128);base=np.fromfile(source/'original-sdr.f32',dtype='<f4').reshape(h,w,4)[...,:3].astype('f8');u=np.broadcast_to((np.arange(w)+.5)/w,(h,w));v=np.broadcast_to(((np.arange(h)+.5)/h)[:,None],(h,w));ev=np.stack([3*u,-.5+2*v,2*(1-u)],-1);code=(ev+.5)/3.5;target=(base*np.exp2(ev)).astype('f4').astype('f8');rows=[]
for matrix in [0,6]:
 for bits in [10,12]:
  p=O/f'AV1-matrix{matrix}-bit{bits}';p.mkdir();levels=2**bits-1;q=np.rint(code*levels).astype('<u2');qn=q.astype('f8')/levels;q.tofile(p/'codes.u16');encoded=p/'gain.avif';lib=p/'libavif-decoded.u16';rc=command([W/'codec',w,h,bits,matrix,p/'codes.u16',encoded,lib],p/'codec.log');row={'matrix':matrix,'bits':bits,'encoder_returncode':rc};rows.append(row)
  if rc:continue
  parsed=parse_heif(encoded.read_bytes());item=parsed['items'][str(parsed['primary_item_id'])];row['encoded_item']={'type':item['item_type'],'pixi':item.get('pixi'),'colr':item.get('colr'),'sha256':sha(encoded)};libdecoded=np.fromfile(lib,dtype='<u2').reshape(h,w,3);row['libavif_code_max_abs']=float(abs(libdecoded.astype('f8')/levels-qn).max());quant=base*np.exp2(-.5+3.5*qn);row['quantization_only']=metric(quant,target);row['quantization_worst_relative_bound']=math.expm1(math.log(2)*3.5/(2*levels))
  carrier,identity=replace_map(template.read_bytes(),encoded.read_bytes(),tmap_metadata(-.5,3,0,3));(p/'carrier.heic').write_bytes(carrier);row['identity']=identity;row['carrier_sha256']=sha(p/'carrier.heic');expected=np.concatenate([qn,np.ones((h,w,1))],-1).astype('<f4');expected.tofile(p/'expected.f32');layers=p/'layers';layers.mkdir();row['layers_returncode']=command([W/'layers',encoded,p/'carrier.heic',p/'expected.f32',layers,1],layers/'native.log');row['layers']=json.loads((layers/'native.json').read_text()) if (layers/'native.json').exists() else {'missing_json':True};row['comparisons']={}
  for name,spec in row['layers'].get('CI_outputs',{}).items():
   if 'file' not in spec:continue
   a=np.fromfile(layers/spec['file'],dtype='<f4').reshape(h,w,4)[...,:3].astype('f8');row['comparisons'][name]={'vs_integer_code':metric(a,qn),'min':float(a.min()) if np.isfinite(a).all() else None,'max':float(a.max()) if np.isfinite(a).all() else None}
  native=p/'native';native.mkdir();row['native_returncode']=command([W/'oracle',template,native,'compare',p/'carrier.heic'],native/'native.log');row['native']=json.loads((native/'native.json').read_text()) if (native/'native.json').exists() else {'missing_json':True}
  if row['native_returncode']==0:
   def load(name):return np.fromfile(native/name,dtype='<f4').reshape(h,w,4)[...,:3].astype('f8')
   s=load('decoded-sdr.f32');f=load('decoded-hdr.f32');g=load('decoded-gain.f32');row['SDR_native_max_abs']=float(abs(s-base).max());row['native_aux_vs_integer_code']=metric(g,qn);row['native_HDR_vs_target']=metric(f,target);row['native_HDR_vs_quantized_target']=metric(f,quant);row['headrooms']=[]
   for entry in row['native']['headrooms']:
    hr=entry['headroom'];expected=apply_decoded_map(base,g,inverse_gamma=1,gain_min=-.5,gain_max=3,scale=iso_scale(hr,capacity_min_log2=0,capacity_max_log2=3),offset_sdr=0,offset_hdr=0);row['headrooms'].append({'headroom':hr,'reference_vs_native':metric(load(entry['file']),expected)})
   a=row['native_HDR_vs_target'];row['encoded_target_gate']=a['max_relative']<=1e-3 and (a['PSNR_peak1_db']=='inf' or a['PSNR_peak1_db']>=60)
  save(O/'analysis-s43.json',{'os_build':'26A434','scope':freeze['scope'],'freeze_sha256':sha(O/'freeze.json'),'rows':rows,'acceptance_complete':False,'A_phase_complete':False})
print(json.dumps({'AV1_cases':len(rows),'native_aux_successes':sum(x.get('native_returncode')==0 for x in rows),'target_passes':sum(x.get('encoded_target_gate',False) for x in rows),'acceptance_complete':False}))
