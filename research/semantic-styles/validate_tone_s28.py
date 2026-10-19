"""Runner-only validation of serialized ratio maps and spatial curve inversion.

No new native forward capture, no camera truth, no acceptance-mask changes.
The 8-bit test is log-gain scalar quantization, not HEIF codec conformance.
"""
from pathlib import Path
from fractions import Fraction as Q
import os,sys,hashlib,json,subprocess,zipfile,shutil,tarfile
import numpy as np
from spatial_curve_retarget import retarget_curve_point
W=Path(os.environ['W']);O=W/'out';O.mkdir(exist_ok=True)
assert subprocess.check_output(['sw_vers','-buildVersion'],text=True).strip()=='26A434'
p=W/'s27.zip'
with p.open('wb') as f:subprocess.run(['gh','api','repos/21Z121Z1/Photographic_Style_Research/actions/artifacts/12176180324/zip'],stdout=f,check=True)
with p.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()=='92dc95ce0a1193c72a55f149d8dd4bda3dd9c1ce202cfb32bc7ae83b209fedaf'
with zipfile.ZipFile(p) as z:
 name=next(n for n in z.namelist() if n.endswith('.gpg'))
 with z.open(name) as a,(W/'s27.gpg').open('wb') as b:shutil.copyfileobj(a,b)
key=W/'session';key.write_text(os.environ['S27_ARCHIVE_SESSION']+'\n');key.chmod(0o600)
with key.open('rb') as f,(O/'prior-decrypt.log').open('w') as log:subprocess.run(['gpg','--batch','--override-session-key-fd',str(f.fileno()),'--output',str(W/'s27.tar.gz'),'--decrypt',str(W/'s27.gpg')],pass_fds=(f.fileno(),),stdout=log,stderr=subprocess.STDOUT,check=True)
key.unlink();D=W/'s27';D.mkdir()
with tarfile.open(W/'s27.tar.gz') as t:t.extractall(D,filter='data')
manifest=json.loads((D/'out/manifest.json').read_text())
for row in manifest['files']:
 p=D/'out'/row['path']
 with p.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==row['sha256']
 assert p.stat().st_size==row['size']
(O/'prior-verification.json').write_text(json.dumps({'source_run':39227962537,'source_artifact':12176180324,'zip_sha256':'92dc95ce0a1193c72a55f149d8dd4bda3dd9c1ce202cfb32bc7ae83b209fedaf','files':len(manifest['files']),'failures':0},indent=2)+'\n')
subprocess.run([sys.executable,'research/semantic-styles/test_spatial_curve_retarget_s27.py',str(O/'scalar-tests')],check=True,stdout=subprocess.DEVNULL)
# Verify the map actually serialized by S27, not its unsaved float64 precursor.
root=D/'out';ref=np.fromfile(root/'native/reference.f16','<f2').reshape(384,512,4)[...,:3].astype('f8');target=np.fromfile(root/'native/local-neutral.f16','<f2').reshape(384,512,4)[...,:3].astype('f8');path=root/'analysis/local-neutral-gain-map.private.npz'
with np.load(path) as m:g=m['log2_rgb_gain'];mask=m['positive_representation_mask']
assert g.dtype==np.dtype('f4') and int(mask.sum())==186949 and g.shape==(384,512,3)
def metrics(reconstructed):
 delta=abs(reconstructed[mask]-target[mask]);rel=delta/abs(target[mask]);luma=np.array([.22897456,.69173852,.07928691]);ev=np.log2((reconstructed[mask]@luma)/(target[mask]@luma))
 return {'positive_pixels':int(mask.sum()),'coverage':float(mask.mean()),'max_abs':float(delta.max()),'max_relative':float(rel.max()),'PSNR_peak1_db':float(-10*np.log10(np.mean(delta**2))),'luma_EV_MAE':float(np.mean(abs(ev))),'luma_EV_max_abs':float(np.max(abs(ev)))}
saved=metrics(ref*np.exp2(g.astype('f8')))
assert saved['max_relative']<=1e-3
allg=np.log2(target[mask]/ref[mask]);lo=allg.min(0);hi=allg.max(0);step=(hi-lo)/255
code=np.rint((allg-lo)/step).clip(0,255).astype('u1');decoded=lo+code.astype('f8')*step;quant=np.copy(ref);quant[mask]=ref[mask]*np.exp2(decoded);qmetrics=metrics(quant);gain_ev_error=abs(decoded-allg)
serialized={'os_build':'26A434','source_run':39227962537,'source_artifact':12176180324,'source_map_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'operator':'local-neutral','float32_serialized_RGB_gain_map':saved,'eight_bit_log2_RGB_scalar_quantizer':{'per_channel_min_EV':lo.tolist(),'per_channel_max_EV':hi.tolist(),'per_channel_step_EV':step.tolist(),'per_channel_half_LSB_EV_bound':(step/2).tolist(),'per_channel_measured_max_EV':gain_ev_error.max(0).tolist(),'metrics':qmetrics,'scope':'Explicit per-channel uniform log2-gain quantizer, no HEIF compression/codec/metadata roundtrip claim'},'native_inverse_accuracy_measured':False,'camera_inverse_verified':False,'thumbnail_encoding_error_included':False,'SDR_carrier_reencoded':False,'old_acceptance_gate_modified':False}
(O/'serialized-map-validation.json').write_text(json.dumps(serialized,indent=2,allow_nan=False)+'\n')
# The new conditional spatial model: each pixel receives a different mixture;
# correct forward blend followed by set inverse must contain the known value.
knots=[Q(0),Q(1,2),Q(1)];curves=[[Q(0),Q(1,2),Q(1)],[Q(0),Q(1,4),Q(1)]];neutral=[knots,knots];misses=0;bad_candidates=0;total=0;max_relative=0.
def eval_piece(table,x):
 return table[0]+x*2*(table[1]-table[0]) if x<=Q(1,2) else table[1]+(x-Q(1,2))*2*(table[2]-table[1])
for wi in range(33):
 w=Q(wi,32)
 for qi in range(1,129):
  x=Q(qi,128);y=(1-w)*eval_piece(curves[0],x)+w*eval_piece(curves[1],x)
  r=retarget_curve_point(y,knots,curves,neutral,[1-w,w],coordinate_space='Declared synthetic scalar; not scene P3')
  misses+=not(r['neutral_lower']<=float(x)<=r['neutral_upper']);total+=1
  if r['guaranteed_1e3']:
   err=abs(r['candidate']-float(x))/float(x);max_relative=max(max_relative,err);bad_candidates+=err>1e-3
assert misses==0 and bad_candidates==0
(O/'spatial-field-validation.json').write_text(json.dumps({'scope':'Conditional exact rational scalar curves with 33 spatial mixtures and 128 inputs; no actual camera weights/domain supplied','os_build':'26A434','queries':total,'interval_misses':misses,'guaranteed_candidate_violations':bad_candidates,'max_relative':max_relative,'camera_inverse_verified':False,'full_consumer_domain_certified':False,'one_e3_threshold_modified':False,'source_sha256':hashlib.sha256(Path('research/semantic-styles/spatial_curve_retarget.py').read_bytes()).hexdigest()},indent=2)+'\n')
print('S28 numerical checks completed on copies. No native recapture or photo upload; all numeric results encrypted.')
