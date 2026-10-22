"""Joint newspan/span enclosure for the original contrast half instruction graph.

The half quotient is proved finite BEFORE bounding its subsequent product.
No normalized-before-division evaluation, gate change or center substitution.
The source program's common scalar terms control pairwise channel spread.
"""
from dataclasses import dataclass
import math
import numpy as np
from leaf_numeric import V,DomainUnknown,hc,fc,exterior,mix
from leaf_correlations import channel_span
from leaf_domains import strictly_positive_branch

EH=2**-10;TH=2**-24;ETH=2**-9;GATE=fc('3EE4F8B580000000')

# Exact saved S15C cell0 outer box and original half contrast parameter.
# Only this proved family is admitted by the default leaf fallback. The
# standalone enclose function remains an explicit diagnostic, not a wider
# admission gate for arbitrary style inputs.
CELL0_LO=(0.,-.014420070058153133,0.)
CELL0_HI=(.23502742808362515,.2394291029825464,.1698263112707185)
CELL0_AMOUNT=.029998779296875


def cell0_supported(rgb,amount):
    return isinstance(rgb,V)and not rgb.point and rgb.precision=='h'and np.shape(rgb.lo)==(3,)and isinstance(amount,V)and not amount.point and amount.precision=='h'and np.shape(amount.lo)==()and np.all(rgb.lo>=CELL0_LO)and np.all(rgb.hi<=CELL0_HI)and float(amount.lo)==CELL0_AMOUNT and float(amount.hi)==CELL0_AMOUNT


def maximum(v):return float(np.max(np.maximum(abs(v.lo),abs(v.hi))))
def error(bound):return EH*bound+TH
def up(x):return math.nextafter(float(x)+2**-40*max(1.,abs(float(x))),math.inf)


def add_shared(x,scalar,A,B):
    # A*sqrt(D)+B is a bound on pairwise spread of x. A common scalar
    # cancels in the real difference; only the original half add errors remain.
    e=error(maximum(x)+maximum(scalar));return x+scalar,A,B+2*e


def mix_spread(a,b,w,Aa,Ba,Ab,Bb):
    one_minus=max(abs(1-float(w.lo)),abs(1-float(w.hi)));wa=maximum(w)
    sub=b-a;ed=error(maximum(a)+maximum(b));prod=sub*w;ep=error(maximum(sub)*wa);ea=error(maximum(a)+maximum(prod));out=a+prod
    return out,one_minus*Aa+wa*Ab,one_minus*Ba+wa*Bb+2*(wa*ed+ep+ea)


@dataclass(frozen=True)
class Result:
    output: V
    changed: V
    quotient: V|None
    proof: dict
    original_GPU_or_full_BG_verified: bool=False


def enclose(rgb,amount):
    if not isinstance(rgb,V)or rgb.point or rgb.precision!='h'or rgb.lo.shape!=(3,)or not isinstance(amount,V)or amount.point or amount.precision!='h'or amount.lo.shape!=():raise TypeError('Whole half RGB and half amount sets required')
    from pixel_leaves import H,F,dot,root_components
    c=rgb.clamp();s=dot(c,[hc('3555')]*3).sqrt();delta=c-s
    # The three occurrences are actual squares, not independent products.
    variance=delta.square().sum_channels();shape=((1-s.f())*s.f()).h();root=c.sqrt();scaled=(amount.f()*F(fc('400B333340000000'),rgb)).h();amp=shape*scaled;r,g,b=root_components(root,amp)
    eroot=ETH*math.sqrt(maximum(c))+TH;colored=root;Ac=1.;Bc=2*eroot
    for scalar in [amp*H(hc('b800'),rgb),g,r,b]:colored,Ac,Bc=add_shared(colored,scalar,Ac,Bc)
    neutral,An,Bn=mix_spread(root,H(hc('3800'),rgb),(-scaled)*shape,1.,2*eroot,0.,0.)
    newroot,A,B=mix_spread(neutral,colored,(variance.f()+F(fc('3FE99999A0000000'),rgb)).h(),An,Bn,Ac,Bc);newroot=newroot.maximum(0);R=maximum(newroot)
    # Squaring the nonnegative root is2R-Lipschitz; retain its actual2u error.
    A*=2*R;B=2*R*B+2*error(R*R)
    low=rgb.minimum(0);high=rgb.maximum(1);sub=low-1
    exterior_pair_error=2*(error(maximum(low)+1)+error(maximum(sub)+maximum(high)))
    square=newroot*newroot;ext=sub+high;changed=ext+square
    B+=exterior_pair_error+2*error(maximum(ext)+maximum(square))
    # changed spread <=D +A*sqrt(D)+B, where D is real max(rgb)-min(rgb).
    A=up(A);B=up(B)
    span=channel_span(rgb);condition=span.f().gt(F(GATE,rgb));proof={'source':'AIR10 contrastFilter SSA3..95','input_lo':rgb.lo.tolist(),'input_hi':rgb.hi.tolist(),'A_sqrt_D':A,'B_absolute':B,'changed_lo':changed.lo.tolist(),'changed_hi':changed.hi.tolist(),'threshold':GATE,'epsilon_mask_or_budgets_changed':False,'division_before_product_preserved':True,'bound_assumption':'existing2u half arithmetic/4u sqrt; deterministic common scalars; finite IEEE min/max'}
    if np.all(condition.no):return Result(changed,changed,None,dict(proof,branch='original else only'))
    minimum=float(strictly_positive_branch(span,GATE).lo)
    d_at_min=(minimum+TH)/(1-EH)
    raw_q=up((1+EH)*(d_at_min+A*math.sqrt(d_at_min)+B)/minimum+TH/minimum)
    # All terms D/s, sqrt(D)/s and1/s decrease on s>0 after substituting
    # D<=(s+tiny)/(1-2u); evaluating s_min covers the original strict branch.
    quotient=rgb.rounded(0.,raw_q)
    if maximum(quotient)>65504:raise DomainUnknown('Joint contrast quotient exceeds original half finite budget')
    Dmax=max(0.,max(float(rgb.hi[i]-rgb.lo[j])for i in range(3)for j in range(3)if i!=j));delta_max=(1+EH)*Dmax+TH
    kappa=up((1+EH)*(minimum+TH)/((1-EH)*minimum)+TH/minimum)
    Aq=up((1+EH)**2*kappa);K=up(Aq*(1+EH));eta=up(Aq*TH+(1+EH)*delta_max*TH+TH)
    L=float(np.min(changed.lo));Hmax=float(np.max(changed.hi));Cspan=Hmax-L
    product_max=up(K*Cspan+eta)
    if product_max>65504:raise DomainUnknown('Joint contrast original post-division product exceeds half finite budget')
    ylo=L;yhi=up(Hmax+(K-1)*Cspan+eta)
    positive=rgb.rounded(np.full(3,ylo),np.full(3,yhi))
    out=positive if np.all(condition.yes)else V(np.minimum(positive.lo,changed.lo),np.maximum(positive.hi,changed.hi),'h',False)
    proof.update(branch='strict-positive plus original else union'if not np.all(condition.yes)else'strict-positive only',strict_span_lower=minimum,real_span_upper_at_lower=d_at_min,quotient_raw_upper=raw_q,quotient_half_upper=float(quotient.hi),original_product_upper=product_max,position_ratio_upper=kappa,post_product_factor=K,post_product_absolute=eta,output_lo=out.lo.tolist(),output_hi=out.hi.tolist(),negative_or_zero_span_not_removed=True,half_quotient_finiteness_proved_before_product=True)
    return Result(out,changed,quotient,proof)
