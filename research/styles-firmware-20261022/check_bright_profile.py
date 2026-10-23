"""Check four exact saved bright inputs and attribute every S25 6+18 residual."""
from pathlib import Path
import argparse
import json

import numpy as np

from baseline_archive import encoded,sha
from bright_point_profile import Profile,make_contract
from bright_saved_replay import arguments,bits
from context_color_api import load
from leaf_numeric import V

R=Path(__file__).parent
E=R/'evidence'


def run(contract_file,output):
    if contract_file.exists()or output.exists(): raise FileExistsError('New profile and result required')
    make_contract(contract_file)
    profile=Profile(contract_file,sha(contract_file))
    d=profile.checked()
    inventory=load(E/'bright-saved-replay-s29a.json')
    traces=load(E/'bright-traces-s29b.json')
    old=load(E/'bright-detail-s25c.json')
    stage_map={}
    certified=inventory['certified_inputs']
    import hashlib
    first_key=hashlib.sha256(encoded(certified)).hexdigest()
    stage_map[first_key]={s['SSA']:s['native_bits']for s in old['stages']}
    for c in traces['calls']: stage_map[c['input_key']]={s['SSA']:s['saved_host_trace_bits']for s in c['stages']}
    points={}
    occurrences=[]
    for row in inventory['residual_rows']:
        for pixel in row['residual_pixels']:
            key=pixel['input_key']
            if key not in points:
                receipt=load(E/row['saved_file'])
                args,host=arguments(E/'second-context-s25a.json',receipt,receipt['rows'][row['row_index']],*pixel['grid'])
                observations={}
                result=profile.forward(*args,observations=observations)
                native=stage_map[key]
                checks=[{'SSA':i,'host_bits':expected,'corrected_bits':bits(observations[i]),
                         'bit_mismatches':sum(a!=b for a,b in zip(expected,bits(observations[i])))}for i,expected in sorted(native.items())]
                square=np.array(d['points'][key]['square132_half_bits'],dtype='u2').view('f2')
                multiplier=np.array(d['points'][key]['multiplier135_half_bits'],dtype='u2').view('f2')
                separate=(multiplier*square).astype('f2')+np.float16(4)
                fused=(multiplier.astype('f8')*square.astype('f8')+4).astype('f2')
                assert fused.view('u2').tolist()==native[137]
                points[key]={'inputs':d['points'][key]['complete_inputs'],
                             'first_observed_divergence_SSA':137,
                             'native132_half_bits':square.view('u2').tolist(),
                             'native135_half_bits':multiplier.view('u2').tolist(),
                             'native136_half_bits':native[136],
                             'old_separate137_half_bits':separate.view('u2').tolist(),
                             'native137_half_bits':native[137],'one_round137_half_bits':fused.view('u2').tolist(),
                             'operation_order':'old: half135*half132 -> round_half136, then +half4 -> round_half137; new local rule: multiply+add then one half rounding',
                             'corrected_stages':checks,'corrected_final_bits':bits(result),
                             'host_final_bits':host.tolist(),
                             'first_remaining_observed_divergence':next((s for s in checks if s['bit_mismatches']),None),
                             'old_final_bits':inventory['unique_residual_inputs'][key]['model_output_bits']}
            p=points[key]
            for channel in pixel['channels']:
                old_bits=pixel['model_output_bits'][channel]
                host_bits=pixel['saved_host_output_bits'][channel]
                occurrences.append({'saved_file':row['saved_file'],'row_index':row['row_index'],'control':row['control'],
                                    'grid':pixel['grid'],'output_channel':channel,'input_key':key,
                                    'first_observed_divergence_SSA':137,
                                    'old_output_half_bits':old_bits,'host_output_half_bits':host_bits,
                                    'corrected_output_half_bits':p['corrected_final_bits'][channel],
                                    'old_signed_half_steps':int(old_bits)-int(host_bits),
                                    'old_absolute_error':float(abs(np.array(old_bits,dtype='u2').view('f2').astype('f8')-np.array(host_bits,dtype='u2').view('f2').astype('f8'))),
                                    'corrected_matches_saved_host':p['corrected_final_bits'][channel]==host_bits,
                                    'attribution_scope':'first observed SSA137, native135/132 operands and native136 match; downstream intervention checked through285; not all unobserved SSA certified'})
    assert len(occurrences)==24 and len(points)==4
    # A neighboring half input is a counterexample to applicability, not a new
    # native numerical counterexample and never silently admitted.
    first=inventory['residual_rows'][0]
    saved=load(E/first['saved_file'])
    args,_=arguments(E/'second-context-s25a.json',saved,saved['rows'][0],0,1)
    neighbor=args[0].lo.astype('f2').view('u2').copy();neighbor[0]+=1
    changed=(V.value(neighbor.view('f2')),*args[1:])
    try: profile.forward(*changed)
    except ValueError as ex: rejected=str(ex)
    else: raise AssertionError('Uncertified neighbor admitted')
    result={'profile_sha256':sha(contract_file),'profile_name':d['schema'],
            'scope':'four exact saved complete bright input tuples; conditional point helper only',
            'unique_points':points,'all24_residual_occurrences':occurrences,
            'old_target_residuals':6,'old_boundary_residuals':18,
            'corrected_residuals':sum(not r['corrected_matches_saved_host']for r in occurrences),
            'all_saved_checkpoints_match':all(p['first_remaining_observed_divergence']is None for p in points.values()),
            'neighbor_input_rejected':rejected,'new_helper_model_evaluations':4,
            'rejected_calls_before_arithmetic':1,
            'new_full_pipeline_model_calls':0,'new_original_kernel_calls':0,
            'v3_or_catalogs_changed':False,'cast16_or_multiple_parameters_enabled':False,
            'GPU_verified':False,'generalized_rule_certified':False}
    output.write_bytes(encoded(result))
    print(json.dumps({'four_points':4,'old_occurrences':24,'remaining':result['corrected_residuals'],
                      'all_saved_checkpoints_match':result['all_saved_checkpoints_match'],
                      'neighbor':'rejected','v3_modified':False,'GPU':False}))
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('contract',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args();run(a.contract,a.output)
