"""Joint real-reference/error enclosure for this build's neutral selective path.

Strictly requires zero four-row lookup, zero three offsets/amplitudes and
zero output_mix. Does not clamp a converted base, change pow domain, substitute
input centers, or assert that a negative interval endpoint is reachable.
Matrices are composed ONLY in the real reference proof; every original FP
stage remains accounted for by the existing2u/4u budgets and half conversion.
"""
from dataclasses import dataclass
import math
import numpy as np
from leaf_numeric import V,fc,DomainUnknown
from guided_affine import A

from color_matrices import TO_LMS_COLUMNS,TO_LAB_COLUMNS,FROM_LAB_A,FROM_LAB_B,FROM_ROOT_COLUMNS,POWER_HEX,INVERSE_POWER_HEX
M=np.array([[fc(v)for v in col]for col in TO_LMS_COLUMNS]).T
N=np.array([[fc(v)for v in col]for col in TO_LAB_COLUMNS]).T
P=np.stack([np.ones(3),[fc(v)for v in FROM_LAB_A],[fc(v)for v in FROM_LAB_B]],axis=1)
Q=np.array([[fc(v)for v in col]for col in FROM_ROOT_COLUMNS]).T
POWER=fc(POWER_HEX);INVERSE_POWER=fc(INVERSE_POWER_HEX)
E32=2**-23;T32=2**-149;ET32=2**-22;EH=2**-10;TH=2**-24;ETH=2**-9;UH=2**-11


def zero(v):return isinstance(v,V)and np.all(v.lo==0)and np.all(v.hi==0)

def supported(rgb,person,skin,sky,texture,offsets,amplitudes,output_mix):
    def typed(v,shape):return isinstance(v,V)and not v.point and v.precision=='h'and v.lo.shape==shape
    from pixel_selective import SelectiveTexture
    return isinstance(texture,SelectiveTexture)and typed(rgb,(3,))and np.shape(texture.values)==(4,360,4)and np.all(texture.values==0)and len(offsets)==3 and all(typed(x,(2,))and zero(x)for x in offsets)and typed(amplitudes,(3,))and zero(amplitudes)and typed(output_mix,())and zero(output_mix)and all(typed(x,())for x in [person,skin,sky])


@dataclass(frozen=True)
class Inputs:
    rgb: V
    person: V
    skin: V
    sky: V
    texture: object
    offsets: tuple
    amplitudes: V
    output_mix: V

    def __post_init__(self):
        if not supported(self.rgb,self.person,self.skin,self.sky,self.texture,self.offsets,self.amplitudes,self.output_mix):raise DomainUnknown('Exact whole-set neutral selective contract not met')


def gamma_n(e,n):return (1+e)**n-1

def interval_matrix(a,lo,hi):
    return np.maximum(a,0)@lo+np.minimum(a,0)@hi,np.maximum(a,0)@hi+np.minimum(a,0)@lo


def polar_error(a_max,b_max):
    r=math.hypot(a_max,b_max)
    # dot(h,h): two products and one sum. sqrt/H angles retain4u budget.
    rel=(1+EH)**2-1;t=(3+2*EH)*TH
    erel=max(math.sqrt(1+rel)*(1+ETH)-1,1-math.sqrt(1-rel)*(1-ETH))
    er=r*erel+(1+ETH)*math.sqrt(t)+TH
    ea=ETH*math.pi+TH;etrig=ETH+TH
    product_error=EH*(r+er)*(1+etrig)+TH
    coordinate_error=er+r*ea+(r+er)*etrig+product_error
    return coordinate_error,{'ideal_radius_max':r,'dot_relative_allowance':rel,'dot_absolute_allowance':t,'radius_error':er,'angle_error':ea,'trig_error':etrig,'product_error':product_error,'ab_roundtrip_error':coordinate_error}


def half_box(lo,hi):
    # Bounds are in reals; native values at this boundary are half. Rounding
    # endpoints to half cannot exclude any half value inside the real bounds.
    if max(np.max(abs(lo)),np.max(abs(hi)))>65504:raise DomainUnknown('Neutral joint half finite domain exceeded')
    return V.bounds(lo,hi)


@dataclass(frozen=True)
class Result:
    source: V
    inverse_v: V
    inverse_root: V
    converted: V
    gamma: V
    proof: dict
    converted_gamma_covered_under_declared_budgets: bool=True
    original_GPU_verified: bool=False


def enclose(inputs: Inputs):
    if not isinstance(inputs,Inputs):raise TypeError('Validated neutral selective input contract required')
    rgb=inputs.rgb
    if not isinstance(rgb,V)or rgb.point or rgb.precision!='h'or rgb.lo.shape!=(3,):raise TypeError('Whole half RGB input set required')
    c=rgb.clamp();lo,hi=c.lo,c.hi
    # M has only positive entries, so its actual f32 graph admits a relative
    # bound even at zero (plus the existing absolute tiny term).
    ylo,yhi=interval_matrix(M,lo,hi);am=gamma_n(E32,5);tm=5*T32*(1+E32)**5
    rr=max((1+am)**POWER*(1+ET32)*(1+E32)-1,1-(1-am)**POWER*(1-ET32)*(1-E32))
    root_max=yhi**POWER;root_error=rr*root_max+(1+ET32)*(1+E32)*tm**POWER+(2+E32)*T32
    nround=gamma_n(E32,5)*(abs(N)@(root_max+root_error))+5*T32
    # A local input range has a real-reference root lower bound as well.
    # Keep it in N's cancellation bounds; the existing FP error remains
    # separate. For the old full[0,1]^3 contract this is exactly the old bound.
    root_min=ylo**POWER;nlo,nhi=interval_matrix(N,root_min,root_max)
    nfloat=abs(N)@root_error+nround
    lab_abs=np.maximum(abs(nlo),abs(nhi))+nfloat
    conversion_error=UH*lab_abs+2**-25
    lab_error=nfloat+conversion_error;actual_lab_abs=lab_abs+conversion_error
    epolar,pinfo=polar_error(actual_lab_abs[1],actual_lab_abs[2])
    polar_vec=np.array([0.,epolar,epolar])
    # P*N identity residual is kept explicitly. No original FP operation is
    # replaced by a matrix product: P,N rounding and Lab quantization remain.
    K=P@N;T=Q@M;bookkeeping=2e-12
    composition_error=abs(K-np.eye(3))@root_max+bookkeeping
    pround=gamma_n(E32,4)*(abs(P)@(actual_lab_abs+polar_vec))+4*T32
    ev=composition_error+abs(P)@(lab_error+polar_vec)+pround
    vlo=-ev;vhi=root_max+ev
    domain_radius=np.maximum(abs(vlo),abs(vhi));power_error=INVERSE_POWER*np.maximum(domain_radius,root_max)**(INVERSE_POWER-1)*ev+(ET32+E32+ET32*E32)*domain_radius**INVERSE_POWER+(2+E32)*T32
    exponent=POWER*INVERSE_POWER;exponent_error=[]
    for ymax in yhi:
        candidates=[0.,float(ymax)]
        if exponent!=1:
            critical=math.exp(-math.log(exponent)/(exponent-1))
            if 0<critical<ymax:candidates.append(critical)
        exponent_error.append(max(abs(x**exponent-x)for x in candidates))
    total_power_error=power_error+np.array(exponent_error)
    powerlo=ylo-total_power_error;powerhi=yhi+total_power_error
    qround=gamma_n(E32,5)*(abs(Q)@(np.maximum(abs(powerlo),abs(powerhi))))+5*T32
    error=abs(Q)@total_power_error+qround+bookkeeping
    # Shared source generators remain in the final nominal Q*M RGB map.
    source=[A.box(a,b)for a,b in zip(lo,hi)];converted=[]
    for row,e in zip(T,error):
        a=A.value(0)
        for weight,value in zip(row,source):a=a.add(value.scale(float(weight)))
        l,h=a.bounds();cast_error=UH*max(abs(l-e),abs(h+e))+2**-25
        converted.append((l-e-cast_error,h+e+cast_error))
    out=half_box(np.array([v[0]for v in converted]),np.array([v[1]for v in converted]));gamma=V.value(1,point=False)
    proof={'reference':'iPhone17,3/24A446 selectiveColorFilter SSA11..230','source_clamped_lo':lo.tolist(),'source_clamped_hi':hi.tolist(),'POWER':POWER,'INVERSE_POWER':INVERSE_POWER,'POWER_product':exponent,'M_relative_error':am,'root_error':root_error.tolist(),'Lab_float_error':nfloat.tolist(),'Lab_half_conversion_error':conversion_error.tolist(),'polar':pinfo,'P_times_N_identity_residual':(K-np.eye(3)).tolist(),'inverse_v_error':ev.tolist(),'inverse_power_error':power_error.tolist(),'exponent_mismatch_error':exponent_error,'Q_times_M':T.tolist(),'RGB_before_half_error':error.tolist(),'half_gamma_joint_value':1,'exact_constant_reasons':['zero texture sampling returns zero for all finite coordinates','four zero+1 values and same-value mixes give exact1 for saturation/luminosity/gamma','zero hue preserves angle; saturation1 preserves radius; luminosity1 preserves light','zero offset/amplitude makes both later Lab vectors the same live values'],'2u_4u_epsilon_mask_or_pow_domain_changed':False,'negative_endpoint_joint_reachability':'not established; this is an outer enclosure','matrix_composition_only_in_real_reference_error_proof':True}
    return Result(c,V.bounds(vlo,vhi,'f'),V.bounds(powerlo,powerhi,'f'),out,gamma,proof)
