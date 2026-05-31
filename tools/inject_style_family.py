#!/usr/bin/env python3
"""Inject an Apple Photographic Styles HEIF family into an Apple-generated base HEIC."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.apple_template_writer import update_style_metadata_bplist
from tools.exif_makernote_swap import build_exif_with_template_makernote
from tools.heif_aux_writer import _box, _full_box, _u16, _u32, _u64
from tools.heif_dump import STYLE_DELTA_AUX_TYPE, iter_boxes, parse_heif
from tools.hevc10_encoder import payload_and_hvcc_from_annexb_hevc


LINEARTHUMB_AUX_TYPE = "tag:apple.com,2023:photo:aux:linearthumbnail"
HDR_GAINMAP_AUX_TYPE = "urn:com:apple:photo:2020:aux:hdrgainmap"
SEMANTIC_SKY_MATTE_AUX_TYPE = "urn:com:apple:photo:2020:aux:semanticskymatte"
STYLE_METADATA_URI_TYPE = "tag:apple.com,2023:photo:metadata:styles"
REBUILT_META_CHILDREN = {"iinf", "iref", "iprp", "idat", "iloc"}


@dataclass(frozen=True)
class LoadedHeif:
    path: Path
    data: bytes
    parsed: dict[str, Any]
    ftyp_box: dict[str, Any]
    preserved_meta_children: list[bytes]
    ipco_property_boxes: list[bytes]
    item_payloads: dict[int, bytes]
    construction_methods: dict[int, int]
    item_order: list[int]


def _raw_box(data: bytes, box_info: dict[str, Any]) -> bytes:
    return data[box_info["offset"] : box_info["offset"] + box_info["size"]]


def _find_top_box(data: bytes, box_type: str) -> dict[str, Any]:
    for box_info in iter_boxes(data):
        if box_info["type"] == box_type:
            return box_info
    raise ValueError(f"{box_type} box not found")


def _cstr(value: str | None) -> bytes:
    return (value or "").encode("utf-8") + b"\0"


def _payload_from_extents(data: bytes, item: dict[str, Any]) -> bytes:
    payload = bytearray()
    for extent in item.get("extents", []):
        offset = int(extent.get("absolute_offset", extent.get("offset", 0)))
        length = int(extent.get("length", 0))
        payload.extend(data[offset : offset + length])
    return bytes(payload)


def load_heif(path: Path) -> LoadedHeif:
    data = path.read_bytes()
    parsed = parse_heif(data, str(path))
    ftyp_box = _find_top_box(data, "ftyp")
    meta_box = _find_top_box(data, "meta")
    meta_children = iter_boxes(
        data,
        meta_box["payload_offset"] + 4,
        meta_box["payload_offset"] + meta_box["payload_size"],
    )

    preserved_meta_children: list[bytes] = []
    ipco_property_boxes: list[bytes] = []
    for child in meta_children:
        if child["type"] == "iprp":
            for iprp_child in iter_boxes(data, child["payload_offset"], child["payload_offset"] + child["payload_size"]):
                if iprp_child["type"] == "ipco":
                    ipco_property_boxes = [
                        _raw_box(data, prop)
                        for prop in iter_boxes(
                            data,
                            iprp_child["payload_offset"],
                            iprp_child["payload_offset"] + iprp_child["payload_size"],
                        )
                    ]
            continue
        if child["type"] not in REBUILT_META_CHILDREN:
            preserved_meta_children.append(_raw_box(data, child))

    if not ipco_property_boxes:
        raise ValueError(f"{path} has no iprp/ipco properties")

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
    return LoadedHeif(
        path=path,
        data=data,
        parsed=parsed,
        ftyp_box=ftyp_box,
        preserved_meta_children=preserved_meta_children,
        ipco_property_boxes=ipco_property_boxes,
        item_payloads=item_payloads,
        construction_methods=construction_methods,
        item_order=item_order,
    )


def _item_dimensions(parsed: dict[str, Any], item_id: int) -> dict[str, int] | None:
    item = parsed.get("items", {}).get(str(item_id), {})
    dims = item.get("dimensions")
    if not dims:
        return None
    return {"width": int(dims["width"]), "height": int(dims["height"])}


def _first_item_id_by_aux(parsed: dict[str, Any], aux_type: str) -> int | None:
    for item_id, item in parsed.get("items", {}).items():
        if item.get("aux_type") == aux_type:
            return int(item_id)
    return None


def _first_item_id_by_type(parsed: dict[str, Any], item_type: str) -> int | None:
    for item_id, item in parsed.get("items", {}).items():
        if item.get("item_type") == item_type:
            return int(item_id)
    return None


def _style_metadata_item_id(parsed: dict[str, Any]) -> int | None:
    for item_id, item in parsed.get("items", {}).items():
        if item.get("item_type") == "uri " and item.get("uri_type") == STYLE_METADATA_URI_TYPE:
            return int(item_id)
    return None


def _child_ids(item: dict[str, Any]) -> list[int]:
    if item.get("derived_child_item_ids"):
        return [int(item_id) for item_id in item["derived_child_item_ids"]]
    for ref in item.get("references_from", []):
        if ref.get("type") == "dimg":
            return [int(item_id) for item_id in ref.get("to_item_ids", [])]
    return []


def style_family_item_ids(donor: LoadedHeif) -> dict[str, int | list[int]]:
    parsed = donor.parsed
    styledeltamap_id = _first_item_id_by_aux(parsed, STYLE_DELTA_AUX_TYPE)
    gainmap_id = _first_item_id_by_aux(parsed, HDR_GAINMAP_AUX_TYPE)
    linearthumb_id = _first_item_id_by_aux(parsed, LINEARTHUMB_AUX_TYPE)
    sky_matte_id = _first_item_id_by_aux(parsed, SEMANTIC_SKY_MATTE_AUX_TYPE)
    tmap_id = _first_item_id_by_type(parsed, "tmap")
    style_metadata_id = _style_metadata_item_id(parsed)

    required = {
        "styledeltamap": styledeltamap_id,
        "gainmap": gainmap_id,
        "linearthumbnail": linearthumb_id,
        "tmap": tmap_id,
        "style_metadata": style_metadata_id,
    }
    missing = [name for name, item_id in required.items() if item_id is None]
    if missing:
        raise ValueError(f"style donor is missing required items: {', '.join(missing)}")

    item_ids: set[int] = {
        int(styledeltamap_id),
        int(gainmap_id),
        int(linearthumb_id),
        int(tmap_id),
        int(style_metadata_id),
    }
    if sky_matte_id is not None:
        item_ids.add(int(sky_matte_id))

    for grid_id in (styledeltamap_id, gainmap_id):
        grid_item = parsed["items"][str(grid_id)]
        item_ids.update(_child_ids(grid_item))

    for item_id, item in parsed.get("items", {}).items():
        if item.get("item_type") == "mime":
            for ref in item.get("references_from", []):
                if ref.get("type") == "cdsc" and gainmap_id in ref.get("to_item_ids", []):
                    item_ids.add(int(item_id))

    donor_primary = int(parsed["primary_item_id"])
    item_ids.discard(donor_primary)
    for item_id, item in parsed.get("items", {}).items():
        if item.get("item_type") == "Exif":
            item_ids.discard(int(item_id))

    return {
        "item_ids": sorted(item_ids),
        "styledeltamap": int(styledeltamap_id),
        "gainmap": int(gainmap_id),
        "linearthumbnail": int(linearthumb_id),
        "sky_matte": int(sky_matte_id) if sky_matte_id is not None else 0,
        "tmap": int(tmap_id),
        "style_metadata": int(style_metadata_id),
    }


def _build_item_id_map(base: LoadedHeif, donor: LoadedHeif, donor_item_ids: list[int]) -> dict[int, int]:
    next_item_id = max(base.item_order)
    id_map = {int(donor.parsed["primary_item_id"]): int(base.parsed["primary_item_id"])}
    for donor_item_id in donor_item_ids:
        next_item_id += 1
        id_map[donor_item_id] = next_item_id
    return id_map


def _infe_from_item(item: dict[str, Any], item_id: int) -> bytes:
    version = 2 if item_id <= 0xFFFF else 3
    flags = 1 if item.get("hidden") else 0
    item_id_bytes = _u16(item_id) if version == 2 else _u32(item_id)
    item_type = item.get("item_type")
    if not item_type or len(item_type) != 4:
        raise ValueError(f"item {item_id} has unsupported item_type {item_type!r}")
    payload = (
        item_id_bytes
        + _u16(int(item.get("item_protection_index", 0)))
        + item_type.encode("ascii")
        + _cstr(item.get("name", ""))
    )
    if item_type == "mime":
        payload += _cstr(item.get("content_type", "")) + _cstr(item.get("content_encoding", ""))
    elif item_type == "uri ":
        payload += _cstr(item.get("uri_type", ""))
    return _full_box("infe", version=version, flags=flags, payload=payload)


def _build_iinf(items: list[tuple[int, dict[str, Any]]]) -> bytes:
    if len(items) > 0xFFFF:
        payload = _u32(len(items))
        version = 1
    else:
        payload = _u16(len(items))
        version = 0
    payload += b"".join(_infe_from_item(item, item_id) for item_id, item in items)
    return _full_box("iinf", version=version, payload=payload)


def _build_references(
    base: LoadedHeif,
    donor: LoadedHeif,
    donor_item_ids: list[int],
    id_map: dict[int, int],
    *,
    base_exif_item_id: int | None = None,
    remapped_tmap_item_id: int | None = None,
) -> list[dict[str, Any]]:
    references: list[dict[str, Any]] = []
    base_primary = int(base.parsed["primary_item_id"])
    for ref in base.parsed.get("references", []):
        copied_ref = {
            "type": ref["type"],
            "from_item_id": int(ref["from_item_id"]),
            "to_item_ids": [int(item_id) for item_id in ref.get("to_item_ids", [])],
        }
        if (
            base_exif_item_id is not None
            and remapped_tmap_item_id is not None
            and copied_ref["type"] == "cdsc"
            and copied_ref["from_item_id"] == base_exif_item_id
            and base_primary in copied_ref["to_item_ids"]
        ):
            copied_ref["to_item_ids"] = [base_primary, remapped_tmap_item_id]
        references.append(copied_ref)
    donor_primary = int(donor.parsed["primary_item_id"])
    donor_item_id_set = set(donor_item_ids)

    def map_target(target: int) -> int | None:
        if target == donor_primary:
            return id_map[donor_primary]
        if target in donor_item_id_set:
            return id_map[target]
        return None

    for ref in donor.parsed.get("references", []):
        from_item_id = int(ref.get("from_item_id", -1))
        if from_item_id not in donor_item_id_set:
            continue
        to_item_ids = []
        for target in ref.get("to_item_ids", []):
            mapped = map_target(int(target))
            if mapped is not None:
                to_item_ids.append(mapped)
        if not to_item_ids:
            continue
        references.append(
            {
                "type": ref["type"],
                "from_item_id": id_map[from_item_id],
                "to_item_ids": to_item_ids,
            }
        )
    return references


def _build_iref(references: list[dict[str, Any]]) -> bytes:
    needs_32_bit = any(
        int(ref["from_item_id"]) > 0xFFFF or any(int(item_id) > 0xFFFF for item_id in ref["to_item_ids"])
        for ref in references
    )
    version = 1 if needs_32_bit else 0
    id_size = 4 if needs_32_bit else 2

    def item_id_bytes(item_id: int) -> bytes:
        return _u32(item_id) if id_size == 4 else _u16(item_id)

    payload = bytearray()
    for ref in references:
        ref_payload = item_id_bytes(int(ref["from_item_id"])) + _u16(len(ref["to_item_ids"]))
        for item_id in ref["to_item_ids"]:
            ref_payload += item_id_bytes(int(item_id))
        payload.extend(_box(ref["type"], ref_payload))
    return _full_box("iref", version=version, payload=bytes(payload))


def _build_iprp(
    base: LoadedHeif,
    donor: LoadedHeif,
    donor_item_ids: list[int],
    id_map: dict[int, int],
    *,
    linearthumb_item_id: int | None = None,
    linearthumb_hvcc: bytes | None = None,
) -> bytes:
    property_boxes = list(base.ipco_property_boxes)
    associations: list[tuple[int, list[dict[str, Any]]]] = []

    for item_id in base.item_order:
        item = base.parsed["items"][str(item_id)]
        associations.append((item_id, list(item.get("property_associations", []))))

    donor_property_map: dict[tuple[int, bool], int] = {}
    for donor_item_id in donor_item_ids:
        donor_item = donor.parsed["items"][str(donor_item_id)]
        remapped_associations = []
        for assoc in donor_item.get("property_associations", []):
            donor_property_index = int(assoc["property_index"])
            replace_hvcc = (
                linearthumb_item_id is not None
                and linearthumb_hvcc is not None
                and donor_item_id == linearthumb_item_id
                and assoc.get("type") == "hvcC"
            )
            property_key = (donor_property_index, replace_hvcc)
            if property_key not in donor_property_map:
                if donor_property_index <= 0 or donor_property_index > len(donor.ipco_property_boxes):
                    raise ValueError(f"donor property index {donor_property_index} out of range")
                property_box = _box("hvcC", linearthumb_hvcc) if replace_hvcc else donor.ipco_property_boxes[donor_property_index - 1]
                property_boxes.append(property_box)
                donor_property_map[property_key] = len(property_boxes)
            remapped_associations.append(
                {
                    "property_index": donor_property_map[property_key],
                    "essential": bool(assoc.get("essential")),
                }
            )
        associations.append((id_map[donor_item_id], remapped_associations))

    ipco = _box("ipco", b"".join(property_boxes))
    needs_32_bit = any(item_id > 0xFFFF for item_id, _ in associations)
    version = 1 if needs_32_bit else 0
    ipma_payload = _u32(len(associations))
    for item_id, assoc_list in associations:
        ipma_payload += (_u32(item_id) if needs_32_bit else _u16(item_id)) + bytes([len(assoc_list)])
        for assoc in assoc_list:
            raw = int(assoc["property_index"]) | (0x8000 if assoc.get("essential") else 0)
            ipma_payload += _u16(raw)
    return _box("iprp", ipco + _full_box("ipma", version=version, flags=1, payload=ipma_payload))


def _build_iloc(records: list[dict[str, Any]], mdat_payload_start: int) -> tuple[bytes, bytes, bytes]:
    payload = bytes([0x44, 0x80]) + _u16(len(records))
    idat_parts: list[bytes] = []
    mdat_parts: list[bytes] = []
    idat_cursor = 0
    mdat_cursor = 0
    for record in records:
        item_payload = record["payload"]
        construction_method = int(record["construction_method"])
        if construction_method == 1:
            base_offset = 0
            extent_offset = idat_cursor
            idat_cursor += len(item_payload)
            idat_parts.append(item_payload)
        elif construction_method == 0:
            base_offset = mdat_payload_start + mdat_cursor
            extent_offset = 0
            mdat_cursor += len(item_payload)
            mdat_parts.append(item_payload)
        else:
            raise ValueError(f"unsupported construction method {construction_method} for item {record['item_id']}")
        payload += (
            _u16(int(record["item_id"]))
            + _u16(construction_method)
            + _u16(0)
            + _u64(base_offset)
            + _u16(1)
            + _u32(extent_offset)
            + _u32(len(item_payload))
        )
    return _full_box("iloc", version=1, payload=payload), b"".join(idat_parts), b"".join(mdat_parts)


def _build_ftyp(base: LoadedHeif, donor: LoadedHeif) -> bytes:
    base_ftyp = base.parsed["ftyp"]
    donor_brands = donor.parsed["ftyp"].get("compatible_brands", [])
    brands: list[str] = []
    for brand in [*base_ftyp.get("compatible_brands", []), *donor_brands, "tmap"]:
        if brand and brand not in brands:
            brands.append(brand)
    payload = base_ftyp["major_brand"].encode("ascii") + _u32(int(base_ftyp.get("minor_version", 0)))
    payload += b"".join(brand.encode("ascii") for brand in brands)
    return _box("ftyp", payload)


def _build_meta(
    base: LoadedHeif,
    iinf: bytes,
    iref: bytes,
    iprp: bytes,
    idat_payload: bytes,
    iloc: bytes,
) -> bytes:
    payload = b"".join(base.preserved_meta_children)
    payload += iinf + iref + iprp + _box("idat", idat_payload) + iloc
    return _full_box("meta", payload=payload)


def _records_and_items(
    base: LoadedHeif,
    donor: LoadedHeif,
    donor_item_ids: list[int],
    id_map: dict[int, int],
    *,
    preview_jpeg: Path | None = None,
    exif_template: Path | None = None,
    update_style_metadata: bool = False,
    linearthumb_item_id: int | None = None,
    linearthumb_payload: bytes | None = None,
) -> tuple[list[dict[str, Any]], list[tuple[int, dict[str, Any]]]]:
    payloads = dict(base.item_payloads)
    if preview_jpeg is not None and exif_template is not None:
        exif_item_ids = [
            int(item_id)
            for item_id, item in base.parsed.get("items", {}).items()
            if item.get("item_type") == "Exif"
        ]
        if exif_item_ids:
            payloads[exif_item_ids[0]] = build_exif_with_template_makernote(exif_template, preview_jpeg)

    records: list[dict[str, Any]] = []
    items_for_iinf: list[tuple[int, dict[str, Any]]] = []
    for item_id in base.item_order:
        item = dict(base.parsed["items"][str(item_id)])
        records.append(
            {
                "item_id": item_id,
                "construction_method": base.construction_methods.get(item_id, 0),
                "payload": payloads.get(item_id, b""),
            }
        )
        items_for_iinf.append((item_id, item))

    for donor_item_id in donor_item_ids:
        remapped_id = id_map[donor_item_id]
        donor_item = dict(donor.parsed["items"][str(donor_item_id)])
        payload = donor.item_payloads.get(donor_item_id, b"")
        if linearthumb_item_id is not None and donor_item_id == linearthumb_item_id and linearthumb_payload is not None:
            payload = linearthumb_payload
        if update_style_metadata and donor_item.get("item_type") == "uri " and donor_item.get("uri_type") == STYLE_METADATA_URI_TYPE:
            if preview_jpeg is None:
                raise ValueError("preview_jpeg is required when update_style_metadata=True")
            payload = update_style_metadata_bplist(payload, preview_jpeg)
        records.append(
            {
                "item_id": remapped_id,
                "construction_method": donor.construction_methods.get(donor_item_id, 0),
                "payload": payload,
            }
        )
        donor_item["item_id"] = remapped_id
        items_for_iinf.append((remapped_id, donor_item))

    return records, items_for_iinf


def _first_exif_item_id(parsed: dict[str, Any]) -> int | None:
    for item_id, item in parsed.get("items", {}).items():
        if item.get("item_type") == "Exif":
            return int(item_id)
    return None


def inject_style_family(
    base_heic: Path,
    style_donor: Path,
    *,
    output_path: Path | None = None,
    preview_jpeg: Path | None = None,
    exif_template: Path | None = None,
    update_style_metadata: bool = False,
    allow_dimension_mismatch: bool = False,
    replace_linearthumb_hevc: Path | None = None,
) -> dict[str, Any]:
    base = load_heif(base_heic)
    donor = load_heif(style_donor)
    donor_family = style_family_item_ids(donor)
    donor_item_ids = list(donor_family["item_ids"])  # type: ignore[arg-type]
    id_map = _build_item_id_map(base, donor, donor_item_ids)

    base_primary = int(base.parsed["primary_item_id"])
    donor_tmap = int(donor_family["tmap"])
    base_dims = _item_dimensions(base.parsed, base_primary)
    donor_tmap_dims = _item_dimensions(donor.parsed, donor_tmap)
    if not allow_dimension_mismatch and base_dims != donor_tmap_dims:
        raise ValueError(f"primary dimensions {base_dims} do not match donor tmap dimensions {donor_tmap_dims}")
    base_exif_item_id = _first_exif_item_id(base.parsed) if preview_jpeg is not None and exif_template is not None else None
    linearthumb_payload: bytes | None = None
    linearthumb_hvcc: bytes | None = None
    if replace_linearthumb_hevc is not None:
        linearthumb_payload, linearthumb_hvcc = payload_and_hvcc_from_annexb_hevc(
            replace_linearthumb_hevc.read_bytes(),
            item_payload_policy="single_idr",
        )

    records, items_for_iinf = _records_and_items(
        base,
        donor,
        donor_item_ids,
        id_map,
        preview_jpeg=preview_jpeg,
        exif_template=exif_template,
        update_style_metadata=update_style_metadata,
        linearthumb_item_id=int(donor_family["linearthumbnail"]),
        linearthumb_payload=linearthumb_payload,
    )
    references = _build_references(
        base,
        donor,
        donor_item_ids,
        id_map,
        base_exif_item_id=base_exif_item_id,
        remapped_tmap_item_id=id_map[int(donor_family["tmap"])],
    )
    ftyp = _build_ftyp(base, donor)
    iinf = _build_iinf(items_for_iinf)
    iref = _build_iref(references)
    iprp = _build_iprp(
        base,
        donor,
        donor_item_ids,
        id_map,
        linearthumb_item_id=int(donor_family["linearthumbnail"]),
        linearthumb_hvcc=linearthumb_hvcc,
    )

    iloc_placeholder, idat_payload, mdat_payload = _build_iloc(records, mdat_payload_start=0)
    meta_placeholder = _build_meta(base, iinf, iref, iprp, idat_payload, iloc_placeholder)
    mdat_payload_start = len(ftyp) + len(meta_placeholder) + 8
    iloc, idat_payload, mdat_payload = _build_iloc(records, mdat_payload_start=mdat_payload_start)
    meta = _build_meta(base, iinf, iref, iprp, idat_payload, iloc)
    if len(meta) != len(meta_placeholder):
        raise RuntimeError("meta size changed after resolving mdat offsets")

    output_bytes = ftyp + meta + _box("mdat", mdat_payload)
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(output_bytes)

    summary = {
        "base_heic": str(base_heic),
        "style_donor": str(style_donor),
        "output": str(output_path) if output_path else None,
        "base_primary_item_id": base_primary,
        "base_primary_dimensions": base_dims,
        "donor_tmap_dimensions": donor_tmap_dims,
        "injected_item_count": len(donor_item_ids),
        "id_map": {str(key): value for key, value in sorted(id_map.items()) if key in donor_item_ids},
        "styledeltamap_item_id": id_map[int(donor_family["styledeltamap"])],
        "gainmap_item_id": id_map[int(donor_family["gainmap"])],
        "linearthumbnail_item_id": id_map[int(donor_family["linearthumbnail"])],
        "sky_matte_item_id": id_map.get(int(donor_family["sky_matte"]), 0),
        "tmap_item_id": id_map[int(donor_family["tmap"])],
        "style_metadata_item_id": id_map[int(donor_family["style_metadata"])],
        "base_exif_item_id": base_exif_item_id,
        "updated_base_exif": preview_jpeg is not None and exif_template is not None,
        "updated_style_metadata": update_style_metadata,
        "replaced_linearthumbnail": replace_linearthumb_hevc is not None,
        "replacement_linearthumbnail_hevc": str(replace_linearthumb_hevc) if replace_linearthumb_hevc else None,
        "replacement_linearthumbnail_payload_bytes": len(linearthumb_payload) if linearthumb_payload is not None else 0,
        "replacement_linearthumbnail_hvcc_bytes": len(linearthumb_hvcc) if linearthumb_hvcc is not None else 0,
    }
    if output_path is not None:
        (output_path.parent / "style_injection_summary.json").write_text(
            json.dumps(summary, indent=2, ensure_ascii=False) + "\n"
        )
    return summary


def _parse_size(value: str) -> tuple[int, int]:
    try:
        width_text, height_text = value.lower().split("x", 1)
        width = int(width_text)
        height = int(height_text)
    except Exception as exc:  # noqa: BLE001
        raise argparse.ArgumentTypeError("size must be WIDTHxHEIGHT, for example 4032x3024") from exc
    if width <= 0 or height <= 0:
        raise argparse.ArgumentTypeError("size dimensions must be positive")
    return width, height


def make_base_with_sips(preview_jpeg: Path, output_path: Path, size: tuple[int, int]) -> Path:
    sips = shutil.which("sips")
    if not sips:
        raise RuntimeError("sips not found; cannot create Apple HEIC base")
    width, height = size
    output_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [sips, "-z", str(height), str(width), "-s", "format", "heic", str(preview_jpeg), "--out", str(output_path)],
        check=True,
        capture_output=True,
    )
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Inject Apple Photographic Styles private HEIF family into a base HEIC.")
    parser.add_argument("--base-heic", type=Path, help="Apple-generated base HEIC to patch.")
    parser.add_argument("--make-base-with-sips", action="store_true", help="Create the base HEIC from --preview-jpeg using sips.")
    parser.add_argument("--base-size", type=_parse_size, default=(4032, 3024), help="Base size for --make-base-with-sips, WIDTHxHEIGHT.")
    parser.add_argument("--preview-jpeg", type=Path, help="Preview JPEG used for sips base generation and Exif/style metadata updates.")
    parser.add_argument("--style-donor", type=Path, required=True, help="Working style-family donor HEIC, for example v8.")
    parser.add_argument("--template", type=Path, help="Apple template HEIC whose MakerNote should be injected into the base Exif.")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--allow-dimension-mismatch", action="store_true")
    parser.add_argument("--no-update-base-exif", action="store_true")
    parser.add_argument("--update-style-metadata", action="store_true")
    parser.add_argument(
        "--replace-linearthumb-hevc",
        type=Path,
        help="Annex-B HEVC stream to use for the injected Apple linearthumbnail item 97 equivalent.",
    )
    args = parser.parse_args()

    if args.make_base_with_sips:
        if args.preview_jpeg is None:
            parser.error("--preview-jpeg is required with --make-base-with-sips")
        base_heic = make_base_with_sips(
            args.preview_jpeg,
            args.output.parent / "base_from_preview_sips.heic",
            args.base_size,
        )
    else:
        if args.base_heic is None:
            parser.error("--base-heic is required unless --make-base-with-sips is used")
        base_heic = args.base_heic

    exif_template = None
    if not args.no_update_base_exif and args.preview_jpeg is not None:
        exif_template = args.template or args.style_donor

    summary = inject_style_family(
        base_heic,
        args.style_donor,
        output_path=args.output,
        preview_jpeg=args.preview_jpeg,
        exif_template=exif_template,
        update_style_metadata=args.update_style_metadata,
        allow_dimension_mismatch=args.allow_dimension_mismatch,
        replace_linearthumb_hevc=args.replace_linearthumb_hevc,
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
