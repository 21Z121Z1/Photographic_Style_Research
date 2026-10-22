import unittest
import numpy as np
from leaf_numeric import V,select,lazy_select,DomainUnknown


class NumericTests(unittest.TestCase):
    def test_precision_transitions_are_explicit_and_zero_sign_is_bounded(self):
        with self.assertRaises(TypeError):V.value(.1)+V.value(.1,'f')
        with self.assertRaises(TypeError):V.value(1)+V.bounds(.1,.2)
        with self.assertRaises(DomainUnknown):V(np.array(.1),np.array(.2),point=True)
        self.assertNotEqual(float(V.value(.1).lo),float(V.value(.1,'f').lo))
        a=V.bounds(0,0);b=a*V.bounds(2,2);self.assertEqual(float(b.lo),0);self.assertEqual(float(b.hi),0)

    def test_undetermined_comparison_unions_both_outputs(self):
        a=V.bounds(.49,.51);r=select(a.lt(.5),V.bounds(1,1),V.bounds(2,2))
        self.assertEqual((float(r.lo),float(r.hi)),(1,2))
        result=lazy_select(V.value(0).gt(0),lambda:V.value(1)/V.value(0),lambda:V.value(0))
        self.assertEqual(float(result.lo),0)

    def test_unproved_division_pow_and_nonfinite_domains_fail_closed(self):
        with self.assertRaises(DomainUnknown):V.bounds(1,1)/V.bounds(-.1,.1)
        with self.assertRaises(DomainUnknown):V.value(-1).pow(.5)
        with self.assertRaises(DomainUnknown):V.value(np.inf)


if __name__=='__main__':unittest.main()
