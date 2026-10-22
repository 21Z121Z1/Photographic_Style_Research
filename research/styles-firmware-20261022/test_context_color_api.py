import copy,json,tempfile,unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch
import numpy as np
from baseline_archive import sha,encoded
from context_color_api import BoundCatalog,Target,Identity,identity,strict_bits,read_rows,seal_catalog
from context_inverse_workflow import contains
from output_code3 import forward as host_encode
from leaf_numeric import V

E=Path(__file__).parent/'evidence'
load=lambda n:json.loads((E/n).read_text())


class ContextColorAPITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context=E/'second-context-s25a.json';cls.precision=E/'model-precision-v3-s25c6.json';cls.partition=E/'color-partition-s22a.json';cls.catalog=E/'context-catalog-s25e.json';cls.handle=BoundCatalog(cls.context,cls.precision,cls.partition,cls.catalog,sha(cls.catalog));d=load('blind-target-A-s25e.json');cls.target=Target(Identity(**d['identity']),d['catalog_sha256'],strict_bits(d['writer_half_bits']));cls.checked=cls.handle.checked();cls.true_A=load('scene-selection-s25a.json')['target_controls'][0]['raw_f32_bits']

    def test_blind_exact_query_contains_true_control_and_multiple_preimages(self):
        q=self.handle.query(self.target);self.assertTrue(contains(q,self.true_A));self.assertEqual(q['model_matching_state_ids'],[17]);self.assertEqual(q['found_f32_population'],401409);self.assertTrue(q['coverage']['complete_model_coverage']);self.assertFalse(q['true_control_input_to_solver'])

    def test_unknown_matching_state_remains_possible_not_excluded(self):
        i,m,p,rows=copy.deepcopy(self.checked);rows[17]['writer_known']=False
        with patch.object(BoundCatalog,'checked',return_value=(i,m,p,rows)):q=self.handle.query(self.target)
        self.assertFalse(q['coverage']['complete_model_coverage']);self.assertIn(17,q['coverage']['unknown_state_ids']);self.assertTrue(any(x['first_f32_bits']<=self.true_A<=x['last_f32_bits']for x in q['unresolved_possible_union']));self.assertEqual(q['candidate_union'],[])

    def test_missing_matching_state_is_not_an_exclusion(self):
        i,m,p,rows=copy.deepcopy(self.checked);del rows[17]
        with patch.object(BoundCatalog,'checked',return_value=(i,m,p,rows)):q=self.handle.query(self.target)
        self.assertIn(17,q['coverage']['missing_state_ids']);self.assertTrue(q['unresolved_are_not_excluded']);self.assertTrue(q['unresolved_possible_union'])

    def test_strict_raw_target_rejects_float_bool_overflow_and_nonfinite(self):
        for bad in [np.zeros((1,1,4),dtype='f4'),np.zeros((1,1,4),dtype=bool),np.full((1,1,4),65536,dtype='u4')]:
            with self.assertRaises(TypeError):strict_bits(bad)
        with self.assertRaises(ValueError):strict_bits(np.full((1,1,4),0x7c00,dtype='u2'))

    def test_wrong_context_cannot_use_the_new_catalog(self):
        h=replace(self.handle,context_file=E/'complete-context-s15a.json')
        with self.assertRaises(ValueError):h.query(self.target)

    def test_single_auxiliary_bit_change_is_a_different_context(self):
        with tempfile.TemporaryDirectory(prefix='psr-context-test-')as name:
            p=Path(name)/'context.json';d=load('second-context-s25a.json');d['raw_f32_bits']['stats'][2560+2*9+4]^=1;p.write_bytes(encoded(d))
            with self.assertRaises(ValueError):replace(self.handle,context_file=p).query(self.target)

    def test_wrong_hardware_build_is_rejected_before_query(self):
        with tempfile.TemporaryDirectory(prefix='psr-context-test-')as name:
            p=Path(name)/'context.json';d=load('second-context-s25a.json');d['identity']['build']='24A445';p.write_bytes(encoded(d))
            with self.assertRaises(ValueError):identity(p,self.precision)

    def test_old_and_rejected_precision_contracts_are_not_silently_upgraded(self):
        for name in ['model-precision-s25b.json','model-precision-v2-s25c4.json']:
            with self.assertRaises(ValueError):identity(self.context,E/name)

    def test_wrong_target_identity_rejected(self):
        wrong=Target(replace(self.target.identity,build='24A445'),self.target.catalog_sha256,self.target.writer_half_bits)
        with self.assertRaises(ValueError):self.handle.query(wrong)

    def test_wrong_directory_digest_rejected(self):
        with self.assertRaises(ValueError):replace(self.handle,expected_catalog_sha256='0'*64).query(self.target)

    def test_changed_chunk_rejected_before_matching(self):
        with tempfile.TemporaryDirectory(prefix='psr-catalog-test-')as name:
            path=Path(name);manifest=load('context-catalog-s25e.json');catalog=path/'catalog.json';catalog.write_bytes(self.catalog.read_bytes())
            for part in manifest['chunks']:(path/part['name']).write_bytes((E/part['name']).read_bytes())
            f=path/manifest['chunks'][0]['name'];f.write_bytes(f.read_bytes()+b' ')
            with self.assertRaises(ValueError):replace(self.handle,catalog_file=catalog).query(self.target)

    def test_duplicate_state_is_rejected(self):
        i,m,p,rows=self.checked;d={'identity':vars(i),'partition_sha256':sha(self.partition),'rows':[rows[0],rows[0]]}
        with patch('context_color_api.load',return_value=d):
            with self.assertRaises(ValueError):read_rows([Path('fixture')],i,sha(self.partition))

    def test_partial_catalog_seal_keeps_missing_states(self):
        with tempfile.TemporaryDirectory(prefix='psr-catalog-test-')as name:
            path=Path(name);chunk=path/'chunk.json';chunk.write_bytes((E/'scan-000-s25d.json').read_bytes());m=seal_catalog(self.context,self.precision,self.partition,[chunk],path/'catalog.json');self.assertFalse(m['complete_model_coverage']);self.assertEqual(len(m['missing_state_ids']),130)

    def test_unmatched_border_returns_empty_not_nearest(self):
        a=self.target.writer_half_bits.copy();a[0,0,0]^=1;t=Target(self.target.identity,self.target.catalog_sha256,a);q=self.handle.query(t);self.assertEqual(q['candidate_union'],[]);self.assertEqual(q['found_f32_population'],0);self.assertTrue(q['coverage']['complete_model_coverage'])

    def test_final_code3_double_rounding_and_separate_offset_regression(self):
        bits=np.array([10903,8335,12388],dtype='u2');actual=host_encode(V.value(bits.view('f2'))).lo.astype('f2').view('u2');self.assertEqual(actual.tolist(),[13319,11757,13952]);self.assertNotEqual(int(actual[1]),11756);self.assertNotEqual(int(actual[1]),11759)

    def test_final_code3_profile_rejects_sets_and_f32_inputs(self):
        with self.assertRaises(TypeError):host_encode(V.bounds([.1,.2,.3],[.11,.21,.31]))
        with self.assertRaises(TypeError):host_encode(V.value([.1,.2,.3],'f'))

    def test_target_is_an_immutable_copy_without_true_control(self):
        a=self.target.writer_half_bits.copy();t=Target(self.target.identity,self.target.catalog_sha256,a);a[0,0,0]^=1;self.assertNotEqual(int(a[0,0,0]),int(t.writer_half_bits[0,0,0]));self.assertFalse(t.writer_half_bits.flags.writeable);self.assertEqual(set(t.record()),{'identity','catalog_sha256','writer_half_bits','true_control_provided_to_solver'});self.assertFalse(t.record()['true_control_provided_to_solver'])

    def test_boundary_plan_has_eight_new_controls_without_old_values(self):
        new=load('new-boundaries-s25e.json')['controls'];old={x['raw_f32_bits']for x in load('color-boundaries-s22c.json')['controls']};self.assertEqual(len(new),8);self.assertFalse(old&{x['raw_f32_bits']for x in new})

    def test_native_boundary_selected_path_and_internal_difference_are_distinct(self):
        n=load('native-boundaries-s25f.json');self.assertEqual(n['total_original_calls'],270);self.assertEqual(len(n['rows']),8);self.assertEqual(sum(x['selected_path_half_bit_mismatches']for x in n['rows']),0);self.assertEqual(sum(x['unselected_bright_bit_mismatches']for x in n['rows']),18);self.assertFalse(n['all_internal_observations_bit_exact'])

    def test_first_failures_retained_and_new_replay_does_not_rewrite_them(self):
        self.assertEqual(load('target-native-binding-s25c.json')['exit_code'],1);self.assertEqual(load('target-B-binding-s25c2.json')['exit_code'],1);self.assertEqual(load('replay-binding-s25c4.json')['exit_code'],1);new=load('target-replay-s25c6.json');self.assertEqual(new['native_calls'],0);self.assertEqual([x['selected_path_half_bit_mismatches']for x in new['rows']],[0,0])


if __name__=='__main__':unittest.main()
