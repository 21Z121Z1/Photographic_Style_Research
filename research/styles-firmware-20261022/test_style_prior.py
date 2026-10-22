import unittest
import numpy as np
from style_prior import SystemLayout, PriorFactors, factors_from_reduced_sum, lhs_updates, rhs_updates


class StylePriorTests(unittest.TestCase):
    def test_prior_floor_and_normalization_without_invented_reduction(self):
        layout=SystemLayout(7,5,2)
        p=factors_from_reduced_sum(70,layout,PriorFactors(.5,.25,0))
        np.testing.assert_array_equal(p.array(),[1,.5,2**-23])
        np.testing.assert_array_equal(factors_from_reduced_sum(0,layout,PriorFactors(1,2,3)).array(),[2**-23]*3)

    def test_lhs_single_factor_intervention_only_changes_degree_and_diagonal(self):
        layout=SystemLayout(7,14,2);ids=np.arange(14)
        a=lhs_updates(layout,ids,PriorFactors(2,3,5),[1,10,100,7,11,13])
        b=lhs_updates(layout,ids,PriorFactors(2,3,6),[1,10,100,7,11,13])
        np.testing.assert_array_equal(a.additions,[2,30,30,30,500,500,500,14,33,33,33,65,65,65])
        out=a.apply(np.zeros(14*99,dtype='f4'))
        self.assertEqual(np.count_nonzero(out),14)
        self.assertTrue(np.all(a.offsets % 99 == 0))
        np.testing.assert_array_equal(np.flatnonzero(a.additions!=b.additions),[4,5,6,11,12,13])
        self.assertFalse(a.native_gpu_verified)

    def test_rhs_preserves_flat_matrix_orientation_and_constant_linear_split(self):
        layout=SystemLayout(7,14,2);ids=np.arange(24);matrix=np.arange(1,13,dtype='f4')
        a=rhs_updates(layout,ids,PriorFactors(2,3,999),[5,7,11,13,17,19],matrix)
        np.testing.assert_array_equal(a.offsets,np.r_[np.arange(12),np.arange(21,33)])
        np.testing.assert_array_equal(a.additions[:3],[10,20,30])
        np.testing.assert_array_equal(a.additions[3:12],matrix[3:]*21)
        np.testing.assert_array_equal(a.additions[12:15],[26,52,78])
        # Quadratic regularization cannot alter the first 12 RHS prior slots.
        b=rhs_updates(layout,ids,PriorFactors(2,3,0),[5,7,11,13,17,19],matrix)
        np.testing.assert_array_equal(a.additions,b.additions)

    def test_prior_factors_and_plane_scales_have_a_synthetic_scale_ambiguity(self):
        layout=SystemLayout(10,20,1);ids=np.arange(20)
        a=lhs_updates(layout,ids,PriorFactors(1,2,3),[2,4,6])
        b=lhs_updates(layout,ids,PriorFactors(2,4,6),[1,2,3])
        np.testing.assert_array_equal(a.additions,b.additions)

    def test_rejects_unsupported_or_ambiguous_buffers_without_claiming_apple_guard(self):
        with self.assertRaises(ValueError):SystemLayout(6,10,1)
        layout=SystemLayout(4,4,1);f=PriorFactors(1,2,3)
        for ids in [[0,0],[-1],[65536],[1.25]]:
            with self.assertRaises(ValueError):lhs_updates(layout,ids,f,[1,1,1])
        with self.assertRaises(ValueError):lhs_updates(layout,[1],f,[1,1,float('nan')])
        with self.assertRaises(ValueError):lhs_updates(layout,[1],f,[1,1,1]).apply([0])


if __name__ == '__main__':unittest.main()
