# Preserve-Base Parseability Regression - 2026-06-02

## Scope

This pass fixes the preserve-base HDR style graft output so Apple-native
parsers see it as a real image before any Photos style-activation claim. It does
not change DNG, gain-map reconstruction, or styledeltamap semantic generation.

Failed input from the previous pass:

`artifacts/constructed/preserve_base_hdr_style_graft_20260601/apple_hdr_preserve_base_style_graft_from_IMG_2911.heic`

Fixed output:

`artifacts/constructed/preserve_base_parseability_fixed_20260602/apple_hdr_preserve_base_style_graft_from_IMG_2911_parseable.heic`

## Root Cause

`IMG_2911.HEIC` contains a file-level `grpl` box with an `altr` entity group
whose `group_id` is `67`. The old preserve-base item allocator used
`max(base_item_id) + 1`, and the target's highest item id was `66`, so the first
injected item was also assigned id `67`.

That created an entity namespace collision:

- `grpl/altr group_id = 67`
- first injected item id = `67`

`heif-info` was lenient and still reported the primary image, but ImageIO,
`sips`, and QuickLook treated the file as not exposing a primary decodable
image. A minimal inert item at id `67` reproduced the failure; the same inert
item at id `68` passed.

The previous writer also merged donor `ftyp` brands into preserve-base outputs.
That was not the primary ImageIO failure, but it caused a `heif-info` brand
warning and added unnecessary risk. Preserve-base mode now bit-preserves the
target `ftyp` when it reuses the target HDR/tmap graph.

## Fix

- `tools/inject_style_family.py` now parses `grpl` entity group ids while
  loading a HEIF.
- `_build_item_id_map` reserves both existing item ids and entity group ids.
- Preserve-base HDR mode writes the target `ftyp` bytes unchanged when the
  target HDR/tmap graph is reused.
- `style_injection_preservation_report.json` now includes a
  `container_preservation` section with top-level box order, meta child order,
  `ftyp`, entity group ids, new item ids, item/group collisions, and base item
  `iloc`/ipma/reference changes.
- `tools/validate_apple_parseability.py` runs Apple-native gates and marks
  ImageIO, `sips`, and QuickLook failures as hard failures.

## Bisection Matrix

All reports are under:

`artifacts/research/preserve_base_parseability_regression_20260602/validation/`

| Case | File | Result | Evidence |
| --- | --- | --- | --- |
| A0 original | `Apple_Native_Samples/IMG_2911.HEIC` | PASS | ImageIO count 1, `sips` 4284x5712, QuickLook thumbnail created |
| Previous failed graft | `artifacts/constructed/preserve_base_hdr_style_graft_20260601/apple_hdr_preserve_base_style_graft_from_IMG_2911.heic` | FAIL | ImageIO count 0, `sips` nil dimensions, QuickLook timeout |
| A1 zero-change serializer roundtrip | `A1_current_serializer_zero_roundtrip.heic` | PASS | Rebuilding meta/iloc alone did not break Apple parseability |
| A3a inert item id 67 | `A3a_inert_uri_no_ref_no_ipma.heic` | FAIL | Reproduces ImageIO count 0 with no style payload |
| A3c inert item id 68 | `A3c_inert_uri_item68_no_ref_no_ipma.heic` | PASS | Same inert payload passes when avoiding group id 67 |
| A4 fixed style metadata only | `A4_fixed_style_metadata_only.heic` | PASS | New item starts at 68 |
| A5a fixed linearthumbnail, no auxl | `A5a_fixed_linearthumbnail_no_auxl.heic` | PASS | New item starts at 68 |
| A5b fixed linearthumbnail with auxl | `A5b_fixed_linearthumbnail_auxl.heic` | PASS | `auxl -> [50, 66]` accepted |
| A6a fixed styledeltamap grid, no auxl | `A6a_fixed_styledeltamap_grid_no_auxl.heic` | PASS | Grid and tile children accepted |
| A6b fixed styledeltamap grid with auxl | `A6b_fixed_styledeltamap_grid_auxl.heic` | PASS | `dimg` plus `auxl -> [50, 66]` accepted |
| A7 fixed semantic sky matte | `A7_fixed_semantic_sky_matte_auxl.heic` | PASS | Semantic aux item accepted |
| A8 fixed full graft | `apple_hdr_preserve_base_style_graft_from_IMG_2911_parseable.heic` | PASS | Full style family accepted by Apple-native parseability gates |

## Final Artifact Validation

Final wrapper report:

`artifacts/research/preserve_base_parseability_regression_20260602/validation/A8_final_fixed_full_graft.apple_parseability.json`

Final HEIF dump:

`artifacts/research/preserve_base_parseability_regression_20260602/validation/A8_final_fixed_full_graft.heif.json`

Final semantic report:

`artifacts/research/preserve_base_parseability_regression_20260602/validation/A8_final_fixed_full_graft.semantic.json`

Final preservation report:

`artifacts/constructed/preserve_base_parseability_fixed_20260602/style_injection_preservation_report.json`

Validation result:

- `heif-info`: pass; compatible brands are target brands `mif1, tmap, MiHE, miaf, MiHB, heic`.
- `sips`: `pixelWidth: 4284`, `pixelHeight: 5712`, `format: heic`.
- Swift ImageIO validator: `ok: true`, `count: 1`, `cgImageWidth: 4284`, `cgImageHeight: 5712`.
- QuickLook: thumbnail created.
- `semantic_fitter`: `hard_warnings: []`.
- Preserve report: primary item `50`, HDR gain map item `64`, and `tmap` item `66` payload families are byte-identical.
- Container report: base entity group ids `[67]`, output item/group collisions `[]`, new item ids `68-101`.

## Remaining Boundary

This proves Apple-native parseability for the preserve-base output. It does not
prove Apple Photos Photographic Styles UI activation. Photos activation still
requires importing the final artifact into Photos or testing through ImageIO
behavior that specifically exposes Photographic Styles controls.
