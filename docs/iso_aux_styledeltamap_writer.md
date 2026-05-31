# ISO Auxiliary Styledeltamap Writer

Date: 2026-05-26

## Scope

This workspace now has an experimental standards-oriented HEIF writer for Apple styledeltamap construction.

The writer creates a real HEIF auxiliary-image graph. It does not claim Apple Photos UI compatibility and it does not claim the residual formula matches Apple's private styledeltamap algorithm.

Public code-point checks used for this implementation:

- MP4RA registers `auxC` as the HEIF Auxiliary type item property.
- MP4RA registers `grid`, `hvc1`, `hvt1`, and `tmap` as HEIF item types.
- MP4RA registers `auxl` as the HEIF auxiliary image item reference and `dimg` as the derived image item reference.
- Public ISO/IEC 23008-12:2025/Amd 1 excerpts describe `tmap` as a tone-map derived image item with exactly two `dimg` inputs: base image first, gain map second. This writer does not emit `tmap` because no valid ISO 21496-1 gain map metadata is constructed here.

The earlier `aux1` spelling is treated as a naming trap. It appears in some secondary texts, but the local Apple samples and the current MP4RA registry use `auxl`.

## Files

- Writer: `tools/heif_aux_writer.py`
- Dumper/validator: `tools/heif_dump.py`
- DNG/JPG residual diagnostics: `tools/proraw_residual_probe.py`
- Plan: `docs/superpowers/plans/2026-05-26-iso-aux-styledeltamap.md`
- Generated artifact: `artifacts/constructed/iso_aux_styledeltamap/iso_aux_styledeltamap.heic`
- Generated dump JSON: `artifacts/constructed/iso_aux_styledeltamap/iso_aux_styledeltamap.heif.json`
- Generated dump Markdown: `artifacts/constructed/iso_aux_styledeltamap/iso_aux_styledeltamap.heif.md`
- Candidate diagnostics: `artifacts/constructed/iso_aux_styledeltamap/diagnostics/IMG_0342/`

## Generated Structure

The generated file uses:

- `ftyp`
  - major brand `heic`
  - compatible brands `mif1`, `heic`, `miaf`
- file-level `meta`
  - `hdlr` handler type `pict`
  - `pitm` primary item id `1`
  - `iinf` entries for primary, styledeltamap grid, and four tile children
  - `iref`
    - `dimg` from styledeltamap grid item `2` to tile items `3..6`
    - `auxl` from styledeltamap grid item `2` to primary item `1`
  - `iprp/ipco/ipma`
    - primary: `hvcC`, `ispe`, `pixi`, `colr`
    - styledeltamap grid: `ispe`, `pixi`, `colr`, `auxC`
    - HEVC tile children: `hvcC`, `ispe`, `pixi`, `colr`
  - `idat`
    - 8-byte HEIF grid descriptor
  - `iloc`
    - primary and tile payloads in `mdat`
    - grid descriptor stored through construction method `1` in `idat`
- `mdat`
  - primary HEVC payload
  - HEVC-coded styledeltamap tile payloads

The current generated styledeltamap is neutral by default:

- candidate: `neutral`
- decoded auxiliary PNG: `decoded-tag_apple.com,2023_photo_aux_styledeltamap.png`
- decoded aux extrema: `(128, 128)` for all RGB channels

The diagnostic generator also emits:

- `neutral.png`, `neutral.float.npy`, `neutral.stats.json`
- `luma_residual.png`, `luma_residual.float.npy`, `luma_residual.stats.json`
- `chroma_luma_residual.png`, `chroma_luma_residual.float.npy`, `chroma_luma_residual.stats.json`
- `residual_probe.md`
- `residual_probe.json`

## Commands

Generate the artifact:

```bash
python3 tools/heif_aux_writer.py \
  --sample IMG_0342 \
  --candidate neutral \
  --max-dim 1024 \
  --tile-size 512 \
  --quality 90 \
  --output artifacts/constructed/iso_aux_styledeltamap/iso_aux_styledeltamap.heic
```

Dump and extract item payloads:

```bash
python3 tools/heif_dump.py \
  artifacts/constructed/iso_aux_styledeltamap/iso_aux_styledeltamap.heic \
  --json artifacts/constructed/iso_aux_styledeltamap/iso_aux_styledeltamap.heif.json \
  --md artifacts/constructed/iso_aux_styledeltamap/iso_aux_styledeltamap.heif.md \
  --extract-items artifacts/constructed/iso_aux_styledeltamap/items
```

External validation:

```bash
heif-info artifacts/constructed/iso_aux_styledeltamap/iso_aux_styledeltamap.heic
heif-convert --with-aux --no-colons \
  artifacts/constructed/iso_aux_styledeltamap/iso_aux_styledeltamap.heic \
  artifacts/constructed/iso_aux_styledeltamap/decoded.png
```

Tests:

```bash
python3 -m unittest discover -s tests -v
```

## Validation Results

`heif-info` accepts the generated file as HEIC:

```text
MIME type: image/heic
main brand: heic
compatible brands: mif1, heic, miaf
image: 1024x768 (id=1), primary
```

`heif-convert --with-aux --no-colons` decodes both the primary and private styledeltamap auxiliary image:

```text
File contains 1 image
Written to artifacts/constructed/iso_aux_styledeltamap/decoded.png
Auxiliary image written to artifacts/constructed/iso_aux_styledeltamap/decoded-tag_apple.com,2023_photo_aux_styledeltamap.png
```

`tools/heif_dump.py` reports:

```text
Styledeltamap item id: 2
Styledeltamap dimensions: {'width': 1024, 'height': 768}
Styledeltamap pixi: {'channels': 3, 'bits': [8, 8, 8]}
Styledeltamap grid: {'version': 0, 'flags': 0, 'rows': 2, 'columns': 2, 'output_width': 1024, 'output_height': 768}
Styledeltamap tile count: 4
```

References:

```text
dimg: 2 -> [3, 4, 5, 6]
auxl: 2 -> [1]
```

The generated file is not a `pillow_heif` multi-image output. `pillow_heif` is only used to produce individual HEVC-coded image payloads and `hvcC` decoder configuration. The final `ftyp`, `meta`, `iprp`, `ipma`, `iref`, `iloc`, `idat`, and `mdat` graph is assembled by `tools/heif_aux_writer.py`.

## Boundaries

### ISO-Conformant HEIF Auxiliary Structure

The current artifact satisfies the structural target:

- primary image item exists and is `hvc1`
- styledeltamap auxiliary item exists and is `grid`
- styledeltamap has `auxC = tag:apple.com,2023:photo:aux:styledeltamap`
- styledeltamap references the primary image through `auxl`
- styledeltamap grid references HEVC tile children through `dimg`
- required properties are associated through `ipma`
- local parser and `heif-info` accept the file

### Apple-Like Styledeltamap Structure

The styledeltamap side follows the Apple-native sample shape at the item-graph level:

- grid-derived auxiliary item
- HEVC tile children
- `auxC`
- `auxl`
- `dimg`
- hidden auxiliary/tile items

It does not yet match every Apple-native detail. Current differences include:

- styledeltamap and tile payloads are 8-bit because the current single-image payload encoder path uses Pillow/Pillow-HEIF RGB input.
- no Apple style metadata bplist item is emitted.
- no EXIF/MakerNote `SemanticStyle` item is emitted.
- no `tmap` chain is emitted.

### Apple Photos UI Compatibility

Not validated. Do not claim Photos activation from this artifact.

The next separate validation target would be importing this file into ImageIO/Photos and checking whether Apple exposes the private style UI or auxiliary data. If it fails, the likely missing pieces are Apple style metadata, MakerNote keys, exact 10-bit tile coding, or a valid HDR gain-map / `tmap` chain.

## Follow-Up: Apple-Parity Template Attempt

The first ImageIO/Photos import test failed to expose the private style UI or auxiliary data. A follow-up parity attempt is documented in:

`docs/apple_parity_styledeltamap_attempt.md`

That attempt generates:

`artifacts/constructed/apple_parity_styledeltamap/apple_parity_styledeltamap.heic`

It uses `Apple_Native_Samples/IMG_0032.HEIC` as a structural template, regenerates the primary image as an Apple-like 6x8 tiled grid, and carries over the Apple-private styledeltamap, HDR gain-map, `tmap`, style metadata URI, and Exif/MakerNote item families. This is a stronger structural/data-type parity artifact than the first ISO auxiliary writer output, but it still requires a new ImageIO/Photos import test before any Photos compatibility claim.
