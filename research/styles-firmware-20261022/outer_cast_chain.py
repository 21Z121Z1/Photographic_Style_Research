"""Keep source boundary decisions around the conditional outer cast result."""
from dataclasses import dataclass
from leaf_numeric import V
from outer_cast import Result as OuterResult,forward as outer


@dataclass(frozen=True)
class Result:
    outer: OuterResult | None
    input_branch_decisions: tuple
    upstream_unknown: str | None
    full_camera_pipeline_verified: bool=False


def forward(cast_chain,post_skin,person,parameter2,tone65,mix4,mix5,*,tuning_type415,raw_cast_type245,bw477):
    if cast_chain.output413 is None:return Result(None,cast_chain.input_branch_decisions,cast_chain.unknown_operator)
    if cast_chain.output413.point or(bw477 is not None and(not isinstance(bw477,V)or bw477.point)):raise TypeError('Boundary-preserving input sets required; no centers')
    r=outer(cast_chain.output413,post_skin.highlight398,person,parameter2,tone65,mix4,mix5,tuning_type415=tuning_type415,raw_cast_type245=raw_cast_type245,bw477=bw477)
    return Result(r,cast_chain.input_branch_decisions,None)
