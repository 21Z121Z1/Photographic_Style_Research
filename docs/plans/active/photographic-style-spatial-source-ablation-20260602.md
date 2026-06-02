# Photographic Style Spatial Source Ablation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a reproducible ablation and diagnostic workflow that can isolate which Apple Photos Photographic Styles HEIC payload family carries residual tone/color spatial response.

**Architecture:** Reuse the current Apple-like HEIF graph writers and parsers instead of inventing a new container writer. The new workflow will patch role-specific item payload families in a known Photos-activating HEIC, generate machine-readable manifests and diagnostics for every variant, and mark Apple Photos rendering behavior as manual evidence only.

**Tech Stack:** Python 3, Pillow, NumPy, existing `tools/heif_dump.py`, `tools/semantic_fitter.py`, `tools/styledeltamap_diagnostics.py`, existing HEVC/x265/VideoToolbox helper paths, libheif `heif-convert` and `heif-info`.

---

## Friend Experiment Summary

The new observation changes the working hypothesis:

- The linear thumbnail affects Photographic Styles rendering, but it is not assumed to be the only or dominant spatial source.
- When the base image and `styledeltamap` are filled with neutral/mid values, style rendering becomes low-frequency and smooth.
- After also filling the entire linear thumbnail with mid values, Photos still appears to retain part of the original image's spatial light/dark structure while tone/color sliders are adjusted.
- Sky matte all-black/all-white tests reportedly showed no obvious difference, so semantic sky matte is a low-priority exclusion candidate.
- The residual source may be in HDR gain map, `tmap`, style bplist, MakerNote, item graph associations, or other unexplained item payloads/metadata.

This plan treats all Photos UI/rendering observations as manual evidence. Automatic checks only prove file structure, payload replacement, aux decode statistics, and graph/hash differences.

## Current Repository Baseline

Audited files:

- `README.md`
- `docs/preview_heic_style_injection_2026-05-31.md`
- `docs/apple_linearthumbnail_item97_findings_2026-05-31.md`
- `docs/linearthumbnail_gainmap_raw_reconstruction_2026-05-31.md`
- `docs/preserve_base_hdr_style_graft_2026-06-01.md`
- `docs/style_semantic_payload_fitting_2026-05-28.md`
- `docs/generated_aux_construction_plan.md`
- `docs/iso_aux_styledeltamap_writer.md`
- `tools/apple_template_writer.py`
- `tools/inject_style_family.py`
- `tools/heif_dump.py`
- `tools/semantic_fitter.py`
- `tools/styledeltamap_diagnostics.py`
- `tools/aux_generator.py`
- `tools/gainmap_sources.py`
- `tools/exif_makernote_swap.py`
- `tests/test_apple_template_writer.py`
- `tests/test_style_family_injector.py`
- `tests/test_semantic_fitter.py`
- `tests/test_gainmap_sources.py`

Baseline facts to preserve:

- `artifacts/constructed/apple_style_injected_from_preview_heic_v1/apple_style_injected_from_preview_heic_v1.heic` is the current user-confirmed Photos UI activating direct-injection artifact.
- Its role IDs are not the Apple-native template IDs: primary `49`, Exif `50`, `styledeltamap` `82`, HDR gain map `95`, sky matte `96`, linearthumbnail `97`, `tmap` `99`, style metadata `100`.
- `tools/semantic_fitter.py` reports zero hard warnings for that v1 artifact.
- `tools/inject_style_family.py` can inject style families, preserve target HDR gain map/`tmap`, replace linearthumbnail payload+`hvcC`, update style bplist, and swap MakerNote into Exif.
- `tools/apple_template_writer.py` can rebuild Apple-template parity files while replacing primary tiles, gain map tiles, styledeltamap tiles, linearthumbnail payload, style bplist, and Exif payload.
- `tools/heif_dump.py` parses item roles, references, properties, payload extents, `auxC`, `hvcC`, `tmap`, `ipma`, `iref`, and `iloc`.
- `tools/styledeltamap_diagnostics.py` decodes aux images with `heif-convert --with-aux` and reports image statistics plus base-luma correlations.
- Plain `python` is not available in this shell; `python3` is available. Plain `python3 -m pytest` currently lacks installed pytest. `heif-convert`, `heif-info`, `exiftool`, `ffmpeg`, `MP4Box`, `swift`, and `x265` are available.

## Candidate Information Sources

The run must record each candidate even when a given variant only modifies a subset:

| Candidate | Current source in HEIF | Automated evidence | Manual Photos evidence |
|---|---|---|---|
| Primary/base image | Primary grid and tile children | role ID, tile hashes, decoded primary stats | Does response follow neutralized base or original structure? |
| Linear thumbnail | `tag:apple.com,2023:photo:aux:linearthumbnail` | role ID, payload hash, `hvcC`, NAL profile, decoded stats | Does response follow neutral/shifted/rotated thumbnail? |
| Styledeltamap | `tag:apple.com,2023:photo:aux:styledeltamap` grid and tile children | role ID, child hashes, decoded stats | Does response follow neutral/shifted/rotated styledeltamap? |
| HDR gain map | `urn:com:apple:photo:2020:aux:hdrgainmap` grid and children | role ID, child hashes, decoded stats | Does response follow HDR gain map changes? |
| Tone map item | `tmap` item payload and `dimg` references | role ID, payload hash, refs | Does response vanish or change when tmap payload is swapped/neutralized? |
| Style metadata bplist | URI `tag:apple.com,2023:photo:metadata:styles` | payload hash, plist key summary, binary key hashes | Does response follow donor metadata? |
| EXIF/MakerNote | `Exif` item, MakerApple private subpayload | payload hash, optional MakerNote hash/diff | Does response follow donor MakerNote or neutralized metadata? |
| Item graph associations | `iref`, `ipma`, `auxl`, `dimg`, `cdsc` | role IDs, refs, property associations | Does UI activation survive role-preserving payload edits? |
| Semantic sky matte | `urn:com:apple:photo:2020:aux:semanticskymatte` | payload hash, decoded black/white stats | Reproduce black/white no-obvious-difference observation. |
| Other payloads | Any role not classified above | item inventory and hash diff | Flag for later if all listed candidates fail. |

## Experiment Matrix

Minimum implemented variants:

| Output name | Mutation | Expected automatic result | Expected manual signal |
|---|---|---|---|
| `baseline_original.heic` | Copy activating baseline | zero hard warnings, original hashes | UI activates and known behavior remains |
| `neutral_base_only.heic` | Replace primary tile family with neutral gray | primary hashes differ only | If response follows base, structure should flatten |
| `neutral_styledeltamap_only.heic` | Replace styledeltamap tile family with neutral map | styledeltamap child hashes differ only | If response follows styledeltamap, structure should flatten |
| `neutral_linearthumb_only.heic` | Replace linearthumbnail with neutral Main10 image | linearthumb hash and `hvcC` differ only | If response follows linearthumb, structure should flatten |
| `neutral_base_styledelta_linearthumb.heic` | Neutralize base, styledeltamap, and linearthumbnail | three role families differ | Tests friend's residual-structure observation |
| `sky_matte_black.heic` | Replace sky matte with black image | sky matte hash differs, decoded mean near 0 | Should match friend's no-obvious-difference observation if sky not key |
| `sky_matte_white.heic` | Replace sky matte with white image | sky matte hash differs, decoded mean near 255 | Same as above |
| `linearthumb_shift_x.heic` | Replace linearthumbnail with shifted image | linearthumb hash differs, decoded stats similar | If source is linearthumb, response shifts horizontally |
| `styledelta_shift_x.heic` | Replace styledeltamap with shifted decoded source or shifted neutral-pattern diagnostic | styledeltamap child hashes differ | If source is styledeltamap, response shifts horizontally |
| `bplist_swapped_only.heic` | Swap style metadata item from a donor HEIC | style metadata hash differs only | If source is bplist metadata, response follows donor metadata |

Optional variants if the narrow helper supports them without broad writer changes:

- `gainmap_neutral.heic`
- `tmap_swapped_only.heic`
- `makernote_swapped_only.heic`
- `linearthumb_rot90.heic`
- `styledelta_rot90.heic`
- `metadata_swapped_only.heic`

## Automatic Verification Items

For every output HEIC:

- `tools/heif_dump.py` JSON and Markdown.
- `tools/semantic_fitter.py` JSON and Markdown where role requirements are satisfied.
- `heif-info` exit status and log.
- `heif-convert --with-aux --no-colons` extraction when available.
- `tools/styledeltamap_diagnostics.py` JSON/Markdown for decoded primary and aux stats.
- Payload family hashes for primary, styledeltamap, HDR gain map, sky matte, linearthumbnail, `tmap`, style bplist, and Exif.
- Item graph references and property associations.
- Manifest fields for input baseline, donor, role IDs, replacement item type, payload hashes before/after, perturbation type, output path, automated validation, and manual Photos fields.

## Manual Apple Photos Table

The run README must include this table with blank fields for the operator:

| Variant | Imports into Photos | Styles UI activates | Tone slider response | Color slider response | Spatial response follows original | Spatial response follows modified payload | Low-frequency only | No response | Notes |
|---|---|---|---|---|---|---|---|---|---|
| baseline_original.heic |  |  |  |  |  |  |  |  |  |
| neutral_base_only.heic |  |  |  |  |  |  |  |  |  |
| neutral_styledeltamap_only.heic |  |  |  |  |  |  |  |  |  |
| neutral_linearthumb_only.heic |  |  |  |  |  |  |  |  |  |
| neutral_base_styledelta_linearthumb.heic |  |  |  |  |  |  |  |  |  |
| sky_matte_black.heic |  |  |  |  |  |  |  |  |  |
| sky_matte_white.heic |  |  |  |  |  |  |  |  |  |
| linearthumb_shift_x.heic |  |  |  |  |  |  |  |  |  |
| styledelta_shift_x.heic |  |  |  |  |  |  |  |  |  |
| bplist_swapped_only.heic |  |  |  |  |  |  |  |  |  |

## Risks, Counterexamples, and Loopholes

- A HEIC can be structurally valid and still not activate Photos styles.
- Photos UI activation does not locate the spatial source.
- Tone/color sliders can respond globally without proving spatial response.
- If neutralization re-encodes a payload with non-Apple codec settings, a failure may be caused by codec/profile mismatch, not source semantics.
- Neutralizing `styledeltamap` does not prove "no style information"; 8-bit 128 and 10-bit 512 neutrality must be recorded separately.
- Sky matte is only one semantic matte. Any other visible semantic/aux item in dumps must stay in the candidate inventory.
- Replacing primary/base may change Exif dimensions, derived transforms, or Photos heuristics. The manifest must report this.
- Swapping style bplist or MakerNote from a different scene may break internal consistency rather than reveal source influence.
- If all listed payload families are neutralized and structure remains, residual response could still come from Photos cache, undocumented metadata, item graph order, or other Apple private payloads.

## Not Doing In This Round

- No in-place modification of source samples.
- No committing generated HEIC files under `artifacts/`.
- No claim that automatic diagnostics prove Apple Photos spatial behavior.
- No forced full-size 50MP to 12MP downscale as the main preserve-base route.
- No broad rewrite of `inject_style_family.py` or `apple_template_writer.py`.
- No hand-authored HEIF box parser replacement.

## Files To Create Or Modify

- Create `tools/style_spatial_ablation.py`
  - Reads a baseline HEIC and optional donor HEIC.
  - Builds role inventory from `tools.heif_dump.parse_file`.
  - Produces variant HEIC files by replacing selected payload families while preserving item graph where possible.
  - Runs diagnostics and writes manifest/README.

- Create `tests/test_style_spatial_ablation.py`
  - Unit tests manifest shape, role lookup, payload family hashing, and dry-run/fixture mutation behavior.
  - Tests use synthetic in-memory payload maps where possible and skip expensive HEVC subprocess work.

- Create `docs/photographic-style-spatial-source-ablation-20260602.md`
  - Final research report with evidence grades: proven, strong evidence, weak/manual pending, excluded, unknown.

- Modify `README.md`
  - Add a short link to the new ablation workflow and report.

## Task 1: Add Ablation Unit Tests First

**Files:**
- Create: `tests/test_style_spatial_ablation.py`
- Target production file: `tools/style_spatial_ablation.py`

- [ ] **Step 1: Write failing tests**

Test cases:

```python
def test_role_inventory_finds_expected_apple_template_items():
    from pathlib import Path
    from tools.style_spatial_ablation import build_role_inventory

    inventory = build_role_inventory(Path("Apple_Native_Samples/IMG_0032.HEIC"))

    assert inventory["primary"].item_id == 49
    assert inventory["styledeltamap"].item_id == 81
    assert inventory["hdrgainmap"].item_id == 94
    assert inventory["semanticskymatte"].item_id == 95
    assert inventory["linearthumbnail"].item_id == 97
    assert inventory["tmap"].item_id == 100
    assert inventory["style_metadata"].item_id == 101
    assert inventory["exif"].item_id == 102
```

```python
def test_manifest_entry_records_manual_photos_fields():
    from pathlib import Path
    from tools.style_spatial_ablation import build_manual_photos_fields, manifest_entry

    entry = manifest_entry(
        name="neutral_linearthumb_only",
        output=Path("out/neutral_linearthumb_only.heic"),
        perturbation="neutral",
        changed_roles=["linearthumbnail"],
        validation={"heif_dump": {"ok": True}},
    )

    assert entry["name"] == "neutral_linearthumb_only"
    assert entry["changed_roles"] == ["linearthumbnail"]
    assert entry["manual_photos_verification"] == build_manual_photos_fields()
```

```python
def test_payload_hash_summary_marks_changed_and_preserved_roles():
    from tools.style_spatial_ablation import compare_role_hashes

    before = {"primary": "aaa", "linearthumbnail": "bbb"}
    after = {"primary": "aaa", "linearthumbnail": "ccc"}

    assert compare_role_hashes(before, after) == {
        "primary": {"before": "aaa", "after": "aaa", "changed": False},
        "linearthumbnail": {"before": "bbb", "after": "ccc", "changed": True},
    }
```

- [ ] **Step 2: Run tests and verify RED**

Run:

```bash
python3 -m unittest tests.test_style_spatial_ablation -v
```

Expected: import failure because `tools.style_spatial_ablation` does not exist.

## Task 2: Implement Core Manifest And Role Inventory

**Files:**
- Create: `tools/style_spatial_ablation.py`
- Test: `tests/test_style_spatial_ablation.py`

- [ ] **Step 1: Implement dataclasses and role lookup**

Add a narrow module with:

```python
@dataclass(frozen=True)
class RoleInfo:
    role: str
    item_id: int
    item_type: str | None
    aux_type: str | None
    dimensions: dict[str, int] | None
    child_item_ids: list[int]
```

and functions:

```python
def build_role_inventory(path: Path) -> dict[str, RoleInfo]: ...
def build_manual_photos_fields() -> dict[str, str | bool | None]: ...
def manifest_entry(name: str, output: Path, perturbation: str, changed_roles: list[str], validation: dict[str, Any]) -> dict[str, Any]: ...
def compare_role_hashes(before: dict[str, str | None], after: dict[str, str | None]) -> dict[str, dict[str, Any]]: ...
```

- [ ] **Step 2: Run tests and verify GREEN**

Run:

```bash
python3 -m unittest tests.test_style_spatial_ablation -v
```

Expected: tests pass.

## Task 3: Implement Payload Replacement Writer

**Files:**
- Modify: `tools/style_spatial_ablation.py`
- Test: `tests/test_style_spatial_ablation.py`

- [ ] **Step 1: Add a failing test for byte-preserving baseline copy**

Test behavior:

```python
def test_baseline_copy_is_byte_identical(tmp_path):
    from pathlib import Path
    from tools.style_spatial_ablation import copy_baseline_variant

    source = Path("Apple_Native_Samples/IMG_0032.HEIC")
    output = tmp_path / "baseline_original.heic"

    copy_baseline_variant(source, output)

    assert output.read_bytes() == source.read_bytes()
```

- [ ] **Step 2: Add writer helpers**

Use existing `tools.inject_style_family.load_heif` and `tools.heif_aux_writer._box/_full_box/_u16/_u32/_u64` patterns to rebuild `ftyp + meta + mdat` after changing payload bytes. Preserve item IDs and references unless the caller explicitly asks for a donor swap.

Core functions:

```python
def copy_baseline_variant(source: Path, output: Path) -> None: ...
def write_with_replaced_payloads(source: Path, output: Path, replacements: dict[int, bytes]) -> None: ...
```

- [ ] **Step 3: Run tests**

Run:

```bash
python3 -m unittest tests.test_style_spatial_ablation -v
```

Expected: tests pass.

## Task 4: Implement Image Perturbation Generators

**Files:**
- Modify: `tools/style_spatial_ablation.py`
- Test: `tests/test_style_spatial_ablation.py`

- [ ] **Step 1: Add tests for neutral and shift operations on small images**

Use Pillow images and assert:

- neutral RGB returns one unique value.
- horizontal shift preserves dimensions and changes edge pixels.
- black/white sky matte generators produce expected extrema.

- [ ] **Step 2: Implement generators**

Functions:

```python
def neutral_rgb_image(size: tuple[int, int], value: int = 128) -> Image.Image: ...
def black_l_image(size: tuple[int, int]) -> Image.Image: ...
def white_l_image(size: tuple[int, int]) -> Image.Image: ...
def shift_image_x(image: Image.Image, pixels: int) -> Image.Image: ...
```

Encoding helpers:

```python
def encode_primary_neutral_tile_family(reference: LoadedHeif, primary: RoleInfo) -> dict[int, bytes]: ...
def encode_styledeltamap_tile_family(image: Image.Image, role: RoleInfo) -> dict[int, bytes]: ...
def encode_linearthumbnail_image(image: Image.Image) -> tuple[bytes, bytes]: ...
def encode_sky_matte_image(image: Image.Image) -> tuple[bytes, bytes]: ...
```

For linearthumbnail, prefer VideoToolbox if available because prior work found the 105-byte Apple-like `hvcC` profile activation-sensitive; allow `--linearthumb-encoder x265` fallback and record the fallback as a codec confound in the manifest.

## Task 5: Implement CLI Run Generation

**Files:**
- Modify: `tools/style_spatial_ablation.py`

- [ ] **Step 1: Add CLI options**

CLI:

```bash
python3 tools/style_spatial_ablation.py \
  --baseline artifacts/constructed/apple_style_injected_from_preview_heic_v1/apple_style_injected_from_preview_heic_v1.heic \
  --donor Apple_Native_Samples/IMG_0033.HEIC \
  --output-root artifacts/style_spatial_ablation \
  --run-id 20260602_manual_probe \
  --linearthumb-encoder videotoolbox
```

- [ ] **Step 2: Generate required variants**

The CLI must generate at least:

- `baseline_original.heic`
- `neutral_base_only.heic`
- `neutral_styledeltamap_only.heic`
- `neutral_linearthumb_only.heic`
- `neutral_base_styledelta_linearthumb.heic`
- `sky_matte_black.heic`
- `sky_matte_white.heic`
- `linearthumb_shift_x.heic`
- `styledelta_shift_x.heic`
- `bplist_swapped_only.heic`

- [ ] **Step 3: Write manifest and README**

Outputs:

- `artifacts/style_spatial_ablation/<run_id>/manifest.json`
- `artifacts/style_spatial_ablation/<run_id>/README.md`
- per-HEIC `*.heif_dump.json`
- per-HEIC `*.heif_dump.md`
- per-HEIC `*.semantic.json` and `*.semantic.md` where possible
- per-HEIC aux diagnostic JSON/Markdown
- decoded aux PNGs where `heif-convert` is available

## Task 6: Generate Real Sample Run And Reports

**Files:**
- Create generated artifacts under ignored `artifacts/style_spatial_ablation/<run_id>/`
- Create: `docs/photographic-style-spatial-source-ablation-20260602.md`
- Modify: `README.md`

- [ ] **Step 1: Generate run**

Run:

```bash
python3 tools/style_spatial_ablation.py \
  --baseline artifacts/constructed/apple_style_injected_from_preview_heic_v1/apple_style_injected_from_preview_heic_v1.heic \
  --donor Apple_Native_Samples/IMG_0033.HEIC \
  --output-root artifacts/style_spatial_ablation \
  --run-id 20260602_v1_source_ablation \
  --linearthumb-encoder videotoolbox
```

- [ ] **Step 2: Run full available verification**

Run at minimum:

```bash
python3 -m unittest tests.test_style_spatial_ablation -v
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 -m pytest tests/ -v
python3 -m compileall tools tests
git diff --check
```

Record pytest as an environment limitation if it is still unavailable on the plain interpreter.

- [ ] **Step 3: Write final research report**

Report sections:

- Executive summary
- What is proven automatically
- Strong evidence supported by existing prior user Photos observation
- Weak/manual pending findings
- Excluded or likely low-priority candidates
- Still unknown
- Response to friend's claims
- Next best experiments
- Verification log and environment limitations

## Self-Review Checklist

- [ ] The plan covers every requested candidate source at least as an inventory item.
- [ ] The minimum required variants are generated.
- [ ] The manifest includes manual Photos fields and never marks them complete automatically.
- [ ] HEIF source files are never modified in place.
- [ ] Large HEIC artifacts remain under ignored `artifacts/`.
- [ ] Automatic report wording does not overclaim Photos behavior.
- [ ] The final report explicitly answers whether the friend's three claims are supported, reproducible, excluded, or still pending.
