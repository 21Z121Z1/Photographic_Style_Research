# Preserve-Base HDR Style Graft - 2026-06-01

## What Is Proven

- `apple_style_injected_from_preview_heic_v1.heic` has been user-confirmed to
  activate Apple Photos Photographic Styles UI.
- v1's main known issue is low-quality q=0.25 `linearthumbnail` compression,
  not missing style activation.
- The preferred linearthumbnail encoding direction is VideoToolbox Main10,
  single-IDR item payload, and `hvcC` generated from the same encoded stream.
- q=0.45 is a better practical quality target than q=0.25 for visible
  linearthumbnail quality.

## External Reference Points

Apple's public HDR gain map documentation identifies the auxiliary data type as
`urn:com:apple:photo:2020:aux:hdrgainmap` and describes it as an 8-bit
single-channel luminance map encoded with the Rec.709 transfer function at
roughly one-quarter source resolution:

https://developer.apple.com/documentation/appkit/applying-apple-hdr-effect-to-your-photos

Apple also exposes the ImageIO constant:

https://developer.apple.com/documentation/ImageIO/kCGImageAuxiliaryDataTypeHDRGainMap

Android's Ultra HDR documentation is the useful public model for
metadata-aware gain-map reconstruction: gain map min/max, gamma, SDR/HDR
offsets, and display ratios determine a linear HDR estimate from the SDR base:

https://developer.android.com/media/platform/hdr-image-format

These references support the HDR gain-map handling, not Apple's private
Photographic Styles `styledeltamap` formula.

## Implemented Changes

`tools/inject_style_family.py` now has `--preserve-base-hdr-family`.

In this mode, the target file's own HDR graph is reused:

- primary/base item remains the target primary;
- target HDR gain map item remains the target gain map;
- target `tmap` item remains the target `tmap`;
- donor gain map and donor `tmap` are not copied;
- donor styledeltamap, linearthumbnail, optional semantic matte, and style
  metadata are copied as new items;
- copied donor style references are remapped to the target primary and target
  `tmap`.

The tool writes `style_injection_preservation_report.json` next to the output.
It reports primary, HDR gain map, and `tmap` payload hashes before/after,
derived child payload hashes, remapped refs, linearthumbnail replacement stats,
and any payload family that could not be preserved.

`tools/gainmap_sources.py` now recognizes Apple HEIC HDR gain maps through
`auxC = urn:com:apple:photo:2020:aux:hdrgainmap`. It reports item id,
dimensions, references, grid children, payload hashes, and decodes the raster
through `heif-convert --with-aux --no-colons` when available.

`tools/aux_generator.py linearthumbnail-best` now makes the source priority
explicit:

- P0: DNG/RAW-derived linearthumbnail;
- P1: metadata-aware RGB gain map plus base image;
- P2: mono/Apple gain-map luma/headroom fallback.

## Validation Artifact

Generated:

`artifacts/constructed/preserve_base_hdr_style_graft_20260601/apple_hdr_preserve_base_style_graft_from_IMG_2911.heic`

2026-06-02 correction: this artifact is structurally readable by `heif-info`
but is not Apple-native parseable. `sips` reports nil pixel dimensions, Swift
ImageIO reports `CGImageSourceGetCount == 0`, and QuickLook times out. The root
cause and fixed output are documented in
`docs/preserve_base_parseability_regression_2026-06-02.md`.

Target:

`Apple_Native_Samples/IMG_2911.HEIC`

Donor:

`artifacts/constructed/apple_parity_styledeltamap_v8_vt_linearthumb_q025/apple_parity_styledeltamap_v8_vt_linearthumb_q025.heic`

Key validation results:

- primary item id `50` preserved;
- HDR gain map item id `64` preserved;
- `tmap` item id `66` preserved;
- primary/HDR gain map/`tmap` payload families are byte-identical before/after;
- new styledeltamap item `97` has `auxl -> [50, 66]`;
- new semantic sky matte item `98` has `auxl -> [50, 66]`;
- new linearthumbnail item `99` has `auxl -> [50, 66]`;
- new style metadata item `100` has `cdsc -> [50, 66]`;
- target `tmap` keeps `dimg -> [50, 64]`;
- `semantic_fitter` hard warnings: `[]`;
- `heif-info` exits successfully, but that is not sufficient evidence for
  Apple-native parseability.

## Still Not Proven

- Preserve-base outputs need Apple Photos import testing per target family.
- The private Apple `styledeltamap` formula is still unknown.
- RGB gain maps can create useful diagnostic residuals, but that is not proof
  of Apple style delta semantics.
- Mono gain maps cannot recover real chroma residuals; they are luma/headroom
  fallback inputs only.
