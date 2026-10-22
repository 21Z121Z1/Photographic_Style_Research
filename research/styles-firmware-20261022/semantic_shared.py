"""Optional shared-reference proof for original precomputed semantic335 only.

No new gain inputs or exposure estimates. Retain original half mix/min/product
order with the unchanged2u+tiny budget, common reference and common person.
"""
from dataclasses import dataclass
import numpy as np
from guided_affine import A
from leaf_numeric import V
from joint_lab import half_round,as_value


def cap_one(a):
    lo,hi=a.bounds()
    if hi<=1:return a
    if lo>=1:return A.value(1)
    slope=(1-lo)/(hi-lo);bias=lo-slope*lo;res=1-(slope+bias)
    return a.scale(slope).add(bias).noise(-2e-12,res+2e-12).guard()


def mix(a,b,w):
    if a is b:return a
    difference=half_round(b.add(a.neg()));product=half_round(difference.product(w));return half_round(a.add(product))


@dataclass(frozen=True)
class Result:
    output: V
    proof: dict


def enclose(bg,fg,reference,person,semantic7):
    if any(not isinstance(v,V)or v.point for v in [bg,fg,reference,person,semantic7])or any(v.precision!='h'or v.lo.shape!=(3,)for v in [bg,fg,reference])or person.precision!='h'or person.lo.shape!=()or semantic7.precision!='f'or semantic7.lo.shape!=(7,):raise TypeError('Whole matching half sampled gains/reference/person and f32 semantic7 required')
    boxes=lambda v:[A.box(lo,hi)for lo,hi in zip(v.lo,v.hi)]
    a,b,ref=boxes(bg),boxes(fg),boxes(reference);p=boxes(semantic7.h());w=A.box(person.lo,person.hi);out=[]
    for i in range(3):
        # Original315/319/320 and327/331/332. Each product uses SAME ref[i].
        f=mix(b[i],A.value(1),p[1]);f=half_round(mix(f,cap_one(f),p[6]).product(ref[i]))
        g=mix(a[i],A.value(1),p[0]);g=half_round(mix(g,cap_one(g),p[5]).product(ref[i]))
        out.append(mix(g,f,w))
    result=as_value(out,'original semantic335 shares reference196,semantic weights and person96')
    return Result(result,{'scope':'AIR10 precomputed315..335; input sampling remains supplied original hull contract','same_reference_in_BG_FG_products':True,'same_person_across_channels':True,'same_semantic_parameters_across_channels':True,'half_mix_sub_mul_add_order_preserved':True,'half_product_before_outer_mix_preserved':True,'half_2u_tiny_budget_changed':False,'added_clamp':False,'endpoint_reachability_proved':False,'GPU_verified':False})
