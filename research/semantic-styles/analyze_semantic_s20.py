"""Runner-only independent rational certificate for native whole-frame witnesses."""
from pathlib import Path
from fractions import Fraction as Q
import sys,json,hashlib
import numpy as np
P,W,O=map(Path,sys.argv[1:]);O.mkdir(exist_ok=True)
witness=json.loads(W.read_text());facts=json.loads((P/'s20-results.json').read_text());assert facts['full_frame_witness_replay_pass'] and not facts['context_mismatches']
def load(name):return np.fromfile(P/name,'<f2').reshape(384,512,4)[...,:3]
def ratio(x):return Q.from_float(float(x))
epsilon=Q(1,1000);details=[];rows=[]
for op,want in [('skin-color',6),('skin-brightness',29),('skin-both',35)]:
 a=load(op+'-neutral-0.f16');b=load(op+'-neutral-1.f16');ya=load(op+'-observed-0.f16');yb=load(op+'-observed-1.f16');assert np.array_equal(ya.view('u2'),yb.view('u2'))
 selected=[w for w in witness if w['operator']==op];assert len(selected)==want
 margins=[];lbs=[]
 for w in selected:
  r,c=divmod(w['point'],512);channel=w['channel'];a0=ratio(a[r,c,channel]);b0=ratio(b[r,c,channel]);lo,hi=sorted([a0,b0]);assert lo>0
  lower=hi*(1-epsilon);upper=lo*(1+epsilon);margin=lower-upper;assert margin>0
  lb=(hi-lo)/(hi+lo);assert lb>epsilon
  # S17 payloads are exact dyadic representations of native stored half values.
  assert np.array_equal(a[r,c],np.asarray(w['neutral_low'],'f2')) and np.array_equal(b[r,c],np.asarray(w['neutral_high'],'f2'))
  details.append({'operator':op,'point':w['point'],'channel':channel,'a':[lo.numerator,lo.denominator],'b':[hi.numerator,hi.denominator],'epsilon':[1,1000],'minimax_lower_bound':[lb.numerator,lb.denominator],'disjoint_success_intervals_margin':[margin.numerator,margin.denominator],'observed_full_frames_bit_identical':True,'global_safe_finite_output_outer':[-65504,65504],'nonfinite_alternatives_not_excluded':True,'tight_global_hull_certified':False})
  margins.append(float(margin));lbs.append(float(lb))
 rows.append({'operator':op,'certified_points':want,'full_frame_observation_half_mismatches':0,'empty_intersection_of_allowed_1e3_estimates':want,'exact_rational_lower_bound_min':min(lbs),'exact_rational_lower_bound_max':max(lbs),'minimum_disjoint_interval_gap':min(margins),'threshold_changed':False,'point_recovery_guarantee_possible':False})
(O/'exact-certificates.private.json').write_text(json.dumps(details,indent=2)+'\n')
report={'source_build':'26A434','scope':'Full observed images exactly equal for two original-native preimages; different native neutralized outputs. Exact rational success-interval contradiction, not floating threshold tuning.','rows':rows,'certificate_count':len(details),'strict_threshold':[1,1000],'old_acceptance_gate_pass':False,'point_inverse_guarantee_over_same_observation_alternatives':False,'global_tight_hull_certified':False,'unconditional_unknown_or_nonfinite_interval':[-float('inf'),float('inf')],'actual_original_frame_can_be_guessed_correctly':True,'warning':'Impossibility is a uniform guarantee over feasible alternatives. It does not prove no estimator can happen to match this fixed original. No original-camera amplitude is inferred.'}
# JSON encodes unbounded endpoints explicitly, never non-standard Infinity.
report['unconditional_unknown_or_nonfinite_interval']=['-inf','+inf']
(O/'s20-certificate-summary.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
print(json.dumps({'exact_native_full_frame_certificates':len(details),'all_threshold_intersections_empty':True,'threshold_unchanged':True}))
