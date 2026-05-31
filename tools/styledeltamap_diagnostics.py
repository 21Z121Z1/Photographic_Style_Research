#!/usr/bin/env python3
"""Decode HEIF auxiliary images with heif-convert and summarize diagnostic PNGs."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image


def _round_list(values: np.ndarray) -> list[float]:
    return [round(float(value), 6) for value in values.tolist()]


def compute_image_stats(image: Image.Image) -> dict[str, Any]:
    arr = np.asarray(image)
    if arr.ndim == 2:
        flat = arr.reshape(-1, 1)
    else:
        flat = arr.reshape(-1, arr.shape[-1])
    sample = arr[: min(arr.shape[0], 512), : min(arr.shape[1], 512)]
    return {
        "mode": image.mode,
        "size": {"width": image.size[0], "height": image.size[1]},
        "dtype": str(arr.dtype),
        "min": _round_list(flat.min(axis=0)),
        "max": _round_list(flat.max(axis=0)),
        "mean": _round_list(flat.mean(axis=0)),
        "std": _round_list(flat.std(axis=0)),
        "unique_values_sample": int(np.unique(sample).size),
    }


def _luma(arr: np.ndarray) -> np.ndarray:
    if arr.ndim == 2:
        return arr.astype(np.float64)
    rgb = arr[..., :3].astype(np.float64)
    return rgb[..., 0] * 0.2126 + rgb[..., 1] * 0.7152 + rgb[..., 2] * 0.0722


def pearson_correlation(a: np.ndarray, b: np.ndarray) -> float | None:
    a = a.astype(np.float64).ravel()
    b = b.astype(np.float64).ravel()
    a_std = a.std()
    b_std = b.std()
    if a_std == 0 or b_std == 0:
        return None
    return round(float(((a - a.mean()) * (b - b.mean())).mean() / (a_std * b_std)), 6)


def compare_to_base(base: Image.Image, aux: Image.Image) -> dict[str, Any]:
    base_resized = base.convert("RGB").resize(aux.size, Image.Resampling.BILINEAR)
    base_luma = _luma(np.asarray(base_resized))
    aux_arr = np.asarray(aux.convert("RGB"))
    return {
        "base_luma_corr_by_aux_channel": [
            pearson_correlation(base_luma, aux_arr[..., channel]) for channel in range(3)
        ]
    }


def run_heif_convert(input_path: Path, output_dir: Path) -> tuple[Path, str]:
    converter = shutil.which("heif-convert")
    if not converter:
        raise RuntimeError("heif-convert not found in PATH")
    output_dir.mkdir(parents=True, exist_ok=True)
    base_output = output_dir / f"{input_path.stem}.png"
    command = [
        converter,
        "--with-aux",
        "--no-colons",
        str(input_path),
        str(base_output),
    ]
    completed = subprocess.run(command, check=True, text=True, capture_output=True)
    return base_output, completed.stdout + completed.stderr


def analyze_file(input_path: Path, output_dir: Path) -> dict[str, Any]:
    file_output_dir = output_dir / input_path.stem
    base_output, log = run_heif_convert(input_path, file_output_dir)
    base_image = Image.open(base_output)
    images = []
    for png_path in sorted(file_output_dir.glob("*.png")):
        image = Image.open(png_path)
        entry = {
            "path": str(png_path),
            "role": "primary" if png_path == base_output else "auxiliary",
            "stats": compute_image_stats(image),
        }
        if png_path != base_output:
            entry["correlation"] = compare_to_base(base_image, image)
        images.append(entry)
    return {
        "source": str(input_path),
        "output_dir": str(file_output_dir),
        "heif_convert_log": log,
        "images": images,
        "note": "PNG outputs are decoded diagnostic views; 10-bit auxiliary payloads may be quantized during conversion.",
    }


def format_markdown(results: list[dict[str, Any]]) -> str:
    lines = [
        "# Styledeltamap Diagnostic Summary",
        "",
        "PNG outputs are decoded diagnostic views; 10-bit auxiliary payloads may be quantized during conversion.",
        "",
        "| Source | Role | PNG | Mode | Size | Min | Max | Mean | Std | Unique Sample | Base Luma Corr |",
        "|---|---|---|---|---|---|---|---|---|---:|---|",
    ]
    for result in results:
        source = result["source"]
        for image in result["images"]:
            stats = image["stats"]
            corr = image.get("correlation", {}).get("base_luma_corr_by_aux_channel", "")
            lines.append(
                "| {source} | {role} | `{png}` | {mode} | {width}x{height} | {minv} | {maxv} | {mean} | {std} | {unique} | {corr} |".format(
                    source=source,
                    role=image["role"],
                    png=Path(image["path"]).name,
                    mode=stats["mode"],
                    width=stats["size"]["width"],
                    height=stats["size"]["height"],
                    minv=stats["min"],
                    maxv=stats["max"],
                    mean=stats["mean"],
                    std=stats["std"],
                    unique=stats["unique_values_sample"],
                    corr=corr,
                )
            )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate styledeltamap auxiliary diagnostics.")
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/diagnostics/styledeltamap"))
    parser.add_argument("--json", dest="json_path", type=Path)
    parser.add_argument("--md", dest="markdown_path", type=Path)
    args = parser.parse_args()

    results = [analyze_file(path, args.output_dir) for path in args.inputs]
    if args.json_path:
        args.json_path.parent.mkdir(parents=True, exist_ok=True)
        args.json_path.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n")
    if args.markdown_path:
        args.markdown_path.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_path.write_text(format_markdown(results))
    if not args.json_path and not args.markdown_path:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
