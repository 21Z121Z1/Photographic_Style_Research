#!/usr/bin/env python3
"""First-pass ProRAW/DNG vs preview residual probe for styledeltamap research."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image


@dataclass(frozen=True)
class RawPreviewPair:
    key: str
    dng: Path
    preview: Path


@dataclass(frozen=True)
class CandidateMap:
    name: str
    image: np.ndarray
    float_map: np.ndarray
    stats: dict[str, Any]


def discover_pairs(root: Path) -> dict[str, RawPreviewPair]:
    dng = {path.name.removesuffix("_converted.DNG"): path for path in root.glob("*_converted.DNG")}
    preview = {path.name.removesuffix("_preview.jpg"): path for path in root.glob("*_preview.jpg")}
    return {
        key: RawPreviewPair(key=key, dng=dng[key], preview=preview[key])
        for key in sorted(set(dng) & set(preview))
    }


def convert_dng_with_sips(dng_path: Path, output_path: Path) -> str:
    sips = shutil.which("sips")
    if not sips:
        raise RuntimeError("sips not found; cannot decode DNG without rawpy")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(
        [sips, "-s", "format", "png", str(dng_path), "--out", str(output_path)],
        check=True,
        text=True,
        capture_output=True,
    )
    return completed.stdout + completed.stderr


def _resize_for_probe(image: Image.Image, max_dim: int) -> Image.Image:
    width, height = image.size
    scale = min(1.0, max_dim / max(width, height))
    if scale == 1.0:
        return image
    new_size = (max(1, round(width * scale)), max(1, round(height * scale)))
    return image.resize(new_size, Image.Resampling.BILINEAR)


def load_normalized_rgb(path: Path, max_dim: int) -> tuple[np.ndarray, dict[str, Any]]:
    image = _resize_for_probe(Image.open(path).convert("RGB"), max_dim)
    arr = np.asarray(image)
    divisor = 65535.0 if arr.dtype == np.uint16 else 255.0
    return arr.astype(np.float32) / divisor, {
        "path": str(path),
        "mode": image.mode,
        "size": {"width": image.size[0], "height": image.size[1]},
        "dtype": str(arr.dtype),
        "normalization_divisor": divisor,
    }


def _summary(values: np.ndarray) -> dict[str, Any]:
    flat = values.reshape(-1, values.shape[-1]) if values.ndim == 3 else values.ravel()
    return {
        "min": np.min(flat, axis=0).round(6).tolist(),
        "max": np.max(flat, axis=0).round(6).tolist(),
        "mean": np.mean(flat, axis=0).round(6).tolist(),
        "std": np.std(flat, axis=0).round(6).tolist(),
        "p01": np.percentile(flat, 1, axis=0).round(6).tolist(),
        "p50": np.percentile(flat, 50, axis=0).round(6).tolist(),
        "p99": np.percentile(flat, 99, axis=0).round(6).tolist(),
    }


def _luma(rgb: np.ndarray) -> np.ndarray:
    return rgb[..., 0] * 0.2126 + rgb[..., 1] * 0.7152 + rgb[..., 2] * 0.0722


def _corr(a: np.ndarray, b: np.ndarray) -> float | None:
    a = a.astype(np.float64).ravel()
    b = b.astype(np.float64).ravel()
    a_std = a.std()
    b_std = b.std()
    if a_std == 0 or b_std == 0:
        return None
    return round(float(((a - a.mean()) * (b - b.mean())).mean() / (a_std * b_std)), 6)


def _center_and_scale(values: np.ndarray) -> np.ndarray:
    centered = values.astype(np.float32) - np.median(values, axis=(0, 1), keepdims=True)
    scale = np.percentile(np.abs(centered), 99)
    if scale <= 1e-6:
        return np.zeros_like(centered, dtype=np.float32)
    return np.clip(centered / scale, -1.0, 1.0).astype(np.float32)


def _quantize_near_neutral(values: np.ndarray, amplitude: int) -> np.ndarray:
    quantized = np.rint(128.0 + np.clip(values, -1.0, 1.0) * float(amplitude))
    return np.clip(quantized, 0, 255).astype(np.uint8)


def _candidate_stats(image: np.ndarray, float_map: np.ndarray, base_rgb: np.ndarray) -> dict[str, Any]:
    flat = image.reshape(-1, image.shape[-1])
    base_luma = _luma(base_rgb)
    return {
        "min": flat.min(axis=0).astype(int).tolist(),
        "max": flat.max(axis=0).astype(int).tolist(),
        "mean": np.mean(flat, axis=0).round(6).tolist(),
        "std": np.std(flat, axis=0).round(6).tolist(),
        "unique_values_sample": int(
            np.unique(image[: min(image.shape[0], 512), : min(image.shape[1], 512)]).size
        ),
        "float_map": _summary(float_map),
        "base_luma_corr_by_channel": [
            _corr(base_luma, image[..., channel]) for channel in range(image.shape[-1])
        ],
    }


def generate_candidate_maps(
    high_rgb: np.ndarray, base_rgb: np.ndarray, amplitude: int = 4
) -> dict[str, CandidateMap]:
    if high_rgb.shape != base_rgb.shape:
        raise ValueError(f"shape mismatch: {high_rgb.shape} vs {base_rgb.shape}")
    if high_rgb.ndim != 3 or high_rgb.shape[-1] != 3:
        raise ValueError(f"expected RGB arrays with shape HxWx3, got {high_rgb.shape}")

    residual = high_rgb.astype(np.float32) - base_rgb.astype(np.float32)
    high_luma = _luma(high_rgb)
    base_luma = _luma(base_rgb)
    luma_residual = (high_luma - base_luma).astype(np.float32)
    luma_float = np.repeat(_center_and_scale(luma_residual[..., None]), 3, axis=2)
    chroma_luma_float = _center_and_scale(residual)
    neutral_float = np.zeros_like(high_rgb, dtype=np.float32)

    candidates = {
        "neutral": neutral_float,
        "luma_residual": luma_float,
        "chroma_luma_residual": chroma_luma_float,
    }
    return {
        name: CandidateMap(
            name=name,
            image=_quantize_near_neutral(float_map, amplitude),
            float_map=float_map,
            stats=_candidate_stats(_quantize_near_neutral(float_map, amplitude), float_map, base_rgb),
        )
        for name, float_map in candidates.items()
    }


def compute_residuals(high_rgb: np.ndarray, base_rgb: np.ndarray) -> dict[str, Any]:
    if high_rgb.shape != base_rgb.shape:
        raise ValueError(f"shape mismatch: {high_rgb.shape} vs {base_rgb.shape}")
    rgb_residual = high_rgb - base_rgb
    high_luma = _luma(high_rgb)
    base_luma = _luma(base_rgb)
    luma_residual = high_luma - base_luma
    chroma_residual = rgb_residual - luma_residual[..., None]
    centered = np.clip((luma_residual + 1.0) * 0.5, 0.0, 1.0)
    quantized_2bit = np.floor(centered * 4).clip(0, 3).astype(np.uint8)
    quantized_4bit = np.floor(centered * 16).clip(0, 15).astype(np.uint8)
    return {
        "rgb_residual": _summary(rgb_residual),
        "luma_residual": _summary(luma_residual),
        "chroma_residual": _summary(chroma_residual),
        "high_base_luma_correlation": _corr(high_luma, base_luma),
        "quantized_luma_residual": {
            "two_bit_unique_values": sorted(int(value) for value in np.unique(quantized_2bit)),
            "four_bit_unique_values": sorted(int(value) for value in np.unique(quantized_4bit)),
        },
    }


def _save_luma_residual_preview(luma_residual: np.ndarray, output_path: Path) -> None:
    normalized = np.clip((luma_residual + 0.5) * 255.0, 0, 255).astype(np.uint8)
    Image.fromarray(normalized, "L").save(output_path)


def _save_candidate_artifacts(candidates: dict[str, CandidateMap], pair_dir: Path) -> list[dict[str, Any]]:
    artifacts = []
    for name, candidate in candidates.items():
        png_path = pair_dir / f"{name}.png"
        npy_path = pair_dir / f"{name}.float.npy"
        stats_path = pair_dir / f"{name}.stats.json"
        Image.fromarray(candidate.image, "RGB").save(png_path)
        np.save(npy_path, candidate.float_map.astype(np.float32))
        stats_path.write_text(json.dumps(candidate.stats, indent=2, ensure_ascii=False) + "\n")
        artifacts.append(
            {
                "name": name,
                "png": str(png_path),
                "npy": str(npy_path),
                "stats_json": str(stats_path),
                "stats": candidate.stats,
            }
        )
    return artifacts


def analyze_pair(pair: RawPreviewPair, output_dir: Path, max_dim: int) -> dict[str, Any]:
    pair_dir = output_dir / pair.key
    pair_dir.mkdir(parents=True, exist_ok=True)
    dng_png = pair_dir / "dng_sips.png"
    sips_log = convert_dng_with_sips(pair.dng, dng_png)
    high_rgb, high_info = load_normalized_rgb(dng_png, max_dim)
    base_rgb, base_info = load_normalized_rgb(pair.preview, max_dim)
    if high_rgb.shape != base_rgb.shape:
        base_image = Image.open(pair.preview).convert("RGB").resize(
            (high_rgb.shape[1], high_rgb.shape[0]), Image.Resampling.BILINEAR
        )
        base_rgb = np.asarray(base_image).astype(np.float32) / 255.0
        base_info["resized_to_match"] = {"width": high_rgb.shape[1], "height": high_rgb.shape[0]}
    residuals = compute_residuals(high_rgb, base_rgb)
    candidates = generate_candidate_maps(high_rgb, base_rgb)
    luma_residual = _luma(high_rgb) - _luma(base_rgb)
    preview_path = pair_dir / "luma_residual_preview.png"
    _save_luma_residual_preview(luma_residual, preview_path)
    return {
        "key": pair.key,
        "dng": str(pair.dng),
        "preview": str(pair.preview),
        "sips_log": sips_log,
        "decoded_dng_png": str(dng_png),
        "analysis_max_dim": max_dim,
        "high": high_info,
        "base": base_info,
        "residuals": residuals,
        "candidate_maps": _save_candidate_artifacts(candidates, pair_dir),
        "diagnostic_preview": str(preview_path),
        "inference_boundary": "This compares macOS-decoded DNG RGB against an exported preview; it is not proof of Apple's styledeltamap algorithm.",
    }


def format_markdown(result: dict[str, Any], pair_count: int) -> str:
    residuals = result["residuals"]
    lines = [
        "# ProRAW Residual Probe",
        "",
        f"- Paired DNG/JPG samples discovered: {pair_count}",
        f"- Sample analyzed: `{result['key']}`",
        f"- DNG: `{result['dng']}`",
        f"- Preview: `{result['preview']}`",
        f"- Analysis max dimension: {result['analysis_max_dim']}",
        f"- Diagnostic residual preview: `{result['diagnostic_preview']}`",
        "",
        "This compares macOS-decoded DNG RGB against an exported preview; it is not proof of Apple's styledeltamap algorithm.",
        "",
        "## Residual Stats",
        "",
        f"- High/base luma correlation: {residuals['high_base_luma_correlation']}",
        f"- Luma residual: `{residuals['luma_residual']}`",
        f"- RGB residual: `{residuals['rgb_residual']}`",
        f"- Chroma residual: `{residuals['chroma_residual']}`",
        f"- Quantized luma residual: `{residuals['quantized_luma_residual']}`",
        "",
        "## Candidate Styledeltamap Rasters",
        "",
        "| Candidate | PNG | NPY | Min | Max | Mean | Std | Unique Sample | Base Luma Corr |",
        "|---|---|---|---|---|---|---|---:|---|",
    ]
    for candidate in result.get("candidate_maps", []):
        stats = candidate["stats"]
        lines.append(
            "| {name} | `{png}` | `{npy}` | {minv} | {maxv} | {mean} | {std} | {unique} | {corr} |".format(
                name=candidate["name"],
                png=candidate["png"],
                npy=candidate["npy"],
                minv=stats["min"],
                maxv=stats["max"],
                mean=stats["mean"],
                std=stats["std"],
                unique=stats["unique_values_sample"],
                corr=stats["base_luma_corr_by_channel"],
            )
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe DNG/JPG residual candidates.")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--sample")
    parser.add_argument("--max-dim", type=int, default=1024)
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/proraw_probe"))
    parser.add_argument("--json", dest="json_path", type=Path)
    parser.add_argument("--md", dest="markdown_path", type=Path)
    args = parser.parse_args()

    pairs = discover_pairs(args.root)
    if not pairs:
        raise SystemExit("No *_converted.DNG / *_preview.jpg pairs found")
    key = args.sample or max(pairs, key=lambda candidate: pairs[candidate].dng.stat().st_size)
    if key not in pairs:
        raise SystemExit(f"Pair not found for sample {key!r}")
    result = analyze_pair(pairs[key], args.output_dir, args.max_dim)
    result["pair_inventory"] = {
        "paired_count": len(pairs),
        "selected_key": key,
    }
    if args.json_path:
        args.json_path.parent.mkdir(parents=True, exist_ok=True)
        args.json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    if args.markdown_path:
        args.markdown_path.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_path.write_text(format_markdown(result, len(pairs)))
    if not args.json_path and not args.markdown_path:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
