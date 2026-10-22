"""Replay saved model inputs only and retain each first zero denominator.

No native batch, point-center fallback, input-domain reduction or gate change.
Guard exclusions are logical path facts; upstream joint reachability of other
box zeros remains unknown until separately proved.
"""
import argparse,hashlib,inspect,json
from pathlib import Path
import numpy as np
from leaf_numeric import V
from semantic_tone import I,Curve1D
from bgfg_tone import run,PixelContext
from all_pixel_leaves import models
from native_bgfg_complete_check import packet


def diagnose(receipt,output):
    if output.exists():raise FileExistsError(output)
    saved=json.loads(receipt.read_text());rows=[];original_div=V.__truediv__
    for index,row in enumerate(saved['rows']):
        captured=[]
        def divide(a,b):
            b=a.box(b)
            if not captured and np.any((b.lo<=0)&(b.hi>=0)):
                frames=inspect.stack();site=next(f for f in frames if Path(f.filename).name.startswith('pixel_'))
                frames_data=[{'file':Path(f.filename).name,'function':f.function,'line':f.lineno}for f in frames if Path(f.filename).name.startswith('pixel_')]
                guarded=site.function in ('preserve','scale')
                captured.append({'numerator_lower':np.asarray(a.lo).tolist(),'numerator_upper':np.asarray(a.hi).tolist(),'denominator_lower':np.asarray(b.lo).tolist(),'denominator_upper':np.asarray(b.hi).tolist(),'precision':b.precision,'stack':frames_data,'classification':'zero excluded by original strict-positive branch guard; conditional interval failed to retain guard'if guarded else'box contains zero; upstream joint reachability not proved','real_zero_on_executed_division_path':'excluded by branch guard'if guarded else'unknown','threshold_changed':False})
            return original_div(a,b)
        V.__truediv__=divide
        try:
            profile={i:x for i,x in enumerate(row['field_values'])};fields=packet(row['block'],profile);data=row['input']
            r=run(row['block'],I.point(data[:3]),fields,PixelContext(*map(float,data[3:6])),semantic_rgb=I.point(data[6:9]),leaf_models=models(Curve1D(tuple(np.linspace(0,1,17)**.8),'supplied whites working coordinate')))
        finally:V.__truediv__=original_div
        rows.append({'saved_row':index,'block':row['block'],'profile':row['profile'],'status':r.status,'missing_operator':r.missing_operator,'first_zero_denominator':captured[0]if captured else None,'operator_input_lower':None if r.missing_input_set is None else r.missing_input_set.lo.tolist(),'operator_input_upper':None if r.missing_input_set is None else r.missing_input_set.hi.tolist()})
    result={'receipt_sha256':hashlib.sha256(receipt.read_bytes()).hexdigest(),'native_calls':0,'input_rows':len(rows),'first_zero_denominators':sum(r['first_zero_denominator']is not None for r in rows),'guard_excluded_zeros':sum(r['first_zero_denominator']is not None and r['first_zero_denominator']['real_zero_on_executed_division_path']=='excluded by branch guard'for r in rows),'rows':rows,'source_sha256':{n:hashlib.sha256((Path(__file__).parent/n).read_bytes()).hexdigest()for n in ['diagnose_set_denominators.py','leaf_numeric.py','pixel_leaves.py','pixel_tonal.py','pixel_remaining.py','leaf_domains.py','bgfg_tone.py']},'point_fallback_used':False}
    output.write_text(json.dumps(result,indent=2)+'\n');return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('receipt',type=Path);p.add_argument('output',type=Path);a=p.parse_args();r=diagnose(a.receipt,a.output);print(json.dumps({k:v for k,v in r.items()if k not in ['rows','source_sha256']}))
