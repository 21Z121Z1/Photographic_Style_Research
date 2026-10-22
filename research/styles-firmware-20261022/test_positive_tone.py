from dataclasses import replace
import unittest
import numpy as np
from positive_tone import PositiveToneStats,PositiveToneContext,coefficients
from positive_tone_skin import coefficients as old_skin


def context():return PositiveToneContext(PositiveToneStats(.4,.003,.05),tuple([0.]*66))


class PositiveBlockTests(unittest.TestCase):
    def test_all_blocks_reuse_accepted_two_fields_and_zero_is_not_global_identity(self):
        c=context()
        for t in (0.,-0.,2**-24,1.):
            r=coefficients(t,c);old=old_skin(t)
            self.assertEqual((len(r.background),len(r.foreground),len(r.semantic)),(17,16,7))
            np.testing.assert_array_equal(r.foreground[9:11],[old.theta9,old.theta10])
            self.assertTrue(np.isfinite(r.values()).all());self.assertFalse(r.native_GPU_verified)
        self.assertAlmostEqual(coefficients(0,c).foreground[0],.2,places=7)
        tun=list(c.tone_tuning);tun[14]=.3
        self.assertAlmostEqual(coefficients(0,replace(c,tone_tuning=tuple(tun))).background[1],.3,places=7)

    def test_foreground_piecewise_discontinuities_are_retained(self):
        c=context();a=coefficients(np.nextafter(np.float32(.5),np.float32(0)),c);b=coefficients(np.nextafter(np.float32(.5),np.float32(1)),c)
        self.assertGreater(b.foreground[4]-a.foreground[4],.05)
        edge=.5**(1/.75);a=coefficients(edge-1e-5,c);b=coefficients(edge+1e-5,c)
        self.assertGreater(a.foreground[2]-b.foreground[2],.14)

    def test_stats_tuning_and_reference_single_interventions_have_scoped_effects(self):
        c=context();a=coefficients(.5,c)
        b=coefficients(.5,replace(c,stats=replace(c.stats,slot5_field6=.5)))
        np.testing.assert_array_equal(a.background,b.background);np.testing.assert_array_equal(a.foreground,b.foreground)
        self.assertNotEqual(a.semantic[1],b.semantic[1])
        tun=list(c.tone_tuning);tun[11]=1
        b=coefficients(.5,replace(c,tone_tuning=tuple(tun)));self.assertGreater(b.foreground[11],a.foreground[11])
        b=coefficients(.5,replace(c,baseline_exposure_field7=2));self.assertEqual(b.semantic[2],2)

    def test_cast_and_tuning_type_are_distinct_and_scene4_clamps(self):
        c=context();a=coefficients(.5,c);b=coefficients(.5,replace(c,cast_code=14))
        self.assertEqual(b.foreground[14],-.25);self.assertEqual(a.foreground[14],0)
        tun=list(c.tone_tuning);tun[29]=1;tun[30]=-1;tun[25:29]=[.1,.2,.3,.4];tun[31:35]=[.4,.5,.6,.7]
        c=replace(c,tone_tuning=tuple(tun),tuning_type=4,scene_brightness=2)
        np.testing.assert_array_equal(coefficients(.5,c).values(),coefficients(.5,replace(c,scene_brightness=16)).values())

    def test_model_domain_and_zero_stats_are_explicit(self):
        c=context();self.assertTrue(np.isfinite(coefficients(.5,replace(c,stats=PositiveToneStats(0,0,0))).values()).all())
        for t in (-1e-8,1.01,np.inf,np.nan):
            with self.assertRaises(ValueError):coefficients(t,c)
        for bad in (replace(c,tone_tuning=(0.,)),replace(c,tuning_type=4),replace(c,tuning_type=True),replace(c,stats=PositiveToneStats(-.1,0,0)),replace(c,stats=PositiveToneStats(0,np.nan,0)),replace(c,baseline_exposure_field7=17)):
            with self.assertRaises(ValueError):coefficients(.5,bad)


if __name__=='__main__':unittest.main()
