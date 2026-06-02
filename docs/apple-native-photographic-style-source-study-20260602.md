# Apple Native Photographic Style Source Study - 2026-06-02

## Scope and Artifacts

This pass studied the local native corpus:

`/Users/retriedstormtrooper/Documents/styledeltamap/Apple_Native_Samples`

Generated evidence lives under:

`artifacts/apple_native_samples/20260602_native_source_study/`

Key outputs:

- `inventory.json`: machine-readable per-sample source of truth.
- `inventory.md`: human sample matrix.
- `sample_matrix.csv`: spreadsheet-ready sample matrix.
- `samples/<sample>/<sample>.heif_dump.json`: full parser dump for each HEIC sample.
- `styledeltamap_stats.json`, `linearthumbnail_stats.json`, `aux_stats.json`, `metadata_summary.json`, `item_graph_summary.json`, `unknown_items.json`, `structure_diff.json`.
- `samples/<sample>/decoded_aux/*.png`: decoded aux previews from `heif-convert --with-aux`.

Important measurement boundary: item ids, references, `pixi`, dimensions, payload sizes, and payload hashes are exact parser evidence. Decoded PNG statistics are diagnostic views, not raw 10-bit HEVC proof; large decoded rasters use bounded metric images for speed, and `inventory.json` marks `metrics_downsampled`.

## Corpus Summary

- 85 HEIC files were found and dumped successfully.
- 84 files contain the Photographic Styles family: `styledeltamap`, `linearthumbnail`, style metadata URI plist, `tmap`, HDR gain map, semantic sky matte, EXIF, MakerApple, and MakerNote.
- `IMG_2911.HEIC` is the only outlier: it has primary image, HDR gain map, `tmap`, EXIF, MakerApple, and MakerNote, but no `styledeltamap`, no `linearthumbnail`, no style metadata URI item, and no semantic sky matte.
- No duplicate SHA-256 files were found in `Apple_Native_Samples`.
- After classifying ordinary `thmb` items as known thumbnails, no unexplained HEIF items remain in this parser pass.

Reference exact examples:

| Sample | SHA-256 | Primary | styledeltamap | linearthumbnail | HDR gain map | Style metadata |
|---|---|---|---|---|---|---|
| `IMG_0032.HEIC` | `76a2fa2723e5a241...ef6501a` | item 49, 4032x3024 | item 81, 2880x2160, payload `926985e292478ecd...`, 33,141 B | item 97, 1024x768, payload `72c4661edf3d0932...`, 5,819 B | item 94, 2016x1512 | item 101, 57,550 B |
| `IMG_2878.HEIC` | `bb16f7f1b9a4727e...d067169a` | item 55, 8064x6048 | item 130, 5760x4320, payload `539a984a4f00b857...`, 357,045 B | item 79, 1024x768, payload `5c8fa75ef3ff1e48...`, 11,449 B | item 72, 4032x3024 | item 82, 57,991 B |
| `IMG_2889.HEIC` | `bf4dc0d800789221...5c9efe9` | item 46, 5712x4284 | item 129, 4096x3072, payload `0c1fb6a3b41878a5...`, 389,590 B | item 48, 1024x768, payload `b65d61733962b305...`, 7,839 B | item 64, 2856x2142 | item 78, 57,984 B |
| `IMG_2911.HEIC` | `724e5e278b35cdfb...068be6b` | item 50, 4284x5712 | missing | missing | item 64, 2142x2856 | missing |

## HEIF Graph Findings

Across all 85 samples, top-level boxes are `ftyp`, `meta`, and `mdat`. Every `meta` includes `hdlr`, `dinf`, `pitm`, `iinf`, `iref`, `iprp`, `grpl`, `idat`, and `iloc`.

Reference types observed:

- `cdsc`: 721 references.
- `auxl`: 673 references.
- `dimg`: 339 references.
- `thmb`: 84 references.

Property types observed:

- `ispe`: 695.
- `auxC`: 673.
- `hvcC`: 594.
- `colr`: 445.
- `pixi`: 255.
- `irot`: 139.
- `clli`: 1.
- `clap`: 1.

No `altr` reference was observed by the current parser. `grpl` boxes are present in all files, but this pass does not parse their payload.

## styledeltamap

**Evidence grade: confirmed structural source; strong candidate control surface; exact Photos formula unknown.**

84/85 samples contain `auxC = tag:apple.com,2023:photo:aux:styledeltamap`.

All style-map role items are `grid` items with `pixi = [10, 10, 10]`. The HEVC payload lives in `dimg` child tiles. Child examples:

- `IMG_0032`: item 81 has 30 children; first child `hvcC` is Main10, level 90, 4:2:0, 10-bit.
- `IMG_2878`: item 130 has 45 children; first child `hvcC` is Main10, level 93, 4:2:0, 10-bit.
- `IMG_2889`: item 129 has 48 children; first child `hvcC` is profile idc 4, 4:4:4, 10-bit.

Grid sizes:

| styledeltamap size | Count |
|---|---:|
| 4096x3072 | 35 |
| 2880x2160 | 30 |
| 5760x4320 | 11 |
| 3520x2640 | 4 |
| 2640x3520 | 2 |
| 2240x1680 | 1 |
| 1680x2240 | 1 |

Exact compressed/derived payload range over 84 style samples:

- Min: 32,654 B.
- Median: 241,506.5 B.
- Max: 1,400,355 B.
- Mean: 337,546.92 B.

Decoded diagnostic metrics over 84 samples:

- Mean channel values: min 123.239882, median 127.525807, max 129.028307.
- Standard deviation: min 0.273390, median 0.515556, max 24.172768.
- Neutral absolute mean offset from 128: min 0.080414, median 0.513427, max 14.047646.
- Base-luma correlation: min -0.411840, median -0.190821, max 0.192750.
- Low-frequency energy ratio: min 0.304915, median 0.776358, max 0.985656.
- No decoded style map is a pure constant in this corpus.

Interpretation: most style maps are near-neutral numerically, but not information-free. Some samples (`IMG_2881`, `IMG_2887`, `IMG_2889`) show much higher decoded variance while still being low-frequency. The style map is therefore closer to a low-amplitude residual/control surface than a normal visible image or a pure semantic matte.

## linearthumbnail

**Evidence grade: confirmed structural source; strongly spatial; not sufficient as sole source.**

84/85 samples contain `auxC = tag:apple.com,2023:photo:aux:linearthumbnail`. The same outlier, `IMG_2911`, lacks it.

All linearthumbnail items are `hvc1` with `pixi = [10, 10, 10]` and a 105-byte Main10 `hvcC` record: profile idc 2, level idc 93, 4:2:0, 10-bit luma/chroma.

Sizes:

- 81 samples: 1024x768.
- 3 samples: 768x1024.

Exact payload range:

- Min: 4,485 B.
- Median: 18,473.5 B.
- Max: 70,948 B.
- Mean: 21,504.11 B.

Decoded diagnostic metrics:

- Base-luma correlation: min 0.899919, median 0.975202, max 0.997585.
- Low-frequency energy ratio: min 0.958949, median 0.994409, max 0.999191.
- Mean channel values: min 72.162350, median 113.868877, max 158.495825.
- Standard deviation: min 14.094756, median 27.322555, max 49.678225.

Interpretation: linearthumbnail is a real spatial image source and tracks the base image strongly. It can plausibly drive a large part of Photos tone/color spatial response. It should not be treated as the only source because every style sample also carries a style metadata plist, MakerApple/MakerNote, base image, HDR gain map, `tmap`, and `styledeltamap`; the friend's neutralized-linearthumbnail observation is consistent with these remaining sources.

## Base, HDR Gain Map, and tmap

**Evidence grade: strong support as remaining spatial candidates; Photos role unproven.**

Every sample has an HDR gain map and `tmap`, including the non-style outlier `IMG_2911`. HDR gain map alone is therefore not a Photographic Styles signature, but it remains a strong spatial source.

HDR gain map exact payload range:

- Min: 22,709 B.
- Median: 116,411 B.
- Max: 591,243 B.
- Mean: 147,362.12 B.

Decoded HDR gain map metrics:

- Base-luma correlation: min 0.566433, median 0.898591, max 0.982394.
- Low-frequency energy ratio: median 0.994698.

The style graph does not always bind `styledeltamap` to `tmap`: 60 style samples have `styledeltamap auxl -> [primary, tmap]`, while 24 have `styledeltamap auxl -> [primary]`. By contrast, all 84 linearthumbnail, sky matte, style metadata, and EXIF role items reference or describe `[primary, tmap]` through `auxl` or `cdsc`.

Interpretation: `tmap` is part of the native style file family, but a direct `styledeltamap -> tmap` aux reference is not mandatory across the native corpus. The base image and HDR gain map remain plausible contributors to Photos' residual spatial response after linearthumbnail neutralization.

## Style Metadata, MakerApple, and MakerNote

**Evidence grade: confirmed common metadata sources; spatial/control role still weakly proven.**

84/85 samples contain `/tag:apple.com,2023:photo:metadata:styles`. `IMG_2911` lacks it.

Style plist payload range:

- Min: 57,536 B.
- Median: 57,963 B.
- Max: 58,001 B.
- Mean: 57,908.44 B.

Every style plist contains binary keys:

- `1`: 51,840 B.
- `3`: 516 B.
- `c`: 2,048 B.
- `d`: 2,048 B.

The hashes for keys `1`, `3`, `c`, and `d` are unique per style sample in this corpus. That makes them important next-round candidates. The plist also has common scalar keys (`0`, `2`, `4`, `5`, `e`, `f`, `g`, `h`, `j`, `k`) and dictionary keys (`6`, `7`, `i`) in all 84 style samples.

ImageIO reports `{MakerApple}` in all 85 files. MakerApple key count ranges from 52 to 64, with median 58. ExifTool reports MakerNote in all 85 files. MakerApple/MakerNote are therefore native Apple metadata sources, but they are not sufficient style signatures because `IMG_2911` has them without style aux/metadata.

## Semantic Mattes and Sky Matte

**Evidence grade: sky matte low-priority; other semantic matte worth tracking but not first candidate.**

84/85 samples contain semantic sky matte:

`urn:com:apple:photo:2020:aux:semanticskymatte`

42/85 samples also contain:

`urn:com:apple:photo:2020:aux:semanticglassesmatte`

Sky matte decoded metrics:

- 84 decoded sky mattes.
- 6 decoded as constant maps.
- Base-luma correlation median 0.262008.
- Median decoded mean 3.361250.
- Median low-frequency energy ratio 0.995032.

Sky matte is present in the same 84 files that have style metadata, but the friend's black/white sky-matte observation plus the weak median base correlation make it a lower-priority candidate than linearthumbnail, style plist binary payloads, base/HDR gain map, and styledeltamap. The corpus does prove that sky matte is not the only semantic source, because `semanticglassesmatte` appears in 42 samples.

## Evidence-Graded Answers

### Confirmed

- Apple native style samples contain a coordinated HEIF family: primary grid, HDR gain map, `tmap`, `styledeltamap`, `linearthumbnail`, sky matte, style metadata URI plist, EXIF, MakerApple, and MakerNote.
- `IMG_2911.HEIC` is a non-style or HDR-only outlier: it keeps HDR gain map, `tmap`, EXIF, MakerApple, and MakerNote, but lacks `styledeltamap`, `linearthumbnail`, style metadata URI, and sky matte.
- `styledeltamap` is a 10-bit three-channel grid aux item in all 84 style samples.
- `linearthumbnail` is a 10-bit Main10 `hvc1` aux item in all 84 style samples and strongly correlates with base luminance.
- Style plist binary keys `1`, `3`, `c`, and `d` are stable in size and unique in hash per style sample.
- Sky matte is not the only semantic matte; `semanticglassesmatte` appears in 42 samples.

### Strong Evidence Supports

- `linearthumbnail` likely drives a large part of tone/color spatial response because it is detailed and highly base-correlated.
- `styledeltamap` is not a normal image and not a pure constant map; it behaves like a low-amplitude residual/control surface.
- Base image and HDR gain map remain plausible sources for Photos spatial response after linearthumbnail neutralization.
- Style metadata plist binary payloads are high-value perturbation targets because they are common, per-sample unique, and far larger than ordinary scalar metadata.

### Weak Evidence / Needs Manual Photos Validation

- Whether plist key `1` (51,840 B) encodes a spatial or histogram-derived control structure.
- Whether plist keys `c` and `d` are tone/color response tables, histograms, or another private representation.
- Whether MakerApple private keys carry data Photos uses for spatial style response.
- Whether samples with high-variance style maps (`IMG_2881`, `IMG_2887`, `IMG_2889`) produce visibly different Photos edit behavior than near-neutral samples.
- Whether `semanticglassesmatte` affects style behavior in glasses/person scenes.

### Low-Priority / Partly Excluded

- Sky matte as the main determinant: native structure shows it is common, but the friend black/white test reportedly showed no visible difference, and corpus evidence does not uniquely bind sky matte to style control.
- HDR gain map alone as a style signature: `IMG_2911` has HDR gain map and `tmap` but lacks the style family.
- MakerApple/MakerNote alone as a style signature: `IMG_2911` has both but lacks style aux/metadata.

### Still Unknown

- The private Apple Photos formula for tone/color response.
- Raw 10-bit styledeltamap sample values beyond decoded diagnostic PNG behavior.
- `grpl` payload meaning in the native item graph.
- Whether Photos uses style plist, MakerApple, base, HDR gain map, or `styledeltamap` dynamically after import versus only for activation/initialization.

## Manual Apple Photos Verification Table

Do these after choosing 1-2 native style samples. Preserve the original primary/base resolution.

| Test | Purpose | Expected interpretation |
|---|---|---|
| Native baseline copy | Establish import/edit baseline | Confirms sample still activates normally. |
| Neutral `styledeltamap` only | Test control-surface role | If response changes while linear/base stay native, style map matters. |
| Neutral `linearthumbnail` only | Test friend observation | If spatial response remains, linear is not sole source. |
| Neutral base only | Test base contribution | Must preserve dimensions; response change implicates base/derived sources. |
| Neutral `styledeltamap` + neutral `linearthumbnail` | Test remaining metadata/base/gain map | Residual response points to base/HDR/tmap/plist/MakerApple. |
| Neutral base + neutral style map + neutral linearthumbnail | Test non-image metadata | Remaining response points to metadata/MakerApple/tmap or Photos cache. |
| Sky matte black | Low-priority exclusion control | Should match friend observation if sky matte is low priority. |
| Sky matte white | Low-priority exclusion control | Compare against black and baseline. |
| Shift/rotate linearthumbnail | Spatial alignment test | Misregistration would strongly implicate linearthumbnail. |
| Shift/rotate styledeltamap | Spatial alignment test | Misregistration would implicate style map as spatial control. |
| Swap/neutral style plist key `1` | Highest metadata candidate | If response changes, plist binary is a real source. |
| Swap/neutral plist keys `c`/`d` | Tone/color table candidate | If response changes, these keys likely encode response data. |

## Next Three Experiments

1. On one high-variance style sample (`IMG_2889.HEIC`) and one near-neutral sample (`IMG_0032.HEIC`), neutralize only `linearthumbnail` while preserving base, style map, gain map, `tmap`, plist, MakerApple, and primary dimensions.
2. On the same pair, shift/rotate `styledeltamap` and `linearthumbnail` separately. This is the cleanest way to test spatial alignment rather than mere activation.
3. Perturb style plist binary key `1` first, then keys `c` and `d`, using payload hash/size-preserving neutral or cross-sample swap where possible.

## Validation Log

Commands completed:

```bash
/Users/retriedstormtrooper/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.test_apple_native_sample_inventory -v
/Users/retriedstormtrooper/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 tools/apple_native_sample_inventory.py Apple_Native_Samples --output-dir artifacts/apple_native_samples/20260602_native_source_study
/Users/retriedstormtrooper/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.test_apple_native_sample_inventory tests.test_heif_dump tests.test_styledeltamap_diagnostics tests.test_semantic_fitter tests.test_gainmap_sources -v
/Users/retriedstormtrooper/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m compileall tools tests
git diff --check
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

Results:

- Full inventory completed with 85 samples and 0 failures.
- Artifact assertions passed: 84 decoded `styledeltamap`, 84 decoded `linearthumbnail`, `IMG_2911.HEIC` as the only missing style-family sample, 85 MakerApple-positive samples, and 0 unknown items after thumbnail classification.
- Targeted bundled-runtime unittest: 18 tests OK.
- `compileall`: OK.
- `git diff --check`: OK.
- Full system-Python unittest discovery: 108 tests OK, 3 skipped.
- `pytest` is not installed in either the bundled Python runtime or system Python, so `python -m pytest tests/ -v` could not be run in this environment.
