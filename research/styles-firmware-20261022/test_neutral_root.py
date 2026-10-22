import unittest
import numpy as np
from leaf_numeric import V,DomainUnknown
from cast_values import CastValues
from pixel_neutral_root import NeutralStats,forward
from pixel_neutral import skin_warmth_positive


class NeutralRootTests(unittest.TestCase):
    def test_renderer_block_is_not_twelve_scalar_prior_and_offsets_are_explicit(self):
        with self.assertRaises(TypeError):CastValues(V.value(np.zeros(12),'f'))
        raw=CastValues(V.value(np.arange(34),'f'))
        self.assertEqual(raw.scalar(15).lo,27);np.testing.assert_array_equal(raw.array(7).lo,[9,10,11])

    def test_disabled_original_root_needs_no_stats_and_does_not_fake_an_active_leaf(self):
        rgb=V.value([.2,.4,.8]);raw=np.zeros(34,dtype='f4');raw[27:31]=.3
        out=forward(rgb,enabled=False,cast=CastValues(V.value(raw,'f')),skin=V.value(.7),person=V.value(.4),use_skin=True,stats=None)
        self.assertIs(out,rgb)

    def test_guard_union_keeps_all_supplied_coefficients_without_a_center_fallback(self):
        raw=np.zeros(34,dtype='f4');lo=raw.copy();hi=raw.copy();lo[27]=-2e-5;hi[27]=2e-5
        stats=NeutralStats(*[V.bounds(x,x,'f')for x in [.7,.45,.3]])
        box=forward(V.bounds([.8,.3,.15],[.8,.3,.15]),enabled=True,cast=CastValues(V.bounds(lo,hi,'f')),skin=V.bounds(.7,.7),person=V.bounds(.4,.4),use_skin=True,stats=stats)
        for amount in [-2e-5,0,2e-5]:
            p=raw.copy();p[27]=amount;q=forward(V.value([.8,.3,.15]),enabled=True,cast=CastValues(V.value(p,'f')),skin=V.value(.7),person=V.value(.4),use_skin=True,stats=NeutralStats(*[V.value(x,'f')for x in [.7,.45,.3]]))
            self.assertTrue(np.all(q.lo>=box.lo)and np.all(q.lo<=box.hi))

    def test_skin_warmth_unmodeled_mode_is_explicitly_rejected(self):
        with self.assertRaises(DomainUnknown):skin_warmth_positive(V.value([.2,.4,.8]),V.value(.4),V.value(.7),V.value([.65,.1,.05]),V.value(0),V.value(.3))


if __name__=='__main__':unittest.main()
