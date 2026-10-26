"""Typed, conditional Texture final-stage adapter using the existing UnderEye model.

This module declares its arithmetic and storage separately: the reused continuous
formula runs in float64, then the RGB output is stored as NumPy float16. This is
not an implementation of Apple's half operations or sampler. Color domain and
effect order are caller-supplied contracts, not recovered camera properties.
SkinSmooth final blending requires external reconstruction, blur, and weights.
The explicit final-blend effect does not implement complete SkinSmooth/Mattify.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from enum import Enum
import hashlib
import importlib.util
from pathlib import Path

import numpy as np


if TYPE_CHECKING:
    from skin_smoothing_final import SkinSmoothingContext
    from under_eye_half import HalfArithmetic


_HELPER = Path(__file__).resolve().parents[1] / 'semantic-styles/studio_under_eye.py'
_SPEC = importlib.util.spec_from_file_location('_psr_existing_under_eye', _HELPER)
_MODEL = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODEL)
HELPER_SHA256 = hashlib.sha256(_HELPER.read_bytes()).hexdigest()
REFERENCE_COMMIT = 'e5d2bcd8db8b3eb6737237ed88167777b3c920ba'


class TransferDomain(Enum):
    LINEAR = 'linear'
    NONLINEAR = 'nonlinear; transfer explicitly named'


@dataclass(frozen=True)
class ColorDomain:
    primaries: str
    transfer: TransferDomain
    transfer_name: str
    reference: str

    def __post_init__(self):
        if type(self.transfer) is not TransferDomain:
            raise TypeError('An explicit transfer-domain enum is required')
        if any(type(v) is not str or not v.strip() for v in
               (self.primaries, self.transfer_name, self.reference)):
            raise TypeError('Named primaries, transfer and reference domain are required')
        if self.transfer is TransferDomain.LINEAR and self.transfer_name != 'identity':
            raise ValueError('Linear storage must declare the identity transfer')


def _frozen(values, dtype, ndim):
    if not isinstance(values, np.ndarray) or values.dtype != np.dtype(dtype):
        raise TypeError(f'Explicit {dtype} ndarray storage is required; no implicit conversion')
    if values.ndim != ndim or not values.size or not np.isfinite(values).all():
        raise ValueError('Nonempty finite storage with the declared rank is required')
    result = values.copy()
    result.setflags(write=False)
    return result


@dataclass(frozen=True)
class HalfRGB:
    values: np.ndarray
    domain: ColorDomain

    def __post_init__(self):
        if not isinstance(self.domain, ColorDomain):
            raise TypeError('An explicit color domain is required')
        a = _frozen(self.values, 'float16', 3)
        if a.shape[-1] != 3:
            raise ValueError('RGB HxWx3 storage is required; alpha must be handled by the caller')
        object.__setattr__(self, 'values', a)


@dataclass(frozen=True)
class HalfMask:
    values: np.ndarray
    provenance: str

    def __post_init__(self):
        a = _frozen(self.values, 'float16', 2)
        if np.any((a < 0) | (a > 1)):
            raise ValueError('Mask probabilities must be within [0,1]')
        if type(self.provenance) is not str or not self.provenance.strip():
            raise TypeError('Mask provenance is required; synthetic masks are not segmentation evidence')
        object.__setattr__(self, 'values', a)


class MissingMaskPolicy(Enum):
    ERROR = 'reject missing mask'
    IDENTITY = 'explicit identity fallback for any missing mask'


@dataclass(frozen=True)
class UnderEyeMasks:
    face: HalfMask | None
    instance: HalfMask | None
    hair: HalfMask | None
    lips: HalfMask | None
    ears: HalfMask | None
    tattoo: HalfMask | None
    glasses: HalfMask | None
    blend: HalfMask | None

    def __post_init__(self):
        if any(v is not None and not isinstance(v, HalfMask) for v in self.__dict__.values()):
            raise TypeError('Every mask must be HalfMask or explicitly missing')


@dataclass(frozen=True)
class UnderEyeParameters:
    brightness_mix: np.float32
    strength: np.float32

    def __post_init__(self):
        for v in (self.brightness_mix, self.strength):
            if type(v) is not np.float32:
                raise TypeError('Explicit f32 scalar parameters are required')
            if not np.isfinite(v) or not 0 <= v <= 1:
                raise ValueError('This conditional adapter supports finite parameters in [0,1]')


@dataclass(frozen=True)
class UnderEyeContext:
    edited: HalfRGB
    masks: UnderEyeMasks
    parameters: UnderEyeParameters
    missing_mask_policy: MissingMaskPolicy = MissingMaskPolicy.ERROR

    def __post_init__(self):
        if not isinstance(self.edited, HalfRGB) or not isinstance(self.masks, UnderEyeMasks):
            raise TypeError('Explicit edited image and typed masks are required')
        if not isinstance(self.parameters, UnderEyeParameters) or type(self.missing_mask_policy) is not MissingMaskPolicy:
            raise TypeError('Typed parameters and an exact missing-mask policy are required')


@dataclass(frozen=True)
class Checkpoint:
    name: str
    values: np.ndarray
    precision: str
    meaning: str

    def __post_init__(self):
        a = np.array(self.values, copy=True)
        a.setflags(write=False)
        object.__setattr__(self, 'values', a)


@dataclass(frozen=True)
class UnderEyeResult:
    output: HalfRGB
    checkpoints: tuple[Checkpoint, ...]
    missing_masks: tuple[str, ...]
    identity_fallback: bool
    model_only: bool = True
    native_half_or_sampler_verified: bool = False
    real_segmentation_verified: bool = False


def apply_under_eye(source: HalfRGB, context: UnderEyeContext) -> UnderEyeResult:
    """Apply the reused FinalMix model to explicit current input, with no native oracle."""
    if not isinstance(source, HalfRGB) or not isinstance(context, UnderEyeContext):
        raise TypeError('Typed source and UnderEye context are required')
    if source.domain != context.edited.domain or source.values.shape != context.edited.values.shape:
        raise ValueError('Source and edited image must share domain and geometry')
    masks = context.masks.__dict__
    missing = tuple(name for name, value in masks.items() if value is None)
    if missing and context.missing_mask_policy is MissingMaskPolicy.ERROR:
        raise ValueError('Missing UnderEye masks: ' + ', '.join(missing))
    if any(m.values.shape != source.values.shape[:2] for m in masks.values() if m is not None):
        raise ValueError('Every present mask must share source geometry')
    checkpoints = [Checkpoint('input', source.values, 'binary16 storage', 'caller-supplied RGB')]
    if missing:
        output = source
    else:
        # Convert explicitly so NumPy promotion cannot silently choose half arithmetic.
        operands = {name: m.values.astype('f8') for name, m in masks.items()}
        p = context.parameters
        weight = _MODEL.weight(**operands, brightness_mix=float(p.brightness_mix), strength=float(p.strength))
        continuous = _MODEL.forward(source.values.astype('f8'), context.edited.values.astype('f8'), weight)
        with np.errstate(over='raise', invalid='raise'):
            stored = continuous.astype('f2')
        output = HalfRGB(stored, source.domain)
        checkpoints += [Checkpoint('weight', weight, 'float64 continuous model', 'dimensionless [0,1] FinalMix weight'),
                        Checkpoint('continuous_output', continuous, 'float64 continuous model', 'before storage conversion')]
    checkpoints.append(Checkpoint('stored_output', output.values, 'binary16 storage', 'conditional model result'))
    return UnderEyeResult(output, tuple(checkpoints), missing, bool(missing))


class TextureEffect(Enum):
    UNDER_EYE = 'UnderEyeBrightening'
    SKIN_SMOOTH = 'SkinSmoothingStandalone'
    SKIN_SMOOTH_FINAL = 'SkinSmoothingFinalBlendOnly'
    MATTIFY = 'Mattify'


@dataclass(frozen=True)
class TextureRun:
    output: HalfRGB | None
    completed_effects: tuple[TextureEffect, ...]
    checkpoints: tuple[Checkpoint, ...]
    gaps: tuple[str, ...]
    model_only: bool = True
    apple_order_verified: bool = False
    full_texture_pipeline_verified: bool = False


def run_conditional_texture(source: HalfRGB, *, effects: tuple[TextureEffect, ...],
                            under_eye: UnderEyeContext | None = None,
                            skin_smooth_final: SkinSmoothingContext | None = None,
                            under_eye_arithmetic: HalfArithmetic | None = None) -> TextureRun:
    """Execute only implemented effects in an explicitly requested experimental order.

    An unavailable stage returns no final output, preserving preceding checkpoints.
    No camera order or position relative to GTM/LTM is asserted by this interface.
    SKIN_SMOOTH_FINAL consumes external operands without reconstructing statistics.
    SKIN_SMOOTH still denotes the unavailable complete effect.
    """
    if not isinstance(source, HalfRGB) or type(effects) is not tuple or any(type(e) is not TextureEffect for e in effects):
        raise TypeError('Typed source and explicit tuple of effect enums are required')
    completed = []
    checkpoints = []
    gaps = []
    current = source
    for index, effect in enumerate(effects):
        if effect is TextureEffect.SKIN_SMOOTH_FINAL:
            from skin_smoothing_final import apply_skin_smoothing_final
            if skin_smooth_final is None:
                return TextureRun(None, tuple(completed), tuple(checkpoints), tuple(gaps) +
                                  ('SkinSmooth final blend: external reconstruction/blur/weights missing',))
            result = apply_skin_smoothing_final(current, skin_smooth_final)
            completed.append(effect)
            checkpoints.extend(Checkpoint(f'{index}.{effect.value}.{cp.name}', cp.values,
                                          cp.precision, cp.meaning) for cp in result.checkpoints)
            current = result.output
            continue
        if effect is not TextureEffect.UNDER_EYE:
            return TextureRun(None, tuple(completed), tuple(checkpoints), tuple(gaps) +
                              (effect.value + ': independent backend unavailable; use existing native unit harness',))
        if under_eye is None:
            return TextureRun(None, tuple(completed), tuple(checkpoints), tuple(gaps) + ('UnderEye: explicit edited/mask context missing',))
        if under_eye_arithmetic is not None:
            from under_eye_half import apply_under_eye_half
            result = apply_under_eye_half(current, under_eye, arithmetic=under_eye_arithmetic)
            completed.append(effect)
        else:
            result = apply_under_eye(current, under_eye)
            if result.identity_fallback:
                gaps.append('UnderEye: explicit identity fallback; missing masks=' + ','.join(result.missing_masks))
            else:
                completed.append(effect)
        checkpoints.extend(result.checkpoints)
        current = result.output
    return TextureRun(current, tuple(completed), tuple(checkpoints), tuple(gaps))
