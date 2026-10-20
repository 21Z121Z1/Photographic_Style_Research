"""HEIF item reader/writer helpers reused from XDRemux research (18340989)."""
#!/usr/bin/env python3
import hashlib
import json
import plistlib
import struct
import sys
from pathlib import Path


def u(data, pos, width):
    return int.from_bytes(data[pos:pos + width], "big") if width else 0


def put(value, width):
    if width == 0:
        if value:
            raise ValueError("non-zero value in zero-width field")
        return b""
    return value.to_bytes(width, "big")


def make_box(box_type, payload):
    return struct.pack(">I4s", 8 + len(payload), box_type.encode("latin1")) + payload


def boxes(data, start, end):
    pos = start
    while pos + 8 <= end:
        size = u(data, pos, 4)
        box_type = data[pos + 4:pos + 8].decode("latin1")
        header = 8
        if size == 1:
            size = u(data, pos + 8, 8)
            header = 16
        elif size == 0:
            size = end - pos
        if size < header or pos + size > end:
            raise ValueError(f"invalid {box_type} box at {pos}")
        yield {
            "pos": pos,
            "size": size,
            "header": header,
            "type": box_type,
            "data_start": pos + header,
            "data_end": pos + size,
        }
        pos += size
    if pos != end:
        raise ValueError(f"box walk stopped {end - pos} bytes early")


def parse_iinf(data, box):
    pos = box["data_start"]
    version = data[pos]
    pos += 4
    count_width = 4 if version >= 1 else 2
    count = u(data, pos, count_width)
    pos += count_width
    entries = []
    for child in boxes(data, pos, box["data_end"]):
        p = child["data_start"]
        infe_version = data[p]
        flags = u(data, p + 1, 3)
        p += 4
        item_id_width = 4 if infe_version >= 3 else 2
        item_id = u(data, p, item_id_width)
        p += item_id_width
        p += 2
        item_type = data[p:p + 4].decode("latin1")
        entries.append({
            "id": item_id,
            "type": item_type,
            "flags": flags,
            "raw": data[child["pos"]:child["pos"] + child["size"]],
        })
    if len(entries) != count:
        raise ValueError(f"iinf count mismatch: {count} != {len(entries)}")
    return version, entries


def make_iinf(version, raw_infes):
    count_width = 4 if version >= 1 else 2
    payload = bytes([version, 0, 0, 0]) + put(len(raw_infes), count_width)
    payload += b"".join(raw_infes)
    return make_box("iinf", payload)


def make_uri_infe(item_id, name, uri):
    if item_id > 0xFFFF:
        raise ValueError("URI infe v2 item ID exceeds UInt16")
    payload = bytes([2, 0, 0, 1]) + put(item_id, 2) + b"\0\0" + b"uri "
    payload += name.encode("utf-8") + b"\0" + uri.encode("utf-8") + b"\0"
    return make_box("infe", payload)


def parse_iref(data, box):
    pos = box["data_start"]
    version = data[pos]
    pos += 4
    id_width = 4 if version >= 1 else 2
    refs = []
    for child in boxes(data, pos, box["data_end"]):
        p = child["data_start"]
        from_id = u(data, p, id_width)
        p += id_width
        count = u(data, p, 2)
        p += 2
        to_ids = []
        for _ in range(count):
            to_ids.append(u(data, p, id_width))
            p += id_width
        refs.append({"type": child["type"], "from": from_id, "to": to_ids})
    return version, refs


def make_iref(version, refs):
    id_width = 4 if version >= 1 else 2
    payload = bytes([version, 0, 0, 0])
    for ref in refs:
        body = put(ref["from"], id_width) + put(len(ref["to"]), 2)
        body += b"".join(put(item_id, id_width) for item_id in ref["to"])
        payload += make_box(ref["type"], body)
    return make_box("iref", payload)


def parse_iloc(data, box):
    pos = box["data_start"]
    version = data[pos]
    flags = data[pos + 1:pos + 4]
    pos += 4
    sizes0 = data[pos]
    sizes1 = data[pos + 1]
    pos += 2
    offset_size = sizes0 >> 4
    length_size = sizes0 & 0x0F
    base_offset_size = sizes1 >> 4
    index_size = (sizes1 & 0x0F) if version in (1, 2) else 0
    count_width = 4 if version >= 2 else 2
    item_count = u(data, pos, count_width)
    pos += count_width
    item_id_size = 4 if version >= 2 else 2
    entries = []
    for _ in range(item_count):
        item_id = u(data, pos, item_id_size)
        pos += item_id_size
        construction_field = 0
        method = 0
        if version in (1, 2):
            construction_field = u(data, pos, 2)
            pos += 2
            method = construction_field & 0x0F
        data_ref = u(data, pos, 2)
        pos += 2
        base_offset = u(data, pos, base_offset_size)
        pos += base_offset_size
        extent_count = u(data, pos, 2)
        pos += 2
        extents = []
        for _ in range(extent_count):
            extent_index = None
            if index_size:
                extent_index = u(data, pos, index_size)
                pos += index_size
            offset = u(data, pos, offset_size)
            pos += offset_size
            length = u(data, pos, length_size)
            pos += length_size
            extents.append({"index": extent_index, "offset": offset, "length": length})
        entries.append({
            "id": item_id,
            "construction_field": construction_field,
            "method": method,
            "data_ref": data_ref,
            "base_offset": base_offset,
            "extents": extents,
        })
    return {
        "version": version,
        "flags": flags,
        "offset_size": offset_size,
        "length_size": length_size,
        "base_offset_size": base_offset_size,
        "index_size": index_size,
        "item_id_size": item_id_size,
        "entries": entries,
    }


def make_iloc(info, entries):
    version = info["version"]
    payload = bytes([version]) + info["flags"]
    payload += bytes([
        (info["offset_size"] << 4) | info["length_size"],
        (info["base_offset_size"] << 4)
        | (info["index_size"] if version in (1, 2) else 0),
    ])
    payload += put(len(entries), 4 if version >= 2 else 2)
    for entry in entries:
        payload += put(entry["id"], info["item_id_size"])
        if version in (1, 2):
            payload += put(entry.get("construction_field", entry["method"] & 0x0F), 2)
        payload += put(entry.get("data_ref", 0), 2)
        payload += put(entry.get("base_offset", 0), info["base_offset_size"])
        payload += put(len(entry["extents"]), 2)
        for extent in entry["extents"]:
            if info["index_size"]:
                payload += put(extent.get("index") or 0, info["index_size"])
            payload += put(extent["offset"], info["offset_size"])
            payload += put(extent["length"], info["length_size"])
    return make_box("iloc", payload)


def item_payload(data, entry, idat):
    if entry.get("data_ref", 0) != 0:
        raise ValueError("external item data is unsupported")
    output = bytearray()
    for extent in entry["extents"]:
        absolute = entry["base_offset"] + extent["offset"]
        if entry["method"] == 1:
            if idat is None:
                raise ValueError(f"item {entry['id']} uses idat but idat is missing")
            absolute += idat["data_start"]
        elif entry["method"] != 0:
            raise ValueError(f"unsupported construction method {entry['method']}")
        if absolute < 0 or extent["length"] < 0 or absolute + extent["length"] > len(data):
            raise ValueError(f"item {entry['id']} extent is outside the file")
        output += data[absolute:absolute + extent["length"]]
    return bytes(output)


