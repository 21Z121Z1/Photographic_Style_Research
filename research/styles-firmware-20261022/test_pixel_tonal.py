import unittest
import numpy as np
from leaf_numeric import V,DomainUnknown
from pixel_tonal import shadows,shadows_negative,models
from bgfg_tone import run,PixelContext
from semantic_tone import I
from tone_interface import ConsumerFields
from test_bgfg_tone import packet


class ShadowTests(unittest.TestCase):
    def test_both_nonzero_leaves_depend_on_supplied_guide_and_keep_black(self):
        rgb=V.value([.2,.4,.8])
        for fn,amount in [(shadows,.5),(shadows_negative,-.5)]:
            a=fn(rgb,V.value(.05),V.value(amount));b=fn(rgb,V.value(.9),V.value(amount))
            self.assertGreater(float(np.max(abs(a.lo-b.lo))),.01)
            zero=fn(V.value([0,0,0]),V.value(.4),V.value(amount));np.testing.assert_array_equal(zero.lo,[0,0,0])

    def test_shadow_set_covers_point_and_chromatic_exterior(self):
        for rgb in [[.2,.4,.8],[-.05,.6,1.1],[.4,.4,.4]]:
            for fn,amount in [(shadows,.5),(shadows_negative,-.5)]:
                x=V.value(rgb);p=fn(x,V.value(.4),V.value(amount));b=fn(V.bounds(x.lo,x.lo),V.bounds(.4,.4),V.bounds(amount,amount))
                self.assertTrue(np.all(p.lo>=b.lo)and np.all(p.lo<=b.hi))

    def test_nonzero_bg_shadow_adapter_removes_that_unknown(self):
        p=packet();v=p.values.copy();v[3]=.5;p=ConsumerFields(p.controls,p.branch,v,p.host_f32_absolute_allowance)
        r=run('bg',I.point([.2,.4,.8]),p,PixelContext(.4,.5),leaf_models=models())
        self.assertEqual(r.status,'computed_set');self.assertFalse(r.full_helper_numeric_verified)


if __name__=='__main__':unittest.main()
