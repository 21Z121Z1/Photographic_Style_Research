#!/usr/bin/env python3
"""Load gain-map rasters from the local sample families used by this project.

The parser is intentionally narrow: it supports MPF JPEG gain maps and the
OPPO/OnePlus LHDR/UHDR private extension forms studied in proxdrtest. It does
not claim that these formats are equivalent to Apple styledeltamap semantics.
"""

from __future__ import annotations

import io
import json
import hashlib
import shutil
import struct
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image

if __package__ in (None, ""):
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.heif_dump import parse_file


QTI_MARKERS = (b"QTI Debug", b"QTI ")
FLOAT_144 = struct.pack("<f", 144.0)
OPPO_UHDR_INFO_FLOAT_COUNT = 20
APPLE_HDR_GAINMAP_AUX_TYPE = "urn:com:apple:photo:2020:aux:hdrgainmap"


@dataclass(frozen=True)
class GainMapSource:
    """Decoded gain-map source and its source-side metadata."""

    source: Path
    mode: str
    image: Image.Image
    metadata: dict[str, Any]
    raw_bytes_len: int = 0


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _item_payload(data: bytes, item: dict[str, Any]) -> bytes:
    payload = bytearray()
    for extent in item.get("extents", []):
        offset = int(extent.get("absolute_offset", extent.get("offset", 0)))
        length = int(extent.get("length", 0))
        payload.extend(data[offset : offset + length])
    return bytes(payload)


def _child_ids(item: dict[str, Any]) -> list[int]:
    if item.get("derived_child_item_ids"):
        return [int(item_id) for item_id in item["derived_child_item_ids"]]
    for ref in item.get("references_from", []):
        if ref.get("type") == "dimg":
            return [int(item_id) for item_id in ref.get("to_item_ids", [])]
    return []


def _has_apple_hdr_gainmap_marker(path: Path) -> bool:
    try:
        return APPLE_HDR_GAINMAP_AUX_TYPE.encode("utf-8") in path.read_bytes()
    except OSError:
        return False


def _sanitize_aux_type(aux_type: str) -> str:
    return (
        aux_type.replace(":", "_")
        .replace("/", "_")
        .replace(".", ".")
        .replace(",", ",")
    )


def _try_register_heif_opener() -> None:
    try:
        import pillow_heif  # type: ignore[import-not-found]

        pillow_heif.register_heif_opener()
    except Exception:
        pass


def _find_jpeg_blob(data: bytes, target_length: int | None = None) -> bytes | None:
    pos = 0
    while True:
        hit = data.find(b"\xff\xd8\xff", pos)
        if hit == -1:
            return None
        end_marker = data.find(b"\xff\xd9", hit + 3)
        if end_marker == -1:
            pos = hit + 1
            continue
        blob = data[hit : end_marker + 2]
        if target_length is None or abs(len(blob) - target_length) < 64:
            return blob
        pos = end_marker + 2


def _find_extension_start(data: bytes) -> int:
    for marker in QTI_MARKERS:
        pos = data.find(marker)
        if pos == -1:
            continue
        box_start = pos - 4
        if box_start < 0:
            continue
        box_size = struct.unpack(">I", data[box_start : box_start + 4])[0]
        if box_size >= 8:
            return box_start + box_size
    raise ValueError("QTI extension marker not found")


def _parse_manifest(data: bytes) -> tuple[list[dict[str, Any]], int, int] | None:
    json_start = data.rfind(b"[{")
    if json_start == -1:
        return None
    json_end = data.find(b"]", json_start)
    if json_end == -1:
        return None
    try:
        entries = json.loads(data[json_start : json_end + 1])
    except (ValueError, json.JSONDecodeError):
        return None
    if not isinstance(entries, list):
        return None
    return entries, json_start, json_end + 1


def _extension_region(data: bytes) -> tuple[bytes, int]:
    try:
        ext_start = _find_extension_start(data)
        return data[ext_start:], ext_start
    except ValueError:
        footer_pos = data.rfind(b"\x00jxrsq")
        if footer_pos == -1:
            return data, 0
        json_end = data.rfind(b"]", max(0, footer_pos - 8192))
        json_start = data.rfind(b"[{", max(0, json_end - 8192)) if json_end != -1 else -1
        if json_start == -1:
            return data, 0
        pos = 0
        known_types = {b"ftyp", b"meta", b"free", b"mdat", b"QTI "}
        while pos < len(data) - 8:
            box_size = struct.unpack(">I", data[pos : pos + 4])[0]
            box_type = data[pos + 4 : pos + 8]
            if box_size < 8 or pos + box_size > len(data):
                break
            if box_type not in known_types:
                return data[pos + 2168 :], pos
            pos += box_size
        return data, 0


def parse_oppo_uhdr_info(floats: tuple[float, ...]) -> dict[str, Any]:
    """Parse OPPO's confirmed 20-float RGB UHDR gain-map info block."""
    if len(floats) < OPPO_UHDR_INFO_FLOAT_COUNT:
        raise ValueError("local.uhdr.gainmap.info must contain at least 20 float32 values")
    return {
        "ratioMin": [floats[0], floats[1], floats[2]],
        "padding": floats[3],
        "ratioMax": [floats[4], floats[5], floats[6]],
        "gamma": [floats[7], floats[8], floats[9]],
        "epsilonSdr": [floats[10], floats[11], floats[12]],
        "epsilonHdr": [floats[13], floats[14], floats[15]],
        "displayRatioSdr": floats[16],
        "displayRatioHdr": floats[17],
        "scale": floats[18],
        "baseImageType": floats[19],
    }


def _score_lhdr_meta(floats: tuple[float, ...]) -> int:
    score = 0
    if abs(floats[2] - 144.0) < 0.01:
        score += 5
    if abs(floats[5] + 1.0) < 0.01:
        score += 3
    if abs(floats[18] - 10.0) < 0.01:
        score += 2
    if abs(floats[19] - 6.0) < 0.01:
        score += 2
    if 2.0 <= floats[0] <= 5.0:
        score += 2
    if 0.0 <= floats[29] <= 2000.0:
        score += 1
    return score


def _extract_lhdr_meta_float144(data: bytes) -> tuple[bytes, tuple[float, ...]] | None:
    best: tuple[bytes, tuple[float, ...]] | None = None
    best_score = 0
    off = 0
    while True:
        hit = data.find(FLOAT_144, off)
        if hit == -1:
            return best
        start = hit - 8
        if 0 <= start and start + 144 <= len(data):
            meta_bytes = data[start : start + 144]
            floats = struct.unpack("<36f", meta_bytes)
            score = _score_lhdr_meta(floats)
            if score > best_score:
                best = (meta_bytes, floats)
                best_score = score
        off = hit + 1


def extract_oppo_gainmap(path: Path) -> GainMapSource:
    """Extract OPPO/OnePlus private LHDR/UHDR gain-map data from a HEIC file."""
    data = path.read_bytes()
    ext, ext_start = _extension_region(data)
    manifest = _parse_manifest(ext)

    if manifest is not None:
        entries, json_start, _ = manifest
        info_entry = next((e for e in entries if e.get("name") == "local.uhdr.gainmap.info"), None)
        data_entry = next((e for e in entries if e.get("name") == "local.uhdr.gainmap.data"), None)
        if info_entry and data_entry:
            info_start = json_start - int(info_entry["offset"])
            info_len = int(info_entry["length"])
            gain_start = json_start - int(data_entry["offset"])
            gain_len = int(data_entry["length"])
            info_bytes = ext[info_start : info_start + info_len]
            gainmap_bytes = ext[gain_start : gain_start + gain_len]
            if len(info_bytes) < 80:
                raise ValueError("truncated OPPO UHDR info block")
            floats = struct.unpack("<20f", info_bytes[:80])
            image = Image.open(io.BytesIO(gainmap_bytes)).convert("RGB")
            return GainMapSource(
                source=path,
                mode="oppo-uhdr-rgb",
                image=image,
                metadata={
                    "container": "oppo-private",
                    "extension_start": ext_start,
                    "manifest_entries": len(entries),
                    "uhdr_info": parse_oppo_uhdr_info(floats),
                },
                raw_bytes_len=len(gainmap_bytes),
            )

    meta = _extract_lhdr_meta_float144(ext)
    entries = manifest[0] if manifest else []
    if meta is None:
        raise ValueError("OPPO private LHDR/UHDR metadata not found")
    meta_bytes, floats = meta
    mask_data = None
    if manifest is not None:
        entries, json_start, _ = manifest
        mask_entry = next((e for e in entries if e.get("name") == "local.hdr.linear.mask"), None)
        if mask_entry is not None:
            mask_start = json_start - int(mask_entry["offset"])
            mask_len = int(mask_entry["length"])
            mask_data = ext[mask_start : mask_start + mask_len]
    if mask_data is None:
        mask_data = _find_jpeg_blob(ext)
    if mask_data is None:
        raise ValueError("OPPO LHDR mask JPEG not found")

    image = Image.open(io.BytesIO(mask_data)).convert("L")
    return GainMapSource(
        source=path,
        mode="oppo-lhdr-mono",
        image=image,
        metadata={
            "container": "oppo-private",
            "extension_start": ext_start,
            "manifest_entries": len(entries),
            "lhdr_meta_floats": list(floats),
            "lhdr_meta_bytes": len(meta_bytes),
        },
        raw_bytes_len=len(mask_data),
    )


def _extract_mpf_images_from_bytes(data: bytes) -> list[bytes]:
    """Extract embedded MPF JPEGs using a conservative marker scan.

    This keeps the tool independent from Apple-template writer internals. The
    primary image is usually the first JPEG; MPImage2 is commonly the gain map.
    """
    images: list[bytes] = []
    pos = 0
    while True:
        blob = _find_jpeg_blob(data[pos:])
        if blob is None:
            return images
        blob_start = data.find(blob, pos)
        if blob_start == -1:
            return images
        images.append(blob)
        pos = blob_start + len(blob)


def _extract_mpf_images(jpeg_path: Path) -> list[bytes]:
    return _extract_mpf_images_from_bytes(jpeg_path.read_bytes())


def extract_mpf_gainmap(path: Path) -> GainMapSource:
    mp_images = _extract_mpf_images(path)
    if len(mp_images) < 2:
        raise ValueError("MPF embedded gain-map JPEG not found")
    image = Image.open(io.BytesIO(mp_images[1])).convert("RGB")
    return GainMapSource(
        source=path,
        mode="mpf-rgb",
        image=image,
        metadata={"container": "mpf", "embedded_image_index": 2, "embedded_images": len(mp_images)},
        raw_bytes_len=len(mp_images[1]),
    )


def extract_dng_preview_mpf_gainmap(path: Path) -> GainMapSource:
    """Extract an MPF gain map from a DNG's embedded PreviewImage."""
    exiftool = shutil.which("exiftool")
    if not exiftool:
        raise RuntimeError("exiftool not found; cannot extract DNG PreviewImage")
    proc = subprocess.run(
        [exiftool, "-m", "-b", "-PreviewImage", str(path)],
        check=True,
        capture_output=True,
    )
    preview = proc.stdout
    if not preview:
        raise ValueError("DNG PreviewImage is empty or missing")
    mp_images = _extract_mpf_images_from_bytes(preview)
    if len(mp_images) < 2:
        raise ValueError("DNG PreviewImage does not contain MPF gain map")
    image = Image.open(io.BytesIO(mp_images[1])).convert("RGB")
    return GainMapSource(
        source=path,
        mode="dng-preview-mpf-rgb",
        image=image,
        metadata={
            "container": "dng-preview-mpf",
            "embedded_image_index": 2,
            "embedded_images": len(mp_images),
            "preview_bytes": len(preview),
        },
        raw_bytes_len=len(mp_images[1]),
    )


def _decode_apple_aux_with_heif_convert(path: Path, aux_type: str) -> tuple[Image.Image, dict[str, Any]]:
    heif_convert = shutil.which("heif-convert")
    if not heif_convert:
        raise RuntimeError(
            "heif-convert not found; Apple HDR gain map structure is recognizable, "
            "but raster decode requires libheif's heif-convert --with-aux"
        )

    with tempfile.TemporaryDirectory(prefix="apple_heic_gainmap_") as tmpdir:
        tmp = Path(tmpdir)
        primary_out = tmp / "decoded.png"
        proc = subprocess.run(
            [heif_convert, "--with-aux", "--no-colons", str(path), str(primary_out)],
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            raise RuntimeError(
                "heif-convert could not decode Apple HDR gain map auxiliary image: "
                f"{proc.stderr.strip() or proc.stdout.strip()}"
            )

        expected = f"decoded-{_sanitize_aux_type(aux_type)}.png"
        candidates = [tmp / expected]
        candidates.extend(sorted(tmp.glob("*hdrgainmap*.png")))
        aux_path = next((candidate for candidate in candidates if candidate.exists()), None)
        if aux_path is None:
            produced = ", ".join(sorted(child.name for child in tmp.iterdir()))
            raise RuntimeError(
                "heif-convert completed, but did not emit the Apple HDR gain map PNG. "
                f"Produced files: {produced or 'none'}"
            )
        with Image.open(aux_path) as decoded:
            image = decoded.convert("L").copy()
        return image, {
            "decoder": "heif-convert --with-aux --no-colons",
            "decoder_stdout": proc.stdout.strip(),
            "decoder_stderr": proc.stderr.strip(),
            "decoded_aux_filename": aux_path.name,
        }


def extract_apple_heic_hdr_gainmap(path: Path) -> GainMapSource:
    """Extract Apple's HEIC HDR gain map auxiliary image when libheif can decode it."""
    if not _has_apple_hdr_gainmap_marker(path):
        raise ValueError("Apple HDR gain map aux type marker not found")

    parsed = parse_file(path)
    data = path.read_bytes()
    gainmap_item_id: int | None = None
    for item_id, item in parsed.get("items", {}).items():
        if item.get("aux_type") == APPLE_HDR_GAINMAP_AUX_TYPE:
            gainmap_item_id = int(item_id)
            break
    if gainmap_item_id is None:
        raise ValueError("Apple HDR gain map auxC property was not associated with an item")

    gainmap_item = parsed["items"][str(gainmap_item_id)]
    item_payload = _item_payload(data, gainmap_item)
    child_hashes: list[dict[str, Any]] = []
    for child_id in _child_ids(gainmap_item):
        child_item = parsed.get("items", {}).get(str(child_id))
        if not child_item:
            continue
        child_payload = _item_payload(data, child_item)
        child_hashes.append(
            {
                "item_id": child_id,
                "item_type": child_item.get("item_type"),
                "payload_bytes": len(child_payload),
                "payload_sha256": _sha256(child_payload),
                "dimensions": child_item.get("dimensions"),
            }
        )

    image, decode_metadata = _decode_apple_aux_with_heif_convert(path, APPLE_HDR_GAINMAP_AUX_TYPE)
    return GainMapSource(
        source=path,
        mode="apple-heic-hdrgainmap",
        image=image,
        metadata={
            "container": "apple-heic",
            "aux_type": APPLE_HDR_GAINMAP_AUX_TYPE,
            "item_id": gainmap_item_id,
            "item_type": gainmap_item.get("item_type"),
            "dimensions": gainmap_item.get("dimensions"),
            "pixi": gainmap_item.get("pixi"),
            "references_from": gainmap_item.get("references_from", []),
            "grid": gainmap_item.get("grid"),
            "payload_bytes": len(item_payload),
            "payload_sha256": _sha256(item_payload),
            "derived_children": child_hashes,
            "apple_public_description": {
                "channels": "8-bit single-channel luminance map",
                "transfer": "Rec.709 transfer function",
                "typical_resolution": "one quarter of original image resolution",
            },
            **decode_metadata,
        },
        raw_bytes_len=len(item_payload),
    )


def load_gainmap_source(path: Path, *, mode: str = "auto") -> GainMapSource:
    """Load a gain-map raster from OPPO HEIC, MPF JPEG, or a plain image file."""
    if mode not in {"auto", "apple-heic", "oppo", "mpf", "image"}:
        raise ValueError("mode must be one of: auto, apple-heic, oppo, mpf, image")
    if mode in {"auto", "oppo"} and path.suffix.lower() in {".heic", ".heif", ".hif"}:
        try:
            return extract_oppo_gainmap(path)
        except Exception:
            if mode == "oppo":
                raise
    if mode in {"auto", "apple-heic"} and path.suffix.lower() in {".heic", ".heif", ".hif"}:
        if mode == "apple-heic" or _has_apple_hdr_gainmap_marker(path):
            return extract_apple_heic_hdr_gainmap(path)
    if mode in {"auto", "mpf"} and path.suffix.lower() in {".jpg", ".jpeg"}:
        try:
            return extract_mpf_gainmap(path)
        except Exception:
            if mode == "mpf":
                raise
    if mode in {"auto", "mpf"} and path.suffix.lower() in {".dng"}:
        try:
            return extract_dng_preview_mpf_gainmap(path)
        except Exception:
            if mode == "mpf":
                raise
    _try_register_heif_opener()
    opened = Image.open(path)
    if opened.mode in {"1", "L", "I;16", "I"}:
        image = opened.convert("L")
        image_mode = "image-mono"
    else:
        image = opened.convert("RGB")
        image_mode = "image-rgb"
    return GainMapSource(
        source=path,
        mode=image_mode,
        image=image,
        metadata={"container": "image"},
        raw_bytes_len=path.stat().st_size,
    )
