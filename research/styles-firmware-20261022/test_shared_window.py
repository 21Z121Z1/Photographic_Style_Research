import json,unittest
from pathlib import Path
import numpy as np
from guided_affine import A
from leaf_numeric import V,DomainUnknown
from complete_fixture import decode
from complete_forward import forward
from native_complete_check import comparisons
from pixel_skin import encode
from pixel_transfer import forward as transfer
from contrast_order_domains import ordered_box,positive,lattice_span_lower,THRESHOLD

ROOT=Path(__file__).parent/'evidence'


class SharedWindowTests(unittest.TestCase):
    def test_shared_generators_preserve_whole_range_and_nonlinear_remainders(self):
        x=A.box(-1,1);y=A.box(2,3);cancel=x.add(x.neg());self.assertLess(cancel.bounds()[1]-cancel.bounds()[0],1e-10)
        square=x.product(x);lo,hi=square.bounds();self.assertLessEqual(lo,0);self.assertGreaterEqual(hi,1);self.assertGreater(hi-lo,.99)
        quotient=x.div(y);lo,hi=quotient.bounds()
        for a in [-1,-.5,0,.5,1]:
            for b in [2,2.5,3]:self.assertLessEqual(lo,a/b);self.assertGreaterEqual(hi,a/b)
        with self.assertRaises(DomainUnknown):x.div(x)

    def test_fixed_context_widths_shrink_without_backend_pow_fallback(self):
        c=decode(json.loads((ROOT/'complete-context-s15a.json').read_text()));saved=json.loads((ROOT/'native-complete-s15a.json').read_text());native={n:np.array(a,dtype='u2').view('f2')for n,a in saved['native_half_bits'].items()};r=forward(c,point=False);m=comparisons(native,r)
        self.assertLess(m['observations']['FG_a']['max_width'],6);self.assertLess(m['observations']['FG_output']['max_width'],.7);self.assertLess(m['observations']['warm409']['max_width'],8);self.assertTrue(all(v['range_covered']for v in m['observations'].values()));self.assertEqual(len(r.pixel_unknowns),12);self.assertIsNone(r.writer)

    def test_bright_encode_contract_cannot_be_applied_to_output_transfer(self):
        saved=json.loads((ROOT/'native-complete-s15a.json').read_text());linear=np.array(saved['native_half_bits']['linear597'],dtype='u2').view('f2');target=np.array(saved['native_half_bits']['output600'],dtype='u2');wrong=0
        for y,x in np.ndindex(linear.shape[:2]):
            v=V.value(linear[y,x]);correct=transfer(v,3,to_linear=False);candidate=encode(v,host_fma=True);np.testing.assert_array_equal(correct.lo.astype('f2').view('u2'),target[y,x]);wrong+=np.count_nonzero(candidate.lo.astype('f2').view('u2')!=target[y,x])
        self.assertEqual(wrong,18)

    def test_alias_identity_never_equates_independent_boxes_or_skips_contracts(self):
        from leaf_numeric import mix
        a=V.bounds([.2,.3,.4],[.3,.5,.7]);w=V.bounds(.2,.8)
        self.assertIs(mix(a,a,w),a)
        other=V.bounds(a.lo,a.hi);r=mix(a,other,w);self.assertGreater(np.max(r.hi-r.lo),np.max(a.hi-a.lo))
        with self.assertRaises(TypeError):mix(a,a,V.value(.5))
        with self.assertRaises(TypeError):encode(V.value([.2,.3,.4]),host_fma='bright')

    def test_diagnostic_callsite_memory_widening_retains_FP_contract(self):
        from numeric_trace_host import widen_callsites
        ir='define void @caller(){\ncall void @probe() #1\ncall void @pure() #2\nret void\n}\nattributes #1 = { memory(none) "unsafe-fp-math"="true" }\nattributes #2 = { memory(none) }'
        fixed,changes=widen_callsites(ir,['probe']);self.assertIn('1',changes);self.assertIn('attributes #1 = { memory(readwrite) "unsafe-fp-math"="true" }',fixed);self.assertIn('attributes #2 = { memory(none) }',fixed)
        receipt=json.loads((ROOT/'internal-memory-s16b.json').read_text());self.assertEqual(receipt['native_main_calls'],3)
        for r in receipt['rows']:
            self.assertEqual(r['replayed_original']['callsite_memory_summary_changes'],{});self.assertFalse(r['probe_bit_differences_after_memory_review']);self.assertFalse(any(r['saved_final_observer_stability'].values()))

    def test_only_saved_BG_failures_use_order_and_budgeted_lattice(self):
        saved=json.loads((ROOT/'bg-dependency-s15c.json').read_text());receipt=json.loads((ROOT/'bg-orders-budget-s16c.json').read_text());self.assertEqual(receipt['original_cells'],8);self.assertEqual(receipt['remaining_unknown_original_cells'],1);self.assertEqual(receipt['unknown_positive_domains'],6)
        cell=next(c for c in saved['partition']['unknown_subsets']if c['cell']==43);box=V(np.array(cell['input_lo']),np.array(cell['input_hi']),'h',False);b=ordered_box(box,(0,1,2));self.assertIsNotNone(b);lower=lattice_span_lower(b);self.assertGreater(lower,THRESHOLD);self.assertLess(lower,2**-11)
        # Saved cell1 includes zero, yet a small span forces all channels near
        # its positive maximum lower bound. The original gate remains fixed.
        c1=next(c for c in saved['partition']['unknown_subsets']if c['cell']==1);v=V(np.array(c1['input_lo']),np.array(c1['input_hi']),'h',False);self.assertGreater(lattice_span_lower(v),THRESHOLD)
        for raw in [[0,.2,.2],[.2,.2,float(np.nextafter(np.float16(.2),np.float16(np.inf)))]]:
            vals=np.array(raw,dtype='f2').astype('f8');nominal=float(vals.max()-vals.min());budget_lower=nominal*(1-2**-10)-2**-24;self.assertGreaterEqual(budget_lower,lattice_span_lower(v))
        self.assertEqual(positive(b,V.value(saved['amount_half'],point=False),(0,1,2))['status'],'known');self.assertEqual(positive(b,V.value(saved['amount_half'],point=False),(0,1,2),active=False)['status'],'known')


if __name__=='__main__':unittest.main()
