"""Replay public synthetic point inputs and audit retained host half ULP gaps.

Requires only the committed receipt and matching model source, not firmware.
No native reference is regenerated and no batch is rerun.
"""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from bgfg_fixed import ExactHelperFields,forward
from leaf_numeric import V,DomainUnknown
from semantic_tone import Curve1D


def ordered(bits):
    bits=np.asarray(bits,dtype='i4')
    return np.where(bits&0x8000,0x8000-(bits&0x7fff),0x8000+bits)


def audit(receipt):
    r=json.loads(receipt.read_text());root=Path(__file__).parent
    for name,sha in r['source_sha256'].items():
        if hashlib.sha256((root/name).read_bytes()).hexdigest()!=sha:raise ValueError('Receipt source revision differs: '+name)
    curve=Curve1D(tuple(np.linspace(0,1,17)**.8),'supplied whites working coordinate');rows=[]
    for index,row in enumerate(r['rows']):
        d=row['input'];f=ExactHelperFields(row['block'],np.array(row['field_values'],dtype='f4'),'public receipt exact synthetic fields')
        try:
            p=forward(V.value(d[:3]),V.value(d[6:9]),f,guide=V.value(d[3]),person=V.value(d[4]),skin=V.value(d[5]),whites=curve).lo.astype('f2')
            q=np.array(row['native_output_half'],dtype='f2')
            if not np.isfinite(q).all():raise DomainUnknown('Nonfinite retained host output')
            gaps=ordered(q.view('u2'))-ordered(p.view('u2'))
            rows.append({'receipt_row':index,'block':row['block'],'profile':row['profile'],'signed_half_ULP_gaps':gaps.tolist(),'point_unknown':None})
        except DomainUnknown as error:rows.append({'receipt_row':index,'point_unknown':str(error)})
    return {'receipt_sha256':hashlib.sha256(receipt.read_bytes()).hexdigest(),'audit_source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'max_absolute_half_ULP_gap':max((abs(v)for r in rows for v in r.get('signed_half_ULP_gaps',[])),default=None),'mismatching_components':sum(v!=0 for r in rows for v in r.get('signed_half_ULP_gaps',[])),'native_batch_rerun':False,'rows':rows}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('receipt',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    r=audit(a.receipt);a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items()if k!='rows'}))
