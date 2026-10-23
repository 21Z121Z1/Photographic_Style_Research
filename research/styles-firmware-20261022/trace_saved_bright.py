"""Three missing saved bright traces via the exact existing S25 host dylib.

No compiler, original iOS runtime or GPU. Reuses saved guided maps, authenticates
all old sealed inputs, copies actual reused IR/shim/dylib privately before load.
"""
from pathlib import Path
import argparse
import ctypes
import hashlib
import json

import numpy as np

from active_color import Color, replace_color
from baseline_archive import Archive, encoded, sha
from bright_saved_replay import arguments, fingerprint
from color_inverse import f32
from complete_fixture import decode
from context_color_api import load
from main_full_host import OBSERVATIONS
from native_guided_check import texture

R = Path(__file__).parent
E = R / 'evidence'
REPO = R.parents[1]


def run(private, output):
    if output.exists(): raise FileExistsError(output)
    inventory = load(E / 'bright-saved-replay-s29a.json')
    detail_file = E / 'bright-detail-s25c.json'
    detail = load(detail_file)
    old = Archive(REPO.parent / detail['private_storage_relative_to_task'], repo=REPO)
    old_proof = old.verify(detail['products'])
    assert old_proof['sealed_manifest_sha256'] == detail['private_manifest_sha256']
    meta = old.manifest()['metadata']
    assert meta['probes']['bright']['original_arithmetic_predicates_and_FP_attrs_changed'] is False
    a = Archive(private, create=True, repo=REPO)
    for n in ['trace_saved_bright.py','bright_saved_replay.py','pixel_bright.py','numeric_trace_host.py']:
        a.input('sources/' + n, (R / n).read_bytes(), 'current replay source identity')
    for old_name, new_name in [('inputs/trace.ll','inputs/reused-trace.ll'),
                               ('inputs/shim.c','inputs/reused-shim.c'),
                               ('artifacts/trace.dylib','inputs/reused-trace.dylib')]:
        a.input(new_name, old.path(old_name).read_bytes(), 'exact existing S25 compiler input/product; no recompile')
    for n in ['second-context-s25a.json','bright-saved-replay-s29a.json','bright-detail-s25c.json',
              'native-targets-s25c.json','native-target-B-s25c2.json','native-boundaries-s25f.json']:
        a.input('binding/' + n, (E / n).read_bytes(), 'actual saved synthetic call input')
    a.seal({'scope':__doc__, 'prior_private_manifest_sha256':detail['private_manifest_sha256'],
            'prior_compiler_command':detail['command'], 'prior_compiled_product':detail['products'],
            'layout':meta['probes']['bright']['layout'], 'new_compilations':0})
    proofs = [a.proof('before-load')]
    lib = ctypes.CDLL(str(a.path('inputs/reused-trace.dylib')))
    fn = lib.psr_main_full
    fn.argtypes = [ctypes.c_void_p]*7+[ctypes.c_int32]+[ctypes.c_uint16]*2+[ctypes.c_void_p]
    fn.restype = None
    original_key = hashlib.sha256(encoded(inventory['certified_inputs'])).hexdigest()
    seen = {original_key}
    calls = []
    context_file = E / 'second-context-s25a.json'
    for entry in inventory['residual_rows']:
        saved = load(E / entry['saved_file'])
        row = saved['rows'][entry['row_index']]
        c = replace_color(decode(load(context_file)), Color(f32(row['control']['raw_f32_bits'])))
        native = {n:np.array(v,dtype='u2').view('f2') for n,v in {**saved['prefix_native_half_bits'],**row['native_half_bits']}.items()}
        for residual in entry['residual_pixels']:
            key = residual['input_key']
            if key in seen: continue
            seen.add(key)
            x,y = residual['grid']
            args, expected = arguments(context_file,saved,row,x,y)
            assert hashlib.sha256(encoded(fingerprint(args))).hexdigest() == key
            arrays = [None if v is None else texture(v) for v in
                      [c.images[0],c.images[1],np.array(c.gtc.red_samples,dtype='f2')[None,:,None],
                       np.array(c.whites.red_samples,dtype='f2')[None,:,None],None,native['BG_output'],native['FG_output'],
                       *[c.images[i] for i in [4,5,6,7,8,9]]]]
            ptrs = (ctypes.c_void_p*13)(*[None if v is None else v.ctypes.data for v in arrays])
            target = texture(c.output_initial)
            out = np.zeros(meta['original']['observation_float_count'],dtype='f4')
            params = c.params.copy()
            # Exactly one original host main at this saved pixel, no producer/guided calls.
            fn(ptrs,target.ctypes.data,c.management.ctypes.data,params.ctypes.data,c.stats.ctypes.data,
               c.roi.ctypes.data,c.srl.ctypes.data,c.version,x,y,out.ctypes.data)
            trace = np.ctypeslib.as_array((ctypes.c_float*meta['probes']['bright']['count']).in_dll(lib,'psr_trace_bright')).copy()
            stages = []
            for ssa,ty,count,offset in meta['probes']['bright']['layout']:
                dt,ut = ('f2','u2') if ty=='half' else ('f4','u4')
                native_bits = trace[offset:offset+count].astype(dt).view(ut).tolist()
                model_bits = inventory['unique_residual_inputs'][key]['stage_bits'][str(ssa)]
                stages.append({'SSA':ssa,'precision':ty,'saved_host_trace_bits':native_bits,
                               'model_bits':model_bits,'bit_mismatches':sum(x!=y for x,y in zip(native_bits,model_bits))})
            stages.sort(key=lambda r:r['SSA'])
            observations,offset = {},0
            for n,ssa,count in OBSERVATIONS:
                observations[n] = out[offset:offset+count]
                offset += count
            stability = {n:int(np.count_nonzero(observations[n].astype('f2').view('u2') !=
                                               native[n][y,x].reshape(-1).view('u2')))
                         for n in ['bright400','working286','skin393','person96','skin95','selected404','output600']}
            call = {'input_key':key,'saved_file':entry['saved_file'],'row_index':entry['row_index'],
                    'control':row['control'],'grid':[x,y],'stages':stages,
                    'first_observed_checkpoint_divergence':next(s for s in stages if s['bit_mismatches']),
                    'stability_vs_saved_full_observations':stability,
                    'observer_stable':not any(stability.values()),'original_host_main_calls':1}
            calls.append(call)
            a.write(f'calls/{len(calls)}.json',encoded(call),mode=0o400)
            if any(stability.values()): raise AssertionError('Observer changed saved outputs; do not attribute unstable trace')
    assert len(calls)==3 and len(seen)==4
    proofs.append(a.proof('after-run'))
    old_after = old.verify(detail['products'])
    assert old_after['sealed_manifest_sha256'] == old_proof['sealed_manifest_sha256']
    result = {'scope':__doc__,'inventory_sha256':sha(E/'bright-saved-replay-s29a.json'),
              'prior_detail_sha256':sha(detail_file),'prior_archive_input_files_verified':old_proof['input_files_verified'],
              'old_private_manifest_sha256':detail['private_manifest_sha256'],
              'actual_reused_product_sha256':sha(a.path('inputs/reused-trace.dylib')),
              'actual_reused_trace_IR_sha256':sha(a.path('inputs/reused-trace.ll')),
              'prior_inputs_and_product_unchanged_after_run':True,
              'private_storage_relative_to_task':str(a.root.relative_to(REPO.parent)),
              'private_manifest_sha256':sha(a.path('prepared.private.json')),'proofs':proofs,
              'calls':calls,'new_original_host_main_calls':3,'new_producer_or_guided_calls':0,
              'new_compilations':0,'CPU_recompiled_AIR':True,'original_iOS_or_GPU':False,
              'observed_first_SSA_is_checkpoint_not_unobserved_full_SSA_proof':True}
    a.write('result.private.json',encoded(result),mode=0o400)
    output.write_bytes(encoded(result))
    print(json.dumps({'calls':3,'first_checkpoints':[(c['grid'],c['first_observed_checkpoint_divergence']['SSA'])for c in calls],
                      'all_observers_stable':all(c['observer_stable']for c in calls),'new_compilations':0,'GPU':False}))
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('private',type=Path);p.add_argument('output',type=Path)
    args=p.parse_args();run(args.private,args.output)
