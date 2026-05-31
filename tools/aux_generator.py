#!/usr/bin/env python3
"""Generate auxiliary image payloads from preview JPG and DNG inputs.

Replaces template-copied linearthumbnail and styledeltamap with scene-derived content.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

# Apple-native reference statistics (from IMG_0032, IMG_0033 analysis)
# LinearThumbnail uses ~42-45% of the 10-bit range, centered near 512
_LINTHUMB_TARGET_LOW = 270  # 10-bit value for darkest scene pixels
_LINTHUMB_TARGET_HIGH = 730  # 10-bit value for brightest scene pixels
_LINTHUMB_TARGET_MID = (_LINTHUMB_TARGET_LOW + _LINTHUMB_TARGET_HIGH) // 2  # 500
_LINTHUMB_TARGET_RANGE = _LINTHUMB_TARGET_HIGH - _LINTHUMB_TARGET_LOW  # 460

# StyleDeltaMap neutral value (10-bit centered = zero delta)
_STYLEDELTAMAP_NEUTRAL_10BIT = 512
_STYLEDELTAMAP_NEUTRAL_8BIT = 128


@dataclass(frozen=True)
class LinearThumbnailResult:
    """Result of linearthumbnail generation."""
    image: Image.Image  # 8-bit PIL image (encoder converts to 10-bit)
    stats: dict[str, Any]


@dataclass(frozen=True)
class StyleDeltaMapResult:
    """Result of styledeltamap generation."""
    image: Image.Image  # 8-bit PIL image (encoder converts to 10-bit)
    stats: dict[str, Any]


def _resize_fit(image: Image.Image, max_dim: int) -> Image.Image:
    """Resize image to fit within max_dim, preserving aspect ratio."""
    w, h = image.size
    scale = min(1.0, max_dim / max(w, h))
    if scale >= 1.0:
        return image
    new_w = max(1, round(w * scale))
    new_h = max(1, round(h * scale))
    return image.resize((new_w, new_h), Image.Resampling.LANCZOS)


def _compute_affine_params(arr_8bit: np.ndarray) -> tuple[float, float]:
    """Compute per-scene affine parameters for linearthumbnail.

    Maps the scene's effective range into the Apple-native 10-bit range
    (~270-730), centered near 500.

    Args:
        arr_8bit: uint8 array of primary/preview pixel values

    Returns:
        (slope, intercept) such that: value_10bit = slope * value_8bit + intercept
    """
    flat = arr_8bit.astype(np.float64).ravel()
    scene_mean = float(np.mean(flat))
    scene_std = float(np.std(flat))

    # Use percentiles for robust range estimation
    p05 = float(np.percentile(flat, 5))
    p95 = float(np.percentile(flat, 95))
    effective_range = max(p95 - p05, 10.0)  # avoid division by zero

    # Map [p05, p95] to [TARGET_LOW, TARGET_HIGH]
    slope = _LINTHUMB_TARGET_RANGE / effective_range
    intercept = _LINTHUMB_TARGET_LOW - slope * p05

    # Sanity clamp: slope should be in [0.5, 5.0] based on observed samples
    slope = max(0.5, min(5.0, slope))
    # Recompute intercept to keep midpoint near target
    intercept = _LINTHUMB_TARGET_MID - slope * scene_mean

    return slope, intercept


def generate_linearthumbnail(
    preview_path: Path,
    *,
    max_dim: int = 1024,
    rotate_ccw: bool = False,
) -> LinearThumbnailResult:
    """Generate a linearthumbnail from a preview JPG.

    The linearthumbnail represents the scene without any Photographic Style
    tone curve applied. It uses the same gamma-encoded space as the primary
    image but with an affine transform mapping the scene range into a narrow
    band of the 10-bit range (~42-45% usage, centered near 500).

    Args:
        preview_path: Path to the preview JPG file.
        max_dim: Maximum dimension for the thumbnail (default 1024).

    Returns:
        LinearThumbnailResult with 8-bit PIL image and statistics.
    """
    with Image.open(preview_path) as src:
        preview = src.convert("RGB")
    if rotate_ccw:
        preview = preview.transpose(Image.Transpose.ROTATE_90)
    preview = _resize_fit(preview, max_dim)

    arr = np.asarray(preview, dtype=np.float64)

    slope, intercept = _compute_affine_params(arr)

    # Apply affine transform and clamp into the narrow Apple-like 10-bit band.
    arr_10bit = np.clip(slope * arr + intercept, _LINTHUMB_TARGET_LOW, _LINTHUMB_TARGET_HIGH)

    # Convert back to 8-bit for the HEVC encoder
    # The encoder does: float = pixel / 255.0, then y = float * 1023
    # So: pixel_8bit = round(value_10bit * 255 / 1023)
    arr_8bit_out = np.clip(arr_10bit * (255.0 / 1023.0), 0, 255)

    result_image = Image.fromarray(arr_8bit_out.astype(np.uint8), "RGB")

    stats = {
        "source": str(preview_path),
        "output_size": {"width": result_image.size[0], "height": result_image.size[1]},
        "affine": {"slope": round(slope, 4), "intercept": round(intercept, 2)},
        "input_stats": {
            "mean": round(float(np.mean(arr)), 2),
            "std": round(float(np.std(arr)), 2),
            "p05": round(float(np.percentile(arr, 5)), 2),
            "p95": round(float(np.percentile(arr, 95)), 2),
        },
        "output_10bit_stats": {
            "mean": round(float(np.mean(arr_10bit)), 2),
            "std": round(float(np.std(arr_10bit)), 2),
            "min": round(float(np.min(arr_10bit)), 2),
            "max": round(float(np.max(arr_10bit)), 2),
        },
    }

    return LinearThumbnailResult(image=result_image, stats=stats)


def generate_styledeltamap(
    *,
    width: int = 2880,
    height: int = 2160,
    neutral_8bit: int = _STYLEDELTAMAP_NEUTRAL_8BIT,
) -> StyleDeltaMapResult:
    """Generate a styledeltamap as a neutral constant map.

    In Apple-native samples with no Photographic Style applied, the
    styledeltamap is effectively a constant map at value 128 (8-bit) /
    512 (10-bit), representing zero delta. Small observed variations
    (~0.4 std) are HEVC compression artifacts.

    Args:
        width: Output width (default 2880, Apple-native).
        height: Output height (default 2160, Apple-native).
        neutral_8bit: Neutral value in 8-bit (default 128).

    Returns:
        StyleDeltaMapResult with 8-bit PIL image and statistics.
    """
    arr = np.full((height, width, 3), neutral_8bit, dtype=np.uint8)
    result_image = Image.fromarray(arr, "RGB")

    stats = {
        "mode": "neutral",
        "neutral_value_8bit": neutral_8bit,
        "neutral_value_10bit_approx": round(neutral_8bit * 1023.0 / 255.0, 1),
        "output_size": {"width": width, "height": height},
    }

    return StyleDeltaMapResult(image=result_image, stats=stats)


def generate_styledeltamap_from_dng(
    dng_path: Path,
    preview_path: Path,
    *,
    width: int = 2880,
    height: int = 2160,
    amplitude: float = 4.0,
) -> StyleDeltaMapResult:
    """Generate a styledeltamap from DNG vs preview residual.

    Computes the luma residual between the high-bit DNG (linear light)
    and the preview JPG (sRGB gamma), then maps it to a centered 10-bit
    representation.

    This is a PLAUSIBLE reconstruction based on the hypothesis that
    styledeltamap encodes tone/style deltas. It is NOT proven to match
    Apple's actual algorithm.

    Args:
        dng_path: Path to the DNG file.
        preview_path: Path to the preview JPG file.
        width: Output width (default 2880).
        height: Output height (default 2160).
        amplitude: Controls residual scaling (default 4.0).

    Returns:
        StyleDeltaMapResult with 8-bit PIL image and statistics.
    """
    import shutil
    import subprocess
    import tempfile

    with tempfile.TemporaryDirectory(prefix="sdmap_") as tmpdir:
        tmp = Path(tmpdir)
        dng_png = tmp / "dng.png"

        sips = shutil.which("sips")
        if not sips:
            raise RuntimeError("sips not found; cannot decode DNG")
        subprocess.run(
            [sips, "-s", "format", "png", str(dng_path), "--out", str(dng_png)],
            check=True,
            capture_output=True,
            text=True,
        )

        dng_img = Image.open(dng_png).convert("RGB")
        preview_img = Image.open(preview_path).convert("RGB")

        dng_img = dng_img.resize((width, height), Image.Resampling.LANCZOS)
        preview_img = preview_img.resize((width, height), Image.Resampling.LANCZOS)

        dng_arr = np.asarray(dng_img, dtype=np.float32) / 255.0
        preview_arr = np.asarray(preview_img, dtype=np.float32) / 255.0

        def srgb_to_linear(x: np.ndarray) -> np.ndarray:
            return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)

        dng_linear = srgb_to_linear(dng_arr)
        preview_linear = srgb_to_linear(preview_arr)

        dng_luma = dng_linear[..., 0] * 0.2126 + dng_linear[..., 1] * 0.7152 + dng_linear[..., 2] * 0.0722
        preview_luma = preview_linear[..., 0] * 0.2126 + preview_linear[..., 1] * 0.7152 + preview_linear[..., 2] * 0.0722

        luma_residual = dng_luma - preview_luma
        centered = np.clip(luma_residual, -1.0, 1.0)
        value_10bit = np.rint(128.0 + centered * amplitude)
        value_8bit = np.clip(value_10bit * (255.0 / 1023.0), 0, 255)

        arr_rgb = np.stack([value_8bit] * 3, axis=-1).astype(np.uint8)
        result_image = Image.fromarray(arr_rgb, "RGB")

        stats = {
            "mode": "dng_residual",
            "dng": str(dng_path),
            "preview": str(preview_path),
            "amplitude": amplitude,
            "luma_residual": {
                "min": round(float(luma_residual.min()), 6),
                "max": round(float(luma_residual.max()), 6),
                "mean": round(float(luma_residual.mean()), 6),
                "std": round(float(luma_residual.std()), 6),
            },
            "output_size": {"width": width, "height": height},
        }

        return StyleDeltaMapResult(image=result_image, stats=stats)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate auxiliary image payloads.")
    sub = parser.add_subparsers(dest="command")

    lt = sub.add_parser("linearthumbnail", help="Generate linearthumbnail from preview JPG")
    lt.add_argument("preview", type=Path)
    lt.add_argument("--max-dim", type=int, default=1024)
    lt.add_argument("--output", "-o", type=Path, required=True)
    lt.add_argument("--json", dest="json_path", type=Path)

    sd = sub.add_parser("styledeltamap", help="Generate styledeltamap (neutral)")
    sd.add_argument("--width", type=int, default=2880)
    sd.add_argument("--height", type=int, default=2160)
    sd.add_argument("--output", "-o", type=Path, required=True)
    sd.add_argument("--json", dest="json_path", type=Path)

    sd_dng = sub.add_parser("styledeltamap-dng", help="Generate styledeltamap from DNG residual")
    sd_dng.add_argument("dng", type=Path)
    sd_dng.add_argument("preview", type=Path)
    sd_dng.add_argument("--width", type=int, default=2880)
    sd_dng.add_argument("--height", type=int, default=2160)
    sd_dng.add_argument("--amplitude", type=float, default=4.0)
    sd_dng.add_argument("--output", "-o", type=Path, required=True)
    sd_dng.add_argument("--json", dest="json_path", type=Path)

    args = parser.parse_args()

    if args.command == "linearthumbnail":
        result = generate_linearthumbnail(args.preview, max_dim=args.max_dim)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        result.image.save(args.output)
        if args.json_path:
            args.json_path.parent.mkdir(parents=True, exist_ok=True)
            args.json_path.write_text(json.dumps(result.stats, indent=2) + "\n")
        else:
            print(json.dumps(result.stats, indent=2))

    elif args.command == "styledeltamap":
        result = generate_styledeltamap(width=args.width, height=args.height)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        result.image.save(args.output)
        if args.json_path:
            args.json_path.parent.mkdir(parents=True, exist_ok=True)
            args.json_path.write_text(json.dumps(result.stats, indent=2) + "\n")
        else:
            print(json.dumps(result.stats, indent=2))

    elif args.command == "styledeltamap-dng":
        result = generate_styledeltamap_from_dng(
            args.dng, args.preview,
            width=args.width, height=args.height,
            amplitude=args.amplitude,
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        result.image.save(args.output)
        if args.json_path:
            args.json_path.parent.mkdir(parents=True, exist_ok=True)
            args.json_path.write_text(json.dumps(result.stats, indent=2) + "\n")
        else:
            print(json.dumps(result.stats, indent=2))

    else:
        parser.print_help()
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
