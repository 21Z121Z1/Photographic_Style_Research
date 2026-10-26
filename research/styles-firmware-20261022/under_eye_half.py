"""Exact half arithmetic candidate for the observed UnderEye final stage.

Weight order comes from the current AIR138 arithmetic records. The two-FMA mix
is a lowering hypothesis that matches the retained finite native observations;
AIR's fast mix does not uniquely prove this lowering for every compiler/input.
Samples are supplied half texel values. No sampler, segmentation or camera order
is implemented. The continuous adapter remains separate.
"""
from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from functools import lru_cache

import numpy as np

from square132_contract import add, sub, mul, fma, rn, value
from texture_style_adapter import HalfRGB, UnderEyeContext, Checkpoint


class HalfArithmetic(Enum):
    RN_GRADUAL_TWO_FMA = 'RN-even, gradual underflow; half weights; fma(-w,X,X), fma(w,E,previous)'


@dataclass(frozen=True)
class UnderEyeHalfResult:
    output: HalfRGB
    weight: np.ndarray
    checkpoints: tuple[Checkpoint, ...]
    model_only: bool = True
    arbitrary_native_inputs_verified: bool = False
    sampler_verified: bool = False
    Apple_order_verified: bool = False


_add=lru_cache(maxsize=8192)(add)
_sub=lru_cache(maxsize=8192)(sub)
_mul=lru_cache(maxsize=8192)(mul)
_fma=lru_cache(maxsize=32768)(fma)


def apply_under_eye_half(source: HalfRGB, context: UnderEyeContext, *, arithmetic: HalfArithmetic) -> UnderEyeHalfResult:
    """Apply a caller-accepted exact arithmetic contract to supplied samples."""
    if type(arithmetic) is not HalfArithmetic or not isinstance(source,HalfRGB) or not isinstance(context,UnderEyeContext):
        raise TypeError('Typed source/context and explicit half arithmetic assumptions required')
    if source.domain != context.edited.domain or source.values.shape != context.edited.values.shape:
        raise ValueError('Source and edited samples must share domain and geometry')
    if np.any(abs(source.values)>2) or np.any(abs(context.edited.values)>2):
        raise ValueError('This arithmetic model declares an RGB sample box [-2,2]')
    masks=context.masks.__dict__
    if any(m is None or m.values.shape != source.values.shape[:2] for m in masks.values()):
        raise ValueError('All eight aligned half mask samples are required; no implicit fallback')
    operands={name:m.values.view('u2') for name,m in masks.items()}
    mix=rn(Fraction(*float(context.parameters.brightness_mix).as_integer_ratio()))
    strength=rn(Fraction(*float(context.parameters.strength).as_integer_ratio()))
    weights=np.empty(source.values.shape[:2],dtype='u2')
    output=np.empty(source.values.shape,dtype='u2')
    x=source.values.view('u2');e=context.edited.values.view('u2')
    for y,z in np.ndindex(weights.shape):
        excluded=int(operands['lips'][y,z])
        for name in ('ears','tattoo','glasses','hair'):
            excluded=_add(excluded,int(operands[name][y,z]))
        w=_mul(_sub(int(operands['face'][y,z]),excluded),int(operands['instance'][y,z]))
        w=0 if value(w)<0 else 0x3c00 if value(w)>1 else w
        for factor in (int(operands['blend'][y,z]),mix,strength):w=_mul(w,factor)
        weights[y,z]=w
        for channel in range(3):
            original=int(x[y,z,channel]);edited=int(e[y,z,channel])
            first=_fma(w ^ 0x8000,original,original)
            output[y,z,channel]=_fma(w,edited,first)
    stored=HalfRGB(output.view('f2'),source.domain)
    weight=weights.view('f2').copy();weight.setflags(write=False)
    checkpoints=(Checkpoint('half_weight',weight,'exact RN binary16','AIR half operation order; supplied samples'),
                 Checkpoint('stored_output',stored.values,'exact RN binary16','two-FMA lowering hypothesis'))
    return UnderEyeHalfResult(stored,weight,checkpoints)
