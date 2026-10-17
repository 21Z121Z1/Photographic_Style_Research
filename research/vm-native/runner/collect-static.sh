#!/bin/bash
set -uo pipefail
OUT="$1"
mkdir -p "$OUT/static" "$OUT/resources"
CACHE=/System/Volumes/Preboot/Cryptexes/OS/System/Library/dyld/dyld_shared_cache_arm64e
if [ ! -f "$CACHE" ]; then
  printf 'Requested cache missing\n' > "$OUT/static/cache-error.txt"
  ls /System/Library/dyld/ > "$OUT/static/cache-locations.txt" 2>&1
  exit 0
fi
ipsw version > "$OUT/static/ipsw-version.txt" 2>&1
ipsw dyld info "$CACHE" > "$OUT/static/cache-info.txt" 2>&1
STAGE="$RUNNER_TEMP/style-static-binaries"
mkdir -p "$STAGE"
for FRAME in CMImaging PhotoImaging NeutrinoCore CoreImage; do
  case "$FRAME" in
    CoreImage) PATH_IN_CACHE=/System/Library/Frameworks/CoreImage.framework/Versions/A/CoreImage ;;
    *) PATH_IN_CACHE="/System/Library/PrivateFrameworks/$FRAME.framework/Versions/A/$FRAME" ;;
  esac
  ipsw dyld macho "$CACHE" "$PATH_IN_CACHE" --loads --symbols --objc --strings > "$OUT/static/$FRAME.metadata.txt" 2> "$OUT/static/$FRAME.metadata.stderr.txt"
  printf '%s metadata rc=%s\n' "$FRAME" "$?"
  ipsw dyld extract "$CACHE" "$PATH_IN_CACHE" --slide --objc --output "$STAGE/$FRAME" > "$OUT/static/$FRAME.extract-log.txt" 2>&1
  FIND_BIN=$(find "$STAGE/$FRAME" -type f -name "$FRAME" -print -quit)
  if [ -n "$FIND_BIN" ]; then
    shasum -a 256 "$FIND_BIN" > "$OUT/static/$FRAME.sha256"
    dwarfdump --uuid "$FIND_BIN" > "$OUT/static/$FRAME.uuid.txt" 2>&1
    # Only text exits this ephemeral runner; no Apple Mach-O is uploaded.
    otool -tvV "$FIND_BIN" > "$OUT/static/$FRAME.disasm.txt" 2> "$OUT/static/$FRAME.disasm.stderr.txt"
  fi
  R="/System/Library/PrivateFrameworks/$FRAME.framework/Versions/A/Resources"
  if [ "$FRAME" = CoreImage ]; then R=/System/Library/Frameworks/CoreImage.framework/Versions/A/Resources; fi
  if [ -d "$R" ]; then
    find "$R" -type f > "$OUT/resources/$FRAME.inventory.txt"
    while IFS= read -r p; do
      relative="${p#"$R"/}"; safe=$(printf '%s' "$relative" | tr '/' '_')
      plutil -convert xml1 -o "$OUT/resources/$FRAME.$safe.xml" "$p" 2>/dev/null
    done < <(find "$R" -type f -name '*.plist')
    while IFS= read -r p; do
      relative="${p#"$R"/}"; safe=$(printf '%s' "$relative" | tr '/' '_')
      shasum -a 256 "$p" >> "$OUT/resources/metallib.sha256"
      xcrun metal-objdump --build-table=module "$p" > "$OUT/resources/$FRAME.$safe.build-table.txt" 2>&1
      xcrun metal-nm "$p" > "$OUT/resources/$FRAME.$safe.nm.txt" 2>&1
      xcrun metal-objdump -d --demangle "$p" > "$OUT/resources/$FRAME.$safe.disasm.txt" 2>&1
      strings -a "$p" > "$OUT/resources/$FRAME.$safe.strings.txt"
    done < <(find "$R" -maxdepth 3 -type f -name '*.metallib')
  fi
  du -sh "$OUT/static/$FRAME"* 2>/dev/null
  rm -rf "$STAGE/$FRAME"
done
xcrun metal-objdump --help > "$OUT/resources/metal-objdump-help.txt" 2>&1
