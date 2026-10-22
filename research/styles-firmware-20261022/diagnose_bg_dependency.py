"""Replay S14C case0 only; shared-span bounds and 64 within-branch boxes."""
import argparse,hashlib,json
from contextlib import contextmanager
from pathlib import Path
import numpy as np
import pixel_leaves,typed_bgfg
from leaf_numeric import V,DomainUnknown
from leaf_correlations import channel_span
from native_main_pre393_check import fixtures,model


@contextmanager
def span_backend(correlated):
    old=pixel_leaves.channel_span
    pixel_leaves.channel_span=channel_span if correlated else lambda x:x.max_channels()-x.min_channels()
    try:yield
    finally:pixel_leaves.channel_span=old


def evaluate(correlated):
    failure={};seen={};olddiv=V.__truediv__;oldcontrast=typed_bgfg.contrast
    def divide(a,b):
        try:return olddiv(a,b)
        except DomainUnknown as e:
            if not failure and 'budget'in str(e):
                b=a.box(b);failure.update(expression='newspan / strictly_positive_branch(span, original threshold)',dividend_lo=np.asarray(a.lo).tolist(),dividend_hi=np.asarray(a.hi).tolist(),divisor_lo=np.asarray(b.lo).tolist(),divisor_hi=np.asarray(b.hi).tolist(),rounded_ratio_finite_half_limit=65504,reason=str(e))
            raise
    def contrast(rgb,amount):
        seen.update(rgb=rgb,amount=amount);return oldcontrast(rgb,amount)
    with span_backend(correlated):
        V.__truediv__=divide;typed_bgfg.contrast=contrast
        try:r=model(next(fixtures()),False)
        finally:V.__truediv__=olddiv;typed_bgfg.contrast=oldcontrast
    return r,seen,failure


def check(output,saved):
    if output.exists():raise FileExistsError(output)
    baseline,old_input,old_failure=evaluate(False);refined,new_input,new_failure=evaluate(True);box=new_input['rgb'];amount=new_input['amount'];boxes=[box]
    # Four exact real subintervals per RGB channel: cover the whole original
    # box, including gray/strict-threshold branches, without changing a mask.
    for axis in range(3):
        children=[]
        for b in boxes:
            edges=np.linspace(b.lo[axis],b.hi[axis],5)
            for j in range(4):
                lo=b.lo.copy();hi=b.hi.copy();lo[axis]=edges[j];hi[axis]=edges[j+1];children.append(V(lo,hi,'h',False))
        boxes=children
    known=[];unknown=[]
    for i,b in enumerate(boxes):
        try:
            with span_backend(True):v=pixel_leaves.contrast(b,amount)
            known.append({'cell':i,'input_lo':b.lo.tolist(),'input_hi':b.hi.tolist(),'output_lo':v.lo.tolist(),'output_hi':v.hi.tolist(),'max_width':float(np.max(v.hi-v.lo))})
        except DomainUnknown as e:unknown.append({'cell':i,'input_lo':b.lo.tolist(),'input_hi':b.hi.tolist(),'reason':str(e)})
    r={'scope':__doc__,'native_calls':0,'source_witness_sha256':hashlib.sha256(saved.read_bytes()).hexdigest(),'original_case':0,'baseline':{'unknown_operator':baseline.unknown_operator,'reason':baseline.unknown_reason,'first_failure':old_failure},'shared_span':{'unknown_operator':refined.unknown_operator,'reason':refined.unknown_reason,'first_failure':new_failure},'contrast_input_lo':box.lo.tolist(),'contrast_input_hi':box.hi.tolist(),'amount_half':float(amount.lo),'partition':{'cells':len(boxes),'known_cells':len(known),'unknown_cells':len(unknown),'full_result_unknown':bool(unknown),'known_subset_max_width':max((r['max_width']for r in known),default=None),'known_subsets':known,'unknown_subsets':unknown},'whole_context_unknown_before':int(baseline.unknown_operator is not None),'whole_context_unknown_after':int(refined.unknown_operator is not None),'whole_context_unknown_after_partition':int(bool(unknown)),'full_context_range_coverage':None,'aggregate_full_width_before':None,'aggregate_full_width_after':None,'threshold_epsilon_mask_budgets_changed':False,'center_substitution':False,'zero_classification':'Active original span.f()>threshold has no zero divisor: intersecting the strict branch raises its lower bound to half0x00a8 (1.0013580322265625e-5). Independent interval/newspan dependence still makes the quotient exceed half finite range. This is a software enclosure gap, not a hardware blocker.','unsafe_rewrite_rejected':'(rgb-low)*newspan/span -> ((rgb-low)/span)*newspan would change original half division overflow/rounding. No such rewrite is used.'};output.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n');return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path);p.add_argument('saved',type=Path);a=p.parse_args();r=check(a.output,a.saved);print(json.dumps({k:r[k]for k in ['baseline','shared_span','whole_context_unknown_before','whole_context_unknown_after']}));print(json.dumps({k:v for k,v in r['partition'].items()if k not in ['known_subsets','unknown_subsets']}))
