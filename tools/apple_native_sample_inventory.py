#!/usr/bin/env python3
"""Corpus inventory for Apple-native Photographic Styles HEIC samples.

The tool is intentionally read-only for input samples. It parses the HEIF item
graph with tools.heif_dump, optionally materializes decoded auxiliary PNG
diagnostics through heif-convert, and writes corpus-level JSON/CSV/Markdown
artifacts for evidence review.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import plistlib
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.heif_dump import format_markdown as format_heif_markdown
from tools.heif_dump import parse_file


STYLE_DELTA_AUX_TYPE = "tag:apple.com,2023:photo:aux:styledeltamap"
LINEARTHUMB_AUX_TYPE = "tag:apple.com,2023:photo:aux:linearthumbnail"
HDR_GAINMAP_AUX_TYPE = "urn:com:apple:photo:2020:aux:hdrgainmap"
SEMANTIC_SKY_MATTE_AUX_TYPE = "urn:com:apple:photo:2020:aux:semanticskymatte"
STYLE_METADATA_URI_TYPE = "tag:apple.com,2023:photo:metadata:styles"
APPLE_SEMANTIC_AUX_PREFIX = "urn:com:apple:photo:2020:aux:semantic"

ROLE_ORDER = (
    "primary",
    "styledeltamap",
    "linearthumbnail",
    "hdr_gain_map",
    "semantic_sky_matte",
    "tmap",
    "style_metadata",
    "exif",
)
KNOWN_AUX_TYPE_ORDER = (
    HDR_GAINMAP_AUX_TYPE,
    LINEARTHUMB_AUX_TYPE,
    SEMANTIC_SKY_MATTE_AUX_TYPE,
    STYLE_DELTA_AUX_TYPE,
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def item_payload(data: bytes, item: dict[str, Any]) -> bytes:
    payload = bytearray()
    for extent in item.get("extents", []):
        offset = int(extent.get("absolute_offset", extent.get("offset", 0)))
        length = int(extent.get("length", 0))
        payload.extend(data[offset : offset + length])
    return bytes(payload)


def derived_payload(data: bytes, parsed: dict[str, Any], item: dict[str, Any]) -> bytes:
    payload = bytearray()
    child_ids = item.get("derived_child_item_ids") or []
    for child_id in child_ids:
        child = parsed.get("items", {}).get(str(child_id))
        if child:
            payload.extend(item_payload(data, child))
    return bytes(payload)


def first_item_id(parsed: dict[str, Any], predicate) -> int | None:
    for item_id, item in sorted(parsed.get("items", {}).items(), key=lambda pair: int(pair[0])):
        if predicate(item):
            return int(item_id)
    return None


def extract_role_item_ids(parsed: dict[str, Any]) -> dict[str, int | None]:
    primary = parsed.get("primary_item_id")
    return {
        "primary": int(primary) if primary is not None else None,
        "styledeltamap": first_item_id(parsed, lambda item: item.get("aux_type") == STYLE_DELTA_AUX_TYPE),
        "linearthumbnail": first_item_id(parsed, lambda item: item.get("aux_type") == LINEARTHUMB_AUX_TYPE),
        "hdr_gain_map": first_item_id(parsed, lambda item: item.get("aux_type") == HDR_GAINMAP_AUX_TYPE),
        "semantic_sky_matte": first_item_id(parsed, lambda item: item.get("aux_type") == SEMANTIC_SKY_MATTE_AUX_TYPE),
        "tmap": first_item_id(parsed, lambda item: item.get("item_type") == "tmap"),
        "style_metadata": first_item_id(
            parsed,
            lambda item: item.get("item_type") == "uri " and item.get("uri_type") == STYLE_METADATA_URI_TYPE,
        ),
        "exif": first_item_id(parsed, lambda item: item.get("item_type") == "Exif"),
    }


def semantic_matte_items(parsed: dict[str, Any]) -> list[dict[str, Any]]:
    mattes = []
    for item_id, item in sorted(parsed.get("items", {}).items(), key=lambda pair: int(pair[0])):
        aux_type = item.get("aux_type") or ""
        if aux_type.startswith(APPLE_SEMANTIC_AUX_PREFIX):
            mattes.append(
                {
                    "item_id": int(item_id),
                    "aux_type": aux_type,
                    "dimensions": item.get("dimensions"),
                    "pixi": item.get("pixi"),
                    "references_from": item.get("references_from", []),
                }
            )
    return mattes


def _jsonable_counter(counter: Counter) -> dict[str, int]:
    return {str(key): int(value) for key, value in sorted(counter.items(), key=lambda pair: str(pair[0]))}


def build_structure_signature(parsed: dict[str, Any]) -> dict[str, Any]:
    items = parsed.get("items", {})
    aux_type_set = {item.get("aux_type") for item in items.values() if item.get("aux_type")}
    aux_types = [
        aux_type for aux_type in KNOWN_AUX_TYPE_ORDER if aux_type in aux_type_set
    ] + sorted(aux_type_set - set(KNOWN_AUX_TYPE_ORDER))
    item_types = Counter(item.get("item_type", "") for item in items.values())
    reference_types = sorted({ref.get("type") for ref in parsed.get("references", []) if ref.get("type")})
    role_ids = extract_role_item_ids(parsed)
    role_dimensions = {}
    for role, item_id in role_ids.items():
        item = items.get(str(item_id)) if item_id is not None else None
        role_dimensions[role] = item.get("dimensions") if item else None
    return {
        "item_count": len(items),
        "primary_item_id": parsed.get("primary_item_id"),
        "major_brand": (parsed.get("ftyp") or {}).get("major_brand"),
        "compatible_brands": (parsed.get("ftyp") or {}).get("compatible_brands", []),
        "item_types": _jsonable_counter(item_types),
        "aux_types": aux_types,
        "reference_types": reference_types,
        "role_item_ids": role_ids,
        "role_dimensions": role_dimensions,
    }


def _role_id_set(role_item_ids: dict[str, int | None]) -> set[int]:
    return {int(item_id) for item_id in role_item_ids.values() if item_id is not None}


def classify_unknown_items(
    parsed: dict[str, Any],
    role_item_ids: dict[str, int | None],
) -> list[dict[str, Any]]:
    role_ids = _role_id_set(role_item_ids)
    dimg_children = {
        int(child_id)
        for item in parsed.get("items", {}).values()
        for child_id in item.get("derived_child_item_ids", []) or []
    }
    known_metadata_types = {"Exif", "mime", "uri "}
    unknown = []
    for item_id_text, item in sorted(parsed.get("items", {}).items(), key=lambda pair: int(pair[0])):
        item_id = int(item_id_text)
        aux_type = item.get("aux_type")
        item_type = item.get("item_type")
        is_known_mime = item_type == "mime" and (
            item.get("content_type") in {"image/jpeg", "application/rdf+xml"}
            or str(item.get("content_type", "")).startswith("image/")
        )
        if item_id in role_ids or item_id in dimg_children:
            continue
        if aux_type:
            continue
        if item_type in known_metadata_types and is_known_mime:
            continue
        if any(ref.get("type") == "thmb" for ref in item.get("references_from", [])):
            continue
        if item_type == "grid" and item.get("references_from"):
            continue
        unknown.append(
            {
                "item_id": item_id,
                "item_type": item_type,
                "name": item.get("name"),
                "content_type": item.get("content_type"),
                "uri_type": item.get("uri_type"),
                "dimensions": item.get("dimensions"),
                "pixi": item.get("pixi"),
                "extent_bytes": sum(int(extent.get("length", 0)) for extent in item.get("extents", [])),
                "references_from": item.get("references_from", []),
                "references_to": item.get("references_to", []),
                "property_types": [assoc.get("type") for assoc in item.get("property_associations", []) if assoc.get("type")],
            }
        )
    return unknown


def _round_list(values: np.ndarray | list[float]) -> list[float]:
    arr = np.asarray(values, dtype=np.float64)
    return [round(float(value), 6) for value in arr.tolist()]


def _luma(arr: np.ndarray) -> np.ndarray:
    if arr.ndim == 2:
        return arr.astype(np.float64)
    rgb = arr[..., :3].astype(np.float64)
    return rgb[..., 0] * 0.2126 + rgb[..., 1] * 0.7152 + rgb[..., 2] * 0.0722


def pearson_correlation(a: np.ndarray, b: np.ndarray) -> float | None:
    av = a.astype(np.float64).ravel()
    bv = b.astype(np.float64).ravel()
    a_std = av.std()
    b_std = bv.std()
    if a_std == 0 or b_std == 0:
        return None
    return round(float(((av - av.mean()) * (bv - bv.mean())).mean() / (a_std * b_std)), 6)


def metric_image(image: Image.Image, max_pixels: int | None) -> tuple[Image.Image, bool]:
    if max_pixels is None or image.width * image.height <= max_pixels:
        return image.copy(), False
    scale = math.sqrt(max_pixels / float(image.width * image.height))
    size = (max(1, int(image.width * scale)), max(1, int(image.height * scale)))
    resized = image.copy()
    resized.thumbnail(size, Image.Resampling.BILINEAR)
    return resized, True


def low_frequency_energy_ratio(values: np.ndarray) -> float | None:
    luma = _luma(values)
    if min(luma.shape[:2]) < 4:
        return None
    centered = luma - float(luma.mean())
    power_total = float(np.square(centered).sum())
    if power_total == 0:
        return 1.0
    spectrum = np.fft.rfft2(centered)
    power = np.abs(spectrum) ** 2
    h, w = luma.shape[:2]
    low_h = max(2, math.ceil(h / 4) + 1)
    low_w = max(2, math.ceil((w // 2 + 1) / 4) + 1)
    low_rows = np.r_[0:low_h, max(low_h, h - low_h) : h]
    low_power = float(power[low_rows, :low_w].sum())
    total_power = float(power.sum())
    if total_power == 0:
        return 1.0
    return round(low_power / total_power, 6)


def compute_decoded_image_stats(
    path: Path,
    *,
    neutral_value: float | None = None,
    base_image_path: Path | None = None,
    base_image: Image.Image | None = None,
    compare_image_path: Path | None = None,
    max_metric_pixels: int | None = 1_048_576,
) -> dict[str, Any]:
    original_image = Image.open(path)
    image, downsampled = metric_image(original_image, max_metric_pixels)
    arr = np.asarray(image)
    flat = arr.reshape(-1, arr.shape[-1]) if arr.ndim == 3 else arr.reshape(-1, 1)
    stats: dict[str, Any] = {
        "path": str(path),
        "mode": original_image.mode,
        "size": {"width": original_image.size[0], "height": original_image.size[1]},
        "metric_size": {"width": image.size[0], "height": image.size[1]},
        "metrics_downsampled": downsampled,
        "dtype": str(arr.dtype),
        "channels": int(flat.shape[-1]),
        "min": _round_list(flat.min(axis=0)),
        "max": _round_list(flat.max(axis=0)),
        "mean": _round_list(flat.mean(axis=0)),
        "median": _round_list(np.median(flat, axis=0)),
        "std": _round_list(flat.std(axis=0)),
        "unique_values_sample": int(np.unique(arr[: min(arr.shape[0], 512), : min(arr.shape[1], 512)]).size),
        "is_constant": bool(np.all(flat == flat[0])),
        "low_frequency_energy_ratio": low_frequency_energy_ratio(arr),
    }
    if neutral_value is not None:
        stats["neutral_value"] = neutral_value
        stats["neutral_abs_mean_offset"] = _round_list(np.abs(flat.astype(np.float64) - neutral_value).mean(axis=0))
        stats["neutral_signed_mean_offset"] = _round_list((flat.astype(np.float64) - neutral_value).mean(axis=0))
    histograms = []
    for channel in range(flat.shape[-1]):
        counts, edges = np.histogram(flat[:, channel], bins=16, range=(0, 256))
        histograms.append({"channel": channel, "counts": counts.astype(int).tolist(), "bin_edges": edges.astype(int).tolist()})
    stats["histogram_16_bins"] = histograms

    aux_luma = _luma(arr)
    if base_image is not None or (base_image_path is not None and base_image_path.exists()):
        base_source = base_image if base_image is not None else Image.open(base_image_path).convert("RGB")
        base = base_source.resize(image.size, Image.Resampling.BILINEAR)
        stats["base_luma_correlation"] = pearson_correlation(_luma(np.asarray(base)), aux_luma)
        base_arr = np.asarray(base)
        stats["base_luma_corr_by_channel"] = [
            pearson_correlation(_luma(base_arr), flat[:, channel].reshape(arr.shape[:2]))
            for channel in range(flat.shape[-1])
        ]
    if compare_image_path is not None and compare_image_path.exists():
        other = Image.open(compare_image_path).convert("RGB").resize(image.size, Image.Resampling.BILINEAR)
        stats["compare_luma_correlation"] = pearson_correlation(_luma(np.asarray(other)), aux_luma)
    return stats


def _item_payload_summary(data: bytes, parsed: dict[str, Any], item_id: int | None) -> dict[str, Any] | None:
    if item_id is None:
        return None
    item = parsed.get("items", {}).get(str(item_id))
    if not item:
        return None
    payload = item_payload(data, item)
    derived = derived_payload(data, parsed, item)
    source_payload = derived if derived else payload
    summary = {
        "item_id": item_id,
        "item_type": item.get("item_type"),
        "name": item.get("name"),
        "aux_type": item.get("aux_type"),
        "uri_type": item.get("uri_type"),
        "content_type": item.get("content_type"),
        "dimensions": item.get("dimensions"),
        "pixi": item.get("pixi"),
        "colr": item.get("colr"),
        "hvcC": item.get("hvcC"),
        "grid": item.get("grid"),
        "tmap": item.get("tmap"),
        "irot": item.get("irot"),
        "payload_bytes": len(payload),
        "payload_sha256": sha256_bytes(payload) if payload else None,
        "derived_payload_bytes": len(derived) if derived else item.get("derived_payload_bytes"),
        "derived_payload_sha256": sha256_bytes(derived) if derived else None,
        "references_from": item.get("references_from", []),
        "references_to": item.get("references_to", []),
        "property_associations": item.get("property_associations", []),
    }
    if source_payload:
        summary["source_payload_bytes"] = len(source_payload)
        summary["source_payload_sha256"] = sha256_bytes(source_payload)
    return summary


def summarize_style_metadata(data: bytes, parsed: dict[str, Any], item_id: int | None) -> dict[str, Any] | None:
    if item_id is None:
        return None
    item = parsed.get("items", {}).get(str(item_id))
    if not item:
        return None
    payload = item_payload(data, item)
    summary: dict[str, Any] = {
        "item_id": item_id,
        "bytes": len(payload),
        "sha256": sha256_bytes(payload) if payload else None,
    }
    try:
        obj = plistlib.loads(payload)
    except Exception as exc:  # noqa: BLE001
        summary["plist_parse_error"] = str(exc)
        return summary
    summary["plist_keys"] = sorted(str(key) for key in obj.keys())
    binary_keys = {}
    numeric_keys = {}
    dict_keys = {}
    for key, value in obj.items():
        skey = str(key)
        if isinstance(value, bytes):
            binary_keys[skey] = {"bytes": len(value), "sha256": sha256_bytes(value)}
        elif isinstance(value, (int, float, bool)):
            numeric_keys[skey] = value
        elif isinstance(value, dict):
            dict_keys[skey] = sorted(str(child_key) for child_key in value.keys())
    summary["binary_keys"] = binary_keys
    summary["scalar_keys"] = numeric_keys
    summary["dict_keys"] = dict_keys
    return summary


def summarize_exiftool(path: Path) -> dict[str, Any]:
    exiftool = shutil.which("exiftool")
    if not exiftool:
        return {"available": False, "error": "exiftool not found"}
    completed = subprocess.run(
        [exiftool, "-G1", "-a", "-s", "-j", str(path)],
        check=False,
        text=True,
        capture_output=True,
    )
    summary: dict[str, Any] = {
        "available": True,
        "returncode": completed.returncode,
        "stderr": completed.stderr.strip(),
    }
    if completed.returncode != 0:
        summary["error"] = completed.stdout.strip()
        return summary
    try:
        rows = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        summary["error"] = str(exc)
        return summary
    row = rows[0] if rows else {}
    keys = sorted(row.keys())
    summary["key_count"] = len(keys)
    summary["has_maker_apple"] = any(key.startswith("MakerApple:") for key in keys)
    summary["has_maker_note"] = any("MakerNote" in key for key in keys)
    summary["has_xmp"] = any(key.startswith("XMP-") for key in keys)
    summary["has_plist"] = any(key.startswith("PLIST:") for key in keys)
    summary["has_semantic_style"] = any("SemanticStyle" in key for key in keys)
    interesting_prefixes = ("MakerApple:", "MakerNotes:", "MakerNote", "PLIST:", "XMP-", "IFD0:", "ExifIFD:")
    summary["interesting_keys"] = [key for key in keys if key.startswith(interesting_prefixes) or "Semantic" in key][:300]
    summary["plist_binary_keys"] = {
        key: row[key]
        for key in keys
        if key.startswith("PLIST:") and isinstance(row.get(key), str) and "Binary data" in row[key]
    }
    return summary


def summarize_imageio_makerapple(paths: list[Path], helper_path: Path | None = None) -> dict[str, dict[str, Any]]:
    swift = shutil.which("swift")
    if not swift:
        return {
            str(path): {"available": False, "error": "swift not found"}
            for path in paths
        }
    if helper_path is None:
        helper_path = Path(__file__).with_name("apple_imageio_metadata.swift")
    if not helper_path.exists():
        return {
            str(path): {"available": False, "error": f"{helper_path} not found"}
            for path in paths
        }
    completed = subprocess.run(
        [swift, str(helper_path), *[str(path) for path in paths]],
        check=False,
        text=True,
        capture_output=True,
    )
    if completed.returncode != 0:
        return {
            str(path): {
                "available": True,
                "returncode": completed.returncode,
                "error": completed.stderr.strip() or completed.stdout.strip(),
            }
            for path in paths
        }
    try:
        rows = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        return {
            str(path): {"available": True, "error": str(exc)}
            for path in paths
        }
    by_path = {
        str(Path(row.get("path", ""))): {"available": True, **row}
        for row in rows
        if row.get("path")
    }
    return {
        str(path): by_path.get(str(path), {"available": True, "error": "missing ImageIO row"})
        for path in paths
    }


def decoded_role_from_path(path: Path) -> str:
    name = path.name.lower()
    if "styledeltamap" in name:
        return "styledeltamap"
    if "linearthumbnail" in name:
        return "linearthumbnail"
    if "hdrgainmap" in name:
        return "hdr_gain_map"
    if "semanticskymatte" in name:
        return "semantic_sky_matte"
    if "semantic" in name:
        return "other_semantic_matte"
    return "unknown_aux"


def decode_aux_diagnostics(
    sample_path: Path,
    decoded_dir: Path,
    *,
    keep_primary_png: bool = False,
) -> dict[str, Any]:
    converter = shutil.which("heif-convert")
    if not converter:
        return {"available": False, "error": "heif-convert not found"}
    decoded_dir.mkdir(parents=True, exist_ok=True)
    base_output = decoded_dir / f"{sample_path.stem}.png"
    completed = subprocess.run(
        [
            converter,
            "--png-compression-level",
            "1",
            "--with-aux",
            "--no-colons",
            str(sample_path),
            str(base_output),
        ],
        check=False,
        text=True,
        capture_output=True,
    )
    result: dict[str, Any] = {
        "available": True,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "output_dir": str(decoded_dir),
        "primary_png": str(base_output) if base_output.exists() else None,
        "images": {},
    }
    if completed.returncode != 0:
        return result
    pngs = sorted(decoded_dir.glob("*.png"))
    role_paths = {}
    for png in pngs:
        if png == base_output:
            continue
        role = decoded_role_from_path(png)
        role_paths.setdefault(role, png)
    base_metric = None
    if base_output.exists():
        base_original = Image.open(base_output).convert("RGB")
        base_metric, _base_downsampled = metric_image(base_original, 1_048_576)
    for role, png in role_paths.items():
        neutral = 128 if role in {"styledeltamap", "linearthumbnail"} else None
        compare = role_paths.get("linearthumbnail") if role == "styledeltamap" else None
        result["images"][role] = compute_decoded_image_stats(
            png,
            neutral_value=neutral,
            base_image=base_metric,
            compare_image_path=compare,
        )
    if base_output.exists():
        result["images"]["primary"] = compute_decoded_image_stats(base_output, max_metric_pixels=1_048_576)
        if not keep_primary_png:
            base_output.unlink()
            result["primary_png_deleted_after_stats"] = True
    return result


def summarize_sample(
    sample_path: Path,
    *,
    sample_output_dir: Path,
    decode_aux: bool,
    keep_primary_png: bool,
    run_exiftool: bool,
    imageio_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    data = sample_path.read_bytes()
    parsed = parse_file(sample_path)
    role_ids = extract_role_item_ids(parsed)
    sample_output_dir.mkdir(parents=True, exist_ok=True)
    heif_json = sample_output_dir / f"{sample_path.stem}.heif_dump.json"
    heif_md = sample_output_dir / f"{sample_path.stem}.heif_dump.md"
    heif_json.write_text(json.dumps(parsed, indent=2, ensure_ascii=False) + "\n")
    heif_md.write_text(format_heif_markdown(parsed))

    role_items = {
        role: _item_payload_summary(data, parsed, item_id)
        for role, item_id in role_ids.items()
    }
    metadata_summary = {
        "style_metadata": summarize_style_metadata(data, parsed, role_ids.get("style_metadata")),
        "exif_item": _item_payload_summary(data, parsed, role_ids.get("exif")),
        "exiftool": summarize_exiftool(sample_path) if run_exiftool else {"available": False, "skipped": True},
        "imageio": imageio_summary or {"available": False, "skipped": True},
    }
    decoded = (
        decode_aux_diagnostics(sample_path, sample_output_dir / "decoded_aux", keep_primary_png=keep_primary_png)
        if decode_aux
        else {"available": False, "skipped": True}
    )
    unknown_items = classify_unknown_items(parsed, role_ids)
    structure = build_structure_signature(parsed)
    sample = {
        "path": str(sample_path),
        "filename": sample_path.name,
        "file_size": len(data),
        "sha256": sha256_bytes(data),
        "is_heif": sample_path.suffix.lower() in {".heic", ".heif", ".hif"},
        "heif_dump_json": str(heif_json),
        "heif_dump_md": str(heif_md),
        "current_tool_can_dump": True,
        "primary_image_dimensions": role_items.get("primary", {}).get("dimensions") if role_items.get("primary") else None,
        "primary_item_id": role_ids.get("primary"),
        "primary_pixi": role_items.get("primary", {}).get("pixi") if role_items.get("primary") else None,
        "primary_color": role_items.get("primary", {}).get("colr") if role_items.get("primary") else None,
        "ftyp": parsed.get("ftyp"),
        "item_count": len(parsed.get("items", {})),
        "role_item_ids": role_ids,
        "role_items": role_items,
        "has_styledeltamap": role_ids.get("styledeltamap") is not None,
        "has_linearthumbnail": role_ids.get("linearthumbnail") is not None,
        "has_hdr_gain_map": role_ids.get("hdr_gain_map") is not None,
        "has_semantic_sky_matte": role_ids.get("semantic_sky_matte") is not None,
        "semantic_mattes": semantic_matte_items(parsed),
        "has_other_semantic_matte": any(
            matte["aux_type"] != SEMANTIC_SKY_MATTE_AUX_TYPE for matte in semantic_matte_items(parsed)
        ),
        "has_style_metadata": role_ids.get("style_metadata") is not None,
        "has_maker_apple": bool(metadata_summary["imageio"].get("has_maker_apple")),
        "has_maker_note": bool(metadata_summary["exiftool"].get("has_maker_note")),
        "metadata_summary": metadata_summary,
        "item_reference_graph_summary": parsed.get("references", []),
        "property_association_summary": {
            item_id: item.get("property_associations", [])
            for item_id, item in parsed.get("items", {}).items()
            if item.get("property_associations")
        },
        "structure_signature": structure,
        "unknown_items": unknown_items,
        "decoded_aux": decoded,
        "current_tool_can_decode_aux_payloads": bool(decoded.get("images")) if decode_aux else False,
        "notes": [],
    }
    if not sample["has_styledeltamap"]:
        sample["notes"].append("No styledeltamap aux item found by auxC type.")
    if not sample["has_linearthumbnail"]:
        sample["notes"].append("No linearthumbnail aux item found by auxC type.")
    return sample


def write_sample_matrix(samples: list[dict[str, Any]], path: Path) -> None:
    fieldnames = [
        "filename",
        "file_size",
        "sha256",
        "item_count",
        "primary_item_id",
        "primary_dimensions",
        "has_styledeltamap",
        "styledeltamap_item_id",
        "styledeltamap_dimensions",
        "styledeltamap_payload_sha256",
        "has_linearthumbnail",
        "linearthumbnail_item_id",
        "linearthumbnail_dimensions",
        "linearthumbnail_payload_sha256",
        "has_hdr_gain_map",
        "hdr_gain_map_item_id",
        "has_semantic_sky_matte",
        "has_other_semantic_matte",
        "has_style_metadata",
        "has_maker_apple",
        "has_maker_note",
        "unknown_item_count",
        "decoded_aux_roles",
        "notes",
    ]
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for sample in samples:
            roles = sample["role_items"]
            decoded_roles = sorted((sample.get("decoded_aux") or {}).get("images", {}).keys())
            writer.writerow(
                {
                    "filename": sample["filename"],
                    "file_size": sample["file_size"],
                    "sha256": sample["sha256"],
                    "item_count": sample["item_count"],
                    "primary_item_id": sample["primary_item_id"],
                    "primary_dimensions": json.dumps(sample.get("primary_image_dimensions"), ensure_ascii=False),
                    "has_styledeltamap": sample["has_styledeltamap"],
                    "styledeltamap_item_id": sample["role_item_ids"].get("styledeltamap"),
                    "styledeltamap_dimensions": json.dumps((roles.get("styledeltamap") or {}).get("dimensions"), ensure_ascii=False),
                    "styledeltamap_payload_sha256": (roles.get("styledeltamap") or {}).get("source_payload_sha256"),
                    "has_linearthumbnail": sample["has_linearthumbnail"],
                    "linearthumbnail_item_id": sample["role_item_ids"].get("linearthumbnail"),
                    "linearthumbnail_dimensions": json.dumps((roles.get("linearthumbnail") or {}).get("dimensions"), ensure_ascii=False),
                    "linearthumbnail_payload_sha256": (roles.get("linearthumbnail") or {}).get("source_payload_sha256"),
                    "has_hdr_gain_map": sample["has_hdr_gain_map"],
                    "hdr_gain_map_item_id": sample["role_item_ids"].get("hdr_gain_map"),
                    "has_semantic_sky_matte": sample["has_semantic_sky_matte"],
                    "has_other_semantic_matte": sample["has_other_semantic_matte"],
                    "has_style_metadata": sample["has_style_metadata"],
                    "has_maker_apple": sample["has_maker_apple"],
                    "has_maker_note": sample["has_maker_note"],
                    "unknown_item_count": len(sample["unknown_items"]),
                    "decoded_aux_roles": ",".join(decoded_roles),
                    "notes": "; ".join(sample["notes"]),
                }
            )


def build_structure_diff(samples: list[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[str, dict[str, Any]] = {}
    for sample in samples:
        signature = sample["structure_signature"]
        key_fields = {
            "item_count": signature["item_count"],
            "aux_types": signature["aux_types"],
            "reference_types": signature["reference_types"],
            "role_dimensions": signature["role_dimensions"],
        }
        key = sha256_bytes(json.dumps(key_fields, sort_keys=True, ensure_ascii=False).encode("utf-8"))
        group = groups.setdefault(key, {"signature_key": key, "signature": key_fields, "samples": []})
        group["samples"].append(sample["filename"])
    aux_presence = {
        "styledeltamap": sorted(sample["filename"] for sample in samples if sample["has_styledeltamap"]),
        "missing_styledeltamap": sorted(sample["filename"] for sample in samples if not sample["has_styledeltamap"]),
        "linearthumbnail": sorted(sample["filename"] for sample in samples if sample["has_linearthumbnail"]),
        "missing_linearthumbnail": sorted(sample["filename"] for sample in samples if not sample["has_linearthumbnail"]),
        "hdr_gain_map": sorted(sample["filename"] for sample in samples if sample["has_hdr_gain_map"]),
        "semantic_sky_matte": sorted(sample["filename"] for sample in samples if sample["has_semantic_sky_matte"]),
        "other_semantic_matte": sorted(sample["filename"] for sample in samples if sample["has_other_semantic_matte"]),
        "style_metadata": sorted(sample["filename"] for sample in samples if sample["has_style_metadata"]),
    }
    duplicate_hashes = defaultdict(list)
    for sample in samples:
        duplicate_hashes[sample["sha256"]].append(sample["filename"])
    return {
        "sample_count": len(samples),
        "structure_groups": sorted(groups.values(), key=lambda group: (-len(group["samples"]), group["samples"])),
        "aux_presence": aux_presence,
        "duplicate_sha256": {
            digest: names
            for digest, names in sorted(duplicate_hashes.items())
            if len(names) > 1
        },
    }


def write_inventory_markdown(samples: list[dict[str, Any]], structure_diff: dict[str, Any], path: Path) -> None:
    lines = [
        "# Apple Native Samples Inventory",
        "",
        f"- Samples: {len(samples)}",
        f"- Structure groups: {len(structure_diff['structure_groups'])}",
        f"- Duplicate SHA-256 groups: {len(structure_diff['duplicate_sha256'])}",
        "",
        "## Presence Summary",
        "",
        "| Feature | Count | Missing |",
        "|---|---:|---|",
    ]
    presence = structure_diff["aux_presence"]
    feature_pairs = [
        ("styledeltamap", "missing_styledeltamap"),
        ("linearthumbnail", "missing_linearthumbnail"),
        ("hdr_gain_map", None),
        ("semantic_sky_matte", None),
        ("other_semantic_matte", None),
        ("style_metadata", None),
    ]
    for present_key, missing_key in feature_pairs:
        missing = presence.get(missing_key, []) if missing_key else []
        lines.append(f"| {present_key} | {len(presence.get(present_key, []))} | {', '.join(missing) or ''} |")
    lines.extend(
        [
            "",
            "## Sample Matrix",
            "",
            "| Sample | Items | Primary | styledeltamap | linearthumbnail | HDR gain map | Sky matte | Style metadata | Unknown | Notes |",
            "|---|---:|---|---|---|---|---|---|---:|---|",
        ]
    )
    for sample in samples:
        roles = sample["role_items"]

        def role_cell(role: str) -> str:
            item = roles.get(role)
            if not item:
                return ""
            dims = item.get("dimensions") or {}
            dim_text = f"{dims.get('width')}x{dims.get('height')}" if dims else ""
            return f"{item.get('item_id')} {dim_text}".strip()

        lines.append(
            "| {name} | {count} | {primary} | {style} | {linear} | {gain} | {sky} | {metadata} | {unknown} | {notes} |".format(
                name=sample["filename"],
                count=sample["item_count"],
                primary=role_cell("primary"),
                style=role_cell("styledeltamap"),
                linear=role_cell("linearthumbnail"),
                gain=role_cell("hdr_gain_map"),
                sky=role_cell("semantic_sky_matte"),
                metadata=role_cell("style_metadata"),
                unknown=len(sample["unknown_items"]),
                notes="; ".join(sample["notes"]),
            )
        )
    lines.append("")
    path.write_text("\n".join(lines))


def write_role_stats(samples: list[dict[str, Any]], output_dir: Path) -> None:
    styledelta = []
    linearthumb = []
    aux = []
    metadata = []
    unknown = []
    graph = []
    for sample in samples:
        for role in ("styledeltamap", "linearthumbnail"):
            item = sample["role_items"].get(role)
            decoded = (sample.get("decoded_aux") or {}).get("images", {}).get(role)
            row = {
                "filename": sample["filename"],
                "item": item,
                "decoded_stats": decoded,
            }
            if role == "styledeltamap":
                styledelta.append(row)
            else:
                linearthumb.append(row)
        aux.append(
            {
                "filename": sample["filename"],
                "roles": {
                    role: sample["role_items"].get(role)
                    for role in ("styledeltamap", "linearthumbnail", "hdr_gain_map", "semantic_sky_matte")
                },
                "semantic_mattes": sample["semantic_mattes"],
                "decoded_aux": sample.get("decoded_aux"),
            }
        )
        metadata.append({"filename": sample["filename"], **sample["metadata_summary"]})
        unknown.append({"filename": sample["filename"], "unknown_items": sample["unknown_items"]})
        graph.append(
            {
                "filename": sample["filename"],
                "references": sample["item_reference_graph_summary"],
                "role_item_ids": sample["role_item_ids"],
                "property_association_summary": sample["property_association_summary"],
            }
        )
    (output_dir / "styledeltamap_stats.json").write_text(json.dumps(styledelta, indent=2, ensure_ascii=False) + "\n")
    (output_dir / "linearthumbnail_stats.json").write_text(json.dumps(linearthumb, indent=2, ensure_ascii=False) + "\n")
    (output_dir / "aux_stats.json").write_text(json.dumps(aux, indent=2, ensure_ascii=False) + "\n")
    (output_dir / "metadata_summary.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n")
    (output_dir / "unknown_items.json").write_text(json.dumps(unknown, indent=2, ensure_ascii=False) + "\n")
    (output_dir / "item_graph_summary.json").write_text(json.dumps(graph, indent=2, ensure_ascii=False) + "\n")


def inventory_directory(
    input_dir: Path,
    output_dir: Path,
    *,
    decode_aux: bool = True,
    keep_primary_png: bool = False,
    run_exiftool: bool = True,
    run_imageio: bool = True,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    sample_paths = sorted(
        path
        for path in input_dir.iterdir()
        if path.is_file() and path.suffix.lower() in {".heic", ".heif", ".hif"}
    )
    imageio_by_path = (
        summarize_imageio_makerapple(sample_paths)
        if run_imageio
        else {str(path): {"available": False, "skipped": True} for path in sample_paths}
    )
    samples = []
    failures = []
    for sample_path in sample_paths:
        sample_dir = output_dir / "samples" / sample_path.stem
        try:
            sample = summarize_sample(
                sample_path,
                sample_output_dir=sample_dir,
                decode_aux=decode_aux,
                keep_primary_png=keep_primary_png,
                run_exiftool=run_exiftool,
                imageio_summary=imageio_by_path.get(str(sample_path)),
            )
        except Exception as exc:  # noqa: BLE001
            failures.append({"path": str(sample_path), "error": repr(exc)})
            continue
        samples.append(sample)
    structure_diff = build_structure_diff(samples)
    inventory = {
        "input_dir": str(input_dir),
        "output_dir": str(output_dir),
        "sample_count": len(samples),
        "failure_count": len(failures),
        "failures": failures,
        "samples": samples,
        "structure_diff": structure_diff,
    }
    (output_dir / "inventory.json").write_text(json.dumps(inventory, indent=2, ensure_ascii=False) + "\n")
    (output_dir / "structure_diff.json").write_text(json.dumps(structure_diff, indent=2, ensure_ascii=False) + "\n")
    write_sample_matrix(samples, output_dir / "sample_matrix.csv")
    write_inventory_markdown(samples, structure_diff, output_dir / "inventory.md")
    write_role_stats(samples, output_dir)
    return inventory


def main() -> int:
    parser = argparse.ArgumentParser(description="Inventory Apple-native Photographic Styles HEIC samples.")
    parser.add_argument("input_dir", type=Path, help="Directory containing Apple native HEIC samples")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--skip-decode-aux", action="store_true", help="Skip heif-convert decoded auxiliary PNG diagnostics")
    parser.add_argument("--keep-primary-png", action="store_true", help="Keep primary PNGs produced by heif-convert")
    parser.add_argument("--skip-exiftool", action="store_true", help="Skip exiftool metadata summary")
    parser.add_argument("--skip-imageio", action="store_true", help="Skip Swift/ImageIO MakerApple summary")
    args = parser.parse_args()

    inventory = inventory_directory(
        args.input_dir,
        args.output_dir,
        decode_aux=not args.skip_decode_aux,
        keep_primary_png=args.keep_primary_png,
        run_exiftool=not args.skip_exiftool,
        run_imageio=not args.skip_imageio,
    )
    print(
        "Inventoried {samples} samples with {failures} failures into {output}".format(
            samples=inventory["sample_count"],
            failures=inventory["failure_count"],
            output=args.output_dir,
        )
    )
    return 1 if inventory["failure_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
