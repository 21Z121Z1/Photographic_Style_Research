import json,unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
from leaf_numeric import V,DomainUnknown
from pixel_leaves import contrast,contrast_independent
from contrast_span_joint import CELL0_LO,CELL0_HI,CELL0_AMOUNT,cell0_supported
from trace_consumer_paths import trace

E=Path(__file__).parent/'evidence'


class DomainConnectionTests(unittest.TestCase):
    def test_default_contrast_admits_the_whole_saved_cell0_only_after_old_failure(self):
        rgb=V(np.array(CELL0_LO),np.array(CELL0_HI),'h',False);amount=V.value(CELL0_AMOUNT,point=False)
        self.assertTrue(cell0_supported(rgb,amount))
        with self.assertRaises(DomainUnknown):contrast_independent(rgb,amount)
        v=contrast(rgb,amount);receipt=json.loads((E/'bg-cell0-joint-s17c.json').read_text());np.testing.assert_array_equal(v.lo,receipt['proof']['output_lo']);np.testing.assert_array_equal(v.hi,receipt['proof']['output_hi'])

    def test_outside_cell0_or_different_amount_keeps_old_unknown(self):
        data=json.loads((E/'bg-dependency-s15c.json').read_text());rgb=V(np.array(data['contrast_input_lo']),np.array(data['contrast_input_hi']),'h',False);amount=V.value(CELL0_AMOUNT,point=False)
        self.assertFalse(cell0_supported(rgb,amount))
        # S19 now admits the exact saved parent via its complete64 cover.
        # A box outside that new strict domain keeps the original unknown.
        outside=V(rgb.lo,rgb.hi+np.array([0.,.001,0.]),'h',False)
        with self.assertRaises(DomainUnknown):contrast(outside,amount)
        base=V(np.array(CELL0_LO),np.array(CELL0_HI),'h',False);self.assertFalse(cell0_supported(base,V.value(np.nextafter(np.float16(CELL0_AMOUNT),np.float16(np.inf)),point=False)))
        with patch('pixel_leaves.contrast_independent',side_effect=DomainUnknown('original domain')):
            with self.assertRaisesRegex(DomainUnknown,'original domain'):contrast(base,V.value(.04,point=False))

    def test_saved64_replay_and_complete_BG_first_unknown_are_kept_separate(self):
        r=json.loads((E/'bg-default-replay-s18a.json').read_text());self.assertEqual(len(r['rows']),64);self.assertEqual(r['independent_unknown_cells'],8);self.assertEqual(r['default_unknown_cells'],7);self.assertEqual([x['cell']for x in r['rows']if x['joint_admitted']],[0]);self.assertEqual(r['original_S14C_case0']['unknown_operator'],'BG352');self.assertFalse(r['original_S14C_case0']['complete_BG_verified']);self.assertTrue(all(v['covered']for v in r['original_S14C_case0']['known_prefix_ranges'].values()))
        q=r['original_S14C_case0']['contrast_calls'][0]['first_division_failure'];self.assertGreater(q['denominator_lo'],0);self.assertEqual(q['precision'],'h')

    def test_negative_domain_witness_is_before_pow_not_a_pow1_simplification(self):
        r=json.loads((E/'selective-domain-s18b.json').read_text());self.assertEqual(r['witness_rgb_half'],[1,1,0]);actual=np.array(r['native_half_bits'],dtype='u2').view('f2');self.assertLess(actual[2],0);self.assertEqual(actual[3],1);self.assertFalse(r['post_pow_SSA213_executed']);self.assertEqual(r['original_host_prefix_calls'],1);self.assertEqual(r['model_vs_host_converted_bit_mismatches'],0)
        with self.assertRaises(DomainUnknown):V.value(actual[:3]).pow(V.value(actual[3]))

    def test_untyped_call_argument_alias_reaches_the_actual_field_byte(self):
        source='''define void @root(ptr %0){
%1=getelementptr i8, ptr %0, i64 556
call void @child(ptr dereferenceable(64) %1)
ret void
}
define void @child(ptr %0){
%1=bitcast ptr %0 to ptr
%2=getelementptr i8, ptr %1, i64 48
%3=load float, ptr %2
ret void
}'''
        r=trace(source,'root',0);self.assertFalse(r['unresolved']);self.assertEqual(r['target_read_count'],1);self.assertEqual(r['parameter_accesses'][0]['target_fields'],['fg.faceI']);self.assertEqual(r['parameter_accesses'][0]['offset'],604)

    def test_dynamic_and_stored_pointer_escapes_remain_unresolved(self):
        source='''define void @root(ptr %0,i64 %1,ptr %2){
%3=getelementptr i8, ptr %0, i64 %1
%4=load float, ptr %3
store ptr %0, ptr %2
ret void
}'''
        r=trace(source,'root',0);self.assertGreaterEqual(len(r['unresolved']),3);self.assertEqual(r['target_read_count'],0)
        actual=json.loads((E/'consumer-paths-s18c.json').read_text());self.assertEqual(actual['payload_headers_consumer_scanned'],0);self.assertEqual(actual['closure']['contexts'],12);self.assertFalse(actual['closure']['unresolved']);self.assertEqual(len(actual['closure']['bounded_induction_loops']),1);self.assertEqual(len(actual['fields']),9);self.assertFalse(actual['global_unused_claim'])

    def test_join_with_an_untracked_external_pointer_cannot_be_called_an_alias_identity(self):
        source='''define void @root(ptr %0,ptr %1,i1 %2){
%3=select i1 %2, ptr %0, ptr %1
%4=load float, ptr %3
ret void
}'''
        r=trace(source,'root',0);self.assertEqual(len(r['unresolved']),2);self.assertEqual(r['unresolved'][0]['kind'],'divergent pointer join')


if __name__=='__main__':unittest.main()
