from pathlib import Path
import hashlib,json,os,subprocess,sys
D=Path('research/hdr-native');W=Path(os.environ['W']);O=W/'out'
assert subprocess.check_output(['sw_vers','-buildVersion'],text=True).strip()=='26A434'
lib=Path('/System/Library/PrivateFrameworks/CMImaging.framework/Versions/A/Resources/default.metallib');assert hashlib.sha256(lib.read_bytes()).hexdigest()=='16a8a119e3e0ae1649d32b2bbc8ea9136cb757a8d1f3eb451025821901edff11'
freeze={'os_build':'26A434','image_version':os.environ.get('ImageVersion'),'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in[D/'probe_bindings_s68.m',D/'probe_headroom_s66.m',D/'run_hdr_s68.py']},'photos':0,'image_dispatches':0,'scope':'Original CPU pixel-buffer coordinate binding and original PSO limits; helper sizes are style-engine intermediates, not a production statistics size claim','original_source_scope':'Same UUID/build; VM residency sets override only','processing_type_for_PSO_metadata':1,'synthetic_main_sizes':[[1024,768],[5712,4284]],'linear_size':[1024,768],'ordinary_thumb_size':[512,384],'mask_size':[32,24],'camera_identity_proven':False,'acceptance_complete':False}
(O/'freeze.json').write_text(json.dumps(freeze,separators=(',',':'))+'\n')
with(O/'build.log').open('x')as f:subprocess.run(['clang','-I',str(D),'-O2','-Wno-deprecated-declarations','-fobjc-arc','-framework','Foundation','-framework','Metal','-framework','CoreVideo','-framework','CoreGraphics',str(D/'probe_bindings_s68.m'),'-o',str(W/'probe')],stdout=f,stderr=subprocess.STDOUT,check=True,timeout=240)
with(O/'native.log').open('x')as f:rc=subprocess.run([str(W/'probe'),str(O/'native.json')],stdout=f,stderr=subprocess.STDOUT,timeout=300).returncode
print(json.dumps({'returncode':rc,'photos':0,'image_dispatches':0,'acceptance_complete':False}));sys.exit(rc)
