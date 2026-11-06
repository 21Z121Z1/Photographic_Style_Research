"""Dense integer flow and the recovered forward-backward confidence.

This is our block-refined search, not Apple Vision. The confidence formula
and the 0.05 gate are the recovered fit.py / temporal.py constants.
1.5 pixels was defined on a 384-wide grid, so the scale used here is
1.5 * (flow_width / 384). That is a unit conversion, not a fitted threshold.
"""
from __future__ import annotations

import numpy as np

FB_PIXELS_AT_WIDTH_384 = 1.5
LOW_CONFIDENCE = 0.05
TAIL_CONFIDENCE = 0.25


def sample_offset(image: np.ndarray, dy: int, dx: int) -> np.ndarray:
    height, width = image.shape
    out = np.full_like(image, np.nan, dtype=np.float64)
    y0 = max(0, -dy)
    y1 = min(height, height - dy)
    x0 = max(0, -dx)
    x1 = min(width, width - dx)
    if y1 <= y0 or x1 <= x0:
        return out
    out[y0:y1, x0:x1] = image[y0 + dy:y1 + dy, x0 + dx:x1 + dx]
    return out


def _box_mean(values: np.ndarray, radius: int) -> np.ndarray:
    if radius <= 0:
        return values
    padded = np.pad(values, radius, mode="edge")
    integral = np.pad(padded, ((1, 0), (1, 0)), mode="constant").cumsum(0).cumsum(1)
    size = 2 * radius + 1
    total = (integral[size:, size:] - integral[:-size, size:] - integral[size:, :-size] + integral[:-size, :-size])
    return total / (size * size)


def integer_flow(src: np.ndarray, dst: np.ndarray, radius: int, prior: np.ndarray | None = None, window: int = 2) -> np.ndarray:
    """Flow at src pixels pointing into dst. Shape (h, w, 2) as dx, dy."""
    height, width = src.shape
    best = np.full((height, width), np.inf)
    flow = np.zeros((height, width, 2), dtype=np.float32)
    if prior is None:
        offsets = [(dy, dx) for dy in range(-radius, radius + 1) for dx in range(-radius, radius + 1)]
        for dy, dx in offsets:
            error = np.nan_to_num(src - sample_offset(dst, dy, dx), nan=1.0) ** 2
            score = _box_mean(error, window)
            better = score < best - 1e-12
            tie = np.abs(score - best) <= 1e-12
            smaller = (dx * dx + dy * dy) < (flow[..., 0] ** 2 + flow[..., 1] ** 2)
            replace = better | (tie & smaller)
            best[replace] = score[replace]
            flow[replace, 0] = dx
            flow[replace, 1] = dy
        return flow
    yy, xx = np.mgrid[:height, :width]
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            y_index = np.clip(np.rint(yy + prior[..., 1] + dy), 0, height - 1).astype(int)
            x_index = np.clip(np.rint(xx + prior[..., 0] + dx), 0, width - 1).astype(int)
            error = (src - dst[y_index, x_index]) ** 2
            score = _box_mean(error, window)
            candidate_x = prior[..., 0] + dx
            candidate_y = prior[..., 1] + dy
            better = score < best - 1e-12
            tie = np.abs(score - best) <= 1e-12
            smaller = (candidate_x ** 2 + candidate_y ** 2) < (flow[..., 0] ** 2 + flow[..., 1] ** 2)
            replace = better | (tie & smaller)
            best[replace] = score[replace]
            flow[replace, 0] = candidate_x[replace]
            flow[replace, 1] = candidate_y[replace]
    return flow


def _repeat(image: np.ndarray, factor: int) -> np.ndarray:
    return np.repeat(np.repeat(image, factor, axis=0), factor, axis=1)


def scene_flow(src: np.ndarray, dst: np.ndarray) -> np.ndarray:
    """Coarse-to-fine flow on a thumbnail-sized luma pair."""
    coarse_src = src[::4, ::4]
    coarse_dst = dst[::4, ::4]
    coarse = integer_flow(coarse_src, coarse_dst, radius=8, window=1)
    prior = np.stack([_repeat(coarse[..., 0], 4)[:src.shape[0], :src.shape[1]] * 4,
                      _repeat(coarse[..., 1], 4)[:src.shape[0], :src.shape[1]] * 4], axis=-1)
    return integer_flow(src, dst, radius=3, prior=prior, window=1)


def warp(image: np.ndarray, flow: np.ndarray) -> np.ndarray:
    """Sample image at x+flow. image is HxWxC or HxW."""
    height, width = flow.shape[:2]
    yy, xx = np.mgrid[:height, :width]
    y_index = yy + flow[..., 1]
    x_index = xx + flow[..., 0]
    y0 = np.floor(y_index).astype(int)
    x0 = np.floor(x_index).astype(int)
    wy = y_index - y0
    wx = x_index - x0

    def take(y_index, x_index):
        valid = (y_index >= 0) & (y_index < height) & (x_index >= 0) & (x_index < width)
        safe_y = np.clip(y_index, 0, height - 1)
        safe_x = np.clip(x_index, 0, width - 1)
        if image.ndim == 2:
            sampled = image[safe_y, safe_x]
            return np.where(valid, sampled, np.nan)
        sampled = image[safe_y, safe_x]
        return np.where(valid[..., None], sampled, np.nan)

    top = take(y0, x0) * (1 - wx)[..., None] + take(y0, x0 + 1) * wx[..., None] if image.ndim == 3 else take(y0, x0) * (1 - wx) + take(y0, x0 + 1) * wx
    bottom = take(y0 + 1, x0) * (1 - wx)[..., None] + take(y0 + 1, x0 + 1) * wx[..., None] if image.ndim == 3 else take(y0 + 1, x0) * (1 - wx) + take(y0 + 1, x0 + 1) * wx
    if image.ndim == 3:
        return top * (1 - wy)[..., None] + bottom * wy[..., None]
    return top * (1 - wy) + bottom * wy


def forward_backward_confidence(forward: np.ndarray, backward: np.ndarray) -> np.ndarray:
    height, width = forward.shape[:2]
    scale = FB_PIXELS_AT_WIDTH_384 * (width / 384.0)
    sampled = warp(backward, forward)
    error = np.linalg.norm(forward + sampled, axis=2)
    yy, xx = np.mgrid[:height, :width]
    inside = ((xx + forward[..., 0] >= 2) & (xx + forward[..., 0] < width - 2) &
              (yy + forward[..., 1] >= 2) & (yy + forward[..., 1] < height - 2))
    finite = np.isfinite(error)
    return np.where(finite, inside * np.exp(-0.5 * (error / scale) ** 2), 0.0)


def time_confidence(policy: str, long_gap: bool, median_interval: float, gap: float) -> float:
    factor = TAIL_CONFIDENCE if policy.startswith("one_sided") else 1.0
    if long_gap and gap > 0:
        factor *= min(1.0, median_interval / gap)
    return float(factor)
