import unittest
import numpy as np
from leaf_numeric import V,DomainUnknown,fc
from pixel_color import smooth_sat,rich_sat,models
from semantic_tone import I
from bgfg_tone import PixelContext,MissingLeaf


class ColorTests(unittest.TestCase):
    def test_nonzero_saturation_changes_chroma_and_box_contains_points(self):
        for fn,args in [(smooth_sat,[.5]),(rich_sat,[1.25,3]),(rich_sat,[1.25,4])]:
            p=fn(V.value([.2,.4,.8]),*[V.value(x)for x in args]);b=fn(V.bounds([.2,.4,.8],[.2,.4,.8]),*[V.bounds(x,x)for x in args])
            self.assertGreater(np.max(abs(p.lo-np.array([.2,.4,.8]))),.005)
            self.assertTrue(np.all(p.lo>=b.lo)and np.all(p.lo<=b.hi))

    def test_smooth_low_gain_branch_uses_f32_threshold_not_rounded_half(self):
        threshold=fc('3F947AE140000000');a=np.float16(threshold);below=np.nextafter(a,np.float16(0));above=np.nextafter(a,np.float16(1))
        for gain in [below,a,above]:
            p=smooth_sat(V.value([.2,.4,.8]),V.value(gain))
            if float(gain)<threshold:self.assertEqual(len(set(p.lo)),1)
            else:self.assertGreater(np.ptp(p.lo),0)

    def test_rich_black_domain_stays_unknown_in_adapter(self):
        with self.assertRaises(DomainUnknown):rich_sat(V.value([0,0,0]),V.value(1.2),V.value(3))
        with self.assertRaises(MissingLeaf):models()['RichSat'](I.point([0,0,0]),I.point(1.2),PixelContext(.4,.5))

    def test_polar_sets_cover_branch_cut_and_interior_trig_extrema(self):
        angle=V.bounds(-.1,.1).atan2(V.bounds(-1,-.9))
        self.assertLessEqual(angle.lo,-np.pi);self.assertGreaterEqual(angle.hi,np.pi)
        for fn in ['sin','cos']:
            b=getattr(V.bounds(-4,4),fn)()
            self.assertLessEqual(b.lo,-1);self.assertGreaterEqual(b.hi,1)
        p=V.bounds(-.1,.1).square();self.assertEqual(p.lo,0);self.assertGreaterEqual(p.hi,.01)

    def test_rich_boundary_equality_keeps_controller_strength_three_path(self):
        c=V.value([.2,.4,.8]);a=rich_sat(c,V.value(.75),V.value(3));b=rich_sat(c,V.value(.75),V.value(4))
        self.assertTrue(np.isfinite(a.lo).all()and np.isfinite(b.lo).all())
        # Strength also changes the independent exponent: equality at the mask
        # gate does not imply the two complete leaf outputs are identical.
        self.assertGreater(np.max(abs(a.lo-b.lo)),0)


if __name__=='__main__':unittest.main()
