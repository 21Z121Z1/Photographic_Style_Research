"""Twelve saved pixels only after the first neutral-joint proof and probe."""
import argparse,json,hashlib
from pathlib import Path
import numpy as np
from leaf_numeric import V
import pixel_selective
from complete_fixture import decode
from complete_forward import forward
from native_complete_check import comparisons


def encode_trace(d):
    return {k:{'lo':v.lo.tolist(),'hi':v.hi.tolist(),'max_width':float(np.max(v.hi-v.lo))}if isinstance(v,V)else v for k,v in d.items()}


def check(context,saved,baseline,first_pixel,output):
    if output.exists():raise FileExistsError(output)
    context_sha=hashlib.sha256(context.read_bytes()).hexdigest();saved_data=json.loads(saved.read_text());previous=json.loads(baseline.read_text());first=json.loads(first_pixel.read_text())
    if any(r.get('context_sha256')!=context_sha for r in [saved_data,previous,first]):raise ValueError('Saved native outputs, baseline and first probe do not match this frozen context')
    if any(first['observer_stability'].values())or any(not r['covered']for r in first['coverage'].values()):raise ValueError('First pixel proof/probe must already cover original observations')
    c=decode(json.loads(context.read_text()));actual={k:np.array(a,dtype='u2').view('f2')for k,a in saved_data['native_half_bits'].items()};old=pixel_selective.selective;rows=[]
    def trace(*a,**kw):
        d={}
        try:return old(*a,**kw,observations=d)
        finally:rows.append(encode_trace(d))
    pixel_selective.selective=trace
    try:r=forward(c,point=False)
    finally:pixel_selective.selective=old
    if len(previous['pixel_traces'])!=len(rows)or len(rows)!=12:raise ValueError('Expected the same twelve saved pixel traces')
    changes=[]
    for i,(oldrow,row)in enumerate(zip(previous['pixel_traces'],rows)):
        changes.append({'grid':[i%4,i//4],'old_converted':oldrow['converted'],'new_converted':row.get('converted'),'old_gamma':oldrow['gamma'],'new_gamma':row.get('gamma'),'joint_domain_used':'joint_proof'in row})
    point=comparisons(actual,forward(c,point=True));sets=comparisons(actual,r);out={'scope':__doc__,'native_calls':0,'context_sha256':hashlib.sha256(context.read_bytes()).hexdigest(),'first_pixel_receipt_sha256':hashlib.sha256(first_pixel.read_bytes()).hexdigest(),'baseline_receipt_sha256':hashlib.sha256(baseline.read_bytes()).hexdigest(),'point':point,'set':sets,'changes':changes,'first_pixel_trace':rows[0],'first_failure':'converted.pow(gamma) still unproved on negative outer bases, now gamma exactly1; no negative endpoint reachability established','original_GPU_or_whole_pipeline_proven':False,'new_leaf_cases':0,'backend_pow_domain_epsilon_mask_budgets_changed':False};root=Path(__file__).parent;out['source_sha256']={n:hashlib.sha256((root/n).read_bytes()).hexdigest()for n in ['color_matrices.py','pixel_color.py','pixel_selective.py','selective_neutral_joint.py','pixel_bright.py','leaf_numeric.py','replay_selective_joint.py','complete_forward.py']};output.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n');print(json.dumps({'pixels':len(rows),'first_unknown':sets['first_unknown'],'unknown_pixels':len(sets['pixel_unknowns']),'converted_width_before':changes[0]['old_converted']['max_width'],'converted_width_after':changes[0]['new_converted']['max_width'],'gamma':changes[0]['new_gamma'],'writer_set_known':r.writer is not None}));return out


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('context',type=Path);p.add_argument('saved',type=Path);p.add_argument('baseline',type=Path);p.add_argument('first_pixel',type=Path);p.add_argument('output',type=Path);a=p.parse_args();check(a.context,a.saved,a.baseline,a.first_pixel,a.output)
