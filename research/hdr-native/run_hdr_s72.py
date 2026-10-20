"""Bind original PhotoImaging consumer callsites; CPU text evidence only."""
from pathlib import Path
import hashlib,json,os,subprocess,sys
D=Path('research/hdr-native');W=Path(os.environ['W']);O=W/'out'
assert subprocess.check_output(['sw_vers','-buildVersion'],text=True).strip()=='26A434'
with (O/'freeze.json').open('x')as f:json.dump({'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in[D/'probe_consumer_bindings_s72.m',D/'probe_headroom_s66.m',D/'run_hdr_s72.py']},'scope':'Original consumer CPU stubs, literals and runtime method ABIs, no image dispatch or production-domain inference','PhotoImaging_UUID':'5F17E1DB-A15E-38C7-9BEC-E081688B62E5','PhotoImaging_archived_binary_sha256':'c72d3ef8d551998ae7b9468ad339a913b6db7ec2388e810357c86252b65246e1','CMImaging_UUID':'3CCD434E-B1E0-3F14-8EF6-E29D58379BE8','photos':0,'image_dispatches':0,'acceptance_complete':False},f,separators=(',',':'));f.write('\n')
with (O/'build.log').open('x')as log:subprocess.run(['clang','-I',str(D),'-O2','-fobjc-arc','-framework','Foundation','-framework','CoreFoundation',str(D/'probe_consumer_bindings_s72.m'),'-o',str(W/'probe')],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240)
with (O/'native.log').open('x')as log:rc=subprocess.run([str(W/'probe'),str(O/'native.json')],stdout=log,stderr=subprocess.STDOUT,timeout=180).returncode
print(json.dumps({'returncode':rc,'photos':0,'image_dispatches':0,'acceptance_complete':False}));sys.exit(rc)
