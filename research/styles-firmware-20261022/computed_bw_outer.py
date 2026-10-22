"""Compute real BW477 before the outer mix; never accepts a supplied BW output."""
from dataclasses import dataclass,replace
from leaf_numeric import V,mix
from outer_cast import forward as outer,Result as OuterResult
from pixel_bw import Parameters,Result as BWResult,forward as bw_forward


@dataclass(frozen=True)
class Result:
    outer: OuterResult | None
    bw: BWResult | None
    output492: V | None
    unknown_reason: str | None
    input_branch_decisions: tuple
    BW_output_supplied_externally: bool=False
    full_camera_pipeline_verified: bool=False


def forward(rgb413,highlight398,guide350,person96,mix4,mix5,*,parameters: Parameters,raw_cast_type245: int,whites,input_branch_decisions=()):
    r=outer(rgb413,highlight398,person96,parameters.parameter2,parameters.tone65,mix4,mix5,tuning_type415=parameters.tuning_type17,raw_cast_type245=raw_cast_type245,bw477=None)
    if r.bw_input472 is None:return Result(r,None,None,'BW input472 unknown',tuple(input_branch_decisions))
    bw=bw_forward(r.bw_input472,guide350,person96,parameters,whites)
    if bw.output477 is None:return Result(r,bw,None,'Selected BW477 branch unknown',tuple(input_branch_decisions))
    errors={k:v for k,v in r.unknowns.items()if k!='BW477'}
    if r.color476 is None:return Result(replace(r,unknowns=errors),bw,None,'Selected color476 branch unknown',tuple(input_branch_decisions))
    bg=mix(r.color476,bw.output477,mix4.h());fg=mix(r.color476,bw.output477,mix5.h());out=mix(fg,bg,person96)
    return Result(replace(r,output492=out,unknowns=errors),bw,out,None,tuple(input_branch_decisions))


def from_chain(cast_chain,post_skin,guide350,person96,mix4,mix5,*,parameters,raw_cast_type245,whites):
    if cast_chain.output413 is None:return Result(None,None,None,'Upstream '+str(cast_chain.unknown_operator),cast_chain.input_branch_decisions)
    if cast_chain.output413.point:raise TypeError('Upstream pipeline must provide whole sets, not centers')
    return forward(cast_chain.output413,post_skin.highlight398,guide350,person96,mix4,mix5,parameters=parameters,raw_cast_type245=raw_cast_type245,whites=whites,input_branch_decisions=cast_chain.input_branch_decisions)
