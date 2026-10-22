"""AIR10 video-haze root, with original guide211 distinct from mixed guide350."""
from dataclasses import dataclass
import numpy as np
from leaf_numeric import V,DomainUnknown,lazy_select,mix,hc
from leaf_domains import strictly_positive_branch
from pixel_leaves import H,F,dot,contrast
from pixel_remaining import local_contrast
from bgfg_tone import mids_half,mids_set
from semantic_tone import I


@dataclass(frozen=True)
class Parameters:
    fields1_8: V
    enabled0: bool

    def __post_init__(self):
        if not isinstance(self.fields1_8,V)or self.fields1_8.precision!='f'or np.shape(self.fields1_8.lo)!=(8,):raise TypeError('Eight supplied f32 SSRHaze fields1..8 required')
        if type(self.enabled0)is not bool:raise TypeError('Actual haze field0 byte flag required')


def mids(rgb,amount):
    if rgb.point:return V.value(mids_half(rgb.lo,amount.lo))
    a=mids_set(I(rgb.lo,rgb.hi),I(amount.lo,amount.hi))
    return V(a.lo,a.hi,'h',False)


def forward(rgb,guide211,person96,parameters: Parameters):
    if not isinstance(parameters,Parameters)or parameters.fields1_8.point!=rgb.point:raise TypeError('Matching explicit haze parameters required')
    p=parameters.fields1_8;mean=dot(rgb,[hc('3555')]*3)
    def branch(denominator,mids_amount):
        offset=(p[0]/denominator).h();gain=(F(1,rgb)/(1-offset.f())).h();linear=gain*rgb+offset
        scaled=lazy_select(mean.gt(0),lambda:(((mean.f()*gain.f()+offset.f())/strictly_positive_branch(mean).f()).h())*rgb,lambda:H([0,0,0],rgb))
        changed=mix(scaled,linear,p[5].h()).maximum(0)
        return mids(changed,mids_amount.h())
    bg=branch(p[1],p[3]);fg=branch(p[2],p[4]);bg=contrast(bg,p[6].h());bg=local_contrast(bg,guide211,p[7].h())
    return mix(bg,fg,person96)


@dataclass(frozen=True)
class Result:
    haze493: V | None
    output501: V | None
    unknown_reason: str | None
    full_camera_pipeline_verified: bool=False


def select_video(rgb492,guide211,person96,parameters: Parameters,*,tuning_type17: int):
    if type(tuning_type17)is not int or not 0<=tuning_type17<=0xffffffff:raise TypeError('Exact tuning field17 required')
    try:haze=forward(rgb492,guide211,person96,parameters);reason=None
    except DomainUnknown as error:haze=None;reason=str(error)
    return Result(haze,haze if tuning_type17==7 and parameters.enabled0 else rgb492,reason)
