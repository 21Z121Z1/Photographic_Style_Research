"""Synthetic conditional blend checks; no Apple native reference is used."""
import unittest

import numpy as np

from skin_smoothing_final import SkinSmoothingContext, apply_skin_smoothing_final
from texture_style_adapter import ColorDomain, HalfRGB, TransferDomain
from texture_style_adapter import (HalfMask, TextureEffect, UnderEyeContext, UnderEyeMasks,
                                   UnderEyeParameters, run_conditional_texture)


class SkinSmoothingFinalTests(unittest.TestCase):
    def setUp(self):
        self.domain = ColorDomain('synthetic RGB', TransferDomain.LINEAR, 'identity', 'synthetic scene')
        self.source = HalfRGB(np.full((3, 4, 3), .5, dtype='f2'), self.domain)
        self.smooth = HalfRGB(np.full((3, 4, 3), .25, dtype='f2'), self.domain)
        self.blurred = HalfRGB(np.full((3, 4, 3), .125, dtype='f2'), self.domain)
        self.zero = np.zeros((3, 4), dtype='f4')

    def context(self, a=0., b=0.):
        return SkinSmoothingContext(self.smooth, self.blurred,
                                    np.full((3, 4), a, dtype='f4'), np.full((3, 4), b, dtype='f4'))

    def test_zero_weights_preserve_all_pixels_including_border(self):
        pixels = np.linspace(-.5, 2, 36, dtype='f2').reshape(3, 4, 3)
        pixels[0, 0] = [-0., 0., -0.]
        source = HalfRGB(pixels, self.domain)
        result = apply_skin_smoothing_final(source, self.context())
        np.testing.assert_array_equal(result.output.values.view('u2'), pixels.view('u2'))
        self.assertTrue(result.model_only)
        self.assertFalse(result.native_half_or_sampler_verified)
        self.assertFalse(result.upstream_reconstruction_verified)
        self.assertFalse(result.apple_order_verified)

    def test_smoothing_and_texture_addback_have_analytical_outputs(self):
        smooth = apply_skin_smoothing_final(self.source, self.context(a=.5))
        texture = apply_skin_smoothing_final(self.source, self.context(a=.5, b=.5))
        np.testing.assert_array_equal(smooth.output.values, .375)
        np.testing.assert_array_equal(texture.output.values, .4375)
        self.assertEqual(texture.checkpoints[-2].values.dtype, np.dtype('f8'))
        self.assertEqual(texture.output.values.dtype, np.dtype('f2'))
        self.assertEqual(len(texture.checkpoints), 7)
        self.assertTrue(all(not c.values.flags.writeable for c in texture.checkpoints))

    def test_coefficients_are_copied_and_no_native_range_is_invented(self):
        a = np.full((3, 4), -1, dtype='f4')
        context = SkinSmoothingContext(self.smooth, self.blurred, a, self.zero)
        a[:] = 2
        self.assertTrue(np.all(context.a == -1))
        self.assertFalse(context.a.flags.writeable)
        result = apply_skin_smoothing_final(self.source, context)
        np.testing.assert_array_equal(result.output.values, .75)

    def test_invalid_coefficient_storage_geometry_and_nonfinite_are_rejected(self):
        for invalid in (self.zero.astype('f8'), self.zero.astype('f2'), self.zero.tolist(),
                        self.zero.astype('complex64')):
            with self.subTest(type=type(invalid)), self.assertRaises(TypeError):
                SkinSmoothingContext(self.smooth, self.blurred, invalid, self.zero)
        for invalid in (np.zeros((4, 3), dtype='f4'), np.full((3, 4), np.nan, dtype='f4')):
            with self.assertRaises(ValueError):
                SkinSmoothingContext(self.smooth, self.blurred, invalid, self.zero)

    def test_domain_shape_and_unsaturated_reconstruction_are_rejected(self):
        other = ColorDomain('other RGB', TransferDomain.LINEAR, 'identity', 'synthetic scene')
        with self.assertRaises(ValueError):
            apply_skin_smoothing_final(HalfRGB(self.source.values, other), self.context())
        with self.assertRaises(ValueError):
            apply_skin_smoothing_final(HalfRGB(np.zeros((2, 4, 3), dtype='f2'), self.domain), self.context())
        with self.assertRaises(ValueError):
            SkinSmoothingContext(HalfRGB(np.full((3, 4, 3), 2, dtype='f2'), self.domain),
                                 self.blurred, self.zero, self.zero)
        with self.assertRaises(TypeError):
            apply_skin_smoothing_final(self.source.values, self.context())

    def test_half_overflow_is_rejected_without_clipping(self):
        with self.assertRaises(FloatingPointError):
            apply_skin_smoothing_final(self.source, self.context(a=1e10))

    def test_final_blend_composes_in_requested_order_with_under_eye(self):
        one = HalfMask(np.ones((3, 4), dtype='f2'), 'synthetic')
        zero = HalfMask(np.zeros((3, 4), dtype='f2'), 'synthetic')
        under_eye = UnderEyeContext(
            HalfRGB(np.full((3, 4, 3), .75, dtype='f2'), self.domain),
            UnderEyeMasks(one, one, zero, zero, zero, zero, zero, one),
            UnderEyeParameters(np.float32(1), np.float32(1)))
        final = TextureEffect.SKIN_SMOOTH_FINAL
        eye = TextureEffect.UNDER_EYE
        forward = run_conditional_texture(self.source, effects=(eye, final),
                                          under_eye=under_eye, skin_smooth_final=self.context(a=.5))
        reverse = run_conditional_texture(self.source, effects=(final, eye),
                                          under_eye=under_eye, skin_smooth_final=self.context(a=.5))
        np.testing.assert_array_equal(forward.output.values, .5)
        np.testing.assert_array_equal(reverse.output.values, .75)
        self.assertEqual(forward.completed_effects, (eye, final))
        self.assertEqual(forward.checkpoints[-1].name, '1.SkinSmoothingFinalBlendOnly.stored_output')
        self.assertFalse(forward.apple_order_verified)
        self.assertFalse(forward.full_texture_pipeline_verified)

    def test_conditional_final_blend_never_unlocks_the_full_effect(self):
        final = TextureEffect.SKIN_SMOOTH_FINAL
        missing = run_conditional_texture(self.source, effects=(final,))
        self.assertIsNone(missing.output)
        self.assertIn('external reconstruction/blur/weights missing', missing.gaps[0])
        blocked = run_conditional_texture(self.source, effects=(final, TextureEffect.SKIN_SMOOTH),
                                          skin_smooth_final=self.context(a=.5))
        self.assertIsNone(blocked.output)
        self.assertEqual(blocked.completed_effects, (final,))
        self.assertEqual(len(blocked.checkpoints), 7)
        np.testing.assert_array_equal(blocked.checkpoints[-1].values, .375)

    def test_repeated_final_blends_consume_previous_stored_output(self):
        final = TextureEffect.SKIN_SMOOTH_FINAL
        result = run_conditional_texture(self.source, effects=(final, final),
                                         skin_smooth_final=self.context(a=.5))
        np.testing.assert_array_equal(result.output.values, .3125)
        self.assertEqual(len({cp.name for cp in result.checkpoints}), 14)


if __name__ == '__main__':
    unittest.main()
