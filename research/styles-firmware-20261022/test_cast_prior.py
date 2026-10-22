import unittest
import numpy as np
from cast_prior import CastControls,CastTable,interpolate,convert_memory,fused_f32
from style_prior import SystemLayout,PriorFactors,rhs_updates


class CastPriorTests(unittest.TestCase):
    def table(self):
        t,c,i=np.meshgrid(np.arange(5),np.arange(5),np.arange(2),indexing='ij')
        v=(t*2+c*4+i*8)[...,None,None]+np.arange(12).reshape(3,4)/16
        return CastTable(v)

    def test_explicit_axis_layout_and_exact_dyadic_interpolation(self):
        r=interpolate(CastControls(-.75,-.25,.5),self.table())
        np.testing.assert_array_equal(r.memory_vectors,11+np.arange(12).reshape(3,4)/16)
        self.assertEqual(r.lower_indices,(0,1,0));self.assertEqual(r.fractions,(.5,.5,.5))
        np.testing.assert_array_equal(r.output_coefficients,r.memory_vectors.reshape(4,3).T)

    def test_clamp_corners_and_strength_zero_are_distinct_from_a_unique_inverse(self):
        table=self.table()
        a=interpolate(CastControls(1,1,1),table);b=interpolate(CastControls(8,9,2),table)
        np.testing.assert_array_equal(a.memory_vectors,table.values[4,4,1])
        np.testing.assert_array_equal(a.output_coefficients,b.output_coefficients)
        identity=np.c_[np.zeros(3),np.eye(3)]
        np.testing.assert_array_equal(interpolate(CastControls(.3,-.2,.7,0),table).output_coefficients,identity)

    def test_fallback_ignores_strength_and_monochrome_conversion_preserves_channel_average(self):
        for strength in [-2,0,3]:
            r=interpolate(CastControls(1,-1,.2,strength),None)
            np.testing.assert_array_equal(r.output_coefficients,np.c_[np.zeros(3),np.eye(3)])
        m=np.arange(12,dtype='f4').reshape(3,4)
        out=convert_memory(m,True)
        np.testing.assert_array_equal(out[0],out[1]);np.testing.assert_array_equal(out[0],out[2])
        np.testing.assert_allclose(out[0],np.arange(4)*3+1,rtol=2e-7)

    def test_fma_uses_one_rounding_in_signed_cancellation(self):
        a=np.float32(1+2**-23);b=np.float32(1-2**-23)
        self.assertEqual(fused_f32(a,b,-1),-2**-46)
        self.assertEqual(np.float32(np.float32(a*b)-1),0)

    def test_finite_model_domain_and_immutable_private_table(self):
        for x in [np.zeros((5,5,3,4)),np.full((5,5,2,3,4),np.nan),np.full((5,5,2,3,4),65)]:
            with self.assertRaises(ValueError):CastTable(x)
        for c in [CastControls(np.nan,0,0),CastControls(0,0,0,9)]:
            with self.assertRaises(ValueError):interpolate(c,self.table())
        with self.assertRaises(ValueError):self.table().values[0,0,0,0,0]=99

    def test_verified_enqueue_packing_connects_to_existing_rhs_operator(self):
        result=interpolate(CastControls(0,0,0,0),self.table())
        flat=result.shader_prior_matrix()
        np.testing.assert_array_equal(flat,[0,0,0,1,0,0,0,1,0,0,0,1])
        update=rhs_updates(SystemLayout(4,4,1),np.arange(12),PriorFactors(2,3,4),[1,1,1],flat)
        np.testing.assert_array_equal(update.additions,[0,0,0,3,0,0,0,3,0,0,0,3])


if __name__=='__main__':unittest.main()
