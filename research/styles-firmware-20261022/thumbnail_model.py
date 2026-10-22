"""Continuous model of cached AIR module 2, lines 109-164.

Inputs are samples AFTER the shader's geometry/GDC/texture sampling. They are
not RAW pixels. This module does not simulate fast half dot/divide, imageblock
storage, sampler precision, capture statistics, or the complete camera.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Literal
import numpy as np
from numpy.typing import NDArray

# Reuse the existing exact-rational set inverse; do not duplicate its solver.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "semantic-styles"))
from semantic_curve_inverse import inverse_curve_pair

FloatArray = NDArray[np.float64]
DOT_WEIGHT = float(np.array([0x34CD], dtype="uint16").view("float16")[0])
DENOM_THRESHOLD = float(np.array([0x1419], dtype="uint16").view("float16")[0])


def rgb(values: NDArray) -> FloatArray:
    out = np.asarray(values, dtype="float64")
    if out.ndim != 2 or out.shape[1] != 3 or len(out) > 65536 or not np.isfinite(out).all():
        raise ValueError("Supply at most 65536 finite RGB triples")
    return out


@dataclass(frozen=True)
class SampleContext:
    post_at_bounds: FloatArray
    pre_resampled: FloatArray
    inside_pre_bounds: NDArray[np.bool_]

    def terms(self, shape: tuple[int, ...]) -> tuple[FloatArray, FloatArray, NDArray[np.bool_]]:
        post, pre = rgb(self.post_at_bounds), rgb(self.pre_resampled)
        inside = np.asarray(self.inside_pre_bounds, dtype=bool)
        if post.shape != shape or pre.shape != shape or inside.shape != shape[:1]:
            raise ValueError("Context shapes must match observation samples")
        denominator = post.sum(axis=-1) * DOT_WEIGHT
        numerator = pre.sum(axis=-1) * DOT_WEIGHT
        scale = np.ones_like(denominator)
        np.divide(numerator, denominator, out=scale, where=denominator > DENOM_THRESHOLD)
        return np.minimum(scale, 1.0), pre, inside


def forward(post_at_output: FloatArray, context: SampleContext) -> FloatArray:
    """Strict interior uses resampled preLTM; exterior caps the ratio at one.

    ``inside_pre_bounds`` must encode both strict coordinate comparisons from
    AIR, not an inclusive rectangle. No extra [0,1] RGB clamp is introduced.
    """
    post = rgb(post_at_output)
    scale, pre, inside = context.terms(post.shape)
    return np.where(inside[:, None], pre, post * scale[:, None])


def conditional_inverse(observed: FloatArray, context: SampleContext,
                        *, prior_lower: float, prior_upper: float) -> dict:
    """Exact-real set inverse in post-at-output, under supplied fixed samples.

    Priors must be explicit. Interior pixels do not observe post-at-output at
    all; a zero exterior multiplier likewise erases it. Report a set there.
    This is a continuous unit result, not a half/native error certificate.
    """
    y = rgb(observed)
    if not np.isfinite([prior_lower, prior_upper]).all() or prior_lower > prior_upper:
        raise ValueError("Supply an ordered finite prior")
    scale, pre, inside = context.terms(y.shape)
    independent = inside | (scale == 0)
    expected = np.where(inside[:, None], pre, 0)
    valid = (~independent) | np.all(y == expected, axis=-1)
    candidate = np.full_like(y, np.nan)
    np.divide(y, scale[:, None], out=candidate, where=(~independent)[:, None])
    valid &= independent | np.all((candidate >= prior_lower) & (candidate <= prior_upper), axis=-1)
    lo = np.where(independent[:, None], prior_lower, candidate)
    hi = np.where(independent[:, None], prior_upper, candidate)
    lo[~valid] = np.nan; hi[~valid] = np.nan; candidate[~valid] = np.nan
    return {"candidate": candidate, "lower": lo, "upper": hi, "valid_mask": valid,
            "unique_in_model_mask": valid & ~independent, "camera_inverse_verified": False,
            "arithmetic": "continuous; native fast-half error not bounded"}


def inverse_supplied_curve(observed: FloatArray, knots: FloatArray, applied: FloatArray,
                           neutral: FloatArray, *, storage: Literal["float16", "float32", "exact"],
                           implementation_error_abs: float) -> dict:
    """Existing S20 conditional curve inverse with an explicit error envelope.

    Call separately per actual GTM/LTM stage and its actual coordinate system.
    This wrapper does not guess stage order or infer a curve from a HEIC tag.
    """
    return inverse_curve_pair(observed, knots, applied, neutral, storage=storage,
                              forward_error_abs=implementation_error_abs)
