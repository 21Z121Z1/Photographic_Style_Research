# Apple Linearthumbnail Parity Plan - 2026-05-31

## Goal

`v5_style_safe` keeps Apple Photos style controls working while `v5` does not. The only intended difference in that comparison is the generated `linearthumbnail` auxiliary item, so this milestone targets item-level and bitstream-level parity for Apple private `linearthumbnail` before continuing styledeltamap semantic fitting.

The active goal tool already contains the prior semantic-fitting objective and cannot be rewritten in place. This plan is the current execution boundary for the renewed goal.

## Current Evidence

Corpus: 85 files in `Apple_Native_Samples/*.HEIC`.

Observed Apple native `linearthumbnail` profile:

- 84 of 85 samples contain `auxC = tag:apple.com,2023:photo:aux:linearthumbnail`.
- The missing sample, `IMG_2911.HEIC`, appears to be a non-style/HDR-only capture and is excluded from linearthumbnail parity.
- Item type is `hvc1`.
- Dimensions are normally `1024x768`; portrait storage variants use `768x1024`.
- `pixi` is always `[10, 10, 10]`.
- `hvcC` parsed profile is always Main 10, profile_idc 2, level_idc 93, 4:2:0, 10-bit luma/chroma.
- Apple sample `IMG_0032.HEIC` and high-payload sample `IMG_2899.HEIC` have byte-identical 105-byte `hvcC` records for linearthumbnail.
- The item reference is `auxl` from linearthumbnail to both primary grid and tone-map item. MP4RA currently registers `auxl` as the HEIF auxiliary image item reference, so `auxl` is the standard reference spelling to match.
- Native linearthumbnail item payloads inspected so far contain exactly one length-prefixed HEVC NAL unit, type 20 (`IDR_N_LP`), and no in-item VPS/SPS/PPS/SEI NAL units.
- Native linearthumbnail IDR payload size in the local corpus ranges from 4485 to 70948 bytes.

Current generated `v5` linearthumbnail mismatch:

- Payload NAL types are `[32, 33, 34, 39, 20, 1]`.
- That means the item payload includes VPS, SPS, PPS, prefix SEI, IDR, and a trailing non-IDR VCL NAL.
- `hvcC` is 110 bytes and byte-different from Apple native item97 `hvcC`.
- Pixel/statistical tuning alone is therefore not a sufficient explanation. The stronger root cause is that generated `v5` is not the same HEIF item data type Apple emits for private `linearthumbnail`.

## External Reference Check

- MP4RA item reference registry lists `auxl` as "Auxiliary image item reference" for HEIF.
- Apple public Image I/O exposes auxiliary-data insertion/extraction APIs for depth and mattes, but does not expose the private styledeltamap or linearthumbnail semantics.
- Apple Vision can generate person segmentation masks through `VNGeneratePersonSegmentationRequest`; this is useful for future person matte candidates, not for proving linearthumbnail parity.

## Implementation Strategy

### 1. Add reusable HEVC NAL inspection

Add helpers to `tools/hevc10_encoder.py`:

- parse Annex B NALs;
- parse length-prefixed HEVC NALs;
- extract a first-frame payload in two policies:
  - existing multi-NAL first-frame behavior for current styledeltamap experiments;
  - Apple still-image item behavior: keep only the first IDR NAL and emit it as one length-prefixed NAL.

The default behavior should remain compatible with existing callers. The generated linearthumbnail path should opt in to the Apple policy.

### 2. Add linearthumbnail native profile checks

Add tests that prove:

- `Apple_Native_Samples/IMG_0032.HEIC` linearthumbnail payload has exactly one NAL type 20;
- the native linearthumbnail `hvcC` payload is 105 bytes and Main 10 level 93;
- the generated Apple-linearthumb encoder policy emits no parameter sets or SEI in the item payload.

If runtime cost is acceptable, add a corpus-oriented test or tool that profiles all local Apple samples and documents any exceptions.

### 3. Generate two controlled candidates

Build controlled candidates so the risk is explicit:

- `v6_stripped_own_hvcc`: generated linearthumbnail payload is single-IDR, but the `hvcC` remains the encoder-produced record.
- `v6_apple_hvcc`: generated linearthumbnail payload is single-IDR and the linearthumbnail `hvcC` property is copied from the Apple template.
- `v7_vt_linearthumb`: generated linearthumbnail is encoded through Apple VideoToolbox Main10 so the item gets a 105-byte Apple-family `hvcC`.
- `v8_vt_linearthumb_q025`: same VideoToolbox path, but quality is tuned down so the IDR payload size falls in the observed Apple native item97 range.

Expected result:

- `v6_stripped_own_hvcc` should decode if the encoder hvcC matches the generated IDR.
- `v6_apple_hvcc` is structurally closer to Apple, but may fail external decode if the generated x265 IDR does not match the Apple template parameter sets. This must be tested, not assumed.
- `v7_vt_linearthumb` should prove the Apple-family codec record and one-IDR item layout.
- `v8_vt_linearthumb_q025` is the preferred candidate if it keeps the same item data type while matching native payload scale.

### 4. Extend semantic reports

Update `tools/semantic_fitter.py` so reports include for key hvc1 items:

- linearthumbnail payload NAL count and NAL types;
- `hvcC` raw byte length and SHA-256;
- hard warning if linearthumbnail is generated but contains parameter sets or SEI in the item payload.

This makes future Photos UI failures easier to separate into container/codec mismatch versus private semantic payload mismatch.

### 5. Optional Apple ML matte path

Do not block this linearthumbnail milestone on sky/person matte generation.

If the item97 parity fix still fails Photos style controls, add a separate Apple-framework candidate path:

- person matte: Vision `VNGeneratePersonSegmentationRequest`;
- portrait matte: Image I/O / AVFoundation auxiliary matte APIs when source data exists;
- sky matte: only use an Apple framework path if a stable public API is available locally. Do not invent a private sky matte payload and call it Apple-equivalent.

## Validation Commands

Run at minimum:

```bash
python3 -m unittest tests.test_apple_template_writer tests.test_semantic_fitter -v
python3 -m unittest discover -s tests -v
python3 tools/heif_dump.py artifacts/constructed/apple_parity_styledeltamap_v6_*/apple_parity_styledeltamap_*.heic --json ... --md ...
python3 tools/semantic_fitter.py ... --json ... --md ...
heif-info artifacts/constructed/apple_parity_styledeltamap_v6_*/apple_parity_styledeltamap_*.heic
heif-convert artifacts/constructed/apple_parity_styledeltamap_v6_*/apple_parity_styledeltamap_*.heic ...png
```

Use `sips`, ImageIO Swift probes, or Photos import only after the structural and external decode gates pass.

The final candidate path for this milestone is expected to be:

```bash
artifacts/constructed/apple_parity_styledeltamap_v8_vt_linearthumb_q025/apple_parity_styledeltamap_v8_vt_linearthumb_q025.heic
```

## Completion Standard

I cannot claim 100% Apple Photos compatibility from parser-only evidence. Completion for this milestone requires:

- local parser reports linearthumbnail `auxC`;
- linearthumbnail `auxl` references primary and tmap as Apple samples do;
- linearthumbnail has `ispe`, `pixi`, `colr`, `hvcC`, and correct orientation associations inherited from the template graph;
- linearthumbnail item payload is one length-prefixed IDR NAL, no VPS/SPS/PPS/SEI in item payload;
- linearthumbnail payload size is in the Apple native item97 scale, not only structurally valid;
- `semantic_fitter` reports this explicitly;
- external HEIF tools still accept/decode the file, or a documented reason explains which exact variant is structural-only.
