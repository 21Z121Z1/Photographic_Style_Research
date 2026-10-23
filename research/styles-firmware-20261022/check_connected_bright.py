"""Model source pass first, saved-host comparison second: S30 composition."""
from pathlib import Path
import argparse,json
import numpy as np
from baseline_archive import encoded,sha
from bright_point_profile import Profile
from connected_bright import source_run
from context_color_api import load

R=Path(__file__).parent
E=R/'evidence'


def serialize(result):
    return {n:{'precision':v.precision,'shape':list(v.lo.shape),
               'model_half_bits':v.lo.astype('f2').view('u2').tolist()}
            for n,v in result.observations.items()}


def compare(observations,reference):
    out={}
    for n,r in observations.items():
        if n not in reference:continue
        a=np.array(r['model_half_bits'],dtype='u2');b=np.array(reference[n],dtype='u2')
        if b.shape==a.shape+(1,):b=b[...,0]
        if a.shape!=b.shape:raise ValueError('Observation shape mismatch '+n)
        differences=np.argwhere(a!=b).tolist()
        out[n]={'components':int(a.size),'half_bit_mismatches':len(differences),'differing_indices':differences,
                'max_absolute_error':float(np.max(abs(a.view('f2').astype('f8')-b.view('f2').astype('f8'))))}
    return out


def run(plan_file,output):
    if output.exists():raise FileExistsError(output)
    plan=load(plan_file);profile=Profile(E/plan['profile'],plan['profile_sha256'])
    model_rows=[]
    # No full-frame host reference arrays are loaded here. S29 may read saved
    # point evidence as identity/whitelist comparisons, never as pixel operands.
    for control in plan['controls']:
        result,record=source_run(E/plan['context'],control,profile,plan)
        record['model_observations']=serialize(result)
        model_rows.append(record)
    d={'status':'models_completed_before_reference_load','plan_sha256':sha(plan_file),
       'source_sha256':{n:sha(R/n)for n in ['connected_bright.py','check_connected_bright.py','freeze_connected_bright.py']},
       'rows':model_rows,'full_model_calls':3,'new_kernel_calls':0,'new_compilations':0,
       'native_arrays_used_as_model_inputs':False,'full_frame_reference_phase_started_only_after_all_models_completed':True,
       'S29_evidence_read_inside_profile':'identity and whitelist comparisons only; all arithmetic operands are model-produced'}
    output.write_bytes(encoded(d))
    expected_hashes={}
    attribution=load(E/'bright-residual-attribution-s29c.json')
    for record in model_rows:
        control=record['control'];file=E/control['expected_saved_file'];expected=load(file)
        expected_hashes[file.name]=sha(file)
        reference={**expected['prefix_native_half_bits'],**expected['rows'][control['expected_saved_row']]['native_half_bits']}
        metrics=compare(record['model_observations'],reference)
        record['saved_host_comparison']=metrics
        record['first_differing_saved_checkpoint']=next(({'name':n,**m}for n,m in metrics.items()if m['half_bit_mismatches']),None)
        for visit in record['visits']:
            if not visit.get('guard_admitted'):continue
            key=visit['expected_input_key'];expected_stages=attribution['unique_points'][key]['corrected_stages']
            visit['saved_bright_checkpoint_comparison']=[{'SSA':r['SSA'],
                'bit_mismatches':sum(x!=y for x,y in zip(visit['bright_stage_bits'][str(r['SSA'])]['bits'],r['host_bits']))}
                for r in expected_stages]
        record['all_saved_observations_equal']=not any(m['half_bit_mismatches']for m in metrics.values())
        record['compared_components']=sum(m['components']for m in metrics.values())
        record['writer_half_bit_mismatches']=metrics.get('writer',{}).get('half_bit_mismatches')
    passed=all(r['status']=='model_source_to_bright_connected'and r['all_saved_observations_equal']and r['writer_generated']for r in model_rows)
    d.update(status='passed_limited_source_composition'if passed else'failed_or_unknown_source_composition',
             saved_host_files_sha256=expected_hashes,
             attribution_sha256=sha(E/'bright-residual-attribution-s29c.json'),
             all_four_target_sites_admitted=sum(v.get('guard_admitted',False)for r in model_rows for v in r['visits'])==4,
             cast0_writer_is_independent_skin_branch=True,bright_selected_into_writer_tested=False,
             helper_original_host_evidence_reused=True,new_original_host_or_GPU_calls=0,
             v3_or_catalogs_replaced=False)
    output.write_bytes(encoded(d))
    print(json.dumps({'status':d['status'],'target_sites_admitted':sum(v.get('guard_admitted',False)for r in model_rows for v in r['visits']),
                      'per_control_components':[r['compared_components']for r in model_rows],
                      'per_control_mismatches':[sum(m['half_bit_mismatches']for m in r['saved_host_comparison'].values())for r in model_rows],
                      'writer_bit_mismatches':[r['writer_half_bit_mismatches']for r in model_rows],
                      'new_full_model_calls':3,'new_kernel_calls':0}))
    return d


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('plan',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args();run(a.plan,a.output)
