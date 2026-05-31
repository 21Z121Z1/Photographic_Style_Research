# Linearthumbnail / Gain Map / RAW Reconstruction Notes - 2026-05-31

## What Changed

`apple_style_injected_from_preview_heic_v1.heic` was confirmed by the user to activate Photographic Styles in Photos, but its linearthumbnail used the q=0.25 VideoToolbox payload inherited from v8 and showed visible compression artifacts.

This pass keeps the proven activation graph unchanged and introduces two additions:

- `tools/inject_style_family.py --replace-linearthumb-hevc` replaces only the injected linearthumbnail item payload plus its `hvcC`.
- `tools/gainmap_sources.py` and new `tools/aux_generator.py` modes generate experimental linearthumbnail/styledeltamap rasters from RGB gain maps, mono gain maps, MPF previews, combined DNG previews, and DNG/JPG pairs.

## Better Activating Candidate

New artifact:

`artifacts/constructed/apple_style_injected_from_preview_heic_v2_q045/apple_style_injected_from_preview_heic_v2_q045.heic`

Build steps:

```bash
swift -module-cache-path /private/tmp/styledeltamap-swift-module-cache \
  tools/apple_vt_hevc_encoder.swift \
  artifacts/constructed/apple_parity_styledeltamap_v8_vt_linearthumb_q025/linearthumbnail_input.png \
  artifacts/constructed/apple_style_injected_from_preview_heic_v2_q045/linearthumbnail_vt_q045.hevc \
  0.45

/Users/retriedstormtrooper/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
  tools/inject_style_family.py \
  --preview-jpeg "/Users/retriedstormtrooper/Downloads/03_图片素材/RAW_DNG照片/RAW_DNG_JPEG_批量导出/IMG_0342_preview.jpg" \
  --make-base-with-sips \
  --base-size 4032x3024 \
  --style-donor artifacts/constructed/apple_parity_styledeltamap_v8_vt_linearthumb_q025/apple_parity_styledeltamap_v8_vt_linearthumb_q025.heic \
  --template Apple_Native_Samples/IMG_0032.HEIC \
  --replace-linearthumb-hevc artifacts/constructed/apple_style_injected_from_preview_heic_v2_q045/linearthumbnail_vt_q045.hevc \
  --output artifacts/constructed/apple_style_injected_from_preview_heic_v2_q045/apple_style_injected_from_preview_heic_v2_q045.heic
```

Validation:

- item 97 remains `hvc1`.
- item 97 `auxC = tag:apple.com,2023:photo:aux:linearthumbnail`.
- item 97 `auxl -> [49, 99]`.
- item 97 `hvcC` remains 105 bytes, Main10, bit depth 10.
- item 97 payload is 22,925 bytes, with one HEVC NAL type `[20]`.
- `tools/semantic_fitter.py` reports `hard_warnings: []`.
- `heif-convert --with-aux` extracts styledeltamap, hdrgainmap, semantic sky matte, and linearthumbnail.
- `heif-info` exits 0 and recognizes the primary image and Apple style metadata. It prints the same non-fatal `error reading brands: insufficient input data` warning seen on v1, so this is not a v2 regression.

## Supported Diagnostic Inputs

`tools/aux_generator.py inspect-gainmap` now supports:

- OPPO/OnePlus UHDR HEIC: `local.uhdr.gainmap.info` + `local.uhdr.gainmap.data`, decoded as RGB gain map.
- OPPO/OnePlus LHDR HEIC: `local.hdr.meta.data` + `local.hdr.linear.mask`, decoded as mono mask.
- MPF JPEG: second embedded JPEG as RGB gain map.
- Combined OPPO DNG: `PreviewImage` extracted by `exiftool`, then MPF gain map decoded from that preview.
- Plain RGB or mono image gain maps.

RGB PQ gain-map rasters are accepted as RGB image inputs. If OPPO UHDR metadata is present, the tool uses the per-channel ratio/gamma fields. If no metadata is present, the raster is treated as a neutral-centered RGB residual diagnostic rather than a standards-accurate PQ reconstruction.

`tools/aux_generator.py linearthumbnail-dng` supports DNG/JPG pairs through macOS `sips` DNG rendering.

## Reconstruction Commands

UHDR RGB gain map:

```bash
python3 tools/aux_generator.py inspect-gainmap /Users/retriedstormtrooper/Documents/proxdrtest/test-samples/uhdr/IMG20260424200116.heic \
  --json artifacts/research/linearthumbnail_gainmap_raw_20260531/uhdr/gainmap_inspect.json \
  --preview-output artifacts/research/linearthumbnail_gainmap_raw_20260531/uhdr/gainmap.png

python3 tools/aux_generator.py linearthumbnail-gainmap /Users/retriedstormtrooper/Documents/proxdrtest/test-samples/uhdr/IMG20260424200116.heic \
  /Users/retriedstormtrooper/Documents/proxdrtest/test-samples/uhdr/IMG20260424200116.heic \
  --output artifacts/research/linearthumbnail_gainmap_raw_20260531/uhdr/linearthumbnail_from_gainmap.png \
  --json artifacts/research/linearthumbnail_gainmap_raw_20260531/uhdr/linearthumbnail_from_gainmap.json
```

LHDR mono gain map:

```bash
python3 tools/aux_generator.py linearthumbnail-gainmap /Users/retriedstormtrooper/Documents/proxdrtest/test-samples/lhdr/IMG20240725150658.heic \
  /Users/retriedstormtrooper/Documents/proxdrtest/test-samples/lhdr/IMG20240725150658.heic \
  --output artifacts/research/linearthumbnail_gainmap_raw_20260531/lhdr/linearthumbnail_from_gainmap.png \
  --json artifacts/research/linearthumbnail_gainmap_raw_20260531/lhdr/linearthumbnail_from_gainmap.json
```

Combined OPPO DNG:

```bash
python3 tools/aux_generator.py linearthumbnail-gainmap "/Users/retriedstormtrooper/Documents/OPPO 互联/combine dng/IMG20260530190200.dng" \
  "/Users/retriedstormtrooper/Documents/OPPO 互联/combine dng/IMG20260530190200.dng" \
  --output artifacts/research/linearthumbnail_gainmap_raw_20260531/combine_dng/linearthumbnail_from_dng_gainmap.png \
  --json artifacts/research/linearthumbnail_gainmap_raw_20260531/combine_dng/linearthumbnail_from_dng_gainmap.json
```

DNG/JPG pair:

```bash
python3 tools/aux_generator.py linearthumbnail-dng "/Users/retriedstormtrooper/Downloads/IDG_20260531_131302_390 2/IMG_2972.DNG" \
  --preview "/Users/retriedstormtrooper/Downloads/IDG_20260531_131302_390 2/IMG_2973.JPG" \
  --output artifacts/research/linearthumbnail_gainmap_raw_20260531/raw_pair/IMG_2972_linearthumbnail_from_dng.png \
  --json artifacts/research/linearthumbnail_gainmap_raw_20260531/raw_pair/IMG_2972_linearthumbnail_from_dng.json
```

## Real-Sample Diagnostics

Artifacts were generated under:

`artifacts/research/linearthumbnail_gainmap_raw_20260531/`

Observed stats:

- UHDR RGB gain map: mode `oppo-uhdr-rgb`, gain map `2298x3060`, linearthumbnail output `769x1024`, 10-bit mean `492.48`, std `132.52`, max `730`.
- LHDR mono gain map: mode `oppo-lhdr-mono`, gain map `1536x2048`, linearthumbnail output `768x1024`, 10-bit mean `495.66`, std `128.65`.
- Combined OPPO DNG: mode `dng-preview-mpf-rgb`, gain map `2710x2032`, linearthumbnail output `1024x768`, 10-bit mean `492.16`, std `143.49`.
- `/Downloads/IDG_20260531_131302_390 2/IMG_2972.DNG` + `IMG_2973.JPG`: DNG linearthumbnail output `1024x768`, 10-bit mean `499.66`, std `142.15`.
- ProRAW pair `IMG_0342_converted.DNG` + `IMG_0342_preview.jpg`: DNG linearthumbnail output `1024x768`, 10-bit mean `505.56`, std `126.20`.

All generated linearthumbnails stay inside the Apple-like narrow 10-bit band `[270, 730]`.

## Interpretation

For linearthumbnail, the high-confidence part is structural and encoding-related: the q=0.45 replacement preserves Photos-activating graph shape and Apple-like HEVC data type while increasing payload size from the q=0.25 range to 22.9 KB. That is the right fix for the visible linearthumbnail compression artifacts.

For gain-map and RAW reconstruction, confidence is intentionally lower. RGB gain maps are useful because they preserve per-channel HDR recovery and can produce low-amplitude color residual candidates for styledeltamap. Mono gain maps are simpler and can recover luma/headroom, but they do not contain real chroma residuals; the mono styledeltamap path therefore uses only neutral-centered luma residual plus small ordered dithering.

These formulas are diagnostic hypotheses, not proven Apple private styledeltamap formulas. The next Photos-facing test should replace item 97 with a gain-map- or RAW-derived high-quality linearthumbnail first, then test styledeltamap replacement separately so activation and rendering effects stay isolated.

## Verification

Commands run:

```bash
/Users/retriedstormtrooper/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.test_gainmap_sources tests.test_aux_generator
/Users/retriedstormtrooper/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.test_style_family_injector
/Users/retriedstormtrooper/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest discover -s tests -p 'test_*.py'
/Users/retriedstormtrooper/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m pytest -q
/Users/retriedstormtrooper/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m compileall tools tests
git diff --check
```

Results:

- `tests.test_gainmap_sources tests.test_aux_generator`: 23 tests OK.
- `tests.test_style_family_injector`: 3 tests OK.
- full unittest discover: 88 tests OK, 1 skipped.
- full pytest: 87 passed, 1 skipped.
- `compileall`: OK.
- `git diff --check`: OK.
