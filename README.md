# Photographic Style Research

Reverse-engineering and reconstruction of Apple Photos' **Photographic Styles** HEIC format — the auxiliary images, metadata structures, and encoding parameters that activate the Styles UI in Apple Photos.

## Overview

Apple Photos uses a proprietary HEIC extension called `styledeltamap` to store per-photo style adjustment data. This project:

1. **Reverse-engineers** the Apple-native HEIC structure (item graph, auxiliary types, encoding parameters)
2. **Reconstructs** compatible HEIC files from standard DNG/JPG photo pairs
3. **Documents** the findings in detailed technical reports

## Project Structure

```
tools/                          # Core tools
  apple_template_writer.py      # Template-based HEIC builder (main pipeline)
  heif_aux_writer.py            # ISO-oriented HEIF auxiliary writer
  heif_dump.py                  # HEIF/ISOBMFF structure parser
  hevc10_encoder.py             # HEVC Main10 encoder (x265 / VideoToolbox)
  apple_vt_hevc_encoder.swift   # Apple VideoToolbox HEVC encoder
  aux_generator.py              # Generate linearthumbnail & styledeltamap
  semantic_fitter.py            # Structural validation tool
  proraw_residual_probe.py      # DNG/JPG residual analysis
  exif_field_updater.py         # Exif field updater
  exif_makernote_swap.py        # Apple MakerNote injection
  styledeltamap_diagnostics.py  # Diagnostic extraction tool

Sources/StyleDeltaMapCore/      # macOS app core command/runner layer
Sources/StyleDeltaMap/          # Native SwiftUI macOS app
script/build_and_run.sh         # Build, stage, sign, and launch the app

tests/                          # Python and Swift test suites
docs/                           # Technical documentation
  nofusion_styledeltamap_reverse_engineering.md
  apple_parity_styledeltamap_attempt.md
  apple_linearthumbnail_item97_findings_2026-05-31.md
  ...

Apple_Native_Samples/           # Reference HEIC files (not in repo)
  IMG_0032.HEIC                 # Primary template sample
  IMG_0033.HEIC                 # Secondary reference sample
```

## Key Findings

### Apple HEIC Item Structure

An Apple Photographic Styles HEIC contains these items:

| Item ID | Type | Role | Encoding |
|---|---|---|---|
| 1-48 | `hvc1` | Primary image tiles (512×512) | 8-bit HEVC Main |
| 49 | `grid` | Primary image grid (4032×3024) | Grid descriptor |
| 51-80 | `hvc1` | styledeltamap tiles (512×512) | 10-bit HEVC Main10 |
| 81 | `grid` | styledeltamap grid (2880×2160) | Grid descriptor |
| 82-93 | `hvc1` | HDR gain map tiles (512×512) | 8-bit HEVC |
| 94 | `grid` | HDR gain map grid (2016×1512) | Grid descriptor |
| 95 | `hvc1` | Semantic sky matte (2016×1512) | 8-bit HEVC |
| 97 | `hvc1` | Linear thumbnail (1024×768) | 10-bit HEVC Main10 |
| 100 | `tmap` | Tone map descriptor | 62 bytes |
| 101 | `uri ` | Style metadata bplist | Binary plist |
| 102 | `Exif` | EXIF/MakerNote | EXIF APP1 |

### Linear Thumbnail (Item 97)

- **Encoding**: 10-bit HEVC Main10, single IDR NAL (type 20)
- **hvcC**: 105 bytes, Main10 profile, level 3.1
- **Transfer function**: BT.709 (NOT PQ)
- **Affine transform**: Maps scene range [p05, p95] → 10-bit [270, 730]
- **Apple-native payload range**: 4,485 – 70,948 bytes

### styledeltamap (Items 51-80)

- **Encoding**: 10-bit HEVC Main10, 30 tiles (5×6 grid)
- **Neutral value**: 128 (8-bit) / 512 (10-bit) = zero style delta
- **Canvas**: 3072×2304, active area 2880×2160

## Usage

### Prerequisites

- Python 3.13+ with: `pillow-heif`, `numpy`, `Pillow`
- macOS with VideoToolbox (for HEVC encoding)
- `heif-convert` / `heif-info` (from `libheif`)

### Generate a styledeltamap HEIC

```bash
# From a DNG/JPG pair
python tools/apple_template_writer.py \
  --template Apple_Native_Samples/IMG_0032.HEIC \
  --dng-root /path/to/dng-jpg-folder \
  --sample IMG_XXXX \
  --quality 90 \
  --generate-styledeltamap \
  --use-preview-style-metadata \
  --use-preview-gainmap \
  --swap-makernote \
  --generate-linearthumb \
  --landscape \
  --output output.heic
```

### Validate output

```bash
# Structural validation
python tools/semantic_fitter.py output.heic --json report.json --md report.md

# HEIF dump
python tools/heif_dump.py output.heic --json dump.json

# Extract auxiliary images
heif-convert --with-aux output.heic decoded.png
```

### Run tests

```bash
python -m pytest tests/ -v
```

### Run the macOS app

The native macOS app is an operator shell for the existing tools. It does not include a visual companion pane; it builds safe `Process` argument arrays for direct style injection, gain-map/RAW auxiliary reconstruction, and validation.

```bash
/bin/bash script/build_and_run.sh
/bin/bash script/build_and_run.sh --verify
swift test
```

## Documentation

- [NoFusion Reverse Engineering](docs/nofusion_styledeltamap_reverse_engineering.md) — Initial analysis of Apple vs NoFusion HEIC files
- [Apple Parity Attempt](docs/apple_parity_styledeltamap_attempt.md) — Template-based reconstruction progress
- [Linear Thumbnail Findings](docs/apple_linearthumbnail_item97_findings_2026-05-31.md) — Item 97 encoding analysis
- [Preserve-Base HDR Style Graft](docs/preserve_base_hdr_style_graft_2026-06-01.md) — Reuse target HDR graph while adding style items
- [Spatial Source Ablation](docs/photographic-style-spatial-source-ablation-20260602.md) — Reproducible source perturbation run for base, styledeltamap, linearthumbnail, sky matte, and style metadata
- [ISO Auxiliary Writer](docs/iso_aux_styledeltamap_writer.md) — Standards-oriented HEIF writer
- [macOS App](docs/macos_app_2026-05-31.md) — Native SwiftUI app architecture, usage, and validation evidence

## Status

- ✅ Template-based HEIC builder working (apple_template_writer.py)
- ✅ All auxiliary images correctly encoded (styledeltamap, linearthumbnail, gainmap)
- ✅ Structural validation passing (0 hard warnings)
- ✅ macOS sips / heif-convert can decode output
- ✅ Direct style injection has been user-verified to activate Apple Photos Photographic Styles UI
- ✅ VideoToolbox Main10 single-IDR linearthumbnail replacement fixes the v1 low-quality q=0.25 direction
- ✅ Preserve-base HDR graft mode can reuse a target HEIC's own primary/HDR gain map/tmap payloads byte-identically while adding style items
- 🔄 HeifBuilder (self-contained, no template) — work in progress
- 🔄 Preserve-base HDR graft Photos UI behavior — structurally valid, still needs import testing per target file family
- ❓ Apple's private styledeltamap math — not proven

## License

Research project. Apple, HEIF, and related trademarks are property of their respective owners.
