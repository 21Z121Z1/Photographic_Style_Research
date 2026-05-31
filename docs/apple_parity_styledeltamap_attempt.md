# Apple-Parity Styledeltamap Attempt

Date: 2026-05-27

## Why The Previous File Failed

The first generated file, `artifacts/constructed/iso_aux_styledeltamap/iso_aux_styledeltamap.heic`, proved a real HEIF auxiliary relationship, but it was still much simpler than Apple-native styledeltamap files.

Key missing families:

- Apple primary image is a `grid` item with 48 HEVC tile children. The first artifact used one standalone `hvc1` primary item.
- Apple styledeltamap is a 10-bit `grid` with 30 HEVC Main10 tile children. The first artifact used 8-bit tile payloads.
- Apple styledeltamap `auxl` references both the primary item and the `tmap` item. The first artifact referenced only the primary item.
- Apple files include an HDR gain-map aux grid, a `tmap` derived item, a semantic sky matte aux item, a linear thumbnail aux item, a style metadata URI item, and an Exif/MakerNote item.
- Apple uses Apple `MiH*` compatible brands and `irot` associations across the relevant image items.

The current hypothesis is that Photos/ImageIO style UI activation needs more than `auxC`; it likely needs the broader Apple capture/edit graph.

## New Artifact

Generated file:

`artifacts/constructed/apple_parity_styledeltamap/apple_parity_styledeltamap.heic`

Generated from:

- Template: `Apple_Native_Samples/IMG_0032.HEIC`
- Primary preview source: `/Users/retriedstormtrooper/Downloads/03_图片素材/RAW_DNG照片/RAW_DNG_JPEG_批量导出/IMG_0342_preview.jpg`

The writer is:

`tools/apple_template_writer.py`

It does not reverse engineer Apple private algorithms. It uses the Apple-native sample as a structural template, regenerates the primary image tile payloads from the selected preview, and copies Apple private auxiliary/metadata payload families from the template.

### Semantic-Fitted Variant (Gain Map + Exif From Preview)

In addition to the baseline copy-based artifact above, there is now a second variant that replaces the most obviously scene-dependent payloads using the source preview JPEG:

`artifacts/constructed/apple_parity_styledeltamap_semantic/apple_parity_styledeltamap_semantic.heic`

Differences vs baseline:

- HDR gain map tiles are regenerated from the preview JPEG's MPF `MPImage2` payload (downsampled to the Apple template gain-map grid shape and encoded into HEVC tiles).
- Exif/MakerNote item payload is replaced using the preview JPEG's Exif APP1 payload, so the capture-time `Apple` MakerNote family (including `SemanticStyle`) matches the scene.

Still copied from the Apple template in this variant:

- styledeltamap grid + 10-bit HEVC tile payloads
- `tmap` payload
- style metadata `uri` bplist payload
- semantic sky matte aux payload
- linear thumbnail aux payload

### V2 Variant (Generated styledeltamap + Preview Gain Map)

A new variant that generates image-specific styledeltamap tiles using a 10-bit HEVC Main10 encoding pipeline:

`artifacts/constructed/apple_parity_styledeltamap_v2/apple_parity_styledeltamap_v2.heic`

Differences vs semantic-fitted variant:

- **styledeltamap tiles are generated** (not copied from template). Each tile is a near-neutral 10-bit residual (centered at 128, std ~0.5) encoded as HEVC Main10 via `ffmpeg→y4m→x265` pipeline.
- HDR gain map tiles regenerated from preview JPEG (same as semantic variant).
- Primary tiles regenerated from preview JPEG (same as all variants).

Still copied from the Apple template in this variant:

- `tmap` payload
- style metadata `uri` bplist payload
- semantic sky matte aux payload
- linear thumbnail aux payload
- Exif/MakerNote item payload

The styledeltamap tile generation pipeline:

1. Load preview JPEG, compute luma statistics (median, std)
2. Generate near-neutral noise image (128 ± small noise, seeded RNG for determinism)
3. Tile into 30 tiles (5×6 grid, 512×512 each)
4. Encode each tile via `x265 --profile main10 --level-idc 3.0` (2-frame trick to force Main 10 profile instead of Main 10 Intra)
5. Extract first frame's NAL units, convert to length-prefixed format
6. Extract hvcC from temporary HEIC (via MP4Box) for property association

The encoded tiles have `profile_idc=2` (Main 10), `level_idc=90`, `bit_depth=10`, `chroma_format=1` (4:2:0) — matching Apple's native hvcC exactly.

## What Is Now Apple-Like

The new artifact has:

- `ftyp` major brand `heic`
- compatible brands copied from Apple sample: `mif1`, `MiHB`, `MiHA`, `heix`, `MiHE`, `MiPr`, `miaf`, `heic`, `tmap`
- primary item id `49`, type `grid`
- primary `dimg` to 48 HEVC tile children
- primary grid dimensions `4032x3024`, 6 rows x 8 columns of 512px tiles
- styledeltamap item id `81`, type `grid`
- styledeltamap `auxC = tag:apple.com,2023:photo:aux:styledeltamap`
- styledeltamap `pixi=[10,10,10]`
- styledeltamap 5x6 grid, 30 HEVC Main10 tile children
- styledeltamap `auxl -> [49, 100]`
- HDR gain map grid item `94`, `auxC=urn:com:apple:photo:2020:aux:hdrgainmap`
- semantic sky matte aux item `95`
- linear thumbnail aux item `97`
- `tmap` item `100`, `dimg -> [49,94]`
- style metadata URI item `101`, URI `tag:apple.com,2023:photo:metadata:styles`
- Exif/MakerNote item `102`
- `cdsc` references from style metadata and Exif to `[49,100]`

The output is not a simple multi-image HEIC and not just the previous ISO aux structure. It now includes the main Apple-native item families observed in `Apple_Native_Samples/IMG_0032.HEIC`.

## What Is Copied

The following payloads are copied from the Apple template in the baseline artifact:

- styledeltamap grid descriptor and 10-bit HEVC tile payloads
- HDR gain-map grid descriptor and tile payloads
- semantic sky matte payload
- linear thumbnail payload and its metadata sidecar
- `tmap` payload
- style metadata bplist payload
- Exif/MakerNote payload
- non-offset metadata boxes and item references

In the semantic-fitted variant (`artifacts/constructed/apple_parity_styledeltamap_semantic/apple_parity_styledeltamap_semantic.heic`), the HDR gain map tile payloads and Exif/MakerNote item payload are replaced using the preview JPEG, while the remaining private payload families above are still template-copied.

This is intentional for the parity attempt. It isolates container/data-type completeness from the unsolved private Apple style-map algorithm.

## What Is Generated

The primary image is generated from `IMG_0342_preview.jpg`:

- resized to `4032x3024`
- padded to a 6x8 tile canvas of `4096x3072`
- split into 48 `512x512` tiles
- each tile encoded as an individual HEVC payload using `pillow_heif`
- final `meta`, `iprp`, `idat`, `iloc`, and `mdat` rebuilt by `tools/apple_template_writer.py`

`pillow_heif` is still not used as a multi-image final writer.

## Validation

Commands run:

```bash
python3 -m unittest discover -s tests -v
python3 tools/heif_dump.py artifacts/constructed/apple_parity_styledeltamap/apple_parity_styledeltamap.heic --json artifacts/constructed/apple_parity_styledeltamap/apple_parity_styledeltamap.heif.json --md artifacts/constructed/apple_parity_styledeltamap/apple_parity_styledeltamap.heif.md --extract-items artifacts/constructed/apple_parity_styledeltamap/items
heif-info artifacts/constructed/apple_parity_styledeltamap/apple_parity_styledeltamap.heic
heif-convert --with-aux --no-colons artifacts/constructed/apple_parity_styledeltamap/apple_parity_styledeltamap.heic artifacts/constructed/apple_parity_styledeltamap/decoded.png

# Semantic-fitted variant (preview-derived HDR gain map + Exif)
python3 tools/heif_dump.py artifacts/constructed/apple_parity_styledeltamap_semantic/apple_parity_styledeltamap_semantic.heic --json artifacts/constructed/apple_parity_styledeltamap_semantic/apple_parity_styledeltamap_semantic.heif.json --md artifacts/constructed/apple_parity_styledeltamap_semantic/apple_parity_styledeltamap_semantic.heif.md --extract-items artifacts/constructed/apple_parity_styledeltamap_semantic/items
heif-info artifacts/constructed/apple_parity_styledeltamap_semantic/apple_parity_styledeltamap_semantic.heic
heif-convert --with-aux --no-colons artifacts/constructed/apple_parity_styledeltamap_semantic/apple_parity_styledeltamap_semantic.heic artifacts/constructed/apple_parity_styledeltamap_semantic/decoded_verify.png

# V2 variant (generated styledeltamap + preview gain map)
python3 tools/heif_dump.py artifacts/constructed/apple_parity_styledeltamap_v2/apple_parity_styledeltamap_v2.heic --json artifacts/constructed/apple_parity_styledeltamap_v2/apple_parity_styledeltamap_v2.heif.json --md artifacts/constructed/apple_parity_styledeltamap_v2/apple_parity_styledeltamap_v2.heif.md
heif-info artifacts/constructed/apple_parity_styledeltamap_v2/apple_parity_styledeltamap_v2.heic
heif-convert --with-aux --no-colons artifacts/constructed/apple_parity_styledeltamap_v2/apple_parity_styledeltamap_v2.heic artifacts/constructed/apple_parity_styledeltamap_v2/decoded.png
```

Observed results:

- Unit tests: 19 passed.
- `heif-info` reads the candidate as a primary 6x8 tiled HEIC image, reports metadata URI and Exif items, and shows the same `error reading brands: insufficient input data` warning that it reports for the Apple-native template itself.
- `heif-convert --with-aux --no-colons` writes 5 PNGs for each variant:
  - `decoded.png`
  - `decoded-tag_apple.com,2023_photo_aux_styledeltamap.png`
  - `decoded-urn_com_apple_photo_2020_aux_hdrgainmap.png`
  - `decoded-urn_com_apple_photo_2020_aux_semanticskymatte.png`
  - `decoded-tag_apple.com,2023_photo_aux_linearthumbnail.png`

Decoded aux dimensions match the Apple template family:

- styledeltamap: `2160x2880` (near-neutral: mean ~127.3, std ~0.5)
- HDR gain map: `1512x2016`
- semantic sky matte: `1512x2016`
- linear thumbnail: `768x1024`

V2 styledeltamap tile hvcC matches Apple's exactly:

- `profile_idc=2` (Main 10)
- `level_idc=90`
- `bit_depth_luma=10`, `bit_depth_chroma=10`
- `chroma_format=1` (4:2:0)

## Remaining Confidence Gap

This artifact reaches structural and data-type parity with the observed Apple sample family, but it is still not proof of Photos UI activation.

Known gaps:

- V2 variant: styledeltamap tiles are generated near-neutral residuals, not Apple's actual style delta algorithm. The tiles have correct codec parameters but different content from Apple's scene-specific styledeltamap.
- All variants: `tmap` payload, style metadata bplist, semantic sky matte, and linear thumbnail are still copied from `IMG_0032` template.
- V2 variant: Exif/MakerNote is still template-copied (not from the preview JPEG).
- The primary tile encoder config is replaced for the regenerated primary payloads, but Apple may expect capture-pipeline-specific encoder details.
- Photos/ImageIO import has not yet been rerun on V2 artifact.

Next steps:

1. Upload V2 to Apple Photos and check if Photographic Styles UI appears.
2. If V2 fails, try V2 with template-copied Exif (keeping MakerNote from IMG_0032).
3. If that works, the issue is Exif mismatch. If it still fails, investigate tmap/style-metadata consistency.

Do not mark the broader goal complete until this new artifact is imported into ImageIO/Photos and the requested private UI or auxiliary data exposure is proven.

## 2026-05-28 v4 Regression And v5 Candidate

The user reported that `apple_parity_styledeltamap_v3c.heic` preserves style-related controls, while `apple_parity_styledeltamap_v4.heic` does not.

The strongest local regression found in v4 is malformed landscape `irot` encoding:

- v3c/template item property index 4: one-byte `irot` payload.
- v4 item property index 4: five-byte FullBox-like payload.
- `exiftool` reports this as `Rotation: Unknown (0 0 0 0 0)`.

This has been fixed in `tools/apple_template_writer.py`, and `tools/heif_dump.py` now reports `irot.payload_bytes` plus warnings for invalid payload sizes.

A new candidate was generated:

`artifacts/constructed/apple_parity_styledeltamap_v5/apple_parity_styledeltamap_v5.heic`

v5 keeps the v4 direction but removes the hard regression:

- landscape `irot=0` is encoded as a one-byte compact item property;
- generated styledeltamap remains present;
- HDR gain map is generated from preview JPEG MPF `MPImage2`;
- generated linearthumbnail is affine-fitted and clamped to a narrow Apple-like range, then encoded Main10 level 3.1;
- style metadata item 101 remains equal to v3c;
- semantic report has zero hard warnings.

Evidence:

- `artifacts/constructed/apple_parity_styledeltamap_v5/apple_parity_styledeltamap_v5.heif.json`
- `artifacts/constructed/apple_parity_styledeltamap_v5/apple_parity_styledeltamap_v5.semantic.md`
- `docs/style_semantic_payload_fitting_2026-05-28.md`

This is still not a Photos compatibility claim. v5 is the next import candidate; if v5 fails while v3c works, isolate item 97 linearthumbnail and item 102 Exif/MakerNote next.

An isolation candidate is also available:

`artifacts/constructed/apple_parity_styledeltamap_v5_style_safe/apple_parity_styledeltamap_v5_style_safe.heic`

It has the fixed one-byte `irot` and generated styledeltamap/HDR gain-map path, but restores the template/v3c linearthumbnail payload. If this works while v5 fails, the remaining breakage is likely item 97 linearthumbnail generation.
