"""S32 full-domain certificate tests, no native or model-pipeline execution."""
from fractions import Fraction as Q
from pathlib import Path
from unittest.mock import patch
import copy,ctypes,math,unittest
import numpy as np
from baseline_archive import sha
from context_color_api import load
from sqrt_double_round import FIRST,LAST,COUNT,single_value,sqrt32_rn,row,verify_row
from square132_contract import value as half_value,rn as half_rn

R=Path(__file__).parent
E=R/'evidence'


class SqrtDoubleRoundTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.certificate=load(E/'sqrt-domain-certificate-s32c.json')

    def test_complete_domain_no_holes_duplicates_or_floating_samples(self):
        c=self.certificate
        self.assertEqual(COUNT,2047)
        self.assertEqual([r['input_half_bits']for r in c['rows']],list(range(FIRST,LAST+1)))
        self.assertEqual(c['scaled_input_bin_counts'],[1023,1024])
        self.assertFalse(c['float_or_libm_used_for_mathematics'])

    def test_all2047_independent_exact_midpoint_cells(self):
        self.assertTrue(all(verify_row(r)for r in self.certificate['rows']))
        self.assertEqual(self.certificate['counterexample_count'],0)
        self.assertEqual(self.certificate['single_to_half_midpoint_hits'],0)

    def test_endpoint_inputs_are_included_and_quarter_itself_is_excluded(self):
        first,last=self.certificate['rows'][0],self.certificate['rows'][-1]
        self.assertEqual(first['input_half_bits'],0x3401)
        self.assertEqual(last['input_half_bits'],0x3bff)
        self.assertEqual(first['ideal_half_sqrt_bits'],0x3800)
        self.assertEqual(last['ideal_half_sqrt_bits'],0x3bff)
        for x in [0x3400,0x3c00]:
            with self.assertRaises(ValueError):sqrt32_rn(x)

    def test_f32_decoder_is_exact_and_rejects_nonfinite(self):
        self.assertEqual(single_value(0x3f000000),Q(1,2))
        self.assertEqual(single_value(0x3f001000),Q(2049,4096))
        self.assertEqual(single_value(0x3f800000),Q(1))
        for b in [0x7f800000,0x7fc00000,0xff800000]:
            with self.assertRaises(TypeError):single_value(b)

    def test_generator_needs_no_floating_sqrt_or_loaded_native_code(self):
        with patch('math.sqrt',side_effect=AssertionError('not an exact certificate')), \
             patch('numpy.sqrt',side_effect=AssertionError('not an exact certificate')), \
             patch('ctypes.CDLL',side_effect=AssertionError('no native execution')):
            self.assertTrue(verify_row(row(FIRST)))
            self.assertTrue(verify_row(row(LAST)))

    def test_corrupted_single_result_and_half_result_are_detected(self):
        r=copy.deepcopy(self.certificate['rows'][100]);r['correctly_RN_single_sqrt_bits']+=1
        with self.assertRaises(ValueError):verify_row(r)
        r=copy.deepcopy(self.certificate['rows'][100]);r['ideal_half_sqrt_bits']+=1
        with self.assertRaises(ValueError):verify_row(r)

    def test_parity_and_strict_root_separation_are_not_empirical_counts(self):
        for code in range(FIRST,LAST+1):
            scaled=half_value(code)*(1<<24)
            self.assertEqual(scaled.denominator,1)
            self.assertEqual(scaled.numerator%2,0)
        for m in range(1024,2048):
            midpoint=Q(2*m+1,4096)
            self.assertEqual((midpoint**2*(1<<24)).denominator,1)
            self.assertEqual((midpoint**2*(1<<24)).numerator%2,1)
            self.assertLess(midpoint,1)

    def test_general_real_input_double_rounding_counterexample_outside_half_domain(self):
        # A rational root just above a half midpoint rounds to the midpoint in
        # f32, then ties to the lower even half. Its square is NOT a half input.
        midpoint=Q(2049,4096);root=midpoint+Q(1,1<<27);input_real=root*root
        s=0x3f001000
        self.assertEqual(single_value(s),midpoint)
        lower=(single_value(s-1)+single_value(s))/2
        upper=(single_value(s)+single_value(s+1))/2
        self.assertTrue(lower<root<upper)
        self.assertEqual(half_rn(root),0x3801)
        self.assertEqual(half_rn(single_value(s)),0x3800)
        self.assertNotEqual(half_value(half_rn(input_real)),input_real)

    def test_machine_chain_uses_hardware_single_sqrt_not_external_libm(self):
        d=load(E/'sqrt-static-s32a.json')
        self.assertTrue(d['psr_sqrt_scalar_is_direct_f32_FSQRT_no_libm_call'])
        self.assertTrue(d['half_machine_extension_call_truncation_confirmed'])
        self.assertTrue(d['vector_three_scalar_calls_confirmed'])
        self.assertEqual(d['f32_FSQRT_addresses'],['15914'])
        self.assertEqual(d['machine_functions']['_psr_sqrt_scalar']['call_targets'],[])
        self.assertFalse(d['FPCR_runtime_state_measured'])
        self.assertFalse(d['original_GPU_or_iOS_execution'])

    def test_existing_S29_selected_host_observations_remain_finite_calibration(self):
        data=load(E/'bright-residual-attribution-s29c.json');by_input={r['input_half_bits']:r for r in self.certificate['rows']}
        count=0;unique=set()
        for p in data['unique_points'].values():
            roots=next(s['host_bits']for s in p['corrected_stages']if s['SSA']==133)
            for x,h in zip(p['native132_half_bits'],roots):
                if FIRST<=x<=LAST:
                    self.assertEqual(by_input[x]['ideal_half_sqrt_bits'],h)
                    count+=1;unique.add(x)
        self.assertEqual(count,2)
        self.assertEqual(len(unique),1)

    def test_old_model_and_S29_to31_evidence_unchanged(self):
        p=load(E/'model-precision-v3-s25c6.json')
        self.assertEqual(len(p['model_source_sha256']),243)
        self.assertTrue(all(sha(R/n)==h for n,h in p['model_source_sha256'].items()))
        previous=load(E/'verification-s31.json')
        self.assertTrue(all(sha(E/n)==h for n,h in previous['evidence_sha256'].items()))


if __name__=='__main__':unittest.main()
