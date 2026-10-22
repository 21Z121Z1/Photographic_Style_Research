import unittest
import numpy as np
from leaf_numeric import V,DomainUnknown
from pixel_leaves import whites_curve,airy,contrast,models
from semantic_tone import Curve1D,I
from bgfg_tone import run,PixelContext
from test_bgfg_tone import packet
from tone_interface import ConsumerFields


class PixelLeafTests(unittest.TestCase):
    def curve(self):return Curve1D(tuple(np.linspace(0,1,17)**.8),'supplied whites working coordinate')

    def test_whites_modes_are_distinct_nonzero_operators(self):
        rgb=V.value([.2,.4,.8]);amount=V.value(.75)
        a=whites_curve(rgb,amount,self.curve(),V.value(0));b=whites_curve(rgb,amount,self.curve(),V.value(1))
        self.assertGreater(float(np.max(abs(a.lo-rgb.lo))),.001)
        self.assertGreater(float(np.max(abs(a.lo-b.lo))),.001)

    def test_airy_declares_black_unknown_and_nonzero_gamma_changes_direction(self):
        rgb=V.value([.2,.4,.8]);a=airy(rgb,V.value(.7));b=airy(rgb,V.value(1.3))
        self.assertTrue(np.all(a.lo>rgb.lo));self.assertTrue(np.all(b.lo<rgb.lo))
        with self.assertRaises(DomainUnknown):airy(V.value([0,0,0]),V.value(.7))

    def test_contrast_sign_and_gray_branch_keep_finite_channel_contract(self):
        rgb=V.value([.2,.4,.8]);a=contrast(rgb,V.value(.25));b=contrast(rgb,V.value(-.25))
        self.assertGreater(float(np.max(abs(a.lo-b.lo))),.01)
        gray=contrast(V.value([.4]*3),V.value(.25));np.testing.assert_array_equal(gray.lo,[gray.lo[0]]*3)
        box=contrast(V.bounds(rgb.lo,rgb.lo),V.bounds(.25,.25));self.assertTrue(np.all(a.lo>=box.lo)and np.all(a.lo<=box.hi))

    def test_nonzero_bg_contrast_adapter_removes_that_unknown(self):
        p=packet();v=p.values.copy();v[1]=.25;p=ConsumerFields(p.controls,p.branch,v,p.host_f32_absolute_allowance)
        r=run('bg',I.point([.2,.4,.8]),p,PixelContext(.4,.5),leaf_models=models(self.curve()))
        self.assertEqual(r.status,'computed_set');self.assertFalse(r.full_helper_numeric_verified)


if __name__=='__main__':unittest.main()
