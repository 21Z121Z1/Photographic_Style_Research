import unittest
import numpy as np
from leaf_numeric import V,hc
from ltm_gain import Parameters,forward,guarded_ratio
from semantic_tone import Curve1D


class LTMGainTests(unittest.TestCase):
    def test_guard_equality_and_neighbors(self):
        eps=np.float16(hc('1c04'));low=np.nextafter(eps,np.float16(0))
        r=guarded_ratio(V.value([.5,.5,.5]),V.value([0,low,eps]))
        self.assertEqual(list(r.lo[:2]),[0,0]);self.assertGreater(r.lo[2],100)

    def test_boundary_set_is_union_not_center(self):
        eps=float(hc('1c04'));r=guarded_ratio(V.bounds([.5]*3,[.5]*3),V.bounds([eps/2]*3,[eps*2]*3))
        self.assertTrue(np.all(r.lo<=0));self.assertTrue(np.all(r.hi>100));self.assertFalse(r.point)

    def test_ltm_coefficients_do_not_enter_producer_but_exposure_does(self):
        curve=Curve1D(tuple(np.linspace(0,1,17)),'test');ref=V.value([.3,.5,.8]);linear=V.value([.2,.4,.6]);params=[.6,.8,.7,1.2,.6,.3,.4]
        def run(p):return forward(ref,linear,Parameters(V.value(np.eye(3),'f'),V.value(1,'f'),V.value(p,'f')),curve)
        a=run(params);p=params.copy();p[0]=0;p[1]=0;p[5]=0;p[6]=0;b=run(p)
        np.testing.assert_array_equal(a.bg203.lo,b.bg203.lo);np.testing.assert_array_equal(a.fg205.lo,b.fg205.lo)
        p[2]=1.1;self.assertGreater(np.max(abs(run(p).bg203.lo-b.bg203.lo)),.1)


if __name__=='__main__':unittest.main()
