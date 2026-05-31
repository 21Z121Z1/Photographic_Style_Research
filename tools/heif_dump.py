#!/usr/bin/env python3
"""Focused HEIF/ISOBMFF structure dumper for auxiliary-image analysis."""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path
from typing import Any


STYLE_DELTA_AUX_TYPE = "tag:apple.com,2023:photo:aux:styledeltamap"


def _u8(data: bytes, offset: int) -> int:
    return data[offset]


def _u16(data: bytes, offset: int) -> int:
    return struct.unpack_from(">H", data, offset)[0]


def _u24(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset : offset + 3], "big")


def _u32(data: bytes, offset: int) -> int:
    return struct.unpack_from(">I", data, offset)[0]


def _u64(data: bytes, offset: int) -> int:
    return struct.unpack_from(">Q", data, offset)[0]


def _read_int(data: bytes, offset: int, size: int) -> tuple[int, int]:
    if size == 0:
        return 0, offset
    return int.from_bytes(data[offset : offset + size], "big"), offset + size


def _fourcc(value: bytes) -> str:
    return value.decode("latin-1", errors="replace")


def _read_cstr(data: bytes, offset: int) -> tuple[str, int]:
    end = data.find(b"\0", offset)
    if end < 0:
        return data[offset:].decode("utf-8", errors="replace"), len(data)
    return data[offset:end].decode("utf-8", errors="replace"), end + 1


def _read_fullbox(data: bytes, payload_offset: int) -> tuple[int, int, int]:
    version = _u8(data, payload_offset)
    flags = _u24(data, payload_offset + 1)
    return version, flags, payload_offset + 4


def iter_boxes(data: bytes, start: int = 0, end: int | None = None) -> list[dict[str, Any]]:
    if end is None:
        end = len(data)
    boxes: list[dict[str, Any]] = []
    offset = start
    while offset + 8 <= end:
        size = _u32(data, offset)
        box_type = _fourcc(data[offset + 4 : offset + 8])
        header_size = 8
        if size == 1:
            if offset + 16 > end:
                break
            size = _u64(data, offset + 8)
            header_size = 16
        elif size == 0:
            size = end - offset
        if size < header_size or offset + size > end:
            boxes.append(
                {
                    "type": box_type,
                    "offset": offset,
                    "size": max(size, 0),
                    "header_size": header_size,
                    "parse_error": "invalid box size",
                }
            )
            break
        boxes.append(
            {
                "type": box_type,
                "offset": offset,
                "size": size,
                "header_size": header_size,
                "payload_offset": offset + header_size,
                "payload_size": size - header_size,
            }
        )
        offset += size
    return boxes


def parse_ftyp(data: bytes, box_info: dict[str, Any]) -> dict[str, Any]:
    pos = box_info["payload_offset"]
    end = pos + box_info["payload_size"]
    if end - pos < 8:
        return {}
    brands = [_fourcc(data[i : i + 4]) for i in range(pos + 8, end, 4) if i + 4 <= end]
    return {
        "major_brand": _fourcc(data[pos : pos + 4]),
        "minor_version": _u32(data, pos + 4),
        "compatible_brands": brands,
    }


def parse_hdlr(data: bytes, box_info: dict[str, Any]) -> dict[str, Any]:
    version, flags, pos = _read_fullbox(data, box_info["payload_offset"])
    end = box_info["payload_offset"] + box_info["payload_size"]
    if pos + 20 > end:
        return {"version": version, "flags": flags}
    handler_type = _fourcc(data[pos + 4 : pos + 8])
    name, _ = _read_cstr(data, pos + 20)
    return {"version": version, "flags": flags, "handler_type": handler_type, "name": name}


def parse_pitm(data: bytes, box_info: dict[str, Any]) -> int | None:
    version, _flags, pos = _read_fullbox(data, box_info["payload_offset"])
    end = box_info["payload_offset"] + box_info["payload_size"]
    if version == 0 and pos + 2 <= end:
        return _u16(data, pos)
    if pos + 4 <= end:
        return _u32(data, pos)
    return None


def parse_infe(data: bytes, box_info: dict[str, Any]) -> dict[str, Any]:
    version, flags, pos = _read_fullbox(data, box_info["payload_offset"])
    end = box_info["payload_offset"] + box_info["payload_size"]
    result: dict[str, Any] = {
        "version": version,
        "flags": flags,
        "hidden": bool(flags & 1),
    }
    if version in (0, 1):
        if pos + 4 > end:
            return result
        result["item_id"] = _u16(data, pos)
        result["item_protection_index"] = _u16(data, pos + 2)
        name, pos = _read_cstr(data, pos + 4)
        content_type, pos = _read_cstr(data, pos)
        content_encoding, _ = _read_cstr(data, pos)
        result.update(
            {
                "name": name,
                "content_type": content_type,
                "content_encoding": content_encoding,
            }
        )
        return result
    if version in (2, 3):
        item_id_size = 4 if version == 3 else 2
        if pos + item_id_size + 6 > end:
            return result
        item_id, pos = _read_int(data, pos, item_id_size)
        result["item_id"] = item_id
        result["item_protection_index"] = _u16(data, pos)
        pos += 2
        result["item_type"] = _fourcc(data[pos : pos + 4])
        pos += 4
        name, pos = _read_cstr(data, pos)
        result["name"] = name
        if result["item_type"] == "mime":
            content_type, pos = _read_cstr(data, pos)
            content_encoding, _ = _read_cstr(data, pos)
            result["content_type"] = content_type
            result["content_encoding"] = content_encoding
        elif result["item_type"] == "uri ":
            uri_type, _ = _read_cstr(data, pos)
            result["uri_type"] = uri_type
        return result
    return result


def parse_iinf(data: bytes, box_info: dict[str, Any]) -> dict[str, dict[str, Any]]:
    version, _flags, pos = _read_fullbox(data, box_info["payload_offset"])
    end = box_info["payload_offset"] + box_info["payload_size"]
    if version in (0, 1):
        if pos + 2 > end:
            return {}
        entry_count = _u16(data, pos)
        pos += 2
    else:
        if pos + 4 > end:
            return {}
        entry_count = _u32(data, pos)
        pos += 4
    items: dict[str, dict[str, Any]] = {}
    for child in iter_boxes(data, pos, end)[:entry_count]:
        if child["type"] != "infe":
            continue
        item = parse_infe(data, child)
        item_id = item.get("item_id")
        if item_id is not None:
            items[str(item_id)] = item
    return items


def parse_iloc(
    data: bytes, box_info: dict[str, Any], idat_payload_offset: int | None = None
) -> dict[str, dict[str, Any]]:
    version, flags, pos = _read_fullbox(data, box_info["payload_offset"])
    end = box_info["payload_offset"] + box_info["payload_size"]
    if pos + 2 > end:
        return {}
    sizes_1 = _u8(data, pos)
    sizes_2 = _u8(data, pos + 1)
    pos += 2
    offset_size = sizes_1 >> 4
    length_size = sizes_1 & 0x0F
    base_offset_size = sizes_2 >> 4
    index_size = sizes_2 & 0x0F if version in (1, 2) else 0
    if version < 2:
        item_count = _u16(data, pos)
        pos += 2
    else:
        item_count = _u32(data, pos)
        pos += 4
    locations: dict[str, dict[str, Any]] = {}
    for _ in range(item_count):
        item_id_size = 2 if version < 2 else 4
        item_id, pos = _read_int(data, pos, item_id_size)
        construction_method = 0
        if version in (1, 2):
            construction_method = _u16(data, pos) & 0x000F
            pos += 2
        data_reference_index = _u16(data, pos)
        pos += 2
        base_offset, pos = _read_int(data, pos, base_offset_size)
        extent_count = _u16(data, pos)
        pos += 2
        extents = []
        for _extent in range(extent_count):
            extent_index = None
            if index_size:
                extent_index, pos = _read_int(data, pos, index_size)
            extent_offset, pos = _read_int(data, pos, offset_size)
            extent_length, pos = _read_int(data, pos, length_size)
            if construction_method == 1 and idat_payload_offset is not None:
                absolute_offset = idat_payload_offset + base_offset + extent_offset
                storage = "idat"
            else:
                absolute_offset = base_offset + extent_offset
                storage = "mdat" if construction_method == 0 else f"construction_method_{construction_method}"
            extent: dict[str, Any] = {
                "offset": extent_offset,
                "length": extent_length,
                "absolute_offset": absolute_offset,
                "storage": storage,
            }
            if extent_index is not None:
                extent["index"] = extent_index
            extents.append(extent)
        locations[str(item_id)] = {
            "version": version,
            "flags": flags,
            "construction_method": construction_method,
            "data_reference_index": data_reference_index,
            "base_offset": base_offset,
            "extents": extents,
        }
    return locations


def parse_ispe(data: bytes, box_info: dict[str, Any]) -> dict[str, Any]:
    _version, _flags, pos = _read_fullbox(data, box_info["payload_offset"])
    end = box_info["payload_offset"] + box_info["payload_size"]
    if pos + 8 > end:
        return {}
    return {"width": _u32(data, pos), "height": _u32(data, pos + 4)}


def parse_pixi(data: bytes, box_info: dict[str, Any]) -> dict[str, Any]:
    _version, _flags, pos = _read_fullbox(data, box_info["payload_offset"])
    end = box_info["payload_offset"] + box_info["payload_size"]
    if pos >= end:
        return {}
    channels = _u8(data, pos)
    pos += 1
    return {"channels": channels, "bits": list(data[pos : min(end, pos + channels)])}


def parse_auxc(data: bytes, box_info: dict[str, Any]) -> dict[str, Any]:
    version, flags, pos = _read_fullbox(data, box_info["payload_offset"])
    end = box_info["payload_offset"] + box_info["payload_size"]
    aux_type, pos = _read_cstr(data[:end], pos)
    subtype = data[pos:end].hex() if pos < end else ""
    return {"version": version, "flags": flags, "aux_type": aux_type, "subtype_hex": subtype}


def parse_colr(data: bytes, box_info: dict[str, Any]) -> dict[str, Any]:
    pos = box_info["payload_offset"]
    end = pos + box_info["payload_size"]
    if pos + 4 > end:
        return {}
    color_type = _fourcc(data[pos : pos + 4])
    result: dict[str, Any] = {"color_type": color_type}
    if color_type == "nclx" and pos + 11 <= end:
        result.update(
            {
                "colour_primaries": _u16(data, pos + 4),
                "transfer_characteristics": _u16(data, pos + 6),
                "matrix_coefficients": _u16(data, pos + 8),
                "full_range_flag": bool(_u8(data, pos + 10) & 0x80),
            }
        )
    elif color_type in ("prof", "rICC"):
        result["icc_profile_bytes"] = end - (pos + 4)
    else:
        result["payload_bytes"] = end - (pos + 4)
    return result


def parse_hvcc(data: bytes, box_info: dict[str, Any]) -> dict[str, Any]:
    pos = box_info["payload_offset"]
    end = pos + box_info["payload_size"]
    payload = data[pos:end]
    result: dict[str, Any] = {"bytes": len(payload)}
    if len(payload) >= 23:
        profile_byte = payload[1]
        result.update(
            {
                "configuration_version": payload[0],
                "general_profile_space": profile_byte >> 6,
                "general_tier_flag": bool(profile_byte & 0x20),
                "general_profile_idc": profile_byte & 0x1F,
                "general_level_idc": payload[12],
                "chroma_format": payload[16] & 0x03,
                "bit_depth_luma": (payload[17] & 0x07) + 8,
                "bit_depth_chroma": (payload[18] & 0x07) + 8,
                "num_temporal_layers": (payload[21] >> 3) & 0x07,
                "nal_unit_arrays": payload[22],
            }
        )
    return result


def parse_grid_payload(payload: bytes) -> dict[str, Any]:
    if len(payload) < 8:
        return {"payload_bytes": len(payload), "parse_error": "grid payload shorter than 8 bytes"}
    return {
        "version": payload[0],
        "flags": payload[1],
        "rows": payload[2] + 1,
        "columns": payload[3] + 1,
        "output_width": int.from_bytes(payload[4:6], "big"),
        "output_height": int.from_bytes(payload[6:8], "big"),
    }


def parse_irot(data: bytes, box_info: dict[str, Any]) -> dict[str, Any]:
    pos = box_info["payload_offset"]
    end = pos + box_info["payload_size"]
    result: dict[str, Any] = {"payload_bytes": box_info["payload_size"]}
    if pos >= end:
        result["parse_warning"] = "irot payload should be exactly 1 byte"
        return result
    angle = (_u8(data, pos) & 0x03) * 90
    result["angle_ccw_degrees"] = angle
    if box_info["payload_size"] != 1:
        result["parse_warning"] = "irot payload should be exactly 1 byte"
    return result


def parse_clap(data: bytes, box_info: dict[str, Any]) -> dict[str, Any]:
    pos = box_info["payload_offset"]
    end = pos + box_info["payload_size"]
    if pos + 32 > end:
        return {}
    names = [
        "clean_aperture_width_n",
        "clean_aperture_width_d",
        "clean_aperture_height_n",
        "clean_aperture_height_d",
        "horiz_off_n",
        "horiz_off_d",
        "vert_off_n",
        "vert_off_d",
    ]
    return {name: _u32(data, pos + index * 4) for index, name in enumerate(names)}


def parse_property(data: bytes, box_info: dict[str, Any], index: int) -> dict[str, Any]:
    parsers = {
        "ispe": parse_ispe,
        "pixi": parse_pixi,
        "auxC": parse_auxc,
        "colr": parse_colr,
        "hvcC": parse_hvcc,
        "irot": parse_irot,
        "clap": parse_clap,
    }
    parsed = parsers.get(box_info["type"], lambda _data, _box: {})(data, box_info)
    return {
        "index": index,
        "type": box_info["type"],
        "offset": box_info["offset"],
        "size": box_info["size"],
        "parsed": parsed,
    }


def parse_ipma(data: bytes, box_info: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    version, flags, pos = _read_fullbox(data, box_info["payload_offset"])
    end = box_info["payload_offset"] + box_info["payload_size"]
    if pos + 4 > end:
        return {}
    entry_count = _u32(data, pos)
    pos += 4
    associations: dict[str, list[dict[str, Any]]] = {}
    for _ in range(entry_count):
        item_id_size = 2 if version == 0 else 4
        item_id, pos = _read_int(data, pos, item_id_size)
        association_count = _u8(data, pos)
        pos += 1
        item_associations = []
        for _assoc in range(association_count):
            if flags & 1:
                raw = _u16(data, pos)
                pos += 2
                essential = bool(raw & 0x8000)
                property_index = raw & 0x7FFF
            else:
                raw = _u8(data, pos)
                pos += 1
                essential = bool(raw & 0x80)
                property_index = raw & 0x7F
            item_associations.append(
                {"property_index": property_index, "essential": essential}
            )
        associations[str(item_id)] = item_associations
    return associations


def parse_iprp(data: bytes, box_info: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    pos = box_info["payload_offset"]
    end = pos + box_info["payload_size"]
    properties: list[dict[str, Any]] = []
    associations: dict[str, list[dict[str, Any]]] = {}
    for child in iter_boxes(data, pos, end):
        if child["type"] == "ipco":
            for index, prop_box in enumerate(
                iter_boxes(data, child["payload_offset"], child["payload_offset"] + child["payload_size"]),
                start=1,
            ):
                properties.append(parse_property(data, prop_box, index))
        elif child["type"] == "ipma":
            associations.update(parse_ipma(data, child))
    return properties, associations


def parse_iref(data: bytes, box_info: dict[str, Any]) -> list[dict[str, Any]]:
    version, flags, pos = _read_fullbox(data, box_info["payload_offset"])
    end = box_info["payload_offset"] + box_info["payload_size"]
    references = []
    id_size = 2 if version == 0 else 4
    for child in iter_boxes(data, pos, end):
        cpos = child["payload_offset"]
        cend = cpos + child["payload_size"]
        if cpos + id_size + 2 > cend:
            continue
        from_item_id, cpos = _read_int(data, cpos, id_size)
        ref_count = _u16(data, cpos)
        cpos += 2
        to_item_ids = []
        for _ in range(ref_count):
            to_item_id, cpos = _read_int(data, cpos, id_size)
            to_item_ids.append(to_item_id)
        references.append(
            {
                "version": version,
                "flags": flags,
                "type": child["type"],
                "from_item_id": from_item_id,
                "to_item_ids": to_item_ids,
            }
        )
    return references


def _box_summary(boxes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "type": box["type"],
            "offset": box["offset"],
            "size": box["size"],
        }
        for box in boxes
    ]


def _payload_from_item_extents(data: bytes, item: dict[str, Any]) -> bytes:
    payload = bytearray()
    for extent in item.get("extents", []):
        offset = extent.get("absolute_offset", extent.get("offset", 0))
        length = extent.get("length", 0)
        payload.extend(data[offset : offset + length])
    return bytes(payload)


def parse_heif(data: bytes, source: str | None = None) -> dict[str, Any]:
    top_boxes = iter_boxes(data)
    result: dict[str, Any] = {
        "source": source,
        "file_size": len(data),
        "boxes": _box_summary(top_boxes),
        "ftyp": {},
        "primary_item_id": None,
        "handler": {},
        "items": {},
        "properties": [],
        "references": [],
        "styledeltamap": None,
    }
    for top in top_boxes:
        if top["type"] == "ftyp":
            result["ftyp"] = parse_ftyp(data, top)
        if top["type"] != "meta":
            continue
        meta_payload = top["payload_offset"]
        _version, _flags, meta_child_start = _read_fullbox(data, meta_payload)
        meta_children = iter_boxes(data, meta_child_start, meta_payload + top["payload_size"])
        result["meta_boxes"] = _box_summary(meta_children)
        idat_payload_offset = next(
            (child["payload_offset"] for child in meta_children if child["type"] == "idat"),
            None,
        )
        property_list: list[dict[str, Any]] = []
        property_associations: dict[str, list[dict[str, Any]]] = {}
        for child in meta_children:
            if child["type"] == "hdlr":
                result["handler"] = parse_hdlr(data, child)
            elif child["type"] == "pitm":
                result["primary_item_id"] = parse_pitm(data, child)
            elif child["type"] == "iinf":
                for item_id, item_info in parse_iinf(data, child).items():
                    item = result["items"].setdefault(item_id, {"item_id": int(item_id)})
                    item.update(item_info)
            elif child["type"] == "iloc":
                locations = parse_iloc(data, child, idat_payload_offset)
                for item_id, location in locations.items():
                    result["items"].setdefault(item_id, {"item_id": int(item_id)})
                    result["items"][item_id].update(location)
            elif child["type"] == "iprp":
                property_list, property_associations = parse_iprp(data, child)
                result["properties"] = property_list
            elif child["type"] == "iref":
                result["references"].extend(parse_iref(data, child))
        property_by_index = {prop["index"]: prop for prop in property_list}
        for item_id, associations in property_associations.items():
            item = result["items"].setdefault(item_id, {"item_id": int(item_id)})
            item_props = []
            for association in associations:
                prop = property_by_index.get(association["property_index"])
                if not prop:
                    item_props.append(association)
                    continue
                expanded = dict(association)
                expanded.update({"type": prop["type"], "parsed": prop["parsed"]})
                item_props.append(expanded)
                parsed = prop["parsed"]
                if prop["type"] == "ispe":
                    item["dimensions"] = parsed
                elif prop["type"] == "pixi":
                    item["pixi"] = parsed
                elif prop["type"] == "auxC":
                    item["aux_type"] = parsed.get("aux_type")
                elif prop["type"] == "hvcC":
                    item["hvcC"] = parsed
                elif prop["type"] == "colr":
                    item["colr"] = parsed
                elif prop["type"] == "irot":
                    item["irot"] = parsed
                elif prop["type"] == "clap":
                    item["clap"] = parsed
            item["property_associations"] = item_props
        _annotate_item_references(result["items"], result["references"])
        for item_id, item in result["items"].items():
            if item.get("item_type") == "grid" and item.get("extents"):
                item["grid"] = parse_grid_payload(_payload_from_item_extents(data, item))
            elif item.get("item_type") == "tmap" and item.get("extents"):
                item["tmap"] = {"payload_bytes": len(_payload_from_item_extents(data, item))}
        for item_id, item in result["items"].items():
            if item.get("aux_type") == STYLE_DELTA_AUX_TYPE:
                result["styledeltamap"] = {
                    "item_id": int(item_id),
                    "aux_type": item.get("aux_type"),
                    "dimensions": item.get("dimensions"),
                    "pixi": item.get("pixi"),
                    "hvcC": item.get("hvcC"),
                    "grid": item.get("grid"),
                    "extents": item.get("extents", []),
                    "derived_child_count": item.get("derived_child_count"),
                    "derived_payload_bytes": item.get("derived_payload_bytes"),
                }
                break
    return result


def _annotate_item_references(
    items: dict[str, dict[str, Any]], references: list[dict[str, Any]]
) -> None:
    for ref in references:
        from_id = str(ref["from_item_id"])
        from_item = items.setdefault(from_id, {"item_id": ref["from_item_id"]})
        from_item.setdefault("references_from", []).append(
            {"type": ref["type"], "to_item_ids": ref["to_item_ids"]}
        )
        for to_id in ref["to_item_ids"]:
            to_item = items.setdefault(str(to_id), {"item_id": to_id})
            to_item.setdefault("references_to", []).append(
                {"type": ref["type"], "from_item_id": ref["from_item_id"]}
            )
        if ref["type"] == "dimg":
            child_ids = ref["to_item_ids"]
            from_item["derived_child_item_ids"] = child_ids
            from_item["derived_child_count"] = len(child_ids)
            from_item["derived_payload_bytes"] = sum(
                sum(extent.get("length", 0) for extent in items.get(str(child_id), {}).get("extents", []))
                for child_id in child_ids
            )


def parse_file(path: Path) -> dict[str, Any]:
    return parse_heif(path.read_bytes(), str(path))


def format_markdown(parsed: dict[str, Any]) -> str:
    lines = []
    source = parsed.get("source") or "<bytes>"
    lines.append(f"# HEIF Dump: `{source}`")
    lines.append("")
    lines.append(f"- File size: {parsed.get('file_size')} bytes")
    ftyp = parsed.get("ftyp") or {}
    lines.append(f"- Major brand: {ftyp.get('major_brand', '')}")
    lines.append(f"- Compatible brands: {', '.join(ftyp.get('compatible_brands', []))}")
    lines.append(f"- Primary item id: {parsed.get('primary_item_id')}")
    handler = parsed.get("handler") or {}
    lines.append(f"- Handler: {handler.get('handler_type', '')} {handler.get('name', '')}".rstrip())
    styledelta = parsed.get("styledeltamap")
    if styledelta:
        lines.append(f"- Styledeltamap item id: {styledelta.get('item_id')}")
        lines.append(f"- Styledeltamap dimensions: {styledelta.get('dimensions')}")
        lines.append(f"- Styledeltamap pixi: {styledelta.get('pixi')}")
        lines.append(f"- Styledeltamap grid: {styledelta.get('grid')}")
        lines.append(f"- Styledeltamap tile count: {styledelta.get('derived_child_count')}")
        lines.append(f"- Styledeltamap tile payload bytes: {styledelta.get('derived_payload_bytes')}")
    else:
        lines.append("- Styledeltamap item id: not present")
    lines.append("")
    lines.append("## Top-Level Boxes")
    lines.append("")
    lines.append("| Type | Offset | Size |")
    lines.append("|---|---:|---:|")
    for box_info in parsed.get("boxes", []):
        lines.append(f"| `{box_info['type']}` | {box_info['offset']} | {box_info['size']} |")
    lines.append("")
    lines.append("## Items")
    lines.append("")
    lines.append("| Item ID | Type | Name | Dimensions | Aux Type | Pixi | Extent Bytes | Derived Tile Bytes | Properties |")
    lines.append("|---:|---|---|---|---|---|---:|---:|---|")
    for item_id in sorted(parsed.get("items", {}), key=lambda value: int(value)):
        item = parsed["items"][item_id]
        extents = item.get("extents", [])
        extent_bytes = sum(extent.get("length", 0) for extent in extents)
        properties = ", ".join(
            f"{assoc.get('property_index')}:{assoc.get('type', '?')}"
            for assoc in item.get("property_associations", [])
        )
        lines.append(
            "| {item_id} | `{item_type}` | {name} | {dimensions} | {aux_type} | {pixi} | {extent_bytes} | {derived_bytes} | {properties} |".format(
                item_id=item_id,
                item_type=item.get("item_type", ""),
                name=(item.get("name") or "").replace("|", "\\|"),
                dimensions=item.get("dimensions", ""),
                aux_type=(item.get("aux_type") or "").replace("|", "\\|"),
                pixi=item.get("pixi", ""),
                extent_bytes=extent_bytes,
                derived_bytes=item.get("derived_payload_bytes", ""),
                properties=properties,
            )
        )
    lines.append("")
    lines.append("## References")
    lines.append("")
    lines.append("| Type | From | To |")
    lines.append("|---|---:|---|")
    for ref in parsed.get("references", []):
        lines.append(f"| `{ref['type']}` | {ref['from_item_id']} | {ref['to_item_ids']} |")
    lines.append("")
    return "\n".join(lines)


def extract_item_payloads(parsed: dict[str, Any], source_path: Path, output_dir: Path) -> list[Path]:
    data = source_path.read_bytes()
    output_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for item_id, item in parsed.get("items", {}).items():
        extents = item.get("extents", [])
        if not extents:
            continue
        payload = bytearray()
        for extent in extents:
            offset = extent.get("absolute_offset", extent.get("offset", 0))
            length = extent.get("length", 0)
            payload.extend(data[offset : offset + length])
        item_type = item.get("item_type") or "item"
        aux_label = "styledeltamap" if item.get("aux_type") == STYLE_DELTA_AUX_TYPE else item_type
        output_path = output_dir / f"{source_path.stem}.item{item_id}.{aux_label}.bin"
        output_path.write_bytes(bytes(payload))
        written.append(output_path)
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description="Dump focused HEIF/ISOBMFF item structure.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--json", dest="json_path", type=Path)
    parser.add_argument("--md", dest="markdown_path", type=Path)
    parser.add_argument("--extract-items", dest="extract_dir", type=Path)
    args = parser.parse_args()

    parsed = parse_file(args.input)
    if args.json_path:
        args.json_path.parent.mkdir(parents=True, exist_ok=True)
        args.json_path.write_text(json.dumps(parsed, indent=2, ensure_ascii=False) + "\n")
    else:
        print(json.dumps(parsed, indent=2, ensure_ascii=False))
    if args.markdown_path:
        args.markdown_path.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_path.write_text(format_markdown(parsed))
    if args.extract_dir:
        extract_item_payloads(parsed, args.input, args.extract_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
