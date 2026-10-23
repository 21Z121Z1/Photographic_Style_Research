"""S32 full2047-input exact midpoint-squared double-rounding certificate."""
from pathlib import Path
import argparse,hashlib,json
from baseline_archive import encoded,sha
from sqrt_double_round import FIRST,LAST,COUNT,row,verify_row,parity_lemma
from square132_contract import value

R=Path(__file__).parent
E=R/'evidence'


def freeze(output):
    if output.exists():raise FileExistsError(output)
    d={'scope':__doc__,'input_first_half_bits':FIRST,'input_last_half_bits':LAST,'input_count':COUNT,
       'coverage':'all inclusive encodings0x3401..0x3bff, not random or floating sample',
       'arithmetic':'Fraction and integer comparisons to squared rounding midpoints, RN ties-even',
       'conditional_chain':'exact half-to-single -> correctly RN single sqrt -> RN half',
       'comparison':'ideal correctly RN half sqrt',
       'native_precision_and_FPCR':'static binary identity/implementation and runtime precision conditions are separate',
       'native_execution_planned':False,'compilation_planned':False,'default_models_changed':False}
    output.write_bytes(encoded(d));print(json.dumps({'domain':[FIRST,LAST],'count':COUNT,'native_calls':0}));return d


def run(plan_file,output):
    if output.exists():raise FileExistsError(output)
    import json
    plan=json.loads(plan_file.read_text());assert plan['input_count']==COUNT
    records=[];low=high=0
    for code in range(FIRST,LAST+1):
        r=row(code);verify_row(r);records.append(r)
        scaled=value(code)*(1<<24)
        assert scaled.denominator==1 and scaled.numerator%2==0
        if code<0x3800:assert scaled.numerator%(1<<12)==0;low+=1
        else:assert scaled.numerator%(1<<13)==0;high+=1
    assert low==1023 and high==1024
    failures=[r for r in records if r['double_round_differs']]
    d={'status':'complete_exact_selected_sqrt_double_rounding_certificate',
       'plan_sha256':sha(plan_file),'domain_half_bits':[FIRST,LAST],'input_count':COUNT,
       'input_encoding_order_sha256':hashlib.sha256(bytes().join(i.to_bytes(2,'little')for i in range(FIRST,LAST+1))).hexdigest(),
       'rows':records,'counterexamples':failures,'counterexample_count':len(failures),
       'single_to_half_midpoint_hits':sum(r['single_result_is_half_midpoint']for r in records),
       'all_exact_cell_certificates_verified':True,'coverage_has_no_duplicates_or_omissions':True,
       'parity_and_separation_lemma':parity_lemma(),'scaled_input_bin_counts':[low,high],
       'float_or_libm_used_for_mathematics':False,'new_native_calls':0,'new_helper_or_full_model_calls':0,
       'new_compilations':0,'actual_FPCR_or_GPU_verified':False,
       'source_sha256':{n:sha(R/n)for n in ['sqrt_double_round.py','certify_sqrt_domain.py','square132_contract.py','square140_contract.py']}}
    output.write_bytes(encoded(d));print(json.dumps({'status':d['status'],'inputs':COUNT,'counterexamples':len(failures),
                                                    'midpoint_hits':d['single_to_half_midpoint_hits'],'native_calls':0}));return d


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['freeze','certify']);p.add_argument('first',type=Path);p.add_argument('second',type=Path,nargs='?')
    a=p.parse_args()
    if a.mode=='freeze':freeze(a.first)
    else:run(a.first,a.second)
