"""AIR10 original355..392 outer color branch, reusing existing saturation leaves."""
from dataclasses import dataclass
import numpy as np
from leaf_numeric import V,fc,lazy_select,select,mix
from pixel_leaves import H,F
from pixel_color import rich_sat,smooth_sat


@dataclass(frozen=True)
class Result:
    saturated374: V
    output392: V
    person_mix389: V
    joint_proof: dict|None=None


def forward(rgb354,person96,color3,color_boost11_2,*,joint=True):
    if any(not isinstance(v,V)for v in [rgb354,person96,color3,color_boost11_2])or any(v.point!=rgb354.point for v in [person96,color3,color_boost11_2])or [v.precision for v in [rgb354,person96,color3,color_boost11_2]]!=['h','h','f','f']:raise TypeError('Matching half RGB/person and original f32 color/boost fields required')
    color=color3.h();delta=select(color.lt(0),(color.f()*F(fc('3FE99999A0000000'),color)).h(),color.square());gain=delta+1
    protect=lazy_select(color.gt(0),lambda:(color.f()+F(fc('BFE3333340000000'),color)).maximum(F(fc('3FC99999A0000000'),color)),lambda:(F(fc('3FB99999A0000000'),color)-color.f()*F(fc('3FE3333340000000'),color)).maximum(F(fc('3FC99999A0000000'),color))).h()
    weight=((1-protect.f())*person96.f()).h()
    if type(joint)is not bool:raise TypeError('Exact shared-color backend selector required')
    if joint and not rgb354.point and np.all(color3.lo==0)and np.all(color3.hi==0):
        from neutral_color_joint import enclose
        result=enclose(rgb354,weight);return Result(result.saturated,result.mixed,weight,result.proof)
    saturated=lazy_select(color.gt(0),lambda:rich_sat(rgb354,gain,color_boost11_2.h()),lambda:smooth_sat(rgb354,gain))
    return Result(saturated,mix(saturated,rgb354,weight),weight)
