import json,unittest,tempfile
from pathlib import Path
from unittest.mock import patch
import numpy as np
from leaf_numeric import V,DomainUnknown
from pixel_leaves import contrast,contrast_independent
import pixel_leaves
from contrast_sorted import saved_cells,family_id,enclose_family,whole_supported,ROOT_LO,ROOT_HI
from contrast_span_joint import CELL0_AMOUNT
from selective_neutral_joint import Inputs,enclose
from pixel_selective import SelectiveTexture

E=Path(__file__).parent/'evidence'


class SortedSameFrameTests(unittest.TestCase):
    def test_saved_cover_and_strict_admission_do_not_use_a_parent_center(self):
        cells,ids=saved_cells();self.assertEqual(len(cells),64);self.assertEqual(ids,{1,17,21,22,38,42,43});a=V.value(CELL0_AMOUNT,point=False);parent=V(np.array(ROOT_LO),np.array(ROOT_HI),'h',False)
        self.assertTrue(whole_supported(parent,a));self.assertIsNone(family_id(parent,a))
        with self.assertRaises(DomainUnknown):contrast_independent(parent,a)
        out=contrast(parent,a);self.assertLess(float(np.max(out.hi-out.lo)),9500);self.assertGreater(float(np.max(out.hi-out.lo)),9000)
        self.assertFalse(whole_supported(parent,V.value(CELL0_AMOUNT,point=True)));self.assertFalse(whole_supported(parent,V.value(.04,point=False)))

    def test_sorted_branches_match_the_prior_arithmetic_and_restore_no_global_patches(self):
        old=json.loads((E/'bg-orders-budget-s16c.json').read_text());now=json.loads((E/'contrast-default-s19a.json').read_text());before=(V.min_channels,V.__truediv__,pixel_leaves.channel_span)
        i,lo,hi=next(v for v in saved_cells()[0]if v[0]==1);r=enclose_family(V(np.array(lo),np.array(hi),'h',False),V.value(CELL0_AMOUNT,point=False));self.assertEqual(len(r.branches),12);self.assertEqual(before,(V.min_channels,V.__truediv__,pixel_leaves.channel_span))
        for row in now['S19_sorted_subdomains']['families_with_branches']:
            previous=next(x for x in old['rows']if x['original_cell']==row['cell'])
            for b in row['branches']:
                p=next(x for x in previous['orders']if x['order']==b['order']);p=p if b['branch']=='positive'else p['else_branch'];self.assertEqual(b['status'],'known');self.assertEqual(b['max_width'],p['max_width'])

    def test_default64_counts_are_distinct_from_historical_ordered_domain_counts(self):
        r=json.loads((E/'contrast-default-s19a.json').read_text());self.assertEqual(r['default_counts']['known'],64);self.assertEqual(r['default_counts']['unknown'],0);self.assertEqual(r['S19_sorted_subdomains']['known_positive'],42);self.assertEqual(r['S19_sorted_subdomains']['known_else'],42);self.assertEqual(r['historical_S16_counts_separate']['unknown_positive'],6)
        self.assertEqual(json.loads((E/'bg-default-replay-s18a.json').read_text())['default_unknown_cells'],7);self.assertFalse(r['source_output_oracle_used'])

    def test_actual_next_BG_failure_is_whites_product_over_shared_z_not_old_contrast(self):
        r=json.loads((E/'contrast-default-s19a.json').read_text())['original_S14C_case0'];self.assertEqual(r['unknown_operator'],'BG352');self.assertFalse(r['full_BG_verified']);self.assertEqual([v['leaf']for v in r['leaf_trace']],['shadows','contrast','whites_curve']);self.assertEqual(r['first_unhandled_leaf']['leaf'],'whites_curve')
        q=next(x for x in r['first_unhandled_leaf']['arithmetic_failures']if x['operation']=='original division');self.assertEqual(q['arguments'][1]['lo'],2**-24);self.assertEqual(q['arguments'][0]['precision'],'h')

    def test_exact_saved_host_inputs_have_local_positive_bounds_without_replacing_upstream(self):
        r=json.loads((E/'selective-sameframe-s19b.json').read_text());self.assertEqual(len(r['local_certificates']),12);self.assertTrue(all(v['local_negative_base_excluded_under_declared_budgets']for v in r['local_certificates']));cloud=r['saved_host_warm_cloud'];self.assertTrue(cloud['negative_base_excluded_under_declared_budgets']);self.assertFalse(cloud['RGB110_is_in_cloud']);self.assertTrue(r['first_original_probe_covered_by_new_local_certificate'])
        H=lambda x:V.value(x,point=False);rgb=V.bounds(cloud['input_lo'],cloud['input_hi']);out=enclose(Inputs(rgb,H(.4),H(.25),H(.2),SelectiveTexture(np.zeros((4,360,4),dtype='f2'),'saved zero lookup'),tuple(H([0,0])for _ in range(3)),H([0,0,0]),H(0)));self.assertGreater(float(np.min(out.converted.lo)),.16)
        # The same lower-root refinement must still cover the already saved
        # full-clamp negative witness; local observed-input positivity cannot
        # turn it into a global nonnegative-domain assertion.
        witness=json.loads((E/'selective-domain-s18b.json').read_text());negative=enclose(Inputs(H(witness['witness_rgb_half']),H(.4),H(.25),H(.2),SelectiveTexture(np.zeros((4,360,4),dtype='f2'),'saved zero lookup'),tuple(H([0,0])for _ in range(3)),H([0,0,0]),H(0)));native=np.asarray(witness['native_converted_half']);self.assertTrue(np.all(native>=negative.converted.lo)and np.all(native<=negative.converted.hi));self.assertLess(negative.converted.lo[2],0)
        self.assertEqual(r['full_propagated_set']['selective_unknown_pixels'],12);self.assertEqual(r['full_propagated_set']['internal_unknowns'],24);self.assertFalse(r['full_propagated_set']['writer_set_known']);self.assertEqual(r['first_outer_box_admitting_clamp_witness'],'saturated374');self.assertTrue(r['minimum_unresolved_relation']['observed_cloud_not_substituted_into_full_chain'])

    def test_mismatched_saved_context_is_rejected_before_model_evaluation(self):
        from selective_sameframe_domain import check
        with tempfile.TemporaryDirectory(prefix='psr-s19-pair-')as t:
            p=Path(t);d=json.loads((E/'complete-context-s15a.json').read_text());d['identity']['build']='mismatch';(p/'context.json').write_text(json.dumps(d))
            with patch('selective_sameframe_domain.forward',side_effect=AssertionError('must not evaluate mismatched pair')):
                with self.assertRaisesRegex(ValueError,'Exact paired'):check(p/'context.json',E/'native-complete-s15a.json',E/'selective-one-pixel-s17a.json',p/'out.json')
                native=json.loads((E/'native-complete-s15a.json').read_text());native['native_half_bits']['warm409'][0][0][0]^=1;(p/'native.json').write_text(json.dumps(native))
                with self.assertRaisesRegex(ValueError,'Exact paired'):check(E/'complete-context-s15a.json',p/'native.json',E/'selective-one-pixel-s17a.json',p/'out.json')
            self.assertFalse((p/'out.json').exists())


if __name__=='__main__':unittest.main()
