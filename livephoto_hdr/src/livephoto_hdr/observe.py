"""Motion-compensated scene-observation interpolation.

Controls are fixed before looking at IMG_8148 scores:
hold_nearest, fixed_log, motion_gated, motion_ungated.
No RGB frame blending is used to hide a low-confidence pixel; those pixels
fall back to the fixed log blend and stay in the score.
"""
from __future__ import annotations

import numpy as np

from .motion import LOW_CONFIDENCE, forward_backward_confidence, scene_flow, time_confidence, warp


def blend(left: np.ndarray, right: np.ndarray, alpha: float, left_confidence: np.ndarray, right_confidence: np.ndarray, mode: str) -> tuple[np.ndarray, np.ndarray]:
    if mode == "hold_nearest":
        chosen = left if alpha < 0.5 else right
        return chosen, np.ones(left.shape[:2], dtype=np.float64)
    fixed = (1.0 - alpha) * left + alpha * right
    if mode == "fixed_log":
        return fixed, np.ones(left.shape[:2], dtype=np.float64)
    if mode == "motion_ungated":
        return fixed, np.ones(left.shape[:2], dtype=np.float64)
    if mode != "motion_gated":
        raise ValueError(mode)
    denominator = (1.0 - alpha) * left_confidence + alpha * right_confidence
    mixed = ((1.0 - alpha) * left_confidence[..., None] * left + alpha * right_confidence[..., None] * right) / np.maximum(denominator[..., None], 1e-5)
    gated = np.where((denominator > LOW_CONFIDENCE)[..., None], mixed, fixed)
    return gated, denominator


def compensate(left: np.ndarray, right: np.ndarray, left_luma: np.ndarray, right_luma: np.ndarray, current_luma: np.ndarray, alpha: float, mode: str, policy: str, long_gap: bool, median_interval: float, gap: float) -> tuple[np.ndarray, dict]:
    """Warp endpoint observations into the current frame, then blend.

    left/right are log-domain images. Luma arrays are the main-frame luma at
    the endpoint and current presentation times, already at the observation grid.
    """
    factor = time_confidence(policy, long_gap, median_interval, gap)
    if mode in {"hold_nearest", "fixed_log"}:
        image, weight = blend(left, right, alpha, np.ones(left.shape[:2]), np.ones(left.shape[:2]), mode)
        return image, {"timeConfidence": factor, "lowConfidenceFraction": 0.0, "meanFlowConfidence": 1.0}
    forward_left = scene_flow(current_luma, left_luma)
    backward_left = scene_flow(left_luma, current_luma)
    forward_right = scene_flow(current_luma, right_luma)
    backward_right = scene_flow(right_luma, current_luma)
    confidence_left = forward_backward_confidence(forward_left, backward_left) * factor
    confidence_right = forward_backward_confidence(forward_right, backward_right) * factor
    warped_left = warp(left, forward_left)
    warped_right = warp(right, forward_right)
    if mode == "motion_ungated":
        image, weight = blend(warped_left, warped_right, alpha, np.ones(left.shape[:2]), np.ones(left.shape[:2]), mode)
    else:
        image, weight = blend(warped_left, warped_right, alpha, confidence_left, confidence_right, mode)
    return image, {
        "timeConfidence": factor,
        "lowConfidenceFraction": float(np.mean(weight <= LOW_CONFIDENCE)),
        "meanFlowConfidence": float(np.mean(np.maximum(confidence_left, confidence_right))),
    }
