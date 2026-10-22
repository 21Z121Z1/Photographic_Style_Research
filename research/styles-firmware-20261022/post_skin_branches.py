"""Set-valued AIR10 SSA393..404 fork; not a serial highlight->bright chain."""
from dataclasses import dataclass
import numpy as np
from leaf_numeric import V,DomainUnknown,mix
from pixel_leaves import H
from pixel_skin import forward as skin_forward,highlight_recover
from pixel_bright import BrightStats,forward as bright_forward


@dataclass(frozen=True)
class Inputs:
    rgb392: V
    working286: V
    person96: V
    skin95: V
    guide350: V
    exposure399: V
    stats18: BrightStats

    def __post_init__(self):
        values=[self.rgb392,self.working286,self.person96,self.skin95,self.guide350,self.exposure399]
        if any(not isinstance(v,V)or v.point or v.precision!='h'for v in values):raise TypeError('Explicit half sets required; centers are not accepted')
        if any(np.shape(v.lo)!=(3,)for v in values[:2])or any(np.shape(v.lo)!=()for v in values[2:]):raise ValueError('Two RGB vectors and four scalar sets required')
        if any(v.lo<0 or v.hi>1 for v in values[2:5]):raise ValueError('Original person/skin/guide sets must stay in [0,1]')
        if not isinstance(self.stats18,BrightStats)or self.stats18.s2_4.point:raise TypeError('Explicit f32 stats sets required')


@dataclass(frozen=True)
class Result:
    skin393: V | None
    highlight398: V | None
    bright400: V | None
    neutralizing_input404: V | None
    unknown_branches: dict
    input_branch_decisions: tuple
    full_camera_pipeline_verified: bool=False


def forward(inputs: Inputs,fields,*,raw_cast_type245: int):
    if type(raw_cast_type245)is not int or not 0<=raw_cast_type245<=0xffffffff:raise ValueError('Actual uint32 shader cast code required; no UI-name inference')
    if not isinstance(inputs,Inputs):raise TypeError('Explicit helper-call context required')
    t9=V.bounds(fields.output_lower[26],fields.output_upper[26],'f');t10=V.bounds(fields.output_lower[27],fields.output_upper[27],'f');errors={}
    try:skin=skin_forward(inputs.rgb392,inputs.skin95,inputs.guide350,t9,t10)
    except DomainUnknown as error:return Result(None,None,None,None,{'skin393':str(error)},fields.branch_decisions)
    try:
        high=highlight_recover(skin,inputs.guide350,H(2,skin));high=mix(skin,high,H(.5,skin))if raw_cast_type245==2 else skin
    except DomainUnknown as error:
        errors['highlight394']=str(error);high=None if raw_cast_type245==2 else skin
    try:bright=bright_forward(skin,inputs.working286,inputs.person96,inputs.skin95,inputs.exposure399,inputs.stats18)
    except DomainUnknown as error:errors['bright400']=str(error);bright=None
    neutral=bright if raw_cast_type245==16 else skin
    return Result(skin,high,bright,neutral,errors,fields.branch_decisions)
