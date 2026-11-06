"""Decode the isolated LinearThumbnail HEVC item without Core Image.

The recovered extract.py copies the compressed item. Parameter sets in hvcC
and the length-prefixed IDR become Annex B for ffmpeg. The decoded integers
are full-range codes; the Apple Log curve is applied by the caller.
"""
from __future__ import annotations

import struct
import subprocess
from pathlib import Path

import numpy as np

from .color import BT709_KR, BT709_KB, rgb_from_yuv420p10


def _boxes(data: bytes, start: int, end: int):
    pos = start
    while pos + 8 <= end:
        size, kind = struct.unpack_from(">I4s", data, pos)
        header = 8
        if size == 1:
            size = struct.unpack_from(">Q", data, pos + 8)[0]
            header = 16
        if size < header or pos + size > end:
            break
        yield pos, header, kind, pos + size
        pos += size


def _hvcc_nals(hvcc: bytes) -> tuple[int, list[bytes]]:
    if hvcc[0] != 1:
        raise ValueError("unsupported hvcC version")
    length_size = (hvcc[21] & 3) + 1
    count = hvcc[22]
    cursor = 23
    nals = []
    for _ in range(count):
        nal_count = struct.unpack_from(">H", hvcc, cursor + 1)[0]
        cursor += 3
        for _nal in range(nal_count):
            length = struct.unpack_from(">H", hvcc, cursor)[0]
            cursor += 2
            nals.append(hvcc[cursor:cursor + length])
            cursor += length
    return length_size, nals


def annex_b_from_isolated(path: Path) -> bytes:
    data = path.read_bytes()
    hvcc = None
    payload = None
    for pos, header, kind, end in _boxes(data, 0, len(data)):
        if kind == b"mdat":
            payload = data[pos + header:end]
        if kind != b"meta":
            continue
        child_start = pos + header
        size, token = struct.unpack_from(">I4s", data, child_start)
        if token not in {b"hdlr", b"iprp", b"iinf", b"iloc", b"pitm"}:
            child_start += 4
        for child in _boxes(data, child_start, end):
            if child[2] != b"iprp":
                continue
            for iprp_child in _boxes(data, child[0] + child[1], child[3]):
                if iprp_child[2] != b"ipco":
                    continue
                for prop in _boxes(data, iprp_child[0] + iprp_child[1], iprp_child[3]):
                    if prop[2] == b"hvcC":
                        hvcc = data[prop[0] + prop[1]:prop[3]]
    if hvcc is None or payload is None:
        raise ValueError(f"isolated linear thumbnail is missing hvcC or mdat: {path}")
    length_size, parameter_sets = _hvcc_nals(hvcc)
    cursor = 0
    samples = []
    while cursor + length_size <= len(payload):
        length = int.from_bytes(payload[cursor:cursor + length_size], "big")
        cursor += length_size
        samples.append(payload[cursor:cursor + length])
        cursor += length
    return b"".join(b"\x00\x00\x00\x01" + nal for nal in parameter_sets + samples)


def decode_isolated_rgb(path: Path, work: Path) -> tuple[np.ndarray, dict]:
    annex = annex_b_from_isolated(path)
    bitstream = work / "still-linear.hevc"
    raw_path = work / "still-linear.yuv"
    bitstream.write_bytes(annex)
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-f", "hevc", "-select_streams", "v:0",
         "-show_entries", "stream=width,height,pix_fmt,color_range,color_primaries,color_transfer,color_space",
         "-of", "json", str(bitstream)],
        check=True, capture_output=True, text=True,
    )
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-f", "hevc", "-i", str(bitstream),
         "-f", "rawvideo", "-pix_fmt", "yuv420p10le", str(raw_path)],
        check=True,
    )
    import json
    stream = json.loads(probe.stdout)["streams"][0]
    width, height = int(stream["width"]), int(stream["height"])
    raw = np.fromfile(raw_path, dtype="<u2")
    # The still item's CICP primaries are Display P3. Its YCbCr matrix is not
    # the recovered Core Image basis; BT.709 coefficients are an explicit assumption.
    rgb = rgb_from_yuv420p10(raw, width, height, 1, BT709_KR, BT709_KB)[0]
    luma = raw[:width * height]
    return rgb, {
        "width": width,
        "height": height,
        "ffmpeg": {key: stream.get(key) for key in ("pix_fmt", "color_range", "color_primaries", "color_transfer", "color_space")},
        "matrixAssumption": "bt709-coefficients-on-display-p3-primaries",
        "lumaCodeMin": int(luma.min()),
        "lumaCodeMax": int(luma.max()),
        "annexBytes": len(annex),
    }
