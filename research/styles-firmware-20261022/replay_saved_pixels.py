"""Replay current models against saved half outputs; never runs AIR or GPU."""
import argparse,hashlib,importlib,json
from pathlib import Path
import numpy as np
from leaf_numeric import DomainUnknown


def replay(module,receipt,output):
    if output.exists():raise FileExistsError(output)
    adapter=importlib.import_module(module);saved=json.loads(receipt.read_text());rows=[]
    for row in saved['rows']:
        data=np.array(row['input'],dtype='f4');native=np.array(row['native_half_bits'],dtype='u2').view('f2').astype('f4');result={}
        for point in [True,False]:
            try:
                value=adapter.model(row['helper'],data,point)
                if point:result.update(point_unknown=None,half_bit_mismatches=int(np.count_nonzero(native.astype('f2').view('u2')!=value.lo.astype('f2').view('u2'))),max_absolute_error=float(np.max(abs(native-value.lo))))
                else:result.update(set_unknown=None,range_covered=bool(np.isfinite(native).all()and np.all(native>=value.lo)and np.all(native<=value.hi)),max_set_width=float(np.max(value.hi-value.lo)))
            except DomainUnknown as error:result['point_unknown'if point else'set_unknown']=str(error)
        for key in ['point_unknown','set_unknown','half_bit_mismatches','max_absolute_error','range_covered']:
            if result.get(key)!=row.get(key):raise AssertionError((key,result.get(key),row.get(key)))
        rows.append(result)
    files=[p for p in Path(__file__).parent.glob('*.py')if p.name.startswith(('pixel_','leaf_'))or p.name in ['replay_saved_pixels.py',module+'.py','cast_values.py']]
    r={'saved_receipt_sha256':hashlib.sha256(receipt.read_bytes()).hexdigest(),'current_model_source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted(files)},'all_previous_point_set_status_and_metrics_equal':True,'native_calls_repeated':0,'GPU_executed':False,'rows':rows}
    output.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n');return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('module');p.add_argument('receipt',type=Path);p.add_argument('output',type=Path);a=p.parse_args();r=replay(a.module,a.receipt,a.output);print(json.dumps({'rows':len(r['rows']),'same_metrics':True,'max_set_width':max((x.get('max_set_width',0)for x in r['rows']),default=0)}))
