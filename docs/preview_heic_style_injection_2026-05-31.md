# Preview HEIC Style Injection Findings - 2026-05-31

## Result

The first direct-injection candidate is:

`artifacts/constructed/apple_style_injected_from_preview_heic_v1/apple_style_injected_from_preview_heic_v1.heic`

The user later confirmed that this v1 file activates Photographic Styles in Apple Photos.

This file is different from the previous Apple-template parity outputs:

- the primary grid and primary tile payloads come from a new Apple HEIC base generated from `IMG_0342_preview.jpg` with `sips`;
- the Apple native sample is not used as the whole-file container template;
- the private style family is injected as remapped items;
- `iinf`, `iref`, `iprp/ipco/ipma`, `idat`, `iloc`, and `mdat` are rebuilt so offsets and references match the new graph.

## Tool

The tool to share is:

`tools/inject_style_family.py`

Build the current candidate:

```bash
/private/tmp/styledeltamap-py313/bin/python tools/inject_style_family.py \
  --preview-jpeg "/Users/retriedstormtrooper/Downloads/03_图片素材/RAW_DNG照片/RAW_DNG_JPEG_批量导出/IMG_0342_preview.jpg" \
  --make-base-with-sips \
  --base-size 4032x3024 \
  --style-donor artifacts/constructed/apple_parity_styledeltamap_v8_vt_linearthumb_q025/apple_parity_styledeltamap_v8_vt_linearthumb_q025.heic \
  --template Apple_Native_Samples/IMG_0032.HEIC \
  --output artifacts/constructed/apple_style_injected_from_preview_heic_v1/apple_style_injected_from_preview_heic_v1.heic
```

The tool can also patch an already generated base HEIC:

```bash
/private/tmp/styledeltamap-py313/bin/python tools/inject_style_family.py \
  --base-heic path/to/base_from_preview.heic \
  --preview-jpeg path/to/preview.jpg \
  --style-donor artifacts/constructed/apple_parity_styledeltamap_v8_vt_linearthumb_q025/apple_parity_styledeltamap_v8_vt_linearthumb_q025.heic \
  --template Apple_Native_Samples/IMG_0032.HEIC \
  --output path/to/injected.heic
```

Do not patch an arbitrary-size base unless its primary dimensions match the donor `tmap` dimensions. The tool rejects the known bad case where the full-size `sips` output is `8064x6048` but the donor `tmap` is `4032x3024`.

To repair linearthumbnail compression artifacts without changing the proven style graph, use the replacement option added after v1:

```bash
/Users/retriedstormtrooper/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 tools/inject_style_family.py \
  --preview-jpeg "/Users/retriedstormtrooper/Downloads/03_图片素材/RAW_DNG照片/RAW_DNG_JPEG_批量导出/IMG_0342_preview.jpg" \
  --make-base-with-sips \
  --base-size 4032x3024 \
  --style-donor artifacts/constructed/apple_parity_styledeltamap_v8_vt_linearthumb_q025/apple_parity_styledeltamap_v8_vt_linearthumb_q025.heic \
  --template Apple_Native_Samples/IMG_0032.HEIC \
  --replace-linearthumb-hevc artifacts/constructed/apple_style_injected_from_preview_heic_v2_q045/linearthumbnail_vt_q045.hevc \
  --output artifacts/constructed/apple_style_injected_from_preview_heic_v2_q045/apple_style_injected_from_preview_heic_v2_q045.heic
```

## Direct Injection Graph

For `apple_style_injected_from_preview_heic_v1.heic`:

- primary item: `49`, from the generated base HEIC;
- styledeltamap: item `82`, `grid`, `auxC = tag:apple.com,2023:photo:aux:styledeltamap`;
- HDR gainmap: item `95`, `grid`, `auxC = urn:com:apple:photo:2020:aux:hdrgainmap`;
- semantic sky matte: item `96`, `hvc1`, `auxC = urn:com:apple:photo:2020:aux:semanticskymatte`;
- linearthumbnail: item `97`, `hvc1`, `auxC = tag:apple.com,2023:photo:aux:linearthumbnail`;
- tmap: item `99`, `tmap`;
- style metadata: item `100`, `uri ` with `tag:apple.com,2023:photo:metadata:styles`;
- base Exif: item `50`, payload updated with the Apple MakerNote private subpayload.

Key references:

- styledeltamap `auxl -> [49, 99]`;
- linearthumbnail `auxl -> [49, 99]`;
- semantic sky matte `auxl -> [49, 99]`;
- HDR gainmap `auxl -> [49]`;
- tmap `dimg -> [49, 95]`;
- style metadata `cdsc -> [49, 99]`;
- Exif `cdsc -> [49, 99]`.

## Validation

Commands run:

```bash
/private/tmp/styledeltamap-py313/bin/python tools/heif_dump.py artifacts/constructed/apple_style_injected_from_preview_heic_v1/apple_style_injected_from_preview_heic_v1.heic --json artifacts/constructed/apple_style_injected_from_preview_heic_v1/apple_style_injected_from_preview_heic_v1.heif.json --md artifacts/constructed/apple_style_injected_from_preview_heic_v1/apple_style_injected_from_preview_heic_v1.heif.md
heif-info artifacts/constructed/apple_style_injected_from_preview_heic_v1/apple_style_injected_from_preview_heic_v1.heic
heif-convert --with-aux --no-colons artifacts/constructed/apple_style_injected_from_preview_heic_v1/apple_style_injected_from_preview_heic_v1.heic artifacts/constructed/apple_style_injected_from_preview_heic_v1/decoded.png
/private/tmp/styledeltamap-py313/bin/python tools/semantic_fitter.py artifacts/constructed/apple_style_injected_from_preview_heic_v1/apple_style_injected_from_preview_heic_v1.heic --reference artifacts/constructed/apple_parity_styledeltamap_v8_vt_linearthumb_q025/apple_parity_styledeltamap_v8_vt_linearthumb_q025.heic --template Apple_Native_Samples/IMG_0032.HEIC --decoded-dir artifacts/constructed/apple_style_injected_from_preview_heic_v1 --json artifacts/constructed/apple_style_injected_from_preview_heic_v1/apple_style_injected_from_preview_heic_v1.semantic.json --md artifacts/constructed/apple_style_injected_from_preview_heic_v1/apple_style_injected_from_preview_heic_v1.semantic.md
```

Results:

- `heif-info` exits successfully and reports primary image `4032x3024`, Exif, XMP, and Apple styles metadata URI.
- `heif-convert --with-aux` extracts styledeltamap, HDR gainmap, semantic sky matte, and linearthumbnail.
- `semantic_fitter` reports `Hard warnings: 0`.
- linearthumbnail remains Apple-like: `hvc1`, 105-byte Main10 `hvcC`, single NAL type `[20]`, `auxl -> [49,99]`.

## Screenshot Claim Assessment

The screenshot claim is directionally supported, with one important boundary.

Supported:

- The local Apple corpus shows styledeltamap is usually near neutral and low amplitude. This fits a residual/prediction-style payload better than a full reconstruction map.
- `v5_style_safe` worked while `v5` failed, and `v8` works after making generated linearthumbnail match Apple native data type. That strongly supports the claim that linearthumbnail is activation-sensitive and likely style-rendering-sensitive.
- Direct injection now preserves the same linearthumbnail data type and links it to the base primary/tmap graph.

Not proven:

- The exact Apple residual formula is still unknown.
- We have not proven that Apple uses one specific prediction model before writing styledeltamap.
- We have not yet imported the direct-injection v1 file into Apple Photos to prove UI activation.

## Next Test

The direct-injection route is viable because v1 activates style controls. The next import test should use the quality-fixed v2 file:

`artifacts/constructed/apple_style_injected_from_preview_heic_v2_q045/apple_style_injected_from_preview_heic_v2_q045.heic`

If v2 activates like v1, use v2 as the baseline for cherry-pick experiments. Replace linearthumbnail, styledeltamap, HDR gainmap, and private metadata one at a time so activation and rendering effects remain attributable.
