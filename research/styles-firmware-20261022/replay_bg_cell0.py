"""Default contrast admission replay: saved64 boxes and original S14C case0 only."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from leaf_numeric import V,DomainUnknown
from pixel_leaves import contrast,contrast_independent
from contrast_span_joint import cell0_supported
import typed_bgfg
from native_main_pre393_check import fixtures,model
from main_pre393_host import OBSERVATIONS


def check(saved,native,output):
    if output.exists():raise FileExistsError(output)
    data=json.loads(saved.read_text());oldnative=json.loads(native.read_text());cells=sorted(data['partition']['known_subsets']+data['partition']['unknown_subsets'],key=lambda r:r['cell'])
    if [c['cell']for c in cells]!=list(range(64)):raise ValueError('Exact saved64 cover required')
    amount=V.value(data['amount_half'],point=False);rows=[]
    for cell in cells:
        rgb=V(np.array(cell['input_lo']),np.array(cell['input_hi']),'h',False);row={'cell':cell['cell'],'input_lo':rgb.lo.tolist(),'input_hi':rgb.hi.tolist(),'joint_admitted':bool(cell0_supported(rgb,amount))}
        for key,fn in [('independent',contrast_independent),('default',contrast)]:
            try:
                v=fn(rgb,amount);row[key]={'status':'known','output_lo':v.lo.tolist(),'output_hi':v.hi.tolist(),'max_width':float(np.max(v.hi-v.lo))}
            except DomainUnknown as e:row[key]={'status':'unknown','reason':str(e)}
        rows.append(row)
    calls=[];old=typed_bgfg.contrast;olddiv=V.__truediv__;active=[]
    def divide(a,b):
        try:return olddiv(a,b)
        except DomainUnknown as e:
            if active and 'first_division_failure'not in active[-1]:
                q=a.box(b);active[-1]['first_division_failure']={'precision':a.precision,'numerator_lo':a.lo.tolist(),'numerator_hi':a.hi.tolist(),'denominator_lo':q.lo.tolist(),'denominator_hi':q.hi.tolist(),'reason':str(e)}
            raise
    def observe(rgb,amount):
        row={'leaf':'contrastFilter','input_lo':rgb.lo.tolist(),'input_hi':rgb.hi.tolist(),'amount_lo':float(amount.lo),'amount_hi':float(amount.hi),'joint_admitted':bool(cell0_supported(rgb,amount))};calls.append(row)
        active.append(row)
        try:
            v=old(rgb,amount);row.update(status='known',max_width=float(np.max(v.hi-v.lo)));return v
        except DomainUnknown as e:row.update(status='unknown',reason=str(e));raise
        finally:active.pop()
    typed_bgfg.contrast=observe;V.__truediv__=divide
    try:full=model(next(fixtures()),False)
    finally:typed_bgfg.contrast=old;V.__truediv__=olddiv
    case=next(r for r in oldnative['rows']if r['case']==0);bits=np.asarray(case['native_output_half_bits'],dtype='u2').view('f2');ranges={};offset=0
    for name,ssa,count in OBSERVATIONS:
        actual=bits[offset:offset+count];offset+=count
        if name in full.observations:
            v=full.observations[name];ranges[name]={'covered':bool(np.all(actual>=v.lo)and np.all(actual<=v.hi)),'max_width':float(np.max(v.hi-v.lo))}
    out={'scope':__doc__,'saved_cover_sha256':hashlib.sha256(saved.read_bytes()).hexdigest(),'native_receipt_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'native_calls':0,'new_partition_or_leaf_cases':0,'rows':rows,'independent_unknown_cells':sum(r['independent']['status']=='unknown'for r in rows),'default_unknown_cells':sum(r['default']['status']=='unknown'for r in rows),'original_S14C_case0':{'unknown_operator':full.unknown_operator,'unknown_reason':full.unknown_reason,'contrast_calls':calls,'known_prefix_ranges':ranges,'complete_BG_verified':False},'cell0_domain_does_not_admit_original_whole_contrast_box':True,'original_threshold_budgets_order_and_else_unchanged':True}
    output.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n');print(json.dumps({k:v for k,v in out.items()if k not in ['rows','original_S14C_case0']}));return out


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('saved',type=Path);p.add_argument('native',type=Path);p.add_argument('output',type=Path);a=p.parse_args();check(a.saved,a.native,a.output)
