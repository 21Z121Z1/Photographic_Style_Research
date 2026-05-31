# ISO Auxiliary Styledeltamap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and validate a standards-based HEIF file containing a primary HEVC image item and an experimental Apple styledeltamap auxiliary image represented as a grid-derived image with HEVC tile children.

**Architecture:** Use `pillow_heif` only as a single-image HEVC payload encoder. Extract each encoded image item's `hvcC` property and `mdat` item payload, then assemble the final `ftyp`, file-level `meta`, `idat`/`mdat`, `iinf`, `iloc`, `iprp`, `ipco`, `ipma`, and `iref` boxes with local ISOBMFF code. Keep styledeltamap raster generation experimental and separately documented.

**Tech Stack:** Python 3, Pillow, pillow-heif, NumPy, macOS `sips`, local `heif-info` / `heif-convert`, existing `tools/heif_dump.py`, `unittest`.

---

## Evidence And Scope

- MP4RA currently registers `auxl` as the HEIF auxiliary image item reference and `dimg` as the derived image reference. Public ISO/IEC 23008-12:2025/Amd 1 excerpts also say auxiliary images link to master images with `auxl`.
- Some secondary texts use `aux1`; that conflicts with the current registry and local Apple dumps. This plan uses `auxl` for the ISO-conformant writer and documents the naming trap.
- Apple-native samples in this workspace store `tag:apple.com,2023:photo:aux:styledeltamap` as a `grid` derived image item with `auxC`, `pixi=[10,10,10]`, `ispe`, `colr`, and `dimg` references to HEVC tile children.
- The first generated artifact is not expected to activate Apple Photos UI. It must prove a real HEIF auxiliary image graph, not just a multi-image HEIC.
- `tmap` is intentionally out of scope unless valid ISO 21496-1 gain map metadata and a gain map image item are available.

## Files

- Create `tools/heif_aux_writer.py`: low-level ISOBMFF box builders, single-image HEVC extraction, candidate-map tiling, and final HEIF assembly.
- Modify `tools/proraw_residual_probe.py`: expose reusable candidate styledeltamap generation functions and CLI output for neutral, luma residual, and chroma/luma residual maps.
- Modify `tools/heif_dump.py`: preserve `iloc` data when `iinf` appears after `iloc`, parse `idat` construction-method extents, expose item hidden flags, and include validation helpers for styledeltamap auxiliary graphs.
- Create `tests/test_heif_aux_writer.py`: unit tests for box structure, `auxC`, `auxl`, `dimg`, grid item payload, and negative multi-image distinction.
- Modify `tests/test_heif_dump.py`: regression coverage for `iloc` before `iinf`, `idat` extents, `auxl`, and grid-derived payload accounting.
- Create `docs/iso_aux_styledeltamap_writer.md`: implementation notes, usage, validation results, and boundaries between ISO aux structure, Apple-like grid shape, and Photos UI compatibility.
- Generate artifacts under `artifacts/constructed/iso_aux_styledeltamap/`.

## Tasks

### Task 1: Strengthen HEIF Dump Parser

- [ ] Write failing tests for `iloc` appearing before `iinf`, preserving extents after later item info parsing.
- [ ] Write failing tests for `construction_method=1` item data stored in `meta/idat`.
- [ ] Implement non-destructive item merging in `parse_heif()`.
- [ ] Track `idat` payload base offsets and resolve `construction_method=1` extents to absolute file offsets for extraction.
- [ ] Parse and report hidden item flags from `infe.flags`.
- [ ] Run `python3 -m unittest tests/test_heif_dump.py -v`.

### Task 2: Candidate Map Generation

- [ ] Write failing tests that neutral, luma residual, and chroma/luma residual map generators produce neutral-centered `uint8` RGB maps and JSON-safe stats.
- [ ] Refactor `tools/proraw_residual_probe.py` to expose `generate_candidate_maps(high_rgb, base_rgb)`.
- [ ] Add CLI output of `.npy`, PNG preview, stats JSON, and Markdown report per candidate.
- [ ] Keep all algorithm wording experimental and compare stats against native Apple diagnostics: near 128, low amplitude, few unique values, weak luma correlation.
- [ ] Run `python3 -m unittest tests/test_proraw_residual_probe.py -v`.

### Task 3: Low-Level HEIF Auxiliary Writer

- [ ] Write failing tests that construct an in-memory HEIF with:
  - `ftyp` major brand `heic`, compatible brands including `mif1`, `heic`, `miaf`.
  - file-level `meta` with `hdlr=pict`, `pitm` pointing to the primary item, `iinf`, `iloc`, `iprp/ipco/ipma`, `iref`, and `idat`.
  - primary item type `hvc1` with `hvcC/ispe/pixi/colr`.
  - styledeltamap item type `grid` with `auxC/ispe/pixi/colr`.
  - HEVC tile child items type `hvc1` with `hvcC/ispe/pixi/colr`.
  - `dimg` from styledeltamap grid to tile children.
  - `auxl` from styledeltamap grid to primary.
- [ ] Implement reusable box builders for `ftyp`, `meta`, `hdlr`, `pitm`, `iinf`, `iloc`, `iprp`, `ipco`, `ipma`, `iref`, `idat`, and `mdat`.
- [ ] Implement grid descriptor payload as `version=0`, `flags=0`, `rows_minus_one`, `columns_minus_one`, `output_width`, `output_height`.
- [ ] Implement `pillow_heif` single-image extraction without depending on multi-image final output.
- [ ] Add CLI:
  - `--dng-root`
  - `--sample`
  - `--candidate neutral|luma_residual|chroma_luma_residual`
  - `--mode apple-like-grid`
  - `--output artifacts/constructed/iso_aux_styledeltamap/iso_aux_styledeltamap.heic`
  - `--tile-size`
  - `--max-dim`
  - `--quality`
- [ ] Run `python3 -m unittest tests/test_heif_aux_writer.py -v`.

### Task 4: Generate And Validate Artifact

- [ ] Generate candidate diagnostics from the DNG/JPG pair directory.
- [ ] Generate `artifacts/constructed/iso_aux_styledeltamap/iso_aux_styledeltamap.heic`.
- [ ] Dump it with:
  `python3 tools/heif_dump.py artifacts/constructed/iso_aux_styledeltamap/iso_aux_styledeltamap.heic --json artifacts/constructed/iso_aux_styledeltamap/iso_aux_styledeltamap.heif.json --md artifacts/constructed/iso_aux_styledeltamap/iso_aux_styledeltamap.heif.md --extract-items artifacts/constructed/iso_aux_styledeltamap/items`
- [ ] Run `heif-info artifacts/constructed/iso_aux_styledeltamap/iso_aux_styledeltamap.heic`.
- [ ] Try `heif-convert --with-aux --no-colons` and document whether external tooling decodes the private styledeltamap aux type.
- [ ] Confirm the dumper reports:
  - exactly one primary item via `pitm`
  - primary item type `hvc1`
  - styledeltamap item type `grid`
  - `auxC` value `tag:apple.com,2023:photo:aux:styledeltamap`
  - `auxl` reference from styledeltamap to primary
  - `dimg` references from styledeltamap grid to HEVC tile children
  - required properties on primary, grid, and child tiles

### Task 5: Documentation And Confidence Loop

- [ ] Write `docs/iso_aux_styledeltamap_writer.md` with usage, structure, validation commands, observed external-tool behavior, and non-goals.
- [ ] Run full local verification:
  - `python3 -m unittest discover -s tests -v`
  - `python3 tools/heif_dump.py ...`
  - `heif-info ...`
  - `heif-convert --with-aux --no-colons ...`
- [ ] Self-audit every acceptance criterion. If any claim is unsupported, either fix it or document the exact failure mode.
- [ ] Do not claim Apple Photos compatibility unless a separate Photos/ImageIO validation proves it.
