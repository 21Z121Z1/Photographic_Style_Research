"""Logic and storage-contract checks; synthetic masks do not test segmentation."""
from dataclasses import replace
import unittest

import numpy as np

from texture_style_adapter import (ColorDomain, TransferDomain, HalfRGB, HalfMask,
    UnderEyeMasks, UnderEyeParameters, UnderEyeContext, MissingMaskPolicy,
    TextureEffect, apply_under_eye, run_conditional_texture, HELPER_SHA256)


class TextureAdapterTest(unittest.TestCase):
    def setUp(self):
        self.domain = ColorDomain('synthetic RGB primaries', TransferDomain.LINEAR, 'identity',
                                  'arbitrary relative radiance; no Apple camera calibration')
        x = np.linspace(0, 1, 8, dtype='f2')
        # Gradient, exposure steps and a hard edge; generated in memory.
        rgb = np.stack([np.tile(x, (4, 1)),
                        np.tile(np.array([0, .01, .0625, .125, .25, .5, 1, 2], 'f2'), (4, 1)),
                        np.tile(np.array([0, 0, 0, 0, 1, 1, 1, 1], 'f2'), (4, 1))], axis=-1)
        self.source = HalfRGB(rgb, self.domain)
        self.edited = HalfRGB((rgb.astype('f4') * .75 + .1).astype('f2'), self.domain)
        zero = HalfMask(np.zeros((4, 8), 'f2'), 'program generated exclusion control')
        one = HalfMask(np.ones((4, 8), 'f2'), 'program generated support control')
        self.masks = UnderEyeMasks(one, one, zero, zero, zero, zero, zero, one)
        self.context = UnderEyeContext(self.edited, self.masks,
                                     UnderEyeParameters(np.float32(.5), np.float32(1)))

    def test_reused_helper_identity_is_bound(self):
        self.assertEqual(HELPER_SHA256, 'e588f764b4b36f154904575a4cfb2a56ced22d11cda7b26637e6aa2fe31329ea')

    def test_zero_and_full_strength_endpoints(self):
        for mix, strength, expected in [(1, 0, self.source.values),
                                        (0, 1, self.source.values),
                                        (1, 1, self.edited.values)]:
            c = replace(self.context, parameters=UnderEyeParameters(np.float32(mix), np.float32(strength)))
            r = apply_under_eye(self.source, c)
            np.testing.assert_array_equal(r.output.values.view('u2'), expected.view('u2'))
            self.assertFalse(r.identity_fallback)

    def test_semantic_support_and_exclusion_footprints(self):
        support = np.zeros((4, 8), 'f2'); support[:, :4] = 1
        exclude = np.zeros_like(support); exclude[1:3, :2] = 1
        m = replace(self.masks, face=HalfMask(support, 'synthetic half-image face support'),
                    hair=HalfMask(exclude, 'synthetic hair exclusion rectangle'))
        r = apply_under_eye(self.source, replace(self.context, masks=m))
        inactive = (support == 0) | (exclude == 1)
        np.testing.assert_array_equal(r.output.values[inactive].view('u2'), self.source.values[inactive].view('u2'))
        self.assertTrue(np.any(r.output.values[~inactive] != self.source.values[~inactive]))
        self.assertFalse(r.real_segmentation_verified)

    def test_exclusion_above_face_clamps_weight_to_zero(self):
        m = replace(self.masks, hair=self.masks.face, lips=self.masks.face)
        r = apply_under_eye(self.source, replace(self.context, masks=m))
        np.testing.assert_array_equal(r.output.values.view('u2'), self.source.values.view('u2'))

    def test_parameter_changes_propagate_to_stored_output(self):
        outputs = []
        for strength in (0, .5, 1):
            c = replace(self.context, parameters=UnderEyeParameters(np.float32(.5), np.float32(strength)))
            outputs.append(apply_under_eye(self.source, c).output.values)
        self.assertTrue(np.any(outputs[0] != outputs[1]))
        self.assertTrue(np.any(outputs[1] != outputs[2]))
        lo, hi = np.minimum(outputs[0], outputs[2]), np.maximum(outputs[0], outputs[2])
        self.assertTrue(np.all((outputs[1] >= lo) & (outputs[1] <= hi)))

    def test_half_tie_and_subnormal_storage_contract(self):
        source = HalfRGB(np.array([[[1, 0, -0.0]]], 'f2'), self.domain)
        edited = HalfRGB(np.array([[[np.nextafter(np.float16(1), np.float16(2)),
                                     np.nextafter(np.float16(0), np.float16(1)), 0]]], 'f2'), self.domain)
        one = HalfMask(np.ones((1, 1), 'f2'), 'synthetic'); zero = HalfMask(np.zeros((1, 1), 'f2'), 'synthetic')
        c = UnderEyeContext(edited, UnderEyeMasks(one, one, zero, zero, zero, zero, zero, one),
                            UnderEyeParameters(np.float32(.5), np.float32(1)))
        r = apply_under_eye(source, c)
        # Explicit NumPy RN storage ties choose even endpoints; no Apple FPCR claim.
        self.assertEqual(int(r.output.values.view('u2')[0, 0, 0]), 0x3c00)
        self.assertEqual(int(r.output.values.view('u2')[0, 0, 1]), 0)
        self.assertFalse(r.native_half_or_sampler_verified)

    def test_nonfinite_and_wrong_precision_rejected(self):
        for v in (np.nan, np.inf, -np.inf):
            a = self.source.values.copy(); a[0, 0, 0] = v
            with self.assertRaises(ValueError): HalfRGB(a, self.domain)
            a = self.masks.face.values.copy(); a[0, 0] = v
            with self.assertRaises(ValueError): HalfMask(a, 'negative control')
        with self.assertRaises(TypeError): HalfRGB(self.source.values.astype('f4'), self.domain)
        with self.assertRaises(TypeError): UnderEyeParameters(.5, np.float32(1))

    def test_parameter_and_mask_ranges_rejected(self):
        for v in (-.1, 1.1, np.nan, np.inf):
            with self.assertRaises(ValueError): UnderEyeParameters(np.float32(v), np.float32(1))
        with self.assertRaises(ValueError): HalfMask(np.full((4, 8), -.1, 'f2'), 'negative control')

    def test_missing_masks_require_explicit_fallback(self):
        c = replace(self.context, masks=replace(self.masks, instance=None))
        with self.assertRaisesRegex(ValueError, 'instance'): apply_under_eye(self.source, c)
        r = apply_under_eye(self.source, replace(c, missing_mask_policy=MissingMaskPolicy.IDENTITY))
        self.assertTrue(r.identity_fallback)
        self.assertEqual(r.missing_masks, ('instance',))
        np.testing.assert_array_equal(r.output.values.view('u2'), self.source.values.view('u2'))

    def test_geometry_and_color_domain_mismatch_rejected(self):
        c = replace(self.context, edited=HalfRGB(self.edited.values[:2], self.domain))
        with self.assertRaises(ValueError): apply_under_eye(self.source, c)
        other = ColorDomain('sRGB', TransferDomain.NONLINEAR, 'sRGB transfer', 'synthetic display-referred')
        c = replace(self.context, edited=HalfRGB(self.edited.values, other))
        with self.assertRaises(ValueError): apply_under_eye(self.source, c)
        c = replace(self.context, masks=replace(self.masks, blend=HalfMask(np.ones((1, 1), 'f2'), 'synthetic')))
        with self.assertRaises(ValueError): apply_under_eye(self.source, c)

    def test_source_and_checkpoints_are_immutable(self):
        source = self.source.values.copy(); wrapped = HalfRGB(source, self.domain); source[:] = 0
        self.assertTrue(np.any(wrapped.values != 0))
        r = apply_under_eye(wrapped, self.context)
        for a in [r.output.values, *(p.values for p in r.checkpoints)]:
            with self.assertRaises(ValueError): a.flat[0] = 0

    def test_unimplemented_effect_never_yields_a_final_image(self):
        r = run_conditional_texture(self.source, effects=(TextureEffect.UNDER_EYE, TextureEffect.SKIN_SMOOTH,
                                                         TextureEffect.MATTIFY), under_eye=self.context)
        self.assertIsNone(r.output)
        self.assertEqual(r.completed_effects, (TextureEffect.UNDER_EYE,))
        self.assertIn('independent backend unavailable', r.gaps[0])
        self.assertEqual(r.checkpoints[-1].name, 'stored_output')
        self.assertFalse(r.full_texture_pipeline_verified)
        self.assertFalse(r.apple_order_verified)

    def test_fallback_does_not_hide_later_unimplemented_effect(self):
        c = replace(self.context, masks=replace(self.masks, face=None), missing_mask_policy=MissingMaskPolicy.IDENTITY)
        r = run_conditional_texture(self.source, effects=(TextureEffect.UNDER_EYE, TextureEffect.MATTIFY), under_eye=c)
        self.assertIsNone(r.output)
        self.assertEqual(len(r.gaps), 2)
        self.assertEqual(r.completed_effects, ())

    def test_empty_and_missing_context_are_explicit(self):
        r = run_conditional_texture(self.source, effects=())
        self.assertIs(r.output, self.source)
        r = run_conditional_texture(self.source, effects=(TextureEffect.UNDER_EYE,))
        self.assertIsNone(r.output)
        self.assertIn('context missing', r.gaps[0])
        with self.assertRaises(TypeError): run_conditional_texture(self.source, effects=['UnderEyeBrightening'])


if __name__ == '__main__':
    unittest.main()
