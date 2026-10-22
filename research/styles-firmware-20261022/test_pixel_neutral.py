import unittest
import numpy as np
from leaf_numeric import V
from pixel_neutral import de_red,de_yellow,red_neutral_only,direction


class NeutralLeafTests(unittest.TestCase):
    def test_supplied_reference_affects_active_red_path(self):
        rgb=V.value([.8,.3,.15]);a=de_red(rgb,V.value(.7),V.value(.4),V.value([.65,.1,.05]),V.value(.3));b=de_red(rgb,V.value(.7),V.value(.4),V.value([.65,0,0]),V.value(.3))
        self.assertGreater(np.max(abs(a.lo-b.lo)),1e-5)

    def test_zero_reference_chroma_uses_original_zero_direction_branch(self):
        for make in [lambda x:V.value(x),lambda x:V.bounds(x,x)]:
            _,unit=direction(make([.65,0,0]));np.testing.assert_array_equal(unit.lo,[0,0]);np.testing.assert_array_equal(unit.hi,[0,0])

    def test_all_active_models_propagate_supplied_sets(self):
        for make,point in [(lambda x:V.value(x),True),(lambda x:V.bounds(x,x),False)]:
            x=make([.8,.3,.15]);r=make([.65,.1,.05]);m=make(.7);a=make(.3)
            out=[de_red(x,m,make(.4),r,a),de_yellow(x,m,r,a),red_neutral_only(x,m,r,a,make(.4),make(.8))]
            self.assertTrue(all(o.point==point and np.isfinite(o.lo).all()for o in out))

    def test_fmod_interval_keeps_both_sides_of_wrap(self):
        a=V.bounds(6.2,6.4).fmod(V.bounds(6.28125,6.28125))
        self.assertLessEqual(a.lo,0);self.assertGreaterEqual(a.hi,6.28)


if __name__=='__main__':unittest.main()
