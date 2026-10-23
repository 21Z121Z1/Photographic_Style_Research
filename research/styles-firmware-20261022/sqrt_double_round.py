"""Exact RN32-sqrt -> RN16 certificate over selected half domain, no floats.

This proves a correctly rounded mathematical chain, not an active FPCR state
or arbitrary libm/GPU accuracy. No native runtime or numpy is used.
"""
from fractions import Fraction as Q
from square132_contract import value as half_value,rn as half_rn
from square140_contract import sqrt_rn

FIRST=0x3401
LAST=0x3bff
COUNT=LAST-FIRST+1


def single_value(bits:int)->Q:
    if type(bits)is not int or not 0<=bits<=0xffffffff or bits&0x7f800000==0x7f800000:
        raise TypeError('Finite binary32 encoding required')
    e=(bits>>23)&255;m=bits&0x7fffff
    if e:m+=1<<23;shift=e-150
    else:shift=-149
    q=Q(m*(1<<shift),1)if shift>=0 else Q(m,1<<(-shift))
    return -q if bits&0x80000000 else q


def sqrt32_rn(input_half:int)->int:
    if type(input_half)is not int or not FIRST<=input_half<=LAST:
        raise ValueError('Selected half sqrt domain0x3401..0x3bff only')
    x=half_value(input_half);lo,hi=0x3f000000,0x3f800000
    while lo<hi:
        mid=(lo+hi+1)//2
        if single_value(mid)**2<=x:lo=mid
        else:hi=mid-1
    if lo<0x3f800000:
        midpoint=(single_value(lo)+single_value(lo+1))/2
        if x>midpoint**2 or(x==midpoint**2 and lo&1):lo+=1
    return lo


def ratio(q):return [q.numerator,q.denominator]
def rational(row):return Q(*row)


def cell(code,decode):
    return (decode(code-1)+decode(code))/2,(decode(code)+decode(code+1))/2


def row(input_half):
    x=half_value(input_half);h=sqrt_rn(input_half);s=sqrt32_rn(input_half);y=single_value(s);double=half_rn(y)
    lh,uh=cell(h,half_value);ls,us=cell(s,single_value)
    # Positive square-root cells can be certified without evaluating sqrt.
    gaps={'half_lower':x-lh*lh,'half_upper':uh*uh-x,
          'single_lower':x-ls*ls,'single_upper':us*us-x}
    assert all(q>0 for q in gaps.values())
    midhit=y==lh or y==uh
    return {'input_half_bits':input_half,'ideal_half_sqrt_bits':h,
            'correctly_RN_single_sqrt_bits':s,'RN_single_to_half_bits':double,
            'double_round_differs':h!=double,'single_result_is_half_midpoint':midhit,
            'input_rational':ratio(x),'sqrt_cell_squared_gaps':{n:ratio(q)for n,q in gaps.items()},
            'single_result_half_cell_gaps':{'lower':ratio(y-lh),'upper':ratio(uh-y)}}


def verify_row(r):
    """Independent midpoint-cell check, without rerunning sqrt binary search."""
    code=r['input_half_bits']
    if type(code)is not int or not FIRST<=code<=LAST:raise ValueError('Input outside selected complete domain')
    x=half_value(code);h=r['ideal_half_sqrt_bits'];s=r['correctly_RN_single_sqrt_bits'];d=r['RN_single_to_half_bits']
    if not 0x3800<=h<=0x3bff or not 0x3f000000<s<0x3f800000:raise ValueError('Unexpected root output range')
    y=single_value(s);lh,uh=cell(h,half_value);ls,us=cell(s,single_value)
    expected={'half_lower':x-lh*lh,'half_upper':uh*uh-x,'single_lower':x-ls*ls,'single_upper':us*us-x}
    if any(v<=0 for v in expected.values()):raise ValueError('Root not strictly inside claimed nearest cell')
    if r['input_rational']!=ratio(x)or r['sqrt_cell_squared_gaps']!={n:ratio(q)for n,q in expected.items()}:
        raise ValueError('Incorrect exact sqrt certificate')
    if not lh<y<uh:raise ValueError('RN32 result does not remain within direct half cell')
    if r['single_result_half_cell_gaps']!={'lower':ratio(y-lh),'upper':ratio(uh-y)}:
        raise ValueError('Incorrect second-rounding cell certificate')
    if d!=h or r['double_round_differs']or r['single_result_is_half_midpoint']:
        raise ValueError('Double-rounding equality claim failed')
    return True


def parity_lemma():
    return {'input_domain_half_bits':[FIRST,LAST],'count':COUNT,
            'x_range':'1/4 < x <=2047/2048 <1','root_range':'1/2 < sqrt(x) <1',
            'scaled_input':'x*2^24 is an even integer (multiple2^12 or2^13)',
            'half_midpoints':'M=(2m+1)/4096, m=1024..2047',
            'midpoint_square':'M^2=(odd integer)/2^24',
            'separation':'abs(x-M^2)>=2^-24; x!=M^2',
            'root_separation':'abs(sqrt(x)-M)=abs(x-M^2)/(sqrt(x)+M)>2^-25 because both root and M<1',
            'single_max_RN_error':'2^-25 for normal roots in(1/2,1)',
            'conclusion':'correct RN32 cannot land on a half midpoint; both RN32->RN16 and direct RN16 choose the same half',
            'proof_scope':'selected finite half primitive domain only; conditional on correct RN at both stages',
            'normal_domain_no_flush_or_NaN_dependency':True,
            'FPCR_RN_or_native_precision_verified':False}
