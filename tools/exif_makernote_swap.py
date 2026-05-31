#!/usr/bin/env python3
"""Build Exif payload: preview JPEG's Exif with template's MakerNote injected."""

from __future__ import annotations

import struct
from pathlib import Path


def build_exif_with_template_makernote(
    template_heic_path: Path,
    preview_jpeg_path: Path,
) -> bytes:
    """Build HEIF Exif item payload using preview's Exif + template's MakerNote.

    The template's MakerNote contains 0x0054/0x005a styledeltamap tags.
    All other Exif fields come from the preview JPEG.
    """
    from tools.heif_dump import parse_file

    # 1. Extract template MakerNote
    p = parse_file(template_heic_path)
    data = template_heic_path.read_bytes()
    exif_item = p["items"].get("102", {})
    template_exif = b""
    for ext in exif_item.get("extents", []):
        template_exif += data[ext["absolute_offset"] : ext["absolute_offset"] + ext["length"]]

    template_maker = _extract_makernote(template_exif)
    if not template_maker:
        raise ValueError("Template MakerNote not found")

    # 2. Extract preview Exif APP1
    preview_data = preview_jpeg_path.read_bytes()
    preview_exif = _extract_jpeg_exif(preview_data)
    if not preview_exif:
        raise ValueError("Preview Exif not found")

    # 3. Find MakerNote in preview Exif and replace it
    tiff = bytearray(preview_exif[6:])  # skip "Exif\0\0"
    endian = ">"
    ifd0_off = struct.unpack(endian + "I", tiff[4:8])[0]

    # Find ExifIFD
    exif_ifd_off = None
    for i in range(struct.unpack(endian + "H", tiff[ifd0_off : ifd0_off + 2])[0]):
        pos = ifd0_off + 2 + i * 12
        if struct.unpack(endian + "H", tiff[pos : pos + 2])[0] == 0x8769:
            exif_ifd_off = struct.unpack(endian + "I", tiff[pos + 8 : pos + 12])[0]
            break
    if exif_ifd_off is None:
        raise ValueError("ExifIFD not found in preview Exif")

    # Find MakerNote entry in ExifIFD
    maker_entry_pos = None
    for i in range(struct.unpack(endian + "H", tiff[exif_ifd_off : exif_ifd_off + 2])[0]):
        pos = exif_ifd_off + 2 + i * 12
        if struct.unpack(endian + "H", tiff[pos : pos + 2])[0] == 0x927c:
            maker_entry_pos = pos
            break
    if maker_entry_pos is None:
        raise ValueError("MakerNote entry not found in preview ExifIFD")

    # Get old MakerNote info
    old_count = struct.unpack(endian + "I", tiff[maker_entry_pos + 4 : maker_entry_pos + 8])[0]
    old_offset = struct.unpack(endian + "I", tiff[maker_entry_pos + 8 : maker_entry_pos + 12])[0]
    new_count = len(template_maker)

    if new_count <= old_count:
        # New MakerNote fits in old space - just overwrite
        tiff[old_offset : old_offset + new_count] = template_maker
        # Zero out remaining bytes
        if new_count < old_count:
            tiff[old_offset + new_count : old_offset + old_count] = b"\x00" * (old_count - new_count)
        # Update count in IFD entry
        tiff[maker_entry_pos + 4 : maker_entry_pos + 8] = struct.pack(endian + "I", new_count)
    else:
        # New MakerNote is larger - append at end and update offset
        new_offset = len(tiff)
        tiff.extend(template_maker)
        # Update count and offset in IFD entry
        tiff[maker_entry_pos + 4 : maker_entry_pos + 8] = struct.pack(endian + "I", new_count)
        tiff[maker_entry_pos + 8 : maker_entry_pos + 12] = struct.pack(endian + "I", new_offset)

    # 4. Build HEIF Exif item payload: "Exif\0\0" + TIFF (with 4-byte size prefix)
    heif_prefix = b"\x00\x00\x00\x06Exif\x00\x00"
    return heif_prefix + bytes(tiff)


def _extract_makernote(exif_payload: bytes) -> bytes | None:
    """Extract raw MakerNote bytes from a HEIF Exif item payload."""
    tiff_idx = exif_payload.find(b"MM\x00*")
    if tiff_idx < 0:
        return None
    tiff = exif_payload[tiff_idx:]
    endian = ">"
    ifd0_off = struct.unpack(endian + "I", tiff[4:8])[0]

    exif_ifd_off = None
    for i in range(struct.unpack(endian + "H", tiff[ifd0_off : ifd0_off + 2])[0]):
        pos = ifd0_off + 2 + i * 12
        if struct.unpack(endian + "H", tiff[pos : pos + 2])[0] == 0x8769:
            exif_ifd_off = struct.unpack(endian + "I", tiff[pos + 8 : pos + 12])[0]
            break
    if exif_ifd_off is None:
        return None

    for i in range(struct.unpack(endian + "H", tiff[exif_ifd_off : exif_ifd_off + 2])[0]):
        pos = exif_ifd_off + 2 + i * 12
        if struct.unpack(endian + "H", tiff[pos : pos + 2])[0] == 0x927c:
            count = struct.unpack(endian + "I", tiff[pos + 4 : pos + 8])[0]
            offset = struct.unpack(endian + "I", tiff[pos + 8 : pos + 12])[0]
            return bytes(tiff[offset : offset + count])  # use count from IFD entry
    return None


def _extract_jpeg_exif(jpeg_data: bytes) -> bytes | None:
    """Extract the Exif APP1 payload from JPEG data."""
    if not jpeg_data.startswith(b"\xff\xd8"):
        return None
    offset = 2
    while offset + 4 <= len(jpeg_data):
        if jpeg_data[offset] != 0xFF:
            offset += 1
            continue
        while offset < len(jpeg_data) and jpeg_data[offset] == 0xFF:
            offset += 1
        if offset >= len(jpeg_data):
            break
        marker = jpeg_data[offset]
        offset += 1
        if marker in (0xD8, 0xD9):
            continue
        if marker == 0xDA:
            break
        if offset + 2 > len(jpeg_data):
            break
        seg_length = int.from_bytes(jpeg_data[offset : offset + 2], "big")
        payload_start = offset + 2
        payload_end = offset + seg_length
        if payload_end > len(jpeg_data):
            break
        if marker == 0xE1:
            payload = jpeg_data[payload_start:payload_end]
            if payload.startswith(b"Exif\x00\x00"):
                return payload
        offset = payload_end
    return None
