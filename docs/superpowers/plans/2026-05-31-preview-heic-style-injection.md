# Preview HEIC Style Injection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a direct injection path that starts from a JPEG converted to an Apple-style HEIC base and injects the Photographic Styles private HEIF family without using the Apple native sample as the whole output template.

**Architecture:** Keep the base HEIC primary graph authoritative, then append/remap a donor style family from the working v8-style HEIC. Rebuild `iinf`, `iref`, `iprp/ipco/ipma`, `idat`, `iloc`, and `mdat` from parsed item payloads so all absolute offsets and references are current.

**Tech Stack:** Python 3.13, local `tools/heif_dump.py` parser, existing HEVC/ImageIO helpers, macOS `sips` for optional Apple HEIC base generation, `heif-info` / `heif-convert` for external validation.

---

## Context

`v8_vt_linearthumb_q025` activates Apple Photos style controls. That proves the generated `linearthumbnail` item can be Apple-compatible when its data type matches native item 97:

- `hvc1`, hidden, `auxC = tag:apple.com,2023:photo:aux:linearthumbnail`
- `ispe = 1024x768`, `pixi = [10,10,10]`
- 105-byte Main10 `hvcC`
- one length-prefixed IDR NAL type 20
- `auxl -> [primary, tmap]`
- payload size in native corpus scale

The remaining gap is architectural: current `tools/apple_template_writer.py` emits a file whose whole item graph comes from `Apple_Native_Samples/IMG_0032.HEIC`, then replaces payloads. The next target is a tool that starts from an Apple-generated HEIC converted from the preview and injects only the style family.

## Friend Claim To Validate

The screenshot claim has two parts:

1. Apple style delta data likely stores a prediction/residual-like correction, so many maps are near-neutral and low-information.
2. `linearthumbnail` is strongly coupled to shadow/style rendering; replacing it changes activation and likely rendering behavior.

Evidence already supports part 2 because `v5_style_safe` worked, `v5` failed, and `v8` works after only the generated linearthumbnail data type was made Apple-like. Part 1 remains a hypothesis: native styledeltamap maps are near-neutral, low-amplitude, and low-entropy, but the exact prediction formula is not proven.

## Files

- Create: `tools/inject_style_family.py`
  - CLI for optional base HEIC generation from preview and direct style-family injection into a base HEIC.
  - Rebuilds merged HEIF metadata with item id remapping.
- Modify: `tools/semantic_fitter.py`
  - Add a warning when `tmap` dimensions do not match the primary item dimensions.
  - Add explicit reporting for injected/remapped item ids.
- Create: `tests/test_style_family_injector.py`
  - Unit tests for item id remapping, reference rewriting, dimension mismatch rejection, and successful injection into a small fixture-like base.
- Create: `docs/preview_heic_style_injection_2026-05-31.md`
  - Findings, commands, friend-facing explanation, and validation results.

## Task 1: Write Failing Tests For Remap And Dimension Policy

**Files:**
- Create: `tests/test_style_family_injector.py`

- [ ] Add a test that loads the existing `IMG_0342_preview_sips.heic` base and asserts it is not directly compatible with v8 style injection because primary dimensions are `8064x6048`, while the donor `tmap` item is `4032x3024`.

Expected test shape:

```python
def test_rejects_dimension_mismatch_between_base_primary_and_donor_tmap():
    base = Path("artifacts/constructed/apple_parity_styledeltamap/IMG_0342_preview_sips.heic")
    donor = Path("artifacts/constructed/apple_parity_styledeltamap_v8_vt_linearthumb_q025/apple_parity_styledeltamap_v8_vt_linearthumb_q025.heic")
    if not base.exists() or not donor.exists():
        self.skipTest("base or donor artifact missing")

    with self.assertRaisesRegex(ValueError, "primary dimensions"):
        inject_style_family(base, donor)
```

- [ ] Add a test that injects v8 into a compatible 4032x3024 base and verifies:
  - primary item id remains the base primary id;
  - injected styledeltamap has `auxC = tag:apple.com,2023:photo:aux:styledeltamap`;
  - injected linearthumbnail has `auxC = tag:apple.com,2023:photo:aux:linearthumbnail`;
  - injected linearthumbnail references `[base_primary, injected_tmap]`;
  - injected `tmap` references `[base_primary, injected_gainmap]`;
  - there are no item-id collisions.

## Task 2: Implement Direct Style Family Injector

**Files:**
- Create: `tools/inject_style_family.py`

- [ ] Implement raw HEIF loading helpers:
  - top-level `ftyp`, `meta`, `mdat` lookup;
  - raw `ipco` property box extraction;
  - item payload extraction for `iloc` construction method 0 and 1;
  - raw meta child preservation for `hdlr`, `dinf`, and `pitm`.

- [ ] Implement style family selection from donor:
  - styledeltamap grid and child tiles;
  - HDR gainmap grid and child tiles;
  - gainmap metadata item;
  - semantic sky matte;
  - linearthumbnail;
  - tmap;
  - style metadata URI item.

- [ ] Exclude donor primary and donor Exif by default.

- [ ] Implement item-id remapping:
  - base item ids keep their original ids;
  - donor style items get fresh ids above the base max id;
  - donor primary references retarget to base primary;
  - donor tmap references retarget to the remapped tmap item.

- [ ] Rebuild boxes:
  - `ftyp` = base brands plus donor-required brands such as `tmap`;
  - `iinf` = base entries plus remapped donor entries;
  - `iref` = base refs plus remapped donor refs;
  - `iprp` = base `ipco` plus donor properties associated with injected items, with `ipma` remapped;
  - `idat` and `mdat` = extracted payloads in new order;
  - `iloc` = all new offsets and lengths.

- [ ] Add `--preview-jpeg` option to update an existing base Exif item with preview Exif plus donor MakerNote private payload using `tools/exif_makernote_swap.py`.

- [ ] Add `--make-base-with-sips` option:
  - resize the preview to a requested size, default `4032x3024`;
  - call `sips -s format heic`;
  - feed the generated base into the injector.

## Task 3: Improve Validation Tooling

**Files:**
- Modify: `tools/semantic_fitter.py`

- [ ] Add hard warning if a candidate has a `tmap` item whose dimensions do not match the primary item dimensions.
- [ ] Add hard warning if styledeltamap or linearthumbnail references an item that is not the current primary item.
- [ ] Keep existing v8 validations green.

## Task 4: Build And Validate A Direct Injection Candidate

**Commands:**

```bash
/private/tmp/styledeltamap-py313/bin/python tools/inject_style_family.py \
  --preview-jpeg "/Users/retriedstormtrooper/Downloads/03_图片素材/RAW_DNG照片/RAW_DNG_JPEG_批量导出/IMG_0342_preview.jpg" \
  --make-base-with-sips \
  --base-size 4032x3024 \
  --style-donor artifacts/constructed/apple_parity_styledeltamap_v8_vt_linearthumb_q025/apple_parity_styledeltamap_v8_vt_linearthumb_q025.heic \
  --template Apple_Native_Samples/IMG_0032.HEIC \
  --output artifacts/constructed/apple_style_injected_from_preview_heic_v1/apple_style_injected_from_preview_heic_v1.heic
```

Validation:

```bash
/private/tmp/styledeltamap-py313/bin/python tools/heif_dump.py ... --json ... --md ...
heif-info ...
heif-convert --with-aux --no-colons ... decoded.png
/private/tmp/styledeltamap-py313/bin/python tools/semantic_fitter.py ... --reference artifacts/constructed/apple_parity_styledeltamap_v8_vt_linearthumb_q025/apple_parity_styledeltamap_v8_vt_linearthumb_q025.heic --template Apple_Native_Samples/IMG_0032.HEIC --decoded-dir ... --json ... --md ...
```

## Task 5: Write Friend-Facing Explanation

**Files:**
- Create: `docs/preview_heic_style_injection_2026-05-31.md`

Include:

- what was verified from the screenshot claim;
- what remains a hypothesis;
- the exact tool command to run;
- why `linearthumbnail` must be Main10 single-IDR and native-size;
- why direct injection must remap ids and keep primary/tmap dimensions consistent;
- Photos UI activation status for the direct-injection candidate.

## Completion Standard

Do not mark the active goal complete until current evidence proves all of the following:

- direct-injection output starts from a generated Apple HEIC base, not a whole-file Apple sample template;
- primary item id and primary payload come from the base HEIC;
- injected style family is present with no id collisions;
- styledeltamap, linearthumbnail, HDR gainmap, semantic matte, tmap, and style metadata keep Apple-compatible item types, properties, and references;
- `tmap -> [base primary, injected gainmap]`;
- style aux items use `auxl` to the base primary and remapped tmap when Apple does;
- `heif-info` accepts the file;
- `heif-convert --with-aux` extracts the expected aux images;
- `semantic_fitter` reports zero hard warnings;
- Apple Photos style UI is tested for the direct-injected file or documented as pending external validation.
