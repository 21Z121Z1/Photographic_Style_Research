#!/usr/bin/env python3
"""Semantic consistency reports for Apple-like styledeltamap HEIF candidates."""

from __future__ import annotations

import argparse
import hashlib
import json
import plistlib
import sys
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.heif_dump import parse_file
from tools.hevc10_encoder import parse_length_prefixed_nals


KEY_ITEMS = ("49", "81", "94", "95", "97", "98", "100", "101", "102")
STYLE_DELTA_AUX_TYPE = "tag:apple.com,2023:photo:aux:styledeltamap"
LINEARTHUMB_AUX_TYPE = "tag:apple.com,2023:photo:aux:linearthumbnail"
HDR_GAINMAP_AUX_TYPE = "urn:com:apple:photo:2020:aux:hdrgainmap"
SEMANTIC_SKY_MATTE_AUX_TYPE = "urn:com:apple:photo:2020:aux:semanticskymatte"
STYLE_METADATA_URI_TYPE = "tag:apple.com,2023:photo:metadata:styles"
DECODED_AUX_FILENAMES = {
    "primary": "decoded.png",
    "styledeltamap": "decoded-tag_apple.com,2023_photo_aux_styledeltamap.png",
    "hdrgainmap": "decoded-urn_com_apple_photo_2020_aux_hdrgainmap.png",
    "linearthumbnail": "decoded-tag_apple.com,2023_photo_aux_linearthumbnail.png",
    "semanticskymatte": "decoded-urn_com_apple_photo_2020_aux_semanticskymatte.png",
}


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _item_payload(data: bytes, item: dict[str, Any]) -> bytes:
    payload = bytearray()
    for extent in item.get("extents", []):
        offset = extent.get("absolute_offset", extent.get("offset", 0))
        length = extent.get("length", 0)
        payload.extend(data[offset : offset + length])
    return bytes(payload)


def _property_payload(parsed: dict[str, Any], data: bytes, property_index: int) -> bytes | None:
    for prop in parsed.get("properties", []):
        if prop.get("index") != property_index:
            continue
        offset = prop.get("offset")
        size = prop.get("size")
        if not isinstance(offset, int) or not isinstance(size, int) or size < 8:
            return None
        return data[offset + 8 : offset + size]
    return None


def _associated_property_payload(
    parsed: dict[str, Any],
    data: bytes,
    item: dict[str, Any],
    property_type: str,
) -> bytes | None:
    for association in item.get("property_associations", []):
        if association.get("type") != property_type:
            continue
        property_index = association.get("property_index")
        if isinstance(property_index, int):
            return _property_payload(parsed, data, property_index)
    return None


def _hevc_nal_summary(payload: bytes) -> dict[str, Any]:
    try:
        nals = parse_length_prefixed_nals(payload)
    except ValueError as exc:
        return {"parse_error": str(exc)}
    return {
        "nal_count": len(nals),
        "nal_types": [nal.nal_type for nal in nals],
        "nal_payload_bytes": [len(nal.payload) for nal in nals],
    }


def _item_summary(parsed: dict[str, Any], data: bytes, item_id: str) -> dict[str, Any] | None:
    item = parsed.get("items", {}).get(item_id)
    if not item:
        return None
    payload = _item_payload(data, item)
    refs_from = item.get("references_from", [])
    irot = item.get("irot")
    summary = {
        "item_id": int(item_id),
        "item_type": item.get("item_type"),
        "hidden": item.get("hidden"),
        "dimensions": item.get("dimensions"),
        "pixi": item.get("pixi"),
        "aux_type": item.get("aux_type"),
        "hvcC": item.get("hvcC"),
        "irot": irot,
        "grid": item.get("grid"),
        "tmap": item.get("tmap"),
        "payload_bytes": len(payload),
        "payload_sha256": _sha256(payload),
        "references_from": refs_from,
    }
    if item.get("item_type") == "hvc1" and payload:
        summary["hevc_nals"] = _hevc_nal_summary(payload)
        hvcc = _associated_property_payload(parsed, data, item, "hvcC")
        if hvcc is not None:
            summary["hvcC_raw"] = {"bytes": len(hvcc), "sha256": _sha256(hvcc)}
    return summary


def _plist_summary(payload: bytes) -> dict[str, Any]:
    try:
        obj = plistlib.loads(payload)
    except Exception as exc:  # noqa: BLE001
        return {"parse_error": str(exc)}
    result: dict[str, Any] = {"keys": sorted(obj.keys())}
    key6 = obj.get("6")
    if isinstance(key6, dict):
        result["key6"] = {}
        for family_name in ("LinearImage", "ToneMappedImage", "LinearGTCImage"):
            family = key6.get(family_name)
            if isinstance(family, dict):
                result["key6"][family_name] = {
                    key: round(float(value), 9)
                    for key, value in sorted(family.items())
                    if isinstance(value, (int, float))
                }
    for key in ("1", "3", "c", "d"):
        value = obj.get(key)
        if isinstance(value, bytes):
            result.setdefault("binary_keys", {})[key] = {
                "bytes": len(value),
                "sha256": _sha256(value),
            }
    key_i = obj.get("i")
    if isinstance(key_i, dict):
        result["gain_summary"] = {
            key: round(float(value), 9)
            for key, value in sorted(key_i.items())
            if isinstance(value, (int, float))
        }
    return result


def _decoded_stats(decoded_dir: Path | None) -> dict[str, Any]:
    if decoded_dir is None:
        return {}
    stats: dict[str, Any] = {}
    for label, filename in DECODED_AUX_FILENAMES.items():
        path = decoded_dir / filename
        if not path.exists():
            continue
        image = Image.open(path)
        arr = np.asarray(image)
        flat = arr.reshape(-1, arr.shape[-1]) if arr.ndim == 3 else arr.reshape(-1)
        stats[label] = {
            "path": str(path),
            "mode": image.mode,
            "size": {"width": image.size[0], "height": image.size[1]},
            "min": np.min(flat, axis=0).tolist() if arr.ndim == 3 else int(np.min(flat)),
            "max": np.max(flat, axis=0).tolist() if arr.ndim == 3 else int(np.max(flat)),
            "mean": np.round(np.mean(flat, axis=0), 6).tolist() if arr.ndim == 3 else round(float(np.mean(flat)), 6),
            "std": np.round(np.std(flat, axis=0), 6).tolist() if arr.ndim == 3 else round(float(np.std(flat)), 6),
            "unique_values": int(len(np.unique(flat, axis=0))) if arr.ndim == 3 else int(len(np.unique(flat))),
        }
    return stats


def _payload_hashes(parsed: dict[str, Any], data: bytes) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for item_id in KEY_ITEMS:
        item = parsed.get("items", {}).get(item_id)
        if item:
            hashes[item_id] = _sha256(_item_payload(data, item))
    return hashes


def _first_item_id(parsed: dict[str, Any], predicate) -> str | None:
    for item_id, item in parsed.get("items", {}).items():
        if predicate(item):
            return item_id
    return None


def _role_item_ids(parsed: dict[str, Any]) -> dict[str, str | None]:
    primary = parsed.get("primary_item_id")
    return {
        "primary": str(primary) if primary is not None else None,
        "styledeltamap": _first_item_id(parsed, lambda item: item.get("aux_type") == STYLE_DELTA_AUX_TYPE),
        "hdrgainmap": _first_item_id(parsed, lambda item: item.get("aux_type") == HDR_GAINMAP_AUX_TYPE),
        "semanticskymatte": _first_item_id(parsed, lambda item: item.get("aux_type") == SEMANTIC_SKY_MATTE_AUX_TYPE),
        "linearthumbnail": _first_item_id(parsed, lambda item: item.get("aux_type") == LINEARTHUMB_AUX_TYPE),
        "tmap": _first_item_id(parsed, lambda item: item.get("item_type") == "tmap"),
        "style_metadata": _first_item_id(
            parsed,
            lambda item: item.get("item_type") == "uri " and item.get("uri_type") == STYLE_METADATA_URI_TYPE,
        ),
        "exif": _first_item_id(parsed, lambda item: item.get("item_type") == "Exif"),
    }


def _refs_exact(item: dict[str, Any], ref_type: str, to_item_ids: list[int]) -> bool:
    return any(
        ref.get("type") == ref_type and ref.get("to_item_ids") == to_item_ids
        for ref in item.get("references_from", [])
    )


def build_report(
    candidate_path: Path,
    *,
    reference_path: Path | None = None,
    template_path: Path | None = None,
    decoded_dir: Path | None = None,
) -> dict[str, Any]:
    candidate_data = candidate_path.read_bytes()
    candidate = parse_file(candidate_path)
    report: dict[str, Any] = {
        "candidate": str(candidate_path),
        "candidate_sha256": _sha256(candidate_data),
        "primary_item_id": candidate.get("primary_item_id"),
        "ftyp": candidate.get("ftyp"),
        "key_items": {
            item_id: _item_summary(candidate, candidate_data, item_id)
            for item_id in KEY_ITEMS
        },
        "irot_properties": [
            prop for prop in candidate.get("properties", []) if prop.get("type") == "irot"
        ],
        "decoded_stats": _decoded_stats(decoded_dir),
        "hard_warnings": [],
    }
    role_item_ids = _role_item_ids(candidate)
    report["role_item_ids"] = role_item_ids
    report["role_items"] = {
        role: _item_summary(candidate, candidate_data, item_id) if item_id else None
        for role, item_id in role_item_ids.items()
    }
    style_metadata_role = report["role_items"].get("style_metadata") or {}
    if style_metadata_role.get("item_id") is not None:
        item = candidate.get("items", {}).get(str(style_metadata_role["item_id"]))
        if item:
            report["style_metadata"] = _plist_summary(_item_payload(candidate_data, item))

    for prop in report["irot_properties"]:
        parsed = prop.get("parsed", {})
        if parsed.get("payload_bytes") != 1:
            report["hard_warnings"].append(
                f"irot property {prop.get('index')} has {parsed.get('payload_bytes')} payload bytes"
            )
    primary_item = report["role_items"].get("primary") or {}
    primary_id = primary_item.get("item_id")
    tmap_item = report["role_items"].get("tmap") or {}
    tmap_id = tmap_item.get("item_id")
    gainmap_item = report["role_items"].get("hdrgainmap") or {}
    gainmap_id = gainmap_item.get("item_id")
    style_item = report["role_items"].get("styledeltamap") or {}
    if not style_item:
        report["hard_warnings"].append("styledeltamap auxiliary item was not found")
    elif primary_id is not None:
        expected = [primary_id, tmap_id] if tmap_id is not None else [primary_id]
        if not _refs_exact(style_item, "auxl", expected):
            report["hard_warnings"].append(
                f"styledeltamap item does not auxl-reference expected items {expected}: refs={style_item.get('references_from')}"
            )

    if tmap_item and primary_item:
        primary_dims = primary_item.get("dimensions")
        tmap_dims = tmap_item.get("dimensions")
        swapped_primary_dims = (
            {"width": primary_dims["height"], "height": primary_dims["width"]}
            if isinstance(primary_dims, dict) and "width" in primary_dims and "height" in primary_dims
            else None
        )
    else:
        primary_dims = None
        tmap_dims = None
        swapped_primary_dims = None
    if tmap_item and primary_item and tmap_dims not in (primary_dims, swapped_primary_dims):
        report["hard_warnings"].append(
            f"tmap dimensions {tmap_dims} do not match primary dimensions {primary_dims}"
        )
    if tmap_item and primary_id is not None and gainmap_id is not None:
        if not _refs_exact(tmap_item, "dimg", [primary_id, gainmap_id]):
            report["hard_warnings"].append(
                f"tmap item does not dimg-reference [primary, gainmap] {[primary_id, gainmap_id]}: refs={tmap_item.get('references_from')}"
            )

    linearthumb_item = report["role_items"].get("linearthumbnail") or {}
    if linearthumb_item.get("aux_type") == LINEARTHUMB_AUX_TYPE:
        nal_summary = linearthumb_item.get("hevc_nals") or {}
        nal_types = nal_summary.get("nal_types")
        if nal_types is None:
            report["hard_warnings"].append("linearthumbnail item payload NAL layout could not be parsed")
        elif len(nal_types) != 1 or nal_types[0] not in (19, 20):
            report["hard_warnings"].append(
                f"linearthumbnail item payload is not Apple single-IDR profile: nal_types={nal_types}"
            )
        if primary_id is not None and tmap_id is not None and not _refs_exact(linearthumb_item, "auxl", [primary_id, tmap_id]):
            report["hard_warnings"].append(
                f"linearthumbnail item does not auxl-reference primary/tmap items {[primary_id, tmap_id]}: refs={linearthumb_item.get('references_from')}"
            )
    else:
        report["hard_warnings"].append("linearthumbnail auxiliary item was not found")

    candidate_hashes = _payload_hashes(candidate, candidate_data)
    comparisons: dict[str, Any] = {}
    for label, path in (("reference", reference_path), ("template", template_path)):
        if path is None:
            continue
        data = path.read_bytes()
        parsed = parse_file(path)
        hashes = _payload_hashes(parsed, data)
        comparisons[label] = {
            "path": str(path),
            "sha256": _sha256(data),
            "payload_hash_equal": {
                item_id: candidate_hashes.get(item_id) == hashes.get(item_id)
                for item_id in sorted(set(candidate_hashes) | set(hashes), key=int)
            },
            "key_items": {
                item_id: _item_summary(parsed, data, item_id)
                for item_id in KEY_ITEMS
            },
        }
    report["comparisons"] = comparisons
    return report


def format_markdown(report: dict[str, Any]) -> str:
    lines = [
        f"# Semantic Fitting Report: `{report['candidate']}`",
        "",
        f"- Candidate SHA-256: `{report['candidate_sha256']}`",
        f"- Primary item id: {report.get('primary_item_id')}",
        f"- Hard warnings: {len(report.get('hard_warnings', []))}",
    ]
    for warning in report.get("hard_warnings", []):
        lines.append(f"  - {warning}")
    if report.get("role_items"):
        lines.extend(["", "## Role Items", ""])
        lines.append("| Role | Item | Type | Dimensions | Aux Type | Refs |")
        lines.append("|---|---:|---|---|---|---|")
        for role, item in report["role_items"].items():
            if not item:
                lines.append(f"| {role} |  |  |  |  |  |")
                continue
            refs = [
                f"{ref.get('type')}->{ref.get('to_item_ids')}"
                for ref in item.get("references_from", [])
            ]
            lines.append(
                "| {role} | {item_id} | `{item_type}` | {dimensions} | {aux_type} | {refs} |".format(
                    role=role,
                    item_id=item.get("item_id"),
                    item_type=item.get("item_type"),
                    dimensions=item.get("dimensions"),
                    aux_type=item.get("aux_type") or "",
                    refs=", ".join(refs),
                )
            )
    lines.extend(["", "## Key Items", ""])
    lines.append("| Item | Type | Dimensions | Aux Type | Payload Bytes | NAL Types | Refs | SHA-256 | irot |")
    lines.append("|---:|---|---|---|---:|---|---|---|---|")
    for item_id in KEY_ITEMS:
        item = report["key_items"].get(item_id)
        if not item:
            continue
        irot = item.get("irot") or {}
        hevc_nals = item.get("hevc_nals") or {}
        nal_types = hevc_nals.get("nal_types", "")
        refs = [
            f"{ref.get('type')}->{ref.get('to_item_ids')}"
            for ref in item.get("references_from", [])
        ]
        lines.append(
            "| {item_id} | `{item_type}` | {dimensions} | {aux_type} | {payload_bytes} | {nal_types} | {refs} | `{sha}` | {irot} |".format(
                item_id=item_id,
                item_type=item.get("item_type"),
                dimensions=item.get("dimensions"),
                aux_type=item.get("aux_type") or "",
                payload_bytes=item.get("payload_bytes"),
                nal_types=nal_types,
                refs=", ".join(refs),
                sha=(item.get("payload_sha256") or "")[:16],
                irot=irot,
            )
        )
    if report.get("decoded_stats"):
        lines.extend(["", "## Decoded Stats", ""])
        lines.append("| Image | Size | Mean | Std | Unique |")
        lines.append("|---|---|---|---|---:|")
        for label, stats in report["decoded_stats"].items():
            lines.append(
                f"| {label} | {stats['size']} | {stats['mean']} | {stats['std']} | {stats['unique_values']} |"
            )
    style_metadata = report.get("style_metadata")
    if style_metadata:
        lines.extend(["", "## Style Metadata", ""])
        lines.append(f"- Keys: `{', '.join(style_metadata.get('keys', []))}`")
        if "binary_keys" in style_metadata:
            for key, value in style_metadata["binary_keys"].items():
                lines.append(f"- Binary key `{key}`: {value['bytes']} bytes, `{value['sha256'][:16]}`")
        if "gain_summary" in style_metadata:
            lines.append(f"- Gain summary: `{style_metadata['gain_summary']}`")
    if report.get("comparisons"):
        lines.extend(["", "## Payload Hash Comparisons", ""])
        for label, comparison in report["comparisons"].items():
            lines.append(f"### {label}: `{comparison['path']}`")
            equal_items = [
                item_id
                for item_id, equal in comparison["payload_hash_equal"].items()
                if equal
            ]
            different_items = [
                item_id
                for item_id, equal in comparison["payload_hash_equal"].items()
                if not equal
            ]
            lines.append(f"- Equal key items: {', '.join(equal_items) or 'none'}")
            lines.append(f"- Different key items: {', '.join(different_items) or 'none'}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a styledeltamap semantic consistency report.")
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--reference", type=Path)
    parser.add_argument("--template", type=Path)
    parser.add_argument("--decoded-dir", type=Path)
    parser.add_argument("--json", dest="json_path", type=Path, required=True)
    parser.add_argument("--md", dest="markdown_path", type=Path, required=True)
    args = parser.parse_args()

    report = build_report(
        args.candidate,
        reference_path=args.reference,
        template_path=args.template,
        decoded_dir=args.decoded_dir,
    )
    args.json_path.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_path.parent.mkdir(parents=True, exist_ok=True)
    args.json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    args.markdown_path.write_text(format_markdown(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
