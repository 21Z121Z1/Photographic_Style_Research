"""S31 exact arithmetic/domain tests, no model helper or native replay."""
from fractions import Fraction as Q
from pathlib import Path
from unittest.mock import patch
import unittest
import numpy as np
from baseline_archive import sha
from context_color_api import load
from square132_contract import (CONSTANTS,RMAX,Assumptions,Unknown,value,rn,mul,add,fma,
                                power_certificate,prefix,weight,classify,low_segment)
from square140_contract import evaluate,sqrt_rn
from bright_low_host import forward as old_low
from leaf_numeric import V

R=Path(__file__).parent
E=R/'evidence'


class SquareContractTests(unittest.TestCase):
    def test_exact_half_rounding_ties_sign_and_zero(self):
        eta=Q(1,1<<24)
        self.assertEqual(rn(eta/2),0)
        self.assertEqual(rn(3*eta/2),2)
        self.assertEqual(rn(-3*eta/2),0x8002)
        self.assertEqual(mul(0xca00,0),0x8000)
        self.assertEqual(fma(0xca00,0,0x4400),0x4400)
        for code in [0,1,0x03ff,0x0400,0x1400,0x2bff,0x3400,0x3bff,0xca00]:
            self.assertEqual(rn(value(code)),code)

    def test_symbolic_checks_and_outer_hull_are_conditional_not_scan_proof(self):
        d=load(E/'square132-proof-s31b.json')
        self.assertTrue(all(d['symbolic_derivation']['constant_inequalities'].values()))
        self.assertEqual(d['generally_proved_outer_hull_half_bits'],[0,0x3bff])
        self.assertEqual(value(RMAX),Q(2047,2048))
        self.assertFalse(d['all_interior_half_values_claimed_reachable'])
        self.assertFalse(d['native_pow_sqrt_FPCR_or_GPU_certified'])

    def test_strength_weight_bounds_and_invalid_strength(self):
        self.assertEqual(weight(0x3c00),CONSTANTS['weight_factor'])
        self.assertEqual(weight(rn(Q(12))),CONSTANTS['weight_cap'])
        self.assertTrue(0<value(weight(0x3c00))<value(weight(rn(Q(12))))<1)
        with self.assertRaises(Unknown):weight(rn(Q(1,2)))

    def test_zero_and_subnormal_are_constructed_not_arbitrary_square_endpoints(self):
        for mode in ['separate','fused']:
            a=Assumptions(True,True,mode)
            self.assertEqual(prefix(0,0x3c00,a)['square132'],0)
            p=prefix(1,0x3c00,a)
            self.assertEqual(p['reference112'],13)
            self.assertEqual(p['square132'],12)
            self.assertTrue(classify(12)['subnormal'])
        checks=load(E/'square132-proof-s31b.json')['full_existing_helper_model_checks']
        self.assertTrue(all(r['full_existing_model_helper_finite']for r in checks))

    def test_normal_below_old_leaf_is_valid_prefix_but_old_guard_still_rejects(self):
        p=prefix(0x1400,0x3c00,Assumptions(True,True,'separate'))
        self.assertEqual(p['square132'],0x21d3)
        self.assertTrue(value(p['square132'])<Q(1,16))
        with self.assertRaises(ValueError):old_low(V.value([float(value(0x21d3))]*3))
        admitted=evaluate(0x21d3,rn_even=True,gradual_underflow=None)
        self.assertEqual(admitted['status'],'conditional_math_point')
        self.assertTrue(admitted['normal_or_exact_zero_path_independent_of_FZ16'])

    def test_exact_power_certificates_do_not_call_floating_pow(self):
        d=load(E/'square132-proof-s31b.json')
        w=next(w for w in d['witnesses']if w['name']=='boundary_0x3400'and w['mode']=='separate')
        with patch('numpy.power',side_effect=AssertionError('not an exact proof')):
            p=prefix(w['c'],0x3c00,Assumptions(True,True,'separate'))
        self.assertEqual(p['square132'],0x3400)
        c=p['power_certificate'];self.assertEqual(c['exponent_numerator'],853)
        self.assertEqual(c['exponent_denominator'],2048)
        with self.assertRaises(AssertionError):power_certificate(w['c'],c['power_half_bits']+1)

    def test_quarter_boundary_and_neighbors_have_exact_prefix_witnesses(self):
        d=load(E/'square132-proof-s31b.json')
        for mode in ['separate','fused']:
            for code in [0x33ff,0x3400,0x3401]:
                rows=[w for w in d['witnesses']if w.get('target_square')==code and w['mode']==mode]
                self.assertEqual(len(rows),1)
                self.assertEqual(rows[0]['exact_prefix']['square132'],code)
        self.assertEqual([classify(x)['selected140_branch']for x in [0x33ff,0x3400,0x3401]],['low','low','sqrt'])
        self.assertEqual(evaluate(0x3400,rn_even=True,gradual_underflow=None)['selected140_half_bits'],0x3800)

    def test_flush_and_sqrt_unknown_are_not_filled(self):
        self.assertEqual(evaluate(12,rn_even=True,gradual_underflow=None)['status'],'unknown')
        self.assertEqual(evaluate(12,rn_even=True,gradual_underflow=True)['selected140_half_bits'],48)
        self.assertEqual(evaluate(0,rn_even=True,gradual_underflow=None)['selected140_half_bits'],0)
        self.assertEqual(evaluate(0x3400,rn_even=None,gradual_underflow=None)['status'],'unknown')
        self.assertEqual(evaluate(0x3401,rn_even=True,gradual_underflow=None)['status'],'unknown')
        self.assertEqual(evaluate(0x3401,rn_even=True,gradual_underflow=None,correct_final_sqrt_half=True)['selected140_half_bits'],sqrt_rn(0x3401))

    def test_old_domain_contains_unused_and_unreachable_inputs(self):
        self.assertTrue(classify(0x2c00)['S29_selected_low_covered'])
        self.assertTrue(classify(0x3401)['S29_low_leaf_accepts_input'])
        self.assertFalse(classify(0x3401)['S29_low_leaf_needed_for140'])
        self.assertTrue(classify(0x3c00)['S29_low_leaf_accepts_input'])
        self.assertFalse(classify(0x3c00)['inside_proved_prefix_outer_range'])
        with self.assertRaises(Unknown):evaluate(0x3c00,rn_even=True,gradual_underflow=True)

    def test_window_absence_does_not_become_general_unreachability(self):
        missing=load(E/'square132-proof-s31b.json')['window_only_unknown_boundary_searches']
        self.assertEqual([(r['target_square'],r['mode'])for r in missing],[(0x2bff,'separate'),(0x2bff,'fused')])
        self.assertTrue(all('no general unreachability'in r['scope']for r in missing))

    def test_exact_math_segment_matches_saved_S29_nodes_without_new_execution(self):
        data=load(E/'bright-residual-attribution-s29c.json')
        for p in data['unique_points'].values():
            host={r['SSA']:r['host_bits']for r in p['corrected_stages']}
            for channel,x in enumerate(p['native132_half_bits']):
                result=low_segment(x,Assumptions(True,True,'fused'))
                self.assertTrue(all(result[i]==host[i][channel]for i in range(134,139)))

    def test_old_sources_profiles_and_failure_receipts_unchanged(self):
        p=load(E/'model-precision-v3-s25c6.json')
        self.assertTrue(all(sha(R/n)==h for n,h in p['model_source_sha256'].items()))
        old=load(E/'verification-s30.json')
        self.assertTrue(all(sha(E/n)==h for n,h in old['evidence_sha256'].items()))
        self.assertFalse(load(E/'square140-admission-s31c.json')['old_leaf_or_v3_modified'])


if __name__=='__main__':unittest.main()
