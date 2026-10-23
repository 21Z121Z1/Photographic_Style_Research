"""Independent exact-rational RN-half prefix/domain contract; never v3 dispatch.

Native pow/sqrt/FPCR accuracy is NOT inferred. Exact ideal-power certificates
are mathematical witnesses. Gradual underflow and RN-even must be declared.
"""
from dataclasses import dataclass
from fractions import Fraction as Q


class Unknown(ValueError):pass


def value(bits:int)->Q:
    if type(bits)is not int or not 0<=bits<=0xffff or (bits&0x7c00)==0x7c00:
        raise TypeError('Finite binary16 encoding required')
    exp=(bits>>10)&31;mant=bits&1023
    if exp:mant+=1024;shift=exp-25
    else:shift=-24
    out=Q(mant*(1<<shift),1)if shift>=0 else Q(mant,1<<(-shift))
    return -out if bits&0x8000 else out


def rn(x:Q,*,negative_zero=False)->int:
    if not isinstance(x,Q):raise TypeError('Exact rational arithmetic required')
    sign=x<0 or (x==0 and negative_zero);x=abs(x)
    if x>value(0x7bff):raise Unknown('Finite rounding contract exceeded')
    lo,hi=0,0x7bff
    while lo<hi:
        mid=(lo+hi+1)//2
        if value(mid)<=x:lo=mid
        else:hi=mid-1
    if value(lo)!=x and lo<0x7bff:
        a=x-value(lo);b=value(lo+1)-x
        if b<a or (a==b and lo&1):lo+=1
    return lo|(0x8000 if sign else 0)


def mul(a,b):return rn(value(a)*value(b),negative_zero=bool((a^b)&0x8000))
def add(a,b):return rn(value(a)+value(b),negative_zero=bool(a&b&0x8000))
def sub(a,b):return add(a,b^0x8000)
def fma(a,b,c):
    product=value(a)*value(b)
    negative=product==0 and value(c)==0 and bool((a^b)&c&0x8000)
    return rn(product+value(c),negative_zero=negative)


CONSTANTS={'encode_threshold':0x1a69,'encode_linear':0x4a76,'power_exponent':0x36aa,
           'encode_scale':0x3c38,'encode_offset':0xab0a,'weight_factor':0x2e66,
           'weight_cap':0x359a,'low_sqrt_threshold':0x3400}
RMAX=rn(value(CONSTANTS['encode_scale'])+value(CONSTANTS['encode_offset']))


def power_rn(c:int):
    """Ideal real c**alpha quantized once to half, using integer powers only."""
    x=value(c);exponent=value(CONSTANTS['power_exponent']);p,q=exponent.numerator,exponent.denominator
    if not 0<=x<=1:raise Unknown('Clamped positive half input required')
    if x==0:return 0
    target=x**p
    lo,hi=0,0x3c00
    while lo<hi:
        mid=(lo+hi+1)//2
        if value(mid)**q<=target:lo=mid
        else:hi=mid-1
    if lo<0x3c00:
        midpoint=(value(lo)+value(lo+1))/2
        boundary=midpoint**q
        if target>boundary or(target==boundary and lo&1):lo+=1
    return lo


def power_certificate(c,power):
    a=value(CONSTANTS['power_exponent']);p,q=a.numerator,a.denominator
    target=value(c)**p
    lower=Q(0)if power==0 else (value(power-1)+value(power))/2
    upper=(value(power)+value(power+1))/2
    lc=target-lower**q;uc=upper**q-target
    closed=power%2==0
    if not(lc>0 or(lc==0 and closed))or not(uc>0 or(uc==0 and closed)):
        raise AssertionError('Ideal power half-rounding certificate failed')
    return {'input_half_bits':c,'power_half_bits':power,'exponent_numerator':p,'exponent_denominator':q,
            'lower_midpoint':[lower.numerator,lower.denominator],'upper_midpoint':[upper.numerator,upper.denominator],
            'lower_power_comparison_sign':1 if lc>0 else 0,'upper_power_comparison_sign':1 if uc>0 else 0,
            'ties_even_endpoint_included':closed,'method':'compare exact c^p with midpoint^q; integer/rational powers, no floating pow',
            'native_powf_or_GPU_accuracy_certified':False}


def reference(c:int,power:int|None=None):
    x=value(c)
    if not 0<=x<=1 or c&0x8000:raise Unknown('Canonical clamped nonnegative half input required')
    if c<=CONSTANTS['encode_threshold']:
        return mul(c,CONSTANTS['encode_linear'])
    if power is None:power=power_rn(c)
    if not Q(7,128)<=value(power)<=1:raise Unknown('Nonlinear power enclosure not established')
    return fma(power,CONSTANTS['encode_scale'],CONSTANTS['encode_offset'])


def weight(strength:int):
    if not 1<=value(strength)<=12:raise Unknown('Derived finite strength half range[1,12] required')
    raw=mul(strength,CONSTANTS['weight_factor'])
    return min(raw,CONSTANTS['weight_cap'])


@dataclass(frozen=True)
class Assumptions:
    rn_even:bool
    gradual_underflow:bool
    mix_mode:str
    def __post_init__(self):
        if self.rn_even is not True or self.gradual_underflow is not True:
            raise Unknown('Explicit RN-even/gradual-underflow mathematical contract required; FPCR not inferred')
        if self.mix_mode not in('separate','fused'):raise Unknown('Explicit subtraction then separate or fused mix required')


def prefix(c:int,strength:int,assumptions:Assumptions):
    if not isinstance(assumptions,Assumptions):raise TypeError('Explicit arithmetic assumptions required')
    p=None if c<=CONSTANTS['encode_threshold']else power_rn(c)
    r=reference(c,p);w=weight(strength);u=mul(r,r);d=sub(u,r)
    product=mul(d,w)
    square=add(r,product)if assumptions.mix_mode=='separate'else fma(d,w,r)
    if not 0<=value(square)<=value(r)<=value(RMAX):raise AssertionError('Symbolically derived enclosure violated')
    return {'c':c,'reference112':r,'weight128':w,'square129':u,'difference':d,
            'rounded_product':product,'square132':square,'mix_mode':assumptions.mix_mode,
            'power_certificate':None if p is None else power_certificate(c,p)}


def classify(square:int):
    x=value(square)
    if x<0 or square&0x8000:raise Unknown('Canonical nonnegative square required')
    low=x<=Q(1,4);old=Q(1,16)<=x<=1
    return {'square132_half_bits':square,'value':[x.numerator,x.denominator],
            'inside_proved_prefix_outer_range':x<=value(RMAX),
            'selected140_branch':'low'if low else'sqrt','equality_at_quarter_belongs_to':'low',
            'zero':x==0,'subnormal':0<x<Q(1,16384),'below_old_leaf_lower_bound':x<Q(1,16),
            'S29_low_leaf_accepts_input':old,
            'S29_low_leaf_needed_for140':low,
            'S29_selected_low_covered':low and old,
            'S29_selected_low_unknown':low and not old,
            'sqrt_numeric_contract':'requires sqrtf-to-half accuracy assumption; domain positive normal here'if not low else'not selected'}


def low_segment(square:int,assumptions:Assumptions):
    if not isinstance(assumptions,Assumptions):raise TypeError('Explicit arithmetic assumptions required')
    if not 0<=value(square)<=value(RMAX):raise Unknown('Proved prefix outer range only')
    s134=mul(square,0x4c00);s135=fma(square,0x4c00,0xca00)
    s136=mul(s135,square);s137=fma(s135,square,0x4400);s138=mul(s137,square)
    return {134:s134,135:s135,136:s136,137:s137,138:s138,
            'selected':s138 if value(square)<=Q(1,4)else None,
            'status':'independent exact IEEE/RN contract; not default or GPU acceptance'}
