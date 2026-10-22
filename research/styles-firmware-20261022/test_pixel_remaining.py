import unittest
import numpy as np
from leaf_numeric import V,DomainUnknown
from pixel_remaining import FUNCTIONS,models,under_grass,under_tone,tonal_contrast,highlight_neg
from semantic_tone import I
from bgfg_tone import PixelContext,run,MissingLeaf
from test_bgfg_tone import packet
from tone_interface import ConsumerFields


class RemainingLeafTests(unittest.TestCase):
    def test_each_nonzero_leaf_has_a_finite_point_and_covering_input_box(self):
        for name,fn in FUNCTIONS.items():
            amount=-.11 if name=='highlightNeg'else .3
            p=fn(V.value([.2,.4,.8]),V.value(.4),V.value(amount))
            b=fn(V.bounds([.2,.4,.8],[.2,.4,.8]),V.bounds(.4,.4),V.bounds(amount,amount))
            self.assertTrue(np.all(p.lo>=b.lo)and np.all(p.lo<=b.hi),name)
            self.assertGreater(np.max(abs(p.lo-np.array([.2,.4,.8]))),1e-5,name)

    def test_person_skin_and_guide_have_distinct_caller_argument_identity(self):
        c=I.point([.2,.4,.8]);a=I.point(.3);m=models()
        for name in ['underGrassFilter','underToneFilter','tonalContrastFilter']:
            x=m[name](c,a,PixelContext(.1,.4,.6));y=m[name](c,a,PixelContext(.9,.4,.6))
            np.testing.assert_array_equal(x.lo,y.lo);np.testing.assert_array_equal(x.hi,y.hi)
        # With person==1 BG underGrass blends back to its clamped input.
        p=under_grass(V.value(c.lo),V.value(1),V.value(.3))
        np.testing.assert_array_equal(p.lo,V.value(c.lo).lo)
        # FG underTone instead blends FROM the input with skin as its weight.
        p=under_tone(V.value(c.lo),V.value(0),V.value(.3))
        np.testing.assert_array_equal(p.lo,V.value(c.lo).lo)

    def test_neck_black_zero_guard_and_invalid_guide_fail_closed(self):
        p=tonal_contrast(V.value([0,0,0]),V.value(.4),V.value(.3));np.testing.assert_array_equal(p.lo,[0,0,0])
        with self.assertRaises(DomainUnknown):highlight_neg(V.value([.2,.4,.8]),V.value(-.1),V.value(-.11))
        with self.assertRaises(MissingLeaf):models()['smartContrast'](I.point([-1,-1,-1]),I.point(.3),PixelContext(.4,.5))

    def test_each_remaining_controller_slot_is_connected_to_a_real_set_model(self):
        from all_pixel_leaves import models as available
        for block,index in [('bg',5),('bg',4),('bg',10),('fg',17+15),('fg',17+14),('fg',17+8)]:
            p=packet();v=p.values.copy();v[index]=.2;p=ConsumerFields(p.controls,p.branch,v,p.host_f32_absolute_allowance)
            r=run(block,I.point([.2,.4,.8]),p,PixelContext(.4,.5,.3),semantic_rgb=I.point([.2,.4,.8]),leaf_models=available())
            self.assertEqual(r.status,'computed_set',(block,index,r.missing_operator));self.assertFalse(r.full_helper_numeric_verified)


if __name__=='__main__':unittest.main()
