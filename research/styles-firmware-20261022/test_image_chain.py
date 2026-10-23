"""Behavioral source-to-writer tests; no Apple reference or precision promotion."""
from dataclasses import replace
from pathlib import Path
import platform
import unittest
from unittest.mock import patch

import numpy as np

import complete_forward
import pixel_output
from complete_fixture import context
from image_chain import BranchSelection, Numerics, SemanticMasks, run
from leaf_numeric import DomainUnknown
from semantic_tone import Curve1D


PORTABLE = Numerics.EXPERIMENTAL_PORTABLE_POINT


class ImageChainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = context()
        # A small tile isolates branch wiring; larger gradients/steps/edges are
        # exercised independently by the synthetic CLI suite.
        cls.base = run(cls.context, numerics=PORTABLE)
        cls.bright = run(cls.context, numerics=PORTABLE,
                         selection=BranchSelection.EXPERIMENTAL_BRIGHT16)

    def test_bright_is_really_consumed_by_the_writer_under_explicit_cast16(self):
        a, b = self.base, self.bright
        self.assertEqual(a.status, 'model_source_to_writer_complete')
        self.assertEqual(b.status, 'model_source_to_writer_complete')
        np.testing.assert_array_equal(a.model.observations['selected404'].lo,
                                      a.model.observations['skin393'].lo)
        np.testing.assert_array_equal(b.model.observations['selected404'].lo,
                                      b.model.observations['bright400'].lo)
        # Upstream source/producer/skin are unchanged. The selected branch is
        # the trigger for the downstream pixel change, not an injected image.
        for name in ('producer_BG203', 'BG_output', 'working286', 'skin393', 'bright400'):
            np.testing.assert_array_equal(a.model.observations[name].lo,
                                          b.model.observations[name].lo)
        self.assertGreater(np.max(abs(a.model.observations['writer'].lo -
                                     b.model.observations['writer'].lo)), .001)
        self.assertEqual(next(x.selected for x in b.branches if x.destination == 'selected404'), 'bright400')
        self.assertFalse(b.apple_pipeline_verified)
        self.assertFalse(b.provenance['inherits_S25_S29_S30_bit_certification'])

    def test_selected_unknown_blocks_writer_but_unselected_unknown_is_retained(self):
        def unsupported(*args, **kwargs):
            raise DomainUnknown('test sentinel: unavailable bright domain')
        with patch.object(complete_forward, 'bright', unsupported):
            skin = run(self.context, numerics=PORTABLE)
            bright = run(self.context, numerics=PORTABLE,
                         selection=BranchSelection.EXPERIMENTAL_BRIGHT16)
        self.assertIsNotNone(skin.model.writer)
        self.assertTrue(skin.model.internal_unknowns)
        self.assertEqual(bright.status, 'unknown_no_writer')
        self.assertIsNone(bright.model.writer)
        self.assertEqual(len(bright.model.pixel_unknowns), 12)
        self.assertTrue(all(x['operator'] == 'selected404' for x in bright.model.pixel_unknowns.values()))
        self.assertTrue(all('test sentinel' in x['reason'] for x in bright.model.pixel_unknowns.values()))
        self.assertNotIn('writer', bright.model.observations)

    def test_source_changes_reach_generated_maps_and_writer_without_native_oracles(self):
        images = list(self.context.images)
        primary = images[0].copy(); primary[1, 1, :3] *= np.float16(.8)
        images[0] = primary
        changed = replace(self.context, images=tuple(images))
        # Portable execution may not obtain a replacement result through any
        # native-library call, nor read saved JSON intermediate observations.
        with patch('ctypes.CDLL', side_effect=AssertionError('native oracle forbidden')):
            result = run(changed, numerics=PORTABLE)
        for name in ('producer_source24', 'producer_BG203', 'BG_output', 'writer'):
            self.assertGreater(np.max(abs(result.model.observations[name].lo -
                                         self.base.model.observations[name].lo)), 0, name)
        self.assertFalse(result.provenance['native_intermediates_used'])
        self.assertEqual(result.provenance['native_calls'], 0)

    def test_zero_missing_masks_are_explicit_and_equal_explicit_zero_inputs(self):
        missing = run(self.context, numerics=PORTABLE, masks=SemanticMasks())
        zeros = np.zeros(self.context.images[0].shape[:2] + (1,), dtype='f2')
        supplied = run(self.context, numerics=PORTABLE,
                       masks=SemanticMasks(zeros, zeros, zeros))
        self.assertEqual(missing.provenance['synthetic_zero_mask_fallbacks'], ['person', 'skin', 'sky'])
        self.assertEqual(supplied.provenance['synthetic_zero_mask_fallbacks'], [])
        for name in ('raw_person63', 'raw_skin70', 'sky77'):
            self.assertFalse(np.any(missing.model.observations[name].lo))
        np.testing.assert_array_equal(missing.model.observations['writer'].lo,
                                      supplied.model.observations['writer'].lo)
        self.assertTrue(any('nil-texture' in gap for gap in missing.gaps))

    def test_checkpoint_dependencies_and_written_alpha_and_border(self):
        for checkpoint in self.bright.checkpoints:
            self.assertTrue(checkpoint.inputs, checkpoint.name)
            self.assertNotIn('raw context / existing named upstream stages', checkpoint.inputs,
                             checkpoint.name)
            self.assertFalse(checkpoint.value.lo.flags.writeable)
            self.assertTrue(checkpoint.domain)
        cp = {c.name: c for c in self.bright.checkpoints}
        self.assertIn('params.exposure7', cp['bright400'].inputs)
        self.assertEqual(cp['selected404'].inputs, ('bright400',))
        writer = self.bright.model.writer
        rgba = writer.output.pixels.lo
        np.testing.assert_array_equal(rgba[~writer.written_pixels],
                                      self.context.output_initial[~writer.written_pixels])
        self.assertTrue(np.all(rgba[writer.written_pixels, 3] == 1))

    def test_contract_rejects_nonfinite_masks_wrong_layout_and_untyped_controls(self):
        for value in (np.nan, np.inf, -np.inf):
            with self.assertRaises(TypeError):
                SemanticMasks(person=np.full((3, 4, 1), value))
        for value in (-.1, 1.1):
            with self.assertRaises(ValueError):
                SemanticMasks(skin=np.full((3, 4, 1), value))
        with self.assertRaises(ValueError):
            run(self.context, numerics=PORTABLE,
                masks=SemanticMasks(person=np.zeros((1, 1, 1))))
        with self.assertRaises(TypeError):
            run(self.context, numerics='experimental_portable_point')
        with self.assertRaises(TypeError):
            run(self.context, numerics=PORTABLE, selection=16)
        images = list(self.context.images)
        images[6] = np.full_like(images[6], -.1)
        with self.assertRaises(ValueError):
            run(replace(self.context, images=tuple(images)), numerics=PORTABLE)

    def test_real_black_input_retains_zero_denominator_unknown_without_epsilon_repair(self):
        images = list(self.context.images)
        for index in (0, 1):
            image = images[index].copy(); image[..., :3] = 0
            images[index] = image
        black = replace(self.context, images=tuple(images))
        result = run(black, numerics=PORTABLE,
                     selection=BranchSelection.EXPERIMENTAL_BRIGHT16)
        self.assertEqual(result.status, 'unknown_no_writer')
        self.assertIsNone(result.model.writer)
        self.assertTrue(result.model.pixel_unknowns)
        self.assertTrue(all('zero' in reason['reason']
                            for reason in result.model.pixel_unknowns.values()))
        self.assertEqual(result.provenance['native_calls'], 0)

    def test_new_experiment_keeps_pinned_context_and_module_functions_unchanged(self):
        before = self.context.params.view('u4').copy()
        output = pixel_output.forward
        forward = complete_forward.forward
        run(self.context, numerics=PORTABLE,
            selection=BranchSelection.EXPERIMENTAL_BRIGHT16)
        np.testing.assert_array_equal(before, self.context.params.view('u4'))
        self.assertIs(output, pixel_output.forward)
        self.assertIs(forward, complete_forward.forward)
        params = self.context.params.copy(); params.view('u4')[0] = 16
        with self.assertRaises(ValueError):
            replace(self.context, params=params)

    def test_curve_coordinate_contract_and_cross_directory_sources_are_bound(self):
        other = replace(self.context,
                        gtc=Curve1D(self.context.gtc.red_samples, 'different supplied coordinate'))
        result = run(other, numerics=PORTABLE)
        self.assertNotEqual(self.base.provenance['raw_input_sha256'],
                            result.provenance['raw_input_sha256'])
        self.assertIn('../hdr-native/guided_reference_v3.py', result.provenance['source_sha256'])
        self.assertIn('../semantic-styles/spatial_curve_retarget.py', result.provenance['source_sha256'])

    @unittest.skipIf(platform.system() == 'Darwin' and platform.machine() == 'arm64',
                     'Strict host gate is expected only on incompatible platforms')
    def test_strict_host_profile_still_refuses_linux(self):
        with self.assertRaisesRegex(ValueError, 'Darwin arm64'):
            run(self.context, numerics=Numerics.STRICT_HOST_POINT)


if __name__ == '__main__':
    unittest.main()
