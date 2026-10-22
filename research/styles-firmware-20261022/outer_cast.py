"""Main AIR10 outer cast SSA414..492, conditional on explicit BW477 result.

This models the actual selections and two BW weights, not the BW algorithm.
Missing BW result remains unknown even when a supplied blend weight is zero.
"""
from dataclasses import dataclass
from leaf_numeric import V,hc,fc,mix,lazy_select,DomainUnknown
from leaf_domains import strictly_positive_branch
from pixel_leaves import H,F,airy,contrast,dot


def tonal(rgb,person,parameter2,tone65,tuning_type):
    base=H(hc('399a')if tuning_type==5 else hc('3b33'),rgb);weight=-parameter2.minimum(0).h()
    amount=mix(base,H(hc('accd'),rgb),weight);chroma_mix=mix(H(1,rgb),H(hc('38cd'),rgb),weight)
    c=airy(rgb,base*H(.5,rgb));offset=(amount.f()*F(fc('3FA99999A0000000'),rgb)).h()
    slope=(F(1,rgb)/(1-(offset*H(2,rgb)).f())).h();linear=slope*c+offset
    luma=dot(c,[hc('3555')]*3)
    scaled=lazy_select(luma.gt(0),lambda:(((slope.f()*luma.f()+offset.f())/strictly_positive_branch(luma).f()).h())*c,lambda:H([0,0,0],rgb))
    changed=mix(scaled,linear,chroma_mix).maximum(0);changed=contrast(changed,(amount.f()*F(fc('BFC99999A0000000'),rgb)).h())
    return mix(changed,rgb,((1-tone65)*person.f()).h())


@dataclass(frozen=True)
class Result:
    tonal468: V | None
    bw_input472: V | None
    color476: V | None
    output492: V | None
    unknowns: dict
    BW_algorithm_verified: bool=False
    full_camera_pipeline_verified: bool=False


def forward(rgb413,highlight398,person,parameter2,tone65,mix4,mix5,*,tuning_type415: int,raw_cast_type245: int,bw477: V|None):
    for value in [tuning_type415,raw_cast_type245]:
        if type(value)is not int or not 0<=value<=0xffffffff:raise TypeError('Exact uint32 shader codes required; no UI enum guessing')
    errors={}
    try:adjusted=tonal(rgb413,person,parameter2,tone65,tuning_type415)
    except DomainUnknown as error:adjusted=None;errors['tonal468']=str(error)
    bw_input=adjusted if raw_cast_type245==3 else rgb413
    color=bw_input if raw_cast_type245==4 else highlight398
    if color is None:errors['color476']='Selected upstream branch unknown'
    if bw477 is None:errors['BW477']='Explicit BW result missing; its pixel algorithm is not modeled here'
    out=None
    if color is not None and bw477 is not None:
        if not isinstance(bw477,V)or bw477.precision!='h'or bw477.point!=color.point:raise TypeError('Matching explicit half BW result required; no center conversion')
        bg=mix(color,bw477,mix4.h());fg=mix(color,bw477,mix5.h());out=mix(fg,bg,person)
    return Result(adjusted,bw_input,color,out,errors)
