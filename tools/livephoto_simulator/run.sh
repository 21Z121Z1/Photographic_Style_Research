#!/bin/bash
set -euo pipefail
mkdir -p probe-results
sw_vers | tee probe-results/host.txt
uname -a | tee -a probe-results/host.txt
ls -d /Applications/Xcode*.app | tee probe-results/xcodes.txt
xcodebuild -version | tee -a probe-results/host.txt
xcrun simctl list runtimes -j > probe-results/runtimes.json
xcrun simctl list devices available -j > probe-results/devices.json
python3 - <<'PY'
import json,os,re
r=json.load(open('probe-results/runtimes.json'))['runtimes']
r=sorted([x for x in r if x.get('isAvailable') and 'iOS' in x.get('name','')],key=lambda x:tuple(map(int,re.findall(r'\d+',x['version']))),reverse=True)
if not r: raise SystemExit('No installed available iOS Simulator runtime; no eligibility result.')
r=r[0]
d=json.load(open('probe-results/devices.json'))['devices'].get(r['identifier'],[])
d=next((x for x in d if x.get('isAvailable') and x['name'].startswith('iPhone')),None)
if not d: raise SystemExit('No matching available iPhone simulator device.')
json.dump({'runtime':r,'device':d},open('probe-results/selected.json','w'),indent=2)
with open(os.environ['GITHUB_ENV'],'a') as f:f.write('SIM_UDID='+d['udid']+'\n')
print('SELECTED',r['name'],r['version'],d['name'],d['udid'])
PY
UDID=$(python3 -c 'import json;print(json.load(open("probe-results/selected.json"))["device"]["udid"])')
SDK=$(xcrun --sdk iphonesimulator --show-sdk-path)
ARCH=$(uname -m)
xcrun --sdk iphonesimulator clang -target "${ARCH}-apple-ios18.0-simulator" -isysroot "$SDK" -fobjc-arc -Wno-deprecated-declarations tools/livephoto_simulator/probe.m -o probe-results/livephoto-probe -framework Foundation -framework AVFoundation -framework Metal
codesign --force --sign - probe-results/livephoto-probe
xcrun simctl boot "$UDID" || true
python3 - "$UDID" <<'PY'
import subprocess,sys
subprocess.run(['xcrun','simctl','bootstatus',sys.argv[1],'-b'],check=True,timeout=240)
PY
xcrun simctl listapps "$UDID" > probe-results/simulator-apps.plist
python3 - "$UDID" <<'PY'
import subprocess,sys,os,json
cmd=['xcrun','simctl','spawn',sys.argv[1],os.path.abspath('probe-results/livephoto-probe')]
with open('probe-results/runtime.jsonl','w') as out,open('probe-results/runtime-stderr.txt','w') as err:
    try:r=subprocess.run(cmd,stdout=out,stderr=err,timeout=120);code=r.returncode
    except subprocess.TimeoutExpired:code=124
json.dump({'exit_code':code},open('probe-results/process-status.json','w'))
print('PROBE_EXIT_CODE',code)
if code: print('Probe process did not finish successfully. Partial output is diagnostic only.')
PY
cat probe-results/runtime.jsonl
cat probe-results/runtime-stderr.txt
python3 - <<'PY'
import json,os
rows=[]
for line in open('probe-results/runtime.jsonl'):
    try:rows.append(json.loads(line))
    except ValueError:pass
sel=json.load(open('probe-results/selected.json'))
s=['# Live Photo Simulator capability probe','', 'Runtime: '+sel['runtime']['name'],'', '| Framework | Loaded |','| --- | --- |']
for r in rows:
    if r.get('kind')=='framework':s.append('| '+r['name']+' | '+str(r['loaded'])+' |')
s+=['','## Gate classes']
for r in rows:
    if r.get('kind')=='class':s.append('- '+r['name']+': '+('present' if r['present'] else 'absent'))
s+=['','No media was uploaded or tested. Framework/class presence alone does not establish wallpaper eligibility. Simulator results are not a substitute for a positive and negative control on the target physical iOS version.']
text='\n'.join(s)+'\n'
open('probe-results/summary.md','w').write(text)
with open(os.environ['GITHUB_STEP_SUMMARY'],'a') as f:f.write(text)
PY
