"""Joint z/curve(z)/changed bound for original whites product then division.

The original half product is separately proved finite before its quotient.
Only a nonnegative zero-origin bounded supplied curve and amount[0,1] qualify.
Every half operation and explicit host float sampler step keeps2u+tiny.
"""
from dataclasses import dataclass
import math
import numpy as np
from leaf_numeric import V,DomainUnknown

EH=2**-10;TH=2**-24;EF=2**-23;TF=2**-149;UH=2**-11


def add(a,b):return(a[0]+b[0],a[1]+b[1])
def scale(a,s):return(a[0]*s,a[1]*s)
def error(a):return(a[0]*EH,a[1]*EH+TH)
def rounded(a):return add(a,error(a))
def up(x):return math.nextafter(float(x)+2e-12*max(1.,abs(float(x))),math.inf)


@dataclass(frozen=True)
class Result:
    quotient: V
    proof: dict


def enclose(c,z,amount,curve):
    if any(not isinstance(v,V)or v.point or v.precision!='h'for v in [c,z,amount])or np.shape(c.lo)!=(3,)or np.shape(z.lo)!=()or np.shape(amount.lo)!=():raise DomainUnknown('Whole half whites operands required')
    table=np.asarray(curve.red_samples,dtype='f8');n=len(table);a=float(amount.hi);zl=float(z.lo);zh=float(z.hi)
    if not 2<=n<=1024 or table[0]!=0 or np.any(table<0)or np.any(table>1)or float(amount.lo)<0 or a>1 or zl<=0 or np.any(c.lo<0):raise DomainUnknown('Whites zero-origin curve/amount/positive-z admission not met')
    # A piecewise linear table with origin0 satisfies f(q)<=S*q, including
    # the original endpoint clamp. The >half.75 branch returns1 instead.
    nodes=np.linspace(0,1,n);S=float(np.max(table[1:]/nodes[1:]));L=float(np.max(abs(np.diff(table)))*(n-1));imax=(1+EH)*(n-1)*zh+TH
    if imax>65504:raise DomainUnknown('Original whites half sample index exceeds finite domain')
    ecoord=EF*(imax+.5)+TF;ecoord+=EF*(imax+ecoord)+TF
    # q's integer interval changes at continuous piecewise-linear knots.
    # q-i lies in[0,1]; preserve the float difference/product/add budgets.
    diff=float(np.max(abs(np.diff(table))));ediff=EF*diff+TF;efrac=EF+TF;ep=EF*(diff+ediff)*(1+efrac)+TF;ea=EF*(float(np.max(table))+(diff+ediff)*(1+efrac)+ep)+TF
    sampler_error=L*ecoord+diff*efrac+ediff*(1+efrac)+ep+ea
    A=up(max((1+UH)*S*(1+EH),1/.75));B=up((1+UH)*(S*TH/(n-1)+sampler_error)+2**-25)
    # Bound ABS of each original half intermediate as C*z+D, with common z.
    # sub=half(target-z), p=half(sub*amount), changed=half(z+p).
    sub=rounded((A+1,B));p=rounded(scale(sub,a));changed=rounded(add((1.,0.),p));C,D=changed
    intermediate_bounds={name:up(coeff[0]*zh+coeff[1])for name,coeff in [('target_minus_z',sub),('difference_times_amount',p),('changed',changed)]}
    if any(bound>65504 for bound in intermediate_bounds.values()):raise DomainUnknown('Original whites mix intermediate finite bound exceeds half budget')
    # Product42 is evaluated BEFORE division45. Prove its finite bound first.
    products=[];quotients=[]
    for maximum in c.hi:
        coeff=rounded(scale(changed,float(maximum)));Pmax=up(coeff[0]*zh+coeff[1])
        if Pmax>65504:raise DomainUnknown('Original whites product42 finite bound exceeds half budget')
        Qmax=up((1+EH)*(coeff[0]+coeff[1]/zl)+TH)
        if Qmax>65504:raise DomainUnknown('Original whites quotient45 finite bound exceeds half budget')
        products.append(Pmax);quotients.append(Qmax)
    q=V(-np.array(quotients),np.array(quotients),'h',False)
    proof={'source':'AIR10 whitesCurve z18,target31,changed32,product42,division45','curve_knots':n,'curve_origin':0,'max_table_value_over_coordinate':S,'curve_Lipschitz':L,'host_sampler_float_error':sampler_error,'target_upper_A_z_plus_B':[A,B],'changed_absolute_upper_C_z_plus_D':[C,D],'original_mix_intermediate_absolute_upper':intermediate_bounds,'original_z_positive_lo':zl,'original_z_hi':zh,'original_product42_absolute_upper':products,'original_quotient45_absolute_upper':quotients,'product_proved_finite_before_quotient':True,'original_product_then_divide_order_preserved':True,'numerator_zero_or_endpoint_reachability_not_inferred':True,'budgets_threshold_epsilon_mask_unchanged':True,'sampler_contract':'explicit host piecewise-linear/clamp supplied half table with2u float-operation allowances and correct half conversion; originalGPU unverified'}
    return Result(q,proof)
