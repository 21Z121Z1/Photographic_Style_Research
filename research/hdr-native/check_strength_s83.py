"""Synthetic structural checks for a new control; no Apple/photo proof."""
from pathlib import Path
import os,json,hashlib,subprocess,sys
import numpy as np
from semantic_strength_s82 import apply
O=Path(os.environ['W'])/'out'
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
source=Path(__file__).with_name('semantic_strength_s82.py')
frozen={'source_sha256':sha(source),'checks_sha256':sha(__file__),'scope':'Synthetic robustness, chunk invariance and additive counterfactual residual cancellation only. No photos, captured Apple PSO, global/local inverse or scene accuracy.','seed':2026102083,'strengths':[0,.25,.5,.75,1],'os_build_required':'26A434'}
(O/'freeze.json').write_text(json.dumps(frozen,indent=2)+'\n')
assert subprocess.check_output(['sw_vers','-buildVersion'],text=True).strip()=='26A434'
rng=np.random.default_rng(frozen['seed']);a=rng.uniform(.02,2,(128,192,3)).astype('f4');full=(a*.7).astype('f4');neutral=(full+.04*rng.normal(size=a.shape)).astype('f4')
before=[hashlib.sha256(x.tobytes()).hexdigest()for x in [a,full,neutral]]
for x in [a,full,neutral]:x.flags.writeable=False
rows=[]
for strength in frozen['strengths']:
    q=apply(a,full,neutral,strength);reference=q['rgb'];max_diff=0;chunk_error=0
    for blocksize in [1,17,31,64,97]:
        blocks=[apply(a[y:y+blocksize],full[y:y+blocksize],neutral[y:y+blocksize],strength)['rgb']for y in range(0,len(a),blocksize)]
        joined=np.concatenate(blocks);different=int(np.count_nonzero(reference.view('u4')!=joined.view('u4')));max_diff=max(max_diff,different);chunk_error=max(chunk_error,float(abs(reference-joined).max()));assert chunk_error<=1e-6
    if strength==0:assert np.array_equal(reference.view('u4'),a.view('u4'))
    restored=reference.astype('f8')*np.exp2(-q['log2_gain']);restored[~q['ratio_valid']]=reference[~q['ratio_valid']]
    rows.append({'strength':strength,'chunk_storage_differences_diagnostic_only':max_diff,'chunk_max_abs':chunk_error,'synthetic_chunk_guard':1e-6,'self_consistency_max_abs':float(abs(restored-a).max()),'valid_pixels':int(q['ratio_valid'].sum())})
assert before==[hashlib.sha256(x.tobytes()).hexdigest()for x in [a,full,neutral]]

# Known additive target: shared reconstruction error cancels without knowing x.
x=rng.uniform(.1,.8,(64,96,3));delta=np.array([.02,-.03,.05]);observed=x+delta;guess=x*.6
q=apply(observed,guess+delta,guess,1);additive_error=float(abs(q['rgb']-x).max());assert additive_error<1e-14

b=np.array([[0.,-0.,-1.],[1.,2.,3.],[np.nan,1.,1.],[np.inf,1.,1.]],'f4');f=np.ones_like(b);n=f.copy();n[1]=0
q=apply(b,f,n,.5);assert not q['ratio_valid'][[0,2,3]].any();assert np.array_equal(q['rgb'][0].view('u4'),b[0].view('u4'));assert np.isnan(q['rgb'][2,0])and np.isposinf(q['rgb'][3,0])
wide=apply(np.array([[1e-300,1e-250,1e-200]]),np.zeros((1,3)),np.array([[1e300,1e250,1e200]]),.5);wide_error=float(abs(wide['rgb']-1).max());assert wide_error<1e-12

rejected=[]
for name,args in [
    ('mismatched_shape',(a,full[:1],neutral,.5)),
    ('nonfinite_strength',(a,full,neutral,float('nan'))),
    ('negative_strength',(a,full,neutral,-.1)),
    ('too_large_strength',(a,full,neutral,1.1)),
    ('half_base_rejected',(a.astype('f2'),full,neutral,.5)),
    ('oversize_tile',(np.zeros((513,512,3),'f4'),)*3+(.5,)),
]:
    try:apply(*args)
    except ValueError:rejected.append(name)
    else:raise AssertionError('Missing input guard: '+name)
huge=np.full((1,3),np.finfo('f4').max,'f4')
try:apply(huge,-huge,huge,1)
except FloatingPointError:rejected.append('float32_output_overflow')
else:raise AssertionError('Output dtype overflow was not rejected')
assert sha(source)==frozen['source_sha256']
report={'os_build':'26A434','image_version':os.environ.get('ImageVersion'),'python':sys.version.split()[0],'numpy':np.__version__,'scope':frozen['scope'],'rows':rows,'readonly_inputs_SHA_unchanged':True,'known_additive_cancel_max_abs':additive_error,'wide_range_intermediate_overflow_avoided_max_abs':wide_error,'invalid_domain_preserves_base_and_mask':True,'rejected_bad_inputs':rejected,'synthetic_structural_checks_pass':True,'new_photos':0,'new_native_Apple_pixel_execution':False,'engineering_accepted':False,'A_phase_complete':False,'acceptance_complete':False}
(O/'analysis.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');print(json.dumps({'synthetic_structural_checks_pass':True,'chunk_max_abs':max(r['chunk_max_abs']for r in rows),'bad_input_guards':len(rejected),'new_photos':0,'engineering_accepted':False}))
