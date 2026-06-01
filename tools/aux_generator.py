#!/usr/bin/env python3
"""Generate auxiliary image payloads from preview JPG and DNG inputs.

Replaces template-copied linearthumbnail and styledeltamap with scene-derived content.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.gainmap_sources import GainMapSource, load_gainmap_source

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


def _srgb_to_linear(x: np.ndarray) -> np.ndarray:
    return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)


def _linear_to_srgb(x: np.ndarray) -> np.ndarray:
    clipped = np.clip(x, 0.0, 1.0)
    return np.where(clipped <= 0.0031308, clipped * 12.92, 1.055 * np.power(clipped, 1.0 / 2.4) - 0.055)


def _to_unit_rgb(image: Image.Image, size: tuple[int, int] | None = None) -> np.ndarray:
    src = image.convert("RGB")
    if size is not None and src.size != size:
        src = src.resize(size, Image.Resampling.LANCZOS)
    return np.asarray(src, dtype=np.float32) / 255.0


def _load_rgb_image(path: Path) -> Image.Image:
    if path.suffix.lower() == ".dng":
        import shutil
        import subprocess
        import tempfile

        sips = shutil.which("sips")
        if not sips:
            raise RuntimeError("sips not found; cannot decode DNG")
        with tempfile.TemporaryDirectory(prefix="dng_decode_") as tmpdir:
            png_path = Path(tmpdir) / "decoded.png"
            subprocess.run(
                [sips, "-s", "format", "png", str(path), "--out", str(png_path)],
                check=True,
                capture_output=True,
                text=True,
            )
            with Image.open(png_path) as decoded:
                return decoded.convert("RGB").copy()
    if path.suffix.lower() in {".heic", ".heif", ".hif"}:
        try:
            import pillow_heif  # type: ignore[import-not-found]

            pillow_heif.register_heif_opener()
        except Exception:
            pass
    with Image.open(path) as src:
        return src.convert("RGB").copy()


def _to_unit_gainmap(source: GainMapSource, size: tuple[int, int]) -> np.ndarray:
    image = source.image
    if image.size != size:
        image = image.resize(size, Image.Resampling.LANCZOS)
    if image.mode == "L":
        arr = np.asarray(image, dtype=np.float32)[..., None] / 255.0
    else:
        arr = np.asarray(image.convert("RGB"), dtype=np.float32) / 255.0
    return arr


def _linearthumbnail_from_float_rgb(
    rgb_float: np.ndarray,
    *,
    max_dim: int,
    source_stats: dict[str, Any],
) -> LinearThumbnailResult:
    rgb_float = np.nan_to_num(rgb_float, nan=0.0, posinf=1.0, neginf=0.0)
    rgb_float = np.clip(rgb_float, 0.0, None)
    encoded = _linear_to_srgb(rgb_float / max(float(np.percentile(rgb_float, 99.5)), 1.0))
    image = Image.fromarray(np.rint(np.clip(encoded, 0.0, 1.0) * 255.0).astype(np.uint8), "RGB")
    image = _resize_fit(image, max_dim)
    arr = np.asarray(image, dtype=np.float64)
    slope, intercept = _compute_affine_params(arr)
    arr_10bit = np.clip(slope * arr + intercept, _LINTHUMB_TARGET_LOW, _LINTHUMB_TARGET_HIGH)
    arr_8bit_out = np.clip(arr_10bit * (255.0 / 1023.0), 0, 255)
    result_image = Image.fromarray(arr_8bit_out.astype(np.uint8), "RGB")
    stats = {
        **source_stats,
        "output_size": {"width": result_image.size[0], "height": result_image.size[1]},
        "affine": {"slope": round(slope, 4), "intercept": round(intercept, 2)},
        "output_10bit_stats": {
            "mean": round(float(np.mean(arr_10bit)), 2),
            "std": round(float(np.std(arr_10bit)), 2),
            "min": round(float(np.min(arr_10bit)), 2),
            "max": round(float(np.max(arr_10bit)), 2),
        },
    }
    return LinearThumbnailResult(image=result_image, stats=stats)


def _vector3(value: Any, default: float) -> np.ndarray:
    if isinstance(value, (list, tuple)):
        values = list(value)
    else:
        values = [value]
    out: list[float] = []
    for idx in range(3):
        try:
            out.append(float(values[idx]))
        except (IndexError, TypeError, ValueError):
            out.append(default)
    return np.asarray(out, dtype=np.float32)


def generate_linearthumbnail_from_gainmap(
    base_path: Path,
    gainmap_path: Path,
    *,
    max_dim: int = 1024,
    gainmap_mode: str = "auto",
    gain_strength: float = 1.0,
) -> LinearThumbnailResult:
    """Generate an experimental linearthumbnail from an SDR base and gain map.

    UHDR RGB gain maps use the OPPO 20-float metadata when present. Mono gain
    maps use the same gain value on all channels. Plain image gain maps use a
    centered heuristic and are meant for diagnostics only.
    """
    source = load_gainmap_source(gainmap_path, mode=gainmap_mode)
    base_rgb = _load_rgb_image(base_path)

    base_unit = _to_unit_rgb(base_rgb)
    base_linear = _srgb_to_linear(base_unit)
    gain_unit = _to_unit_gainmap(source, base_rgb.size)
    if gain_unit.shape[-1] == 1:
        gain_unit = np.repeat(gain_unit, 3, axis=2)

    formula = "centered-heuristic"
    if source.mode == "oppo-uhdr-rgb" and "uhdr_info" in source.metadata:
        info = source.metadata["uhdr_info"]
        ratio_min = np.maximum(_vector3(info.get("ratioMin"), 1.0), 1e-6)
        ratio_max = np.maximum(_vector3(info.get("ratioMax"), 1.0), ratio_min)
        gamma = np.maximum(_vector3(info.get("gamma"), 1.0), 1e-6)
        eps_sdr = _vector3(info.get("epsilonSdr"), 0.0)
        eps_hdr = _vector3(info.get("epsilonHdr"), 0.0)
        gain_weight = np.power(np.clip(gain_unit, 0.0, 1.0), gamma.reshape(1, 1, 3))
        log2_gain = np.log2(ratio_min).reshape(1, 1, 3) + gain_weight * (
            np.log2(ratio_max).reshape(1, 1, 3) - np.log2(ratio_min).reshape(1, 1, 3)
        )
        hdr_linear = np.maximum(base_linear + eps_sdr.reshape(1, 1, 3), 0.0) * np.exp2(log2_gain) - eps_hdr.reshape(1, 1, 3)
        formula = "oppo-uhdr-rgb-ratio"
    else:
        log2_gain = (gain_unit - 0.5) * 2.0 * float(gain_strength)
        hdr_linear = base_linear * np.exp2(log2_gain)
        if source.mode == "oppo-lhdr-mono":
            formula = "oppo-lhdr-mono-centered-heuristic"

    source_stats = {
        "mode": "gainmap_linearthumbnail",
        "formula": formula,
        "base": str(base_path),
        "gainmap": str(gainmap_path),
        "gainmap_source_mode": source.mode,
        "gainmap_size": {"width": source.image.size[0], "height": source.image.size[1]},
        "gainmap_raw_bytes": source.raw_bytes_len,
        "gainmap_metadata": source.metadata,
        "hdr_linear_stats": {
            "mean": round(float(np.mean(hdr_linear)), 6),
            "std": round(float(np.std(hdr_linear)), 6),
            "p01": round(float(np.percentile(hdr_linear, 1)), 6),
            "p99": round(float(np.percentile(hdr_linear, 99)), 6),
        },
    }
    return _linearthumbnail_from_float_rgb(hdr_linear, max_dim=max_dim, source_stats=source_stats)


def generate_linearthumbnail_from_best_source(
    *,
    dng_path: Path | None = None,
    preview_path: Path | None = None,
    base_path: Path | None = None,
    gainmap_path: Path | None = None,
    max_dim: int = 1024,
    preview_mix: float = 0.25,
    gainmap_mode: str = "auto",
    gain_strength: float = 1.0,
) -> LinearThumbnailResult:
    """Generate a linearthumbnail with explicit source priority.

    P0 is DNG/RAW-derived, P1 is metadata-aware RGB gain map, and P2 is
    mono/Apple gain-map fallback. The priority choice is reported in stats so
    downstream graft reports do not blur proven inputs with diagnostic ones.
    """
    decisions: list[dict[str, Any]] = []
    if dng_path is not None:
        result = generate_linearthumbnail_from_dng(
            dng_path,
            preview_path,
            max_dim=max_dim,
            preview_mix=preview_mix,
        )
        stats = {
            **result.stats,
            "source_priority": "P0-dng-raw-derived",
            "source_confidence": "high-for-linearthumbnail-input, unproven-for-Apple-private-style-math",
            "selection_decisions": [
                {"priority": "P0", "source": str(dng_path), "selected": True, "reason": "DNG/RAW render was provided"}
            ],
        }
        return LinearThumbnailResult(result.image, stats)

    decisions.append({"priority": "P0", "selected": False, "reason": "DNG/RAW input was not provided"})
    if base_path is not None and gainmap_path is not None:
        result = generate_linearthumbnail_from_gainmap(
            base_path,
            gainmap_path,
            max_dim=max_dim,
            gainmap_mode=gainmap_mode,
            gain_strength=gain_strength,
        )
        source_mode = str(result.stats.get("gainmap_source_mode", ""))
        is_rgb = source_mode in {"oppo-uhdr-rgb", "mpf-rgb", "dng-preview-mpf-rgb", "image-rgb"}
        priority = "P1-rgb-gainmap-metadata-aware" if is_rgb else "P2-mono-gainmap-fallback"
        confidence = (
            "medium-for-HDR-linear-estimate, diagnostic-for-styledeltamap"
            if is_rgb
            else "luma-headroom-only-fallback, no-chroma-recovery"
        )
        decisions.append(
            {
                "priority": "P1" if is_rgb else "P2",
                "source": str(gainmap_path),
                "selected": True,
                "reason": f"gain map source mode {source_mode}",
            }
        )
        stats = {
            **result.stats,
            "source_priority": priority,
            "source_confidence": confidence,
            "selection_decisions": decisions,
        }
        return LinearThumbnailResult(result.image, stats)

    decisions.append(
        {
            "priority": "P1/P2",
            "selected": False,
            "reason": "base image and gain-map input were not both provided",
        }
    )
    raise ValueError("No supported linearthumbnail source was provided; supply DNG or base+gainmap")


def generate_linearthumbnail_from_dng(
    dng_path: Path,
    preview_path: Path | None = None,
    *,
    max_dim: int = 1024,
    preview_mix: float = 0.25,
) -> LinearThumbnailResult:
    """Generate an experimental linearthumbnail from a RAW/DNG render.

    `sips` is used as the conservative platform decoder. If a paired preview is
    supplied, it is blended in lightly so the result stays close to the rendered
    base while keeping more RAW-derived tonal information than preview-only mode.
    """
    raw_rgb = _load_rgb_image(dng_path)
    raw_linear = _srgb_to_linear(_to_unit_rgb(raw_rgb))
    formula = "sips-dng-render"
    if preview_path is not None:
        preview_rgb = _load_rgb_image(preview_path)
        preview_linear = _srgb_to_linear(_to_unit_rgb(preview_rgb, raw_rgb.size))
        mix = float(np.clip(preview_mix, 0.0, 1.0))
        raw_linear = raw_linear * (1.0 - mix) + preview_linear * mix
        formula = "sips-dng-render-preview-blend"

    source_stats = {
        "mode": "dng_linearthumbnail",
        "formula": formula,
        "dng": str(dng_path),
        "preview": str(preview_path) if preview_path else None,
        "preview_mix": preview_mix if preview_path else 0.0,
        "raw_render_size": {"width": raw_rgb.size[0], "height": raw_rgb.size[1]},
        "raw_linear_stats": {
            "mean": round(float(np.mean(raw_linear)), 6),
            "std": round(float(np.std(raw_linear)), 6),
            "p01": round(float(np.percentile(raw_linear, 1)), 6),
            "p99": round(float(np.percentile(raw_linear, 99)), 6),
        },
    }
    return _linearthumbnail_from_float_rgb(raw_linear, max_dim=max_dim, source_stats=source_stats)


def _bayer8(height: int, width: int) -> np.ndarray:
    matrix = np.array(
        [
            [0, 48, 12, 60, 3, 51, 15, 63],
            [32, 16, 44, 28, 35, 19, 47, 31],
            [8, 56, 4, 52, 11, 59, 7, 55],
            [40, 24, 36, 20, 43, 27, 39, 23],
            [2, 50, 14, 62, 1, 49, 13, 61],
            [34, 18, 46, 30, 33, 17, 45, 29],
            [10, 58, 6, 54, 9, 57, 5, 53],
            [42, 26, 38, 22, 41, 25, 37, 21],
        ],
        dtype=np.float32,
    )
    tiled = np.tile(matrix, (height // 8 + 1, width // 8 + 1))[:height, :width]
    return (tiled + 0.5) / 64.0 - 0.5


def generate_styledeltamap_from_gainmap(
    gainmap_path: Path,
    *,
    width: int = 2880,
    height: int = 2160,
    amplitude: float = 6.0,
    gainmap_mode: str = "auto",
    dither_mono: bool = True,
) -> StyleDeltaMapResult:
    """Generate an experimental styledeltamap candidate from a gain map.

    RGB gain maps keep per-channel residuals. Mono maps produce a neutral-low
    amplitude RGB map; optional ordered dithering prevents large single-value
    regions without pretending to recover missing chroma.
    """
    source = load_gainmap_source(gainmap_path, mode=gainmap_mode)
    gain = _to_unit_gainmap(source, (width, height))
    is_mono = gain.shape[-1] == 1
    if is_mono:
        residual = gain[..., 0] - float(np.median(gain[..., 0]))
        scale = max(float(np.percentile(np.abs(residual), 95)), 1e-6)
        delta = residual / scale * amplitude
        if dither_mono:
            delta = delta + _bayer8(height, width) * 0.75
        arr = np.stack([128.0 + delta] * 3, axis=2)
    else:
        channel_center = np.median(gain.reshape(-1, 3), axis=0).reshape(1, 1, 3)
        residual_rgb = gain - channel_center
        scale = np.maximum(np.percentile(np.abs(residual_rgb.reshape(-1, 3)), 95, axis=0), 1e-6).reshape(1, 1, 3)
        arr = 128.0 + residual_rgb / scale * amplitude

    arr_u8 = np.rint(np.clip(arr, 0, 255)).astype(np.uint8)
    result_image = Image.fromarray(arr_u8, "RGB")
    stats = {
        "mode": "gainmap_styledeltamap",
        "formula": "rgb-residual" if not is_mono else "mono-residual-with-dither" if dither_mono else "mono-residual",
        "gainmap": str(gainmap_path),
        "gainmap_source_mode": source.mode,
        "output_size": {"width": width, "height": height},
        "amplitude": amplitude,
        "mean": [round(float(v), 4) for v in arr_u8.reshape(-1, 3).mean(axis=0)],
        "std": [round(float(v), 4) for v in arr_u8.reshape(-1, 3).std(axis=0)],
        "unique_values": int(np.unique(arr_u8.reshape(-1, 3), axis=0).shape[0]),
        "gainmap_metadata": source.metadata,
    }
    return StyleDeltaMapResult(image=result_image, stats=stats)


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
        value_8bit = np.rint(np.clip(128.0 + centered * amplitude, 0, 255))

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

    lt_gm = sub.add_parser("linearthumbnail-gainmap", help="Generate linearthumbnail from SDR base plus gain map")
    lt_gm.add_argument("base", type=Path)
    lt_gm.add_argument("gainmap", type=Path)
    lt_gm.add_argument("--max-dim", type=int, default=1024)
    gainmap_modes = ["auto", "apple-heic", "oppo", "mpf", "image"]
    lt_gm.add_argument("--gainmap-mode", choices=gainmap_modes, default="auto")
    lt_gm.add_argument("--gain-strength", type=float, default=1.0)
    lt_gm.add_argument("--output", "-o", type=Path, required=True)
    lt_gm.add_argument("--json", dest="json_path", type=Path)

    lt_dng = sub.add_parser("linearthumbnail-dng", help="Generate linearthumbnail from DNG, optionally blended with preview JPG")
    lt_dng.add_argument("dng", type=Path)
    lt_dng.add_argument("--preview", type=Path)
    lt_dng.add_argument("--max-dim", type=int, default=1024)
    lt_dng.add_argument("--preview-mix", type=float, default=0.25)
    lt_dng.add_argument("--output", "-o", type=Path, required=True)
    lt_dng.add_argument("--json", dest="json_path", type=Path)

    lt_best = sub.add_parser("linearthumbnail-best", help="Generate linearthumbnail using DNG > RGB gain map > mono gain map priority")
    lt_best.add_argument("--dng", type=Path)
    lt_best.add_argument("--preview", type=Path)
    lt_best.add_argument("--base", type=Path)
    lt_best.add_argument("--gainmap", type=Path)
    lt_best.add_argument("--max-dim", type=int, default=1024)
    lt_best.add_argument("--preview-mix", type=float, default=0.25)
    lt_best.add_argument("--gainmap-mode", choices=gainmap_modes, default="auto")
    lt_best.add_argument("--gain-strength", type=float, default=1.0)
    lt_best.add_argument("--output", "-o", type=Path, required=True)
    lt_best.add_argument("--json", dest="json_path", type=Path)

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

    sd_gm = sub.add_parser("styledeltamap-gainmap", help="Generate styledeltamap candidate from a gain map")
    sd_gm.add_argument("gainmap", type=Path)
    sd_gm.add_argument("--width", type=int, default=2880)
    sd_gm.add_argument("--height", type=int, default=2160)
    sd_gm.add_argument("--amplitude", type=float, default=6.0)
    sd_gm.add_argument("--gainmap-mode", choices=gainmap_modes, default="auto")
    sd_gm.add_argument("--no-dither-mono", action="store_true")
    sd_gm.add_argument("--output", "-o", type=Path, required=True)
    sd_gm.add_argument("--json", dest="json_path", type=Path)

    inspect = sub.add_parser("inspect-gainmap", help="Inspect and optionally preview a supported gain-map input")
    inspect.add_argument("gainmap", type=Path)
    inspect.add_argument("--gainmap-mode", choices=gainmap_modes, default="auto")
    inspect.add_argument("--preview-output", type=Path)
    inspect.add_argument("--json", dest="json_path", type=Path)

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

    elif args.command == "linearthumbnail-gainmap":
        result = generate_linearthumbnail_from_gainmap(
            args.base,
            args.gainmap,
            max_dim=args.max_dim,
            gainmap_mode=args.gainmap_mode,
            gain_strength=args.gain_strength,
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        result.image.save(args.output)
        if args.json_path:
            args.json_path.parent.mkdir(parents=True, exist_ok=True)
            args.json_path.write_text(json.dumps(result.stats, indent=2, ensure_ascii=False) + "\n")
        else:
            print(json.dumps(result.stats, indent=2, ensure_ascii=False))

    elif args.command == "linearthumbnail-dng":
        result = generate_linearthumbnail_from_dng(
            args.dng,
            args.preview,
            max_dim=args.max_dim,
            preview_mix=args.preview_mix,
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        result.image.save(args.output)
        if args.json_path:
            args.json_path.parent.mkdir(parents=True, exist_ok=True)
            args.json_path.write_text(json.dumps(result.stats, indent=2, ensure_ascii=False) + "\n")
        else:
            print(json.dumps(result.stats, indent=2, ensure_ascii=False))

    elif args.command == "linearthumbnail-best":
        result = generate_linearthumbnail_from_best_source(
            dng_path=args.dng,
            preview_path=args.preview,
            base_path=args.base,
            gainmap_path=args.gainmap,
            max_dim=args.max_dim,
            preview_mix=args.preview_mix,
            gainmap_mode=args.gainmap_mode,
            gain_strength=args.gain_strength,
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        result.image.save(args.output)
        if args.json_path:
            args.json_path.parent.mkdir(parents=True, exist_ok=True)
            args.json_path.write_text(json.dumps(result.stats, indent=2, ensure_ascii=False) + "\n")
        else:
            print(json.dumps(result.stats, indent=2, ensure_ascii=False))

    elif args.command == "styledeltamap":
        result = generate_styledeltamap(width=args.width, height=args.height)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        result.image.save(args.output)
        if args.json_path:
            args.json_path.parent.mkdir(parents=True, exist_ok=True)
            args.json_path.write_text(json.dumps(result.stats, indent=2) + "\n")
        else:
            print(json.dumps(result.stats, indent=2))

    elif args.command == "styledeltamap-gainmap":
        result = generate_styledeltamap_from_gainmap(
            args.gainmap,
            width=args.width,
            height=args.height,
            amplitude=args.amplitude,
            gainmap_mode=args.gainmap_mode,
            dither_mono=not args.no_dither_mono,
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        result.image.save(args.output)
        if args.json_path:
            args.json_path.parent.mkdir(parents=True, exist_ok=True)
            args.json_path.write_text(json.dumps(result.stats, indent=2, ensure_ascii=False) + "\n")
        else:
            print(json.dumps(result.stats, indent=2, ensure_ascii=False))

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

    elif args.command == "inspect-gainmap":
        source = load_gainmap_source(args.gainmap, mode=args.gainmap_mode)
        stats = {
            "source": str(args.gainmap),
            "mode": source.mode,
            "size": {"width": source.image.size[0], "height": source.image.size[1]},
            "image_mode": source.image.mode,
            "raw_bytes": source.raw_bytes_len,
            "metadata": source.metadata,
        }
        if args.preview_output:
            args.preview_output.parent.mkdir(parents=True, exist_ok=True)
            source.image.save(args.preview_output)
            stats["preview_output"] = str(args.preview_output)
        if args.json_path:
            args.json_path.parent.mkdir(parents=True, exist_ok=True)
            args.json_path.write_text(json.dumps(stats, indent=2, ensure_ascii=False) + "\n")
        else:
            print(json.dumps(stats, indent=2, ensure_ascii=False))

    else:
        parser.print_help()
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
