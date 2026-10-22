"""Capture the unchanged first selective pow failure in the saved whole context."""
import argparse,inspect,json,hashlib
from pathlib import Path
import numpy as np
from leaf_numeric import V,DomainUnknown
from complete_fixture import decode
from complete_forward import forward


def check(context,output):
    if output.exists():raise FileExistsError(output)
    c=decode(json.loads(context.read_text()));old=V.pow;first={}
    def trace(a,b):
        try:return old(a,b)
        except DomainUnknown as e:
            frame=inspect.currentframe().f_back
            if not first and frame.f_code.co_filename.endswith('pixel_selective.py'):
                b=a.box(b);first.update(expression='converted.pow(gamma)',base_lo=a.lo.tolist(),base_hi=a.hi.tolist(),exponent_lo=b.lo.tolist(),exponent_hi=b.hi.tolist(),reason=str(e),line=frame.f_lineno)
            raise
    V.pow=trace
    try:r=forward(c,point=False)
    finally:V.pow=old
    data={'scope':__doc__,'native_calls':0,'context_sha256':hashlib.sha256(context.read_bytes()).hexdigest(),'first_selective_failure':first,'first_context_unknown':next(iter(r.pixel_unknowns.items()),None),'pixel_unknown_count':len(r.pixel_unknowns),'writer_known':r.writer is not None,'reachability':'The set base includes negative RGB after interval Lab inversion. This does not establish a reachable negative native converted value; the preserved native point is finite. Joint dependence through semantic/BG/FG/skin/color remains lost. No integer-exponent or arbitrary pow enclosure is assumed.','domain_or_budget_changed':False};output.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n');print(json.dumps(data));return data


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('context',type=Path);p.add_argument('output',type=Path);a=p.parse_args();check(a.context,a.output)
