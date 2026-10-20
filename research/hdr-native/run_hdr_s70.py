"""Original CPU ROI + original histogram PSO; frozen synthetic crop controls."""
from pathlib import Path
import hashlib,json,os,subprocess,sys
D=Path('research/hdr-native');W=Path(os.environ['W']);O=W/'out'
assert subprocess.check_output(['sw_vers','-buildVersion'],text=True).strip()=='26A434'
lib=Path('/System/Library/PrivateFrameworks/CMImaging.framework/Versions/A/Resources/default.metallib')
assert hashlib.sha256(lib.read_bytes()).hexdigest()=='16a8a119e3e0ae1649d32b2bbc8ea9136cb757a8d1f3eb451025821901edff11'
freeze={'os_build':'26A434','CMI_UUID':'3CCD434E-B1E0-3F14-8EF6-E29D58379BE8','source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in[D/'probe_matte_roi_s70.m',D/'histogram_probe_s55.m',D/'run_hdr_s70.py']},'photos':0,'scope':'Original wrapper ROI encoding and original PSO manual dispatch only; no camera/scene or complete inverse claim','default_matte_crops':[0,0,0,0],'main_and_linear':[1024,768],'mask':[32,24],'person_step':'x>=16','skin_step':'y>=12','threshold_from_original_AIR':.25,'predicted_normalized_bilinear_clamp_totals_before_native':{'default':[774144,774144],'person_full_matte_crop':[399360,774144],'skin_full_matte_crop':[774144,401408],'person_shifted_matte_crop':[595968,774144],'skin_shifted_matte_crop':[774144,598016],'person_logical_size_crop':[774144,774144],'skin_logical_size_crop':[774144,774144]},'model_status':'hypothesis frozen before native, not a full sampler contract','acceptance_complete':False}
(O/'freeze.json').write_text(json.dumps(freeze,separators=(',',':'))+'\n')
with(O/'build.log').open('x')as log:subprocess.run(['clang','-I',str(D),'-O2','-Wno-deprecated-declarations','-fobjc-arc','-framework','Foundation','-framework','Metal','-framework','CoreVideo','-framework','CoreGraphics',str(D/'probe_matte_roi_s70.m'),'-o',str(W/'probe')],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240)
with(O/'native.log').open('x')as log:rc=subprocess.run([str(W/'probe'),str(O/'native.json')],stdout=log,stderr=subprocess.STDOUT,timeout=420).returncode
print(json.dumps({'native_returncode':rc,'photos':0,'scope':'synthetic original ROI/PSO only','acceptance_complete':False}));sys.exit(rc)
