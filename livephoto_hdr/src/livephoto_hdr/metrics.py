"""Spatial-follow measurements on log-luma structure.

The three ROI windows are the ones used in S11 raw L945 on a 384×288 grid.
They are not refitted to IMG_8148.
"""
from __future__ import annotations

import numpy as np

REC2020_Y = np.array([0.2627, 0.6780, 0.0593], dtype=np.float64)
HISTORICAL_ROIS = ((10, 190, 40, 280), (20, 165, 70, 240), (10, 190, 20, 300))


def gaussian(image: np.ndarray, sigma: float) -> np.ndarray:
    radius = max(1, int(round(3 * sigma)))
    axis = np.arange(-radius, radius + 1, dtype=np.float64)
    kernel = np.exp(-0.5 * (axis / sigma) ** 2)
    kernel /= kernel.sum()
    padded = np.pad(image, radius, mode="edge")
    horizontal = np.apply_along_axis(lambda row: np.convolve(row, kernel, mode="valid"), 1, padded)
    return np.apply_along_axis(lambda row: np.convolve(row, kernel, mode="valid"), 0, horizontal)


def structure(log_luma: np.ndarray) -> np.ndarray:
    band = gaussian(log_luma, 1) - gaussian(log_luma, 6)
    scale = np.sqrt(np.maximum(gaussian(band * band, 6), 0))
    return band / np.maximum(scale, 0.03)


def translation(earlier: np.ndarray, later: np.ndarray) -> dict:
    """Shift, in pixels, that moves `earlier` onto `later`.

    Positive dx means the later image is translated to the right.
    """
    earlier = np.nan_to_num(earlier - np.nanmean(earlier))
    later = np.nan_to_num(later - np.nanmean(later))
    window = np.hanning(earlier.shape[0])[:, None] * np.hanning(earlier.shape[1])[None, :]
    corr = np.fft.ifft2(np.fft.fft2(later * window) * np.conj(np.fft.fft2(earlier * window))).real
    peak = np.unravel_index(int(np.argmax(corr)), corr.shape)
    refined = []
    for axis, position in enumerate(peak):
        size = corr.shape[axis]
        base = int(position if position <= size // 2 else position - size)
        samples = [corr[tuple((position + offset) % size if i == axis else peak[i] for i in range(2))] for offset in (-1, 0, 1)]
        denominator = samples[0] - 2 * samples[1] + samples[2]
        delta = 0.0 if denominator == 0 else 0.5 * (samples[0] - samples[2]) / denominator
        refined.append(base + float(np.clip(delta, -0.5, 0.5)))
    return {"dy": refined[0], "dx": refined[1], "peak": float(corr[peak])}


def log_luma_from_log_rgb(log_rgb: np.ndarray) -> np.ndarray:
    linear = np.exp2(log_rgb)
    return np.log2(np.maximum(linear @ REC2020_Y, 1e-8))


def mae_ev(prediction_log_rgb: np.ndarray, target_log_rgb: np.ndarray) -> dict:
    pred = log_luma_from_log_rgb(prediction_log_rgb)
    target = log_luma_from_log_rgb(target_log_rgb)
    height, width = target.shape
    yy, xx = np.mgrid[:height, :width]
    mask = (yy >= 4) & (yy < height - 4) & (xx >= 4) & (xx < width - 4) & np.isfinite(pred) & np.isfinite(target)
    error = (pred - target)[mask]
    return {
        "pixels": int(mask.sum()),
        "maeEV": float(np.mean(np.abs(error))),
        "medianEV": float(np.median(np.abs(error))),
        "p90EV": float(np.percentile(np.abs(error), 90)),
        "signedMedianEV": float(np.median(error)),
    }


def upsample_bilinear(image: np.ndarray, height: int, width: int) -> np.ndarray:
    src_h, src_w = image.shape
    y = (np.arange(height) + 0.5) * src_h / height - 0.5
    x = (np.arange(width) + 0.5) * src_w / width - 0.5
    y0 = np.clip(np.floor(y).astype(int), 0, src_h - 1)
    x0 = np.clip(np.floor(x).astype(int), 0, src_w - 1)
    y1 = np.clip(y0 + 1, 0, src_h - 1)
    x1 = np.clip(x0 + 1, 0, src_w - 1)
    wy = (y - y0)[:, None]
    wx = (x - x0)[None, :]
    top = image[y0][:, x0] * (1 - wx) + image[y0][:, x1] * wx
    bottom = image[y1][:, x0] * (1 - wx) + image[y1][:, x1] * wx
    return top * (1 - wy) + bottom * wy
