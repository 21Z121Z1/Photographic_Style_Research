# Linearthumbnail Gainmap And Raw Reconstruction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the Photos-activating direct-injection output's overcompressed `linearthumbnail`, then add experimental tools that reconstruct better `linearthumbnail` and candidate `styledeltamap` rasters from HDR gain maps and paired RAW/JPEG sources.

**Architecture:** Keep the proven style activation graph unchanged. Only replace item 97 with a higher-quality Apple VideoToolbox Main10 single-IDR payload for the production candidate. Add a separate diagnostic/generation layer that can ingest preview JPEG, MPF gain map, OPPO UHDR/LHDR HEIC private gain-map data, and DNG/JPG pairs without claiming those formulas are Apple-equivalent.

**Tech Stack:** Python 3.13, Pillow, NumPy, macOS `sips`, Apple VideoToolbox Swift helper, existing HEIF parser/writer, proxdrtest private LHDR/UHDR parsing layout, Android Ultra HDR gain-map formula as public reference.

---

## Current Evidence

- `apple_style_injected_from_preview_heic_v1.heic` activates Apple Photos style controls.
- v1 uses the q=0.25 VideoToolbox linearthumbnail inherited from v8.
- q=0.25 produces a single-IDR payload around 6.6 KB. It is Apple-native scale but visibly overcompressed.
- Prior measurements show q=0.45 produces a single-IDR payload around 22.9 KB, still within the observed native linearthumbnail payload range of 4485 to 70948 bytes.
- Android Ultra HDR documentation defines the gain-map relationship in log space: gain map metadata gives `GainMapMin`, `GainMapMax`, `Gamma`, offsets, and display capacities; RGB metadata can be per-channel, while grayscale applies one recovery map to all channels.
- proxdrtest already extracts OPPO UHDR as 20 float32 metadata plus JPEG gain map bytes, and LHDR as 36 float32 metadata plus a local HDR linear mask JPEG.

## Safety Boundary

Do not change the proven activation graph unless a test requires it. This turn should:

- preserve direct injection item graph shape;
- preserve base primary payload from generated Apple HEIC;
- preserve `auxl`/`dimg`/`cdsc` semantics;
- replace only the linearthumbnail payload and matching `hvcC` in the donor or direct-injected output;
- treat gain-map/raw reconstruction as experimental diagnostics unless Photos validation proves behavior.

## Files

- Modify: `tools/aux_generator.py`
  - Add gain-map and raw-based reconstruction helpers.
  - Add CLI subcommands for linearthumbnail/styledeltamap generation from gain maps and DNG/JPG pairs.
- Create: `tools/gainmap_sources.py`
  - Extract MPF gain maps from JPEG.
  - Extract OPPO UHDR RGB gain maps and LHDR mono masks from HEIC using local logic compatible with proxdrtest.
  - Convert gain maps and metadata to normalized arrays.
- Modify: `tools/inject_style_family.py`
  - Add `--replace-linearthumb-image` and `--replace-linearthumb-hevc` options so direct injection can cherry-pick only item 97 without rebuilding a whole donor.
- Modify: `tools/apple_template_writer.py`
  - Keep VideoToolbox quality explicit in build summaries and docs.
- Add tests: `tests/test_gainmap_sources.py`, extend `tests/test_style_family_injector.py`, extend `tests/test_aux_generator.py`.
- Add docs: `docs/linearthumbnail_gainmap_raw_reconstruction_2026-05-31.md`.

## Task 1: Fix Production Linearthumbnail Compression

- [x] Generate a q=0.45 VideoToolbox linearthumbnail from the same preview source.
- [x] Build `apple_style_injected_from_preview_heic_v2_q045.heic` by injecting the same style family into the same base while replacing only item 97 payload and `hvcC`.
- [x] Validate:
  - item 97 remains `hvc1`, 105-byte Main10 `hvcC`, single NAL type `[20]`;
  - item 97 payload is in native corpus range;
  - `semantic_fitter` hard warnings are zero;
  - `heif-info` and `heif-convert --with-aux` pass.

## Task 2: Gain Map Source Extraction

- [x] Implement `extract_mpf_gainmap(jpeg_path)` for Apple/Android HDR preview JPEGs.
- [x] Implement `extract_oppo_private_gainmap(heic_path)` for:
  - UHDR: `local.uhdr.gainmap.info` + `local.uhdr.gainmap.data`;
  - LHDR: `local.hdr.meta.data` + `local.hdr.linear.mask`.
- [x] Preserve gain-map channel count:
  - RGB UHDR stays RGB;
  - mono LHDR stays L;
  - RGB PQ or 4:4:4 JPEG decodes to RGB.
- [x] Report metadata floats and inferred mode in JSON.

## Task 3: Reconstruct Linearthumbnail From Gain Map

- [x] Implement a reference gain-map render function:
  - decode base SDR to float;
  - decode gain map to recovery values;
  - if metadata is present, apply log-space gain formula at full weight;
  - for RGB gain maps, apply per-channel gain; for mono, apply shared luma gain;
  - compress the recovered HDR-ish image into Apple linearthumbnail's narrow 10-bit range using robust percentiles.
- [x] Add optional high-frequency blend:
  - use base image chroma/detail to avoid gain-map blockiness;
  - keep output stats in Apple linearthumbnail band.
- [x] Add tests using synthetic RGB and mono gain maps to prove shape, channel behavior, and bounded output.

## Task 4: Candidate Styledeltamap From Gain Map

- [x] Implement experimental `styledeltamap_from_gainmap`:
  - RGB gain map: compute per-channel log gain residual, robustly center around neutral 128, clamp low amplitude;
  - mono gain map: use luma residual plus low-amplitude ordered dithering to avoid large flat blocks;
  - raw/JPG pair: keep existing DNG residual path but output diagnostics that compare correlation and amplitude to Apple samples.
- [x] Keep this output explicitly experimental in JSON/docs.

## Task 5: Support User-Specified Inputs

Input forms to exercise:

- `/Users/retriedstormtrooper/Documents/proxdrtest/test-samples/uhdr/*.heic` RGB gain map.
- `/Users/retriedstormtrooper/Documents/proxdrtest/test-samples/lhdr/*.heic` mono gain map.
- `/Users/retriedstormtrooper/Downloads/03_图片素材/RAW_DNG照片/RAW_DNG_JPEG_批量导出/*_converted.DNG` + `*_preview.jpg`.
- `/Users/retriedstormtrooper/Downloads/IDG_20260531_131302_390 2/IMG_2972.DNG` + `IMG_2973.JPG`.
- `/Users/retriedstormtrooper/Documents/OPPO 互联/combine dng/*.dng` samples; decode with `sips` and extract embedded preview/gain-map data where present.

## Task 6: Tests And Commit

- [x] Run targeted tests.
- [x] Run full test suite.
- [x] Run `compileall`.
- [x] Run `git diff --check`.
- [x] Generate docs and artifacts.
- [x] Commit the resulting code/docs to the current git repository after validation.

## Completion Standard

This goal is complete for this turn only if:

- v2 q=0.45 direct-injection artifact still passes structural/external decoders;
- item 97 uses better quality while retaining Apple-compatible data type;
- gain-map/raw reconstruction tools support all requested input families at least as diagnostics;
- all current tests pass;
- docs explain which formulas are proven, which are experimental, and how to run the tools;
- changes are committed.
