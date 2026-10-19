"""Small exact scalar checks; no image compute, safe in local memory scope."""
from pathlib import Path
from fractions import Fraction as Q
import sys,json,hashlib,math
sys.path.insert(0,str(Path(__file__).parent))
from spatial_curve_retarget import retarget_curve_point
O=Path(sys.argv[1]);O.mkdir(parents=True,exist_ok=True)
X=[Q(0),Q(1,2),Q(1)];F=[[Q(0),Q(1,2),Q(1)],[Q(0),Q(1,4),Q(1)]];G=[X,X];rows=[]
for weight in [Q(0),Q(1,4),Q(1,2),Q(3,4),Q(1)]:
 y=(1-weight)*Q(1,2)+weight*Q(1,4)
 r=retarget_curve_point(y,X,F,G,[1-weight,weight],coordinate_space='Declared synthetic scalar coordinate')
 assert r['neutral_lower']<=.5<=r['neutral_upper'] and r['candidate']==.5 and r['guaranteed_1e3']
 rows.append({'weight_second':str(weight),'observed':str(y),'expected':.5,'result':r})
# Counterexample to blending per-curve inverses: at x=.5, mixed y=3/8.
 correct=retarget_curve_point(Q(3,8),X,F,G,[Q(1,2),Q(1,2)],coordinate_space='Declared synthetic scalar coordinate')
 separate=[retarget_curve_point(Q(3,8),X,[f],[X],[1],coordinate_space='Declared synthetic scalar coordinate')['candidate'] for f in F]
 wrong=sum(separate)/2;assert abs(wrong-.5)/.5>1e-3 and correct['candidate']==.5
 plateau=retarget_curve_point(Q(1,2),[0,Q(1,4),Q(3,4),1],[[0,Q(1,2),Q(1,2),1]],[[0,Q(1,4),Q(3,4),1]],[1],coordinate_space='Declared synthetic scalar coordinate')
 assert plateau['plateau'] and not plateau['guaranteed_1e3'] and plateau['candidate'] is None and plateau['neutral_lower']==.25 and plateau['neutral_upper']==.75
 low=retarget_curve_point(0,X,[X],[X],[1],coordinate_space='Declared synthetic scalar coordinate');high=retarget_curve_point(1,X,[X],[X],[1],coordinate_space='Declared synthetic scalar coordinate')
 assert low['input_lower']==-math.inf and high['input_upper']==math.inf
 outside=retarget_curve_point(2,X,[X],[X],[1],coordinate_space='Declared synthetic scalar coordinate');assert not outside['valid']
 nonfinite=retarget_curve_point(math.nan,X,[X],[X],[1],coordinate_space='Declared synthetic scalar coordinate');assert not nonfinite['valid']
 try:retarget_curve_point(.5,X,F,G,[1,-1],coordinate_space='Declared synthetic scalar coordinate')
 except ValueError:pass
 else:raise AssertionError('Negative spatial weights must be rejected')
 report={'execution':'Linux VM, small exact-rational scalar tests only, no image compute','cases':len(rows)+6,'all_pass':True,'same_observation_correct_inverse':correct['candidate'],'blend_separate_inverses':wrong,'blend_separate_inverse_relative_error':abs(wrong-.5)/.5,'plateau_neutral_interval':[plateau['neutral_lower'],plateau['neutral_upper']],'old_1e3_threshold_modified':False,'camera_inverse_verified':False,'full_consumer_domain_certified':False,'curve_application_order_confirmed_on_camera':False,'model_sha256':hashlib.sha256((Path(__file__).parent/'spatial_curve_retarget.py').read_bytes()).hexdigest(),'rows':rows}
with (O/'spatial-curve-scalar-tests.json').open('x') as f:json.dump(report,f,indent=2,allow_nan=False);f.write('\n')
print(json.dumps({k:v for k,v in report.items() if k!='rows'}))
