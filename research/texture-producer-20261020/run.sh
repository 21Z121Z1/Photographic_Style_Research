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
