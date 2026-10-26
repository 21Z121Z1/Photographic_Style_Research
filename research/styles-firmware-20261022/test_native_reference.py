"""Synthetic receipt tests; these do not execute or certify Apple native code."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from native_reference import (BASE_SINGLE, EXPONENT_SINGLE, classify_math, collect,
                              envelope, unpack, check_root_wrapper)


ROOT_ASM = '''_probe_root:
0000000100001000 mrs x8, FPCR
0000000100001004 fmov s0, w1
0000000100001008 fcvt s0, h0
000000010000100c fsqrt s0, s0
0000000100001010 fmov w2, s0
0000000100001014 fcvt h1, s0
0000000100001018 fmov w3, s1
000000010000101c mrs x9, FPCR
_main:
0000000100001020 ret
'''


class NativeReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        certificate = json.loads((Path(__file__).parent/'evidence/sqrt-domain-certificate-s32c.json').read_text())
        cls.raw = {'schema':'psr-fresh-apple-cpu-v1', 'historical_sealed_image_loaded':False,
                   'target_uuid':'1'*32, 'target_image':'synthetic.dylib', 'target_symbol':'powf',
                   'target_symbol_exact':True, 'target_image_offset':4096,
                   'thread_before':42, 'thread_after':42, 'pow_calls':1, 'sqrt_instructions':2047,
                   'power':{'input_half_bits':[0x2b8f,0x36aa],
                            'input_single_bits':[BASE_SINGLE,EXPONENT_SINGLE],
                            'output_single_bits':0x3e9da000, 'output_half_bits':0x34ed,
                            'fpcr_before':0, 'fpcr_after':0},
                   'sqrt_rows':[[r['input_half_bits'],r['correctly_RN_single_sqrt_bits'],
                                 r['RN_single_to_half_bits'],0,0] for r in certificate['rows']]}

    def test_full_finite_sqrt_certificate_comparison_and_scope(self):
        result = classify_math(self.raw)
        self.assertEqual(result['sqrt_observations'],2047)
        self.assertEqual(result['sqrt_single_or_half_mismatches'],0)
        self.assertTrue(result['pow_matches_ideal_half_for_this_input'])
        self.assertFalse(result['original_sealed_image_verified'])
        self.assertFalse(result['historical_calls_certified'])
        self.assertFalse(result['full_pipeline_verified'])

    def test_observed_numeric_mismatch_is_retained(self):
        raw = copy.deepcopy(self.raw)
        raw['sqrt_rows'][0][1] += 1
        result = classify_math(raw)
        self.assertEqual(result['sqrt_single_or_half_mismatches'],1)
        self.assertEqual(result['sqrt_failure_examples'][0]['input_half_bits'],0x3401)

    def test_missing_reordered_duplicate_and_wrong_identity_are_rejected(self):
        for kind in ('missing','duplicate','reordered','identity','thread','target'):
            raw = copy.deepcopy(self.raw)
            if kind == 'missing': raw['sqrt_rows'].pop()
            if kind == 'duplicate': raw['sqrt_rows'][1] = raw['sqrt_rows'][0]
            if kind == 'reordered': raw['sqrt_rows'].reverse()
            if kind == 'identity': raw['historical_sealed_image_loaded'] = True
            if kind == 'thread': raw['thread_after'] += 1
            if kind == 'target': raw['target_uuid'] = ''
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                classify_math(raw)

    def test_wrong_mode_and_changed_FPCR_are_rejected(self):
        for before,after in ((0,1),(1<<22,1<<22),(1<<26,1<<26)):
            raw = copy.deepcopy(self.raw)
            raw['sqrt_rows'][0][-2:] = [before,after]
            with self.assertRaises(ValueError):classify_math(raw)

    def test_transport_preserves_every_observed_bit_and_rejects_tampering(self):
        wrapped = envelope(self.raw)
        self.assertEqual(unpack(wrapped),self.raw)
        wrapped['sha256'] = '0'*64
        with self.assertRaises(ValueError):unpack(wrapped)

    def test_root_window_rejects_a_call_removed_instruction_or_FPCR_write(self):
        self.assertEqual(check_root_wrapper(ROOT_ASM)['FSQRT_instructions'],1)
        for bad in (ROOT_ASM.replace('fsqrt s0, s0','bl _sqrtf'),
                    ROOT_ASM.replace('fcvt s0, h0','nop'), ROOT_ASM+'\nmsr FPCR, x0\n'):
            with self.assertRaises(ValueError):check_root_wrapper(bad)

    def test_linux_never_silently_runs_a_substitute(self):
        with tempfile.TemporaryDirectory() as folder, patch('native_reference.platform.system',return_value='Linux'):
            out=Path(folder)/'native'
            with self.assertRaises(RuntimeError):collect(out)
            self.assertFalse(out.exists())


if __name__ == '__main__':
    unittest.main()
