"""Runner-only saved-data audit. No native search and no new estimator tuning."""
from pathlib import Path
import json,sys,hashlib,struct
import numpy as np
from PIL import Image
P,A,B,O=map(Path,sys.argv[1:]);O.mkdir(exist_ok=True);H,W=384,512
OPS=['skin-color','skin-brightness','skin-both']
def load(p,c=4,d='f2'):return np.fromfile(p,d).reshape(H,W,c)[...,:3].astype('f8')
def save(p,x):p.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
y=load(P/'native.f16');source=load(P/'texture-0.bin');rtA=load(A/'native/new-roundtrip.f16');rtB=load(B/'native/new-roundtrip.f16')
eligible=np.isfinite(y).all(-1)&(y>1/255).all(-1);assert eligible.sum()==186949
dt=np.dtype([('point','<u4'),('family','<u2'),('x','<f2',(3,)),('ys','<f2',(4,3))],align=False)
def read_records(root,phase):
    f=json.loads((root/'native'/('s'+phase+'-results.json')).read_text());records=np.memmap(root/'native/finite-candidates.bin',dtype=dt,mode='r');out={};pos=0
    for row in f['points']:
        count=row['candidate_count'];out[row['point']]=records[pos:pos+count];pos+=count
    assert pos==len(records);return out,f
recA,fA=read_records(A,'14');recB,fB=read_records(B,'16')
assert all(x['batch_control_half_mismatches']==0 for f in [fA,fB] for x in f['points'])
facts=json.loads((A/'analysis/finite-domain-intervals.private.json').read_text());by={r['point']:r for r in facts}
est=[y+load(A/'native'/(op+'-new-neutral.f16'))-rtA for op in OPS]
for point,row in by.items():
    r,c=divmod(point,W)
    for op,v in enumerate(row['domains'][0]['intervals']):
        if not v.get('empty'):
            lo=np.asarray(v['lower']);hi=np.asarray(v['upper']);est[op][r,c]=np.divide(2*lo*hi,lo+hi,out=(lo+hi)*.5,where=(lo+hi)!=0)
newfacts=json.loads((B/'analysis/finite-domain-intervals.private.json').read_text())
for row in newfacts:
    point=row['point'];r,c=divmod(point,W)
    for op,v in enumerate(row['domains'][0]['intervals']):
        if v.get('empty'):continue
        lo=np.asarray(v.get('union_with_previous_lower',v['lower']));hi=np.asarray(v.get('union_with_previous_upper',v['upper']))
        est[op][r,c]=np.divide(2*lo*hi,lo+hi,out=(lo+hi)*.5,where=(lo+hi)!=0)
for op,value in zip(OPS,est):
    with np.load(B/'analysis'/(op+'-interval-estimate.npz')) as z:assert np.array_equal(z['rgb'],value.astype('f4'))
original_points=np.zeros((H,W),bool);nonunique=np.zeros((3,H,W),bool);ambiguous=np.zeros_like(nonunique);inside=np.ones_like(nonunique)
truths=[load(P/(op+'-removed-oracle.f16')) for op in OPS]
perpoint=[];witnesses=[];root_counts=[]
for point in sorted(recA):
    r,c=divmod(point,W);original_points[r,c]=True
    arrays=[recA[point]]+([recB[point]] if point in recB else [])
    rec=np.concatenate(arrays);match=np.all(rec['ys'][:,0,:]==y[r,c],-1);independent=match&(rec['family']<4)
    roots=rec[match];ind=rec[independent];assert len(ind)>0
    original_in_independent=bool(np.any(np.all(ind['x']==source[r,c],-1)))
    truth_input_in_any=bool(np.any(np.all(roots['x']==source[r,c],-1)));assert truth_input_in_any
    root_counts.append(len(np.unique(ind['x'].view('u2'),axis=0)));ops=[]
    for op in range(3):
        values=roots['ys'][:,op+1,:].astype('f8');lo=values.min(0);hi=values.max(0)
        lbv=np.divide(hi-lo,hi+lo,out=np.zeros(3),where=lo>0);lb=float(lbv.max());nonunique[op,r,c]=lb>1e-3;ambiguous[op,r,c]=bool((hi!=lo).any())
        v=ind['ys'][:,op+1,:].astype('f8');il=v.min(0);iu=v.max(0);expected=truths[op][r,c]
        inside[op,r,c]=bool(np.all((expected>=il)&(expected<=iu)))
        error=float(np.max(abs(est[op][r,c]-expected)/np.maximum(abs(expected),1e-12)))
        ops.append({'operator':OPS[op],'finite_union_lower':lo.tolist(),'finite_union_upper':hi.tolist(),'relative_minimax_global_lower_bound':lb,'estimate_relative_error_against_oracle':error,'oracle_inside_independent_local_hull':bool(inside[op,r,c]),'global_upper_bound_certified':False,'unique_neutral_outputs_in_union':len(np.unique(values,axis=0))})
        if lb>1e-3:
            channel=int(lbv.argmax());i=int(values[:,channel].argmin());j=int(values[:,channel].argmax())
            witnesses.append({'point':point,'operator':OPS[op],'channel':channel,'x_low':roots['x'][i].astype('f8').tolist(),'x_high':roots['x'][j].astype('f8').tolist(),'y_actual_identical':y[r,c].tolist(),'neutral_low':values[i].tolist(),'neutral_high':values[j].tolist(),'relative_minimax_lower_bound':lb,'source_records':['S15','S16'],'whole_image_context_fixed':True})
    perpoint.append({'point':point,'independent_exact_unique_roots':root_counts[-1],'original_in_independent_roots':original_in_independent,'original_in_diagnostic_or_independent_roots':truth_input_in_any,'operations':ops})
matte=np.fromfile(P/'texture-11.bin','f2').reshape(H,W).astype('f8');pad=np.pad(matte,1,mode='edge');mx=np.maximum.reduce([pad[a:a+H,b:b+W] for a in range(3) for b in range(3)]);mn=np.minimum.reduce([pad[a:a+H,b:b+W] for a in range(3) for b in range(3)]);edge=(mx-mn)>1/255
def metrics(a,b,mask):
    d=abs(a-b);q=np.max(d/np.maximum(abs(b),1e-12),-1)
    return {'pixels':int(mask.sum()),'coverage':float(mask.mean()),'max_abs':float(d[mask].max()),'max_relative':float(q[mask].max()),'failed_gt_1e3_float64':int(np.count_nonzero(mask&(q>1e-3))),'psnr_db':float(-10*np.log10(np.mean(d[mask]**2))) if d[mask].any() else 'inf'}
rows=[];masks={};lum=lambda a:a@np.array([.22897456,.69173852,.07928691])
for oi,(op,value) in enumerate(zip(OPS,est)):
    expected=load(P/(op+'-removed-oracle.f16'));rel=np.max(abs(value-expected)/np.maximum(abs(expected),1e-12),-1);failed=eligible&(rel>1e-3)
    masks[op+'_failed']=failed;masks[op+'_global_nonunique_gt_threshold']=nonunique[oi]
    valid=eligible&(lum(value)>0)&(lum(expected)>0);ev=np.zeros((H,W));ev[valid]=np.log2(lum(value)[valid]/lum(expected)[valid])
    dx=abs(np.diff(ev,axis=1));dy=abs(np.diff(ev,axis=0));rx=(edge[:,1:]|edge[:,:-1])&valid[:,1:]&valid[:,:-1];ry=(edge[1:]|edge[:-1])&valid[1:]&valid[:-1];grad=np.r_[dx[rx],dy[ry]]
    rows.append({'operator':op,'S16_f64_reconstruction':metrics(value,expected,eligible),'S16_export_f32':metrics(value.astype('f4').astype('f8'),expected,eligible),'remaining_failed':int(failed.sum()),'remaining_failed_with_impossibility_witness':int((failed&nonunique[oi]).sum()),'remaining_failed_without_impossibility_witness':int((failed&~nonunique[oi]).sum()),'all_296_with_impossibility_witness':int(nonunique[oi].sum()),'all_296_with_some_output_nonuniqueness':int(ambiguous[oi].sum()),'all_296_without_observed_nonuniqueness':int((original_points&~ambiguous[oi]).sum()),'oracle_outside_independent_local_hull':int((original_points&~inside[oi]).sum()),'remaining_failed_with_oracle_outside_local_hull':int((failed&~inside[oi]).sum()),'remaining_failed_on_matte_edge':int((failed&edge).sum()),'remaining_failed_interior':int((failed&~edge).sum()),'outside_skin_footprint_max_change':float(abs(value[mx==0]-y[mx==0]).max()),'error_ev_gradient_on_matte_edge_p99':float(np.quantile(grad,.99)),'error_ev_gradient_on_matte_edge_max':float(grad.max()),'max_possible_lower_bound_from_witnesses':max(p['operations'][oi]['relative_minimax_global_lower_bound'] for p in perpoint)})
    color=np.zeros((H,W,3),dtype='u1');color[nonunique[oi]]=[255,170,0];color[failed]=[255,0,0];Image.fromarray(np.rot90(color,3)).save(O/(op+'-uncertainty-mask.png'))
np.savez_compressed(O/'classification-masks.private.npz',**masks,original_points=original_points,matte_edge=edge,near_black_or_nonfinite=~eligible)
roi=(P/'bytes-5.bin').read_bytes();param=(P/'buffer-1.bin').read_bytes();color=(P/'bytes-0.bin')
origin=struct.unpack_from('<2H',roi,160);input_map=struct.unpack_from('<4f',roi,16)
actual_map_expected=tuple(float(x) for x in np.asarray([1/W,1/H,0,0],dtype='f4'))
assert input_map==actual_map_expected and origin==(0,0)
preview_checks=[]
for label,root,fn in [('S15',A,'s14-analysis.json'),('S16',B,'s16-analysis.json')]:
    ff=json.loads((root/'analysis'/fn).read_text());checks=ff['preview_integrity'];assert all(c['before']==c['after'] for c in checks)
    preview_checks.append({'phase':label,'checks':len(checks),'failed':0,'manifest_and_inputs_checked':True})
report={'os_build':'26A434','no_new_native_search':True,'source_runs':[39139035394,39161546771,39162035138],'original_eligible_pixels':int(eligible.sum()),'original_coverage':float(eligible.mean()),'threshold_unchanged':1e-3,'original_296_points':int(original_points.sum()),'independent_exact_preimage_found_at_all_296':True,'exact_full_F_roundtrip_on_296':metrics(rtB,y,original_points),'full_native_roundtrip_all_eligible_still':metrics(rtB,y,eligible),'rows':rows,'original_input_seen_among_independent_candidates':sum(p['original_in_independent_roots'] for p in perpoint),'unique_independent_roots_min':min(root_counts),'unique_independent_roots_max':max(root_counts),'captured_primary_input_map':list(input_map),'output_origin':list(origin),'captured_SSR_cast_u32':struct.unpack_from('<I',param)[0],'preview_integrity':preview_checks,'global_hull_certified':False,'analysis_domain':'Union of all declared S15 cubes and S16 cubes for refined47. Exact native feasible roots, both independent and diagnostic. Does not certify absent roots outside these finite domains.','classification_limits':{'parameter_identification':'theta9/10 and other consumer parameters fixed and known; original capture decomposition not identified.','matte_edge':'Association only, fixed mattes and zero spatial coupling control; cannot call all edge failures matte errors.','quantization':'Original native half-valued map demonstrably many-to-one; which internal rounding/clamp/fold produces each collision is not established.','model_omission':'Original native PSO used. These failures do not establish an omitted forward operator; inverse root selection/domain is still incomplete.'}}
save(O/'s17-audit.json',report);save(O/'per-point-classification.private.json',perpoint);save(O/'all-impossibility-witnesses.private.json',witnesses)
