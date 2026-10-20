#!/usr/bin/env bash
set -euo pipefail
TASK_ROOT="$(cd "$(dirname "$0")" && pwd)"
TASK_OUT="${1:?output directory required}"
mkdir -p "$TASK_OUT"
sw_vers > "$TASK_OUT/os.txt"
xcodebuild -version > "$TASK_OUT/xcode.txt"
xcrun --sdk macosx --show-sdk-version > "$TASK_OUT/sdk.txt"
git -C "$TASK_ROOT" rev-parse HEAD > "$TASK_OUT/head.txt"
xcrun clang -g -O0 -fobjc-arc -fblocks -Wall -Wextra "$TASK_ROOT/inventory.m" \
    -framework Foundation -framework CoreImage -framework Metal \
    -o "$TASK_OUT/inventory" 2>&1 | tee "$TASK_OUT/build.log"
"$TASK_OUT/inventory" "$TASK_OUT/inventory.json" 2>&1 | tee "$TASK_OUT/inventory.log"
# LLDB observes the original methods; it does not modify Apple code or policies.
xcrun lldb --batch -s "$TASK_ROOT/disassemble.lldb" -- \
    "$TASK_OUT/inventory" "$TASK_OUT/debug-inventory.json" 2>&1 | tee "$TASK_OUT/disassembly.log"
rm "$TASK_OUT/inventory"
xcrun clang -g -O0 -fobjc-arc -fblocks -Wall -Wextra "$TASK_ROOT/inference.m" \
    -framework Foundation -framework CoreGraphics -framework CoreImage -framework CoreVideo -framework ImageIO -framework Vision \
    -o "$TASK_OUT/inference" 2>&1 | tee "$TASK_OUT/inference-build.log"
curl --fail --location --silent --show-error \
    https://raw.githubusercontent.com/scikit-image/scikit-image/v0.25.2/skimage/data/astronaut.png \
    --output "$TASK_OUT/public-astronaut.png"
python3 - "$TASK_OUT" <<'PY'
import hashlib,json,pathlib,subprocess,sys
p=pathlib.Path(sys.argv[1]);input_path=p/'public-astronaut.png'
assert hashlib.sha256(input_path.read_bytes()).hexdigest()=='88431cd9653ccd539741b555fb0a46b61558b301d4110412b5bc28b5e3ea6cb5'
rows=[]
for mode in ['vision','fsinc','VNGenerateHumanAttributesSegmentationRequest','VNGenerateFaceSegmentsRequest','VNGenerateGlassesSegmentationRequest']:
    with (p/(mode+'.stdout.log')).open('wb') as stdout,(p/(mode+'.stderr.log')).open('wb') as stderr:
        try:
            result=subprocess.run([str(p/'inference'),mode,str(input_path),str(p/(mode+'.json'))],stdout=stdout,stderr=stderr,timeout=180)
            status=result.returncode
        except subprocess.TimeoutExpired:status='timeout180'
    rows.append({'mode':mode,'exit':status})
(p/'inference-processes.json').write_text(json.dumps(rows,indent=2)+'\n')
PY
rm "$TASK_OUT/inference"
xcrun clang -g -O0 -fobjc-arc -fblocks -Wall -Wextra "$TASK_ROOT/stats_preflight.m" \
    -framework Foundation -framework Metal -framework CoreVideo \
    -o "$TASK_OUT/stats-preflight" 2>&1 | tee "$TASK_OUT/stats-build.log"
python3 - "$TASK_OUT" <<'PY'
import json,pathlib,subprocess,sys
p=pathlib.Path(sys.argv[1]);rows=[]
for name in ['CMITextureStylesMattify','CMITextureStylesUnderEyeBrighten','CMITextureStylesSkinSmoothStandalone']:
    with (p/(name+'.stdout.log')).open('wb') as stdout,(p/(name+'.stderr.log')).open('wb') as stderr:
        try:
            result=subprocess.run([str(p/'stats-preflight'),name,str(p/(name+'.json'))],stdout=stdout,stderr=stderr,timeout=120)
            status=result.returncode
        except subprocess.TimeoutExpired:status='timeout120'
    rows.append({'class':name,'exit':status})
(p/'stats-processes.json').write_text(json.dumps(rows,indent=2)+'\n')
PY
rm "$TASK_OUT/stats-preflight"
xcrun clang -g -O0 -fobjc-arc -fblocks -Wall -Wextra "$TASK_ROOT/generate_stats.m" \
    -framework Foundation -framework CoreGraphics -framework CoreImage -framework CoreVideo \
    -framework ImageIO -framework Vision -framework Metal -framework MetalKit \
    -o "$TASK_OUT/generate-stats" 2>&1 | tee "$TASK_OUT/generate-stats-build.log"
python3 - "$TASK_OUT" <<'PY'
import json,pathlib,subprocess,sys,os
p=pathlib.Path(sys.argv[1]);rows=[]
for effect,landmark_type,parameter_source,exposure in [('Mattify',1,'defaults',0),('Mattify',1,'Studio',0),('Mattify',1,'Studio',1),('Mattify',1,'Studio',-1),('UnderEyeBrighten',1,'Studio',0),('SkinSmoothStandalone',1,'Studio',0)]:
    name=effect.lower()+'-type'+str(landmark_type)+'-'+parameter_source+'-EV'+str(exposure)
    with (p/(name+'.stdout.log')).open('wb') as stdout,(p/(name+'.stderr.log')).open('wb') as stderr:
        try:
            result=subprocess.run([str(p/'generate-stats'),str(p/'public-astronaut.png'),str(p/(name+'.json')),str(landmark_type),parameter_source,str(exposure)],stdout=stdout,stderr=stderr,timeout=120,env={**os.environ,'TEXTURE_EFFECT':effect})
            status=result.returncode
        except subprocess.TimeoutExpired:status='timeout120'
    rows.append({'effect':effect,'landmark_type_control':landmark_type,'parameter_source':parameter_source,'exposure':exposure,'exit':status})
(p/'generate-stats-processes.json').write_text(json.dumps(rows,indent=2)+'\n')
if any(isinstance(row['exit'],int) and row['exit']<0 for row in rows):
    with (p/'generate-stats-debug.log').open('wb') as output:
        try:
            result=subprocess.run(['xcrun','lldb','--batch','-o','run','-k','thread backtrace all','-k','quit','--',str(p/'generate-stats'),str(p/'public-astronaut.png'),str(p/'mattify-debug.json'),'1','Studio','0'],stdout=output,stderr=subprocess.STDOUT,timeout=120)
            debug_status=result.returncode
        except subprocess.TimeoutExpired:debug_status='timeout120'
    (p/'generate-stats-debug-process.json').write_text(json.dumps({'debugger_exit':debug_status,'scope':'crash diagnosis; not successful generation'})+'\n')
PY
rm "$TASK_OUT/generate-stats"
xcrun clang -g -O0 -fobjc-arc -fblocks -Wall -Wextra "$TASK_ROOT/produce_carrier.m" \
    -framework Foundation -framework CoreGraphics -framework CoreImage -framework CoreVideo \
    -framework ImageIO -framework Vision -o "$TASK_OUT/produce-carrier" 2>&1 | tee "$TASK_OUT/carrier-build.log"
"$TASK_OUT/produce-carrier" "$TASK_OUT/public-astronaut.png" "$TASK_OUT" > "$TASK_OUT/carrier.stdout.log" 2> "$TASK_OUT/carrier.stderr.log"
python3 "$TASK_ROOT/pack_carrier.py" "$TASK_OUT" 2>&1 | tee "$TASK_OUT/carrier-assembly.log"
xcrun clang -g -O0 -fobjc-arc -fblocks -Wall -Wextra "$TASK_ROOT/native_admission.m" \
    -framework Foundation -framework CoreGraphics -framework CoreImage -framework CoreVideo \
    -framework ImageIO -framework Vision -o "$TASK_OUT/native-admission" 2>&1 | tee "$TASK_OUT/admission-build.log"
python3 - "$TASK_OUT" <<'PY'
import json,pathlib,subprocess,sys
p=pathlib.Path(sys.argv[1]);rows=[]
for f in sorted(p.glob('*.heic')):
    with (p/(f.name+'.admission.stdout.log')).open('wb') as stdout,(p/(f.name+'.admission.stderr.log')).open('wb') as stderr:
        try:
            r=subprocess.run([str(p/'native-admission'),str(f),str(p/(f.name+'.admission.json'))],stdout=stdout,stderr=stderr,timeout=120);status=r.returncode
        except subprocess.TimeoutExpired:status='timeout120'
    rows.append({'file':f.name,'exit':status})
(p/'admission-processes.json').write_text(json.dumps(rows,indent=2)+'\n')
PY
xcrun lldb --batch -s "$TASK_ROOT/person_readback.lldb" -- \
    "$TASK_OUT/native-admission" "$TASK_OUT/texture-candidate.heic" "$TASK_OUT/person-debug-admission.json" \
    2>&1 | tee "$TASK_OUT/person-metadata-readback.log"
rm "$TASK_OUT/produce-carrier" "$TASK_OUT/native-admission"
xcrun clang -g -O0 -fobjc-arc -fblocks -Wall -Wextra "$TASK_ROOT/coreml_fsinc.m" \
    -framework Foundation -framework CoreGraphics -framework CoreImage -framework CoreVideo \
    -framework ImageIO -framework Vision -framework CoreML \
    -o "$TASK_OUT/coreml-fsinc" 2>&1 | tee "$TASK_OUT/coreml-fsinc-build.log"
python3 - "$TASK_OUT" <<'PY'
import json,pathlib,subprocess,sys
p=pathlib.Path(sys.argv[1])
with (p/'coreml-fsinc.stdout.log').open('wb') as stdout,(p/'coreml-fsinc.stderr.log').open('wb') as stderr:
    try:
        result=subprocess.run([str(p/'coreml-fsinc'),str(p/'public-astronaut.png'),str(p/'coreml-fsinc.json')],stdout=stdout,stderr=stderr,timeout=180)
        status=result.returncode
    except subprocess.TimeoutExpired:status='timeout180'
(p/'coreml-fsinc-process.json').write_text(json.dumps({'exit':status})+'\n')
PY
rm "$TASK_OUT/coreml-fsinc" "$TASK_OUT/public-astronaut.png"
