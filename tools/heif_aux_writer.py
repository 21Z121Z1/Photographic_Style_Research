#!/usr/bin/env python3
"""Standards-oriented HEIF auxiliary image writer for styledeltamap experiments."""

from __future__ import annotations

import argparse
import json
import math
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pillow_heif
from PIL import Image

from tools.heif_dump import STYLE_DELTA_AUX_TYPE, iter_boxes, parse_heif
from tools.proraw_residual_probe import (
    analyze_pair,
    convert_dng_with_sips,
    discover_pairs,
    format_markdown as format_residual_markdown,
    generate_candidate_maps,
    load_normalized_rgb,
)


@dataclass(frozen=True)
class EncodedImage:
    payload: bytes
    hvcc: bytes
    width: int
    height: int
    pixi_bits: tuple[int, ...] = (8, 8, 8)


@dataclass(frozen=True)
class BuildSummary:
    output: str
    primary_dimensions: dict[str, int]
    styledeltamap_dimensions: dict[str, int]
    grid: dict[str, int]
    candidate: str
    pair_key: str
    diagnostics_dir: str


def _u16(value: int) -> bytes:
    return value.to_bytes(2, "big")


def _u32(value: int) -> bytes:
    return value.to_bytes(4, "big")


def _u64(value: int) -> bytes:
    return value.to_bytes(8, "big")


def _box(box_type: str, payload: bytes = b"") -> bytes:
    return _u32(8 + len(payload)) + box_type.encode("ascii") + payload


def _full_box(box_type: str, version: int = 0, flags: int = 0, payload: bytes = b"") -> bytes:
    return _box(box_type, bytes([version]) + flags.to_bytes(3, "big") + payload)


def _cstr(value: str) -> bytes:
    return value.encode("utf-8") + b"\0"


def grid_payload(rows: int, columns: int, width: int, height: int) -> bytes:
    if not (1 <= rows <= 256 and 1 <= columns <= 256):
        raise ValueError(f"grid rows/columns must be in 1..256, got {rows}x{columns}")
    if not (1 <= width <= 0xFFFFFFFF and 1 <= height <= 0xFFFFFFFF):
        raise ValueError(f"grid dimensions must fit uint32, got {width}x{height}")
    return bytes([0, 0, rows - 1, columns - 1]) + _u16(width) + _u16(height)


def _ftyp() -> bytes:
    return _box("ftyp", b"heic" + _u32(0) + b"mif1heicmiaf")


def _hdlr() -> bytes:
    payload = b"\0\0\0\0" + b"pict" + b"\0" * 12 + _cstr("PictureHandler")
    return _full_box("hdlr", payload=payload)


def _pitm(item_id: int) -> bytes:
    return _full_box("pitm", payload=_u16(item_id))


def _infe(item_id: int, item_type: str, name: str = "", hidden: bool = False) -> bytes:
    flags = 1 if hidden else 0
    payload = _u16(item_id) + _u16(0) + item_type.encode("ascii") + _cstr(name)
    return _full_box("infe", version=2, flags=flags, payload=payload)


def _iinf(items: list[dict[str, Any]]) -> bytes:
    payload = _u16(len(items))
    for item in items:
        payload += _infe(
            item_id=item["id"],
            item_type=item["type"],
            name=item.get("name", ""),
            hidden=item.get("hidden", False),
        )
    return _full_box("iinf", payload=payload)


def _iloc(items: list[dict[str, Any]], mdat_payload_start: int, idat_payload: bytes) -> bytes:
    payload = bytes([0x44, 0x80]) + _u16(len(items))
    mdat_cursor = 0
    idat_cursor = 0
    for item in items:
        item_payload = item["payload"]
        storage = item["storage"]
        if storage == "idat":
            construction_method = 1
            base_offset = 0
            extent_offset = idat_cursor
            idat_cursor += len(item_payload)
        elif storage == "mdat":
            construction_method = 0
            base_offset = mdat_payload_start + mdat_cursor
            extent_offset = 0
            mdat_cursor += len(item_payload)
        else:
            raise ValueError(f"unsupported item storage {storage!r}")
        payload += (
            _u16(item["id"])
            + _u16(construction_method)
            + _u16(0)
            + _u64(base_offset)
            + _u16(1)
            + _u32(extent_offset)
            + _u32(len(item_payload))
        )
    if idat_cursor != len(idat_payload):
        raise ValueError("idat payload accounting mismatch")
    return _full_box("iloc", version=1, payload=payload)


def _ispe(width: int, height: int) -> bytes:
    return _full_box("ispe", payload=_u32(width) + _u32(height))


def _pixi(bits: tuple[int, ...]) -> bytes:
    return _full_box("pixi", payload=bytes([len(bits), *bits]))


def _colr_nclx() -> bytes:
    # BT.709 primaries, sRGB transfer, BT.601 matrix, full range.
    return _box("colr", b"nclx" + _u16(1) + _u16(13) + _u16(6) + bytes([0x80]))


def _auxc(aux_type: str) -> bytes:
    return _full_box("auxC", payload=_cstr(aux_type))


def _hvcc(payload: bytes) -> bytes:
    return _box("hvcC", payload)


def _iprp(items: list[dict[str, Any]]) -> bytes:
    property_boxes: list[bytes] = []
    associations: list[tuple[int, list[tuple[int, bool]]]] = []

    def add_property(prop: bytes) -> int:
        property_boxes.append(prop)
        return len(property_boxes)

    for item in items:
        assoc: list[tuple[int, bool]] = []
        for prop_type, prop_payload, essential in item["properties"]:
            if prop_type == "hvcC":
                prop = _hvcc(prop_payload)
            elif prop_type == "ispe":
                prop = _ispe(*prop_payload)
            elif prop_type == "pixi":
                prop = _pixi(prop_payload)
            elif prop_type == "colr":
                prop = _colr_nclx()
            elif prop_type == "auxC":
                prop = _auxc(prop_payload)
            else:
                raise ValueError(f"unsupported property type {prop_type!r}")
            assoc.append((add_property(prop), essential))
        associations.append((item["id"], assoc))

    ipco = _box("ipco", b"".join(property_boxes))
    ipma_payload = _u32(len(associations))
    for item_id, assoc in associations:
        ipma_payload += _u16(item_id) + bytes([len(assoc)])
        for property_index, essential in assoc:
            raw = property_index | (0x8000 if essential else 0)
            ipma_payload += _u16(raw)
    ipma = _full_box("ipma", flags=1, payload=ipma_payload)
    return _box("iprp", ipco + ipma)


def _reference_box(ref_type: str, from_item_id: int, to_item_ids: list[int]) -> bytes:
    payload = _u16(from_item_id) + _u16(len(to_item_ids)) + b"".join(_u16(item_id) for item_id in to_item_ids)
    return _box(ref_type, payload)


def _iref(aux_item_id: int, primary_item_id: int, tile_item_ids: list[int]) -> bytes:
    return _full_box(
        "iref",
        payload=_reference_box("dimg", aux_item_id, tile_item_ids)
        + _reference_box("auxl", aux_item_id, [primary_item_id]),
    )


def _build_items(
    primary: EncodedImage,
    style_tiles: list[EncodedImage],
    grid_width: int,
    grid_height: int,
    grid_rows: int,
    grid_columns: int,
) -> list[dict[str, Any]]:
    grid = {
        "id": 2,
        "type": "grid",
        "name": "styledeltamap",
        "hidden": True,
        "storage": "idat",
        "payload": grid_payload(grid_rows, grid_columns, grid_width, grid_height),
        "properties": [
            ("ispe", (grid_width, grid_height), False),
            ("pixi", style_tiles[0].pixi_bits, False),
            ("colr", None, False),
            ("auxC", STYLE_DELTA_AUX_TYPE, False),
        ],
    }
    items = [
        {
            "id": 1,
            "type": "hvc1",
            "name": "primary",
            "hidden": False,
            "storage": "mdat",
            "payload": primary.payload,
            "properties": [
                ("hvcC", primary.hvcc, True),
                ("ispe", (primary.width, primary.height), False),
                ("pixi", primary.pixi_bits, False),
                ("colr", None, False),
            ],
        },
        grid,
    ]
    for index, tile in enumerate(style_tiles, start=3):
        items.append(
            {
                "id": index,
                "type": "hvc1",
                "name": f"styledeltamap_tile_{index - 2:04d}",
                "hidden": True,
                "storage": "mdat",
                "payload": tile.payload,
                "properties": [
                    ("hvcC", tile.hvcc, True),
                    ("ispe", (tile.width, tile.height), False),
                    ("pixi", tile.pixi_bits, False),
                    ("colr", None, False),
                ],
            }
        )
    return items


def _meta(items: list[dict[str, Any]], mdat_payload_start: int) -> bytes:
    idat_payload = b"".join(item["payload"] for item in items if item["storage"] == "idat")
    tile_item_ids = [item["id"] for item in items if item["id"] >= 3]
    payload = (
        _hdlr()
        + _pitm(1)
        + _iinf(items)
        + _iref(aux_item_id=2, primary_item_id=1, tile_item_ids=tile_item_ids)
        + _iprp(items)
        + _box("idat", idat_payload)
        + _iloc(items, mdat_payload_start, idat_payload)
    )
    return _full_box("meta", payload=payload)


def build_styledeltamap_heif(
    primary: EncodedImage,
    style_tiles: list[EncodedImage],
    grid_width: int,
    grid_height: int,
    grid_rows: int,
    grid_columns: int,
) -> bytes:
    if len(style_tiles) != grid_rows * grid_columns:
        raise ValueError(
            f"grid {grid_rows}x{grid_columns} needs {grid_rows * grid_columns} tiles, got {len(style_tiles)}"
        )
    items = _build_items(primary, style_tiles, grid_width, grid_height, grid_rows, grid_columns)
    ftyp = _ftyp()
    meta_placeholder = _meta(items, mdat_payload_start=0)
    mdat_payload_start = len(ftyp) + len(meta_placeholder) + 8
    meta = _meta(items, mdat_payload_start=mdat_payload_start)
    if len(meta) != len(meta_placeholder):
        raise RuntimeError("meta size changed after offset resolution")
    mdat_payload = b"".join(item["payload"] for item in items if item["storage"] == "mdat")
    return ftyp + meta + _box("mdat", mdat_payload)


def _first_ipco_payload(data: bytes, box_type: str) -> bytes:
    for top in iter_boxes(data):
        if top["type"] != "meta":
            continue
        _version = data[top["payload_offset"]]
        children = iter_boxes(data, top["payload_offset"] + 4, top["payload_offset"] + top["payload_size"])
        for child in children:
            if child["type"] != "iprp":
                continue
            for iprp_child in iter_boxes(data, child["payload_offset"], child["payload_offset"] + child["payload_size"]):
                if iprp_child["type"] != "ipco":
                    continue
                for prop in iter_boxes(
                    data,
                    iprp_child["payload_offset"],
                    iprp_child["payload_offset"] + iprp_child["payload_size"],
                ):
                    if prop["type"] == box_type:
                        return data[prop["payload_offset"] : prop["payload_offset"] + prop["payload_size"]]
    raise ValueError(f"{box_type} property not found")


def _item_payload(data: bytes, item: dict[str, Any]) -> bytes:
    payload = bytearray()
    for extent in item.get("extents", []):
        offset = extent.get("absolute_offset", extent.get("offset", 0))
        length = extent.get("length", 0)
        payload.extend(data[offset : offset + length])
    return bytes(payload)


def encode_image_payload(image: Image.Image, quality: int = 90) -> EncodedImage:
    with tempfile.NamedTemporaryFile(suffix=".heic") as tmp:
        pillow_heif.from_pillow(image.convert("RGB")).save(tmp.name, quality=quality)
        data = Path(tmp.name).read_bytes()
    parsed = parse_heif(data)
    primary_id = str(parsed["primary_item_id"])
    item = parsed["items"][primary_id]
    hvcc = _first_ipco_payload(data, "hvcC")
    pixi = tuple(item.get("pixi", {}).get("bits", [8, 8, 8]))
    dimensions = item.get("dimensions") or {"width": image.width, "height": image.height}
    return EncodedImage(
        payload=_item_payload(data, item),
        hvcc=hvcc,
        width=int(dimensions["width"]),
        height=int(dimensions["height"]),
        pixi_bits=tuple(int(bit) for bit in pixi),
    )


def _image_from_float_rgb(rgb: np.ndarray) -> Image.Image:
    arr = np.clip(np.rint(rgb * 255.0), 0, 255).astype(np.uint8)
    return Image.fromarray(arr, "RGB")


def _tile_image(image: Image.Image, tile_size: int) -> tuple[list[Image.Image], int, int]:
    columns = math.ceil(image.width / tile_size)
    rows = math.ceil(image.height / tile_size)
    padded = Image.new("RGB", (columns * tile_size, rows * tile_size), (128, 128, 128))
    padded.paste(image.convert("RGB"), (0, 0))
    tiles = []
    for row in range(rows):
        for column in range(columns):
            left = column * tile_size
            top = row * tile_size
            tiles.append(padded.crop((left, top, left + tile_size, top + tile_size)))
    return tiles, rows, columns


def build_from_pair(
    root: Path,
    output: Path,
    sample: str | None = None,
    candidate: str = "neutral",
    max_dim: int = 1024,
    tile_size: int = 512,
    quality: int = 90,
) -> BuildSummary:
    pairs = discover_pairs(root)
    if not pairs:
        raise RuntimeError(f"No *_converted.DNG / *_preview.jpg pairs found in {root}")
    key = sample or max(pairs, key=lambda candidate_key: pairs[candidate_key].dng.stat().st_size)
    if key not in pairs:
        raise RuntimeError(f"Pair not found for sample {key!r}")
    pair = pairs[key]
    diagnostics_dir = output.parent / "diagnostics"
    probe = analyze_pair(pair, diagnostics_dir, max_dim)
    pair_diagnostics_dir = diagnostics_dir / key
    (pair_diagnostics_dir / "residual_probe.json").write_text(
        json.dumps(probe, indent=2, ensure_ascii=False) + "\n"
    )
    (pair_diagnostics_dir / "residual_probe.md").write_text(format_residual_markdown(probe, len(pairs)))

    dng_png = Path(probe["decoded_dng_png"])
    high_rgb, _ = load_normalized_rgb(dng_png, max_dim)
    base_rgb, _ = load_normalized_rgb(pair.preview, max_dim)
    if high_rgb.shape != base_rgb.shape:
        base_image = Image.open(pair.preview).convert("RGB").resize(
            (high_rgb.shape[1], high_rgb.shape[0]), Image.Resampling.BILINEAR
        )
        base_rgb = np.asarray(base_image).astype(np.float32) / 255.0
    candidates = generate_candidate_maps(high_rgb, base_rgb)
    if candidate not in candidates:
        raise RuntimeError(f"Unknown candidate {candidate!r}; expected one of {sorted(candidates)}")

    primary_image = _image_from_float_rgb(base_rgb)
    style_image = Image.fromarray(candidates[candidate].image, "RGB")
    style_tiles, rows, columns = _tile_image(style_image, tile_size)

    primary = encode_image_payload(primary_image, quality=quality)
    encoded_tiles = [encode_image_payload(tile, quality=quality) for tile in style_tiles]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(
        build_styledeltamap_heif(
            primary=primary,
            style_tiles=encoded_tiles,
            grid_width=style_image.width,
            grid_height=style_image.height,
            grid_rows=rows,
            grid_columns=columns,
        )
    )
    summary = BuildSummary(
        output=str(output),
        primary_dimensions={"width": primary.width, "height": primary.height},
        styledeltamap_dimensions={"width": style_image.width, "height": style_image.height},
        grid={"rows": rows, "columns": columns, "tile_size": tile_size},
        candidate=candidate,
        pair_key=key,
        diagnostics_dir=str(diagnostics_dir),
    )
    (output.parent / "build_summary.json").write_text(
        json.dumps(summary.__dict__, indent=2, ensure_ascii=False) + "\n"
    )
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Build an experimental styledeltamap auxiliary HEIF.")
    parser.add_argument(
        "--dng-root",
        type=Path,
        default=Path("/Users/retriedstormtrooper/Downloads/03_图片素材/RAW_DNG照片/RAW_DNG_JPEG_批量导出"),
    )
    parser.add_argument("--sample")
    parser.add_argument(
        "--candidate",
        choices=["neutral", "luma_residual", "chroma_luma_residual"],
        default="neutral",
    )
    parser.add_argument("--mode", choices=["apple-like-grid"], default="apple-like-grid")
    parser.add_argument("--max-dim", type=int, default=1024)
    parser.add_argument("--tile-size", type=int, default=512)
    parser.add_argument("--quality", type=int, default=90)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/constructed/iso_aux_styledeltamap/iso_aux_styledeltamap.heic"),
    )
    args = parser.parse_args()

    summary = build_from_pair(
        root=args.dng_root,
        output=args.output,
        sample=args.sample,
        candidate=args.candidate,
        max_dim=args.max_dim,
        tile_size=args.tile_size,
        quality=args.quality,
    )
    print(json.dumps(summary.__dict__, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
