"""Scene scaling -> supplied-context Tone blocks -> explicit consumer fields.

An interface composition, not a full camera/pixel pipeline. Does not invent
stats/maps/curves, equate sceneType with tuningType, or turn coefficients to EV.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from negative_tone import ToneStats,NegativeToneContext,coefficients as negative_coefficients
from positive_tone import PositiveToneStats,PositiveToneContext,coefficients as positive_coefficients
from positive_tone_skin import semantic_skin_model
from tone_boundaries import BranchDecision,positive_decisions,negative_decisions

BG_NAMES=('whites','contrast','richSat','shadows','gammaContrast','localContrast','airy','mids','sat','lighten','underGrass','airyGamma','warmthMatchI','warmthMatchQ','warmthMatchSkyI','warmthMatchSkyQ','bgGlobalMix')
FG_NAMES=('personMix','airy','mids','lighten','whites','airyGamma','shadows','contrast','smartContrast','skinHighLights','skinLocalContrast','saturation','faceI','faceQ','underTone','neckShade')
SEM_NAMES=('bgLTM','fgLTM','bgExposureGain','fgExposureGain','GTC','HR','personHR')


@dataclass(frozen=True)
class RendererControls:
    """Supplied renderer values; not UI calibration or EV."""
    intensity: float
    tone: float
    color: float

    def array(self):
        a=np.array([self.intensity,self.tone,self.color],dtype='f4')
        if not np.isfinite(a).all()or not 0<=a[0]<=1 or np.any(abs(a[1:])>1):
            raise ValueError('Declared pre-scale controls: intensity [0,1], tone/color [-1,1]')
        return a


@dataclass(frozen=True)
class ResolvedSceneType:
    """Output of CPU scene resolution; SSRParams byte32, not tuningType652."""
    code: int

    def __post_init__(self):
        if type(self.code)is not int or not 0<=self.code<=0xffffffff:raise ValueError('Resolved sceneType must be uint32')


@dataclass(frozen=True)
class ScaledControls:
    intensity: np.float32
    tone: np.float32
    color: np.float32
    scene_type: ResolvedSceneType


def scale_controls(controls: RendererControls,scene: ResolvedSceneType,tone_tuning: tuple[float,...]) -> ScaledControls:
    values=controls.array();tun=np.array(tone_tuning,dtype='f4')
    if tun.shape!=(66,)or not np.isfinite(tun).all()or np.max(abs(tun))>16:raise ValueError('66 supplied bounded tuning values required')
    # Original 0x1d42f2328..2368: code3 uses byte198/19c/1a0,
    # code21 uses byte1a4/1a8/1ac. No clamp is present in this block.
    first={3:59,21:62}.get(scene.code)
    if first is not None:
        factors=tun[[first+2,first,first+1]]  # intensity, tone, color
        values=np.multiply(values,factors,dtype=np.float32)
    return ScaledControls(*values,scene)


@dataclass(frozen=True)
class SuppliedToneStats:
    negative_fields: ToneStats
    slot0_field6: float
    slot6_field5: float

    def positive_fields(self):
        return PositiveToneStats(self.slot0_field6,self.negative_fields.slot5_field6,self.slot6_field5)


@dataclass(frozen=True)
class ToneFrameContext:
    stats: SuppliedToneStats
    tone_tuning: tuple[float,...]
    tuning_type: int=0
    cast_code: int=0
    scene_brightness: float=0.
    baseline_exposure_field7: float=1.
    people_threshold_low: float=0.
    people_threshold_high: float=1.
    face_exposure_boost_ratio: float=1.

    def common(self):
        if any(type(x)is not int or not 0<=x<=255 for x in (self.tuning_type,self.cast_code)):
            raise ValueError('Distinct explicit tuningType/cast integer codes required')


@dataclass(frozen=True)
class ConsumerFields:
    controls: ScaledControls
    branch: str
    values: np.ndarray
    host_f32_absolute_allowance: np.ndarray
    pixel_pipeline_verified: bool=False
    branch_decisions: tuple[BranchDecision,...]=()

    def __post_init__(self):
        for name in ('values','host_f32_absolute_allowance'):
            a=np.array(getattr(self,name),dtype='f8',copy=True)
            if a.shape!=(40,)or not np.isfinite(a).all():raise ValueError('40 finite coefficients/allowances required')
            a.flags.writeable=False;object.__setattr__(self,name,a)

    @property
    def branch_determined(self):return all(b.state!='undetermined'for b in self.branch_decisions)

    @property
    def value_contract(self):
        return 'coefficient_center_with_error_allowance'if self.branch_determined else 'set_coverage_only'

    @property
    def output_lower(self):return self.values-self.host_f32_absolute_allowance

    @property
    def output_upper(self):return self.values+self.host_f32_absolute_allowance

    def named_fields(self):
        result={};i=0
        for block,names,offset in [('bg',BG_NAMES,488),('fg',FG_NAMES,556),('semantic',SEM_NAMES,620)]:
            for field,name in enumerate(names):
                result[f'{block}.{name}']={'field':field,'byte_offset':offset+field*4,'approximate_center':float(self.values[i]),
                                         'lower':float(self.output_lower[i]),'upper':float(self.output_upper[i]),
                                         'branch_determined':all(b.state!='undetermined'for b in self.branch_decisions if i in b.affected_flat_fields)};i+=1
        return result

    def ssr_block_f32(self,*,allow_approximation=False):
        """160B approximation at byte488; all remaining SSRParams are external."""
        if not self.branch_determined and not allow_approximation:
            raise ValueError('Undetermined branch: carry output sets or explicitly request a non-native approximation')
        return self.values.astype('<f4').tobytes()

    def skin_only_forward(self,rgb,skin_weight,guide,*,allow_approximation=False):
        """Only the existing two-field continuous skin consumer; other ops omitted."""
        if not self.branch_determined and not allow_approximation:
            raise ValueError('Undetermined coefficient branch; center rendering needs explicit approximation consent')
        return semantic_skin_model.forward(rgb,skin_weight,guide,float(self.values[26]),float(self.values[27]))


def evaluate(controls: RendererControls,scene: ResolvedSceneType,frame: ToneFrameContext) -> ConsumerFields:
    frame.common();scaled=scale_controls(controls,scene,frame.tone_tuning)
    if scaled.tone>=0:
        c=PositiveToneContext(frame.stats.positive_fields(),frame.tone_tuning,frame.tuning_type,frame.cast_code,frame.scene_brightness,frame.baseline_exposure_field7)
        result=positive_coefficients(float(scaled.tone),c);branch='positive_or_zero'
    else:
        c=NegativeToneContext(frame.stats.negative_fields,frame.tone_tuning,frame.tuning_type,frame.cast_code,frame.scene_brightness,frame.people_threshold_low,frame.people_threshold_high,frame.face_exposure_boost_ratio,frame.baseline_exposure_field7)
        result=negative_coefficients(float(scaled.tone),c);branch='negative'
    # Scaled tone outside either declared model domain is rejected by the model,
    # not silently clipped into a different equation or replaced with identity.
    decisions=positive_decisions(float(scaled.tone))if branch=='positive_or_zero'else negative_decisions(c)
    return ConsumerFields(scaled,branch,result.values(),result.host_f32_absolute_allowance,branch_decisions=decisions)
