import unittest
import numpy as np
from leaf_numeric import V
from cast_values import CastValues
from pixel_warmth import forward
from native_warmth_root_check import cases,model


class WarmthRootTests(unittest.TestCase):
    def test_person_one_selects_second_branch_without_first_warmth_feedthrough(self):
        data=next(cases());data[3]=1;data[5]=.1;data[7]=.1
        a=model('root',data,True);other=data.copy();other[4]=-.3;b=model('root',other,True)
        np.testing.assert_array_equal(a.lo,b.lo)

    def test_mapped_half_gate_can_skip_nonzero_f32_control(self):
        raw=np.zeros(34,dtype='f4');raw[0]=1e-4
        # 0.5+0.5*control rounds to half0.5 before the original gate.
        rgb=V.value([.2,.4,.8]);out=forward(rgb,CastValues(V.value(raw,'f')),V.value(.4))
        np.testing.assert_array_equal(out.lo,rgb.lo)

    def test_activated_known_set_covers_fixed_point(self):
        data=next(cases());p=model('root',data,True);b=model('root',data,False)
        self.assertTrue(np.all(p.lo>=b.lo)and np.all(p.lo<=b.hi))

    def test_both_person_extremes_are_separate_outputs(self):
        data=next(cases());data[3]=0;a=model('root',data,True);data[3]=1;b=model('root',data,True)
        self.assertGreater(np.max(abs(a.lo-b.lo)),.001)


if __name__=='__main__':unittest.main()
