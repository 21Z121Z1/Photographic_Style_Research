"""Neutral smoothSat then original half mix392, using the same live RGB.

Only the source-checked raw color3==0 set branch uses this model. The
roundtrip residual and the RGB source remain joint through subtract/mul/add.
"""
from dataclasses import dataclass
import numpy as np
from guided_affine import A
from leaf_numeric import V,DomainUnknown
from joint_lab import sources,clamped_sources,mat,half_round,as_value
from selective_neutral_joint import roundtrip,Q,M,EH,TH
T=Q@M


@dataclass(frozen=True)
class Result:
    saturated: V
    mixed: V
    proof: dict


def enclose(rgb,weight):
    if not isinstance(rgb,V)or rgb.point or rgb.precision!='h'or np.shape(rgb.lo)!=(3,)or not isinstance(weight,V)or weight.point or weight.precision!='h'or np.shape(weight.lo)!=():raise TypeError('Matching whole half RGB and original half weight required')
    core=roundtrip(rgb,shared_lab=True);x=sources(rgb);c=clamped_sources(rgb);small=mat(c,T-np.eye(3));residual=[];sat=[];mixed=[];w=A.box(weight.lo,weight.hi);rows=[]
    for i in range(3):
        d=small[i].noise(-core.proof['converted_half_error_about_QM_RGB'][i],core.proof['converted_half_error_about_QM_RGB'][i]);dl,dh=d.bounds()
        # clamp(c+d)-c has its signed displacement inside[min(0,dl),max(0,dh)].
        d=A.box(min(0.,dl),max(0.,dh));lo=float(rgb.lo[i]);hi=float(rgb.hi[i]);ext_lo=min(lo,0)+max(lo-1,0);ext_hi=min(hi,0)+max(hi-1,0)
        e1=EH*max(abs(max(lo,1)-1),abs(max(hi,1)-1))+TH;e70=(1+EH)*e1+EH*max(abs(ext_lo),abs(ext_hi))+TH;e71=EH*(max(abs(ext_lo),abs(ext_hi))+e70+1)+TH
        d=d.noise(-(e70+e71),e70+e71).guard();s=x[i].add(d)
        # Evaluate the original proof graph in order: half(x-s), half(*w),
        # half(s+product). Shared source cancels in x-s in the real reference;
        # each native operation keeps its original2u+tiny allowance.
        difference=half_round(d.neg());product=half_round(difference.product(w));out=half_round(s.add(product));residual.append(d);sat.append(s);mixed.append(out);rows.append({'roundtrip_residual_bounds':list(d.bounds()),'original_difference_bounds':list(difference.bounds()),'original_product_bounds':list(product.bounds())})
    return Result(as_value(sat,'neutral smoothSat = same FG RGB + bounded original roundtrip displacement'),as_value(mixed,'original mix392 retains same FG RGB and same smoothSat displacement'),{'core':core.proof,'channels':rows,'source_RGB_shared_with_saturated_and_difference':True,'original_half_subtract_multiply_add_order':True,'original_exterior_clamp_and_budgets_retained':True,'raw_color3_zero_required':True})
