"""Only frozen S15 twelve pixels: complete propagated shared color path."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from leaf_numeric import V
from joint_lab import JointRGB
from complete_fixture import decode
import complete_forward,main_pre393,pixel_selective
from native_complete_check import comparisons
from selective_sameframe_domain import CONTEXT_SHA,NATIVE_SHA


def encode(v):
    if isinstance(v,V):return {'lo':v.lo.tolist(),'hi':v.hi.tolist(),'max_width':float(np.max(v.hi-v.lo))}
    return v


def check(context,native,contract,output):
    if output.exists():raise FileExistsError(output)
    if hashlib.sha256(context.read_bytes()).hexdigest()!=CONTEXT_SHA or hashlib.sha256(native.read_bytes()).hexdigest()!=NATIVE_SHA:raise ValueError('Exact frozen same-frame context/native receipt required')
    source_contract=json.loads(contract.read_text())
    if not source_contract['all_match']or source_contract['smooth_function_sha256']!='5163cdebd82f65a95aa8307c0e526c38db38e8e9ce0e174bb8c03997a901e065':raise ValueError('Matched neutral smoothSat precision contract required first')
    c=decode(json.loads(context.read_text()));actual={k:np.array(v,dtype='u2').view('f2')for k,v in json.loads(native.read_text())['native_half_bits'].items()};colors=[];selectives=[];oldcolor=main_pre393.outer_color;oldselective=pixel_selective.selective
    def color(*args,**kwargs):
        r=oldcolor(*args,**kwargs);colors.append({'input_FG354':encode(args[0]),'saturated374':encode(r.saturated374),'output392':encode(r.output392),'weight389':encode(r.person_mix389),'joint_proof':r.joint_proof});return r
    def selective(*args,**kwargs):
        trace={};row={'warm_input':encode(args[0]),'JointRGB_reaches_warm409':isinstance(args[0],JointRGB)};selectives.append(row)
        try:return oldselective(*args,**kwargs,observations=trace)
        finally:row['trace']={k:encode(v)for k,v in trace.items()}
    main_pre393.outer_color=color;pixel_selective.selective=selective
    try:sets=complete_forward.forward(c,point=False)
    finally:main_pre393.outer_color=oldcolor;pixel_selective.selective=oldselective
    point=comparisons(actual,complete_forward.forward(c,point=True));ranges=comparisons(actual,sets);old=json.loads((Path(__file__).parent/'evidence/selective-sameframe-s19b.json').read_text());baseline={r['name']:r['max_width']for r in old['propagated_upstream_stages']};stages=[];candidate=np.array([1.,1.,0.])
    for name in ['FG354','saturated374','output392','skin393','neutral408','warm409','selective413','output600','writer']:
        if name not in sets.observations:continue
        v=sets.observations[name];row={'name':name,'max_width':float(np.max(v.hi-v.lo)),'previous_S19_width':baseline.get(name),'native_range_covered':ranges['observations'][name].get('range_covered')}
        if np.shape(v.lo)[-1]==3:row['clamped_box_RGB110_pixels']=int(np.count_nonzero(np.all((v.clamp().lo<=candidate)&(candidate<=v.clamp().hi),axis=-1)))
        stages.append(row)
    lower=[];negative_pixels=[]
    for i,row in enumerate(selectives):
        d=row['trace'].get('converted')
        if d is not None:
            lo=np.asarray(d['lo']);lower.append(float(lo.min()))
            if np.any(lo<0):negative_pixels.append({'grid':[i%4,i//4],'lo':d['lo'],'hi':d['hi'],'endpoint_joint_reachability':'not established'})
    result={'scope':__doc__,'context_sha256':CONTEXT_SHA,'native_receipt_sha256':NATIVE_SHA,'static_contract_sha256':hashlib.sha256(contract.read_bytes()).hexdigest(),'new_original_host_calls':0,'saved_pixels':12,'point':point,'set':ranges,'stages':stages,'color_rows':colors,'selective_rows':selectives,'converted_minimum_lower':min(lower)if lower else None,'converted_negative_outer_pixels':negative_pixels,'input_substitution_or_domain_shrink':False,'observed_host_warm_cloud_used_as_input':False,'writer_set_really_generated':sets.writer is not None,'source_color_zero_only':True,'original_GPU_or_real_frame_verified':False};output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');print(json.dumps({'stages':stages,'selective_unknown':len(sets.pixel_unknowns),'internal_unknown':len(sets.internal_unknowns),'negative_outer_pixels':len(negative_pixels),'joint_lineage_pixels':sum(v['JointRGB_reaches_warm409']for v in selectives),'writer_set':sets.writer is not None,'point_bit_mismatches':sum(v['half_bit_mismatches']for v in point['observations'].values())}))
    if any(not v.get('range_covered',True)for v in ranges['observations'].values()):raise AssertionError('Shared color bound excludes a saved native observation; receipt retained')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('context',type=Path);p.add_argument('native',type=Path);p.add_argument('contract',type=Path);p.add_argument('output',type=Path);a=p.parse_args();check(a.context,a.native,a.contract,a.output)
