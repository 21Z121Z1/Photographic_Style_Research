"""Independent S29 bright point profile: four exact authenticated input tuples.

Computes half FMA at SSA137, reuses the unmodified v3 graph elsewhere.
Not an inverse precision contract, neighborhood rule, set model or GPU model.
"""
from dataclasses import dataclass
from pathlib import Path
import inspect
import hashlib
import types

import numpy as np

from baseline_archive import encoded, sha
from bright_saved_replay import bits, fingerprint, traced_forward
from context_color_api import load
from leaf_numeric import V

R=Path(__file__).parent
E=R/'evidence'
NAME='bright-s29-four-saved-tuples-fma137-point-v1'


def make_contract(output):
    if output.exists(): raise FileExistsError(output)
    inventory=load(E/'bright-saved-replay-s29a.json')
    traces=load(E/'bright-traces-s29b.json')
    old=load(E/'bright-detail-s25c.json')
    first=hashlib.sha256(encoded(inventory['certified_inputs'])).hexdigest()
    data={first:{s['SSA']:s['native_bits']for s in old['stages']}}
    for call in traces['calls']:
        if not call['observer_stable']: raise ValueError('Unstable trace cannot certify inputs')
        data[call['input_key']]={s['SSA']:s['saved_host_trace_bits']for s in call['stages']}
    assert set(data)==set(inventory['unique_residual_inputs']) and len(data)==4
    points={}
    for key,stages in data.items():
        model=inventory['unique_residual_inputs'][key]
        assert all(model['stage_bits'][str(i)]==stages[i]for i in [132,133,134,135,136])
        points[key]={'complete_inputs':model['inputs'],'square132_half_bits':stages[132],
                    'multiplier135_half_bits':stages[135],'rounded_product136_half_bits':stages[136],
                    'host137_half_bits':stages[137],'host285_half_bits':stages[285]}
    d={'schema':NAME,'version':['iPhone17,3','24A446','SmartStyleV1','CMISmartStyleProcessorV1'],
       'basis_precision_sha256':sha(E/'model-precision-v3-s25c6.json'),
       'scope':'exact four complete saved half/f32 input tuples; no implicit neighborhood or other caller',
       'points':points,'only_changed_arithmetic':'SSA137 = round_half(multiplier135*square132 + half4), one rounding; original separate SSA136 remains an observation',
       'other_operations':'unmodified pinned v3 function with tracing expansion from bright_saved_replay.py',
       'source_sha256':{n:sha(R/n)for n in ['bright_point_profile.py','bright_saved_replay.py','pixel_bright.py','leaf_numeric.py']},
       'input_sha256':{n:sha(E/n)for n in ['bright-saved-replay-s29a.json','bright-traces-s29b.json','bright-detail-s25c.json']},
       'point_only':True,'v3_replaced':False,'inverse_scope_expanded':False,'GPU_verified':False}
    output.write_bytes(encoded(d))
    return d


@dataclass(frozen=True)
class Profile:
    file:Path
    expected_sha256:str

    def checked(self):
        if sha(self.file)!=self.expected_sha256: raise ValueError('Explicit independent profile SHA required')
        d=load(self.file)
        if d['schema']!=NAME or len(d['points'])!=4: raise ValueError('Four saved input tuples only')
        for n,h in d['source_sha256'].items():
            if sha(R/n)!=h: raise ValueError('Profile source changed')
        for n,h in d['input_sha256'].items():
            if sha(E/n)!=h: raise ValueError('Profile evidence changed')
        return d

    def forward(self,*args,observations=None):
        d=self.checked()
        fp=fingerprint(args)
        key=hashlib.sha256(encoded(fp)).hexdigest()
        if key not in d['points'] or fp!=d['points'][key]['complete_inputs']:
            raise ValueError('Outside exact authenticated four-tuple bright domain')
        if any(not v.point for v in [*args[:5],*vars(args[5]).values()]):
            raise TypeError('Point-only profile; no set acceptance')
        point=d['points'][key]
        def fma137(square,multiplier,product):
            if bits(square)!=point['square132_half_bits'] or bits(multiplier)!=point['multiplier135_half_bits'] or bits(product)!=point['rounded_product136_half_bits']:
                raise ValueError('Authenticated SSA132/135/136 contract not reached')
            return multiplier.fma_half(square,V.value(4))
        # Reuse exactly the generated baseline function code. Copy globals, so
        # neither original clone nor pixel_bright globals are ever patched.
        baseline=traced_forward()
        clone=inspect.getclosurevars(baseline).nonlocals['clone']
        namespace=dict(clone.__globals__)
        namespace['psr137']=fma137
        fn=types.FunctionType(clone.__code__,namespace,clone.__name__,clone.__defaults__,clone.__closure__)
        fn.__kwdefaults__=clone.__kwdefaults__
        return fn(*args,observations=observations)
