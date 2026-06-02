#!/usr/bin/env python3
"""Batch export DNG/JPG pairs to styled HEIC files (horizontal only)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
PROJECT_DIR = TOOLS_DIR.parent
STYLE_DONOR = PROJECT_DIR / "artifacts" / "constructed" / "apple_parity_styledeltamap_v8_vt_linearthumb_q025" / "apple_parity_styledeltamap_v8_vt_linearthumb_q025.heic"
TEMPLATE = PROJECT_DIR / "Apple_Native_Samples" / "IMG_0032.HEIC"
PYTHON = sys.executable
SWIFT_ENCODER = TOOLS_DIR / "apple_vt_hevc_encoder.swift"


def get_image_dimensions(path: Path) -> tuple[int, int]:
    """Get image width and height using sips."""
    result = subprocess.run(
        ["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(path)],
        capture_output=True,
        text=True,
    )
    width = height = 0
    for line in result.stdout.splitlines():
        if "pixelWidth" in line:
            width = int(line.split(":")[1].strip())
        elif "pixelHeight" in line:
            height = int(line.split(":")[1].strip())
    return width, height


def find_dng_jpg_pairs(folder: Path) -> list[tuple[Path, Path]]:
    """Find DNG files with matching preview JPGs."""
    pairs = []
    for dng in sorted(folder.glob("*_converted.DNG")):
        base_name = dng.stem.replace("_converted", "")
        jpg = folder / f"{base_name}_preview.jpg"
        if jpg.exists():
            pairs.append((dng, jpg))
    return pairs


def process_pair(
    dng: Path,
    jpg: Path,
    output_dir: Path,
    style_donor: Path,
    template: Path,
) -> dict:
    """Process a single DNG/JPG pair into a styled HEIC."""
    stem = dng.stem.replace("_converted", "")
    lt_png = output_dir / f"{stem}_linearthumbnail.png"
    lt_hevc = output_dir / f"{stem}_linearthumbnail_vt_q045.hevc"
    heic_output = output_dir / f"{stem}_styled.heic"

    # Step 1: Generate linearthumbnail PNG from DNG
    lt_cmd = [
        PYTHON, str(TOOLS_DIR / "aux_generator.py"),
        "linearthumbnail-dng", str(dng),
        "--preview", str(jpg),
        "--output", str(lt_png),
        "--json", str(output_dir / f"{stem}_linearthumbnail.json"),
    ]
    subprocess.run(lt_cmd, check=True, capture_output=True)

    # Step 2: Encode PNG to HEVC with VideoToolbox
    swift_cmd = [
        "swift", "-module-cache-path", "/private/tmp/styledeltamap-swift-module-cache",
        str(SWIFT_ENCODER),
        str(lt_png),
        str(lt_hevc),
        "0.45",
    ]
    subprocess.run(swift_cmd, check=True, capture_output=True)

    # Step 3: Inject style family
    inject_cmd = [
        PYTHON, str(TOOLS_DIR / "inject_style_family.py"),
        "--make-base-with-sips",
        "--preview-jpeg", str(jpg),
        "--base-size", "4032x3024",
        "--style-donor", str(style_donor),
        "--template", str(template),
        "--replace-linearthumb-hevc", str(lt_hevc),
        "--output", str(heic_output),
    ]
    result = subprocess.run(inject_cmd, capture_output=True, text=True)
    summary = json.loads(result.stdout) if result.stdout else {}
    return summary


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", type=Path)
    parser.add_argument("--output-dir", "-o", type=Path)
    args = parser.parse_args()

    output_dir = args.output_dir or args.folder
    output_dir.mkdir(parents=True, exist_ok=True)

    pairs = find_dng_jpg_pairs(args.folder)
    horizontal_pairs = []
    for dng, jpg in pairs:
        w, h = get_image_dimensions(dng)
        if w > h:
            horizontal_pairs.append((dng, jpg, w, h))

    print(f"Found {len(horizontal_pairs)} horizontal DNG/JPG pairs")
    results = []
    for dng, jpg, w, h in horizontal_pairs:
        print(f"Processing {dng.name} ({w}x{h})...")
        try:
            summary = process_pair(dng, jpg, output_dir, STYLE_DONOR, TEMPLATE)
            results.append({"pair": dng.name, "width": w, "height": h, "summary": summary})
        except Exception as e:
            print(f"  ERROR: {e}")

    (output_dir / "batch_summary.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False) + "\n"
    )
    print(f"Done. {len(results)} files processed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
