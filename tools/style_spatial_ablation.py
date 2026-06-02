#!/usr/bin/env python3
"""Generate Photographic Styles spatial-source ablation HEICs."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.heif_aux_writer import _box, _full_box, _u16, _u32, _u64, encode_image_payload
from tools.heif_dump import STYLE_DELTA_AUX_TYPE, iter_boxes, parse_file, parse_heif
from tools.hevc10_encoder import encode_hevc10_still_videotoolbox, encode_hevc10_tile
from tools.semantic_fitter import build_report as build_semantic_report
from tools.semantic_fitter import format_markdown as format_semantic_markdown
from tools.styledeltamap_diagnostics import analyze_file as analyze_aux_file
from tools.styledeltamap_diagnostics import format_markdown as format_aux_markdown


LINEARTHUMB_AUX_TYPE = "tag:apple.com,2023:photo:aux:linearthumbnail"
HDR_GAINMAP_AUX_TYPE = "urn:com:apple:photo:2020:aux:hdrgainmap"
SEMANTIC_SKY_MATTE_AUX_TYPE = "urn:com:apple:photo:2020:aux:semanticskymatte"
STYLE_METADATA_URI_TYPE = "tag:apple.com,2023:photo:metadata:styles"
DEFAULT_BASELINE = Path(
    "artifacts/constructed/apple_style_injected_from_preview_heic_v1/"
    "apple_style_injected_from_preview_heic_v1.heic"
)
DEFAULT_DONOR = Path("Apple_Native_Samples/IMG_0033.HEIC")


@dataclass(frozen=True)
class RoleInfo:
    role: str
    item_id: int
    item_type: str | None
    aux_type: str | None
    dimensions: dict[str, int] | None
    child_item_ids: list[int]


@dataclass(frozen=True)
class LoadedSource:
    path: Path
    data: bytes
    parsed: dict[str, Any]
    top_boxes: list[dict[str, Any]]
    meta_box: dict[str, Any]
    meta_header: bytes
    meta_children: list[dict[str, Any]]
    item_payloads: dict[int, bytes]
    construction_methods: dict[int, int]
    item_order: list[int]
    idat_item_order: list[int]


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _raw_box(data: bytes, box_info: dict[str, Any]) -> bytes:
    return data[box_info["offset"] : box_info["offset"] + box_info["size"]]


def _payload_from_extents(data: bytes, item: dict[str, Any]) -> bytes:
    payload = bytearray()
    for extent in item.get("extents", []):
        offset = int(extent.get("absolute_offset", extent.get("offset", 0)))
        length = int(extent.get("length", 0))
        payload.extend(data[offset : offset + length])
    return bytes(payload)


def _load_source(path: Path) -> LoadedSource:
    data = path.read_bytes()
    parsed = parse_heif(data, str(path))
    top_boxes = iter_boxes(data)
    meta_box = next((box for box in top_boxes if box["type"] == "meta"), None)
    if meta_box is None:
        raise ValueError(f"{path} has no meta box")
    meta_header = data[meta_box["payload_offset"] : meta_box["payload_offset"] + 4]
    meta_children = iter_boxes(
        data,
        meta_box["payload_offset"] + 4,
        meta_box["payload_offset"] + meta_box["payload_size"],
    )
    item_payloads = {
        int(item_id): _payload_from_extents(data, item)
        for item_id, item in parsed.get("items", {}).items()
        if item.get("extents")
    }
    construction_methods = {
        int(item_id): int(item.get("construction_method", 0))
        for item_id, item in parsed.get("items", {}).items()
    }
    item_order = sorted(int(item_id) for item_id in parsed.get("items", {}))
    idat_item_order = sorted(
        (item_id for item_id, method in construction_methods.items() if method == 1),
        key=lambda item_id: parsed["items"][str(item_id)]["extents"][0]["absolute_offset"],
    )
    return LoadedSource(
        path=path,
        data=data,
        parsed=parsed,
        top_boxes=top_boxes,
        meta_box=meta_box,
        meta_header=meta_header,
        meta_children=meta_children,
        item_payloads=item_payloads,
        construction_methods=construction_methods,
        item_order=item_order,
        idat_item_order=idat_item_order,
    )


def _child_ids(item: dict[str, Any]) -> list[int]:
    if item.get("derived_child_item_ids"):
        return [int(item_id) for item_id in item["derived_child_item_ids"]]
    for ref in item.get("references_from", []):
        if ref.get("type") == "dimg":
            return [int(item_id) for item_id in ref.get("to_item_ids", [])]
    return []


def _role_item_id(parsed: dict[str, Any], role: str) -> int | None:
    if role == "primary":
        primary = parsed.get("primary_item_id")
        return int(primary) if primary is not None else None
    for item_id, item in parsed.get("items", {}).items():
        if role == "styledeltamap" and item.get("aux_type") == STYLE_DELTA_AUX_TYPE:
            return int(item_id)
        if role == "hdrgainmap" and item.get("aux_type") == HDR_GAINMAP_AUX_TYPE:
            return int(item_id)
        if role == "semanticskymatte" and item.get("aux_type") == SEMANTIC_SKY_MATTE_AUX_TYPE:
            return int(item_id)
        if role == "linearthumbnail" and item.get("aux_type") == LINEARTHUMB_AUX_TYPE:
            return int(item_id)
        if role == "tmap" and item.get("item_type") == "tmap":
            return int(item_id)
        if (
            role == "style_metadata"
            and item.get("item_type") == "uri "
            and item.get("uri_type") == STYLE_METADATA_URI_TYPE
        ):
            return int(item_id)
        if role == "exif" and item.get("item_type") == "Exif":
            return int(item_id)
    return None


def build_role_inventory(path: Path) -> dict[str, RoleInfo]:
    parsed = parse_file(path)
    inventory: dict[str, RoleInfo] = {}
    for role in (
        "primary",
        "styledeltamap",
        "hdrgainmap",
        "semanticskymatte",
        "linearthumbnail",
        "tmap",
        "style_metadata",
        "exif",
    ):
        item_id = _role_item_id(parsed, role)
        if item_id is None:
            continue
        item = parsed["items"][str(item_id)]
        inventory[role] = RoleInfo(
            role=role,
            item_id=item_id,
            item_type=item.get("item_type"),
            aux_type=item.get("aux_type"),
            dimensions=item.get("dimensions"),
            child_item_ids=_child_ids(item),
        )
    return inventory


def build_manual_photos_fields() -> dict[str, str | bool | None]:
    return {
        "imports_into_photos": None,
        "styles_ui_activates": None,
        "tone_slider_response": None,
        "color_slider_response": None,
        "has_spatial_structure": None,
        "spatial_structure_follows": "",
        "low_frequency_only": None,
        "no_response": None,
        "notes": "",
    }


def manifest_entry(
    *,
    name: str,
    output: Path,
    perturbation: str,
    changed_roles: list[str],
    validation: dict[str, Any],
) -> dict[str, Any]:
    return {
        "name": name,
        "output_file": str(output),
        "perturbation": perturbation,
        "changed_roles": changed_roles,
        "validation": validation,
        "manual_photos_verification": build_manual_photos_fields(),
    }


def compare_role_hashes(
    before: dict[str, str | None],
    after: dict[str, str | None],
) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for role in sorted(set(before) | set(after)):
        before_hash = before.get(role)
        after_hash = after.get(role)
        result[role] = {
            "before": before_hash,
            "after": after_hash,
            "changed": before_hash != after_hash,
        }
    return result


def copy_baseline_variant(source: Path, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, output)


def _hvcC_property_indices(parsed: dict[str, Any], item_ids: list[int]) -> set[int]:
    indices: set[int] = set()
    for item_id in item_ids:
        item = parsed.get("items", {}).get(str(item_id), {})
        for assoc in item.get("property_associations", []):
            if assoc.get("type") == "hvcC":
                indices.add(int(assoc["property_index"]))
    return indices


def _replace_iprp_hvcc(source: LoadedSource, iprp_box: dict[str, Any], hvcc_replacements: dict[int, bytes]) -> bytes:
    if not hvcc_replacements:
        return _raw_box(source.data, iprp_box)
    children = iter_boxes(
        source.data,
        iprp_box["payload_offset"],
        iprp_box["payload_offset"] + iprp_box["payload_size"],
    )
    rebuilt_children: list[bytes] = []
    for child in children:
        if child["type"] != "ipco":
            rebuilt_children.append(_raw_box(source.data, child))
            continue
        property_boxes = iter_boxes(
            source.data,
            child["payload_offset"],
            child["payload_offset"] + child["payload_size"],
        )
        rebuilt_props: list[bytes] = []
        for index, prop in enumerate(property_boxes, start=1):
            if index in hvcc_replacements:
                rebuilt_props.append(_box("hvcC", hvcc_replacements[index]))
            else:
                rebuilt_props.append(_raw_box(source.data, prop))
        rebuilt_children.append(_box("ipco", b"".join(rebuilt_props)))
    return _box("iprp", b"".join(rebuilt_children))


def _build_iloc_and_payloads(
    source: LoadedSource,
    payloads: dict[int, bytes],
    mdat_payload_start: int,
) -> tuple[bytes, bytes, bytes]:
    iloc_payload = bytes([0x44, 0x80]) + _u16(len(source.item_order))
    idat_parts: list[bytes] = []
    mdat_parts: list[bytes] = []
    idat_offsets: dict[int, int] = {}
    idat_cursor = 0
    for item_id in source.idat_item_order:
        idat_offsets[item_id] = idat_cursor
        payload = payloads.get(item_id, b"")
        idat_parts.append(payload)
        idat_cursor += len(payload)
    mdat_cursor = 0
    for item_id in source.item_order:
        payload = payloads.get(item_id, b"")
        method = source.construction_methods.get(item_id, 0)
        if method == 1:
            base_offset = 0
            extent_offset = idat_offsets[item_id]
        elif method == 0:
            base_offset = mdat_payload_start + mdat_cursor
            extent_offset = 0
            mdat_parts.append(payload)
            mdat_cursor += len(payload)
        else:
            raise ValueError(f"unsupported construction method {method} for item {item_id}")
        iloc_payload += (
            _u16(item_id)
            + _u16(method)
            + _u16(0)
            + _u64(base_offset)
            + _u16(1)
            + _u32(extent_offset)
            + _u32(len(payload))
        )
    return _full_box("iloc", version=1, payload=iloc_payload), b"".join(idat_parts), b"".join(mdat_parts)


def _build_meta(source: LoadedSource, idat_payload: bytes, iloc: bytes, hvcc_replacements: dict[int, bytes]) -> bytes:
    children: list[bytes] = []
    wrote_idat = False
    wrote_iloc = False
    for child in source.meta_children:
        if child["type"] == "idat":
            children.append(_box("idat", idat_payload))
            wrote_idat = True
        elif child["type"] == "iloc":
            if not wrote_idat:
                children.append(_box("idat", idat_payload))
                wrote_idat = True
            children.append(iloc)
            wrote_iloc = True
        elif child["type"] == "iprp":
            children.append(_replace_iprp_hvcc(source, child, hvcc_replacements))
        else:
            children.append(_raw_box(source.data, child))
    if not wrote_idat:
        children.append(_box("idat", idat_payload))
    if not wrote_iloc:
        children.append(iloc)
    return _box("meta", source.meta_header + b"".join(children))


def write_with_replaced_payloads(
    source_path: Path,
    output: Path,
    replacements: dict[int, bytes],
    *,
    hvcc_replacements: dict[int, bytes] | None = None,
) -> None:
    source = _load_source(source_path)
    payloads = dict(source.item_payloads)
    payloads.update(replacements)
    hvcc_replacements = hvcc_replacements or {}
    iloc_placeholder, idat_payload, mdat_payload = _build_iloc_and_payloads(source, payloads, mdat_payload_start=0)
    meta_placeholder = _build_meta(source, idat_payload, iloc_placeholder, hvcc_replacements)
    mdat_payload_start = sum(
        len(_raw_box(source.data, box))
        for box in source.top_boxes
        if box["offset"] < source.meta_box["offset"] and box["type"] != "mdat"
    ) + len(meta_placeholder) + 8
    iloc, idat_payload, mdat_payload = _build_iloc_and_payloads(
        source,
        payloads,
        mdat_payload_start=mdat_payload_start,
    )
    meta = _build_meta(source, idat_payload, iloc, hvcc_replacements)
    if len(meta) != len(meta_placeholder):
        raise RuntimeError("meta size changed after resolving mdat offsets")

    output_parts: list[bytes] = []
    wrote_meta = False
    wrote_mdat = False
    for box in source.top_boxes:
        if box["type"] == "meta":
            output_parts.append(meta)
            wrote_meta = True
        elif box["type"] == "mdat":
            output_parts.append(_box("mdat", mdat_payload))
            wrote_mdat = True
        else:
            output_parts.append(_raw_box(source.data, box))
    if not wrote_meta:
        output_parts.append(meta)
    if not wrote_mdat:
        output_parts.append(_box("mdat", mdat_payload))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(b"".join(output_parts))


def neutral_rgb_image(size: tuple[int, int], value: int = 128) -> Image.Image:
    return Image.new("RGB", size, (value, value, value))


def black_l_image(size: tuple[int, int]) -> Image.Image:
    return Image.new("L", size, 0)


def white_l_image(size: tuple[int, int]) -> Image.Image:
    return Image.new("L", size, 255)


def shift_image_x(image: Image.Image, pixels: int) -> Image.Image:
    pixels = int(pixels)
    if pixels == 0:
        return image.copy()
    result = Image.new(image.mode, image.size)
    width, _height = image.size
    result.paste(image.crop((0, 0, width - pixels, image.height)), (pixels, 0))
    result.paste(image.crop((width - pixels, 0, width, image.height)), (0, 0))
    return result


def _role_payload_hashes(path: Path) -> dict[str, str | None]:
    loaded = _load_source(path)
    inventory = build_role_inventory(path)
    hashes: dict[str, str | None] = {}
    for role, info in inventory.items():
        item_ids = [info.item_id, *info.child_item_ids]
        digest = hashlib.sha256()
        seen = False
        for item_id in item_ids:
            payload = loaded.item_payloads.get(item_id)
            if payload is None:
                continue
            digest.update(item_id.to_bytes(4, "big"))
            digest.update(payload)
            seen = True
        hashes[role] = digest.hexdigest() if seen else None
    return hashes


def _grid_tile_layout(source: LoadedSource, role: RoleInfo) -> tuple[int, int, int, int]:
    item = source.parsed["items"][str(role.item_id)]
    grid = item.get("grid") or {}
    rows = int(grid.get("rows") or 1)
    columns = int(grid.get("columns") or max(len(role.child_item_ids), 1))
    first_child = source.parsed["items"][str(role.child_item_ids[0])]
    dims = first_child.get("dimensions") or {"width": 512, "height": 512}
    return rows, columns, int(dims["width"]), int(dims["height"])


def _encode_primary_neutral(source: LoadedSource, role: RoleInfo, value: int = 128) -> tuple[dict[int, bytes], dict[int, bytes]]:
    rows, columns, tile_w, tile_h = _grid_tile_layout(source, role)
    active_w = int((role.dimensions or {}).get("width") or columns * tile_w)
    active_h = int((role.dimensions or {}).get("height") or rows * tile_h)
    canvas = Image.new("RGB", (columns * tile_w, rows * tile_h), (0, 0, 0))
    canvas.paste(neutral_rgb_image((active_w, active_h), value=value), (0, 0))
    replacements: dict[int, bytes] = {}
    common_hvcc: bytes | None = None
    for index, item_id in enumerate(role.child_item_ids):
        row = index // columns
        col = index % columns
        tile = canvas.crop((col * tile_w, row * tile_h, (col + 1) * tile_w, (row + 1) * tile_h))
        encoded = encode_image_payload(tile)
        replacements[item_id] = encoded.payload
        common_hvcc = common_hvcc or encoded.hvcc
    hvcc = {
        index: common_hvcc
        for index in _hvcC_property_indices(source.parsed, role.child_item_ids)
        if common_hvcc is not None
    }
    return replacements, hvcc


def _encode_hevc10_grid(
    source: LoadedSource,
    role: RoleInfo,
    image: Image.Image,
    *,
    crf: int,
) -> tuple[dict[int, bytes], dict[int, bytes]]:
    rows, columns, tile_w, tile_h = _grid_tile_layout(source, role)
    active_w = int((role.dimensions or {}).get("width") or image.size[0])
    active_h = int((role.dimensions or {}).get("height") or image.size[1])
    active = image.convert("RGB").resize((active_w, active_h), Image.Resampling.BILINEAR)
    canvas = Image.new("RGB", (columns * tile_w, rows * tile_h), (0, 0, 0))
    canvas.paste(active, (0, 0))
    replacements: dict[int, bytes] = {}
    common_hvcc: bytes | None = None
    for index, item_id in enumerate(role.child_item_ids):
        row = index // columns
        col = index % columns
        tile = canvas.crop((col * tile_w, row * tile_h, (col + 1) * tile_w, (row + 1) * tile_h))
        payload, hvcc = encode_hevc10_tile(tile, crf=crf)
        replacements[item_id] = payload
        common_hvcc = common_hvcc or hvcc
    hvcc_replacements = {
        index: common_hvcc
        for index in _hvcC_property_indices(source.parsed, role.child_item_ids)
        if common_hvcc is not None
    }
    return replacements, hvcc_replacements


def _encode_single_hevc10(
    source: LoadedSource,
    role: RoleInfo,
    image: Image.Image,
    *,
    encoder: str,
    crf: int,
    vt_quality: float,
) -> tuple[dict[int, bytes], dict[int, bytes], dict[str, Any]]:
    size = (int(role.dimensions["width"]), int(role.dimensions["height"])) if role.dimensions else image.size
    encoded_image = image.convert("RGB").resize(size, Image.Resampling.BILINEAR)
    if encoder == "videotoolbox":
        payload, hvcc = encode_hevc10_still_videotoolbox(
            encoded_image,
            item_payload_policy="single_idr",
            quality=vt_quality,
        )
    elif encoder == "x265":
        payload, hvcc = encode_hevc10_tile(
            encoded_image,
            crf=crf,
            level_idc=3.1,
            full_range=True,
            item_payload_policy="single_idr",
        )
    else:
        raise ValueError(f"unsupported linearthumb encoder {encoder!r}")
    hvcC_indices = _hvcC_property_indices(source.parsed, [role.item_id])
    return (
        {role.item_id: payload},
        {index: hvcc for index in hvcC_indices},
        {"encoder": encoder, "payload_bytes": len(payload), "hvcC_bytes": len(hvcc)},
    )


def _encode_single_8bit(
    source: LoadedSource,
    role: RoleInfo,
    image: Image.Image,
) -> tuple[dict[int, bytes], dict[int, bytes], dict[str, Any]]:
    size = (int(role.dimensions["width"]), int(role.dimensions["height"])) if role.dimensions else image.size
    encoded_image = image.convert("RGB").resize(size, Image.Resampling.BILINEAR)
    encoded = encode_image_payload(encoded_image)
    hvcC_indices = _hvcC_property_indices(source.parsed, [role.item_id])
    return (
        {role.item_id: encoded.payload},
        {index: encoded.hvcc for index in hvcC_indices},
        {"encoder": "pillow-heif", "payload_bytes": len(encoded.payload), "hvcC_bytes": len(encoded.hvcc)},
    )


def _decode_aux_images(input_path: Path, output_dir: Path) -> dict[str, Path]:
    converter = shutil.which("heif-convert")
    if not converter:
        raise RuntimeError("heif-convert not found in PATH")
    output_dir.mkdir(parents=True, exist_ok=True)
    base_output = output_dir / "decoded.png"
    subprocess.run(
        [converter, "--with-aux", "--no-colons", str(input_path), str(base_output)],
        check=True,
        text=True,
        capture_output=True,
    )
    return {
        "primary": base_output,
        "styledeltamap": output_dir / "decoded-tag_apple.com,2023_photo_aux_styledeltamap.png",
        "hdrgainmap": output_dir / "decoded-urn_com_apple_photo_2020_aux_hdrgainmap.png",
        "semanticskymatte": output_dir / "decoded-urn_com_apple_photo_2020_aux_semanticskymatte.png",
        "linearthumbnail": output_dir / "decoded-tag_apple.com,2023_photo_aux_linearthumbnail.png",
    }


def _image_stats(path: Path) -> dict[str, Any]:
    image = Image.open(path)
    arr = np.asarray(image)
    flat = arr.reshape(-1, arr.shape[-1]) if arr.ndim == 3 else arr.reshape(-1)
    return {
        "path": str(path),
        "mode": image.mode,
        "size": {"width": image.size[0], "height": image.size[1]},
        "min": np.min(flat, axis=0).tolist() if arr.ndim == 3 else int(np.min(flat)),
        "max": np.max(flat, axis=0).tolist() if arr.ndim == 3 else int(np.max(flat)),
        "mean": np.round(np.mean(flat, axis=0), 6).tolist() if arr.ndim == 3 else round(float(np.mean(flat)), 6),
        "std": np.round(np.std(flat, axis=0), 6).tolist() if arr.ndim == 3 else round(float(np.std(flat)), 6),
    }


def _payload_for_role(path: Path, role: str) -> bytes | None:
    loaded = _load_source(path)
    inventory = build_role_inventory(path)
    info = inventory.get(role)
    if info is None:
        return None
    return loaded.item_payloads.get(info.item_id)


def _variant_readme_table(entries: list[dict[str, Any]]) -> str:
    header = (
        "| Variant | Imports into Photos | Styles UI activates | Tone slider response | "
        "Color slider response | Spatial response follows original | Spatial response follows modified payload | "
        "Low-frequency only | No response | Notes |"
    )
    sep = "|---|---|---|---|---|---|---|---|---|---|"
    rows = [header, sep]
    for entry in entries:
        rows.append(f"| {entry['name']}.heic |  |  |  |  |  |  |  |  |  |")
    return "\n".join(rows)


def _preservation_summary(role_hashes: dict[str, dict[str, Any]]) -> dict[str, bool]:
    def preserved(role: str) -> bool:
        return not bool(role_hashes.get(role, {}).get("changed"))

    return {
        "preserved_primary_image": preserved("primary"),
        "preserved_hdr_gainmap": preserved("hdrgainmap"),
        "preserved_tmap": preserved("tmap"),
        "preserved_style_bplist": preserved("style_metadata"),
        "preserved_exif_makernote_payload": preserved("exif"),
        "preserved_semantic_sky_matte": preserved("semanticskymatte"),
        "preserved_linearthumbnail": preserved("linearthumbnail"),
        "preserved_styledeltamap": preserved("styledeltamap"),
    }


def _replaced_item_summary(inventory: dict[str, RoleInfo], changed_roles: list[str]) -> list[dict[str, Any]]:
    result = []
    for role in changed_roles:
        info = inventory.get(role)
        if info is None:
            continue
        result.append(
            {
                "role": role,
                "item_id": info.item_id,
                "item_type": info.item_type,
                "aux_type": info.aux_type,
                "child_item_ids": info.child_item_ids,
            }
        )
    return result


def _write_run_readme(run_dir: Path, entries: list[dict[str, Any]]) -> None:
    lines = [
        "# Photographic Styles Spatial Source Ablation Run",
        "",
        "## Manual Apple Photos Steps",
        "",
        "1. Import each HEIC into Apple Photos.",
        "2. Open Edit.",
        "3. Switch Photographic Styles.",
        "4. Adjust tone and color separately.",
        "5. Fill the table below without treating UI activation as source localization.",
        "",
        _variant_readme_table(entries),
        "",
        "## Automatic Evidence Boundary",
        "",
        "The manifest and reports prove file structure, item role hashes, aux decode statistics, and graph differences only. Apple Photos rendering behavior remains manual evidence.",
        "",
    ]
    run_dir.joinpath("README.md").write_text("\n".join(lines), encoding="utf-8")


def _run_heif_dump(path: Path, stem: str, run_dir: Path) -> dict[str, Any]:
    json_path = run_dir / f"{stem}.heif_dump.json"
    md_path = run_dir / f"{stem}.heif_dump.md"
    subprocess.run(
        ["python3", "tools/heif_dump.py", str(path), "--json", str(json_path), "--md", str(md_path)],
        check=True,
        text=True,
        capture_output=True,
    )
    return {"ok": True, "json": str(json_path), "markdown": str(md_path)}


def _run_semantic(path: Path, stem: str, run_dir: Path, decoded_dir: Path, baseline: Path, donor: Path | None) -> dict[str, Any]:
    json_path = run_dir / f"{stem}.semantic.json"
    md_path = run_dir / f"{stem}.semantic.md"
    report = build_semantic_report(
        path,
        reference_path=baseline,
        template_path=donor,
        decoded_dir=decoded_dir if decoded_dir.exists() else None,
    )
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(format_semantic_markdown(report), encoding="utf-8")
    return {"ok": True, "json": str(json_path), "markdown": str(md_path), "hard_warnings": report.get("hard_warnings", [])}


def _run_aux_diagnostics(path: Path, stem: str, run_dir: Path) -> tuple[dict[str, Any], Path | None]:
    json_path = run_dir / f"{stem}.aux_diagnostics.json"
    md_path = run_dir / f"{stem}.aux_diagnostics.md"
    try:
        result = analyze_aux_file(path, run_dir / "decoded_aux")
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc)}, None
    json_path.write_text(json.dumps([result], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(format_aux_markdown([result]), encoding="utf-8")
    return {"ok": True, "json": str(json_path), "markdown": str(md_path)}, Path(result["output_dir"])


def _run_heif_info(path: Path) -> dict[str, Any]:
    info = shutil.which("heif-info")
    if not info:
        return {"ok": False, "error": "heif-info not found"}
    completed = subprocess.run([info, str(path)], text=True, capture_output=True)
    return {
        "ok": completed.returncode == 0,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def _validate_variant(path: Path, stem: str, run_dir: Path, baseline: Path, donor: Path | None) -> dict[str, Any]:
    validation: dict[str, Any] = {"heif_info": _run_heif_info(path)}
    try:
        validation["heif_dump"] = _run_heif_dump(path, stem, run_dir)
    except Exception as exc:  # noqa: BLE001
        validation["heif_dump"] = {"ok": False, "error": str(exc)}
    aux_validation, decoded_dir = _run_aux_diagnostics(path, stem, run_dir)
    validation["aux_diagnostics"] = aux_validation
    try:
        validation["semantic_fitter"] = _run_semantic(path, stem, run_dir, decoded_dir or run_dir, baseline, donor)
    except Exception as exc:  # noqa: BLE001
        validation["semantic_fitter"] = {"ok": False, "error": str(exc)}
    return validation


def _build_variant(
    source: LoadedSource,
    baseline: Path,
    output: Path,
    *,
    name: str,
    donor: Path | None,
    decoded_sources: dict[str, Path],
    linearthumb_encoder: str,
    linearthumb_crf: int,
    linearthumb_vt_quality: float,
) -> tuple[list[str], str, dict[str, Any]]:
    inventory = build_role_inventory(baseline)
    replacements: dict[int, bytes] = {}
    hvcc_replacements: dict[int, bytes] = {}
    generation: dict[str, Any] = {}

    def merge(encoded: tuple[dict[int, bytes], dict[int, bytes]] | tuple[dict[int, bytes], dict[int, bytes], dict[str, Any]]) -> None:
        replacements.update(encoded[0])
        hvcc_replacements.update(encoded[1])
        if len(encoded) == 3:
            generation.update(encoded[2])

    if name == "baseline_original":
        copy_baseline_variant(baseline, output)
        return [], "copy", {}

    if name in {"neutral_base_only", "neutral_base_styledelta_linearthumb"}:
        merge(_encode_primary_neutral(source, inventory["primary"], value=128))

    if name in {"neutral_styledeltamap_only", "neutral_base_styledelta_linearthumb"}:
        role = inventory["styledeltamap"]
        size = (int(role.dimensions["width"]), int(role.dimensions["height"]))
        merge(_encode_hevc10_grid(source, role, neutral_rgb_image(size, 128), crf=linearthumb_crf))

    if name in {"neutral_linearthumb_only", "neutral_base_styledelta_linearthumb"}:
        role = inventory["linearthumbnail"]
        size = (int(role.dimensions["width"]), int(role.dimensions["height"]))
        merge(
            _encode_single_hevc10(
                source,
                role,
                neutral_rgb_image(size, 128),
                encoder=linearthumb_encoder,
                crf=linearthumb_crf,
                vt_quality=linearthumb_vt_quality,
            )
        )

    if name == "sky_matte_black":
        role = inventory["semanticskymatte"]
        size = (int(role.dimensions["width"]), int(role.dimensions["height"]))
        merge(_encode_single_8bit(source, role, black_l_image(size)))

    if name == "sky_matte_white":
        role = inventory["semanticskymatte"]
        size = (int(role.dimensions["width"]), int(role.dimensions["height"]))
        merge(_encode_single_8bit(source, role, white_l_image(size)))

    if name == "linearthumb_shift_x":
        role = inventory["linearthumbnail"]
        source_png = decoded_sources.get("linearthumbnail")
        if source_png is None or not source_png.exists():
            raise RuntimeError("decoded baseline linearthumbnail is required for linearthumb_shift_x")
        shifted = shift_image_x(Image.open(source_png).convert("RGB"), max(1, Image.open(source_png).width // 8))
        merge(
            _encode_single_hevc10(
                source,
                role,
                shifted,
                encoder=linearthumb_encoder,
                crf=linearthumb_crf,
                vt_quality=linearthumb_vt_quality,
            )
        )

    if name == "styledelta_shift_x":
        role = inventory["styledeltamap"]
        source_png = decoded_sources.get("styledeltamap")
        if source_png is None or not source_png.exists():
            raise RuntimeError("decoded baseline styledeltamap is required for styledelta_shift_x")
        image = Image.open(source_png).convert("RGB")
        shifted = shift_image_x(image, max(1, image.width // 8))
        merge(_encode_hevc10_grid(source, role, shifted, crf=linearthumb_crf))

    if name == "bplist_swapped_only":
        if donor is None:
            raise RuntimeError("donor is required for bplist_swapped_only")
        payload = _payload_for_role(donor, "style_metadata")
        if payload is None:
            raise RuntimeError(f"donor {donor} has no style metadata payload")
        replacements[inventory["style_metadata"].item_id] = payload

    if name != "baseline_original" and not replacements:
        raise RuntimeError(f"variant {name} did not create replacements")

    write_with_replaced_payloads(baseline, output, replacements, hvcc_replacements=hvcc_replacements)
    changed_roles = [
        role
        for role, info in inventory.items()
        if info.item_id in replacements or any(child_id in replacements for child_id in info.child_item_ids)
    ]
    perturbation = name.removesuffix("_only")
    return changed_roles, perturbation, generation


def run_ablation(
    *,
    baseline: Path,
    donor: Path | None,
    output_root: Path,
    run_id: str,
    linearthumb_encoder: str = "videotoolbox",
    linearthumb_crf: int = 28,
    linearthumb_vt_quality: float = 0.45,
) -> dict[str, Any]:
    if not baseline.exists():
        raise FileNotFoundError(f"baseline not found: {baseline}")
    if donor is not None and not donor.exists():
        raise FileNotFoundError(f"donor not found: {donor}")
    run_dir = output_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    source = _load_source(baseline)
    baseline_inventory = build_role_inventory(baseline)
    donor_inventory = build_role_inventory(donor) if donor else {}
    before_hashes = _role_payload_hashes(baseline)
    decoded_sources = _decode_aux_images(baseline, run_dir / "_baseline_decoded")

    variants = [
        "baseline_original",
        "neutral_base_only",
        "neutral_styledeltamap_only",
        "neutral_linearthumb_only",
        "neutral_base_styledelta_linearthumb",
        "sky_matte_black",
        "sky_matte_white",
        "linearthumb_shift_x",
        "styledelta_shift_x",
        "bplist_swapped_only",
    ]
    entries: list[dict[str, Any]] = []
    for name in variants:
        output = run_dir / f"{name}.heic"
        changed_roles, perturbation, generation = _build_variant(
            source,
            baseline,
            output,
            name=name,
            donor=donor,
            decoded_sources=decoded_sources,
            linearthumb_encoder=linearthumb_encoder,
            linearthumb_crf=linearthumb_crf,
            linearthumb_vt_quality=linearthumb_vt_quality,
        )
        after_hashes = _role_payload_hashes(output)
        validation = _validate_variant(output, name, run_dir, baseline, donor)
        role_hashes = compare_role_hashes(before_hashes, after_hashes)
        output_inventory = build_role_inventory(output)
        entry = manifest_entry(
            name=name,
            output=output,
            perturbation=perturbation,
            changed_roles=changed_roles,
            validation=validation,
        )
        entry.update(
            {
                "input_baseline": str(baseline),
                "recipient_file": str(baseline),
                "donor": str(donor) if donor else None,
                "replaced_items": _replaced_item_summary(output_inventory, changed_roles),
                "preservation": _preservation_summary(role_hashes),
                "role_hashes": role_hashes,
                "role_inventory": {
                    role: {
                        "item_id": info.item_id,
                        "item_type": info.item_type,
                        "aux_type": info.aux_type,
                        "dimensions": info.dimensions,
                        "child_item_ids": info.child_item_ids,
                    }
                    for role, info in output_inventory.items()
                },
                "generation": generation,
            }
        )
        entries.append(entry)

    manifest = {
        "run_id": run_id,
        "baseline": str(baseline),
        "donor": str(donor) if donor else None,
        "output_dir": str(run_dir),
        "linearthumb_encoder": linearthumb_encoder,
        "linearthumb_crf": linearthumb_crf,
        "linearthumb_vt_quality": linearthumb_vt_quality,
        "baseline_role_inventory": {
            role: {
                "item_id": info.item_id,
                "item_type": info.item_type,
                "aux_type": info.aux_type,
                "dimensions": info.dimensions,
                "child_item_ids": info.child_item_ids,
            }
            for role, info in baseline_inventory.items()
        },
        "donor_role_inventory": {
            role: {
                "item_id": info.item_id,
                "item_type": info.item_type,
                "aux_type": info.aux_type,
                "dimensions": info.dimensions,
                "child_item_ids": info.child_item_ids,
            }
            for role, info in donor_inventory.items()
        },
        "variants": entries,
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    _write_run_readme(run_dir, entries)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Photographic Styles spatial-source ablation HEICs.")
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    parser.add_argument("--donor", type=Path, default=DEFAULT_DONOR)
    parser.add_argument("--output-root", type=Path, default=Path("artifacts/style_spatial_ablation"))
    parser.add_argument("--run-id", default="20260602_v1_source_ablation")
    parser.add_argument("--linearthumb-encoder", choices=["x265", "videotoolbox"], default="videotoolbox")
    parser.add_argument("--linearthumb-crf", type=int, default=28)
    parser.add_argument("--linearthumb-vt-quality", type=float, default=0.45)
    args = parser.parse_args()

    manifest = run_ablation(
        baseline=args.baseline,
        donor=args.donor,
        output_root=args.output_root,
        run_id=args.run_id,
        linearthumb_encoder=args.linearthumb_encoder,
        linearthumb_crf=args.linearthumb_crf,
        linearthumb_vt_quality=args.linearthumb_vt_quality,
    )
    print(json.dumps({"manifest": str(Path(manifest["output_dir"]) / "manifest.json")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
