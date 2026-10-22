import copy,hashlib,json,tempfile,unittest
from pathlib import Path
import numpy as np
from color_inverse import Domain,cell,f32,u32,verify_partition,solve_target
from query_color_inverse import query

ROOT=Path(__file__).parent;E=ROOT/'evidence'
load=lambda n:json.loads((E/n).read_text())


class ColorInverseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan=load('color-partition-s22a.json');cls.domain=Domain();cls.rows=[];cls.chunks=sorted(E.glob('scan-[0-9][0-9][0-9]-s22b.json'))
        for p in cls.chunks:cls.rows+=json.loads(p.read_text())['rows']
        cls.goal=np.array(load('target-point3-s22e.json')['writer_half_bits'],dtype='u2')

    def solve(self,rows=None,target=None):return solve_target(self.domain,self.plan['cells'],self.plan['states'],self.rows if rows is None else rows,self.goal if target is None else target)

    def test_declared_raw_domain_and_negative_zero_are_explicit(self):
        self.assertEqual(self.domain.count,1052770305);self.assertEqual(float(f32(self.domain.last_bits)),.375);self.assertFalse(self.domain.record()['negative_zero_searched'])
        with self.assertRaises(TypeError):Domain(0,0x7f800000)
        with self.assertRaises(TypeError):Domain(0x80000000,0x80000000)

    def test_complete_half_partition_and_independent_omission_checks(self):
        r=verify_partition(self.domain,self.plan['cells'],self.plan['states']);self.assertEqual(r['half_cells'],13825);self.assertEqual(r['interface_states'],146);self.assertEqual(r['endpoint_casts_and_adjacent_omission_checks'],55298);self.assertFalse(r['writer_monotonicity_assumed'])

    def test_missing_overlap_and_duplicate_interface_key_fail_closed(self):
        c=copy.deepcopy(self.plan['cells']);c[100][1]+=1
        with self.assertRaises(ValueError):verify_partition(self.domain,c,self.plan['states'])
        c=copy.deepcopy(self.plan['cells']);c[100][1]-=1
        with self.assertRaises(ValueError):verify_partition(self.domain,c,self.plan['states'])
        s=copy.deepcopy(self.plan['states']);s[1]['key']=s[0]['key']
        with self.assertRaises(ValueError):verify_partition(self.domain,self.plan['cells'],s)

    def test_zero_bin_contains_tiny_f32_and_tie_but_next_maps_positive_half(self):
        c=cell(0,self.domain);self.assertEqual(c['first_f32_bits'],0);self.assertEqual(c['upper_real'],2**-25);self.assertTrue(c['upper_closed']);self.assertEqual(np.float16(f32(c['last_f32_bits'])).view('u2'),0);self.assertEqual(np.float16(f32(c['last_f32_bits']+1)).view('u2'),1);self.assertGreater(c['last_f32_bits'],u32(2**-126))

    def test_point3_half_cell_8191_is_contained_in_larger_returned_candidate(self):
        c=cell(int(np.float16(.3).view('u2')),self.domain);r=self.solve();self.assertEqual(c['f32_population'],8191);self.assertFalse(c['lower_closed']);self.assertFalse(c['upper_closed']);span=r['candidate_union'][0];self.assertLessEqual(span['first_f32_bits'],c['first_f32_bits']);self.assertGreaterEqual(span['last_f32_bits'],c['last_f32_bits']);self.assertEqual(r['found_f32_population'],57343);self.assertGreater(r['found_f32_population'],8191)

    def test_actual_model_scan_is146_fresh_states_not_old_five_lookup(self):
        self.assertEqual(len(self.rows),146);self.assertEqual(len({r['state_id']for r in self.rows}),146);self.assertTrue(all(r['writer_known']for r in self.rows));self.assertEqual(load('color-inverse-s22c.json')['model_forward_evaluations'],146)

    def test_platform_query_returns_multiple_classes_and_both_known_controls(self):
        q=load('query-platform-s22e.json');self.assertEqual(q['model_matching_state_ids'],[0,1]);self.assertEqual(len(q['candidate_interface_classes']),2);self.assertFalse(q['unique_parameter']);span=q['candidate_union'][0]
        for x in [.01,.02]:self.assertLessEqual(span['first_f32_bits'],u32(x));self.assertGreaterEqual(span['last_f32_bits'],u32(x))
        self.assertTrue(span['upper_closed']);self.assertEqual(span['upper_real'],.02210235595703125)

    def test_reusable_query_matches_aggregation_with_open_outer_endpoints(self):
        r=self.solve();saved=load('query-point3-s22e.json');self.assertEqual(r['candidate_union'],saved['candidate_union']);self.assertEqual(r['model_matching_state_ids'],[93]);self.assertFalse(r['candidate_union'][0]['lower_closed']);self.assertFalse(r['candidate_union'][0]['upper_closed']);self.assertFalse(r['original_host_exhaustive'])

    def test_impossible_modified_border_target_has_no_nearest_fallback(self):
        target=self.goal.copy();target[0,0,0]^=np.uint16(1);r=self.solve(target=target);self.assertTrue(r['coverage']['complete_model_coverage']);self.assertEqual(r['candidate_union'],[]);self.assertEqual(r['found_f32_population'],0)

    def test_missing_and_unknown_state_are_not_excluded_candidates(self):
        r=self.solve(rows=[v for v in self.rows if v['state_id']!=93]);self.assertFalse(r['coverage']['complete_model_coverage']);self.assertEqual(r['coverage']['missing_state_ids'],[93]);self.assertEqual(r['candidate_union'],[])
        rows=copy.deepcopy(self.rows);rows[93]['writer_known']=False;r=self.solve(rows=rows);self.assertEqual(r['coverage']['unknown_state_ids'],[93]);self.assertFalse(r['coverage']['complete_model_coverage'])

    def test_duplicate_catalog_state_and_wrong_target_type_are_rejected(self):
        with self.assertRaises(ValueError):self.solve(rows=self.rows+[self.rows[0]])
        with self.assertRaises(TypeError):self.solve(target=self.goal.astype('f4'))

    def test_json_query_rejects_pixel_floats_instead_of_reinterpreting_them(self):
        with tempfile.TemporaryDirectory(prefix='psr-query-negative-')as name:
            root=Path(name);target=root/'target.json';data=load('target-point3-s22e.json');data['writer_half_bits']=np.asarray(data['writer_half_bits'],dtype='f8').tolist();target.write_text(json.dumps(data))
            with self.assertRaises(TypeError):query(E/'color-partition-s22a.json',target,self.chunks,root/'out.json')

    def test_minimal_original_boundary_cost_and_all_expectations(self):
        r=load('native-boundaries-s22d.json');self.assertEqual(len(r['rows']),8);self.assertEqual(r['prefix_original_calls'],78);self.assertEqual(r['new_main_original_calls'],192);self.assertEqual(r['total_original_kernel_calls'],270);self.assertEqual(r['prefix_half_bit_mismatches_vs_S21'],0)
        for row in r['rows']:self.assertTrue(row['target_match_expectations_agree']);self.assertTrue(row['model_writer_sha256_match']);self.assertEqual(row['observer_plain_writer_half_bit_mismatches'],0);self.assertTrue(all(row['logical_interface_matches'].values()))

    def test_final_audit_does_not_turn_partial_native_into_domain_proof(self):
        r=load('inverse-audit-s22e.json');self.assertTrue(r['complete_model_finite_domain']['complete_model_coverage']);self.assertFalse(r['original_host_all146_states_exhaustively_verified']);self.assertTrue(r['all_model_candidate_signature_ids_have_original_witness']);self.assertFalse(r['full_photo_inverse_verified']);self.assertTrue(any('RichSat' in v for v in r['unknown_scope']))

    def test_search_sources_are_linked_without_repeating_original_batch(self):
        r=load('source-link-s22e.json');self.assertTrue(r['all_preexisting_search_functions_AST_equal']);self.assertTrue(r['run_color_inverse_source_unchanged']);self.assertEqual(r['new_model_forward_evaluations'],0);self.assertEqual(r['new_original_calls'],0)

    def test_own_source_and_catalog_inputs_prebound_before_tests(self):
        r=load('test-binding-s22f.pre.json');self.assertEqual(r['source_sha256_before_execution'][Path(__file__).name],hashlib.sha256(Path(__file__).read_bytes()).hexdigest());self.assertIn('color-partition-s22a.json',r['input_sha256_before_execution']);self.assertIn('native-boundaries-s22d.json',r['input_sha256_before_execution'])


if __name__=='__main__':unittest.main()
