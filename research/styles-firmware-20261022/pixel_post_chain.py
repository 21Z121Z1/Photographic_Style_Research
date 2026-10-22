"""Set-only actual 492->501->566->567 dataflow; unknowns remain explicit."""
from dataclasses import dataclass
from leaf_numeric import V,DomainUnknown
from pixel_haze import select_video
from pixel_postprotect import forward as postprotect
from pixel_channel_mix import forward as channel_mix


@dataclass(frozen=True)
class Result:
    output501: V | None
    output566: V | None
    output567: V | None
    unknown_operator: str | None
    reason: str | None
    input_branch_decisions: tuple
    haze_internal_unknown: str | None
    full_camera_pipeline_verified: bool=False


def forward(computed_outer,guide211,person96,*,haze,tuning_type17,cast,stats,texture10_present,cast_type0,tone17_19):
    marker=computed_outer.input_branch_decisions
    if computed_outer.output492 is None:return Result(None,None,None,'upstream492',computed_outer.unknown_reason,marker,None)
    if computed_outer.output492.point:raise TypeError('Pipeline input must preserve entire sets, not centers')
    h=select_video(computed_outer.output492,guide211,person96,haze,tuning_type17=tuning_type17)
    if h.output501 is None:return Result(None,None,None,'haze493',h.unknown_reason,marker,h.unknown_reason)
    try:p=postprotect(h.output501,computed_outer.outer.color476,cast,stats,texture10_present=texture10_present)
    except DomainUnknown as error:return Result(h.output501,None,None,'postprotect566',str(error),marker,h.unknown_reason)
    try:out=channel_mix(p,person96,cast_type0=cast_type0,tone17_19=tone17_19,stats=stats)
    except DomainUnknown as error:return Result(h.output501,p,None,'channel567',str(error),marker,h.unknown_reason)
    return Result(h.output501,p,out,None,None,marker,h.unknown_reason)
