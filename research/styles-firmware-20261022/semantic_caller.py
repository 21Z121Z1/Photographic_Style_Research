"""AIR10 caller's cast2 mutation before the complete semantic helper.

Input working/reference RGB are the already transformed samples at the helper
call, not original sensor/decoded HEIC pixels. Propagate boxes, never a center.
"""
import numpy as np
from semantic_tone import I,imix,forward_set


def prepare_intervals(fields,*,cast_type: int,baseline_exposure: float):
    if type(cast_type)is not int or not 0<=cast_type<=255 or not np.isfinite(baseline_exposure)or abs(baseline_exposure)>16:
        raise ValueError('Explicit cast type and supplied baselineExposure.field7 required')
    lo=fields.output_lower[33:40].copy();hi=fields.output_upper[33:40].copy()
    if cast_type==2:
        weight=float(np.float32(np.float32(1)-np.float32(np.float32(.5)*fields.controls.intensity)))
        indexes=[5,6]+([2,3]if fields.controls.tone<=0 else [])
        for n in indexes:
            target=float(np.float32(baseline_exposure))if n in (2,3)else 1.
            value=imix(I(lo[n],hi[n]),target,weight)
            lo[n]=value.lo;hi[n]=value.hi
    return lo,hi


def runtime_semantic_set(inputs,fields,*,cast_type: int,baseline_exposure: float):
    lo,hi=prepare_intervals(fields,cast_type=cast_type,baseline_exposure=baseline_exposure)
    return forward_set(inputs,lo,hi,input_branches=fields.branch_decisions)


def mixed_guide_set(fields,guide_texture8,guide_texture9,person_weight,*,cast_type,baseline_exposure):
    values=np.asarray([guide_texture8,guide_texture9,person_weight],dtype='f2')
    if not np.isfinite(values).all()or np.min(values)<0 or np.max(values)>1:raise ValueError('Supplied aligned guide8/guide9/person half values [0,1] required')
    lo,hi=prepare_intervals(fields,cast_type=cast_type,baseline_exposure=baseline_exposure)
    coefficients=I.half_cast(lo[:2],hi[:2]);a,b,w=map(float,values)
    bg=imix(b,a,I(coefficients.lo[0],coefficients.hi[0]));fg=imix(b,a,I(coefficients.lo[1],coefficients.hi[1]))
    return imix(bg,fg,w)
