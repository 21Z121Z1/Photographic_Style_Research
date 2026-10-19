"""Synthetic public native probe; all heavy work stays on the macOS runner."""
from pathlib import Path
import os,subprocess,sys,json,hashlib
W=Path(os.environ['W']);O=W/'out';O.mkdir(exist_ok=True);src=Path('research/hdr-native');status=[]
assert subprocess.check_output(['sw_vers','-buildVersion'],text=True).strip()=='26A434'
def run(args,name,timeout=600,required=True):
 with (O/(name+'.log')).open('w') as log:rc=subprocess.run(list(map(str,args)),stdout=log,stderr=subprocess.STDOUT,timeout=timeout).returncode
 status.append({'operation':name,'returncode':rc});(O/'status.json').write_text(json.dumps(status,indent=2)+'\n')
 if required:assert rc==0,name
 return rc
sdk=Path(subprocess.check_output(['xcrun','--sdk','macosx','--show-sdk-path'],text=True).strip())
snippets=[]
for name in ['CIImage.h','CIContext.h','CIContext+ImageRepresentation.h']:
 p=sdk/'System/Library/Frameworks/CoreImage.framework/Headers'/name
 if not p.exists():continue
 lines=p.read_text().splitlines()
 for i,line in enumerate(lines):
  if any(x in line for x in ['imageByApplyingGainMap','HDRImage','HDRGainMap','contentHeadroom','writeHEIFRepresentation']):snippets.append({'file':name,'line':i+1,'declaration':'\n'.join(lines[max(0,i-2):min(len(lines),i+5)])})
(O/'SDK-api-snippets.json').write_text(json.dumps({'sdk':str(sdk),'matches':snippets},indent=2)+'\n')
exe=W/'hdr-s29';flags=['clang','-O2','-fobjc-arc','-framework','Foundation','-framework','CoreImage','-framework','ImageIO','-framework','Metal','-framework','CoreGraphics']
run(flags+[src/'hdr_headroom_s29.m','-o',exe],'build-s29');rc=run([exe,O/'native'],'native-s29',1200,required=False)
(O/'source-sha256.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [src/'hdr_headroom_s29.m',src/'run_hdr_s29.py']},indent=2)+'\n')
# Only our own synthetic generated carrier/pixels are written to O. Never add
# Apple binaries, raw GPU captures, or real-photo pixels to this public job.
assert rc==0,'Read native-results.json and native-s29.log before another run'
print('S29 original Core Image dual-rendition and headroom synthetic probe finished.')
