"""Piecewise Apple Log inverse.

Constants are the recorded literals. They are not fitted to these samples.
Float64 matches the handoff and the recovered analyze.py literals.
The recovered LivePhotoHDR native.m evaluates the same decimals as float32;
that single-precision path is separate and is not used to change the constants.
Code-range unpacking is not part of the curve.
"""
from __future__ import annotations

import numpy as np

R0 = -0.05641088
RT = 0.01
C = 47.28711236
BETA = 0.00964052
GAMMA = 0.08550479
DELTA = 0.69336945


def toe_threshold() -> float:
    return C * (RT - R0) ** 2


def exponent_inverse(code: np.ndarray) -> np.ndarray:
    return np.exp2((np.asarray(code, dtype=np.float64) - DELTA) / GAMMA) - BETA


def toe_inverse(code: np.ndarray) -> np.ndarray:
    values = np.asarray(code, dtype=np.float64)
    return np.sqrt(np.maximum(values, 0.0) / C) + R0


def piecewise_inverse(code: np.ndarray) -> np.ndarray:
    values = np.asarray(code, dtype=np.float64)
    threshold = toe_threshold()
    return np.where(values >= threshold, exponent_inverse(values), toe_inverse(values))


def piecewise_inverse_float32(code: np.ndarray) -> np.ndarray:
    """Recovered native.m single-precision evaluation. Not a retuned curve."""
    values = np.asarray(code, dtype=np.float32)
    threshold = np.float32(C) * np.float32(RT - R0) ** np.float32(2)
    exponent = np.exp2((values - np.float32(DELTA)) / np.float32(GAMMA)) - np.float32(BETA)
    toe = np.sqrt(np.maximum(values, np.float32(0)) / np.float32(C)) + np.float32(R0)
    return np.where(values >= threshold, exponent, toe).astype(np.float32)


def unpack_code(integer_code: np.ndarray, bit_depth: int, code_range: str) -> np.ndarray:
    """Map stored integers to the curve's code domain.

    full: code / (2**bit_depth - 1). This is the video contract when the
    container says full range (pc). legal is an explicit alternate and is
    never the default for an Apple Log track.
    """
    if bit_depth < 8:
        raise ValueError(f"unsupported bit depth {bit_depth}")
    codes = np.asarray(integer_code, dtype=np.float64)
    full_scale = float((1 << bit_depth) - 1)
    if code_range == "full":
        return codes / full_scale
    if code_range == "legal":
        if bit_depth == 8:
            low, high = 16.0, 235.0
        elif bit_depth == 10:
            low, high = 64.0, 940.0
        else:
            low = 16.0 * (1 << (bit_depth - 8))
            high = 235.0 * (1 << (bit_depth - 8))
        return (codes - low) / (high - low)
    raise ValueError(f"code range must be 'full' or 'legal', got {code_range!r}")
