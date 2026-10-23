"""Audit saved S28 table observations; no forward, compiler or kernel calls."""
from pathlib import Path
import argparse
import json
import re
import subprocess

import numpy as np

from baseline_archive import encoded, sha
from context_color_api import load
from joint_color_api import ACCEPTED, V3
from observation_ulps import bitmap, digest_bits
from raw_f32_sets import Interval, intersect_all, population, records
from test_observation_ulps import tables

R = Path(__file__).parent
E = R / 'evidence'
REPO = R.parents[1]


def direct_ids(table, observed):
    """Independent predicate: positive half codes, no rank/scan helper."""
    a = table.arrays
    exact = np.all(a == observed, axis=(1, 2, 3))
    delta = np.abs(a[:, table.mask].astype('i4') - observed[table.mask].astype('i4'))
    outside = np.count_nonzero(a[:, ~table.mask] != observed[~table.mask], axis=1)
    tolerance = np.all(delta <= 1, axis=1) & (outside == 0)
    return np.flatnonzero(exact).tolist(), np.flatnonzero(tolerance).tolist(), delta.max(axis=1), outside


def audit(output, summary_file):
    if output.exists() or summary_file.exists():
        raise FileExistsError('New audit outputs only')
    result_file = E / 'observation-results-s28b.json'
    d = load(result_file)
    t = tables()
    plan = load(E / 'observation-experiment-plan-s28a.json')
    error = load(E / 'observation-error-contract-s28a.json')
    assert sha(E / 'observation-experiment-plan-s28a.json') == d['plan_sha256']
    assert sha(E / 'observation-error-contract-s28a.json') == d['observation_error_contract_sha256'] == plan['contract_sha256']
    assert error['artificial_measurement_contract'] and not error['JPEG_HEIC_GPU_error_model']
    assert error['RGB_half_rank_budget'] == 1 and error['alpha_bit_exact'] and error['unwritten_bit_exact']
    assert not error['original_exact_acceptance_threshold_modified'] and not error['model_numerical_error_budgets_modified']
    assert d['status'] == 'completed_fixed_artificial_observation_experiment'
    assert d['all_input_files_unchanged'] and d['new_forward_or_kernel_calls'] == 0
    for name, expected in d['source_inputs_sha256'].items():
        assert sha(E / name) == expected
    for name, expected in d['source_sha256'].items():
        assert sha(R / name) == expected
    cases = {c['case']['id']: c for c in d['cases']}
    assert [c['case'] for c in d['cases']] == plan['cases']
    primary = 0
    comparisons = []
    for case in d['cases']:
        for side, scene in case['scenes'].items():
            table = t[side]
            assert scene['original_model_writer_half_bits'] == table.arrays[case['case']['state_id']].tolist()
            for pattern, entry in scene['patterns'].items():
                obs = np.array(entry['observed_half_bits'], dtype='u2')
                q = entry['scan']
                a, b, delta, outside = direct_ids(table, obs)
                assert q['exact']['known_state_ids'] == a and q['tolerance']['known_state_ids'] == b
                for mode, ids in [('exact', a), ('tolerance', b)]:
                    assert q[mode]['known_candidates'] == records(table.candidate_set(ids))
                    assert q[mode]['known_population'] == population(table.candidate_set(ids))
                    assert q[mode]['possible_candidates'] == q[mode]['known_candidates']
                    assert q[f'{mode}_match_bitmap'] == bitmap(ids)
                assert q['unknown_state_ids'] == [] and q['unknown_possible_candidates'] == []
                assert q['known_states_checked'] == 146 and q['components_checked_per_known_state'] == 120
                assert q['observed_writer_sha256'] == digest_bits(obs)
                assert entry['legacy_exact_API_same_matches']
                for i, p in enumerate(q['per_known_state']):
                    assert p == {'state_id': i, 'exact_match': i in a, 'tolerance_match': i in b,
                                 'max_written_RGB_half_steps': int(delta[i]),
                                 'exact_zone_differing_components': int(outside[i])}
                primary += 1
            selected = scene['patterns']['first_rgb_plus1']['scan']
            comparisons.append({'case': case['case']['id'], 'scene': side,
                                'original_exact_population': scene['patterns']['identity']['scan']['exact']['known_population'],
                                'perturbed_exact_population': selected['exact']['known_population'],
                                'tolerance_population': selected['tolerance']['known_population'],
                                'tolerance_state_ids': selected['tolerance']['known_state_ids'],
                                'truth_retained_tolerance': selected['tolerance']['truth_retained_in_known']})
        for j in case['joint_comparisons']:
            scans = [case['scenes'][s]['patterns'][p]['scan'] for s, p in zip(['first', 'second'], j['patterns'])]
            for mode in ['exact', 'tolerance']:
                expected = intersect_all([tuple(Interval.read(r) for r in s[mode]['known_candidates']) for s in scans])
                assert j[mode]['known_candidates'] == records(expected)
                assert j[mode]['known_population'] == population(expected)
                assert j[mode]['possible_candidates'] == records(expected)
                assert j[mode]['unresolved_population'] == 0
                assert j[mode]['additional_elimination_beyond_smallest_single'] == 0
    assert primary == 56
    enumeration = d['single_component_enumeration']
    assert len(enumeration) == 576
    expected_keys = {(c['id'], s, tuple(map(int, coordinate)), delta)
                     for c in plan['cases'] for s in ['first', 'second']
                     for coordinate in np.argwhere(t[s].mask) for delta in [-1, 1]}
    assert {(r['case'], r['scene'], tuple(r['coordinate']), r['delta_half_steps']) for r in enumeration} == expected_keys
    expansions = []
    enumeration_ranges = []
    for row in enumeration:
        case = cases[row['case']]
        table = t[row['scene']]
        observed = table.arrays[case['case']['state_id']].copy()
        key = tuple(row['coordinate'])
        observed[key] = int(observed[key]) + row['delta_half_steps']
        a, b, _, _ = direct_ids(table, observed)
        assert row['observed_writer_sha256'] == digest_bits(observed)
        assert row['exact_state_ids'] == a == [] and row['tolerance_state_ids'] == b
        assert row['exact_match_bitmap'] == bitmap(a) and row['tolerance_match_bitmap'] == bitmap(b)
        assert row['exact_population'] == 0 and row['tolerance_population'] == population(table.candidate_set(b))
        assert not row['truth_retained_exact'] and row['truth_retained_tolerance']
        original = case['scenes'][row['scene']]['patterns']['identity']['scan']['exact']
        if row['tolerance_population'] > original['known_population']:
            assert row['scene'] == 'first'
            second = case['scenes']['second']['patterns']['identity']['scan']['tolerance']
            joined = intersect_all([table.candidate_set(b), tuple(Interval.read(r) for r in second['known_candidates'])])
            assert records(joined) == second['known_candidates']
            state = case['case']['state_id']
            extra = min(set(b) - set(original['known_state_ids']))
            pair = [state, extra]
            raw = [table.plan['states'][s]['representative_f32_bits'] for s in pair]
            expansions.append({**row, 'matching_raw_union': records(table.candidate_set(b)),
                               'example_indistinguishable_state_pair_in_first_observation': pair,
                               'example_raw_f32_pair': raw,
                               'example_raw_values': [float(np.array(r, dtype='u4').view('f4')) for r in raw],
                               'second_identity_joint_candidates': records(joined),
                               'second_identity_joint_population': population(joined),
                               'joint_equals_stronger_second': True,
                               'extra_elimination_beyond_second': 0})
    assert len(expansions) == 4
    for c in plan['cases']:
        for side in ['first', 'second']:
            rows = [r for r in enumeration if r['case'] == c['id'] and r['scene'] == side]
            enumeration_ranges.append({'case': c['id'], 'scene': side, 'count': len(rows),
                                       'exact_empty': sum(not r['exact_state_ids'] for r in rows),
                                       'truth_retained_tolerance': sum(r['truth_retained_tolerance'] for r in rows),
                                       'tolerance_population_range': [min(r['tolerance_population'] for r in rows), max(r['tolerance_population'] for r in rows)]})
    # Independent pair check in positive half-code space; all 10585 state pairs.
    center_count = dict.fromkeys(t, 0)
    overlap_count = dict.fromkeys(t, 0)
    exact_pairs, joint_pairs = [], []
    for i in range(146):
        for j in range(i + 1, 146):
            overlaps, exacts = [], []
            for side, table in t.items():
                a, b = table.arrays[i], table.arrays[j]
                same_zone = np.array_equal(a[~table.mask], b[~table.mask])
                delta = int(np.abs(a[table.mask].astype('i4') - b[table.mask].astype('i4')).max())
                center_count[side] += bool(same_zone and delta <= 1)
                overlap_count[side] += bool(same_zone and delta <= 2)
                overlaps.append(same_zone and delta <= 2)
                exacts.append(np.array_equal(a, b))
            if all(overlaps): joint_pairs.append([i, j])
            if all(exacts): exact_pairs.append([i, j])
    graph = d['pairwise_ambiguity']
    assert graph['single_scene_center_compatible_pair_counts'] == center_count == {'first': 24, 'second': 1}
    assert graph['single_scene_radius1_box_overlap_pair_counts'] == overlap_count == {'first': 877, 'second': 1}
    assert graph['joint_radius1_box_overlap_pairs'] == joint_pairs == exact_pairs == [[0, 1]]
    assert graph['new_nonexact_joint_overlap_count'] == 0 and graph['constructed_measurement_ambiguity_witness'] is None
    minimum = d['minimal_exact_failure']
    assert minimum['L0_changed_components'] == minimum['Linfinity_half_steps'] == 1
    assert minimum['scan']['exact']['known_population'] == 0
    assert minimum['scan']['tolerance']['truth_retained_in_known']
    assert d['table_observation_scans'] == 632 and d['state_observation_checks'] == 92272
    assert d['component_constraints_checked'] == 11072640
    summary = {'scope': 'S28 artificial half-observation tolerance, model_only; known source/auxiliary contexts',
               'error_contract_sha256': d['observation_error_contract_sha256'],
               'primary_plus1_comparisons': comparisons, 'single_component_cohort': enumeration_ranges,
               'four_error_induced_first_scene_expansions': expansions,
               'minimum_exact_failure': {k: minimum[k] for k in ['case', 'scene', 'coordinate', 'delta_half_steps', 'L0_changed_components', 'Linfinity_half_steps', 'minimality']},
               'minimal_changed_half_codes': [14329, 14328],
               'primary_contract_external_negative_observations': 24,
               'all24_contract_external_negative_tolerance_sets_empty': True,
               'all_primary_admissible_tolerance_joint_equal_to_second': True,
               'joint_additional_elimination_beyond_strongest_single': 0,
               'exact_joint_cannot_rescue_a_single_empty_exact_set': True,
               'pairwise_ambiguity': graph, 'unknown_states_in_actual_full_directories': 0,
               'candidate_unions_and_bitmaps': result_file.name,
               'unknown_policy': 'preserve unknown/missing as possible; tested only in synthetic omission fixtures',
               'new_model_forward_or_original_kernel_calls': 0}
    for case in d['cases']:
        for scene in case['scenes'].values():
            for pattern in plan['negative_patterns']:
                assert not scene['patterns'][pattern]['scan']['tolerance']['possible_candidates']
    summary_file.write_bytes(encoded(summary))
    # Source/input identity and raw pre/post logs, including the frozen plan ordering.
    bindings = {}
    for name in ['freeze-binding-s28a', 'experiment-binding-s28b', 'test-binding-s28c2']:
        path = E / f'{name}.json'
        b = load(path)
        pre = E / f'{name}.pre.json'
        log = E / f'{name}.log'
        assert b['exit_code'] == 0 and b['source_unchanged_during_command'] and b['inputs_unchanged_during_command']
        assert sha(pre) == b['pre_run_binding_sha256'] and sha(log) == b['log_sha256']
        bindings[name] = {'post_sha256': sha(path), 'pre_sha256': sha(pre), 'log_sha256': sha(log),
                          'elapsed_seconds': b['elapsed_seconds'], 'exit_code': 0}
    pre = load(E / 'experiment-binding-s28b.pre.json')
    assert pre['input_sha256_before_execution']['observation-experiment-plan-s28a.json'] == d['plan_sha256']
    assert pre['input_sha256_before_execution']['observation-error-contract-s28a.json'] == d['observation_error_contract_sha256']
    for n, h in d['source_sha256'].items(): assert pre['source_sha256_before_execution'][n] == h
    tests = re.search(r'Ran (\d+) tests in ([\d.]+)s\n\nOK', (E / 'test-binding-s28c2.log').read_text())
    assert tests
    iteration = load(E / 'source-iteration-s28c.json')
    for record in [iteration['source'], *iteration['raw_failed_run_artifacts'].values()]:
        assert sha(REPO.parent / record['private_relative_to_task']) == record['sha256']
    failed = load(E / 'test-binding-s28c.json')
    assert failed['exit_code'] == 1 and failed['source_unchanged_during_command'] and failed['inputs_unchanged_during_command']
    assert failed['log_sha256'] == iteration['raw_failed_run_artifacts']['test-binding-s28c.log']['sha256']
    assert sha(E / iteration['public_failed_log']['name']) == iteration['public_failed_log']['sha256']
    assert load(E / 'test-binding-s28c.pre.json')['source_sha256_before_execution']['test_observation_ulps.py'] == iteration['source']['sha256']
    audit_iteration = load(E / 'audit-iteration-s28d.json')
    for record in [audit_iteration['source'], *audit_iteration['raw_failed_run_artifacts'].values()]:
        assert sha(REPO.parent / record['private_relative_to_task']) == record['sha256']
    failed_audit = load(E / 'verification-binding-s28d.json')
    assert failed_audit['exit_code'] == 1 and failed_audit['source_unchanged_during_command'] and failed_audit['inputs_unchanged_during_command']
    assert failed_audit['log_sha256'] == audit_iteration['raw_failed_run_artifacts']['verification-binding-s28d.log']['sha256']
    assert sha(E / audit_iteration['public_failed_log']['name']) == audit_iteration['public_failed_log']['sha256']
    assert load(E / 'verification-binding-s28d.pre.json')['source_sha256_before_execution']['verify_observation.py'] == audit_iteration['source']['sha256']
    precision = load(E / 'model-precision-v3-s25c6.json')
    assert sha(E / 'model-precision-v3-s25c6.json') == V3
    assert all(sha(R / n) == h for n, h in precision['model_source_sha256'].items())
    assert len(precision['model_source_sha256']) == 243
    assert sha(R / 'context_color_api.py') == precision['inverse_API_sha256']
    for filename, expected in ACCEPTED.values(): assert sha(E / filename) == expected
    prior = load(E / 'verification-s27.json')
    changes = [n for n, h in prior['current_source_sha256'].items() if sha(R / n) != h]
    assert changes == ['bound_validation.py']
    assert all(sha(E / n) == h for n, h in prior['evidence_sha256'].items())
    old_cost = load(E / 'stage-audit-s25h2.json')['full_point_cost']
    assert old_cost['total_recorded_plus_uninstrumented_range'] == [162, 163]
    assert not subprocess.check_output(['git', 'diff', '--name-only', 'HEAD', '--', str(E)], cwd=REPO, text=True).strip()
    for path in E.glob('*s28*'):
        if path.is_file():
            assert b'\0' not in path.read_bytes() and not re.search(rb'/Users/[A-Za-z0-9._-]+/', path.read_bytes())
            if path.suffix == '.json': load(path)
    receipt = {'status': 'passed_artificial_observation_contract_and_independent_saved_table_audit',
               'scope': summary['scope'], 'base_HEAD': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip(),
               'branch': subprocess.check_output(['git', 'branch', '--show-current'], cwd=REPO, text=True).strip(),
               'summary_sha256': sha(summary_file), 'result_sha256': sha(result_file),
               'error_contract_sha256': d['observation_error_contract_sha256'], 'precision_sha256': V3,
               'single_context_API_and243_model_sources_unchanged': True,
               'prior_S27_source_changes_only_stage_binding_metadata': changes,
               'prior_S27_evidence_SHA_unchanged': True,
               'experimental_cost': {'core_table_scans': 632, 'state_observation_checks': 92272,
                                     'component_constraints': 11072640, 'legacy_exact_API_reference_queries': 56,
                                     'distinct_state_pairs_checked': 10585, 'seconds': d['elapsed_seconds']},
               'verification_cost': {'independent_saved_observation_predicates': 632,
                                     'independent_distinct_pair_checks': 10585,
                                     'derived_expansion_intersections': 4,
                                     'all_are_existing_array_or_interval_operations': True},
               'tests': {'count': int(tests[1]), 'seconds': float(tests[2]), 'result': 'OK',
                         'forward_and_kernel_entrypoints_blocked_in_test': True,
                         'partial_unknown_examples_are_synthetic_fixtures': True},
               'new_forward_calls': 0, 'new_original_kernel_calls': 0, 'new_compilations': 0,
               'model_only': True, 'JPEG_HEIC_GPU_error_model': False,
               'original_exact_thresholds_and_model_budgets_unchanged': True,
               'scene_domain_cast_or_free_fields_expanded': False,
               'S25_cost_limit_retained': old_cost,
               'bindings': bindings,
               'initial_test_assertion_failure_retained': iteration,
               'initial_auditor_argument_failure_retained': audit_iteration,
               'current_source_sha256': {p.name: sha(p) for p in sorted(R.glob('*.py'))},
               'document_sha256': {n: sha(R / n) for n in ['PROGRESS-S28.zh-CN.md', 'README.zh-CN.md']},
               'evidence_sha256': {p.name: sha(p) for p in sorted(E.glob('*s28*')) if p.is_file()},
               'remaining': ['shared field3 is caller assumption, not UI mapping',
                             'only fixed two synthetic contexts, cast0/tuning2 and raw+0..3/8; supplied auxiliaries',
                             'per-context 140 states not host exhaustive; historical IR cause unknown',
                             'bright6+18 residuals and cast16/multiple-free-fields prohibition unchanged',
                             'old set unknowns and nine-field missing-cache software bridge remain',
                             'originalGPU/UI/real same-frame/IMG_2810 build and unknown-source inverse unverified',
                             'S19 source-retention and S25 failed-v2 cost bounds preserved']}
    output.write_bytes(encoded(receipt))
    print(json.dumps({'status': receipt['status'], 'tests': int(tests[1]), 'minimal_failure': [1, 1],
                      'single_step_exact_empty': 576, 'single_step_tolerance_truth_retained': 576,
                      'first_scene_expansions': 4, 'new_nonexact_joint_overlap_pairs': 0,
                      'new_forward_or_kernel_calls': 0}))
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('summary', type=Path)
    args = parser.parse_args()
    audit(args.output, args.summary)
