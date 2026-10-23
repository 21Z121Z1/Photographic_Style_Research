"""Focused S28 observation-contract tests; no forward/kernel execution."""
import copy
import tempfile
import unittest
from dataclasses import asdict, replace
from pathlib import Path
from unittest.mock import patch

import numpy as np

from baseline_archive import encoded, sha
from context_color_api import BoundCatalog, Target, load
from joint_color_api import ACCEPTED, SharedField3, compatible
from observation_ulps import Catalog, from_ranks, geometry, joint, perturb, ranks
from raw_f32_sets import Interval

R = Path(__file__).parent
E = R / 'evidence'
ERROR = E / 'observation-error-contract-s28a.json'


def tables():
    plan = load(E / 'observation-experiment-plan-s28a.json')
    result = {}
    for side, filename in plan['contexts'].items():
        context = E / filename
        catalog, digest = ACCEPTED[sha(context)]
        handle = BoundCatalog(context, E / 'model-precision-v3-s25c6.json',
                              E / 'color-partition-s22a.json', E / catalog, digest)
        result[side] = Catalog(handle, ERROR)
    compatible([t.contract for t in result.values()])
    return result


def target(table, bits):
    return Target(table.identity, table.handle.expected_catalog_sha256, bits)


def partial(table, path, *, missing=(), unknown=()):
    """Synthetic omission only; every retained known row remains unchanged."""
    rows = []
    for i, value in table.rows.items():
        if i in missing:
            continue
        row = copy.deepcopy(value)
        if i in unknown:
            row['writer_known'] = False
            row.pop('writer_half_bits', None)
            row.pop('writer_sha256', None)
        rows.append(row)
    chunk = path / 'fixture-chunk.json'
    chunk.write_bytes(encoded({'identity': asdict(table.identity),
                              'partition_sha256': sha(table.handle.partition_file),
                              'rows': rows, 'fixture_only': True}))
    manifest = path / 'fixture-catalog.json'
    manifest.write_bytes(encoded({'schema': 'psr-context-catalog-v1',
                                 'identity': asdict(table.identity),
                                 'partition_sha256': sha(table.handle.partition_file),
                                 'chunks': [{'name': chunk.name, 'sha256': sha(chunk)}],
                                 'fixture_only': True}))
    return Catalog(replace(table.handle, catalog_file=manifest,
                           expected_catalog_sha256=sha(manifest)), ERROR)


class FiniteHalfTests(unittest.TestCase):
    def test_all_finite_encodings_round_trip(self):
        bits = np.arange(65536, dtype='u2')
        finite = bits[np.isfinite(bits.view('f2'))]
        np.testing.assert_array_equal(from_ranks(ranks(finite)), finite)
        self.assertEqual(len(set(map(int, ranks(finite)))), len(finite))

    def test_signed_zeros_are_distinct_adjacent(self):
        self.assertEqual(list(ranks(np.array([0x8000, 0], dtype='u2'))), [32767, 32768])
        values = np.array([-2., -1., -.5, 0., .5, 1., 2.], dtype='f2')
        self.assertTrue(np.all(np.diff(ranks(values.view('u2'))) > 0))

    def test_nonfinite_wrong_dtype_and_outside_finite_rank_rejected(self):
        for value in [0x7c00, 0xfc00, 0x7e00]:
            with self.assertRaises(TypeError):
                ranks(np.array([value], dtype='u2'))
        with self.assertRaises(TypeError):
            ranks(np.array([1.], dtype='f2'))
        for value in [0x3ff, 0xfc00]:
            with self.assertRaises(ValueError):
                from_ranks(np.array([value]))


class ObservationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tables = tables()
        cls.result = load(E / 'observation-results-s28b.json')

    def scan(self, side='first', state=7, pattern='identity', table=None):
        t = table or self.tables[side]
        bits, _ = perturb(self.tables[side].arrays[state], t.mask, pattern)
        return t.scan(target(t, bits), diagnostics=True)

    def test_roi_contract_and_all_states_preflight(self):
        for t in self.tables.values():
            g = geometry(t.handle.context_file)
            self.assertEqual(g['RGB_component_count'], 36)
            self.assertEqual(g['exact_component_count'], 84)
            self.assertEqual(g['output_offset'], [1, 1])
            self.assertEqual(t.ids, list(range(146)))
            self.assertEqual(t.unknown, [])
            self.assertTrue(np.all(t.arrays[:, t.mask].view('f2') > 0))
            self.assertFalse(t.mask.flags.writeable)

    def test_original_exact_api_is_unchanged_for_known_targets(self):
        for side, t in self.tables.items():
            for state in [0, 7, 17, 122]:
                q = self.scan(side, state)
                old = t.handle.query(target(t, t.arrays[state]))
                self.assertEqual(q['exact']['known_state_ids'], old['model_matching_state_ids'])
                self.assertEqual([Interval.read(r) for r in q['exact']['known_candidates']],
                                 [Interval.read(r) for r in old['candidate_union']])

    def test_admissible_rules_are_coordinate_only_and_keep_truth(self):
        for side, t in self.tables.items():
            for state in [0, 7, 17, 122]:
                for pattern in ['first_rgb_plus1', 'first_rgb_minus1', 'checker_rgb_pm1']:
                    bits, change = perturb(t.arrays[state], t.mask, pattern)
                    self.assertTrue(change['within_artificial_contract'])
                    self.assertEqual(change['max_half_rank_steps'], 1)
                    self.assertTrue(np.array_equal(bits[~t.mask], t.arrays[state][~t.mask]))
                    q = t.scan(target(t, bits))
                    self.assertEqual(q['exact']['known_state_ids'], [])
                    self.assertIn(state, q['tolerance']['known_state_ids'])

    def test_all_120_constraints_are_enforced_independently(self):
        # Independent direct positive uint16 differences, without ranks/scan.
        for case in self.result['cases']:
            for side, scene in case['scenes'].items():
                t = self.tables[side]
                for entry in scene['patterns'].values():
                    obs = np.array(entry['observed_half_bits'], dtype='u2')
                    q = entry['scan']
                    exact = np.all(t.arrays == obs, axis=(1, 2, 3))
                    delta = np.abs(t.arrays[:, t.mask].astype('i4') - obs[t.mask].astype('i4'))
                    tol = np.all(delta <= 1, axis=1) & np.all(t.arrays[:, ~t.mask] == obs[~t.mask], axis=1)
                    self.assertEqual(q['exact']['known_state_ids'], np.flatnonzero(exact).tolist())
                    self.assertEqual(q['tolerance']['known_state_ids'], np.flatnonzero(tol).tolist())
                    self.assertEqual(q['known_states_checked'], 146)
                    self.assertEqual(q['components_checked_per_known_state'], 120)

    def test_contract_external_errors_fail_without_nearest_fallback(self):
        for side in self.tables:
            for state in [0, 7, 17, 122]:
                for pattern in ['first_rgb_plus2', 'first_alpha_plus1', 'first_unwritten_rgb_plus1']:
                    q = self.scan(side, state, pattern)
                    self.assertEqual(q['tolerance']['possible_candidates'], [])
                    self.assertFalse(q['nearest_fallback'])

    def test_minimum_failure_is_one_component_one_step(self):
        w = self.result['minimal_exact_failure']
        a = np.array(w['original_half_bits'], dtype='u2')
        b = np.array(w['observed_half_bits'], dtype='u2')
        self.assertEqual(np.argwhere(a != b).tolist(), [[1, 1, 0]])
        self.assertEqual([int(a[1, 1, 0]), int(b[1, 1, 0])], [14329, 14328])
        self.assertEqual(w['scan']['exact']['known_population'], 0)
        self.assertEqual(w['scan']['tolerance']['known_population'], 1018499073)

    def test_saved_exhaustive_single_step_cohort_and_expansions(self):
        rows = self.result['single_component_enumeration']
        keys = {(r['case'], r['scene'], tuple(r['coordinate']), r['delta_half_steps']) for r in rows}
        self.assertEqual(len(rows), 576)
        self.assertEqual(len(keys), 576)
        self.assertTrue(all(not r['exact_state_ids'] and r['truth_retained_tolerance'] for r in rows))
        baseline = {c['case']['id']: {s: r['patterns']['identity']['scan']['exact']['known_population']
                    for s, r in c['scenes'].items()} for c in self.result['cases']}
        expanded = [r for r in rows if r['tolerance_population'] > baseline[r['case']][r['scene']]]
        self.assertEqual([(r['case'], r['scene']) for r in expanded],
                         [(c, 'first') for c in ['platform', 'state7', 'active_A', 'active_B']])

    def test_joint_tolerance_is_second_single_not_extra_information(self):
        a = self.scan('first', 7, 'first_rgb_plus1')
        b = self.scan('second', 7, 'first_rgb_minus1')
        r = joint([a, b], 'tolerance', shared_parameter=SharedField3(True))
        self.assertEqual(r['known_state_ids'], [7])
        self.assertEqual(r['possible_population'], 860159)
        self.assertEqual(r['equal_to_single_indices'], [1])
        self.assertEqual(r['additional_elimination_beyond_smallest_single'], 0)
        self.assertEqual(joint([a, b], 'exact', shared_parameter=SharedField3(True))['possible_population'], 0)

    def test_declaration_duplicate_context_and_mixed_contracts_rejected(self):
        a, b = self.scan('first'), self.scan('second')
        with self.assertRaises(TypeError):
            joint([a, b], 'tolerance')
        with self.assertRaises(ValueError):
            joint([a, b], 'tolerance', shared_parameter=None)
        with self.assertRaises(ValueError):
            joint([a, a], 'tolerance', shared_parameter=SharedField3(True))
        bad = copy.deepcopy(b)
        bad['observation_error_contract_sha256'] = '0' * 64
        with self.assertRaises(ValueError):
            joint([a, bad], 'tolerance', shared_parameter=SharedField3(True))

    def test_wrong_context_shape_and_nonfinite_observation_rejected(self):
        a, b = self.tables['first'], self.tables['second']
        with self.assertRaises(ValueError):
            a.scan(target(b, b.arrays[7]))
        with self.assertRaises(ValueError):
            a.scan(target(a, a.arrays[7][:2]))
        bits = a.arrays[7].copy()
        bits[1, 1, 0] = 0x7e00
        with self.assertRaises(ValueError):
            target(a, bits)

    def test_changed_budget_and_changed_roi_mask_rejected(self):
        with tempfile.TemporaryDirectory(prefix='psr-error-fixture-') as name:
            path = Path(name) / 'error.json'
            d = load(ERROR)
            d['RGB_half_rank_budget'] = 2
            path.write_bytes(encoded(d))
            with self.assertRaises(ValueError):
                Catalog(self.tables['first'].handle, path)
            d = load(ERROR)
            d['contexts'][self.tables['first'].identity.complete_context_sha256]['tolerated_RGB_components'][0][0][0] = True
            path.write_bytes(encoded(d))
            with self.assertRaises(ValueError):
                Catalog(self.tables['first'].handle, path)

    def test_missing_matching_rows_preserve_unknown_joint_candidates(self):
        with tempfile.TemporaryDirectory(prefix='psr-observation-partial-') as name:
            t = partial(self.tables['first'], Path(name), missing={7, 8, 9})
            a = self.scan('first', 7, 'first_rgb_plus1', table=t)
            b = self.scan('second', 7, 'identity')
            r = joint([a, b], 'tolerance', shared_parameter=SharedField3(True))
            self.assertEqual(r['known_population'], 0)
            self.assertEqual(r['possible_population'], 860159)
            self.assertEqual(r['unresolved_population'], 860159)
            self.assertEqual(a['unknown_state_ids'], [7, 8, 9])

    def test_all_unknown_rows_cannot_exclude_second_scene(self):
        with tempfile.TemporaryDirectory(prefix='psr-observation-partial-') as name:
            t = partial(self.tables['first'], Path(name), unknown=set(range(146)))
            a = self.scan('first', 7, table=t)
            self.assertEqual(a['known_states_checked'], 0)
            self.assertEqual(a['tolerance']['possible_population'], 1052770305)
            r = joint([a, self.scan('second')], 'tolerance', shared_parameter=SharedField3(True))
            self.assertEqual(r['unresolved_population'], 860159)

    def test_ambiguity_box_threshold_is_two_not_one_and_not_equivalence(self):
        a = self.result['pairwise_ambiguity']
        self.assertEqual(a['pair_count'], 10585)
        self.assertEqual(a['single_scene_center_compatible_pair_counts'], {'first': 24, 'second': 1})
        self.assertEqual(a['single_scene_radius1_box_overlap_pair_counts'], {'first': 877, 'second': 1})
        self.assertEqual(a['joint_radius1_box_overlap_pairs'], [[0, 1]])
        self.assertEqual(a['new_nonexact_joint_overlap_count'], 0)
        self.assertTrue(a['tolerance_relation_not_claimed_equivalence_or_transitive'])
        # Scalar boxes around ranks100 and102 intersect at101; their centers fail budget1.
        self.assertTrue(set(range(99, 102)) & set(range(101, 104)))
        self.assertGreater(abs(100 - 102), 1)

    def test_concrete_indistinguishable_parameter_pair_survives_both_scenes(self):
        p = self.result['pairwise_ambiguity']['exact_indistinguishable_parameter_pair']
        self.assertEqual(p['raw_f32_bits'], [0, 1008981770])
        for t in self.tables.values():
            np.testing.assert_array_equal(t.arrays[0], t.arrays[1])
            self.assertEqual(self.scan('first', 0)['tolerance']['known_state_ids'], [0, 1])

    def test_lookup_and_joint_cannot_call_forward_or_original_kernel(self):
        with patch('complete_forward.forward', side_effect=AssertionError('forbidden forward')), \
             patch('native_color_boundaries.upstream', side_effect=AssertionError('forbidden kernel')), \
             patch('native_color_boundaries.render', side_effect=AssertionError('forbidden kernel')):
            r = joint([self.scan('first'), self.scan('second')], 'tolerance',
                      shared_parameter=SharedField3(True))
            self.assertEqual(r['new_forward_or_kernel_calls'], 0)


if __name__ == '__main__':
    unittest.main()
