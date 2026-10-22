"""Set-only main SSA408->409->413 prefix, preserving first unknown and input."""
from dataclasses import dataclass
from leaf_numeric import V,DomainUnknown
from cast_values import CastValues
from pixel_neutral_root import NeutralStats,forward as neutralize
from pixel_warmth import forward as warmth
from pixel_selective import SelectiveTexture,forward as selective


@dataclass(frozen=True)
class Result:
    output413: V | None
    unknown_operator: str | None
    unknown_input_set: V | None
    reason: str | None
    input_branch_decisions: tuple
    full_camera_pipeline_verified: bool=False


def forward(post_skin,*,cast: CastValues,person,skin,sky,output_mix,enabled_neutralizing: bool,use_skin: bool,stats: NeutralStats|None,texture: SelectiveTexture):
    x=post_skin.neutralizing_input404
    if x is None:return Result(None,'upstream404',None,'Upstream set unknown',post_skin.input_branch_decisions)
    if not isinstance(x,V)or x.point or cast.raw.point:raise TypeError('Full input sets required; no coefficient or pixel centers')
    for name,fn in [('neutralizing408',lambda x:neutralize(x,enabled=enabled_neutralizing,cast=cast,skin=skin,person=person,use_skin=use_skin,stats=stats)),('warmth409',lambda x:warmth(x,cast,person)),('selective413',lambda x:selective(x,cast,texture,person,skin,sky,output_mix))]:
        try:x=fn(x)
        except DomainUnknown as error:return Result(None,name,x,str(error),post_skin.input_branch_decisions)
    return Result(x,None,None,None,post_skin.input_branch_decisions)
