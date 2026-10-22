"""Compare whole guided sets with saved original-host values, no native rerun."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from guided_conditioned import forward_set,forward
from native_guided_check import fixtures
from leaf_numeric import DomainUnknown


def check(receipt,output):
    if output.exists():raise FileExistsError(output)
    saved=json.loads(receipt.read_text());rows=[]
    for (inputs,name),row in zip(fixtures(),saved['rows'],strict=True):
        if row['case']!=name or row['input_gain']!=inputs.input_gain.tolist()or row['guide']!=inputs.guide.tolist()or row['epsilon_f32']!=float(inputs.epsilon_f32):raise ValueError('Saved fixture changed')
        result={'case':name,'set_unknown':None,'observations':{}}
        try:
            point=forward(inputs);result['point_unknown']=None;result['point_bit_mismatches']={k:int(np.count_nonzero(v.view('u2')!=np.array(row['native_half_bits'][k],dtype='u2')))for k,v in point.items()}
            if any(result['point_bit_mismatches'].values()):raise AssertionError('Saved point result changed')
        except DomainUnknown as error:result['point_unknown']=str(error)
        if result['point_unknown']!=row['point_unknown']:raise AssertionError('Saved point domain changed')
        try:
            modeled=forward_set(inputs)
            for k,v in modeled.items():
                native=np.array(row['native_half_bits'][k],dtype='u2').view('f2').astype('f8');result['observations'][k]={'range_covered':bool(np.isfinite(native).all()and np.all(native>=v.lo)and np.all(native<=v.hi)),'max_set_width':float(np.max(v.hi-v.lo))}
        except DomainUnknown as error:result['set_unknown']=str(error)
        rows.append(result)
    r={'saved_native_receipt_sha256':hashlib.sha256(receipt.read_bytes()).hexdigest(),'source_sha256':{n:hashlib.sha256((Path(__file__).parent/n).read_bytes()).hexdigest()for n in ['guided_conditioned.py','check_guided_sets.py','leaf_numeric.py']},'native_kernel_calls':0,'GPU_executed':False,'sets_known':sum(x['set_unknown']is None for x in rows),'sets_unknown':sum(x['set_unknown']is not None for x in rows),'known_range_violations':sum(o['range_covered']is False for x in rows for o in x['observations'].values()),'rows':rows,'sampler_error_and_2u_4u_are_assumptions':True}
    output.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n')
    if r['known_range_violations']:raise AssertionError('Known set violation, receipt retained')
    return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('receipt',type=Path);p.add_argument('output',type=Path);a=p.parse_args();r=check(a.receipt,a.output);print(json.dumps({k:r[k]for k in ['sets_known','sets_unknown','known_range_violations']}))
