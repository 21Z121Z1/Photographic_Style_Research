"""One saved BW witness after correcting instrumentation memory effects."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
import native_bw_check as base


def check(source,receipt,output):
    prior=json.loads(receipt.read_text());witness=prior['rows'][0];previous=base.cases
    try:base.cases=lambda:iter([np.array(witness['input'],dtype='f4')]);r=base.check(source,output)
    finally:base.cases=previous
    equal=r['rows'][0]['observed']==witness['observed'];r['observer_contract_regression']={'one_saved_witness_only':True,'source_receipt_sha256':hashlib.sha256(receipt.read_bytes()).hexdigest(),'change':'BW observation wrapper memory(read)->memory(readwrite); retain all original FP attributes','all_three_saved_observations_equal':equal,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'original_batch_repeated':False}
    output.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n')
    if not equal:raise AssertionError('Observer contract correction changed saved observations')
    return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('receipt',type=Path);p.add_argument('output',type=Path);a=p.parse_args();r=check(a.source,a.receipt,a.output);print(json.dumps(r['observer_contract_regression']))
