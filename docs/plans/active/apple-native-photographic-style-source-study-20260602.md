# Apple Native Photographic Style Source Study Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Build a read-only, machine-readable evidence base for `Apple_Native_Samples` that identifies Photographic Styles HEIF item/aux/metadata sources and ranks the next perturbation targets.

**Architecture:** Reuse `tools/heif_dump.py` as the graph parser and add narrow corpus tools that summarize roles, payload hashes, decoded diagnostic statistics, and cross-sample structure diffs. Original samples remain untouched; all generated dumps, PNG diagnostics, CSVs, JSON, and reports go under `artifacts/apple_native_samples/<run_id>/`.

**Tech Stack:** Python 3, `tools.heif_dump`, `Pillow`, `numpy`, `plistlib`, `heif-convert`, `heif-info`, `exiftool`, `unittest`/`pytest`.

---

## Friend Experiment Summary

- Replacing the primary/base image with an SDR middle-gray image does not fully explain the remaining Photos tone/color spatial response.
- `linearthumbnail` affects Photos behavior, but current evidence says it is not sufficient as the sole spatial source.
- When both `styledeltamap` and base are neutralized, style response becomes lower-frequency and smoother.
- Even after neutralizing the entire `linearthumbnail`, Photos can still preserve some original-scene brightness/structure response.
- The likely remaining sources are other HEIF items, metadata payloads, MakerApple/MakerNote, `tmap`, HDR gain map, or hidden/unknown item graph relationships.
- Sky matte black/white tests reportedly made no obvious difference, so sky matte starts as a low-priority candidate unless the native corpus shows strong style-metadata coupling.

## Research Scope

Primary scope is the local directory:

`/Users/retriedstormtrooper/Documents/styledeltamap/Apple_Native_Samples`

This pass must first produce native-corpus evidence, then only add minimal ablation plans or manifests if evidence remains ambiguous. It must not generate a large synthetic HEIC set and must not modify original Apple samples.

## Apple_Native_Samples Inventory Seed

Initial directory audit found 85 HEIC files:

`IMG_0032.HEIC`, `IMG_0033.HEIC`, `IMG_2878.HEIC`, `IMG_2879.HEIC`, `IMG_2881.HEIC`, `IMG_2882.HEIC`, `IMG_2883.HEIC`, `IMG_2884.HEIC`, `IMG_2885.HEIC`, `IMG_2886.HEIC`, `IMG_2887.HEIC`, `IMG_2888.HEIC`, `IMG_2889.HEIC`, `IMG_2890.HEIC`, `IMG_2891.HEIC`, `IMG_2892.HEIC`, `IMG_2893.HEIC`, `IMG_2894.HEIC`, `IMG_2895.HEIC`, `IMG_2896.HEIC`, `IMG_2897.HEIC`, `IMG_2898.HEIC`, `IMG_2899.HEIC`, `IMG_2900.HEIC`, `IMG_2901.HEIC`, `IMG_2902.HEIC`, `IMG_2903.HEIC`, `IMG_2904.HEIC`, `IMG_2905.HEIC`, `IMG_2906.HEIC`, `IMG_2907.HEIC`, `IMG_2908.HEIC`, `IMG_2909.HEIC`, `IMG_2910.HEIC`, `IMG_2911.HEIC`, `IMG_2912.HEIC`, `IMG_2913.HEIC`, `IMG_2914.HEIC`, `IMG_2915.HEIC`, `IMG_2916.HEIC`, `IMG_2917.HEIC`, `IMG_2918.HEIC`, `IMG_2919.HEIC`, `IMG_2920.HEIC`, `IMG_2921.HEIC`, `IMG_2922.HEIC`, `IMG_2923.HEIC`, `IMG_2924.HEIC`, `IMG_2925.HEIC`, `IMG_2926.HEIC`, `IMG_2927.HEIC`, `IMG_2928.HEIC`, `IMG_2929.HEIC`, `IMG_2930.HEIC`, `IMG_2931.HEIC`, `IMG_2932.HEIC`, `IMG_2933.HEIC`, `IMG_2934.HEIC`, `IMG_2935.HEIC`, `IMG_2936.HEIC`, `IMG_2937.HEIC`, `IMG_2938.HEIC`, `IMG_2939.HEIC`, `IMG_2940.HEIC`, `IMG_2941.HEIC`, `IMG_2942.HEIC`, `IMG_2943.HEIC`, `IMG_2944.HEIC`, `IMG_2945.HEIC`, `IMG_2946.HEIC`, `IMG_2947.HEIC`, `IMG_2948.HEIC`, `IMG_2949.HEIC`, `IMG_2950.HEIC`, `IMG_2951.HEIC`, `IMG_2952.HEIC`, `IMG_2953.HEIC`, `IMG_2954.HEIC`, `IMG_2955.HEIC`, `IMG_2956.HEIC`, `IMG_2957.HEIC`, `IMG_2958.HEIC`, `IMG_2959.HEIC`, `IMG_2960.HEIC`, `IMG_2961.HEIC`.

Initial classification:

- `IMG_0032.HEIC` and `IMG_0033.HEIC`: previously studied Apple-native references with `styledeltamap`, HDR gain map, semantic sky matte, `linearthumbnail`, style bplist URI item, `tmap`, and EXIF/MakerNote.
- `IMG_2878.HEIC` through `IMG_2961.HEIC`: likely Apple-native corpus expansion; must be independently classified by SHA-256, file size, primary dimensions, style aux presence, linearthumbnail presence, metadata URI, and unknown items. Do not assume every file is a style sample.
- Known exception candidate from earlier docs: `IMG_2911.HEIC` may be non-style or HDR-only; verify from this run instead of inheriting the claim.

## Existing Tool Capability

- `tools/heif_dump.py`: parses `ftyp`, `pitm`, `iinf/infe`, `iloc`, `iprp/ipco/ipma`, `ispe`, `pixi`, `auxC`, `colr`, `hvcC`, `irot`, `clap`, `iref`, `grid`, `tmap`, and derived `dimg` payload byte totals. Outputs JSON/Markdown and can extract item payloads.
- `tools/styledeltamap_diagnostics.py`: runs `heif-convert --with-aux` and summarizes decoded PNG diagnostic views with min/max/mean/std and base-luma correlation.
- `tools/semantic_fitter.py`: identifies key role items, hashes payloads, parses style bplist summaries, checks role references, and reports HEVC NAL layout for `hvc1` items.
- `tools/gainmap_sources.py`: can identify/decode Apple HDR gain map diagnostics through `heif-convert`.
- `tools/aux_generator.py`: can create linearthumbnail/styledeltamap diagnostic rasters for experiments, but should not be the first path here.
- Tests already cover the core parser and diagnostics in `tests/test_heif_dump.py`, `tests/test_styledeltamap_diagnostics.py`, `tests/test_semantic_fitter.py`, `tests/test_gainmap_sources.py`, and related builder/generator tests.

## Minimum New Tool Capability

Create focused read-only tools:

- `tools/apple_native_sample_inventory.py`
  - Parse every HEIC sample with `tools.heif_dump.parse_file`.
  - Record file path, filename, file size, SHA-256, HEIF brands, primary item/dimensions, primary bit depth/pixi/color, role items, aux types, item references, property associations, payload hashes, decoded aux stats if available, metadata summaries, and unknown items.
  - Write `inventory.json`, `inventory.md`, `sample_matrix.csv`, per-sample `heif_dump.json`, per-sample `heif_dump.md`, `item_graph_summary.json`, `unknown_items.json`, `metadata_summary.json`, `styledeltamap_stats.json`, `linearthumbnail_stats.json`, `aux_stats.json`, and `structure_diff.json`.
- Optional only if the first tool grows too broad: `tools/apple_native_item_graph_diff.py` for separate cross-sample graph grouping.
- Optional only if decoded stats become too broad: `tools/apple_native_aux_stats.py` for decoded PNG low-frequency and histogram metrics.

## Candidate Spatial Information Sources

Ranked candidates to inspect in every native sample:

1. Primary/base image tiles and primary grid structure.
2. `linearthumbnail` aux item: item id, dimensions, 10-bit profile, payload hash, NAL layout, decoded stats, correlation with base luminance.
3. `styledeltamap` aux item: item id, dimensions, 10-bit profile, payload hash, decoded stats, neutral offset, histogram, low-frequency energy, correlation with base and linearthumbnail luminance.
4. HDR gain map aux item and `tmap` relationship.
5. `/tag:apple.com,2023:photo:metadata:styles` URI bplist, especially binary keys and numeric image-stat fields.
6. EXIF/MakerApple/MakerNote payloads, especially large or stable binary regions and Apple private tags.
7. Unknown or hidden HEIF items, unusual item types, unclassified metadata, and non-sky semantic matte aux types.
8. Semantic sky matte, as a low-priority exclusion candidate unless graph or metadata coupling contradicts the friend test.

## Automatic Diagnostic Matrix

For every sample:

- Parse full HEIF dump and save JSON/Markdown.
- Group item types, aux types, reference types, property associations, item dimensions, `pixi`, `colr`, `hvcC`, payload bytes, derived payload bytes, and payload hashes.
- Identify Photographic Styles signature: `styledeltamap`, `linearthumbnail`, style metadata URI, `tmap`, EXIF/MakerNote, and style aux references to primary/tmap.
- Decode aux PNG diagnostics with `heif-convert --with-aux` when available.
- For each decoded aux PNG, record mode, dimensions, dtype, min/max/mean/std, median, neutral offset, unique values, sampled histogram, low-frequency energy ratio, and base-luma correlation.
- If both `styledeltamap` and `linearthumbnail` decode, compute luminance correlation between them.
- Record unable-to-dump and unable-to-decode failures explicitly as environment/tool limits.
- Build cross-sample groups by style signature, item count, role item ids, dimensions, aux type set, reference type set, metadata key set, and unknown item signatures.

## Minimum Manual Photos Verification Matrix

Automated file evidence cannot prove Apple Photos spatial response. The report should include a manual verification table for later Photos import/edit testing:

- Native baseline copied unchanged from 1-2 representative Apple samples.
- Neutral `styledeltamap` only.
- Neutral `linearthumbnail` only.
- Neutral primary/base only with preserve-base resolution constraint respected.
- Neutral `styledeltamap` plus neutral `linearthumbnail`.
- Neutral base plus neutral `styledeltamap` plus neutral `linearthumbnail`.
- Sky matte black and sky matte white, as low-priority controls.
- `linearthumbnail` rotate/shift.
- `styledeltamap` rotate/shift.
- One neutral/swap test for the most suspicious metadata payload after inventory evidence identifies it.

Do not generate this full set during the corpus study unless the evidence cannot rank candidates. If any ablation is created, use only 1-2 true Apple samples and preserve primary/base dimensions.

## Explicit Non-Goals

- No modification of original `Apple_Native_Samples` files.
- No large synthetic HEIC generation pass.
- No claim that a box parser proves Apple Photos UI/rendering behavior.
- No claim that decoded PNG values equal raw 10-bit HEVC payload values.
- No claim that `styledeltamap` is information-free because it appears near gray.
- No claim that sky matte is the only semantic source.
- No base image downsampling for convenience in any Photos-facing ablation.
- No committing large native samples or generated HEIC files.

## Risks and Counterexamples

- `heif-convert` may quantize 10-bit aux diagnostics to 8-bit PNG, so stats describe diagnostic views unless raw decode is later available.
- Some item roles may move across sample families; hard-coded item ids are only hints, not truth.
- Missing `linearthumbnail` in one sample may mean non-style, orientation/storage variant, or parser miss; verify by aux type and metadata, not filename.
- EXIF/MakerNote may carry private binary data that is hard to parse; record size/hash/stability rather than ignoring it.
- A candidate payload can be common to all native style samples and still not control Photos spatial response.
- Friend manual observations are important, but this run must label them as manual observations, not automated proof.

## Tasks

### Task 1: Finish Corpus Audit

**Files:**
- Read: `README.md`
- Read: `docs/*.md`
- Read: `tools/*.py`
- Read: `tests/*.py`
- Read: `Apple_Native_Samples/*.HEIC`

- [x] Confirm working directory is `/Users/retriedstormtrooper/Documents/styledeltamap`.
- [x] Confirm `README.md`, `docs/`, `tools/`, and `tests/` exist and identify relevant existing capabilities.
- [x] Confirm `Apple_Native_Samples` contains 85 `.HEIC` files.
- [x] Hash-check all samples through the inventory tool and flag exact duplicates if any.

### Task 2: Write Failing Tests for Inventory Extraction

**Files:**
- Create: `tests/test_apple_native_sample_inventory.py`
- Create: `tools/apple_native_sample_inventory.py`

- [x] Write tests that build tiny synthetic parsed HEIF dictionaries and assert role extraction for `styledeltamap`, `linearthumbnail`, HDR gain map, sky matte, `tmap`, style metadata URI, and EXIF.
- [x] Write tests for median/neutral-offset/low-frequency decoded image stats on a small image array.
- [x] Write tests for structure signatures and unknown-item classification.
- [x] Run `python3 -m unittest tests.test_apple_native_sample_inventory -v` and confirm the tests fail because the tool does not exist.

### Task 3: Implement Inventory Tool

**Files:**
- Create: `tools/apple_native_sample_inventory.py`
- Modify only if required: `tools/heif_dump.py`

- [x] Add role constants for `styledeltamap`, `linearthumbnail`, HDR gain map, sky matte, style metadata URI, and common Apple semantic aux prefixes.
- [x] Add payload extraction/hash helpers that respect existing item extents and derived `dimg` child payload bytes.
- [x] Add role extraction from aux type, item type, URI type, and primary item id.
- [x] Add decoded image stats with median, neutral offset, histogram, low-frequency energy ratio, and Pearson correlations.
- [x] Add metadata summary for style bplist and EXIF/MakerNote payload bytes/hash.
- [x] Add unknown item classification for unroleable non-primary, non-tile, non-common-metadata items.
- [x] Add CLI: `python3 tools/apple_native_sample_inventory.py Apple_Native_Samples --output-dir artifacts/apple_native_samples/<run_id>`.
- [x] Write all required JSON/Markdown/CSV artifacts.

### Task 4: Run Native Corpus Diagnostics

**Files:**
- Generate: `artifacts/apple_native_samples/20260602_native_source_study/*`

- [x] Run the new inventory tool over the entire `Apple_Native_Samples` directory.
- [x] Ensure every HEIC sample has a `heif_dump.json`.
- [x] Ensure decoded aux stats are recorded for each decodable aux payload.
- [x] Record decode failures with command output and environment reason.
- [x] Check that original sample SHA-256 values remain unchanged after the run.

### Task 5: Analyze and Report Evidence

**Files:**
- Create: `docs/apple-native-photographic-style-source-study-20260602.md`

- [x] Summarize common native structure and variants.
- [x] Rank evidence for `styledeltamap`, `linearthumbnail`, base image, HDR gain map/`tmap`, style bplist, MakerNote, sky matte, other semantic mattes, and unknown items.
- [x] Answer whether sky matte is low-priority from native graph evidence plus the friend black/white observation.
- [x] Include a next-step experiment top three list.
- [x] Include manual Photos validation table without overstating it as automated proof.

### Task 6: Verification and Self-Review

**Files:**
- Read generated artifacts and reports.

- [x] Run `python3 -m unittest tests.test_apple_native_sample_inventory -v`.
- [x] Run targeted existing parser/diagnostic tests.
- [x] Check `python3 -m pytest tests/ -v`; `pytest` was unavailable in both local Python runtimes, so full validation used `unittest discover`.
- [x] Run `python3 -m compileall tools tests`.
- [x] Run `git diff --check`.
- [x] Re-read `inventory.json`, `structure_diff.json`, and final report for unsupported claims.
- [x] Ask: do conclusions cite concrete sample names, item ids, hashes, stats, or manual-observation labels? Fix any claim that does not.
