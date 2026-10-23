"""S31 arithmetic-domain admission examples, no native or full-model calls."""
from pathlib import Path
import argparse,json
from baseline_archive import encoded,sha
from context_color_api import load
from square132_contract import RMAX
from square140_contract import evaluate

R=Path(__file__).parent
E=R/'evidence'


def run(output):
    if output.exists():raise FileExistsError(output)
    data=load(E/'square132-proof-s31b.json')
    examples=[]
    for x in [0,12,0x21d3,0x2bff,0x2c00,0x33ff,0x3400,0x3401,RMAX]:
        examples.append({'name':'RN_normality_admission_'+hex(x),
                         'without_flush_or_sqrt_premise':evaluate(x,rn_even=True,gradual_underflow=None),
                         'with_gradual_and_correct_final_sqrt_premises':evaluate(x,rn_even=True,gradual_underflow=True,correct_final_sqrt_half=True)})
    d={'profile':'independent arithmetic-domain analysis, not default integration',
       'square_proof_sha256':sha(E/'square132-proof-s31b.json'),
       'source_sha256':{n:sha(R/n)for n in ['square140_contract.py','check_square140.py','square132_contract.py']},
       'examples':examples,'unknown_RN':evaluate(0x3400,rn_even=None,gradual_underflow=None),
       'all_examples_are_conditional_mathematical_contracts':True,
       'low_quarter_equality_exact_result_half_bits':evaluate(0x3400,rn_even=True,gradual_underflow=None)['selected140_half_bits'],
       'prefix_under_old_lower_bound_constructive_counterexample':next(w for w in data['witnesses']if w['name']=='normal_below_old_domain'and w['mode']=='separate'),
       'old_leaf_or_v3_modified':False,'new_kernel_calls':0,'new_native_compilations':0,'new_full_model_or_helper_calls':0}
    assert d['low_quarter_equality_exact_result_half_bits']==0x3800
    output.write_bytes(encoded(d));print(json.dumps({'arithmetic_examples':len(examples),'quarter_low_output':'0x3800',
       'normal_below_old_domain_admitted_by_operation_conditions':examples[2]['without_flush_or_sqrt_premise']['status'],
       'subnormal_without_FPCR_premise':examples[1]['without_flush_or_sqrt_premise']['status'],
       'new_original_calls':0}))
    return d


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path);run(p.parse_args().output)
