"""Deterministic synthetic raw contexts for image-chain diagnostics.

These are explicit code3-domain test textures and supplied masks, not camera
frames, segmentation predictions, UI presets, or a calibrated color space.
The matched reference ABI is inherited; raw images and ROI grids are generated.
"""
from dataclasses import dataclass, replace
from enum import Enum
import numpy as np
from complete_fixture import context as abi_context
from complete_forward import Context
from leaf_numeric import V
from pixel_skin import decode as code3_decode


class Pattern(str, Enum):
    GRADIENT = 'gradient'
    EXPOSURE = 'exposure'
    COLORS = 'colors'
    EDGES = 'edges'
    ZERO = 'zero'


class MaskPattern(str, Enum):
    SPATIAL = 'spatial'
    ZERO = 'zero'
    ONE = 'one'


@dataclass(frozen=True)
class SyntheticSpec:
    pattern: Pattern
    height: int = 8
    width: int = 12
    masks: MaskPattern = MaskPattern.SPATIAL

    def __post_init__(self):
        if type(self.pattern) is not Pattern or type(self.masks) is not MaskPattern:
            raise TypeError('Exact synthetic pattern and mask enums required')
        if any(type(n) is not int or not 2 <= n <= 30 for n in (self.height, self.width)):
            raise ValueError('Bounded model tile dimensions 2..30; output adds a one-pixel border')


def rgb_pattern(spec: SyntheticSpec) -> np.ndarray:
    if not isinstance(spec, SyntheticSpec):
        raise TypeError('SyntheticSpec required')
    y, x = np.mgrid[:spec.height, :spec.width]
    u, v = x / (spec.width - 1), y / (spec.height - 1)
    if spec.pattern is Pattern.GRADIENT:
        level = .001 + .96 * u
        rgb = np.stack([level, level * (.63 + .18 * v), level * (.41 + .14 * v)], -1)
    elif spec.pattern is Pattern.EXPOSURE:
        # Stated exposure stops describe this generator, not a camera EV model.
        stops = np.linspace(-8, 2, min(8, spec.width))
        level = .18 * np.exp2(stops[np.minimum(x * len(stops) // spec.width, len(stops) - 1)])
        rgb = np.stack([level, .78 * level, .56 * level], -1)
    elif spec.pattern is Pattern.COLORS:
        colors = np.array([[.92,.13,.06],[.09,.75,.16],[.06,.18,.94],
                           [.86,.65,.08],[.75,.12,.62],[.07,.67,.74],
                           [.025,.018,.012],[.12,.08,.04],[.38,.25,.17],
                           [.74,.55,.39],[.98,.89,.76],[.32,.48,.70]])
        rgb = colors[(y * 3 // spec.height) * 4 + np.minimum(x * 4 // spec.width, 3)]
    elif spec.pattern is Pattern.EDGES:
        left = np.array([.035,.022,.014]); right = np.array([.88,.72,.51])
        rgb = np.where((x < spec.width // 2)[...,None], left, right)
        rgb = np.where((y == spec.height // 2)[...,None], np.array([.13,.38,.76]), rgb)
    else:
        rgb = np.zeros((spec.height, spec.width, 3))
    return np.asarray(rgb, dtype='f2')


def semantic_masks(spec: SyntheticSpec) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    y, x = np.mgrid[:spec.height, :spec.width]
    if spec.masks is MaskPattern.SPATIAL:
        u = (x + .5) / spec.width; v = (y + .5) / spec.height
        person = np.clip(1 - ((u - .5) / .43)**2 - ((v - .52) / .58)**2, 0, 1)
        skin = np.clip(1 - ((u - .5) / .24)**2 - ((v - .28) / .30)**2, 0, 1) * person
        sky = np.clip((.32 - v) / .25, 0, 1) * (1 - person)
    else:
        person = skin = sky = np.full((spec.height, spec.width), int(spec.masks is MaskPattern.ONE))
    return tuple(np.asarray(a[...,None], dtype='f2') for a in (person, skin, sky))


def make_context(spec: SyntheticSpec) -> Context:
    base = abi_context()
    rgb = rgb_pattern(spec)
    alpha = np.ones((*rgb.shape[:2], 1), dtype='f2')
    primary = np.concatenate([rgb, alpha], -1)
    linear_rgb = code3_decode(V.value(rgb)).lo.astype('f2')
    linear = np.concatenate([linear_rgb, alpha], -1).astype('f2')
    level = rgb.astype('f4') @ np.array([.25,.5,.25], dtype='f4')
    guide = np.stack([level, .9*level, .8*level, np.ones_like(level)], -1).astype('f2')
    person, skin, sky = semantic_masks(spec)
    matte = (.15 + .65 * person).astype('f2')
    guide8 = (.07 + .65 * level)[...,None].astype('f2')
    guide9 = (.13 + .55 * level)[...,None].astype('f2')
    roi = base.roi.copy(); h, w = rgb.shape[:2]
    roi.view('u2')[:6] = [w,h,w,h,w+1,h+1]
    for k in range(3,12):
        roi[4*(k-3)+4:4*(k-3)+8] = [1/w,1/h,0,0]
    # Keep both original supplied producer-to-consumer normalized ROI offsets.
    roi[12:16] = [1/w,1/h,-.07,.04]
    roi[16:20] = [1/w,1/h,.08,-.05]
    return replace(base, images=(primary,linear,guide,matte,guide8,guide9,person,skin,sky,base.images[9]),
                   roi=roi, producer_shape=(min(4,h),min(6,w)),
                   output_initial=np.full((h+2,w+2,4),-.75,dtype='f2'))


def describe(spec: SyntheticSpec) -> dict:
    return {'pattern':spec.pattern.value, 'shape':[spec.height,spec.width],
            'masks':spec.masks.value, 'mask_source':'program-generated analytic fields; no person segmentation validation',
            'input_domain':'explicit half code3 ABI test values; transfer enum 3; color primaries unidentified',
            'linear_auxiliary':'synthetic code3_decode(source) from existing generic model; supplied raw auxiliary, not a recovered scene',
            'exposure_generator_stops':[-8,2] if spec.pattern is Pattern.EXPOSURE else None,
            'source_range':[float(rgb_pattern(spec).min()),float(rgb_pattern(spec).max())],
            'camera_or_Apple_reference':False}
