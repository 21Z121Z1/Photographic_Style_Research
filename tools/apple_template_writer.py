#!/usr/bin/env python3
"""Apple-template HEIF writer for styledeltamap parity experiments."""

from __future__ import annotations

import argparse
import io
import json
import struct
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
from PIL import Image

from tools.heif_aux_writer import _box, _full_box, _u16, _u32, _u64, encode_image_payload
from tools.heif_dump import iter_boxes, parse_file, parse_heif
from tools.hevc10_encoder import (
    encode_hevc10_still_videotoolbox,
    encode_hevc10_tile,
    payload_and_hvcc_from_annexb_hevc,
)
from tools.exif_field_updater import build_updated_exif_item
from tools.exif_makernote_swap import build_exif_with_template_makernote
from tools.proraw_residual_probe import discover_pairs
from tools.aux_generator import generate_linearthumbnail, generate_styledeltamap


PRIMARY_GRID_ITEM_ID = 49
PRIMARY_TILE_IDS = list(range(1, 49))
PRIMARY_TILE_HVCC_PROPERTY_INDEX = 23
GAINMAP_GRID_ITEM_ID = 94
GAINMAP_TILE_IDS = list(range(82, 94))
GAINMAP_TILE_HVCC_PROPERTY_INDEX = 25
STYLEDELTAMAP_TILE_IDS = list(range(51, 81))
STYLEDELTAMAP_TILE_HVCC_PROPERTY_INDEX = 24
STYLEDELTAMAP_GRID_CANVAS = (3072, 2304)
STYLEDELTAMAP_OUTPUT_SIZE = (2880, 2160)
STYLEDELTAMAP_GRID_ROWS = 5
STYLEDELTAMAP_GRID_COLS = 6
EXIF_ITEM_ID = 102
STYLE_METADATA_ITEM_ID = 101
LINTHUMB_ITEM_ID = 97
LINTHUMB_HVCC_PROPERTY_INDEX = 27
LINTHUMB_SIZE = (1024, 768)
APPLE_PRIMARY_SIZE = (4032, 3024)
APPLE_GAINMAP_SIZE = (2016, 1512)
APPLE_TILE_SIZE = 512
APPLE_GRID_CANVAS_SIZE = (4096, 3072)
APPLE_GAINMAP_CANVAS_SIZE = (2048, 1536)


@dataclass(frozen=True)
class ReplacementTile:
    payload: bytes
    hvcc: bytes
    width: int = APPLE_TILE_SIZE
    height: int = APPLE_TILE_SIZE


@dataclass(frozen=True)
class Hevc10Tile:
    payload: bytes
    hvcc: bytes
    width: int = APPLE_TILE_SIZE
    height: int = APPLE_TILE_SIZE


@dataclass(frozen=True)
class TemplateParts:
    data: bytes
    parsed: dict[str, Any]
    ftyp_box: bytes
    copied_meta_children_before_iprp: list[bytes]
    copied_meta_children_after_iprp_before_idat: list[bytes]
    ipco_property_boxes: list[bytes]
    ipma_box: bytes
    item_payloads: dict[int, bytes]
    construction_methods: dict[int, int]
    idat_item_order: list[int]
    item_order: list[int]


def _iter_jpeg_segments(data: bytes) -> list[tuple[int, int, int]]:
    if not data.startswith(b"\xff\xd8"):
        raise ValueError("not a JPEG file (missing SOI marker)")
    segments: list[tuple[int, int, int]] = []
    offset = 2
    end = len(data)
    while offset + 4 <= end:
        if data[offset] != 0xFF:
            offset += 1
            continue
        while offset < end and data[offset] == 0xFF:
            offset += 1
        if offset >= end:
            break
        marker = data[offset]
        offset += 1
        if marker in (0xD8, 0xD9):
            continue
        if marker == 0xDA:
            break
        if offset + 2 > end:
            break
        seg_length = int.from_bytes(data[offset : offset + 2], "big")
        offset += 2
        payload_start = offset
        payload_end = offset + seg_length - 2
        if payload_end > end or payload_end < payload_start:
            break
        segments.append((marker, payload_start, payload_end))
        offset = payload_end
    return segments


def extract_mpf_embedded_jpeg(jpeg_path: Path, image_number: int = 2) -> bytes:
    """Extract an embedded MPF image as raw JPEG bytes.

    Apple HDR JPEG previews often store a gain map as MPImage2.
    """

    if image_number < 1:
        raise ValueError("image_number must be 1-based")
    data = jpeg_path.read_bytes()
    mpf_tiff_start: int | None = None
    for marker, payload_start, payload_end in _iter_jpeg_segments(data):
        if marker != 0xE2:
            continue
        if payload_end - payload_start < 4:
            continue
        if data[payload_start : payload_start + 4] == b"MPF\x00":
            mpf_tiff_start = payload_start + 4
            break
    if mpf_tiff_start is None:
        raise ValueError("MPF APP2 segment not found")

    endian = data[mpf_tiff_start : mpf_tiff_start + 2]
    if endian == b"II":
        order = "<"
    elif endian == b"MM":
        order = ">"
    else:
        raise ValueError("Unsupported MPF TIFF endianness")

    def u16(pos: int) -> int:
        return struct.unpack_from(order + "H", data, pos)[0]

    def u32(pos: int) -> int:
        return struct.unpack_from(order + "I", data, pos)[0]

    if u16(mpf_tiff_start + 2) != 0x2A:
        raise ValueError("MPF TIFF header missing magic 0x2A")
    ifd0_rel = u32(mpf_tiff_start + 4)
    ifd0 = mpf_tiff_start + ifd0_rel
    if ifd0 + 2 > len(data):
        raise ValueError("MPF IFD0 offset out of range")
    entry_count = u16(ifd0)
    cursor = ifd0 + 2
    mpentry_offset_rel: int | None = None
    mpentry_count: int | None = None
    number_of_images: int | None = None
    type_sizes = {1: 1, 2: 1, 3: 2, 4: 4, 5: 8, 7: 1}
    for _ in range(entry_count):
        if cursor + 12 > len(data):
            break
        tag = u16(cursor)
        field_type = u16(cursor + 2)
        count = u32(cursor + 4)
        value_or_offset = u32(cursor + 8)
        cursor += 12
        if tag == 0xB001:
            number_of_images = value_or_offset if field_type == 4 and count == 1 else value_or_offset
        elif tag == 0xB002:
            unit = type_sizes.get(field_type)
            if unit is None:
                continue
            byte_count = count * unit
            if byte_count <= 4:
                mpentry_offset_rel = None
                mpentry_count = byte_count
            else:
                mpentry_offset_rel = value_or_offset
                mpentry_count = byte_count

    if number_of_images is None:
        raise ValueError("MPF NumberOfImages tag not found")
    if mpentry_count is None:
        raise ValueError("MPF MPEntry tag not found")
    if mpentry_count != number_of_images * 16:
        raise ValueError("MPF MPEntry length does not match NumberOfImages")
    if mpentry_offset_rel is None:
        raise ValueError("Inline MPEntry is not supported")

    mpentry_start = mpf_tiff_start + mpentry_offset_rel
    mpentry_end = mpentry_start + mpentry_count
    if mpentry_end > len(data):
        raise ValueError("MPEntry payload out of range")
    mpentry = data[mpentry_start:mpentry_end]

    entries: list[dict[str, int]] = []
    for index in range(number_of_images):
        pos = index * 16
        attr = struct.unpack_from(order + "I", mpentry, pos)[0]
        size = struct.unpack_from(order + "I", mpentry, pos + 4)[0]
        start = struct.unpack_from(order + "I", mpentry, pos + 8)[0]
        dep1 = struct.unpack_from(order + "H", mpentry, pos + 12)[0]
        dep2 = struct.unpack_from(order + "H", mpentry, pos + 14)[0]
        entries.append({"attributes": attr, "size": size, "start": start, "dep1": dep1, "dep2": dep2})

    if image_number > len(entries):
        raise ValueError(f"MPF image_number {image_number} out of range (has {len(entries)})")
    entry = entries[image_number - 1]
    raw_start = entry["start"]
    raw_size = entry["size"]
    candidates = [raw_start, mpf_tiff_start + raw_start]
    start_offset: int | None = None
    for cand in candidates:
        if 0 <= cand <= len(data) - 2 and data[cand : cand + 2] == b"\xff\xd8":
            start_offset = cand
            break
    if start_offset is None:
        raise ValueError("Could not resolve MPF image start offset")
    end_offset = start_offset + raw_size
    if end_offset > len(data):
        raise ValueError("MPF image payload extends past end of file")
    return data[start_offset:end_offset]


def extract_exif_app1_payload(jpeg_path: Path) -> bytes:
    data = jpeg_path.read_bytes()
    for marker, payload_start, payload_end in _iter_jpeg_segments(data):
        if marker != 0xE1:
            continue
        payload = data[payload_start:payload_end]
        if payload.startswith(b"Exif\x00\x00"):
            return payload
    raise ValueError("Exif APP1 payload not found")


def build_heif_exif_item_payload_from_jpeg(jpeg_path: Path) -> bytes:
    exif_payload = extract_exif_app1_payload(jpeg_path)
    return _u32(6) + exif_payload


def _raw_box(data: bytes, box_info: dict[str, Any]) -> bytes:
    return data[box_info["offset"] : box_info["offset"] + box_info["size"]]


def _payload_from_extents(data: bytes, item: dict[str, Any]) -> bytes:
    payload = bytearray()
    for extent in item.get("extents", []):
        offset = extent.get("absolute_offset", extent.get("offset", 0))
        length = extent.get("length", 0)
        payload.extend(data[offset : offset + length])
    return bytes(payload)


def _find_top_box(data: bytes, box_type: str) -> dict[str, Any]:
    for box_info in iter_boxes(data):
        if box_info["type"] == box_type:
            return box_info
    raise ValueError(f"{box_type} box not found")


def _load_template(template_path: Path) -> TemplateParts:
    data = template_path.read_bytes()
    parsed = parse_heif(data, str(template_path))
    ftyp = _find_top_box(data, "ftyp")
    meta = _find_top_box(data, "meta")
    _version = data[meta["payload_offset"]]
    meta_children = iter_boxes(data, meta["payload_offset"] + 4, meta["payload_offset"] + meta["payload_size"])

    before_iprp: list[bytes] = []
    after_iprp_before_idat: list[bytes] = []
    ipco_property_boxes: list[bytes] = []
    ipma_box = b""
    seen_iprp = False
    for child in meta_children:
        if child["type"] == "iprp":
            seen_iprp = True
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
                elif iprp_child["type"] == "ipma":
                    ipma_box = _raw_box(data, iprp_child)
            continue
        if child["type"] in {"idat", "iloc"}:
            continue
        if not seen_iprp:
            before_iprp.append(_raw_box(data, child))
        else:
            after_iprp_before_idat.append(_raw_box(data, child))

    if not ipco_property_boxes or not ipma_box:
        raise ValueError("template iprp/ipco/ipma could not be parsed")

    item_payloads = {
        int(item_id): _payload_from_extents(data, item)
        for item_id, item in parsed["items"].items()
        if item.get("extents")
    }
    construction_methods = {
        int(item_id): int(item.get("construction_method", 0))
        for item_id, item in parsed["items"].items()
    }
    idat_item_order = sorted(
        (item_id for item_id, method in construction_methods.items() if method == 1),
        key=lambda item_id: parsed["items"][str(item_id)]["extents"][0]["absolute_offset"],
    )
    return TemplateParts(
        data=data,
        parsed=parsed,
        ftyp_box=_raw_box(data, ftyp),
        copied_meta_children_before_iprp=before_iprp,
        copied_meta_children_after_iprp_before_idat=after_iprp_before_idat,
        ipco_property_boxes=ipco_property_boxes,
        ipma_box=ipma_box,
        item_payloads=item_payloads,
        construction_methods=construction_methods,
        idat_item_order=idat_item_order,
        item_order=sorted(int(item_id) for item_id in parsed["items"]),
    )


IROT_PROPERTY_INDEX_TO_ZERO = 4  # 270° -> 0° for landscape images
TMAP_ISPE_PROPERTY_INDEX = 20  # tmap's ispe property (3024x4032 or 4032x3024)


def _template_property_payload(template: TemplateParts, property_index: int, property_type: str) -> bytes:
    if property_index <= 0 or len(template.ipco_property_boxes) < property_index:
        raise ValueError(f"template does not contain property index {property_index}")
    box = template.ipco_property_boxes[property_index - 1]
    if box[4:8] != property_type.encode("ascii"):
        raise ValueError(
            f"template property {property_index} is {box[4:8].decode('latin-1')!r}, expected {property_type!r}"
        )
    return box[8:]


def _rebuilt_iprp(
    template: TemplateParts,
    hvcc_replacements: dict[int, bytes],
    *,
    landscape: bool = False,
) -> bytes:
    property_boxes = list(template.ipco_property_boxes)
    for index, hvcc in sorted(hvcc_replacements.items()):
        if index <= 0 or len(property_boxes) < index:
            raise ValueError(f"template does not contain expected hvcC property index {index}")
        property_boxes[index - 1] = _box("hvcC", hvcc)
    if landscape:
        # Set irot to 0° for non-tmap items
        if 1 <= IROT_PROPERTY_INDEX_TO_ZERO <= len(property_boxes):
            property_boxes[IROT_PROPERTY_INDEX_TO_ZERO - 1] = _box("irot", bytes([0]))
        # Swap tmap ispe dimensions (3024x4032 -> 4032x3024)
        if 1 <= TMAP_ISPE_PROPERTY_INDEX <= len(property_boxes):
            property_boxes[TMAP_ISPE_PROPERTY_INDEX - 1] = _full_box(
                "ispe", payload=_u32(4032) + _u32(3024)
            )
    return _box("iprp", _box("ipco", b"".join(property_boxes)) + template.ipma_box)


def _build_payload_maps(
    template: TemplateParts,
    primary_tiles: list[ReplacementTile],
    gainmap_tiles: list[ReplacementTile] | None,
    exif_item_payload: bytes | None,
    styledeltamap_tiles: list[Hevc10Tile] | None = None,
    style_metadata_payload: bytes | None = None,
    linearthumbnail_payload: bytes | None = None,
) -> tuple[dict[int, bytes], bytes, dict[int, int], bytes]:
    if len(primary_tiles) != len(PRIMARY_TILE_IDS):
        raise ValueError(f"expected {len(PRIMARY_TILE_IDS)} primary tiles, got {len(primary_tiles)}")
    payloads = dict(template.item_payloads)
    for item_id, tile in zip(PRIMARY_TILE_IDS, primary_tiles):
        payloads[item_id] = tile.payload

    if gainmap_tiles is not None:
        if len(gainmap_tiles) != len(GAINMAP_TILE_IDS):
            raise ValueError(f"expected {len(GAINMAP_TILE_IDS)} gain map tiles, got {len(gainmap_tiles)}")
        for item_id, tile in zip(GAINMAP_TILE_IDS, gainmap_tiles):
            payloads[item_id] = tile.payload

    if styledeltamap_tiles is not None:
        if len(styledeltamap_tiles) != len(STYLEDELTAMAP_TILE_IDS):
            raise ValueError(
                f"expected {len(STYLEDELTAMAP_TILE_IDS)} styledeltamap tiles, got {len(styledeltamap_tiles)}"
            )
        for item_id, tile in zip(STYLEDELTAMAP_TILE_IDS, styledeltamap_tiles):
            payloads[item_id] = tile.payload

    if exif_item_payload is not None:
        payloads[EXIF_ITEM_ID] = exif_item_payload

    if style_metadata_payload is not None:
        payloads[STYLE_METADATA_ITEM_ID] = style_metadata_payload

    if linearthumbnail_payload is not None:
        payloads[LINTHUMB_ITEM_ID] = linearthumbnail_payload

    idat_offsets: dict[int, int] = {}
    idat_parts = []
    cursor = 0
    for item_id in template.idat_item_order:
        payload = payloads[item_id]
        idat_offsets[item_id] = cursor
        idat_parts.append(payload)
        cursor += len(payload)

    mdat_parts = [
        payloads[item_id]
        for item_id in template.item_order
        if template.construction_methods.get(item_id, 0) == 0 and item_id in payloads
    ]
    return payloads, b"".join(idat_parts), idat_offsets, b"".join(mdat_parts)


def _rebuilt_iloc(
    template: TemplateParts,
    payloads: dict[int, bytes],
    idat_offsets: dict[int, int],
    mdat_payload_start: int,
) -> bytes:
    payload = bytes([0x44, 0x80]) + _u16(len(template.item_order))
    mdat_cursor = 0
    for item_id in template.item_order:
        item_payload = payloads.get(item_id, b"")
        construction_method = template.construction_methods.get(item_id, 0)
        if construction_method == 1:
            base_offset = 0
            extent_offset = idat_offsets[item_id]
        elif construction_method == 0:
            base_offset = mdat_payload_start + mdat_cursor
            extent_offset = 0
            mdat_cursor += len(item_payload)
        else:
            raise ValueError(f"unsupported construction method {construction_method} for item {item_id}")
        payload += (
            _u16(item_id)
            + _u16(construction_method)
            + _u16(0)
            + _u64(base_offset)
            + _u16(1)
            + _u32(extent_offset)
            + _u32(len(item_payload))
        )
    return _full_box("iloc", version=1, payload=payload)


def _build_meta(
    template: TemplateParts,
    hvcc_replacements: dict[int, bytes],
    payloads: dict[int, bytes],
    idat_payload: bytes,
    idat_offsets: dict[int, int],
    mdat_payload_start: int,
    *,
    landscape: bool = False,
) -> bytes:
    payload = b"".join(template.copied_meta_children_before_iprp)
    payload += _rebuilt_iprp(template, hvcc_replacements, landscape=landscape)
    payload += b"".join(template.copied_meta_children_after_iprp_before_idat)
    payload += _box("idat", idat_payload)
    payload += _rebuilt_iloc(template, payloads, idat_offsets, mdat_payload_start)
    return _full_box("meta", payload=payload)


def build_apple_template_parity_heif(
    template_path: Path,
    primary_tiles: list[ReplacementTile],
    *,
    gainmap_tiles: list[ReplacementTile] | None = None,
    exif_item_payload: bytes | None = None,
    styledeltamap_tiles: list[Hevc10Tile] | None = None,
    landscape: bool = False,
    style_metadata_payload: bytes | None = None,
    linearthumbnail_payload: bytes | None = None,
    linearthumbnail_hvcc: bytes | None = None,
) -> bytes:
    template = _load_template(template_path)
    hvcc_replacements: dict[int, bytes] = {PRIMARY_TILE_HVCC_PROPERTY_INDEX: primary_tiles[0].hvcc}
    if gainmap_tiles is not None:
        hvcc_replacements[GAINMAP_TILE_HVCC_PROPERTY_INDEX] = gainmap_tiles[0].hvcc
    if styledeltamap_tiles is not None:
        hvcc_replacements[STYLEDELTAMAP_TILE_HVCC_PROPERTY_INDEX] = styledeltamap_tiles[0].hvcc
    if linearthumbnail_hvcc is not None:
        hvcc_replacements[LINTHUMB_HVCC_PROPERTY_INDEX] = linearthumbnail_hvcc
    payloads, idat_payload, idat_offsets, mdat_payload = _build_payload_maps(
        template,
        primary_tiles,
        gainmap_tiles,
        exif_item_payload,
        styledeltamap_tiles,
        style_metadata_payload,
        linearthumbnail_payload,
    )
    meta_placeholder = _build_meta(
        template,
        hvcc_replacements,
        payloads,
        idat_payload,
        idat_offsets,
        mdat_payload_start=0,
        landscape=landscape,
    )
    mdat_payload_start = len(template.ftyp_box) + len(meta_placeholder) + 8
    meta = _build_meta(
        template,
        hvcc_replacements,
        payloads,
        idat_payload,
        idat_offsets,
        mdat_payload_start=mdat_payload_start,
        landscape=landscape,
    )
    if len(meta) != len(meta_placeholder):
        raise RuntimeError("meta size changed after offset resolution")
    return template.ftyp_box + meta + _box("mdat", mdat_payload)


def prepare_primary_grid_tiles(image_path: Path, quality: int = 90, rotate_ccw: bool = False) -> list[ReplacementTile]:
    image = Image.open(image_path).convert("RGB")
    if rotate_ccw:
        image = image.transpose(Image.Transpose.ROTATE_90)
    image = image.resize(APPLE_PRIMARY_SIZE, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", APPLE_GRID_CANVAS_SIZE, (0, 0, 0))
    canvas.paste(image, (0, 0))
    tiles: list[ReplacementTile] = []
    for row in range(APPLE_GRID_CANVAS_SIZE[1] // APPLE_TILE_SIZE):
        for column in range(APPLE_GRID_CANVAS_SIZE[0] // APPLE_TILE_SIZE):
            left = column * APPLE_TILE_SIZE
            top = row * APPLE_TILE_SIZE
            tile_image = canvas.crop((left, top, left + APPLE_TILE_SIZE, top + APPLE_TILE_SIZE))
            encoded = encode_image_payload(tile_image, quality=quality)
            tiles.append(ReplacementTile(payload=encoded.payload, hvcc=encoded.hvcc))
    return tiles


def prepare_hdr_gainmap_grid_tiles_from_preview(preview_jpeg_path: Path, quality: int = 90, rotate_ccw: bool = False) -> list[ReplacementTile]:
    mpf_jpeg = extract_mpf_embedded_jpeg(preview_jpeg_path, image_number=2)
    gainmap = Image.open(io.BytesIO(mpf_jpeg)).convert("L")
    if rotate_ccw:
        gainmap = gainmap.transpose(Image.Transpose.ROTATE_90)
    gainmap = gainmap.resize(APPLE_GAINMAP_SIZE, Image.Resampling.LANCZOS)
    canvas = Image.new("L", APPLE_GAINMAP_CANVAS_SIZE, 0)
    canvas.paste(gainmap, (0, 0))
    canvas_rgb = canvas.convert("RGB")
    tiles: list[ReplacementTile] = []
    for row in range(APPLE_GAINMAP_CANVAS_SIZE[1] // APPLE_TILE_SIZE):
        for column in range(APPLE_GAINMAP_CANVAS_SIZE[0] // APPLE_TILE_SIZE):
            left = column * APPLE_TILE_SIZE
            top = row * APPLE_TILE_SIZE
            tile_image = canvas_rgb.crop((left, top, left + APPLE_TILE_SIZE, top + APPLE_TILE_SIZE))
            encoded = encode_image_payload(tile_image, quality=quality)
            tiles.append(ReplacementTile(payload=encoded.payload, hvcc=encoded.hvcc))
    hvcc0 = tiles[0].hvcc if tiles else b""
    if any(tile.hvcc != hvcc0 for tile in tiles):
        raise ValueError("gain map tiles produced multiple hvcC configurations")
    return tiles


def prepare_styledeltamap_tiles(
    preview_jpeg_path: Path,
    *,
    amplitude: float = 2.0,
    crf: int = 28,
) -> list[Hevc10Tile]:
    """Generate 30 neutral 10-bit HEVC Main10 tiles for the styledeltamap.

    Generates a constant-neutral map (value 128 in 8-bit / ~512 in 10-bit)
    matching the observed Apple-native styledeltamap content when no
    Photographic Style is applied.  Each tile is encoded as 10-bit HEVC
    Main10 via the ffmpeg+x265 pipeline.
    """
    sdmap_result = generate_styledeltamap(
        width=STYLEDELTAMAP_OUTPUT_SIZE[0],
        height=STYLEDELTAMAP_OUTPUT_SIZE[1],
    )
    tile_img_array = np.asarray(sdmap_result.image)

    canvas = np.zeros((STYLEDELTAMAP_GRID_CANVAS[1], STYLEDELTAMAP_GRID_CANVAS[0], 3), dtype=np.uint8)
    h, w = tile_img_array.shape[:2]
    canvas[:h, :w, :] = tile_img_array

    tiles: list[Hevc10Tile] = []
    common_hvcc: bytes | None = None
    for row in range(STYLEDELTAMAP_GRID_ROWS):
        for col in range(STYLEDELTAMAP_GRID_COLS):
            left = col * APPLE_TILE_SIZE
            top = row * APPLE_TILE_SIZE
            tile_arr = canvas[top : top + APPLE_TILE_SIZE, left : left + APPLE_TILE_SIZE, :]
            tile_img = Image.fromarray(tile_arr, "RGB")
            payload, hvcc = encode_hevc10_tile(tile_img, crf=crf)
            if common_hvcc is None:
                common_hvcc = hvcc
            tiles.append(Hevc10Tile(payload=payload, hvcc=common_hvcc))

    if not tiles:
        raise ValueError("no styledeltamap tiles were generated")
    return tiles


def compute_luma_percentiles(image_path: Path) -> dict[str, float]:
    """Compute BT.709 luminance percentiles from an image for style metadata."""
    import numpy as np

    img = Image.open(image_path).convert("RGB")
    arr = np.asarray(img, dtype=np.float32) / 255.0
    luma = 0.2126 * arr[:, :, 0] + 0.7152 * arr[:, :, 1] + 0.0722 * arr[:, :, 2]

    percentiles = {}
    for name, pct in [("p02", 2), ("p10", 10), ("p25", 25), ("p50", 50), ("p75", 75), ("p98", 98)]:
        percentiles[name] = float(np.percentile(luma, pct))
    percentiles["blackPoint"] = float(np.percentile(luma, 0.5))
    percentiles["whitePoint"] = float(np.percentile(luma, 99.5))
    percentiles["highKey"] = float(np.percentile(luma, 95))
    return percentiles


def update_style_metadata_bplist(
    template_bplist: bytes,
    preview_jpeg_path: Path,
) -> bytes:
    """Update style metadata bplist with image-specific LinearImage percentiles."""
    import plistlib

    obj = plistlib.loads(template_bplist)
    percentiles = compute_luma_percentiles(preview_jpeg_path)

    key6 = obj.get("6", {})
    if "LinearImage" in key6 and isinstance(key6["LinearImage"], dict):
        key6["LinearImage"].update(percentiles)

    return plistlib.dumps(obj, fmt=plistlib.FMT_BINARY)


def build_from_pair_with_apple_template(
    root: Path,
    template_path: Path,
    output: Path,
    sample: str | None = None,
    quality: int = 90,
    use_preview_gainmap: bool = False,
    use_preview_exif: bool = False,
    generate_styledeltamap: bool = False,
    styledeltamap_crf: int = 28,
    landscape: bool = False,
    use_preview_style_metadata: bool = False,
    update_exif_fields: bool = False,
    swap_makernote: bool = False,
    generate_linearthumb: bool = False,
    linearthumb_crf: int = 28,
    linearthumb_path: Path | None = None,
    linearthumb_encoder: str = "x265",
    linearthumb_vt_quality: float = 0.45,
    linearthumb_hevc_path: Path | None = None,
    use_template_linearthumb_hvcc: bool = False,
) -> dict[str, Any]:
    pairs = discover_pairs(root)
    if not pairs:
        raise RuntimeError(f"No *_converted.DNG / *_preview.jpg pairs found in {root}")
    key = sample or max(pairs, key=lambda candidate_key: pairs[candidate_key].dng.stat().st_size)
    if key not in pairs:
        raise RuntimeError(f"Pair not found for sample {key!r}")
    preview_img = Image.open(pairs[key].preview).convert("RGB")
    # For landscape images with irot=0°, don't rotate the preview.
    # For portrait images with irot=270°, rotate preview 90° CCW to match template storage.
    rotate_ccw = not landscape and preview_img.width > preview_img.height
    tiles = prepare_primary_grid_tiles(pairs[key].preview, quality=quality, rotate_ccw=rotate_ccw)
    gainmap_tiles = (
        prepare_hdr_gainmap_grid_tiles_from_preview(pairs[key].preview, quality=quality, rotate_ccw=rotate_ccw)
        if use_preview_gainmap
        else None
    )
    if swap_makernote:
        exif_item_payload = build_exif_with_template_makernote(template_path, pairs[key].preview)
    elif update_exif_fields:
        exif_item_payload = build_updated_exif_item(template_path, pairs[key].preview)
    elif use_preview_exif:
        exif_item_payload = build_heif_exif_item_payload_from_jpeg(pairs[key].preview)
    else:
        exif_item_payload = None
    styledeltamap_tiles = (
        prepare_styledeltamap_tiles(pairs[key].preview, crf=styledeltamap_crf)
        if generate_styledeltamap
        else None
    )
    linearthumb_payload: bytes | None = None
    linearthumb_hvcc: bytes | None = None
    def encode_linearthumb_image(image: Image.Image) -> tuple[bytes, bytes]:
        if linearthumb_encoder == "x265":
            return encode_hevc10_tile(
                image,
                crf=linearthumb_crf,
                level_idc=3.1,
                full_range=True,
                item_payload_policy="single_idr",
            )
        if linearthumb_encoder == "videotoolbox":
            return encode_hevc10_still_videotoolbox(
                image,
                item_payload_policy="single_idr",
                quality=linearthumb_vt_quality,
            )
        raise ValueError(f"unsupported linearthumb_encoder {linearthumb_encoder!r}")

    if linearthumb_hevc_path:
        linearthumb_payload, linearthumb_hvcc = payload_and_hvcc_from_annexb_hevc(
            linearthumb_hevc_path.read_bytes(),
            item_payload_policy="single_idr",
        )
    elif linearthumb_path:
        lt_result = generate_linearthumbnail(
            linearthumb_path,
            max_dim=max(LINTHUMB_SIZE),
            rotate_ccw=False,
        )
        lt_img = lt_result.image.resize(LINTHUMB_SIZE, Image.Resampling.LANCZOS)
        linearthumb_payload, linearthumb_hvcc = encode_linearthumb_image(lt_img)
    elif generate_linearthumb:
        lt_result = generate_linearthumbnail(pairs[key].preview, max_dim=1024, rotate_ccw=rotate_ccw)
        lt_img = lt_result.image.resize(LINTHUMB_SIZE, Image.Resampling.LANCZOS)
        linearthumb_payload, linearthumb_hvcc = encode_linearthumb_image(lt_img)
    if linearthumb_hvcc is not None and use_template_linearthumb_hvcc:
        template = _load_template(template_path)
        linearthumb_hvcc = _template_property_payload(template, LINTHUMB_HVCC_PROPERTY_INDEX, "hvcC")
    style_metadata_payload = None
    if use_preview_style_metadata:
        template = _load_template(template_path)
        template_style_meta = template.item_payloads.get(101, b"")
        if template_style_meta:
            style_metadata_payload = update_style_metadata_bplist(template_style_meta, pairs[key].preview)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(
        build_apple_template_parity_heif(
            template_path,
            tiles,
            gainmap_tiles=gainmap_tiles,
            exif_item_payload=exif_item_payload,
            styledeltamap_tiles=styledeltamap_tiles,
            landscape=landscape,
            style_metadata_payload=style_metadata_payload,
            linearthumbnail_payload=linearthumb_payload,
            linearthumbnail_hvcc=linearthumb_hvcc,
        )
    )
    replaced_from_preview = ["Primary image tile payloads (preview JPEG)"]
    if use_preview_gainmap:
        replaced_from_preview.append("HDR gain map tile payloads (MPImage2)")
    if use_preview_exif:
        replaced_from_preview.append("Exif/MakerNote item payload (full replacement)")
    if update_exif_fields:
        replaced_from_preview.append("Exif standard fields (capture time, exposure, etc.) from preview")
    if swap_makernote:
        replaced_from_preview.append("Exif (preview full + template MakerNote 0x0054/0x005a)")
    if generate_styledeltamap:
        replaced_from_preview.append("styledeltamap 10-bit HEVC tile payloads (generated near-neutral)")
    if generate_linearthumb:
        replaced_from_preview.append(
            f"linear thumbnail 10-bit HEVC payload (affine-fitted from preview, {linearthumb_encoder})"
        )
    if linearthumb_path:
        replaced_from_preview.append(
            f"linear thumbnail 10-bit HEVC payload (affine-fitted from {linearthumb_path}, {linearthumb_encoder})"
        )
    if linearthumb_hevc_path:
        replaced_from_preview.append(f"linear thumbnail 10-bit HEVC payload (preencoded Annex B {linearthumb_hevc_path})")
    if linearthumb_hvcc is not None and use_template_linearthumb_hvcc:
        replaced_from_preview.append("linear thumbnail hvcC property copied from Apple template")
    if use_preview_style_metadata:
        replaced_from_preview.append("style metadata bplist (LinearImage percentiles from preview)")

    copied_from_template = [
        "semantic sky matte auxiliary item",
        "Apple ftyp brands and non-iloc meta references",
    ]
    linearthumb_replaced = generate_linearthumb or linearthumb_path is not None or linearthumb_hevc_path is not None
    if not linearthumb_replaced:
        copied_from_template.insert(0, "linear thumbnail auxiliary item and metadata")
    if not generate_styledeltamap:
        copied_from_template.insert(0, "styledeltamap grid and 10-bit HEVC tile payloads")
    if not use_preview_style_metadata:
        copied_from_template.insert(len(copied_from_template) - 1, "style metadata URI item")
    copied_from_template.insert(1, "tmap item payload")
    if use_preview_gainmap:
        copied_from_template.insert(1, "HDR gain map grid payload and aux item graph")
    else:
        copied_from_template.insert(1, "HDR gain map grid and HEVC tile payloads")
    if not (use_preview_exif or update_exif_fields or swap_makernote):
        copied_from_template.insert(len(copied_from_template) - 1, "Exif/MakerNote item")
    elif update_exif_fields or swap_makernote:
        copied_from_template.insert(
            len(copied_from_template) - 1,
            "Apple MakerNote private subpayload including 0x0054/0x005a",
        )
    if landscape:
        copied_from_template.append("irot=0° and tmap ispe=4032x3024 (landscape mode)")
    summary = {
        "output": str(output),
        "template": str(template_path),
        "sample": key,
        "preview": str(pairs[key].preview),
        "primary_grid": {
            "output_width": APPLE_PRIMARY_SIZE[0],
            "output_height": APPLE_PRIMARY_SIZE[1],
            "tile_size": APPLE_TILE_SIZE,
            "rows": APPLE_GRID_CANVAS_SIZE[1] // APPLE_TILE_SIZE,
            "columns": APPLE_GRID_CANVAS_SIZE[0] // APPLE_TILE_SIZE,
            "tile_count": len(tiles),
        },
        "replaced_from_preview": replaced_from_preview,
        "copied_from_template": copied_from_template,
        "experimental_boundary": "Apple private auxiliary and metadata payloads remain template-copied unless explicitly listed under replaced_from_preview.",
        "linearthumbnail_payload_policy": "single_idr" if linearthumb_replaced else "template",
        "linearthumbnail_encoder": (
            "preencoded-annexb" if linearthumb_hevc_path else linearthumb_encoder if linearthumb_replaced else "template"
        ),
        "linearthumbnail_vt_quality": (
            linearthumb_vt_quality
            if linearthumb_replaced and not linearthumb_hevc_path and linearthumb_encoder == "videotoolbox"
            else None
        ),
        "linearthumbnail_hvcc_source": (
            "template"
            if linearthumb_hvcc is not None and use_template_linearthumb_hvcc
            else "encoder"
            if linearthumb_hvcc is not None
            else "template"
        ),
    }
    (output.parent / "build_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Build an Apple-template styledeltamap parity HEIF.")
    parser.add_argument("--template", type=Path, default=Path("Apple_Native_Samples/IMG_0032.HEIC"))
    parser.add_argument(
        "--dng-root",
        type=Path,
        default=Path("/Users/retriedstormtrooper/Downloads/03_图片素材/RAW_DNG照片/RAW_DNG_JPEG_批量导出"),
    )
    parser.add_argument("--sample", default="IMG_0342")
    parser.add_argument("--quality", type=int, default=90)
    parser.add_argument(
        "--use-preview-gainmap",
        action="store_true",
        help="Replace HDR gain map tile payloads using MPF MPImage2 extracted from the preview JPEG.",
    )
    parser.add_argument(
        "--use-preview-exif",
        action="store_true",
        help="Replace Exif/MakerNote item payload using the preview JPEG's Exif APP1 payload.",
    )
    parser.add_argument(
        "--generate-styledeltamap",
        action="store_true",
        help="Generate image-specific near-neutral 10-bit HEVC Main10 styledeltamap tiles.",
    )
    parser.add_argument(
        "--styledeltamap-crf",
        type=int,
        default=28,
        help="CRF quality for styledeltamap 10-bit HEVC tile encoding (default: 28).",
    )
    parser.add_argument(
        "--landscape",
        action="store_true",
        help="Set irot=0° and tmap ispe=4032x3024 for landscape images. Use when the preview JPEG is landscape.",
    )
    parser.add_argument(
        "--use-preview-style-metadata",
        action="store_true",
        help="Update style metadata bplist with image-specific LinearImage percentiles from the preview JPEG.",
    )
    parser.add_argument(
        "--update-exif-fields",
        action="store_true",
        help="Update standard Exif fields (capture time, exposure, etc.) from preview while preserving template MakerNote.",
    )
    parser.add_argument(
        "--swap-makernote",
        action="store_true",
        help="Use preview's full Exif with template's MakerNote (0x0054/0x005a) injected.",
    )
    parser.add_argument(
        "--generate-linearthumb",
        action="store_true",
        help="Generate linear thumbnail from preview JPG instead of copying from template.",
    )
    parser.add_argument(
        "--linearthumb-crf",
        type=int,
        default=28,
        help="CRF quality for linear thumbnail 10-bit HEVC encoding (default: 28).",
    )
    parser.add_argument(
        "--linearthumb-encoder",
        choices=("x265", "videotoolbox"),
        default="x265",
        help="HEVC encoder for generated linear thumbnail payloads.",
    )
    parser.add_argument(
        "--linearthumb-vt-quality",
        type=float,
        default=0.45,
        help="VideoToolbox quality for generated linear thumbnail HEVC payloads (default: 0.45).",
    )
    parser.add_argument(
        "--linearthumb-path",
        type=Path,
        default=None,
        help="Path to a PNG file to use as the linear thumbnail (resized to 1024x768).",
    )
    parser.add_argument(
        "--linearthumb-hevc-path",
        type=Path,
        default=None,
        help="Path to a preencoded Annex B HEVC stream for the linear thumbnail.",
    )
    parser.add_argument(
        "--use-template-linearthumb-hvcc",
        action="store_true",
        help="Use the Apple template's linearthumbnail hvcC property for generated linearthumbnail payloads.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/constructed/apple_parity_styledeltamap/apple_parity_styledeltamap.heic"),
    )
    args = parser.parse_args()
    summary = build_from_pair_with_apple_template(
        root=args.dng_root,
        template_path=args.template,
        output=args.output,
        sample=args.sample,
        quality=args.quality,
        use_preview_gainmap=args.use_preview_gainmap,
        use_preview_exif=args.use_preview_exif,
        generate_styledeltamap=args.generate_styledeltamap,
        styledeltamap_crf=args.styledeltamap_crf,
        landscape=args.landscape,
        use_preview_style_metadata=args.use_preview_style_metadata,
        update_exif_fields=args.update_exif_fields,
        swap_makernote=args.swap_makernote,
        generate_linearthumb=args.generate_linearthumb,
        linearthumb_crf=args.linearthumb_crf,
        linearthumb_path=args.linearthumb_path,
        linearthumb_encoder=args.linearthumb_encoder,
        linearthumb_vt_quality=args.linearthumb_vt_quality,
        linearthumb_hevc_path=args.linearthumb_hevc_path,
        use_template_linearthumb_hvcc=args.use_template_linearthumb_hvcc,
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
