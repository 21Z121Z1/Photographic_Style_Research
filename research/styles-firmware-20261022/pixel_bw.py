"""Actual AIR10 BW477 root, with separate SSRParams0 and resolved cast245.

Curve and f32 fields are explicit. A BW output is computed, not accepted from
an external oracle. Internal stark and tonal unknowns remain separately visible.
"""
from dataclasses import dataclass
import numpy as np
from leaf_numeric import V,hc,fc,mix,select,DomainUnknown
from pixel_leaves import H,F,dot,root_components,whites_curve
from outer_cast import tonal_core


@dataclass(frozen=True)
class Parameters:
    parameter2: V
    tone20: V
    tone65: V
    cast_type0: int
    tuning_type17: int

    def __post_init__(self):
        values=[self.parameter2,self.tone20,self.tone65]
        if any(not isinstance(v,V)or v.precision!='f'or np.shape(v.lo)!=()for v in values)or any(v.point!=values[0].point for v in values):raise TypeError('Three matching scalar f32 SSRParams fields required')
        if any(type(x)is not int or not 0<=x<=0xffffffff for x in [self.cast_type0,self.tuning_type17]):raise TypeError('Exact uint32 SSRParams0/17 codes required; not resolved245 or UI names')


def stark(rgb,guide,person,parameter2,tone20,whites):
    amount=select(parameter2.gt(0),(parameter2.f()*F(fc('3FD99999A0000000'),rgb)).h(),-parameter2)*tone20
    corrected=whites_curve(rgb,amount,whites,H(1,rgb));c=corrected.clamp()
    s=dot(c,[hc('3555')]*3).sqrt();shape=((1-s.f())*s.f()).h();root=c.sqrt();guide_root=guide.sqrt()
    r,g,b=root_components(root,shape)
    colored=((((-guide_root)*shape+root)+g)+r)+b
    neutral=mix(root,guide_root,-shape);out=mix(neutral,colored,H(hc('3a66'),rgb)).maximum(0).square()
    out=((corrected.minimum(0)-1)+corrected.maximum(1))+out
    out=mix(out,out.maximum(corrected),H(0,rgb))
    return mix(out,rgb,(person.f()*F(fc('3FE99999A0000000'),rgb)).h())


@dataclass(frozen=True)
class Result:
    stark12: V | None
    primary18: V | None
    tonal67: V | None
    output477: V | None
    unknowns: dict
    full_camera_pipeline_verified: bool=False


def forward(rgb,guide,person,parameters: Parameters,whites):
    if not isinstance(parameters,Parameters)or parameters.parameter2.point!=rgb.point:raise TypeError('Matching explicit BW parameters required')
    errors={}
    try:strong=stark(rgb,guide,person,parameters.parameter2.h(),parameters.tone20.h(),whites)
    except DomainUnknown as error:strong=None;errors['stark12']=str(error)
    primary=strong if parameters.cast_type0==4 else rgb
    if primary is None:return Result(strong,None,None,None,errors)
    base=H(hc('399a')if parameters.tuning_type17==5 else 1,primary)
    try:tonal=tonal_core(primary,person,parameters.tone65,base,base,H(1,primary))
    except DomainUnknown as error:tonal=None;errors['tonal67']=str(error)
    out=tonal if parameters.cast_type0==15 else primary
    return Result(strong,primary,tonal,out,errors)
