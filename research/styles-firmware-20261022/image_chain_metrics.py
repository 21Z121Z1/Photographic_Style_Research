"""Finite aligned diagnostic differences, never an Apple accuracy certificate."""
from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class Comparison:
    max_absolute_error: float
    rmse: float
    mean_absolute_error: float
    components: int
    pixels: int
    half_bit_mismatches: int
    absolute_error_percentiles: dict
    histogram: tuple
    exceedance_components: int
    exceedance_examples: tuple

    def record(self):
        from dataclasses import asdict
        return asdict(self)


def compare_rgb(actual, reference, *, pixel_mask=None, threshold=1e-3) -> Comparison:
    """Compare RGB only on supplied common written pixels, reject nonfinite data.

    Arrays must use real integer or floating storage and already share shape
    and coordinate domain. This function does
    not align/resize/expose images or invent a mask for unavailable pixels.
    """
    a = np.asarray(actual); b = np.asarray(reference)
    if a.dtype.kind not in 'iuf' or b.dtype.kind not in 'iuf':
        raise TypeError('Real integer or floating RGB/RGBA storage required')
    if a.shape != b.shape or a.ndim != 3 or a.shape[-1] not in (3,4):
        raise TypeError('Identical aligned HxWxRGB/RGBA shapes required')
    if not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError('Nonfinite values remain unknown, never counted as matching')
    if not np.isfinite(threshold) or threshold < 0:
        raise ValueError('Finite nonnegative diagnostic threshold required')
    mask = np.ones(a.shape[:2], dtype=bool) if pixel_mask is None else np.asarray(pixel_mask)
    if mask.dtype != np.dtype(bool) or mask.shape != a.shape[:2] or not mask.any():
        raise TypeError('Nonempty exact boolean common-written pixel mask required')
    a = a[...,:3]; b = b[...,:3]
    if np.any(np.abs(a.astype('f8')) > 65504) or np.any(np.abs(b.astype('f8')) > 65504):
        raise ValueError('RGB exceeds finite half storage; half-bit comparison unavailable')
    error = np.abs(a.astype('f8') - b.astype('f8')); samples = error[mask]
    thresholds = [0,1e-6,1e-4,1e-3,.01,.1]
    bins = [{'lower_inclusive':float(lo),
             'upper_exclusive':float(hi) if np.isfinite(hi) else None,
             'count':int(np.count_nonzero((samples >= lo) & (samples < hi)))}
            for lo,hi in zip(thresholds,thresholds[1:]+[np.inf])]
    exceeding = (error > threshold) & mask[...,None]
    coordinates = np.argwhere(exceeding)
    examples = tuple({'y':int(y),'x':int(x),'channel':int(c),
                      'actual':float(a[y,x,c]),'reference':float(b[y,x,c]),
                      'absolute_error':float(error[y,x,c])}
                     for y,x,c in coordinates[:16])
    return Comparison(float(samples.max()),float(np.sqrt(np.mean(np.square(samples)))),
                      float(samples.mean()),int(samples.size),int(mask.sum()),
                      int(np.count_nonzero(a.astype('f2').view('u2')[mask] != b.astype('f2').view('u2')[mask])),
                      {str(p):float(np.percentile(samples,p)) for p in (0,50,90,95,99,100)},
                      tuple(bins),int(coordinates.shape[0]),examples)
