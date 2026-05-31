# No Fusion styledeltamap Reverse Engineering

Date: 2026-05-25

## Executive Summary

This pass analyzed Apple-native HEIC files that contain `tag:apple.com,2023:photo:aux:styledeltamap`, then compared them with No Fusion outputs using the same HEIF item-graph dumper and decoded auxiliary-image diagnostics.

Key findings:

- Apple-native `IMG_0032.HEIC` and `IMG_0033.HEIC` store `styledeltamap` as a HEIF `grid` derived image with an `auxC` property, not as a standalone full raster item. The grid references tiled HEVC items through `dimg`.
- The Apple-native `styledeltamap` is `2880x2160`, `pixi=[10,10,10]`, tiled as 30 child items, and has only about 32-33 KB of compressed tile payload in these samples. The decoded diagnostic PNG is nearly neutral around 128 with very low variation.
- No Fusion `IMG_4745.HEIC` has ImageIO image count 3 and a larger item graph than Apple-native, but its `styledeltamap` payload is not a large high-detail high-bit layer. It is a `4096x3072`, 10-bit, 4:4:4 `grid` whose 48 child tiles total only 9,264 bytes and decode to a constant `[128,128,128]` diagnostic PNG.
- No Fusion does inject Apple MakerNote `SemanticStyle` in `IMG_4745.HEIC` and `IMG_E4745.heic`. Apple-native samples expose related MakerApple dictionaries through ImageIO, but ExifTool does not label them as `SemanticStyle`.
- `NoFusion_Samples/IMG_0032.HEIC` and `NoFusion_Samples/IMG_0033.HEIC` are byte-identical to the Apple-native samples, so they are not independent No Fusion evidence.
- ProRAW/JPG paired samples exist and can produce candidate residual maps from high-bit DNG data. This is plausible as a construction input path, but no paired Apple-native `styledeltamap` for the same scene is present, so the Apple algorithm remains unproven.

No FairPlay bypass, IPA decryption, credential extraction, or invasive service testing was performed. Existing app-bundle HEIC resources were only scanned as image files; app binaries were not cracked or disassembled.

## Artifacts and Tools

- HEIF dumper: `tools/heif_dump.py`
- Auxiliary diagnostics: `tools/styledeltamap_diagnostics.py`
- ProRAW residual probe: `tools/proraw_residual_probe.py`
- Unit tests: `tests/test_heif_dump.py`, `tests/test_styledeltamap_diagnostics.py`, `tests/test_proraw_residual_probe.py`
- HEIF JSON/Markdown dumps: `artifacts/dumps/*.heif.json`, `artifacts/dumps/*.heif.md`
- Decoded auxiliary diagnostics: `artifacts/diagnostics/styledeltamap/diagnostics.md`
- ProRAW residual probe: `artifacts/proraw_probe/IMG_0342/residual_probe.md`
- Negative construction experiment: `artifacts/constructed/pillow_multiframe_not_aux.heic`

## Sample Inventory

| File | Size | Primary Dimensions | ImageIO Count | HEIF Items | Auxiliary Types | Style Candidate | Notes |
|---|---:|---|---:|---:|---|---|---|
| `Apple_Native_Samples/IMG_0032.HEIC` | 402,472 B | 4032x3024 | 1 | 101 | `styledeltamap`, HDR gain map, semantic sky matte, linear thumbnail | Yes | Apple-native reference; SHA-256 `76a2fa...6501a`. |
| `Apple_Native_Samples/IMG_0033.HEIC` | 405,582 B | 4032x3024 | 1 | 101 | `styledeltamap`, HDR gain map, semantic sky matte, linear thumbnail | Yes | Apple-native reference; SHA-256 `c2f18a...213a0`. |
| `NoFusion_Samples/IMG_0032.HEIC` | 402,472 B | 4032x3024 | 1 | 101 | Same as Apple `IMG_0032` | Yes, but duplicate | Byte-identical to Apple-native `IMG_0032.HEIC`; not independent No Fusion output. |
| `NoFusion_Samples/IMG_0033.HEIC` | 405,582 B | 4032x3024 | 1 | 101 | Same as Apple `IMG_0033` | Yes, but duplicate | Byte-identical to Apple-native `IMG_0033.HEIC`; not independent No Fusion output. |
| `NoFusion_Samples/IMG_4745.HEIC` | 10,110,863 B | 4032x3024 | 3 | 123 | HDR gain map, linear thumbnail, `styledeltamap` | Yes | No Fusion output with explicit MakerNote `SemanticStyle`. |
| `NoFusion_Samples/IMG_E4745.heic` | 2,412,405 B | 4032x3024 | 1 | 65 | HDR gain map only | No | Has MakerNote `SemanticStyle`, but no `styledeltamap`. |
| `NoFusion_Work/.../hdrImage.heic` | 394 KB | 1613x1210 | not used | 28 | MPEG aux, HDR gain map | No | App-bundle image asset; no `styledeltamap`. |
| `NoFusion_Work/.../disparity.heic` | 1.2 MB | 4032x3024 | not used | 69 | HDR gain map, MPEG aux, XMP disparity | No | App-bundle image asset; no `styledeltamap`; has MakerNote `SemanticStyle`. |
| `NoFusion_Work/.../metadata.heic` | 50 KB | 286x216 | not used | 6 | MPEG aux, HDR gain map | No | App-bundle image asset; no `styledeltamap`. |
| ProRAW directory | 365 DNG, 241 JPG | mixed | n/a | n/a | n/a | Reconstruction inputs only | 241 `_converted.DNG` / `_preview.jpg` pairs discovered. |

## Apple-Native File Structure

Reference: `Apple_Native_Samples/IMG_0032.HEIC`.

Top-level structure:

- `ftyp`: major brand `heic`; compatible brands include `mif1`, `heic`, `miaf`, `tmap`, Apple `MiH*` brands.
- `meta`: item graph and properties.
- `mdat`: compressed media payload.

Important items:

| Item | Type | Role | Dimensions | Pixel Info | Relationships |
|---:|---|---|---|---|---|
| 49 | `grid` | Primary image | 4032x3024 | `pixi=[8,8,8]` | `dimg` to 48 HEVC tiles; thumbnail item 50. |
| 81 | `grid` | `styledeltamap` aux | 2880x2160 | `pixi=[10,10,10]` | `dimg` to 30 HEVC tiles; `auxl` references `[49,100]`. |
| 94 | `grid` | HDR gain map aux | 2016x1512 | `pixi=[8]` | `dimg` to 12 HEVC tiles; `auxl` references primary. |
| 95 | `hvc1` | semantic sky matte aux | 2016x1512 | `pixi=[8]` | `auxl` references `[49,100]`; `cdsc` metadata item 96. |
| 97 | `hvc1` | linear thumbnail aux | 1024x768 | `pixi=[10,10,10]` | `auxl` references `[49,100]`; `cdsc` metadata item 98. |
| 100 | `tmap` | tone map derived item | 3024x4032 | `pixi=[10,10,10]` | `dimg` references `[49,94]`. |
| 101 | `uri ` | `/tag:apple.com,2023:photo:metadata:styles` | n/a | bplist, 57,550 B | `cdsc` references `[49,100]`. |
| 102 | `Exif` | EXIF/MakerNote | n/a | 3,068 B | `cdsc` references `[49,100]`. |

The Apple `styledeltamap` is therefore an auxiliary derived grid item. Its own item extent is only the 8-byte grid descriptor; the actual compressed image payload lives in the 30 referenced HEVC tile items. In the two Apple-native samples, those tile payloads total 33,141 B and 32,654 B.

Decoded diagnostics via `heif-convert --with-aux`:

| Sample | Decoded styledeltamap Size | Min | Max | Mean | Std | Unique Sample Values | Base-Luma Correlation |
|---|---|---|---|---|---|---:|---|
| Apple `IMG_0032` | 2160x2880 RGB PNG | `[125,126,124]` | `[129,130,130]` | `[127.78,127.92,127.76]` | `[0.43,0.28,0.47]` | 5 | low, around `-0.087..0.005` |
| Apple `IMG_0033` | 2160x2880 RGB PNG | `[123,126,123]` | `[130,131,130]` | `[127.77,127.91,127.76]` | `[0.44,0.30,0.48]` | 6 | low, around `-0.089..-0.059` |

Interpretation: the decoded diagnostic view is low-amplitude and strongly quantized around neutral 128. It does not look like a normal image, luminance map, or semantic mask. It may represent a small residual/control surface, but this evidence alone does not prove its semantic formula.

## No Fusion Comparison

Reference: `NoFusion_Samples/IMG_4745.HEIC`.

Important differences from Apple-native:

| Feature | Apple Native | No Fusion `IMG_4745` | Evidence Status |
|---|---|---|---|
| ImageIO image count | 1 | 3 | Proven by `CGImageSourceGetCount`. |
| HEIF item count | 101 | 123 | Proven by `tools/heif_dump.py`. |
| Primary image payload | 48 tiles, 232,384 B compressed payload | 48 tiles, 8,454,723 B compressed payload | Proven by `dimg` child extent totals. |
| `styledeltamap` item | item 81, `grid`, 2880x2160 | item 73, `grid`, 4096x3072 | Proven. |
| `styledeltamap` pixel info | 10-bit 3-channel, HEVC 4:2:0 tile children | 10-bit 3-channel, HEVC 4:4:4 tile children | Proven by `pixi` and child `hvcC`. |
| `styledeltamap` compressed payload | 30 tiles, 33 KB | 48 tiles, 9.3 KB | Proven. |
| `styledeltamap` decoded diagnostic | near-neutral with slight variation | constant `[128,128,128]` | Proven after auxiliary PNG extraction. |
| semantic sky matte | present | absent | Proven by aux type inventory. |
| MakerNote `SemanticStyle` | not labeled by ExifTool, but ImageIO MakerApple has related dictionaries | explicit `{_0=1,_1=0,_2=0}` | Proven for No Fusion sample. |

The report's phrase "3 images" is directionally correct for ImageIO-visible image count on `IMG_4745.HEIC`, but the lower-level HEIF graph is not literally just three image items. It contains 123 item entries, including tiled grids, metadata, `tmap`, and auxiliary relationships.

The claim that No Fusion's `styledeltamap` is a large high-bit data layer is falsified for `IMG_4745.HEIC`. The large data in the file is primarily the main 4032x3024 image tile payload and the linear thumbnail. The `styledeltamap` is structurally larger in dimensions and 4:4:4 pixel format, but its compressed payload is tiny and decodes to a constant neutral map.

`IMG_E4745.heic` is important as a negative/variant output: it has MakerNote `SemanticStyle` but lacks `styledeltamap`. That suggests MakerNote alone is not equivalent to the full Photos-compatible structure.

## Payload-Level Interpretation

Observed `styledeltamap` behavior:

- Apple-native payload is low-amplitude and quantized after decode, with very few values near neutral 128.
- No Fusion payload is a neutral constant map after decode.
- Apple-native style map has weak or negative spatial correlation with base luma, unlike HDR gain maps, which correlate strongly with luminance.
- Apple-native samples include a style metadata bplist (`/tag:apple.com,2023:photo:metadata:styles`) with histogram/statistical entries, 2048-byte binary arrays, and gain/original-range values. No Fusion also carries this bplist, but in `IMG_4745` the analogous `c`/`d` 2048-byte arrays are all zero in the inspected dump.

Confidence:

- It is proven that `styledeltamap` is not an ordinary visible image or semantic matte in these samples.
- It is strongly suggested that it is a compact residual/control map centered at neutral.
- It is plausible, but not proven, that the residual is derived from higher-bit tone/style pipeline data.
- It is not supported that No Fusion's `styledeltamap` stores a rich high-bit reconstruction payload in `IMG_4745.HEIC`.

## ProRAW / High-Bit Reconstruction Probe

Input folder:

`/Users/retriedstormtrooper/Downloads/03_图片素材/RAW_DNG照片/RAW_DNG_JPEG_批量导出`

Inventory:

- 365 DNG files named `*_converted.DNG`
- 241 preview JPG files named `*_preview.jpg`
- 241 matched DNG/JPG pairs

Probe sample: `IMG_0342`.

Metadata:

- DNG model: Apple iPhone 15 Pro
- DNG software: Adobe DNG Converter 16.5
- DNG raw image: 8064x6048, 16-bit Linear Raw, `WhiteLevel=65535`
- Preview JPG: 8064x6048, 8-bit Display P3
- `sips` can decode the DNG to a 8064x6048, 16-bit/color RGB PNG.

Residual probe at max dimension 1024:

- High/base luma correlation: `0.96451`
- Luma residual range: `-0.030184..0.391308`
- Luma residual mean/std: `0.228447 / 0.055419`
- Quantized luma residual values: 2-bit `[1,2]`, 4-bit `[7,8,9,10,11]`

Interpretation:

The ProRAW/JPG pair provides enough high-bit vs rendered-base information to construct plausible residual maps. The first-pass luma residual is low-dimensional after quantization, which is consistent with the broad "small residual/control surface" hypothesis. However, because no same-scene Apple-native `styledeltamap` is paired with these DNG/JPG files, this is only an input-feasibility result. It does not prove Apple's style map formula.

## Construction Requirements

A Photos-compatible construction attempt must reproduce more than an aux type string. Based on the Apple-native and No Fusion structures, a candidate file likely needs:

- Primary HEIC image item with correct `ispe`, `pixi`, `hvcC`, `colr`, orientation, and tiled/grid relationships.
- `auxC` property with `tag:apple.com,2023:photo:aux:styledeltamap`.
- `styledeltamap` as a derived `grid` item with HEVC tile children, not merely an appended second image.
- `auxl` references from the styledelta grid to the primary and likely to the `tmap` item.
- A `tmap` derived item linking primary/HDR gain-map structure where HDR/gain-map metadata exists.
- `/tag:apple.com,2023:photo:metadata:styles` bplist metadata item with `cdsc` references.
- EXIF/MakerNote data with Apple MakerNote version and, for No Fusion-like files, explicit `SemanticStyle`.
- Consistent color/pixel properties: Apple-native style maps use 10-bit 4:2:0 tile payloads; No Fusion `IMG_4745` uses 10-bit 4:4:4 tile payloads.

Negative construction experiment:

- `artifacts/constructed/pillow_multiframe_not_aux.heic` was created from a base image and a neutral map using `pillow_heif` multi-image save.
- Dump result: 4 items, no `auxC`, no `styledeltamap`, and only `cdsc` references.
- Conclusion: a normal multi-image HEIC writer is insufficient. A real constructor needs ImageIO auxiliary-data writing or a lower-level ISOBMFF writer that can emit `auxC`, `ipma`, `iref`, `iloc`, tiled grids, and metadata relationships.

## NoFusion_Analysis_Report Claim Audit

| Claim | Result | Confidence | Evidence |
|---|---|---|---|
| No Fusion uses multiple image items / images. | Proven for `IMG_4745.HEIC`; not for every output. | High | ImageIO count is 3 for `IMG_4745`, 1 for `IMG_E4745`; HEIF item count is 123 vs 65. |
| No Fusion contains a large high-bit/HDR-like auxiliary layer. | Falsified if referring to `styledeltamap`; plausible only for other image/tone-map payloads. | High for falsifying styledeltamap. | `styledeltamap` tile payload is 9,264 B and decodes constant 128. |
| No Fusion `styledeltamap` is larger/structurally different than Apple-native. | Proven structurally; falsified as "larger payload". | High | Dimensions 4096x3072 vs 2880x2160; 4:4:4 vs Apple 4:2:0; payload 9.3 KB vs Apple 33 KB. |
| No Fusion injects Apple MakerNote `SemanticStyle`. | Proven for `IMG_4745.HEIC` and `IMG_E4745.heic`. | High | ExifTool reports `{_0=1,_1=0,_2=0}`. |
| No Fusion relies on HEIC metadata/auxiliary construction rather than native capture APIs. | Strongly suggested by output files; not directly proven by file structure alone. | Medium | Non-native-looking HEIF graph plus MakerNote/style metadata are present, but no binary/API tracing was performed. |
| `styledeltamap` acts as high-bit recovery data. | Plausible for Apple in abstract, unproven here. | Low/Medium | Apple map is low-amplitude quantized; no paired high-bit source and same-scene style map exists. |

## Validation Log

Commands run:

- `python3 -m unittest tests/test_heif_dump.py -v`
- `python3 -m unittest tests/test_styledeltamap_diagnostics.py -v`
- `python3 -m unittest tests/test_proraw_residual_probe.py -v`
- `python3 tools/heif_dump.py <sample> --json ... --md ... --extract-items ...`
- `exiftool -G1 -a -s ... Apple_Native_Samples/*.HEIC NoFusion_Samples/*`
- `heif-info <sample>`
- `heif-convert --with-aux --no-colons <sample> <out.png>`
- `python3 tools/styledeltamap_diagnostics.py Apple_Native_Samples/IMG_0032.HEIC Apple_Native_Samples/IMG_0033.HEIC NoFusion_Samples/IMG_4745.HEIC ...`
- `python3 tools/proraw_residual_probe.py --root <RAW_DNG_JPEG_批量导出> --sample IMG_0342 ...`
- Swift/ImageIO one-off inspection using `CGImageSourceGetCount` and `CGImageSourceCopyPropertiesAtIndex`.
- `shasum -a 256` for duplicate detection.

Failures or limits:

- `pytest` is not installed for the system Python, so tests use `unittest`.
- `rawpy` is not installed; the ProRAW probe uses macOS `sips` to decode DNG into 16-bit RGB PNG.
- `pillow_heif` can enumerate 10-bit auxiliary images but cannot directly return 10-bit aux rasters; `heif-convert` was used for diagnostic PNG extraction.
- Generated PNG diagnostics are decoded/possibly quantized views, not raw HEVC bitstream values.
- No macOS Photos import/UI behavior was validated in this pass.
- No same-scene ProRAW/JPG/Apple-native styledeltamap triplet was available, so reconstruction remains a hypothesis.

## Open Questions

- What exactly do the bplist keys `1`, `3`, `c`, and `d` encode inside `/tag:apple.com,2023:photo:metadata:styles`?
- Does Photos require the `tmap` relationship for Photographic Styles UI activation, or only for high-quality edit behavior?
- Are No Fusion's constant neutral `styledeltamap` and nonzero style metadata enough for UI activation, with actual edit quality carried elsewhere?
- Which MakerApple key/value combinations are required versus incidental capture metadata?
- Can a same-scene ProRAW + rendered HEIC + Apple-native `styledeltamap` triplet be captured to fit and test an actual residual model?
