#!/usr/bin/env python3
"""Encode PIL images as 10-bit HEVC Main10 tiles via ffmpeg+x265."""

from __future__ import annotations

import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from PIL import Image


@dataclass(frozen=True)
class HevcNalUnit:
    """A parsed HEVC NAL unit without any Annex B or length-prefix framing."""

    nal_type: int
    payload: bytes
    offset: int | None = None


def encode_hevc10_tile(
    image: Image.Image,
    *,
    crf: int = 28,
    level_idc: float = 3.0,
    full_range: bool = False,
    item_payload_policy: str = "first_frame",
) -> tuple[bytes, bytes]:
    """Encode a PIL RGB image as a 10-bit HEVC Main10 single-frame bitstream.

    Returns (hevc_payload, hvcc_bytes).
    The hevc_payload is the raw HEVC bitstream suitable for an hvc1 item.
    The hvcc_bytes is the HEVCDecoderConfigurationRecord for property association.

    item_payload_policy:
        "first_frame" keeps the legacy first-frame payload, including parameter
        sets/SEI emitted before the first IDR picture.
        "single_idr" matches Apple still-image auxiliary items observed in
        native linearthumbnail samples: exactly one length-prefixed IDR NAL.
    """
    if image.mode != "RGB":
        image = image.convert("RGB")

    width, height = image.size

    with tempfile.TemporaryDirectory(prefix="hevc10_") as tmpdir:
        tmp = Path(tmpdir)
        yuv_path = tmp / "frame.yuv"
        hevc_path = tmp / "frame.hevc"
        hevc2_path = tmp / "frame2.hevc"

        # Convert PIL image to raw 10-bit YUV420p10le
        _save_yuv420p10le(image, yuv_path)

        # Encode 2 identical frames so x265 selects Main 10 profile (not Main 10 Intra)
        double_yuv = tmp / "frame_2f.yuv"
        double_yuv.write_bytes(yuv_path.read_bytes() * 2)

        x265_cmd = [
            "x265",
            "--input-res", f"{width}x{height}",
            "--fps", "1",
            "--input-depth", "10",
            "--output-depth", "10",
            "--profile", "main10",
            "--level-idc", str(level_idc),
            "--no-high-tier",
            "--frames", "2",
            "--crf", str(crf),
            "--input", str(double_yuv),
            "-o", str(hevc2_path),
        ]
        if full_range:
            x265_cmd[1:1] = ["--range", "full"]
        subprocess.run(
            x265_cmd,
            check=True,
            capture_output=True,
        )

        # Extract item payload according to the caller's container profile.
        hevc_data = hevc2_path.read_bytes()
        item_payload = _extract_item_payload(hevc_data, item_payload_policy)

        # For MP4Box packaging, we need Annex B format
        first_frame_annex = _extract_first_frame_annex_b(hevc_data)
        hevc_path.write_bytes(first_frame_annex)

        # Package into temporary HEIC to extract hvcC via heif_dump
        heic_path = tmp / "tile.heic"
        subprocess.run(
            ["MP4Box", "-new", "-add-image", str(hevc_path), str(heic_path)],
            check=True,
            capture_output=True,
        )

        heic_data = heic_path.read_bytes()
        hvcc_raw = _extract_hvcc_from_heic(heic_data)

        return item_payload, hvcc_raw


def encode_hevc10_still_videotoolbox(
    image: Image.Image,
    *,
    item_payload_policy: str = "single_idr",
    quality: float = 0.45,
) -> tuple[bytes, bytes]:
    """Encode a PIL image through Apple's VideoToolbox HEVC Main10 path.

    This is intended for Apple-private still auxiliary items whose native
    samples use Apple-system HEVC parameter sets, such as linearthumbnail.
    """
    if quality <= 0.0 or quality > 1.0:
        raise ValueError("quality must be in the range (0.0, 1.0]")
    if image.mode != "RGB":
        image = image.convert("RGB")

    script_path = Path(__file__).with_name("apple_vt_hevc_encoder.swift")
    if not script_path.exists():
        raise FileNotFoundError(f"VideoToolbox encoder script not found: {script_path}")

    with tempfile.TemporaryDirectory(prefix="vt_hevc10_", dir="/private/tmp") as tmpdir:
        tmp = Path(tmpdir)
        input_png = tmp / "input.png"
        hevc_path = tmp / "frame.hevc"
        image.save(input_png)

        module_cache = Path("/private/tmp/styledeltamap-swift-module-cache")
        module_cache.mkdir(parents=True, exist_ok=True)
        swift_cmd = [
            "swift",
            "-module-cache-path",
            str(module_cache),
            str(script_path),
            str(input_png),
            str(hevc_path),
            f"{quality:.6f}",
        ]
        # VideoToolbox can fail to allocate IOSurface-backed pixel buffers when
        # the Swift process is launched with stderr/stdout pipes. Let it inherit
        # the parent file descriptors instead of using capture_output=True.
        subprocess.run(swift_cmd, check=True)

        hevc_data = hevc_path.read_bytes()
        return payload_and_hvcc_from_annexb_hevc(hevc_data, item_payload_policy=item_payload_policy)


def payload_and_hvcc_from_annexb_hevc(
    hevc_data: bytes,
    *,
    item_payload_policy: str = "single_idr",
) -> tuple[bytes, bytes]:
    """Build an hvc1 item payload and hvcC record from an Annex B HEVC stream."""
    item_payload = _extract_item_payload(hevc_data, item_payload_policy)
    with tempfile.TemporaryDirectory(prefix="hevc_annexb_", dir="/private/tmp") as tmpdir:
        tmp = Path(tmpdir)
        hevc_path = tmp / "frame.hevc"
        heic_path = tmp / "tile.heic"
        hevc_path.write_bytes(hevc_data)
        subprocess.run(
            ["MP4Box", "-new", "-add-image", str(hevc_path), str(heic_path)],
            check=True,
            capture_output=True,
        )
        return item_payload, _extract_hvcc_from_heic(heic_path.read_bytes())


def parse_length_prefixed_nals(hevc_payload: bytes, *, length_size: int = 4) -> list[HevcNalUnit]:
    """Parse length-prefixed HEVC NAL units from an hvc1 item payload."""
    if length_size <= 0:
        raise ValueError("length_size must be positive")
    nals: list[HevcNalUnit] = []
    offset = 0
    data_len = len(hevc_payload)
    while offset < data_len:
        if offset + length_size > data_len:
            raise ValueError("truncated HEVC NAL length prefix")
        nal_length = int.from_bytes(hevc_payload[offset : offset + length_size], "big")
        nal_start = offset + length_size
        nal_end = nal_start + nal_length
        if nal_length <= 0:
            raise ValueError("zero-length HEVC NAL")
        if nal_end > data_len:
            raise ValueError("truncated HEVC NAL payload")
        payload = hevc_payload[nal_start:nal_end]
        nals.append(HevcNalUnit(nal_type=(payload[0] >> 1) & 0x3F, payload=payload, offset=offset))
        offset = nal_end
    return nals


def _save_yuv420p10le(image: Image.Image, path: Path) -> None:
    """Save a PIL RGB image as raw YUV420p10le (little-endian 10-bit samples)."""
    import numpy as np

    arr = np.asarray(image, dtype=np.float32) / 255.0  # [0, 1]
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]

    # BT.709 full-range conversion
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    cb = -0.1146 * r - 0.3854 * g + 0.5000 * b + 0.5
    cr = 0.5000 * r - 0.4542 * g - 0.0458 * b + 0.5

    # Scale to 10-bit [0, 1023]
    y10 = np.clip(y * 1023, 0, 1023).astype(np.uint16)
    cb10 = np.clip(cb * 1023, 0, 1023).astype(np.uint16)
    cr10 = np.clip(cr * 1023, 0, 1023).astype(np.uint16)

    # Subsample chroma 4:2:0 (center-weighted average of 2x2 blocks)
    h, w = y10.shape
    cb_sub = cb10.reshape(h // 2, 2, w // 2, 2).mean(axis=(1, 3)).astype(np.uint16)
    cr_sub = cr10.reshape(h // 2, 2, w // 2, 2).mean(axis=(1, 3)).astype(np.uint16)

    # Write planar YUV420p10le (little-endian uint16 per sample)
    with open(path, "wb") as f:
        f.write(y10.tobytes())  # Y plane: H x W
        f.write(cb_sub.tobytes())  # Cb plane: H/2 x W/2
        f.write(cr_sub.tobytes())  # Cr plane: H/2 x W/2


def _annex_b_nal_spans(hevc_data: bytes) -> list[tuple[int, int, int, int]]:
    """Return (start_code_offset, nal_start, nal_end, nal_type) spans."""
    starts: list[tuple[int, int]] = []
    i = 0
    while i < len(hevc_data) - 3:
        if hevc_data[i : i + 4] == b"\x00\x00\x00\x01":
            starts.append((i, 4))
            i += 4
        elif hevc_data[i : i + 3] == b"\x00\x00\x01":
            starts.append((i, 3))
            i += 3
        else:
            i += 1
    spans: list[tuple[int, int, int, int]] = []
    for idx, (offset, start_len) in enumerate(starts):
        nal_start = offset + start_len
        if nal_start >= len(hevc_data):
            continue
        nal_end = starts[idx + 1][0] if idx + 1 < len(starts) else len(hevc_data)
        if nal_end <= nal_start:
            continue
        nal_type = (hevc_data[nal_start] >> 1) & 0x3F
        spans.append((offset, nal_start, nal_end, nal_type))
    return spans


def parse_annex_b_nals(hevc_data: bytes) -> list[HevcNalUnit]:
    """Parse Annex B HEVC NAL units."""
    return [
        HevcNalUnit(nal_type=nal_type, payload=hevc_data[nal_start:nal_end], offset=offset)
        for offset, nal_start, nal_end, nal_type in _annex_b_nal_spans(hevc_data)
    ]


def _length_prefixed_payload(nals: list[HevcNalUnit]) -> bytes:
    result = bytearray()
    for nal in nals:
        result.extend(len(nal.payload).to_bytes(4, "big"))
        result.extend(nal.payload)
    return bytes(result)


def _extract_item_payload(hevc_data: bytes, policy: str) -> bytes:
    if policy == "first_frame":
        return _extract_first_frame(hevc_data)
    if policy == "single_idr":
        return _extract_single_idr(hevc_data)
    raise ValueError(f"unsupported item_payload_policy {policy!r}")


def _extract_first_frame(hevc_data: bytes) -> bytes:
    """Extract VPS+SPS+PPS+first IDR slice from a multi-frame HEVC bitstream.

    Returns length-prefixed NAL units (no Annex B start codes).
    """
    nals = parse_annex_b_nals(hevc_data)
    second_idr_offset = _find_second_idr_offset(nals)
    first_frame_nals = [
        nal for nal in nals if second_idr_offset is None or (nal.offset is not None and nal.offset < second_idr_offset)
    ]
    return _length_prefixed_payload(first_frame_nals)


def _extract_single_idr(hevc_data: bytes) -> bytes:
    """Extract the first IDR NAL as a one-NAL length-prefixed item payload."""
    for nal in parse_annex_b_nals(hevc_data):
        if nal.nal_type in {19, 20}:
            return _length_prefixed_payload([nal])
    raise ValueError("HEVC bitstream did not contain an IDR NAL")


def _extract_first_frame_annex_b(hevc_data: bytes) -> bytes:
    """Extract VPS+SPS+PPS+first IDR slice in Annex B format."""
    nals = parse_annex_b_nals(hevc_data)
    second_idr_offset = _find_second_idr_offset(nals)
    if second_idr_offset is not None:
        return hevc_data[:second_idr_offset]
    return hevc_data


def _find_second_idr_offset(nals: list[HevcNalUnit]) -> int | None:
    """Find the byte offset of the second IDR NAL unit."""
    idr_types = {19, 20}
    idr_count = 0
    for nal in nals:
        if nal.nal_type in idr_types:
            idr_count += 1
            if idr_count == 2 and nal.offset is not None:
                return nal.offset
    return None


def _extract_hvcc_from_heic(heic_data: bytes) -> bytes:
    """Extract the raw hvcC property box bytes from a HEIC file."""
    from tools.heif_dump import iter_boxes

    meta = None
    for box in iter_boxes(heic_data):
        if box["type"] == "meta":
            meta = box
            break
    if meta is None:
        raise ValueError("meta box not found")

    ipco = None
    for child in iter_boxes(heic_data, meta["payload_offset"] + 4, meta["payload_offset"] + meta["payload_size"]):
        if child["type"] == "iprp":
            for prop in iter_boxes(heic_data, child["payload_offset"], child["payload_offset"] + child["payload_size"]):
                if prop["type"] == "ipco":
                    ipco = prop
                    break
            break
    if ipco is None:
        raise ValueError("ipco box not found")

    for prop in iter_boxes(heic_data, ipco["payload_offset"], ipco["payload_offset"] + ipco["payload_size"]):
        if prop["type"] == "hvcC":
            # Return just the payload (without the 8-byte box header)
            # since _rebuilt_iprp will wrap it with _box("hvcC", ...)
            return heic_data[prop["payload_offset"] : prop["payload_offset"] + prop["payload_size"]]
    raise ValueError("hvcC property not found")
