"""Query the exhaustively computed model catalog with explicit target bits."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from color_inverse import Domain,solve_target
from select_active_color import CONTEXT_SHA


def export_target(native_file,index,output):
    if output.exists():raise FileExistsError(output)
    e=Path(__file__).parent/'evidence';expected=json.loads((e/'verification-s21.json').read_text())['evidence_sha256']['native-active-s21c.json'];digest=hashlib.sha256(native_file.read_bytes()).hexdigest()
    if digest!=expected:raise ValueError('Example exporter only reads the saved authorized S21 synthetic host receipt')
    row=json.loads(native_file.read_text())['rows'][index];result={'known_context_sha256':CONTEXT_SHA,'writer_half_bits':row['native_half_bits']['writer'],'source_native_sha256':digest,'source_row':index,'source_raw_f32_bits':row['control']['raw_f32_bits'],'role':'target bytes only; search forward states are independently computed'};output.write_text(json.dumps(result,separators=(',',':'))+'\n');return result


def query(plan_file,target_file,chunks,output):
    if output.exists():raise FileExistsError(output)
    load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();p=load(plan_file);target=load(target_file)
    if target['known_context_sha256']!=CONTEXT_SHA:raise ValueError('Target must explicitly belong to the fixed known-source/auxiliary context')
    rows=[]
    for file in chunks:
        r=load(file)
        if r['plan_sha256']!=sha(plan_file)or r['base_context_sha256']!=CONTEXT_SHA:raise ValueError('Catalog context/partition mismatch')
        rows+=r['rows']
    raw=np.asarray(target['writer_half_bits'])
    if raw.dtype.kind not in 'ui'or np.any(raw<0)or np.any(raw>65535):raise TypeError('Target JSON must contain raw uint16 integers, not pixels as floats')
    result=solve_target(Domain(p['domain']['first_f32_bits'],p['domain']['last_f32_bits']),p['cells'],p['states'],rows,raw.astype('u2'));result['inputs_sha256']={plan_file.name:sha(plan_file),target_file.name:sha(target_file),**{f.name:sha(f)for f in chunks}};result['new_model_forward_evaluations']=0;result['new_native_calls']=0
    output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');print(json.dumps({'matching_states':result['model_matching_state_ids'],'candidate_union':result['candidate_union'],'complete_model_coverage':result['coverage']['complete_model_coverage']}));return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='action',required=True);q=sub.add_parser('export');q.add_argument('native',type=Path);q.add_argument('index',type=int);q.add_argument('output',type=Path);q=sub.add_parser('solve');q.add_argument('plan',type=Path);q.add_argument('target',type=Path);q.add_argument('output',type=Path);q.add_argument('chunks',nargs='+',type=Path);a=p.parse_args()
    if a.action=='export':export_target(a.native,a.index,a.output)
    else:query(a.plan,a.target,a.chunks,a.output)
