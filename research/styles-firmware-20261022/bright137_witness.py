"""A fail-closed SSA137 correction for ONE authenticated saved bright witness.

Not wired into pixel_bright or v3. No cast16/multiple-parameter inverse support.
"""
from dataclasses import dataclass,field
from pathlib import Path
import argparse,json
import numpy as np
from baseline_archive import sha,encoded
from leaf_numeric import V

DETAIL_SHA='825f669bfbf2463361042d45f4773da588051c99e499794a451e2dfb84b3353a'
CONTEXT_SHA='37d3385222f3f42988d79dbbe5db89c3147c6988f5c0b7ef9ff10bab97031be6'


def require_inverse_scope(cast_type:int,free_fields:frozenset):
    if type(cast_type)is not int or type(free_fields)is not frozenset:raise TypeError('Explicit cast and frozen free-field set required')
    if cast_type!=0 or free_fields!=frozenset({3}):raise ValueError('This accepted inverse work covers fixed cast0 and field3 only; cast16/multiple free parameters are unverified and prohibited')


@dataclass(frozen=True)
class Saved137:
    evidence_file:Path
    square_bits:tuple=field(init=False)
    multiplier_bits:tuple=field(init=False)

    def __post_init__(self):
        if sha(self.evidence_file)!=DETAIL_SHA:raise ValueError('Exact saved original diagnostic required')
        d=json.loads(self.evidence_file.read_text());stages={s['SSA']:s for s in d['stages']}
        if d['context_sha256']!=CONTEXT_SHA or d['grid']!=[0,1]or any(d['observer_stability_half_bit_mismatches'].values()):raise ValueError('Saved context/grid/observer domain mismatch')
        if any(stages[i]['bit_mismatches']for i in [132,133,134,135,136])or d['first_observed_checkpoint_divergence']['SSA']!=137:raise ValueError('First-divergence contract changed')
        object.__setattr__(self,'square_bits',tuple(stages[132]['native_bits']));object.__setattr__(self,'multiplier_bits',tuple(stages[135]['native_bits']))

    def apply(self,square:V,multiplier:V):
        for value,expected in [(square,self.square_bits),(multiplier,self.multiplier_bits)]:
            if not isinstance(value,V)or value.precision!='h'or not value.point or value.lo.shape!=(3,):raise TypeError('Exact half3 points only')
            if not np.array_equal(value.lo,value.lo.astype('f2').astype('f8'))or tuple(value.lo.astype('f2').view('u2'))!=expected:raise ValueError('Outside the saved SSA137 input domain; do not apply witness-specific contraction elsewhere')
        return multiplier.fma_half(square,V.value(4))


def check(evidence,output):
    if output.exists():raise FileExistsError(output)
    domain=Saved137(evidence);d=json.loads(evidence.read_text());s={x['SSA']:x for x in d['stages']};square=V.value(np.array(domain.square_bits,dtype='u2').view('f2'));multiplier=V.value(np.array(domain.multiplier_bits,dtype='u2').view('f2'));separate=multiplier*square+V.value(4);fixed=domain.apply(square,multiplier);native=np.array(s[137]['native_bits'],dtype='u2');old_diff=int(np.count_nonzero(separate.lo.astype('f2').view('u2')!=native));new_diff=int(np.count_nonzero(fixed.lo.astype('f2').view('u2')!=native))
    if old_diff!=1 or new_diff:raise AssertionError('Saved SSA137 correction does not reproduce original checkpoint')
    rejected={}
    for label,cast,fields in [('cast16',16,frozenset({3})),('multiple_parameters',0,frozenset({2,3}))]:
        try:require_inverse_scope(cast,fields)
        except ValueError as ex:rejected[label]=str(ex)
        else:raise AssertionError('Unsupported inverse scope was not rejected')
    require_inverse_scope(0,frozenset({3}));result={'scope':__doc__,'saved_diagnostic_sha256':sha(evidence),'complete_context_sha256':CONTEXT_SHA,'grid':[0,1],'node':137,'input_square132_half_bits':list(domain.square_bits),'input_multiplier135_half_bits':list(domain.multiplier_bits),'native137_half_bits':native.tolist(),'separate_rounding_half_bits':separate.lo.astype('f2').view('u2').tolist(),'local_one_round_half_bits':fixed.lo.astype('f2').view('u2').tolist(),'before_half_bit_mismatches':old_diff,'after_local_half_bit_mismatches':new_diff,'domain':'exact authenticated saved half3 operands only; no implicit neighborhood or other caller','default_pixel_bright_modified':False,'v3_precision_contract_modified':False,'remaining_original_bright_differences':{'S25_targets':6,'S25_boundaries':18},'downstream_or_full_bright_replayed':False,'cast16_and_multiple_parameter_rejections':rejected,'native_or_full_point_forward_calls':0,'scope_guard_does_not_certify_new_caller':True}
    output.write_bytes(encoded(result));print(json.dumps({'saved_node':137,'before':old_diff,'after_local':new_diff,'native_calls':0,'default_pipeline_changed':False,'cast16_and_multiple_parameters':'prohibited'}));return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('evidence',type=Path);p.add_argument('output',type=Path);a=p.parse_args();check(a.evidence,a.output)
