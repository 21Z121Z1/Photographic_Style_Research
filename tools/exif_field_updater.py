#!/usr/bin/env python3
"""Update standard Exif fields in a HEIF Exif item payload while preserving MakerNote."""

from __future__ import annotations

import struct
from pathlib import Path


# Fields to copy from preview JPEG to template Exif
# Format: (tag_id, ifd_name)
# Field type/count are read from the source; value is copied if it fits.
FIELDS_TO_COPY = [
    # IFD0
    (0x010f, "IFD0"),   # Make
    (0x0110, "IFD0"),   # Model
    (0x0112, "IFD0"),   # Orientation
    (0x011a, "IFD0"),   # XResolution
    (0x011b, "IFD0"),   # YResolution
    (0x0128, "IFD0"),   # ResolutionUnit
    (0x0131, "IFD0"),   # Software
    (0x0132, "IFD0"),   # ModifyDate
    (0x013c, "IFD0"),   # HostComputer
    (0x0213, "IFD0"),   # YCbCrPositioning

    # ExifIFD
    (0x829a, "ExifIFD"),  # ExposureTime
    (0x829d, "ExifIFD"),  # FNumber
    (0x8822, "ExifIFD"),  # ExposureProgram
    (0x8827, "ExifIFD"),  # ISO
    (0x9000, "ExifIFD"),  # ExifVersion
    (0x9003, "ExifIFD"),  # DateTimeOriginal
    (0x9004, "ExifIFD"),  # CreateDate
    (0x9010, "ExifIFD"),  # OffsetTime
    (0x9011, "ExifIFD"),  # OffsetTimeOriginal
    (0x9012, "ExifIFD"),  # OffsetTimeDigitized
    (0x9101, "ExifIFD"),  # ComponentsConfiguration
    (0x9201, "ExifIFD"),  # ShutterSpeedValue
    (0x9202, "ExifIFD"),  # ApertureValue
    (0x9203, "ExifIFD"),  # BrightnessValue
    (0x9204, "ExifIFD"),  # ExposureCompensation
    (0x9207, "ExifIFD"),  # MeteringMode
    (0x9209, "ExifIFD"),  # Flash
    (0x920a, "ExifIFD"),  # FocalLength
    (0x9214, "ExifIFD"),  # SubjectArea
    (0x9291, "ExifIFD"),  # SubSecTimeOriginal
    (0x9292, "ExifIFD"),  # SubSecTimeDigitized
    (0xa000, "ExifIFD"),  # FlashpixVersion
    (0xa001, "ExifIFD"),  # ColorSpace
    (0xa002, "ExifIFD"),  # PixelXDimension
    (0xa003, "ExifIFD"),  # PixelYDimension
    (0xa20e, "ExifIFD"),  # FocalPlaneXResolution
    (0xa20f, "ExifIFD"),  # FocalPlaneYResolution
    (0xa210, "ExifIFD"),  # FocalPlaneResolutionUnit
    (0xa217, "ExifIFD"),  # SensingMethod
    (0xa301, "ExifIFD"),  # SceneType
    (0xa401, "ExifIFD"),  # CustomRendered
    (0xa402, "ExifIFD"),  # ExposureMode
    (0xa403, "ExifIFD"),  # WhiteBalance
    (0xa405, "ExifIFD"),  # FocalLengthIn35mmFormat
    (0xa431, "ExifIFD"),  # SerialNumber
    (0xa432, "ExifIFD"),  # LensInfo
    (0xa433, "ExifIFD"),  # LensMake
    (0xa434, "ExifIFD"),  # LensModel
    (0xa406, "ExifIFD"),  # SceneCaptureType
    (0xa460, "ExifIFD"),  # GainControl

    # GPS IFD
    (0x0001, "GPS"),     # GPSLatitudeRef
    (0x0002, "GPS"),     # GPSLatitude
    (0x0003, "GPS"),     # GPSLongitudeRef
    (0x0004, "GPS"),     # GPSLongitude
    (0x0005, "GPS"),     # GPSAltitudeRef
    (0x0006, "GPS"),     # GPSAltitude
    (0x0007, "GPS"),     # GPSTimeStamp
    (0x001d, "GPS"),     # GPSDateStamp
    (0x0011, "GPS"),     # GPSImgDirectionRef
    (0x0012, "GPS"),     # GPSImgDirection
    (0x0013, "GPS"),     # GPSDestBearingRef
    (0x0014, "GPS"),     # GPSDestBearing
    (0x000c, "GPS"),     # GPSMeasureMode
    (0x000d, "GPS"),     # GPSSpeedRef
    (0x000e, "GPS"),     # GPSSpeed
    (0x001f, "GPS"),     # GPSHPositioningError
]


def _parse_ifd(tiff: bytes, ifd_offset: int, endian: str = ">") -> dict[int, tuple[int, int, bytes, int]]:
    """Parse an IFD. Returns {tag: (field_type, count, value_raw_4bytes, entry_pos)}."""
    if ifd_offset + 2 > len(tiff):
        return {}
    count = struct.unpack(endian + "H", tiff[ifd_offset : ifd_offset + 2])[0]
    entries = {}
    for i in range(count):
        pos = ifd_offset + 2 + i * 12
        if pos + 12 > len(tiff):
            break
        tag = struct.unpack(endian + "H", tiff[pos : pos + 2])[0]
        ftype = struct.unpack(endian + "H", tiff[pos + 2 : pos + 4])[0]
        fcount = struct.unpack(endian + "I", tiff[pos + 4 : pos + 8])[0]
        value_raw = tiff[pos + 8 : pos + 12]
        entries[tag] = (ftype, fcount, value_raw, pos)
    return entries


def _read_value(tiff, ftype: int, fcount: int, value_raw, tiff_base: int = 0, endian: str = ">") -> bytes:
    """Read the actual value bytes from an IFD entry.

    Args:
        tiff: The full TIFF data (or full Exif payload).
        ftype: IFD field type.
        fcount: Field count.
        value_raw: The 4-byte value/offset field from the IFD entry.
        tiff_base: Offset of the TIFF header within tiff (for offset resolution).
    """
    type_sizes = {1: 1, 2: 1, 3: 2, 4: 4, 5: 8, 7: 1, 9: 4, 10: 8, 12: 8}
    total = type_sizes.get(ftype, 1) * fcount
    if total <= 4:
        return bytes(value_raw[:total])
    else:
        offset = struct.unpack(endian + "I", bytes(value_raw))[0]
        return bytes(tiff[tiff_base + offset : tiff_base + offset + total])


def _write_value_at_offset(result: bytearray, tiff_base: int, entry_pos: int, value_raw_4bytes,
                           new_value: bytes, new_total: int, old_ftype: int, old_fcount: int,
                           endian: str = ">") -> bool:
    """Write a new value into an IFD entry at absolute position entry_pos.

    Uses the old field type/count to determine the allocated size.
    """
    if new_total <= 4:
        # Inline value - always safe to write
        new_vraw = new_value.ljust(4, b"\x00")
        result[entry_pos + 8 : entry_pos + 12] = new_vraw
        return True
    else:
        # Value at offset - use field type to determine old allocation
        type_sizes = {1: 1, 2: 1, 3: 2, 4: 4, 5: 8, 7: 1, 9: 4, 10: 8, 12: 8}
        old_alloc = type_sizes.get(old_ftype, 1) * old_fcount

        if new_total <= old_alloc:
            old_offset = struct.unpack(endian + "I", bytes(value_raw_4bytes))[0]
            abs_pos = tiff_base + old_offset
            if abs_pos + new_total <= len(result):
                result[abs_pos : abs_pos + new_total] = new_value
                return True
        return False


def update_exif_fields(template_exif: bytes, preview_exif: bytes) -> bytes:
    """Update standard Exif fields in template from preview, preserving MakerNote.

    Args:
        template_exif: The HEIF Exif item payload (includes prefix + TIFF).
        preview_exif: The JPEG Exif APP1 payload (includes "Exif\\0\\0" prefix + TIFF).

    Returns:
        Updated Exif payload with template MakerNote but preview's standard fields.
    """
    # Find TIFF data in template (may have 10-byte or 6-byte prefix)
    t_tiff_idx = template_exif.find(b"MM\x00*")
    if t_tiff_idx < 0:
        return template_exif
    result = bytearray(template_exif)

    # Find TIFF data in preview
    p_tiff_idx = preview_exif.find(b"MM\x00*")
    if p_tiff_idx < 0:
        return template_exif
    p_tiff = preview_exif[p_tiff_idx:]

    endian = ">"

    # Parse all IFDs
    # Template: result is bytearray, t_tiff_idx is where TIFF starts in result
    # Parse IFDs using result with absolute positions
    t_ifd0_off = struct.unpack(endian + "I", result[t_tiff_idx + 4 : t_tiff_idx + 8])[0]
    t_ifd0 = _parse_ifd(result, t_tiff_idx + t_ifd0_off, endian)

    # Preview: p_tiff starts at TIFF header, IFD offsets are relative to p_tiff start
    p_ifd0_off = struct.unpack(endian + "I", p_tiff[4:8])[0]
    p_ifd0 = _parse_ifd(p_tiff, p_ifd0_off, endian)

    # Find sub-IFD offsets
    def get_sub_ifd(ifd, tiff_data, ifd_tag, tiff_base):
        if ifd_tag in ifd:
            off = struct.unpack(endian + "I", ifd[ifd_tag][2])[0]
            return _parse_ifd(tiff_data, tiff_base + off, endian)
        return {}

    t_exif_ifd = get_sub_ifd(t_ifd0, result, 0x8769, t_tiff_idx)
    p_exif_ifd = get_sub_ifd(p_ifd0, p_tiff, 0x8769, 0)
    t_gps_ifd = get_sub_ifd(t_ifd0, result, 0x8825, t_tiff_idx)
    p_gps_ifd = get_sub_ifd(p_ifd0, p_tiff, 0x8825, 0)

    # Build lookup: ifd_name -> (t_entries, p_entries)
    ifd_map = {
        "IFD0": (t_ifd0, p_ifd0),
        "ExifIFD": (t_exif_ifd, p_exif_ifd),
        "GPS": (t_gps_ifd, p_gps_ifd),
    }

    type_sizes = {1: 1, 2: 1, 3: 2, 4: 4, 5: 8, 7: 1, 9: 4, 10: 8, 12: 8}

    for tag, ifd_name in FIELDS_TO_COPY:
        if ifd_name not in ifd_map:
            continue
        t_entries, p_entries = ifd_map[ifd_name]

        if tag not in t_entries or tag not in p_entries:
            continue

        t_ftype, t_fcount, t_vraw, t_pos = t_entries[tag]
        p_ftype, p_fcount, p_vraw, p_pos = p_entries[tag]

        # Read source value from preview (p_tiff starts at TIFF header, so base=0)
        p_value = _read_value(p_tiff, p_ftype, p_fcount, p_vraw, tiff_base=0, endian=endian)
        p_total = type_sizes.get(p_ftype, 1) * p_fcount

        # Write to template (tiff_base = t_tiff_idx since offsets are relative to TIFF header)
        _write_value_at_offset(result, t_tiff_idx, t_pos, t_vraw, p_value, p_total,
                               old_ftype=t_ftype, old_fcount=t_fcount, endian=endian)

    return bytes(result)


def build_updated_exif_item(template_heic_path: Path, preview_jpeg_path: Path) -> bytes:
    """Build an updated Exif item payload from template HEIC and preview JPEG.

    Keeps the template's MakerNote (with 0x0054/0x005a styledeltamap tags)
    but updates standard Exif fields (capture time, exposure, GPS, etc.) from the preview.
    """
    from tools.heif_dump import parse_file

    # Extract template Exif from HEIC
    p = parse_file(template_heic_path)
    data = template_heic_path.read_bytes()
    exif_item = p["items"].get("102", {})
    template_exif = b""
    for ext in exif_item.get("extents", []):
        template_exif += data[ext["absolute_offset"] : ext["absolute_offset"] + ext["length"]]

    # Extract preview Exif from JPEG
    preview_data = preview_jpeg_path.read_bytes()
    preview_exif = _extract_jpeg_exif(preview_data)

    if not preview_exif:
        return template_exif

    return update_exif_fields(template_exif, preview_exif)


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
