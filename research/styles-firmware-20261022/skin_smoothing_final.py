"""Conditional SkinSmooth final blend with external reconstruction.

Source anchor: research/semantic-styles/REPORT.zh-CN.md, SEM-23,
AIR0151:207-239, at e5d2bcd8db8b3eb6737237ed88167777b3c920ba.
The continuous formula is (1-a)X+(a+b)S-bB. S is the previously saturated
reconstruction and B is the external blur sample. All images share X's named
color domain. Coefficients a/b are caller-supplied derived dimensionless weights,
not sliders, recovered masks, or computed Apple statistics. Their supported
model domain is finite f32, without an inferred native range.

Arithmetic is float64 followed by binary16 storage. Native half ordering,
sampling, upstream reconstruction, and placement in the image chain are unverified.
"""
from dataclasses import dataclass

import numpy as np

from texture_style_adapter import Checkpoint, HalfRGB


@dataclass(frozen=True)
class SkinSmoothingContext:
    smooth: HalfRGB
    blurred: HalfRGB
    a: np.ndarray
    b: np.ndarray

    def __post_init__(self):
        if not isinstance(self.smooth, HalfRGB) or not isinstance(self.blurred, HalfRGB):
            raise TypeError('Explicit HalfRGB reconstruction and blur are required')
        if self.smooth.domain != self.blurred.domain or self.smooth.values.shape != self.blurred.values.shape:
            raise ValueError('Reconstruction and blur must share domain and geometry')
        if np.any((self.smooth.values < 0) | (self.smooth.values > 1)):
            raise ValueError('S must be the externally saturated reconstruction in [0,1]')
        for name in ('a', 'b'):
            value = getattr(self, name)
            if not isinstance(value, np.ndarray) or value.dtype != np.dtype('float32'):
                raise TypeError('Explicit f32 coefficient arrays are required')
            if value.shape != self.smooth.values.shape[:2] or not np.isfinite(value).all():
                raise ValueError('Finite HxW coefficient arrays matching the images are required')
            frozen = value.copy()
            frozen.setflags(write=False)
            object.__setattr__(self, name, frozen)


@dataclass(frozen=True)
class SkinSmoothingResult:
    output: HalfRGB
    checkpoints: tuple[Checkpoint, ...]
    model_only: bool = True
    native_half_or_sampler_verified: bool = False
    upstream_reconstruction_verified: bool = False
    apple_order_verified: bool = False


def apply_skin_smoothing_final(source: HalfRGB, context: SkinSmoothingContext) -> SkinSmoothingResult:
    """Blend a supplied saturated reconstruction and blur with supplied weights."""
    if not isinstance(source, HalfRGB) or not isinstance(context, SkinSmoothingContext):
        raise TypeError('Typed source and SkinSmoothingContext are required')
    if source.domain != context.smooth.domain or source.values.shape != context.smooth.values.shape:
        raise ValueError('Source and context must share domain and geometry')
    x = source.values.astype('f8')
    s = context.smooth.values.astype('f8')
    blurred = context.blurred.values.astype('f8')
    a = context.a.astype('f8')[..., None]
    b = context.b.astype('f8')[..., None]
    continuous = (1-a)*x + (a+b)*s - b*blurred
    continuous = np.where((a == 0) & (b == 0), x, continuous)
    with np.errstate(over='raise', invalid='raise'):
        output = HalfRGB(continuous.astype('f2'), source.domain)
    checkpoints = tuple(Checkpoint(name, values, precision, meaning) for name, values, precision, meaning in (
        ('input', source.values, 'binary16 storage', 'caller-supplied X'),
        ('smooth', context.smooth.values, 'binary16 storage', 'externally saturated S'),
        ('blurred', context.blurred.values, 'binary16 storage', 'external blur sample B'),
        ('a', context.a, 'binary32 storage', 'external derived blend weight a'),
        ('b', context.b, 'binary32 storage', 'external derived texture weight b'),
        ('continuous_output', continuous, 'float64 continuous model', '(1-a)X+(a+b)S-bB'),
        ('stored_output', output.values, 'binary16 storage', 'conditional final blend result'),
    ))
    return SkinSmoothingResult(output, checkpoints)
