"""macOS runner only. Full enumeration of declared local sets, not global hulls.

Truth-centred candidates are used only as diagnostics/nonuniqueness witnesses.
Neither root choice nor estimator uses the held original or its neutral output.
"""
from pathlib import Path
import sys, json, hashlib
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
context=json.loads((S/'s14-results.json').read_text()); assert not context['context_mismatches']
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
interval_est=[a.copy() for a in centred]
truths=[load(P/(op+'-removed-oracle.f16')) for op in OPS]
requested=np.zeros((H,W),bool); local_exact=np.zeros((H,W),bool)
impossible=np.zeros((3,H,W),bool); est_ambiguous=np.zeros_like(impossible); old_failed=[]
for op,truth in zip(OPS,truths):
    oldpred=target+load(OLD/(op+'-new-neutral.f16'))-oldrt
    old_failed.append(eligible&(np.max(abs(oldpred-truth)/np.maximum(abs(truth),1e-12),-1)>1e-3))
points=[]; examples=[]; pos=0; domain_counts=[]
for result in context['points']:
    point=result['point']; row,col=divmod(point,W); requested[row,col]=True
    assert result['batch_control_half_mismatches']==0 and result['local_union_enumerated_completely']
    count=result['candidate_count']; rec=records[pos:pos+count]; pos+=count
    assert len(rec)==count and np.all(rec['point']==point)
    match=np.all(rec['ys'][:,0,:]==target[row,col],-1); estimator=match&(rec['family']<4)
    diagnostic=match&(rec['family']==4); local_exact[row,col]=estimator.any()
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
                # Harmonic midpoint minimizes maximum scalar relative error
                # within this declared local set. No oracle-based selection.
                interval_est[op][row,col]=np.divide(2*a*b,a+b,out=(a+b)*.5,where=(a+b)!=0)
                est_ambiguous[op,row,col]=lb>1e-3
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
    trials.append({'operator':op,'S8_residual':metrics(oldpred,truth,eligible),'new_best_root_residual':metrics(best,truth,eligible),'local_harmonic_interval_estimate':metrics(harmonic,truth,eligible),'new_estimate_on_original_failed_points':metrics(harmonic,truth,failed),'outside_skin_footprint_max_change':float(abs(harmonic[~footprint]-target[~footprint]).max()),'old_failures':int(failed.sum()),'original_failed_with_global_minimax_impossibility_witness':int(np.count_nonzero(failed&impossible[oi])),'all_requested_with_global_minimax_impossibility_witness':int(impossible[oi].sum()),'old_failed_with_estimator_set_ambiguity_above_threshold':int(np.count_nonzero(failed&est_ambiguous[oi])),'old_failed_without_exact_independent_local_root':int(np.count_nonzero(failed&~local_exact)),'old_failed_with_exact_local_root_but_not_proven_impossible':int(np.count_nonzero(failed&local_exact&~impossible[oi])),'old_failed_on_matte_edge':int(np.count_nonzero(failed&edge)),'remaining_failed_on_matte_edge':int(np.count_nonzero(newfail&edge)),'remaining_failed_interior':int(np.count_nonzero(newfail&~edge))})
    preview(harmonic,op+'-interval-estimate'); preview(best,op+'-best-root-residual')
    np.savez_compressed(O/(op+'-interval-estimate.npz'),rgb=harmonic.astype('f4'),requested=requested,local_exact_root=local_exact,nonunique_minimax_gt_threshold=impossible[oi])
np.savez_compressed(O/'interval-audit-masks.npz',requested=requested,local_exact=local_exact,global_impossibility_witness=impossible,matte_edge=edge)
dump(O/'finite-domain-intervals.private.json',points); dump(O/'impossibility-witnesses.private.json',examples)
# Additional sensitivity levels only. Existing half/full-budget runs are kept
# as historical evidence. Spatial ROI statistics avoid whole-frame p99 hiding
# the small face support. These are chosen transforms, not camera calibration.
base=load(ALL/'consumer-tone0/primary_input.f32',4,'f4')
def smooth(a):
    a=np.clip(a,0,1).astype('f4')
    for axis in [0,1]:
        pads=[(0,0),(0,0)]; pads[axis]=(2,2); p=np.pad(a,pads,mode='edge'); z=np.zeros_like(a)
        for i,k in enumerate([1,4,6,4,1]):
            sl=[slice(None),slice(None)]; sl[axis]=slice(i,i+a.shape[axis]); z+=p[tuple(sl)]*(k/16)
        a=z
    return a*a*(3-2*a)
M=ALL/'consumer-tone0/semantic'
face=smooth(np.fromfile(M/'faceSkinMatte.f16','f2').reshape(H,W)); person=smooth(np.fromfile(M/'personMatte.f16','f2').reshape(H,W))
face_rows=[]; ident=[]; valid=np.isfinite(base).all(-1)&(np.min(base,axis=-1)>1/255)
for name,weight in [('face-only',face),('body-only',person*(1-face))]:
    for fraction in [.25,.75]:
        amp=float(np.log2(1.09765625))*fraction; gain=-np.float32(amp)*weight
        result=base*np.exp2(gain)[...,None]; recovered=result*np.exp2(-gain)[...,None]
        c0=base/np.maximum(base.sum(-1,keepdims=True),1e-12); c1=result/np.maximum(result.sum(-1,keepdims=True),1e-12)
        dx=abs(np.diff(gain,axis=1)); dy=abs(np.diff(gain,axis=0))
        rx=(weight[:,1:]>0)|(weight[:,:-1]>0); ry=(weight[1:]>0)|(weight[:-1]>0)
        edges=np.r_[dx[rx],dy[ry]]; lap=gain[1:-1,2:]+gain[1:-1,:-2]+gain[2:,1:-1]+gain[:-2,1:-1]-4*gain[1:-1,1:-1]
        roi=(weight[1:-1,1:-1]>0); bg=weight==0
        face_rows.append({'operator':name,'fraction_of_log2j_chosen_not_inferred':fraction,'amplitude_ev':amp,'support_pixels':int((weight>0).sum()),'support_edge_gradient_ev_p99':float(np.quantile(edges,.99)),'support_edge_gradient_ev_max':float(edges.max()),'support_laplacian_ev_p99':float(np.quantile(abs(lap[roi]),.99)),'chromaticity_max_abs':float(abs(c0[valid]-c1[valid]).max()),'background_max_abs':float(abs(result[bg]-base[bg]).max()),'budget_overshoot_pixels':int(np.count_nonzero((gain>0)|(gain < -amp-1e-7))),'roundtrip':metrics(recovered,base,valid),'camera_accuracy':None})
        preview(result,f'{name}-budget{fraction:g}')
    # Equally exact algebraic decompositions over a wider amplitude range
    # demonstrate that final RGB alone supplies no amplitude observation.
    for fraction in [0,.25,.5,.75,1,2]:
        g=-float(np.log2(1.09765625))*fraction*weight.astype('f8'); candidate=base*np.exp2(g)[...,None]
        ident.append({'operator':name,'fraction':fraction,'max_observation_reconstruction_relative':metrics(candidate*np.exp2(-g)[...,None],base,valid)['max_relative'],'physical_camera_model_validated':False})
dump(O/'s14-analysis.json',{'os_build':'26A434','threshold_unchanged':1e-3,'points_requested':int(requested.sum()),'local_sets_completely_enumerated':True,'global_hull_certified':False,'source_original_used_by_estimator':False,'unique_root_or_camera_truth_claimed':False,'independent_set_exact_roots_points':int(local_exact.sum()),'new_full_roundtrip':metrics(rt,target,eligible),'original_S8_full_roundtrip':metrics(oldrt,target,eligible),'trials':trials,'face_body_additional_sensitivity':face_rows,'amplitude_identifiability_witnesses':ident,'display':{'config':'cg-config-v2.2.0_aces-v1.3_ocio-v2.4','config_sha256':hashlib.sha256(cfg.serialize().encode()).hexdigest(),'view':'ACES 1.0 - SDR Video','source':'Linear P3-D65','exposure_ev':0},'preview_integrity':integrity,'classifications':{'matte_edge':'Correlation only; no causal blanket assignment.','half_nonuniqueness':'Exact native witness pairs; global impossibility lower bounds where > threshold. No proof all ambiguity comes solely from rounding.','forward_model_missing_operator':'Native original PSO used, so no emulated forward operator omitted; inverse domain and root-selection remain incomplete.','parameter_identification':'Controlled consumer theta9/10 known. Original baked camera parameters/Studio statistics remain unknown.'}})
