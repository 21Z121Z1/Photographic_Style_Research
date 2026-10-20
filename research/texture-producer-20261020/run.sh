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
    -framework Foundation -framework CoreImage -framework CoreVideo -framework ImageIO -framework Vision \
    -o "$TASK_OUT/inference" 2>&1 | tee "$TASK_OUT/inference-build.log"
curl --fail --location --silent --show-error \
    https://raw.githubusercontent.com/scikit-image/scikit-image/v0.25.2/skimage/data/astronaut.png \
    --output "$TASK_OUT/public-astronaut.png"
python3 - "$TASK_OUT" <<'PY'
import hashlib,json,pathlib,subprocess,sys
p=pathlib.Path(sys.argv[1]);input_path=p/'public-astronaut.png'
assert hashlib.sha256(input_path.read_bytes()).hexdigest()=='88431cd9653ccd539741b555fb0a46b61558b301d4110412b5bc28b5e3ea6cb5'
rows=[]
for mode in ['vision','fsinc']:
    with (p/(mode+'.stdout.log')).open('wb') as stdout,(p/(mode+'.stderr.log')).open('wb') as stderr:
        try:
            result=subprocess.run([str(p/'inference'),mode,str(input_path),str(p/(mode+'.json'))],stdout=stdout,stderr=stderr,timeout=180)
            status=result.returncode
        except subprocess.TimeoutExpired:status='timeout180'
    rows.append({'mode':mode,'exit':status})
(p/'inference-processes.json').write_text(json.dumps(rows,indent=2)+'\n')
PY
rm "$TASK_OUT/inference" "$TASK_OUT/public-astronaut.png"
