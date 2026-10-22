import unittest
import numpy as np
from leaf_numeric import V,DomainUnknown,lazy_select
from leaf_domains import strictly_positive_branch


class ConditionalDomainTests(unittest.TestCase):
    def test_original_strict_guard_keeps_equality_in_else_and_all_positive_halves(self):
        for threshold in [0.,1e-5,.5]:
            x=V.bounds(0,1);restricted=strictly_positive_branch(x,threshold)
            halves=np.arange(0x3c01,dtype='u2').view('f2').astype('f8')
            selected=halves[halves>threshold]
            self.assertTrue(np.all(selected>=restricted.lo)and np.all(selected<=restricted.hi))
            self.assertGreater(restricted.lo,threshold)
        with self.assertRaises(DomainUnknown):strictly_positive_branch(V.value(.5),.5)

    def test_guard_domain_split_preserves_zero_else_without_dividing_by_zero(self):
        x=V.bounds(0,1)
        result=lazy_select(x.gt(0),lambda:V.bounds(1e-4,1e-4)/strictly_positive_branch(x),lambda:V.bounds(0,0))
        self.assertLessEqual(result.lo,0);self.assertGreaterEqual(result.hi,1)
        # Use a bounded numerator so the finite half budget also remains known.

    def test_point_operations_remain_identical_on_original_positive_branch(self):
        for value in [.01,.1,.5,1.]:
            p=V.value(value);self.assertIs(strictly_positive_branch(p,1e-5),p)


if __name__=='__main__':unittest.main()
