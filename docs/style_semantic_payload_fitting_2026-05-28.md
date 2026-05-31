# Style Semantic Payload Fitting Notes

Date: 2026-05-28

## Scope

This note records the current v3c/v4 diagnosis and the next generated-payload candidate:

- Working reference reported by user: `artifacts/constructed/apple_parity_styledeltamap_v3c/apple_parity_styledeltamap_v3c.heic`
- Failing generated-aux candidate reported by user: `artifacts/constructed/apple_parity_styledeltamap_v4/apple_parity_styledeltamap_v4.heic`
- New candidate: `artifacts/constructed/apple_parity_styledeltamap_v5/apple_parity_styledeltamap_v5.heic`

The goal is not to claim Apple Photos compatibility from parser success. The goal is to remove known structural regressions, make generated private payloads more Apple-like, and produce evidence that can guide the next Photos/ImageIO import test.

## v4 Regression

The most concrete v4 bug was not `auxC`, `auxl`, `dimg`, or `tmap`. Those graph relationships were present.

The hard failure was item property index 4:

- Apple template `irot` payload: 1 byte, `03`
- v3c `irot` payload: 1 byte, `03`
- v4 `irot` payload: 5 bytes, `0000000000`

`heif_dump` previously tolerated this and reported 0 degrees. `exiftool` reported the real interoperability symptom:

```text
Rotation: Unknown (0 0 0 0 0)
```

Because property index 4 is associated with the primary grid and the private auxiliary image items, this invalid compact property can poison the whole ImageIO transform graph. This is the strongest local explanation for why v4 lost style behavior while v3c did not.

The second v4 risk was item 97, `tag:apple.com,2023:photo:aux:linearthumbnail`:

- v3c copied the Apple/template linearthumbnail payload.
- v4 generated a much larger linearthumbnail payload from a raw-looking preview source.
- v4 decoded linearthumbnail used nearly the full 8-bit output range, unlike the Apple/template narrow centered thumbnail.

Item 101 was not the v4 regression by itself: v3c and v4 item 101 style bplist payloads are byte-identical.

## Implemented Changes

Code changes:

- `tools/apple_template_writer.py`
  - Writes landscape `irot` as a one-byte compact item property instead of a FullBox-like payload.
  - Encodes generated linearthumbnail with Main10 level 3.1.
  - Treats explicit linearthumbnail source paths as affine-fitted thumbnail sources rather than raw payload sources.
  - Clarifies `build_summary.json` when only the Apple MakerNote private subpayload is template-derived.

- `tools/aux_generator.py`
  - Clamps linearthumbnail output into the observed Apple-like narrow 10-bit band before HEVC encoding.

- `tools/hevc10_encoder.py`
  - Adds optional full-range signaling for generated Main10 payloads.

- `tools/heif_dump.py`
  - Reports `irot.payload_bytes` and flags non-one-byte payloads.

- `tools/semantic_fitter.py`
  - Adds a reproducible comparison report for candidate, working reference, and template HEIF files.
  - Reports key item hashes, item properties, decoded aux stats, style bplist summaries, and hard warnings.

Tests:

- `tests/test_heif_dump.py` now covers malformed `irot` payload detection.
- `tests/test_apple_template_writer.py` now asserts landscape `irot` writes exactly one byte.
- `tests/test_semantic_fitter.py` now proves the v4 report flags the malformed `irot` and v3c does not.
- `tests/test_aux_generator.py` now checks real-preview linearthumbnail output remains in an Apple-like narrow range.

## v5 Candidate

Generated file:

```text
artifacts/constructed/apple_parity_styledeltamap_v5/apple_parity_styledeltamap_v5.heic
```

Build policy:

- Primary image grid: generated from `IMG_0342_preview.jpg`
- Styledeltamap grid tiles: generated near-neutral Main10 HEVC
- HDR gain map tiles: generated from preview JPEG MPF `MPImage2`
- Linearthumbnail: generated from preview through affine fitting, clamped to Apple-like narrow range, encoded Main10 level 3.1
- Style metadata item 101: same scene-updated bplist path as v3c/v4
- Exif item 102: preview Exif with template Apple MakerNote private subpayload including `0x0054` and `0x005a`
- Landscape mode: fixed one-byte `irot=0` and tmap `ispe=4032x3024`

Validation artifacts:

```text
artifacts/constructed/apple_parity_styledeltamap_v5/apple_parity_styledeltamap_v5.heif.json
artifacts/constructed/apple_parity_styledeltamap_v5/apple_parity_styledeltamap_v5.heif.md
artifacts/constructed/apple_parity_styledeltamap_v5/apple_parity_styledeltamap_v5.semantic.json
artifacts/constructed/apple_parity_styledeltamap_v5/apple_parity_styledeltamap_v5.semantic.md
```

Local validation:

- `heif-info` reads the file as HEIC and reports primary image `4032x3024`, metadata URI, Exif, and `angle (ccw): 0`.
- `heif-convert --with-aux --no-colons` extracts primary, styledeltamap, HDR gain map, semantic sky matte, and linearthumbnail.
- `semantic_fitter.py` reports zero hard warnings for v5.
- `exiftool` reports normal horizontal rotations, not `Unknown`.
- ImageIO's public `kCGImageAuxiliaryDataTypeHDRGainMap` query sees the HDR gain map in both v3c and v5. Direct queries with Apple-private strings for styledeltamap/linearthumbnail return nil even for user-reported-working v3c, so that public API is not a valid pass/fail test for the private style UI.

Key v5 semantic report facts:

- All `irot` properties have `payload_bytes: 1`.
- Styledeltamap item 81 still has `auxC=tag:apple.com,2023:photo:aux:styledeltamap`.
- Styledeltamap still `auxl`-references primary item 49.
- v5 item 101 is equal to v3c item 101.
- v5 item 97 differs from v3c/template because it is generated.

## Isolation Candidate

An additional isolation candidate was generated:

```text
artifacts/constructed/apple_parity_styledeltamap_v5_style_safe/apple_parity_styledeltamap_v5_style_safe.heic
```

It keeps the fixed landscape `irot`, generated styledeltamap, generated HDR gain map, and v4-style Exif/MakerNote policy, but restores the template/v3c linearthumbnail payload. Use it if v5 still fails in Photos:

- If `v5_style_safe` works but v5 fails, item 97 linearthumbnail generation is still the problem.
- If both fail, look next at landscape transform policy and Exif/MakerNote mixing.
- If both work, the main v4 regression was the malformed `irot` property.

Validation artifacts:

```text
artifacts/constructed/apple_parity_styledeltamap_v5_style_safe/apple_parity_styledeltamap_v5_style_safe.heif.json
artifacts/constructed/apple_parity_styledeltamap_v5_style_safe/apple_parity_styledeltamap_v5_style_safe.semantic.md
```

## Remaining Risks

I do not have 100% confidence that v5 will activate Apple Photos style controls until it is imported into Photos/ImageIO and tested. The strongest local bugs are fixed, but the private Apple family still has unresolved semantic gaps:

- The generated linearthumbnail is more Apple-like than v4 but not byte- or encoder-identical to native Apple output.
- The styledeltamap is neutral and experimental. It does not claim to be Apple's true style residual formula.
- The `tmap` payload and style bplist binary keys `1`, `3`, `c`, and `d` are still template-derived.
- The Exif item uses preview standard fields with a template MakerNote private subpayload. This preserves template tags `0x0054` and `0x005a`, but it is not a fully scene-native MakerNote.

## Next Photos Test

Import v5 into Apple Photos/ImageIO and compare against v3c:

```text
artifacts/constructed/apple_parity_styledeltamap_v5/apple_parity_styledeltamap_v5.heic
```

If v5 still fails while v3c works, the next isolation candidates are:

1. v5 with template/v3c linearthumbnail restored, keeping fixed `irot`.
2. v5 with v3c/template Exif restored, keeping fixed `irot` and generated linearthumbnail.
3. v5 with generated linearthumbnail but portrait/v3c transform policy restored.

The semantic report tool should be used for every candidate so the changed item family is explicit.
