# Apple-Parity Styledeltamap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate a HEIF candidate whose styledeltamap-related item graph and data types match Apple-native samples closely enough to test missing Photos/ImageIO activation requirements.

**Architecture:** Treat `Apple_Native_Samples/IMG_0032.HEIC` as the structural template. Keep the DNG/JPG-derived primary image path, but rebuild the final ISOBMFF file using Apple-like primary `grid` tiling, copied Apple private auxiliary/metadata item families, copied `tmap`/gain-map/style metadata/Exif item structure, and locally regenerated `iloc`/`iprp`/`mdat` offsets. Use `pillow_heif` only for individual HEVC tile payloads.

**Tech Stack:** Python 3, Pillow, pillow-heif, NumPy, local `tools/heif_dump.py`, `heif-info`, `heif-convert`, `plutil`, `unittest`.

---

## Root-Cause Evidence

The previous generated file imported into ImageIO/Photos but failed to expose the private style UI or auxiliary data. Current comparison against `Apple_Native_Samples/IMG_0032.HEIC` shows the prior artifact is structurally too small:

- Current primary item is a standalone `hvc1`; Apple primary is a `grid` item with 48 HEVC tile children.
- Current styledeltamap is `grid + 4 hvc1 tiles`, but its `pixi` and tile `hvcC` are 8-bit; Apple styledeltamap is `grid + 30 hvc1 tiles`, `pixi=[10,10,10]`, HEVC Main10.
- Current styledeltamap `auxl` references only the primary item; Apple styledeltamap references the primary and `tmap` item.
- Current file has no HDR gain-map auxiliary item, no `tmap`, no linear thumbnail aux, no semantic sky matte aux, no style metadata URI item, no Exif/MakerNote item, no Apple `MiH*` brands, and no `irot` parity.
- Apple sample includes style metadata bplist item `101` with URI `tag:apple.com,2023:photo:metadata:styles`, and Exif item `102`, both `cdsc`-referencing primary and `tmap`.

The first implementable parity milestone is therefore not a better residual formula. It is an Apple-template parity container:

- Generate a DNG/JPG-derived primary image as a 6x8 HEVC tile grid matching Apple item `49`.
- Preserve or copy Apple private auxiliary families for styledeltamap, HDR gain map, semantic sky matte, linear thumbnail, style metadata, Exif/MakerNote, and `tmap`.
- Rebuild offsets and property associations so local and external HEIF parsers accept the file.

## Standards And Registry Checks

- MP4RA registers `auxl` as "Auxiliary image item reference" and `dimg` as "Derived image item reference".
- MP4RA registers `auxC`, `hvcC`, `ispe`, `pixi`, `colr`, and `irot` as HEIF item properties.
- MP4RA registers HEIF item types including `grid`, `hvc1`, and `tmap`.
- ISO/IEC 23008-12:2025/Amd 1 is the current amendment for tone-map derivation support. It should only be treated as valid `tmap` work when a real base/gain-map/tone-map chain exists; this plan copies the Apple template's already-valid `tmap` family instead of inventing metadata.

## Files

- Create: `tools/apple_template_writer.py`
  - Reads an Apple-native HEIC template.
  - Extracts raw item payloads, raw item properties, references, and non-rebuilt meta children.
  - Regenerates the primary grid tile payloads from the DNG/JPG preview.
  - Replaces the primary tile `hvcC` property with the regenerated tile encoder config.
  - Rebuilds `iprp`, `idat`, `iloc`, `meta`, and `mdat`.
- Modify: `tools/heif_dump.py`
  - Add enough reporting for `tmap`, raw property inventory, and URI/Exif metadata parity checks if tests expose gaps.
- Create/modify: `tests/test_apple_template_writer.py`
  - Validate Apple-template parity item graph against the local Apple sample.
  - Validate the generated candidate contains the expected item families and references.
- Create: `docs/apple_parity_styledeltamap_attempt.md`
  - Record what is copied, what is generated, why this is still experimental, and which checks passed or failed.
- Generate: `artifacts/constructed/apple_parity_styledeltamap/apple_parity_styledeltamap.heic`
- Generate: `artifacts/constructed/apple_parity_styledeltamap/apple_parity_styledeltamap.heif.json`
- Generate: `artifacts/constructed/apple_parity_styledeltamap/apple_parity_styledeltamap.heif.md`

## Tasks

### Task 1: Build A Parity Diff Harness

- [ ] Write a failing test that compares the previous `iso_aux_styledeltamap.heic` dump against the Apple sample and proves it is missing the Apple-only families.
- [ ] Implement a small comparison helper in `tests/test_apple_template_writer.py` that checks required Apple parity features:
  - primary item is `grid`
  - primary grid has 48 `dimg` tile children
  - styledeltamap item is `grid`
  - styledeltamap has `auxC=tag:apple.com,2023:photo:aux:styledeltamap`
  - styledeltamap `pixi=[10,10,10]`
  - styledeltamap has 30 tile children
  - styledeltamap `auxl` points to primary and `tmap`
  - HDR gain map aux grid exists
  - `tmap` item exists and has `dimg=[primary,gainmap]`
  - style metadata URI item exists and `cdsc` references primary and `tmap`
  - Exif item exists and `cdsc` references primary and `tmap`
- [ ] Run the test and verify it fails on the previous artifact for the expected reasons.

### Task 2: Implement Apple Template Writer

- [ ] Write a failing test that calls `build_apple_template_parity_heif()` with fake replacement primary tile payloads and verifies the parsed graph has Apple parity features.
- [ ] Implement template parsing:
  - top-level `ftyp`
  - `meta` child extraction
  - raw `ipco` property boxes
  - raw `ipma` box
  - `iinf`/`iref`/`grpl` copying
  - item payload extraction from `idat` and `mdat`
- [ ] Implement `iprp` rebuilding with property index `23` replaced by the regenerated primary-tile `hvcC`.
- [ ] Implement `iloc` rebuilding with fixed 4-byte offsets, 4-byte lengths, 8-byte base offsets, and construction method `1` for `idat` items.
- [ ] Implement `mdat` rebuilding by item-id order while preserving copied auxiliary item payloads.
- [ ] Run the unit test and verify it passes.

### Task 3: Generate DNG/JPG-Derived Primary Grid

- [ ] Write a failing test for primary-grid tile preparation:
  - resize preview to `4032x3024`
  - pad to `4096x3072`
  - split into `6x8` 512px tiles
  - encode every tile as an individual HEVC payload
- [ ] Implement `build_from_pair_with_apple_template()`.
- [ ] Generate `apple_parity_styledeltamap.heic` from sample `IMG_0342`.
- [ ] Dump the output and verify local structural parity.

### Task 4: External Validation

- [ ] Run `heif-info artifacts/constructed/apple_parity_styledeltamap/apple_parity_styledeltamap.heic`.
- [ ] Run `heif-convert --with-aux --no-colons` and record whether primary plus copied private aux images decode.
- [ ] If decode fails, inspect whether `hvcC` replacement, `iloc`, item order, or primary tile payload coding caused the failure; fix only after locating the failing boundary.

### Task 5: Documentation And Completion Audit

- [ ] Write `docs/apple_parity_styledeltamap_attempt.md`.
- [ ] Update `docs/iso_aux_styledeltamap_writer.md` with a link to the Apple-parity attempt and clarify why the previous artifact failed.
- [ ] Run:
  - `python3 -m unittest discover -s tests -v`
  - `python3 tools/heif_dump.py artifacts/constructed/apple_parity_styledeltamap/apple_parity_styledeltamap.heic ...`
  - `heif-info ...`
  - `heif-convert --with-aux --no-colons ...`
- [ ] Do not mark the goal complete unless Apple Photos/ImageIO activation is re-tested and the output is proven to expose the requested private UI or auxiliary data. If the file only reaches structural/data-type parity, keep the goal active and document the remaining external validation gap.
