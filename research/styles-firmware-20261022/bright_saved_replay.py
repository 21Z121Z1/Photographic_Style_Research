"""S29 saved bright replay: isolated exact137 experiment, never v3 mutation."""
from pathlib import Path
import argparse
import ast
import hashlib
import json

import numpy as np

import pixel_bright
from active_color import Color, replace_color
from baseline_archive import encoded, sha
from bright137_witness import Saved137
from color_inverse import f32
from complete_fixture import decode
from context_color_api import load
from leaf_numeric import V
from pixel_bright import BrightStats

R = Path(__file__).parent
E = R / 'evidence'
PROFILE = 'bright-s29-authenticated137-downstream-point-v1'


def bits(v):
    dt, ut = ('f2', 'u2') if v.precision == 'h' else ('f4', 'u4')
    return v.lo.astype(dt).view(ut).reshape(-1).tolist()


def fingerprint(args):
    return [{'precision': v.precision, 'shape': list(v.lo.shape), 'bits': bits(v)}
            for v in [*args[:5], *vars(args[5]).values()]]


def arguments(context, saved, row, x, y):
    c = replace_color(decode(load(context)), Color(f32(row['control']['raw_f32_bits'])))
    native = {n: np.array(a, dtype='u2').view('f2')
              for n, a in {**saved['prefix_native_half_bits'], **row['native_half_bits']}.items()}
    def val(name):
        a = native[name][y, x]
        return V.value(a.reshape(-1)[0] if a.size == 1 else a)
    def stat(g, k):
        return V.value(c.stats[2560 + g * 9 + k], 'f')
    args = (val('skin393'), val('working286'), val('person96'), val('skin95'),
            V.value(c.params[7]).h(), BrightStats(stat(2,4), stat(3,4), stat(5,0), stat(6,6), stat(6,4)))
    return args, native['bright400'][y, x].view('u2').reshape(-1)


def traced_forward(*, certified_args=None):
    """Clone our pinned v3 function, expand only its low expression for tracing.

    Corrected mode admits exactly one complete authenticated input fingerprint.
    No global monkeypatch, source modification or general FMA policy.
    """
    precision = load(E / 'model-precision-v3-s25c6.json')
    if sha(R / 'pixel_bright.py') != precision['model_source_sha256']['pixel_bright.py']:
        raise ValueError('Pinned v3 bright source required')
    tree = ast.parse((R / 'pixel_bright.py').read_text())
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'forward')
    selected = [n for n in fn.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'low' for t in n.targets)]
    if len(selected) != 1:
        raise ValueError('One pinned low expression required')
    node = selected[0]
    expected = ast.parse("low=(((square*H(hc('4c00'),rgb)+H(hc('ca00'),rgb))*square)+H(4,rgb))*square").body[0]
    if ast.dump(node, include_attributes=False) != ast.dump(expected, include_attributes=False):
        raise ValueError('Original operation tree changed')
    replacement = ast.parse("""
p133=save(133,square.sqrt())
p134=save(134,square*H(hc('4c00'),rgb))
p135=save(135,p134+H(hc('ca00'),rgb))
p136=save(136,p135*square)
p137=save(137,psr137(square,p135,p136))
low=save(138,p137*square)
""").body
    i = fn.body.index(node)
    fn.body[i:i+1] = replacement
    module = ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[]))
    saved137 = Saved137(E / 'bright-detail-s25c.json')
    namespace = dict(vars(pixel_bright))
    def psr137(square, multiplier, product):
        return product + V.value(4) if certified_args is None else saved137.apply(square, multiplier)
    namespace['psr137'] = psr137
    exec(compile(module, '<PSR-S29-pinned-bright-clone>', 'exec'), namespace)
    clone = namespace['forward']
    contract = fingerprint(certified_args) if certified_args is not None else None
    def run(*args, observations=None):
        values = [*args[:5], *vars(args[5]).values()]
        if any(not isinstance(v, V) or not v.point or not np.isfinite(v.lo).all() for v in values):
            raise TypeError('Finite point operands only; no set acceptance')
        if contract is not None and fingerprint(args) != contract:
            raise ValueError('Outside authenticated full bright input tuple')
        return clone(*args, observations=observations)
    return run


def run(output):
    if output.exists():
        raise FileExistsError(output)
    context = E / 'second-context-s25a.json'
    saved = load(E / 'native-targets-s25c.json')
    args, expected = arguments(context, saved, saved['rows'][0], 0, 1)
    original, fixed = {}, {}
    old = traced_forward()(*args, observations=original)
    new = traced_forward(certified_args=args)(*args, observations=fixed)
    detail = load(E / 'bright-detail-s25c.json')
    stages = []
    for row in detail['stages']:
        i = row['SSA']
        stages.append({'SSA': i, 'precision': row['precision'], 'saved_host_bits': row['native_bits'],
                       'old_model_bits': bits(original[i]), 'corrected_model_bits': bits(fixed[i]),
                       'old_bit_mismatches': sum(a != b for a,b in zip(bits(original[i]),row['native_bits'])),
                       'corrected_bit_mismatches': sum(a != b for a,b in zip(bits(fixed[i]),row['native_bits']))})
        assert bits(original[i]) == row['model_bits']
    # Reuse all ten saved rows, deduplicate complete bright-input tuples before arithmetic.
    cache, rows = {}, []
    for filename in ['native-targets-s25c.json','native-target-B-s25c2.json','native-boundaries-s25f.json']:
        receipt = load(E / filename)
        for index, row in enumerate(receipt['rows']):
            residuals = []
            for y in range(3):
                for x in range(4):
                    a, expected_bits = arguments(context, receipt, row, x, y)
                    fp = fingerprint(a)
                    key = hashlib.sha256(encoded(fp)).hexdigest()
                    if key not in cache:
                        observations = {}
                        point = traced_forward()(*a, observations=observations)
                        cache[key] = {'inputs': fp, 'model_output_bits': bits(point),
                                      'stage_bits': {str(k): bits(v) for k,v in observations.items()}}
                    item = cache[key]
                    differences = [k for k,(m,n) in enumerate(zip(item['model_output_bits'],expected_bits)) if m != n]
                    if differences:
                        residuals.append({'grid':[x,y], 'input_key':key, 'channels':differences,
                                          'saved_host_output_bits':expected_bits.tolist(),
                                          'model_output_bits':item['model_output_bits']})
            total = sum(len(r['channels']) for r in residuals)
            assert total == row['point']['observations']['bright400']['half_bit_mismatches']
            rows.append({'saved_file':filename,'row_index':index,'control':row['control'],
                         'half_bit_mismatches':total,'residual_pixels':residuals})
    keys = {r['input_key'] for row in rows for r in row['residual_pixels']}
    result = {'scope':__doc__, 'profile':PROFILE, 'context_sha256':sha(context),
              'precision_domain':'one exact complete saved bright input tuple; original half3 SSA132/135 guard also enforced',
              'certified_grid':[0,1], 'certified_inputs':fingerprint(args), 'stages':stages,
              'old_final_bits':bits(old), 'corrected_final_bits':bits(new), 'saved_host_final_bits':expected.tolist(),
              'corrected_first_remaining_observed_divergence':next((r for r in stages if r['corrected_bit_mismatches']),None),
              'residual_rows':rows, 'unique_residual_inputs':{k:cache[k] for k in sorted(keys)},
              'helper_model_evaluations':len(cache)+2, 'unique_all_saved_inputs':len(cache),
              'new_full_pipeline_model_calls':0,'new_original_kernel_calls':0,
              'default_v3_modified':False,'GPU_verified':False,
              'source_sha256':{p.name:sha(p)for p in [R/'bright_saved_replay.py',R/'pixel_bright.py',R/'bright137_witness.py']},
              'input_sha256':{n:sha(E/n)for n in ['second-context-s25a.json','native-targets-s25c.json','native-target-B-s25c2.json','native-boundaries-s25f.json','bright-detail-s25c.json','model-precision-v3-s25c6.json']}}
    output.write_bytes(encoded(result))
    print(json.dumps({'corrected_final_bits':bits(new),'saved_host_final_bits':expected.tolist(),
                      'first_remaining_observed_SSA':None if result['corrected_first_remaining_observed_divergence'] is None else result['corrected_first_remaining_observed_divergence']['SSA'],
                      'residual_counts':[r['half_bit_mismatches']for r in rows],
                      'unique_residual_inputs':len(keys),'new_original_kernel_calls':0}))
    return result


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path)
    run(p.parse_args().output)
