"""S31 symbolic enclosure checks and exact-rational constructive witnesses.

Floating evaluations generate boundary candidates only. Every reported
nonlinear witness is independently certified with integer powers and RN-half.
No floating scan is used as the general reachable-range proof.
"""
from pathlib import Path
from fractions import Fraction as Q
import argparse,hashlib,json,re
import numpy as np
from baseline_archive import encoded,sha
from context_color_api import load
from leaf_numeric import V
from pixel_bright import forward as bright,BrightStats
from square132_contract import (CONSTANTS,RMAX,Assumptions,value,rn,mul,add,fma,
                                prefix,classify,low_segment)

R=Path(__file__).parent
E=R/'evidence'


def frac(q):return [q.numerator,q.denominator]


def freeze(output):
    if output.exists():raise FileExistsError(output)
    centers=[int(np.float16(x).view('u2'))for x in [.006,.06]]
    d={'scope':__doc__,'fixed_strength_half_bits':0x3c00,
       'fixed_witnesses':[{'name':'zero','c':0},{'name':'smallest_input_subnormal','c':1},
                          {'name':'normal_below_old_domain','c':0x1400},{'name':'upper_endpoint','c':0x3c00}],
       'boundary_candidate_windows':[{'center_half_bits':centers[0],'radius_half_encodings':128,'target_square_bits':[0x2bff,0x2c00,0x2c01]},
                                     {'center_half_bits':centers[1],'radius_half_encodings':128,'target_square_bits':[0x33ff,0x3400,0x3401]}],
       'mix_modes':['separate','fused'],'candidate_rule':'ascending input encoding; first predicted hit per target/mode, then exact rational verification; absence is window-only unknown',
       'candidate_prediction_not_general_proof':True,'general_proof':'symbolic monotone RN enclosure and exact rational constant inequalities',
       'full_helper_checks':'only four fixed witnesses, model-only; synthetic other channels and working inputs; no original calls',
       'native_kernel_or_compile_planned':False,'v3_or_whitelist_updates_planned':False}
    output.write_bytes(encoded(d));print(json.dumps({'frozen':True,'boundary_candidate_evaluations':1028,'fixed_full_helper_witnesses':4}))
    return d


def algebra():
    c={n:value(b)for n,b in CONSTANTS.items()};pmin=Q(7,128)
    checks={'positive_exponent_at_most_half':0<c['power_exponent']<=Q(1,2),
            'threshold_above_square_of_power_lower':c['encode_threshold']>pmin*pmin,
            'threshold_below_1over256':c['encode_threshold']<Q(1,256),
            'scale_above_one':c['encode_scale']>1,
            'linear_positive_below13':0<c['encode_linear']<13,
            'nonlinear_lower_fused_positive':value(rn(c['encode_scale']*pmin+c['encode_offset']))>0,
            'nonlinear_lower_separate_positive':value(add(mul(rn(pmin),CONSTANTS['encode_scale']),CONSTANTS['encode_offset']))>0,
            'linear_upper_below_encode_max':value(rn(c['encode_linear']*c['encode_threshold']))<=value(RMAX),
            'encode_max_strictly_below1':0<value(RMAX)<1,
            'weight_in_unit_interval':0<c['weight_factor']<c['weight_cap']<1,
            'weight_below_three_eighths':c['weight_cap']<Q(3,8),
            'nonlinear_lower_above_minimum_positive_reference':value(rn(c['encode_scale']*pmin+c['encode_offset']))>=value(mul(1,CONSTANTS['encode_linear'])),
            'half_constants_decode_without_manual_translation':value(0x4c00)==16 and value(0xca00)==-12 and value(0x4400)==4}
    assert all(checks.values())
    return {'exact_constants':{n:{'half_bits':CONSTANTS[n],'rational':frac(x)}for n,x in c.items()},
            'constant_inequalities':checks,'power_branch_lower_rational':frac(pmin),
            'reference_upper_bits':RMAX,'reference_upper_rational':frac(value(RMAX)),
            'minimum_positive_linear_reference_bits':mul(1,CONSTANTS['encode_linear']),
            'finite_prerequisites':['clamped RGB canonical finite half in[0,1]',
                                    'stats/exposure conversions, ratio and other strength intermediates finite',
                                    'RN-even and monotone finite arithmetic; subnormal witnesses require gradual underflow',
                                    'nonlinear half power in[7/128,1]; implied by correctly RN-quantized real c^alpha, not asserted for arbitrary GPU pow'],
            'strength_steps':['clamped spread and ev in[0,1]; factor=min(spread,ev) in[0,1]',
                              'base=half(clamp(4*ratio-9,1,3)) in[1,3]',
                              'half(max(1,(3*factor+1)*base)) in[1,12] by monotone f32/half RN and exact endpoints',
                              'weight=clamp(half(strength*half0x2e66),0,half0x359a) in[B,W] subset[0,1]'],
            'reference_steps':['linear: c>=0 -> RN(L*c)>=0; c<=t -> RN(L*c)<=RN(L*t)<=Rmax',
                               'nonlinear: alpha<=1/2 and c>t>(7/128)^2 imply real c^alpha>7/128',
                               'under stated power quantization condition, P in[7/128,1]; monotone scale/offset RN gives0<reference<=Rmax',
                               'sign(c)=1 for c>0 and canonical+0 for c=0; reference in[0,Rmax], Rmax=RN(A+C)<1'],
            'square_steps':['r in[0,Rmax] subset[0,1]; u=RN(r*r) in[0,r] by monotone RN and RN(r)=r',
                            'd=RN(u-r) in[-r,0]',
                            'separate mix: v=RN(d*w) in[d,0], so RN(r+v) in[0,r]',
                            'fused mix: exact r+d*w in[0,r], so RN(r+d*w) in[0,r]',
                            'therefore square132 in[0,Rmax] for both stated mix contracts; endpoint witnesses make this an attained outer hull, not all interior values attainable'],
            'proof_grade':'reviewable quantified monotonic-rounding derivation plus exact-rational inequality checks; not a formal theorem-prover or originalGPU proof'}


def static_binding():
    old=load(E/'bright-detail-s25c.json');file=R.parents[1].parent/old['private_storage_relative_to_task']/'inputs/trace.ll'
    assert sha(file)==old['actual_compiler_inputs']['inputs/trace.ll']['sha256']
    text=file.read_text();body=next(m[0]for m in re.finditer(r'^define[^\n]*@([^ (]+)\([^\n]+\{\n.*?^}',text,re.M|re.S)if'renderBrightAndContrast'in m[1])
    ids=set(range(45,59))|set(range(104,113))|set(range(127,141))
    rows={int(m[1]):m[0]for l in body.splitlines()if(m:=re.match(r'\s*%(\d+) =.*',l))and int(m[1])in ids}
    assert set(range(127,141))<=rows.keys()and 'ole' in rows[139]and'0xH3400'in rows[139]
    return {'actual_saved_trace_IR_sha256':sha(file),'SSA_line_sha256':{str(i):hashlib.sha256(l.encode()).hexdigest()for i,l in sorted(rows.items())},
            'original_relation139':'ordered <= half0x3400; equality selects low138 at140',
            'source_reference':'112=encode(saturate(rgb7));129=112*112;128=clamp(58*half0x2e66,0,half0x359a);132=mix(112,129,128)',
            'CPU_machine_134_138_map_sha256':sha(E/'bright-machine-map-s29e2.json'),
            'mix_rounding_scope':'derive both subtraction+separate and subtraction+FMA contracts; fast-math does not establish all originalGPU implementations',
            'v3_point_source_sha256':sha(R/'pixel_bright.py')}


def predicted_candidates(plan):
    alpha=float(value(CONSTANTS['power_exponent']));A=float(value(CONSTANTS['encode_scale']));C=float(value(CONSTANTS['encode_offset']));w=float(value(CONSTANTS['weight_factor']))
    candidates=[];missing=[];count=0
    for window in plan['boundary_candidate_windows']:
        center=window['center_half_bits'];radius=window['radius_half_encodings']
        codes=np.arange(center-radius,center+radius+1,dtype='u2');c=codes.view('f2').astype('f8')
        p=np.power(c,alpha).astype('f2').astype('f8');r=(p*A+C).astype('f2').astype('f8');u=(r*r).astype('f2').astype('f8');d=(u-r).astype('f2').astype('f8')
        for mode in plan['mix_modes']:
            x=(r+(d*w).astype('f2').astype('f8')).astype('f2')if mode=='separate'else(r+d*w).astype('f2')
            count+=len(codes)
            for target in window['target_square_bits']:
                found=np.flatnonzero(x.view('u2')==target)
                if len(found):candidates.append({'name':'boundary_'+hex(target),'c':int(codes[found[0]]),'mode':mode,'target_square':target})
                else:missing.append({'target_square':target,'mode':mode,'scope':'not found in frozen window; no general unreachability claim'})
    return candidates,missing,count


def run(plan_file,output):
    if output.exists():raise FileExistsError(output)
    plan=load(plan_file);proof=algebra();binding=static_binding();candidates,missing,count=predicted_candidates(plan)
    cases=[{**x,'mode':mode}for x in plan['fixed_witnesses']for mode in plan['mix_modes']]+candidates
    witnesses=[]
    for case in cases:
        record=prefix(case['c'],plan['fixed_strength_half_bits'],Assumptions(True,True,case['mode']))
        if 'target_square'in case:assert record['square132']==case['target_square'],'Candidate did not survive exact power/RN verification'
        witnesses.append({**case,'exact_prefix':record,'classification':classify(record['square132']),
                          'low_segment':low_segment(record['square132'],Assumptions(True,True,case['mode'])),
                          'reachability_grade':'constructive helper-prefix input under declared IEEE/power conditions; not fixed-source or originalGPU reachability'})
    context=load(E/'second-context-s25a.json');stats=np.array(context['raw_f32_bits']['stats'],dtype='u4').view('f4')
    stat=lambda g,k:V.value(stats[2560+g*9+k],'f')
    bs=BrightStats(stat(2,4),stat(3,4),stat(5,0),stat(6,6),stat(6,4));checks=[]
    for case in plan['fixed_witnesses']:
        rgb=V.value([float(value(case['c'])),.3,.6]);obs={}
        out=bright(rgb,V.value([.2,.3,.4]),V.value(.4),V.value(.3),V.value(.8),bs,observations=obs)
        s=int(obs[58].lo.astype('f2').view('u2'));r=int(obs[112].lo.astype('f2').view('u2')[0]);x=int(obs[132].lo.astype('f2').view('u2')[0])
        exact=prefix(case['c'],s,Assumptions(True,True,'separate'))
        assert s==0x3c00 and r==exact['reference112']and x==exact['square132']
        checks.append({'name':case['name'],'rgb_input_half_bits':rgb.lo.astype('f2').view('u2').tolist(),
                       'other_inputs':'working(.2,.3,.4),person.4,skin.3,exposure.8; fixed raw S25 stats',
                       'strength58_half_bits':s,'reference112_half_bits':r,'square132_half_bits':x,
                       'full_existing_model_helper_finite':bool(np.isfinite(out.lo).all()),
                       'grade':'existing v3 helper model construction, no original host/GPU'})
    endpoint=next(w for w in witnesses if w['name']=='upper_endpoint')
    zero=next(w for w in witnesses if w['name']=='zero')
    assert endpoint['exact_prefix']['square132']==RMAX and zero['exact_prefix']['square132']==0
    selected=[]
    for x in [0,1,0x03ff,0x0400,0x2bff,0x2c00,0x2c01,0x33ff,0x3400,0x3401,RMAX,0x3c00]:
        selected.append(classify(x))
    d={'status':'conditional_symbolic_domain_derivation_with_exact_constructive_witnesses',
       'plan_sha256':sha(plan_file),'symbolic_derivation':proof,'static_binding':binding,
       'witnesses':witnesses,'window_only_unknown_boundary_searches':missing,'old_leaf_and_branch_classifications':selected,
       'full_existing_helper_model_checks':checks,
       'generally_proved_outer_hull_half_bits':[0,RMAX],
       'all_interior_half_values_claimed_reachable':False,
       'old_S29_leaf':'covers selected low inputs square in[1/16,1/4]; for square>1/4 low is not selected; below1/16 actual prefix witnesses exist and old leaf must remain unknown',
       'reachability_layers':['quantified symbolic conditional outer hull','exact rational prefix witness',
                              'four existing v3 full-helper model witnesses','fixed-source/originalGPU reachability unverified'],
       'native_pow_sqrt_FPCR_or_GPU_certified':False,'v3_or_S29_whitelist_modified':False,
       'cost':{'floating_boundary_candidate_prefix_evaluations':count,'candidate_search_is_not_proof':True,
               'exact_rational_witnesses':len(witnesses),'new_full_existing_helper_model_calls':4,
               'new_full_pipeline_calls':0,'new_original_kernel_calls':0,'new_native_compilations':0},
       'source_sha256':{n:sha(R/n)for n in ['square132_contract.py','prove_square132.py','pixel_bright.py','pixel_skin.py','leaf_numeric.py']}}
    output.write_bytes(encoded(d));print(json.dumps({'status':d['status'],'outer_hull':[0,RMAX],
       'exact_witnesses':len(witnesses),'unresolved_window_targets':missing,
       'fixed_witness_square_bits':[(c['name'],c['square132_half_bits'])for c in checks],
       'new_model_helpers':4,'new_kernels':0}))
    return d


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['freeze','prove']);p.add_argument('first',type=Path);p.add_argument('second',type=Path,nargs='?')
    a=p.parse_args()
    if a.mode=='freeze':freeze(a.first)
    else:run(a.first,a.second)
