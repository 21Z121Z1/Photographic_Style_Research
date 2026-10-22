import unittest
import numpy as np
from pixel_lighten import lighten,negative_lighten
from leaf_numeric import V,DomainUnknown
from all_pixel_leaves import models
from tone_interface import ConsumerFields
from test_bgfg_tone import packet
from semantic_tone import I
from bgfg_tone import run,PixelContext


class LightenTests(unittest.TestCase):
    def test_nonzero_leaves_depend_on_guide_and_cover_known_point(self):
        for fn,amount in [(lighten,.5),(negative_lighten,1.4)]:
            rgb=V.value([.2,.4,.8]);a=fn(rgb,V.value(.05),V.value(amount));b=fn(rgb,V.value(.9),V.value(amount))
            self.assertGreater(float(np.max(abs(a.lo-b.lo))),.01)
            bounds=fn(V.bounds(rgb.lo,rgb.lo),V.bounds(.05,.05),V.bounds(amount,amount))
            self.assertTrue(np.all(a.lo>=bounds.lo)and np.all(a.lo<=bounds.hi))

    def test_zero_guide_has_an_unproved_pow_domain_not_hardware_blockage(self):
        for fn,amount in [(lighten,.5),(negative_lighten,1.4)]:
            with self.assertRaises(DomainUnknown):fn(V.value([.2,.4,.8]),V.value(0),V.value(amount))

    def test_two_stage_bg_lighten_uses_available_shadow_and_lighten_models(self):
        p=packet();v=p.values.copy();v[9]=.3;p=ConsumerFields(p.controls,p.branch,v,p.host_f32_absolute_allowance)
        r=run('bg',I.point([.2,.4,.8]),p,PixelContext(.4,.5),leaf_models=models())
        self.assertEqual(r.status,'computed_set');self.assertFalse(r.full_helper_numeric_verified)


if __name__=='__main__':unittest.main()
