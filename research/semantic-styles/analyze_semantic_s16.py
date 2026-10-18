"""macOS runner only. Full enumeration of declared local sets, not global hulls.

Truth-centred candidates are used only as diagnostics/nonuniqueness witnesses.
Neither root choice nor estimator uses the held original or its neutral output.
"""
from pathlib import Path
import sys, json, hashlib, os, struct
import numpy as np
from PIL import Image
import PyOpenColorIO as ocio
S,P,OLD,ALL,O=map(Path,sys.argv[1:]); O.mkdir(exist_ok=True)
OPS=['skin-color','skin-brightness','skin-both']; H,W=384,512
def load(p,c=4,d='f2'): return np.fromfile(p,d).reshape(H,W,c)[...,:3].astype('f8')
def dump(p,x): p.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def metrics(a,b,mask):
    diff=abs(a-b); rel=np.max(diff/np.maximum(abs(b),1e-12),-1); v=mask&np.isfinite(rel)
    if not v.any(): return {'pixels':0}
    lum=lambda x:x@np.array([.22897456,.69173852,.07928691])
    evmask=v&(lum(a)>0)&(lum(b)>0); ev=np.log2(lum(a)[evmask]/lum(b)[evmask])
    return {'pixels':int(v.sum()),'coverage':float(v.mean()),'max_abs':float(diff[v].max()),'max_relative':float(rel[v].max()),'failed_gt_1e3_float64':int(np.count_nonzero(v&(rel>1e-3))),'psnr_db':float(-10*np.log10(np.mean(diff[v]**2))) if diff[v].any() else 'inf','ev_mae':float(abs(ev).mean()) if ev.size else None,'ev_max_abs':float(abs(ev).max()) if ev.size else None}
cfg=ocio.Config.CreateFromBuiltinConfig('cg-config-v2.2.0_aces-v1.3_ocio-v2.4')
processor=cfg.getProcessor('Linear P3-D65','sRGB - Display','ACES 1.0 - SDR Video',ocio.TRANSFORM_DIR_FORWARD).getDefaultCPUProcessor()
integrity=[]
def preview(x,name):
    h=hashlib.sha256(x.tobytes()).hexdigest(); a=np.array(x,dtype='f4',order='C',copy=True)
    processor.apply(ocio.PackedImageDesc(a,W,H,3))
    im=Image.fromarray(np.rot90(np.round(np.clip(a,0,1)*255).astype('u1'),3)); im.thumbnail((512,512)); im.save(O/(name+'-ACES.png'))
    after=hashlib.sha256(x.tobytes()).hexdigest(); assert h==after
    integrity.append({'image':name,'before':h,'after':after,'unchanged':True})
context=json.loads((S/'s16-results.json').read_text()); assert not context['context_mismatches']
roi=(P/'bytes-5.bin').read_bytes(); input_map=struct.unpack_from('<4f',roi,16)
expected_map=tuple(float(x) for x in np.asarray([1/W,1/H,0,0],dtype='f4'))
assert input_map==expected_map, 'Packed native input map must equal captured identity map'
assert context['fresh_vs_S5']['half_differing_components']==0 and context['packed_sampler_basis_max_abs']==0
assert all(z['output_changes_outside_selected']==0 for z in context['spatial_controls'])
assert all(z['changed_bytes_outside_target']==0 for z in context['parameter_interventions'])
target=load(P/'native.f16'); rt=load(S/'new-roundtrip.f16'); oldrt=load(OLD/'new-roundtrip.f16')
eligible=np.fromfile(OLD/'original-eligible.u8','u1').reshape(H,W).astype(bool)
matte=np.fromfile(P/'texture-11.bin','f2').reshape(H,W).astype('f8'); pad=np.pad(matte,1,mode='edge')
hi=np.maximum.reduce([pad[a:a+H,b:b+W] for a in range(3) for b in range(3)])
lo=np.minimum.reduce([pad[a:a+H,b:b+W] for a in range(3) for b in range(3)])
edge=(hi-lo)>1/255; footprint=hi>0
dtype=np.dtype([('point','<u4'),('family','<u2'),('x','<f2',(3,)),('ys','<f2',(4,3))],align=False)
assert dtype.itemsize==36
records=np.memmap(S/'finite-candidates.bin',dtype=dtype,mode='r')
centred=[target+load(S/(op+'-new-neutral.f16'))-rt for op in OPS]
PREV=Path(os.environ['S16_PREVIOUS']); prior_points=json.loads((PREV/'analysis/finite-domain-intervals.private.json').read_text()); prior_by={e['point']:e for e in prior_points}
prev_rt=load(PREV/'native/new-roundtrip.f16'); baseline=[target+load(PREV/'native'/(op+'-new-neutral.f16'))-prev_rt for op in OPS]
assert np.array_equal(load(S/'start-roundtrip.f16'),prev_rt), 'S15 preimage replay must be unchanged before S16 search'
for entry in prior_points:
    row,col=divmod(entry['point'],W)
    for op,v in enumerate(entry['domains'][0]['intervals']):
        if not v.get('empty'):
            aa=np.asarray(v['lower']);bb=np.asarray(v['upper']);baseline[op][row,col]=np.divide(2*aa*bb,aa+bb,out=(aa+bb)*.5,where=(aa+bb)!=0)
interval_est=[a.copy() for a in baseline]
truths=[load(P/(op+'-removed-oracle.f16')) for op in OPS]
requested=np.zeros((H,W),bool); local_exact=np.zeros((H,W),bool)
impossible=np.zeros((3,H,W),bool); est_ambiguous=np.zeros_like(impossible); old_failed=[]
for op,truth in zip(OPS,truths):
    oldpred=target+load(OLD/(op+'-new-neutral.f16'))-oldrt
    old_failed.append(eligible&(np.max(abs(oldpred-truth)/np.maximum(abs(truth),1e-12),-1)>1e-3))
for entry in prior_points:
    row,col=divmod(entry['point'],W);local_exact[row,col]=entry['domains'][0]['exact_matches_including_duplicates']>0
    for op in range(3):
        v=entry['domains'][2]['intervals'][op];impossible[op,row,col]=v.get('relative_minimax_lower_bound',0)>1e-3
        v=entry['domains'][0]['intervals'][op];est_ambiguous[op,row,col]=v.get('relative_minimax_lower_bound',0)>1e-3
points=[]; examples=[]; pos=0; domain_counts=[]
for result in context['points']:
    point=result['point']; row,col=divmod(point,W); requested[row,col]=True
    assert result['batch_control_half_mismatches']==0 and result['local_union_enumerated_completely']
    count=result['candidate_count']; rec=records[pos:pos+count]; pos+=count
    assert len(rec)==count and np.all(rec['point']==point)
    match=np.all(rec['ys'][:,0,:]==target[row,col],-1); estimator=match&(rec['family']<4)
    diagnostic=match&(rec['family']==4); local_exact[row,col]|=estimator.any()
    domains=[]
    for name,mask in [('independent_estimator_cubes',estimator),('truth_diagnostic_cube',diagnostic),('union_for_nonuniqueness_proof_only',match)]:
        roots=rec[mask]; intervals=[]
        for op in range(3):
            if not len(roots): intervals.append({'operator':OPS[op],'empty':True}); continue
            values=roots['ys'][:,op+1,:].astype('f8'); a=values.min(0); b=values.max(0)
            # For positive scalar targets, no estimate can have relative error
            # less than (b-a)/(b+a) against both endpoints. These endpoints are
            # native witnesses, so this is a GLOBAL lower bound even though
            # the searched sets provide no global upper bound.
            bounds=np.divide(b-a,b+a,out=np.zeros(3),where=a>0); lb=float(bounds.max())
            j=int(bounds.argmax()); ia=int(values[:,j].argmin()); ib=int(values[:,j].argmax())
            intervals.append({'operator':OPS[op],'lower':a.tolist(),'upper':b.tolist(),'relative_minimax_lower_bound':lb,'oracle_inside_local_channel_hull':bool(np.all((truths[op][row,col]>=a)&(truths[op][row,col]<=b)))})
            if name=='independent_estimator_cubes':
                old=prior_by[point]['domains'][0]['intervals'][op]
                if not old.get('empty'):
                    a=np.minimum(a,np.asarray(old['lower']));b=np.maximum(b,np.asarray(old['upper']))
                    intervals[-1]['union_with_previous_lower']=a.tolist();intervals[-1]['union_with_previous_upper']=b.tolist()
                    lb=float(np.max(np.divide(b-a,b+a,out=np.zeros(3),where=a>0)))
                # Harmonic midpoint minimizes maximum scalar relative error
                # within this declared local set. No oracle-based selection.
                interval_est[op][row,col]=np.divide(2*a*b,a+b,out=(a+b)*.5,where=(a+b)!=0)
                est_ambiguous[op,row,col]|=lb>1e-3
            if name=='union_for_nonuniqueness_proof_only' and lb>1e-3:
                impossible[op,row,col]=True
                if len(examples)<40:
                    examples.append({'point':point,'operator':OPS[op],'channel':j,'lower_bound':lb,'x1':roots['x'][ia].astype('f8').tolist(),'x2':roots['x'][ib].astype('f8').tolist(),'same_y':target[row,col].tolist(),'neutral1':values[ia].tolist(),'neutral2':values[ib].tolist(),'family1':int(roots['family'][ia]),'family2':int(roots['family'][ib])})
        domains.append({'name':name,'exact_matches_including_duplicates':int(mask.sum()),'unique_half_rgb_roots':len(np.unique(rec['x'][mask].view('u2'),axis=0)),'intervals':intervals})
    assert diagnostic.any(), 'Truth centre is an exact control and must be feasible'
    points.append({'point':point,'matte_edge':bool(edge[row,col]),'skin_matte':float(matte[row,col]),'domains':domains,'global_hull':None,'global_hull_identified':False})
    domain_counts.append(int(estimator.sum()))
assert pos==len(records)
preview(target,'reference'); trials=[]
for op,truth,best,harmonic,failed in zip(OPS,truths,centred,interval_est,old_failed):
    oi=OPS.index(op); oldpred=target+load(OLD/(op+'-new-neutral.f16'))-oldrt
    q=np.max(abs(harmonic-truth)/np.maximum(abs(truth),1e-12),-1); newfail=eligible&(q>1e-3)
    trials.append({'operator':op,'S8_residual':metrics(oldpred,truth,eligible),'S15_interval_baseline':metrics(baseline[oi],truth,eligible),'new_best_root_residual':metrics(best,truth,eligible),'local_harmonic_interval_estimate':metrics(harmonic,truth,eligible),'new_estimate_on_original_failed_points':metrics(harmonic,truth,failed),'outside_skin_footprint_max_change':float(abs(harmonic[~footprint]-target[~footprint]).max()),'old_failures':int(failed.sum()),'original_failed_with_global_minimax_impossibility_witness':int(np.count_nonzero(failed&impossible[oi])),'all_requested_with_global_minimax_impossibility_witness':int(impossible[oi].sum()),'old_failed_with_estimator_set_ambiguity_above_threshold':int(np.count_nonzero(failed&est_ambiguous[oi])),'old_failed_without_exact_independent_local_root':int(np.count_nonzero(failed&~local_exact)),'old_failed_with_exact_local_root_but_not_proven_impossible':int(np.count_nonzero(failed&local_exact&~impossible[oi])),'old_failed_on_matte_edge':int(np.count_nonzero(failed&edge)),'remaining_failed_on_matte_edge':int(np.count_nonzero(newfail&edge)),'remaining_failed_interior':int(np.count_nonzero(newfail&~edge))})
    preview(harmonic,op+'-interval-estimate'); preview(best,op+'-best-root-residual')
    np.savez_compressed(O/(op+'-interval-estimate.npz'),rgb=harmonic.astype('f4'),requested=requested,local_exact_root=local_exact,nonunique_minimax_gt_threshold=impossible[oi])
np.savez_compressed(O/'interval-audit-masks.npz',requested=requested,local_exact=local_exact,global_impossibility_witness=impossible,matte_edge=edge)
dump(O/'finite-domain-intervals.private.json',points); dump(O/'impossibility-witnesses.private.json',examples)
previous_report=json.loads((PREV/'analysis/s14-analysis.json').read_text())
face_rows=previous_report['face_body_additional_sensitivity'];ident=previous_report['amplitude_identifiability_witnesses']
dump(O/'s16-analysis.json',{'os_build':'26A434','threshold_unchanged':1e-3,'points_requested':int(requested.sum()),'previous_interval_run':39161546771,'targeted_diagnostic_failure_set_selected_using_prior_oracle_error':True,'records_saved_exact_only':True,'enumerated_candidates':sum(p['enumerated_candidate_count'] for p in context['points']),'local_sets_completely_enumerated':True,'new_local_radius_half_codes':24,'unchanged_previous_points_reused':True,'global_hull_certified':False,'source_original_used_by_estimator':False,'unique_root_or_camera_truth_claimed':False,'independent_set_exact_roots_points':int(local_exact.sum()),'new_full_roundtrip':metrics(rt,target,eligible),'original_S8_full_roundtrip':metrics(oldrt,target,eligible),'trials':trials,'face_body_additional_sensitivity':face_rows,'amplitude_identifiability_witnesses':ident,'display':{'config':'cg-config-v2.2.0_aces-v1.3_ocio-v2.4','config_sha256':hashlib.sha256(cfg.serialize().encode()).hexdigest(),'view':'ACES 1.0 - SDR Video','source':'Linear P3-D65','exposure_ev':0},'preview_integrity':integrity,'classifications':{'matte_edge':'Correlation only; no causal blanket assignment.','half_nonuniqueness':'Exact native witness pairs; global impossibility lower bounds where > threshold. No proof all ambiguity comes solely from rounding.','forward_model_missing_operator':'Native original PSO used, so no emulated forward operator omitted; inverse domain and root-selection remain incomplete.','parameter_identification':'Controlled consumer theta9/10 known. Original baked camera parameters/Studio statistics remain unknown.'}})
