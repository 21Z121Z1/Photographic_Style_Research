"""Explicit YCbCr matrices. These are ITU coefficients, not a captured Core Image basis."""
from __future__ import annotations

import numpy as np

# Rec.2020 non-constant luminance, matching an nclc matrix value of 9.
REC2020_KR = 0.2627
REC2020_KB = 0.0593
# BT.709 matrix, used only when a resource's own colr says so.
BT709_KR = 0.2126
BT709_KB = 0.0722


def ycbcr_to_rgb(y: np.ndarray, cb: np.ndarray, cr: np.ndarray, kr: float, kb: float) -> np.ndarray:
    kg = 1.0 - kr - kb
    red = y + 2.0 * (1.0 - kr) * cr
    blue = y + 2.0 * (1.0 - kb) * cb
    green = (y - kr * red - kb * blue) / kg
    return np.stack([red, green, blue], axis=-1)


def upsample_420(channel: np.ndarray) -> np.ndarray:
    return np.repeat(np.repeat(channel, 2, axis=0), 2, axis=1)


def rgb_from_yuv420p10(raw: np.ndarray, width: int, height: int, frames: int, kr: float, kb: float) -> np.ndarray:
    plane = width * height
    chroma = (width // 2) * (height // 2)
    frame_samples = plane + 2 * chroma
    if raw.size != frames * frame_samples:
        raise ValueError(f"expected {frames * frame_samples} samples, got {raw.size}")
    output = np.empty((frames, height, width, 3), dtype=np.float64)
    for index in range(frames):
        base = index * frame_samples
        y = raw[base:base + plane].reshape(height, width) / 1023.0
        cb = raw[base + plane:base + plane + chroma].reshape(height // 2, width // 2)
        cr = raw[base + plane + chroma:base + frame_samples].reshape(height // 2, width // 2)
        cb = (upsample_420(cb)[:height, :width] - 512.0) / 1023.0
        cr = (upsample_420(cr)[:height, :width] - 512.0) / 1023.0
        output[index] = ycbcr_to_rgb(y, cb, cr, kr, kb)
    return output
