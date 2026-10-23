"""Operation/normality-based SSA134..140 admission, not a tuple whitelist.

Independent mathematical RN contract only. No default integration or inferred
FPCR/libm/GPU accuracy. Sqrt numerical acceptance requires a separate premise.
"""
from fractions import Fraction as Q
from square132_contract import value,rn,Assumptions,Unknown,RMAX,low_segment,classify

NAME='bright-square134-to140-conditional-rn-domain-v1'


def sqrt_rn(square:int):
    x=value(square)
    if not 0<=x<=1:raise Unknown('Bounded nonnegative sqrt argument required')
    lo,hi=0,0x3c00
    while lo<hi:
        mid=(lo+hi+1)//2
        if value(mid)**2<=x:lo=mid
        else:hi=mid-1
    if lo<0x3c00:
        midpoint=(value(lo)+value(lo+1))/2
        if x>midpoint**2 or(x==midpoint**2 and lo&1):lo+=1
    return lo


def evaluate(square:int,*,rn_even:bool|None,gradual_underflow:bool|None,
             correct_final_sqrt_half:bool=False):
    for x in [rn_even,gradual_underflow]:
        if x is not None and type(x)is not bool:raise TypeError('Explicit boolean or unknown FP conditions required')
    if type(correct_final_sqrt_half)is not bool:raise TypeError('Explicit sqrt quantization premise required')
    classification=classify(square)
    if not classification['inside_proved_prefix_outer_range']:
        raise Unknown('Outside conditional prefix hull; no clamp or GPU impossibility claim')
    common={'profile':NAME,'square132_half_bits':square,'classification':classification,
            'RN_even_is_premise_not_measured_FPCR':rn_even,
            'gradual_underflow_premise':gradual_underflow,
            'native_GPU_or_complete_bright_certified':False}
    if rn_even is not True:
        return {**common,'status':'unknown','selected140_half_bits':None,'reason':'RN-even premise missing'}
    if value(square)>Q(1,4):
        if not correct_final_sqrt_half:
            return {**common,'status':'unknown','selected140_half_bits':None,
                    'reason':'sqrt positive/normal domain proven, final sqrtf-to-half accuracy premise missing',
                    'S29_low_leaf_not_used':True}
        return {**common,'status':'conditional_math_point','selected140_half_bits':sqrt_rn(square),
                'operation':'sqrt133 selected at140','S29_low_leaf_not_used':True,
                'sqrt_quantization_assumed':True}
    ideal=low_segment(square,Assumptions(True,True,'fused'))
    used={132:square,**{i:ideal[i]for i in range(134,139)}}
    subnormals=[i for i,b in used.items()if 0<abs(value(b))<Q(1,16384)]
    if subnormals and gradual_underflow is not True:
        return {**common,'status':'unknown','selected140_half_bits':None,
                'reason':'selected low path has subnormal operands/results; gradual-underflow premise missing',
                'subnormal_SSA':subnormals}
    return {**common,'status':'conditional_math_point','selected140_half_bits':ideal[138],
            'operation':'mapped half FMA135/FMA137 with multiply134/136/138',
            'low_stage_half_bits':{str(i):ideal[i]for i in range(134,139)},
            'subnormal_SSA':subnormals,'gradual_underflow_needed':bool(subnormals),
            'normal_or_exact_zero_path_independent_of_FZ16':not subnormals,
            'old_S29_unknown_not_reclassified_in_default_model':classification['S29_selected_low_unknown']}
