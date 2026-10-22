"""Actual iPhone17,3/24A446 plugin GTC-table construction, not pixel GTM.

Extends the existing S54 ratio model with the previously untested non-257
header branch. Kernel coordinates, actual tone curves, capture color space and
the shader's sampler/half arithmetic remain separate caller obligations.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import math
from pathlib import Path
import struct
import sys
import numpy as np
from numpy.typing import NDArray

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hdr-native"))
from producer_curve_record_s54 import f32, from_bits, ios_gtc_input_ratios


def round_nonnegative_fraction_f32(value: Fraction) -> float:
    """One correctly rounded RN-even f32 result, including rare double ties.

    The initial f64 conversion is within one f32 neighbor. Compare exact
    rational distances to it and its adjacent f32s; prefer an even low bit.
    This avoids treating Python's separate multiply/add as an ARM FMADD.
    """
    if not 0 <= value <= 65535:
        raise ValueError("This operator's declared finite nonnegative range is 0..65535")
    initial = struct.unpack("<I", struct.pack("<f", float(value)))[0]
    candidates = [b for b in (initial-1, initial, initial+1) if 0 <= b <= 0x477fff00]
    bits = min(candidates, key=lambda b: (abs(Fraction(from_bits(b)) - value), b & 1))
    return from_bits(bits)


@dataclass(frozen=True)
class GTCTexture:
    header: int
    normalized_nodes: NDArray
    half_values: NDArray[np.float16]
    branch: str
    coordinate_domain: str = "Metadata curve-table coordinate; not established as scene-linear RGB"
    camera_inverse_verified: bool = False


def build_texture(raw: bytes, *, max_header: int = 4097) -> GTCTexture:
    """Construct 256 R16Float values for finite, nonzero-normalizer records.

    H is the first uint16, not a product/metadata generation. This helper reads
    words[1..H-1], normalizes by words[H-1], and ignores trailing words. The
    plugin rejects H<=64; our bounded harness additionally limits H<=4097.
    A zero divisor is explicitly unsupported, preserving its native Inf/NaN
    obligation rather than claiming that the original implementation rejects it.
    """
    if len(raw) < 2 or len(raw) % 2:
        raise ValueError("Supply a complete little-endian uint16 record")
    header = struct.unpack_from("<H", raw)[0]
    if not 65 <= header <= max_header or max_header > 4097:
        raise ValueError("Supported bounded header range is 65..4097")
    if len(raw) < 2 * header:
        raise ValueError("Record is shorter than the plugin's actual read span")
    words = np.frombuffer(raw, dtype="<u2", count=header)
    divisor = int(words[-1])
    if not divisor:
        raise ValueError("Zero normalization divisor: native nonfinite path is not certified")
    if header == 257:
        # S54's writer-specific decoder expects258words, while the actual
        # plugin reads only257. Supply an ignored dummy trailing writer word.
        ratios = np.array(ios_gtc_input_ratios(raw[:514] + b"\0\0"), dtype="f8")
        with np.errstate(over="ignore"):
            values = ratios.astype("f2")
        return GTCTexture(header, ratios, values, "257-header existing S54 ratio + half route")
    nodes = np.array([f32(int(v) / divisor) for v in words[1:]], dtype="f4")
    output = []
    for k in range(256):
        coordinate = f32(f32(float(header-2) * k) / 255.0)
        index = min(max(math.floor(coordinate), 0), header-3)
        a, b = float(nodes[index]), float(nodes[index+1])
        delta = f32(b-a)
        fraction = f32(coordinate - index)
        fused = Fraction(delta) * Fraction(fraction) + Fraction(a)
        output.append(round_nonnegative_fraction_f32(fused))
    with np.errstate(over="ignore"):
        values = np.asarray(output, dtype="f4").astype("f2")
    return GTCTexture(header, nodes, values, "generic-header f64/f32 normalize + f32 resample/FMA + half")
