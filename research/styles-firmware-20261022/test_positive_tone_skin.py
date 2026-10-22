import unittest
import numpy as np
from positive_tone_skin import coefficients,forward


class PositiveToneSkinTests(unittest.TestCase):
    def test_boundaries_and_actual_nonmonotonic_theta9(self):
        self.assertEqual(coefficients(0).theta9,0)
        self.assertEqual(coefficients(1).theta9,-1)
        self.assertGreater(coefficients(.4).theta9,coefficients(.8).theta9)
        self.assertAlmostEqual(float(coefficients(1).theta10),-.5,places=7)
        for t in [-.01,1.01,float('nan')]:
            with self.assertRaises(ValueError):coefficients(t)

    def test_existing_conditional_skin_model_is_reused_with_explicit_context(self):
        rng=np.random.default_rng(27);x=rng.uniform(.02,1.2,size=(128,3)).astype('f4');guide=rng.uniform(.1,1,size=128).astype('f4')
        np.testing.assert_array_equal(forward(x,np.zeros(128),guide,tone=.6),x)
        np.testing.assert_array_equal(forward(x,np.ones(128),guide,tone=0),x)
        self.assertGreater(float(np.max(abs(forward(x,np.ones(128),guide,tone=.6)-x))),.01)
        self.assertFalse(coefficients(.6).native_GPU_verified)


if __name__=='__main__':unittest.main()
