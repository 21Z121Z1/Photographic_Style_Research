"""Isolated parameter effects, mutation guards and honest failure/placement labels."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from image_chain import BranchSelection, Numerics, run
from module_sensitivity import (Intervention, PARAMETER_EDITS, TEXTURE_STRENGTHS,
                                _context_arrays, _context_contract, apply, execute,
                                stage_difference, under_eye_after_writer)
from synthetic_inputs import MaskPattern, Pattern, SyntheticSpec, make_context


PORTABLE = Numerics.EXPERIMENTAL_PORTABLE_POINT


class ModuleSensitivityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Tiny, all-one semantic masks make every intended skin intervention
        # observable without implying that synthetic masks identify real people.
        cls.spec = SyntheticSpec(Pattern.GRADIENT, 2, 2, MaskPattern.ONE)
        cls.context = make_context(cls.spec)
        cls.temp = tempfile.TemporaryDirectory()
        cls.output = Path(cls.temp.name)/'sensitivity'
        with patch('ctypes.CDLL', side_effect=AssertionError('Native oracle forbidden')):
            cls.report = execute(cls.output, spec=cls.spec, numerics=PORTABLE,
                                 selection=BranchSelection.EXPERIMENTAL_BRIGHT16)
        cls.rows = {row['intervention']: row for row in cls.report['runs']}

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_every_intervention_changes_only_its_declared_raw_inputs(self):
        before = _context_arrays(self.context)
        for intervention in Intervention:
            changed = apply(self.context, intervention)
            after = _context_arrays(changed.context)
            actual = {path for path in before if before[path].tobytes() != after[path].tobytes()}
            self.assertEqual(actual, {change.path for change in changed.changes}, intervention.value)
            self.assertLessEqual(actual, set(changed.permitted_paths))
            self.assertEqual(_context_contract(changed.context), _context_contract(self.context))
            if intervention in PARAMETER_EDITS:
                self.assertEqual(actual, {f'params[{PARAMETER_EDITS[intervention][0]}]'})
            if intervention in TEXTURE_STRENGTHS:
                self.assertFalse(actual)
                self.assertEqual(changed.texture_strength, TEXTURE_STRENGTHS[intervention])
        # Applying every intervention did not mutate the shared baseline.
        fresh = make_context(self.spec)
        self.assertEqual(self.context.params.tobytes(), fresh.params.tobytes())
        for a, b in zip(self.context.images, fresh.images):
            self.assertEqual(a.tobytes(), b.tobytes())

    def test_raw_gtc_ltm_and_skin_controls_have_recorded_real_stage_effects(self):
        expectations = ((Intervention.GTC_IDENTITY, 'producer_BG203'),
                        (Intervention.GTC_WEIGHT_ZERO, 'producer_BG203'),
                        (Intervention.GTC_WEIGHT_ONE, 'producer_BG203'),
                        (Intervention.LTM_FG_NEUTRAL, 'precomputed335'),
                        (Intervention.SKIN_THETA9, 'skin393'),
                        (Intervention.SKIN_THETA10, 'skin393'))
        for case, stage in expectations:
            row = self.rows[case.value]
            self.assertEqual(row['status'], 'model_source_to_writer_complete', case.value)
            self.assertGreater(row['stage_differences'][stage]['max_absolute_error'], 0, case.value)
            self.assertEqual(row['stage_differences']['source38']['max_absolute_error'], 0)
            self.assertIn('rmse', row['final_image_difference'])
            self.assertEqual(sum(x['count'] for x in row['final_image_difference']['histogram']), 12)

    def test_bg_ltm_is_inactive_for_full_person_and_active_for_zero_person(self):
        inactive = self.rows[Intervention.LTM_BG_NEUTRAL.value]
        self.assertEqual(inactive['stage_differences']['precomputed335']['max_absolute_error'], 0)
        self.assertEqual(inactive['final_image_difference']['max_absolute_error'], 0)
        # Person=1 selects the FG semantic mix. Person=0 isolates BG and turns
        # the same declared edit into a real stage/output change.
        context = make_context(SyntheticSpec(Pattern.GRADIENT, 2, 2, MaskPattern.ZERO))
        baseline = run(context, numerics=PORTABLE, selection=BranchSelection.EXPERIMENTAL_BRIGHT16)
        changed = run(apply(context, Intervention.LTM_BG_NEUTRAL).context,
                      numerics=PORTABLE, selection=BranchSelection.EXPERIMENTAL_BRIGHT16)
        self.assertEqual(changed.status, 'model_source_to_writer_complete')
        for name in ('precomputed335', 'writer'):
            self.assertGreater(np.max(abs(baseline.model.observations[name].lo -
                                         changed.model.observations[name].lo)), 0)

    def test_bright_zero_exposure_preserves_selected_failure_without_writer(self):
        row = self.rows[Intervention.BRIGHT_EXPOSURE_ZERO.value]
        self.assertEqual(row['status'], 'unknown_no_writer')
        self.assertNotIn('final_image_sha256', row)
        self.assertTrue(row['pixel_unknowns'])
        self.assertTrue(all(v['operator'] == 'selected404' for v in row['pixel_unknowns'].values()))
        self.assertEqual(row['stage_differences']['writer']['status'], 'actual_checkpoint_unavailable')
        self.assertEqual(row['target_Apple_native_calls'], 0)

    def test_inactive_bright_exposure_does_not_change_cast0_writer(self):
        baseline = run(self.context, numerics=PORTABLE, selection=BranchSelection.CONTEXT)
        changed = apply(self.context, Intervention.BRIGHT_EXPOSURE_ZERO)
        result = run(changed.context, numerics=PORTABLE, selection=BranchSelection.CONTEXT)
        self.assertEqual(result.status, 'model_source_to_writer_complete')
        self.assertTrue(result.model.internal_unknowns)
        np.testing.assert_array_equal(baseline.model.observations['writer'].lo,
                                      result.model.observations['writer'].lo)
        self.assertEqual(next(b.selected for b in result.branches if b.destination == 'selected404'), 'skin393')

    def test_zero_masks_change_named_sampling_stages_and_are_not_segmentation_claims(self):
        for intervention, name in ((Intervention.PERSON_ZERO, 'raw_person63'),
                                   (Intervention.SKIN_ZERO, 'raw_skin70')):
            row = self.rows[intervention.value]
            self.assertEqual(row['stage_differences'][name]['max_absolute_error'], 1)
            self.assertIn('not a segmentation result', row['raw_changes'][0]['meaning'])

    def test_texture_strength_endpoints_and_midpoint_are_caller_selected_post_writer(self):
        errors = []
        for intervention in TEXTURE_STRENGTHS:
            row = self.rows[intervention.value]
            self.assertEqual(row['status'], 'model_source_to_writer_complete')
            self.assertEqual(row['stage_differences']['writer']['max_absolute_error'], 0)
            texture = row['texture']
            self.assertFalse(texture['apple_order_verified'])
            self.assertFalse(texture['full_texture_pipeline_verified'])
            self.assertFalse(texture['native_half_or_sampler_verified'])
            self.assertEqual(len(texture['mask_sha256']), 8)
            self.assertEqual(texture['written_roi_yxyx'], [1, 1, 3, 3])
            self.assertIn('unidentified primaries', texture['source_domain']['primaries'])
            errors.append(row['final_image_difference']['max_absolute_error'])
        self.assertEqual(errors[0], 0)
        self.assertGreater(errors[1], 0)
        self.assertGreater(errors[2], errors[1])
        arrays = np.load(self.output/Intervention.UNDER_EYE_ONE.value/'checkpoints.npz')
        self.assertEqual(arrays['texture.input'].shape, (2, 2, 3))
        self.assertTrue(np.all(arrays['texture.input'] >= 0))
        self.assertEqual(arrays['final_image'].shape, (4, 4, 4))
        self.assertTrue(np.all(arrays['final_image'][0] == np.float16(-.75)))

    def test_all_stage_differences_and_model_call_costs_are_persisted(self):
        self.assertEqual(self.report['source_to_writer_model_calls'], len(Intervention))
        self.assertEqual(self.report['texture_model_calls'], 3)
        self.assertEqual(self.report['target_Apple_native_calls'], 0)
        self.assertEqual(self.report['GPU_calls'], 0)
        self.assertFalse(self.report['Apple_pipeline_verified'])
        self.assertFalse(self.report['Apple_Texture_placement_verified'])
        self.assertTrue(self.report['source_snapshot_stable'])
        self.assertEqual(self.report['source_sha256_before'], self.report['source_sha256_after'])
        self.assertIn('research/styles-firmware-20261022/module_sensitivity.py',
                      self.report['source_sha256_before'])
        for row in self.report['runs']:
            self.assertEqual(row['source_to_writer_model_calls'], 1)
            self.assertEqual(row['evidence_level'], 'model_only')
            self.assertEqual(len(row['stage_differences']), 60)
            self.assertTrue((self.output/row['intervention']/'context.json').is_file())
            self.assertTrue((self.output/row['intervention']/'checkpoints.npz').is_file())
        self.assertGreater(self.report['summary']['blocked_or_unknown'], 0)

    def test_invalid_choices_and_existing_output_are_rejected_without_mutation(self):
        with self.assertRaises(TypeError):
            apply(self.context, 'skin-theta9-025')
        with self.assertRaises(FileExistsError):
            execute(self.output, spec=self.spec, numerics=PORTABLE,
                    selection=BranchSelection.EXPERIMENTAL_BRIGHT16)
        with self.assertRaises(TypeError):
            execute(Path(self.temp.name)/'bad', spec=self.spec,
                    numerics=Numerics.STRICT_HOST_POINT, selection=BranchSelection.CONTEXT)
        with self.assertRaises(ValueError):
            execute(Path(self.temp.name)/'dup', spec=self.spec, numerics=PORTABLE,
                    selection=BranchSelection.CONTEXT,
                    interventions=(Intervention.BASELINE, Intervention.BASELINE))
        with self.assertRaises(TypeError):
            under_eye_after_writer(None, strength=.5, supplied_output_transfer_code=3)
        with self.assertRaises(ValueError):
            under_eye_after_writer(None, strength=np.float32(.5), supplied_output_transfer_code=0)

    def test_stage_metrics_preserve_half_bit_difference_and_scalar_domain(self):
        a = np.zeros((2, 2), dtype='f2'); b = a.copy(); b[0, 0] = -0.
        metric = stage_difference(a, b, precision='h', reference_name='signed-zero control')
        self.assertEqual(metric['max_absolute_error'], 0)
        self.assertEqual(metric['storage_bit_mismatches'], 1)
        with self.assertRaises(ValueError):
            stage_difference(a, np.full_like(a, np.nan), precision='h', reference_name='nonfinite')


if __name__ == '__main__':
    unittest.main()
