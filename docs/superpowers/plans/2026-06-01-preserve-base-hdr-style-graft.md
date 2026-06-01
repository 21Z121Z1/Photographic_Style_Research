# Preserve-Base HDR Style Graft Plan - 2026-06-01

Detailed workspace plan:

`artifacts/research/preserve_base_hdr_style_graft_20260601/plan.md`

The implementation goal is to move from "build a new preview-derived HEIC and
copy the whole donor style/HDR family" to "reuse an existing Apple-readable HDR
HEIC's primary, HDR gain map, and `tmap` payloads byte-identically, then graft
only Photographic Styles items."

High-confidence facts:

- `apple_style_injected_from_preview_heic_v1.heic` was user-confirmed to
  activate Apple Photos Photographic Styles UI.
- v1's problem is linearthumbnail quality, not activation failure.
- VideoToolbox Main10, single-IDR payloads, and matching stream-derived `hvcC`
  are the correct linearthumbnail encoding direction.
- Apple HDR gain maps can be recognized by
  `urn:com:apple:photo:2020:aux:hdrgainmap`.

Implementation plan:

1. Add preserve-base mode to `tools/inject_style_family.py`.
2. In preserve-base mode, omit donor gain map and donor `tmap` from copied
   items, and remap donor style references to the target primary and target
   `tmap`.
3. Write a preservation report with primary, HDR gain map, `tmap`, injected
   item ids, payload hashes, child payload hashes, remapped refs, and any
   failed preservation claims.
4. Add Apple HEIC HDR gain-map source detection and `heif-convert --with-aux`
   raster extraction to `tools/gainmap_sources.py`.
5. Add explicit linearthumbnail source priority to `tools/aux_generator.py`:
   P0 DNG/RAW, P1 metadata-aware RGB gain map, P2 mono/Apple luma fallback.
6. Add tests for source priority, Apple HDR gain-map extraction, and
   preserve-base payload preservation.
7. Generate one local preserve-base artifact from `IMG_2911.HEIC` and verify
   with `heif-info`, `heif_dump`, and `semantic_fitter`.
8. Update docs to separate proven Photos activation, preserve-base structural
   validation, and unproven private styledeltamap semantics.

Non-goals:

- Do not claim preserve-base Photos UI activation until a generated output is
  imported and tested.
- Do not claim RGB or mono gain-map residuals match Apple's private
  styledeltamap formula.
- Do not fake `tmap`; preserve or construct it only when a valid gain-map chain
  exists.
