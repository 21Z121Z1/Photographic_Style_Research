# Apple Linearthumbnail Item97 Findings - 2026-05-31

## Summary

The `v5_style_safe` versus `v5` split points to generated `linearthumbnail` as a real activation-sensitive component. The important mismatch was not only the raster content. `v5` stored item 97 as a multi-NAL HEVC access unit containing VPS/SPS/PPS/SEI/IDR/trailing VCL NALs, while Apple native `linearthumbnail` samples store the item payload as one length-prefixed IDR NAL.

The new best candidate is:

`artifacts/constructed/apple_parity_styledeltamap_v8_vt_linearthumb_q025/apple_parity_styledeltamap_v8_vt_linearthumb_q025.heic`

It uses a preencoded Apple VideoToolbox Main10 linearthumbnail stream, then injects the resulting single-IDR item payload and matching 105-byte `hvcC` into the Apple-template writer. The VideoToolbox quality is tuned to `0.25` so the generated item payload falls in the same size scale as Apple native item 97.

## Native Corpus Profile

Corpus inspected: 85 HEIC files in `Apple_Native_Samples`.

Observed linearthumbnail profile:

- 84 files contain `auxC = tag:apple.com,2023:photo:aux:linearthumbnail`.
- `IMG_2911.HEIC` does not contain this style linearthumbnail family and appears to be a non-style/HDR-only sample.
- Native linearthumbnail item type: `hvc1`.
- Native dimensions: normally `1024x768`, with orientation/storage variants in portrait captures.
- `pixi`: `[10, 10, 10]`.
- `hvcC`: Main10, profile_idc 2, level_idc 93, 4:2:0, 10-bit luma/chroma.
- Native item payload: exactly one length-prefixed HEVC NAL, type 20 (`IDR_N_LP`), no VPS/SPS/PPS/SEI inside the item payload.
- Observed native linearthumbnail IDR payload size range in the local corpus: 4485 to 70948 bytes.
- Item reference: `auxl` from linearthumbnail to primary grid item and tmap item.

## Candidate Results

### v5

`artifacts/constructed/apple_parity_styledeltamap_v5/apple_parity_styledeltamap_v5.heic`

- item 97 NAL types: `[32, 33, 34, 39, 20, 1]`.
- `hvcC`: 110 bytes.
- Result: Photos style path failed per user report.
- Diagnosis: not Apple-native linearthumbnail item payload type.

### v6_stripped_own_hvcc

`artifacts/constructed/apple_parity_styledeltamap_v6_stripped_own_hvcc/apple_parity_styledeltamap_v6_stripped_own_hvcc.heic`

- item 97 NAL types: `[20]`.
- `hvcC`: 110 bytes from x265/MP4Box.
- libheif extraction succeeds.
- Result: structurally fixed payload framing, but `hvcC` still differs from Apple native data type length.

### v6_apple_hvcc

`artifacts/constructed/apple_parity_styledeltamap_v6_apple_hvcc/apple_parity_styledeltamap_v6_apple_hvcc.heic`

- item 97 NAL types: `[20]`.
- `hvcC`: forced to the Apple template's 105-byte record.
- libheif extraction does not fail, but decoded linearthumbnail statistics are obviously wrong.
- Result: rejected. Forcing a template `hvcC` onto an x265 IDR creates a parameter-set mismatch.

### v7_vt_linearthumb

`artifacts/constructed/apple_parity_styledeltamap_v7_vt_linearthumb/apple_parity_styledeltamap_v7_vt_linearthumb.heic`

- item 97 type: `hvc1`.
- item 97 aux type: `tag:apple.com,2023:photo:aux:linearthumbnail`.
- item 97 references: `auxl -> [49, 100]`.
- item 97 properties: `ispe`, `pixi`, `auxC`, `hvcC`, `irot`.
- item 97 `hvcC`: 105 bytes, Main10, profile_idc 2, level_idc 93, 4:2:0, 10-bit luma/chroma.
- item 97 payload: one length-prefixed NAL, type 20.
- preencoded Annex-B source NALs: VPS/SPS/PPS/SEI/IDR; writer keeps only IDR in item payload and keeps parameter sets in `hvcC`.
- libheif `--with-aux` extracts the linearthumbnail successfully.
- Result: useful intermediate candidate, but rejected as the best Photos probe because the item 97 IDR payload was 238669 bytes, much larger than the observed native linearthumbnail range.

The raw `hvcC` bytes are not byte-identical to `IMG_0032.HEIC`, because VideoToolbox creates parameter sets for the newly encoded local linearthumbnail. This is expected and preferable to forcing the template `hvcC`, which was proven to decode incorrectly. The achieved parity is item graph, property set, bit depth, `hvcC` record class/length/profile, and item payload NAL layout.

### v8_vt_linearthumb_q025

`artifacts/constructed/apple_parity_styledeltamap_v8_vt_linearthumb_q025/apple_parity_styledeltamap_v8_vt_linearthumb_q025.heic`

- item 97 type: `hvc1`.
- item 97 aux type: `tag:apple.com,2023:photo:aux:linearthumbnail`.
- item 97 references: `auxl -> [49, 100]`.
- item 97 properties: `ispe`, `pixi`, `auxC`, `hvcC`, `irot`.
- item 97 `hvcC`: 105 bytes, Main10, profile_idc 2, level_idc 93, 4:2:0, 10-bit luma/chroma.
- item 97 payload: one length-prefixed NAL, type 20, payload bytes 6662.
- `v5_style_safe`/template item 97 payload bytes: 5815.
- `semantic_fitter` hard warnings: none.
- libheif `--with-aux` extracts styledeltamap, HDR gain map, sky matte, and linearthumbnail.
- Result: current preferred Photos probe because it matches the Apple item data type and native payload scale without forcing mismatched parameter sets.

## Implementation Notes

Added:

- `tools/apple_vt_hevc_encoder.swift`
  - Encodes a PNG to Annex-B HEVC using VideoToolbox Main10.
  - Emits VPS/SPS/PPS from `CMVideoFormatDescription` and compressed sample NALs.
  - Sets 709 color attachments so the generated `hvcC` is 105 bytes for a 1024x768 linearthumbnail.
  - Accepts optional `quality`; default is `0.45`, while the current preferred probe uses `0.25`.

- `tools/hevc10_encoder.py`
  - `parse_length_prefixed_nals()`
  - `parse_annex_b_nals()`
  - `payload_and_hvcc_from_annexb_hevc()`
  - `encode_hevc10_still_videotoolbox()` for non-sandboxed usage.

- `tools/apple_template_writer.py`
  - `--linearthumb-encoder {x265,videotoolbox}`
  - `--linearthumb-hevc-path` for preencoded Annex-B injection.
  - generated linearthumbnail now uses single-IDR payload policy.

- `tools/semantic_fitter.py`
  - reports `hevc_nals` and raw `hvcC` length/hash for hvc1 key items.
  - hard-warns when linearthumbnail payload is not Apple single-IDR profile.

## Reproduction

Build the linearthumbnail source PNG:

```bash
/private/tmp/styledeltamap-py313/bin/python -c "from pathlib import Path; from PIL import Image; from tools.aux_generator import generate_linearthumbnail; src=Path('/Users/retriedstormtrooper/Downloads/03_图片素材/RAW_DNG照片/RAW_DNG_JPEG_批量导出/IMG_0342_preview.jpg'); out=Path('artifacts/constructed/apple_parity_styledeltamap_v8_vt_linearthumb_q025/linearthumbnail_input.png'); img=generate_linearthumbnail(src, max_dim=1024, rotate_ccw=False).image.resize((1024,768), Image.Resampling.LANCZOS); img.save(out)"
```

Encode with VideoToolbox directly from shell:

```bash
swift -module-cache-path /private/tmp/styledeltamap-swift-module-cache tools/apple_vt_hevc_encoder.swift artifacts/constructed/apple_parity_styledeltamap_v8_vt_linearthumb_q025/linearthumbnail_input.png artifacts/constructed/apple_parity_styledeltamap_v8_vt_linearthumb_q025/linearthumbnail_vt_q025.hevc 0.25
```

Build final HEIC:

```bash
/private/tmp/styledeltamap-py313/bin/python tools/apple_template_writer.py --template Apple_Native_Samples/IMG_0032.HEIC --sample IMG_0342 --quality 90 --use-preview-gainmap --swap-makernote --generate-styledeltamap --use-preview-style-metadata --landscape --linearthumb-hevc-path artifacts/constructed/apple_parity_styledeltamap_v8_vt_linearthumb_q025/linearthumbnail_vt_q025.hevc --output artifacts/constructed/apple_parity_styledeltamap_v8_vt_linearthumb_q025/apple_parity_styledeltamap_v8_vt_linearthumb_q025.heic
```

Validate:

```bash
/private/tmp/styledeltamap-py313/bin/python tools/heif_dump.py artifacts/constructed/apple_parity_styledeltamap_v8_vt_linearthumb_q025/apple_parity_styledeltamap_v8_vt_linearthumb_q025.heic --json artifacts/constructed/apple_parity_styledeltamap_v8_vt_linearthumb_q025/apple_parity_styledeltamap_v8_vt_linearthumb_q025.heif.json --md artifacts/constructed/apple_parity_styledeltamap_v8_vt_linearthumb_q025/apple_parity_styledeltamap_v8_vt_linearthumb_q025.heif.md
heif-info artifacts/constructed/apple_parity_styledeltamap_v8_vt_linearthumb_q025/apple_parity_styledeltamap_v8_vt_linearthumb_q025.heic
heif-convert --with-aux --no-colons artifacts/constructed/apple_parity_styledeltamap_v8_vt_linearthumb_q025/apple_parity_styledeltamap_v8_vt_linearthumb_q025.heic artifacts/constructed/apple_parity_styledeltamap_v8_vt_linearthumb_q025/decoded.png
/private/tmp/styledeltamap-py313/bin/python tools/semantic_fitter.py artifacts/constructed/apple_parity_styledeltamap_v8_vt_linearthumb_q025/apple_parity_styledeltamap_v8_vt_linearthumb_q025.heic --reference artifacts/constructed/apple_parity_styledeltamap_v5_style_safe/apple_parity_styledeltamap_v5_style_safe.heic --template Apple_Native_Samples/IMG_0032.HEIC --decoded-dir artifacts/constructed/apple_parity_styledeltamap_v8_vt_linearthumb_q025 --json artifacts/constructed/apple_parity_styledeltamap_v8_vt_linearthumb_q025/apple_parity_styledeltamap_v8_vt_linearthumb_q025.semantic.json --md artifacts/constructed/apple_parity_styledeltamap_v8_vt_linearthumb_q025/apple_parity_styledeltamap_v8_vt_linearthumb_q025.semantic.md
```

## Current Boundary

This work does not prove Apple Photos UI activation. It proves the generated file now matches the Apple native linearthumbnail item structure and data type much more closely than v5:

- no multi-NAL linearthumbnail item payload;
- no x265 110-byte linearthumbnail `hvcC`;
- no forced-template `hvcC` mismatch;
- no oversized high-quality linearthumbnail payload in the preferred v8 candidate;
- auxiliary extraction remains valid.

If Photos still does not activate style controls, the next likely targets are style metadata plist semantics, Exif/MakerNote private fields, and generated styledeltamap tile semantics. Sky/person matte generation should remain a separate experiment because the successful `v5_style_safe` still used template-copied semantic matte data.
