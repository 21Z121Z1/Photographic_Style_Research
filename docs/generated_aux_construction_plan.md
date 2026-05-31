# Generated Auxiliary Construction Plan

Date: 2026-05-27

## Motivation

Currently `apple_template_writer.py` copies `tag_apple.com,2023_photo_aux_linearthumbnail.png` and `tag_apple.com,2023_photo_aux_styledeltamap.png` payloads byte-for-byte from the Apple template HEIC (`IMG_0032.HEIC`). This means the auxiliary image content is always from the template scene, not the user's actual photo. We want to generate these payloads from the user's preview JPG and high-bit DNG.

## Analysis Summary

### LinearThumbnail

**What it is:** A 10-bit, 1024×768 (portrait) HEVC Main10 image with no ICC color profile. It represents the scene without any Photographic Style tone curve applied — a "linear" (as in "no style adjustment") thumbnail.

**Relationship to primary image:** Affine transform of the sRGB-encoded primary:

```
linthumb_10bit ≈ slope × primary_srgb + intercept
```

Observed values across Apple-native samples:

| Sample | slope (mean) | intercept (mean) | 10-bit range used |
|--------|-------------|------------------|-------------------|
| IMG_0032 | ~1.78 | ~275 | [275, 730] ≈ 44% |
| IMG_0033 | ~1.67 | ~264 | [264, 689] ≈ 42% |
| IMG_4745 (NoFusion) | ~3.97 | ~-258 | full range ≈ 99% |

**Key finding:** The "linear" in linearthumbnail means "linear tone curve" (no style), NOT "linear light" (gamma=1.0). The encoding is in the same gamma-encoded space as the primary (sRGB-like). Correlation with sRGB primary (0.985) is higher than with linearized primary (0.953).

**Residual:** ~18 in 10-bit space (std). High spatial autocorrelation (lag-1 ≈ 0.97) — not random noise, but systematic differences from resize algorithm and HEVC compression.

### StyleDeltaMap

**What it is:** A 10-bit, 2880×2160 grid of 30 HEVC Main10 tiles (5×6 grid, 512px tiles). Has an Apple-private `appl` ICC profile (560 bytes). Represents the per-pixel difference between styled and unstyled rendering.

**Observed content:** In all Apple-native samples examined, the styledeltamap is essentially a **neutral constant map** centered at 128 (8-bit) / 512 (10-bit):

- IMG_0032: mean=127.78, std=0.43, 7 unique values
- IMG_0033: mean=127.77, std=0.44, 9 unique values
- IMG_4745 (NoFusion): mean=128.0, std=0.0, exactly constant

The small variation in Apple samples is HEVC compression artifacts on a constant image, NOT meaningful style delta data. Spatial analysis shows edges are slightly lower (~127.1) while interior is ~128.0 — consistent with tile-boundary compression artifacts.

**Interpretation:** These samples were captured with "Standard" or no Photographic Style, so the delta is zero. The 10-bit centered representation (128 = zero) allows encoding positive and negative deltas when a style IS applied.

## Implementation Plan

### Architecture

Create a new module `tools/aux_generator.py` with two generator functions:

1. `generate_linearthumbnail(preview_path, max_dim=1024)` → `Image.Image` (10-bit PIL image)
2. `generate_styledeltamap(width=2880, height=2160, neutral_value=512)` → `Image.Image` (10-bit PIL image)

Then modify `apple_template_writer.py` to call these generators instead of copying template payloads for items 97 (linearthumbnail) and 81 (styledeltamap grid tiles).

### Step 1: LinearThumbnail Generator

**Input:** Preview JPG path, target max dimension (default 1024)

**Algorithm:**
1. Load preview JPG as RGB
2. Resize to fit within max_dim, preserving aspect ratio (portrait → 768×1024, landscape → 1024×768)
3. Convert 8-bit sRGB values to 10-bit: `value_10bit = round(value_8bit * 1023 / 255)`
4. Apply per-scene affine calibration:
   - Compute scene statistics (mean, percentiles)
   - Choose slope and offset to map the scene's effective range into ~[270, 730] in 10-bit
   - This matches Apple-native behavior (42-45% of range, centered near 512)
5. The output is a 10-bit PIL image (mode 'I;16' or stored as uint16)

**Affine calibration approach:**
The Apple-native samples show a consistent pattern:
- Intercept ≈ 512 - slope × scene_midpoint
- Slope ≈ desired_range / scene_8bit_range
- Where desired_range ≈ 455 (matching IMG_0032's 730-275)
- And scene_midpoint ≈ scene mean

A reasonable per-scene formula:
```python
scene_mean = preview.mean()  # 8-bit
scene_std = preview.std()
# Map [scene_mean - 2*scene_std, scene_mean + 2*scene_std] to [270, 730]
# slope = 460 / (4 * scene_std)
# intercept = 512 - slope * scene_mean
# Clamp to reasonable bounds matching Apple behavior
```

### Step 2: StyleDeltaMap Generator

**Input:** Target dimensions, neutral value (default 512 for 10-bit zero delta)

**Algorithm:**
1. Generate a constant-value image at the target 10-bit value
2. Dimensions: 2880×2160 (or 2160×2880 with rotation)

**Future extension:** If DNG-based residual is desired:
1. Decode DNG to linear RGB
2. Decode preview JPG to linear RGB (apply srgb_to_linear)
3. Resize both to styledeltamap dimensions
4. Compute residual: `delta = dng_linear - preview_linear`
5. Center and scale: `styledeltamap = 512 + delta * amplitude`
6. Clamp to [0, 1023]

### Step 3: Integration into apple_template_writer.py

Modify `_build_payload_maps()` to accept optional generated payloads:
- `linearthumbnail_payload: bytes | None` — replaces template item 97
- `styledeltamap_tiles: list[Hevc10Tile] | None` — already supported (replaces template styledeltamap tiles)

Add a new top-level function or modify `build_apple_template_parity_heif()` to:
1. Call `generate_linearthumbnail()` → encode as 10-bit HEVC Main10 → replace item 97 payload
2. Call `generate_styledeltamap()` → encode as 10-bit HEVC Main10 tiles → replace styledeltamap tile payloads

### Step 4: HEVC Encoding

Both generators produce PIL images that need to be encoded as 10-bit HEVC Main10 using the existing `encode_hevc10_tile()` from `hevc10_encoder.py`.

For linearthumbnail: single HEVC frame (item 97 is `hvc1`, not a grid)
For styledeltamap: 30 HEVC frames (5×6 grid of 512×512 tiles)

### Step 5: Metadata Sidecar for LinearThumbnail

The Apple template has a metadata sidecar (item 98) referenced via `cdsc` from item 97. This is likely a small binary blob with thumbnail metadata. Options:
- Copy from template (simplest, content likely scene-independent)
- Generate a minimal placeholder

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `tools/aux_generator.py` | **Create** | LinearThumbnail and StyleDeltaMap generators |
| `tools/apple_template_writer.py` | **Modify** | Use generators instead of template copy for items 97 and 81 |
| `tests/test_aux_generator.py` | **Create** | Unit tests for generators |
| `docs/generated_aux_construction_plan.md` | **Create** | This document |

## Validation

1. `python3 -m unittest discover -s tests -v` — all tests pass
2. Build a test artifact with generated aux images
3. `python3 tools/heif_dump.py <artifact> --json ... --md ...` — verify structure
4. `heif-convert --with-aux --no-colons <artifact> <out.png>` — verify decoded output
5. Compare decoded linearthumbnail statistics with Apple-native reference

## Risks and Limitations

- **Affine parameters are empirical:** The per-scene slope/offset are derived from fitting 2 Apple samples. A real Apple capture pipeline may use different calibration.
- **No ICC profile for linearthumbnail:** We correctly omit it (Apple does too), but the decoded PNG may look different without color management context.
- **StyleDeltaMap is neutral:** Without knowing Apple's actual style delta algorithm, we generate a neutral map. This is correct for "no style" / "Standard" style but won't reproduce style-specific deltas.
- **HEVC encoding quality:** The `x265` CRF encoding may produce different bitstream characteristics than Apple's hardware encoder.
