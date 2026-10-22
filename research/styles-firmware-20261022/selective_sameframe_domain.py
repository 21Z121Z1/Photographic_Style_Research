"""Paired S15 host warm-input exclusion vs full upstream set reachability.

Observed half inputs are exact saved observations, not interval centers. The
local certificates never replace propagated warm boxes in complete_forward.
No new original AIR call, pow213 inference, clamp or global-domain restriction.
"""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from complete_fixture import decode
from complete_forward import forward
from pixel_selective import SelectiveTexture
from selective_neutral_joint import Inputs,enclose
from leaf_numeric import V

CONTEXT_SHA='ffae597ca79f92447a2bdae45bbc007450be27ae9165bef78d0e6b3cb0932b11'
NATIVE_SHA='f16a7163475e4e78c11c1b7aae33bfd363c6a2ca425aa808f54772367bfd1081'
PROBE_SHA='d86aaf8c0b32733fe7b401921f76a767de0a22b1150e738b181f00843e420423'


def bounds(v):return {'lo':v.lo.tolist(),'hi':v.hi.tolist(),'max_width':float(np.max(v.hi-v.lo))}


def check(context,native,first_probe,output):
    if output.exists():raise FileExistsError(output)
    context_sha=hashlib.sha256(context.read_bytes()).hexdigest();saved=json.loads(native.read_text());first=json.loads(first_probe.read_text())
    if context_sha!=CONTEXT_SHA or saved['context_sha256']!=context_sha or first['context_sha256']!=context_sha or hashlib.sha256(native.read_bytes()).hexdigest()!=NATIVE_SHA or hashlib.sha256(first_probe.read_bytes()).hexdigest()!=PROBE_SHA:raise ValueError('Exact paired frozen context/native/probe required')
    c=decode(json.loads(context.read_text()));actual={k:np.array(v,dtype='u2').view('f2')for k,v in saved['native_half_bits'].items()};H=lambda x:V.value(x,point=False);warm=actual['warm409']
    if warm.shape!=(3,4,3)or not np.all(c.images[8]==c.images[8][0,0,0]):raise ValueError('Exact saved twelve pixels/uniform supplied sky required')
    lookup=SelectiveTexture(c.images[9],'paired saved zero lookup');offsets=tuple(H([0,0])for _ in range(3));amplitudes=H(c.params[18:21]);outputmix=H(c.params[112]);rows=[]
    def certificate(rgb,person,skin):return enclose(Inputs(rgb,person,skin,H(c.images[8][0,0,0]),lookup,offsets,amplitudes,outputmix))
    for y,x in np.ndindex(warm.shape[:2]):
        r=certificate(H(warm[y,x]),H(actual['person96'][y,x].reshape(-1)[0]),H(actual['skin95'][y,x].reshape(-1)[0]));rows.append({'grid':[x,y],'exact_saved_warm_half':warm[y,x].astype('f8').tolist(),'local_converted_enclosure':bounds(r.converted),'gamma':bounds(r.gamma),'local_negative_base_excluded_under_declared_budgets':bool(np.all(r.converted.lo>=0))})
    cloud=certificate(V.bounds(warm.min(axis=(0,1)),warm.max(axis=(0,1))),V.bounds(actual['person96'].min(),actual['person96'].max()),V.bounds(actual['skin95'].min(),actual['skin95'].max()))
    # The complete propagated set remains independent and is not replaced by
    # the observed cloud or any certificate; retain its original failures.
    propagated=forward(c,point=False);candidate=np.array([1.,1.,0.]);stages=[]
    for name in ['source38','linear137','reference196','working286','semantic347','BG352','FG354','saturated374','output392','skin393','neutral408','warm409']:
        if name not in propagated.observations:continue
        v=propagated.observations[name];clipped=v.clamp();contains=np.all((clipped.lo<=candidate)&(candidate<=clipped.hi),axis=-1)
        stages.append({'name':name,'max_width':float(np.max(v.hi-v.lo)),'clamped_box_contains_RGB110_pixels':int(np.count_nonzero(contains))})
    p=propagated.observations['warm409'];cloudlo=warm.min(axis=(0,1)).astype('f8');cloudhi=warm.max(axis=(0,1)).astype('f8');member=np.all((p.lo>=cloudlo)&(p.hi<=cloudhi),axis=-1)
    native_converted=np.array(next(r for r in first['rows']if r['name']=='converted')['native_bits'],dtype='u2').view('f2');local0=rows[0]['local_converted_enclosure'];covered=bool(np.all(native_converted>=local0['lo'])and np.all(native_converted<=local0['hi']))
    out={'scope':__doc__,'context_sha256':context_sha,'native_receipt_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'first_probe_sha256':hashlib.sha256(first_probe.read_bytes()).hexdigest(),'new_original_host_calls':0,'new_synthetic_pixels':0,'local_certificates':rows,'saved_host_warm_cloud':{'input_lo':cloudlo.tolist(),'input_hi':cloudhi.tolist(),'converted':bounds(cloud.converted),'negative_base_excluded_under_declared_budgets':bool(np.all(cloud.converted.lo>=0)),'RGB110_is_in_cloud':bool(np.all(cloudlo<=candidate)and np.all(candidate<=cloudhi)),'source':'twelve exact original host warm409 half observations from paired S15 context; not centers or propagated bounds'},'first_original_probe_covered_by_new_local_certificate':covered,'propagated_upstream_stages':stages,'first_outer_box_admitting_clamp_witness':next((s['name']for s in stages if s['clamped_box_contains_RGB110_pixels']),None),'full_propagated_set':{'selective_unknown_pixels':len(propagated.pixel_unknowns),'internal_unknowns':len(propagated.internal_unknowns),'writer_set_known':propagated.writer is not None,'warm_boxes_proven_inside_observed_cloud_pixels':int(np.count_nonzero(member)),'negative_reachability':'unknown under the full upstream rounding enclosure; componentwise outer containment is not a reachable witness'},'minimum_unresolved_relation':{'predicate':'exists admissible shared upstream rounding realization of this exact context whose warm409 RGB gives a negative selective converted base','missing_relation':'same FG354 -> neutral-gain smoothSat polar/Lab roundtrip saturated374 -> person-weighted mix392; keep common RGB/Lab roots and saturated-vs-FG difference rather than independent output boxes','current_box_membership_cannot_prove_RGB110_reachable':True,'observed_cloud_not_substituted_into_full_chain':True},'what_is_excluded':'negative pre-pow base for the twelve saved exact host warm inputs and their enclosing RGB cloud, conditional on existing selective2u/4u/conversion budgets','what_is_not_excluded':'all upstream rounding choices of the complete pipeline; original GPU; other raw contexts/lookup/active styles','S18_RGB110_full_clamp_witness_retained':True,'S19_native_pow213_executed':False,'pow1_shortcut_extra_clamp_domain_or_budget_change':False};output.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n');print(json.dumps({'local_exclusions':sum(r['local_negative_base_excluded_under_declared_budgets']for r in rows),'cloud_lower':cloud.converted.lo.tolist(),'first_outer_box':out['first_outer_box_admitting_clamp_witness'],'full_set_unknown':len(propagated.pixel_unknowns),'writer_set':propagated.writer is not None}));return out


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('context',type=Path);p.add_argument('native',type=Path);p.add_argument('first_probe',type=Path);p.add_argument('output',type=Path);a=p.parse_args();check(a.context,a.native,a.first_probe,a.output)
