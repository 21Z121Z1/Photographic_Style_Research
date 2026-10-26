"""Exact arithmetic plus replay of finite retained native GPU observations."""
import json
import hashlib
from pathlib import Path
import unittest

import numpy as np

from native_texture_reference import compare_independent_half
from native_reference import encoded
from texture_style_adapter import (ColorDomain,TransferDomain,HalfRGB,HalfMask,UnderEyeContext,
                                   UnderEyeMasks,UnderEyeParameters,TextureEffect,run_conditional_texture)
from under_eye_half import HalfArithmetic,apply_under_eye_half


class ExactUnderEyeHalfTests(unittest.TestCase):
    def setUp(self):
        self.domain=ColorDomain('synthetic RGB',TransferDomain.LINEAR,'identity','arbitrary synthetic samples')
        self.source=HalfRGB(np.ones((1,1,3),dtype='f2'),self.domain)
        self.one=HalfMask(np.ones((1,1),dtype='f2'),'synthetic')
        self.zero=HalfMask(np.zeros((1,1),dtype='f2'),'synthetic')
        self.masks=UnderEyeMasks(self.one,self.one,self.zero,self.zero,self.zero,self.zero,self.zero,self.one)

    def context(self,edited,mix=.5):
        return UnderEyeContext(HalfRGB(edited,self.domain),self.masks,
                               UnderEyeParameters(np.float32(mix),np.float32(1)))

    def test_half_tie_and_subnormal_are_rounded_exactly_under_explicit_assumptions(self):
        source=HalfRGB(np.array([[[1,0,0]]],dtype='f2'),self.domain)
        edited=np.array([[[np.nextafter(np.float16(1),np.float16(2)),
                           np.nextafter(np.float16(0),np.float16(1)),1]]],dtype='f2')
        result=apply_under_eye_half(source,self.context(edited),arithmetic=HalfArithmetic.RN_GRADUAL_TWO_FMA)
        self.assertEqual(result.output.values.view('u2').tolist(),[[[0x3c00,0,0x3800]]])
        self.assertFalse(result.arbitrary_native_inputs_verified)
        self.assertFalse(result.sampler_verified)

    def test_arithmetic_assumptions_and_sample_box_are_not_silently_inferred(self):
        context=self.context(np.zeros((1,1,3),dtype='f2'))
        with self.assertRaises(TypeError):apply_under_eye_half(self.source,context,arithmetic='two-fma')
        with self.assertRaises(ValueError):
            apply_under_eye_half(HalfRGB(np.full((1,1,3),3,dtype='f2'),self.domain),context,
                                  arithmetic=HalfArithmetic.RN_GRADUAL_TWO_FMA)

    def test_exact_backend_is_an_explicit_reusable_chain_choice(self):
        result=run_conditional_texture(self.source,effects=(TextureEffect.UNDER_EYE,),
                 under_eye=self.context(np.zeros((1,1,3),dtype='f2')),
                 under_eye_arithmetic=HalfArithmetic.RN_GRADUAL_TWO_FMA)
        np.testing.assert_array_equal(result.output.values,.5)
        self.assertEqual(result.checkpoints[0].name,'half_weight')
        self.assertFalse(result.full_texture_pipeline_verified)
        self.assertTrue(result.model_only)

    def test_independent_exact_model_matches_all_18_retained_native_image_and_weight_cases(self):
        fixture=Path(__file__).parent/'evidence/native-reference-20261026/texture-24f7bbe.json'
        record=json.loads(fixture.read_text())
        cpu=json.loads((fixture.parent/'cpu-24f7bbe.json').read_text())
        self.assertEqual(hashlib.sha256(encoded(record)).hexdigest(),cpu['texture_report_sha256'])
        self.assertEqual(record['git']['HEAD'],'24f7bbedf4d8eece715d539b100e4c6bb4c92256')
        result=compare_independent_half(record['native'],record['inputs'])
        self.assertEqual(len(result['rows']),18)
        self.assertTrue(result['all_observed_RGB_bits_equal'])
        self.assertEqual(sum(row['weight_half_bit_mismatches'] for row in result['rows']),0)
        self.assertFalse(result['native_intermediates_used'])
        self.assertFalse(result['arbitrary_native_inputs_verified'])


if __name__=='__main__':unittest.main()
