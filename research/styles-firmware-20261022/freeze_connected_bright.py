"""Freeze S30 three existing controls/four exact sites before model execution."""
from pathlib import Path
import argparse,json
from baseline_archive import encoded,sha
from context_color_api import load

R=Path(__file__).parent
E=R/'evidence'


def freeze(output):
    if output.exists():raise FileExistsError(output)
    prior=load(E/'bright-saved-replay-s29a.json')
    seen=set();controls=[]
    for row in prior['residual_rows']:
        sites=[]
        for pixel in row['residual_pixels']:
            if pixel['input_key']in seen:continue
            seen.add(pixel['input_key']);sites.append({'grid':pixel['grid'],'input_key':pixel['input_key']})
        if sites:
            controls.append({'raw_f32_bits':row['control']['raw_f32_bits'],'control_id':row['control']['id'],
                             'expected_saved_file':row['saved_file'],'expected_saved_row':row['row_index'],'targets':sites})
    assert len(controls)==3 and len(seen)==4
    d={'scope':__doc__,'context':'second-context-s25a.json','context_sha256':sha(E/'second-context-s25a.json'),
       'profile':'bright-point-profile-s29c.json','profile_sha256':sha(E/'bright-point-profile-s29c.json'),
       'precision_sha256':sha(E/'model-precision-v3-s25c6.json'),
       'selection_rule':'S29 residual-row order, first occurrence of every distinct complete-input key; no outcome-based selection',
       'controls':controls,'full_model_runs_planned':3,
       'native_saved_arrays_policy':'loaded only by post-run comparison; never passed to model or used to fill upstream',
       'raw_context_inputs':'frozen source/linear, auxiliary textures and raw ABI buffers/curves only',
       'bright_guard_mismatch_policy':'unknown/failure; no native fill, no v3 fallback at target site',
       'other_pixels':'unchanged v3 bright; selected actual writer remains cast0 skin branch',
       'no_kernel_or_compile_planned':True,'pre_execution_freeze':True}
    output.write_bytes(encoded(d));print(json.dumps({'controls':3,'target_sites':4,'planned_model_calls':3,'new_kernel_calls':0}))
    return d


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path);freeze(p.parse_args().output)
