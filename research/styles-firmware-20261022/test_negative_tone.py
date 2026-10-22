from dataclasses import replace
import unittest
import numpy as np
from negative_tone import ToneStats,NegativeToneContext,coefficients


def context():
    return NegativeToneContext(ToneStats(.4,.5,.08,.06,.003,.05,.02,.008,.5),tuple([0.]*66))


class NegativeToneTests(unittest.TestCase):
    def test_three_complete_coefficient_blocks_and_negative_foreground_skin_terms(self):
        c=context()
        for t in [-1,-.5,-2**-24]:
            r=coefficients(t,c)
            self.assertEqual((len(r.background),len(r.foreground),len(r.semantic)),(17,16,7))
            self.assertTrue(np.isfinite(r.values()).all())
            np.testing.assert_array_equal(r.foreground[[9,10]],[0,0])
            self.assertGreater(r.foreground[15],0)
            self.assertFalse(r.native_GPU_verified)

    def test_scene_base_selection_and_scene4_brightness_interpolation(self):
        tun=np.zeros(66);tun[21:25]=[.1,.2,.3,.4];tun[35:39]=[.4,.5,.6,.7]
        c=replace(context(),tone_tuning=tuple(tun))
        a=coefficients(-.5,c);b=coefficients(-.5,replace(c,scene_code=3))
        np.testing.assert_allclose(a.background[[7,8,9]],[.3,1.2,.4],atol=3e-8,rtol=1e-7)
        np.testing.assert_allclose(b.background[[7,8,9]],[.6,1.5,.7],atol=3e-8,rtol=1e-7)
        tun[29]=1;tun[30]=-1;tun[31:35]=[.2,.4,.6,.8];tun[25:29]=[.4,.6,.8,1]
        c=replace(c,scene_code=4,scene_brightness=0,tone_tuning=tuple(tun))
        np.testing.assert_allclose(coefficients(-.5,c).background[[7,8,9]],[.7,1.5,.9],atol=3e-8,rtol=1e-7)

    def test_same_tone_with_different_explicit_stats_is_not_a_fixed_curve(self):
        c=context();a=coefficients(-.5,c)
        changed=replace(c,stats=replace(c.stats,slot0_field4=1.2,slot5_field4=.1))
        b=coefficients(-.5,changed)
        self.assertGreater(float(np.max(abs(a.values()-b.values()))),.05)

    def test_blend_clamp_saturates_and_foreground_does_not_read_blend_field(self):
        c=context();a=coefficients(-.5,replace(c,stats=replace(c.stats,stats_field4=2)))
        b=coefficients(-.5,replace(c,stats=replace(c.stats,stats_field4=10)))
        np.testing.assert_array_equal(a.values(),b.values())
        low=coefficients(-.5,replace(c,stats=replace(c.stats,stats_field4=-1)))
        np.testing.assert_array_equal(a.foreground,low.foreground)
        self.assertGreater(float(np.max(abs(a.semantic-low.semantic))),.001)

    def test_semantic_field5_uses_the_correct_two_stage_mix_near_zero(self):
        # Regression for the first native comparison: starting the final inner
        # mix at .7 would leave a spurious .3 discontinuity in this coefficient.
        c=context();c=replace(c,stats=replace(c.stats,stats_field4=1))
        self.assertAlmostEqual(coefficients(-2**-24,c).semantic[5],1,places=6)

    def test_zero_stats_are_kept_but_invalid_context_is_rejected(self):
        c=context();self.assertTrue(np.isfinite(coefficients(-.5,replace(c,stats=ToneStats(*([0.]*9)))).values()).all())
        for t in [0,.1,-1.01,-2**-25,float('nan')]:
            with self.assertRaises(ValueError):coefficients(t,c)
        for bad in [replace(c,blend_high=c.blend_low),replace(c,tone_tuning=(0.,)),replace(c,scene_code=4),replace(c,stats=replace(c.stats,slot5_field4=float('nan')))]:
            with self.assertRaises(ValueError):coefficients(-.5,bad)


if __name__=='__main__':unittest.main()
