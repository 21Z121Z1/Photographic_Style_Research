import json,tempfile,unittest
from dataclasses import replace
from pathlib import Path
import numpy as np
from baseline_archive import sha,encoded
from context_color_api import BoundCatalog,Target,identity,strict_bits
from bright137_witness import Saved137,require_inverse_scope
from leaf_numeric import V

R=Path(__file__).parent;E=R/'evidence'
load=lambda n:json.loads((E/n).read_text())


class SamePrecisionScenesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.precision=E/'model-precision-v3-s25c6.json';cls.plan=E/'color-partition-s22a.json';cls.first=BoundCatalog(E/'complete-context-s15a.json',cls.precision,cls.plan,E/'first-context-catalog-v3-s26c.json',sha(E/'first-context-catalog-v3-s26c.json'));cls.second=BoundCatalog(E/'second-context-s25a.json',cls.precision,cls.plan,E/'context-catalog-s25e.json',sha(E/'context-catalog-s25e.json'));cls.a=cls.first.checked();cls.b=cls.second.checked();cls.node=Saved137(E/'bright-detail-s25c.json')

    def operands(self):return V.value(np.array(self.node.square_bits,dtype='u2').view('f2')),V.value(np.array(self.node.multiplier_bits,dtype='u2').view('f2'))

    def test_all_thirteen_saved_first_scene_points_pass_without_native_calls(self):
        d=load('first-scene-v3-replay-s26a.json');self.assertEqual(d['new_point_calls'],13);self.assertEqual(d['native_calls'],0);self.assertEqual(len({x['raw_f32_bits']for x in d['rows']}),13);self.assertTrue(all(not x['differences']for x in d['rows']));self.assertEqual(d['all_point_half_bit_mismatches'],0)

    def test_both_catalogs_have_exact_same_precision_but_distinct_contexts(self):
        self.assertEqual(self.a[0].precision_contract_sha256,self.b[0].precision_contract_sha256);self.assertNotEqual(self.a[0].complete_context_sha256,self.b[0].complete_context_sha256);self.assertEqual(len(self.a[3]),146);self.assertEqual(len(self.b[3]),146)

    def test_all_first_states_are_new_computations_with_no_target_read(self):
        files=sorted(E.glob('scan-[0-9][0-9][0-9]-s26b.json'));data=[json.loads(f.read_text())for f in files];self.assertEqual([r['state_id']for d in data for r in d['rows']],list(range(146)));self.assertTrue(all(not d['target_read']and d['native_calls']==0 for d in data));self.assertTrue(all(r['writer_known']for d in data for r in d['rows']))

    def test_exact_collision_groups_differ_under_same_precision(self):
        d=load('same-precision-comparison-s26c.json');self.assertEqual(d['unique_writer_counts'],{'first':140,'second':145});self.assertEqual(d['collision_groups']['first'],[[0,1],[4,5],[7,8,9],[31,32],[71,72]]);self.assertEqual(d['collision_groups']['second'],[[0,1]]);self.assertEqual(d['changed_class_state_ids'],[4,5,7,8,9,31,32,71,72]);self.assertEqual(len(d['removed_pairs']),6);self.assertFalse(d['added_pairs'])

    def test_candidate_sets_for_changed_class_have_different_populations(self):
        q=load('changed-class-queries-s26c2.json')['changed_class_queries'];self.assertEqual(q['first:7']['model_matching_state_ids'],[7,8,9]);self.assertEqual(q['second:7']['model_matching_state_ids'],[7]);self.assertEqual(q['first:7']['found_f32_population'],2400255);self.assertEqual(q['second:7']['found_f32_population'],860159);self.assertFalse(q['first:7']['candidate_union'][0]['lower_closed']);self.assertFalse(q['first:7']['candidate_union'][0]['upper_closed'])

    def test_old_writer_bits_equal_fresh_rebuild_without_relabelling(self):
        old={r['state_id']:r for f in E.glob('scan-[0-9][0-9][0-9]-s22b.json')for r in json.loads(f.read_text())['rows']}
        self.assertEqual(len(old),146)
        for i in range(146):self.assertEqual(old[i]['writer_half_bits'],self.a[3][i]['writer_half_bits'])
        self.assertTrue(load('changed-class-queries-s26c2.json')['new_directory_was_freshly_evaluated_not_relabelled'])

    def test_context_file_swap_is_rejected_in_both_directions(self):
        for h,context in [(self.first,self.second.context_file),(self.second,self.first.context_file)]:
            with self.assertRaises(ValueError):replace(h,context_file=context).checked()

    def test_cross_context_target_is_rejected_in_both_directions(self):
        for h,other,rows in [(self.first,self.b[0],self.a[3]),(self.second,self.a[0],self.b[3])]:
            target=Target(other,h.expected_catalog_sha256,strict_bits(rows[17]['writer_half_bits']))
            with self.assertRaises(ValueError):h.query(target)

    def test_scoped_node137_corrects_saved_node_only(self):
        square,multiplier=self.operands();fixed=self.node.apply(square,multiplier);self.assertEqual(fixed.lo.astype('f2').view('u2').tolist(),[16889,16417,16630]);separate=(multiplier*square+V.value(4)).lo.astype('f2').view('u2');self.assertEqual(int(np.count_nonzero(separate!=fixed.lo.astype('f2').view('u2'))),1)

    def test_scoped_node_rejects_one_half_step_outside_witness(self):
        square,multiplier=self.operands();bits=np.array(self.node.square_bits,dtype='u2');bits[1]+=1
        with self.assertRaises(ValueError):self.node.apply(V.value(bits.view('f2')),multiplier)

    def test_scoped_node_rejects_set_f32_and_wrong_shape(self):
        square,multiplier=self.operands()
        for bad in [square.f(),V.bounds(square.lo,square.hi),V.value([1,2])]:
            with self.assertRaises(TypeError):self.node.apply(bad,multiplier)

    def test_node_rejects_unverified_evidence_even_if_values_match(self):
        with tempfile.TemporaryDirectory(prefix='psr-node137-test-')as name:
            p=Path(name)/'detail.json';p.write_bytes((E/'bright-detail-s25c.json').read_bytes()+b' ')
            with self.assertRaises(ValueError):Saved137(p)

    def test_cast16_and_multiple_free_parameters_are_prohibited(self):
        require_inverse_scope(0,frozenset({3}))
        for cast,fields in [(16,frozenset({3})),(0,frozenset({2,3})),(2,frozenset({3}))]:
            with self.assertRaises(ValueError):require_inverse_scope(cast,fields)
        with self.assertRaises(TypeError):require_inverse_scope(True,frozenset({3}))
        with tempfile.TemporaryDirectory(prefix='psr-cast16-test-')as name:
            p=Path(name)/'context.json';d=load('complete-context-s15a.json');d['raw_f32_bits']['params'][0]=16;p.write_bytes(encoded(d))
            with self.assertRaises(ValueError):identity(p,self.precision)

    def test_v3_sources_default_bright_and_old_cost_limit_remain_unchanged(self):
        p=load('model-precision-v3-s25c6.json');self.assertTrue(all(sha(R/n)==h for n,h in p['model_source_sha256'].items()));self.assertEqual(sha(R/'context_color_api.py'),p['inverse_API_sha256']);self.assertFalse(load('bright137-local-s26d.json')['default_pixel_bright_modified']);self.assertEqual(load('stage-audit-s25h2.json')['full_point_cost']['total_recorded_plus_uninstrumented_range'],[162,163]);self.assertEqual(load('bright137-local-s26d.json')['remaining_original_bright_differences'],{'S25_targets':6,'S25_boundaries':18})


if __name__=='__main__':unittest.main()
