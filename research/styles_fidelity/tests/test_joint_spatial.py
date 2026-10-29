import unittest
import numpy as np

from research.styles_fidelity.joint_spatial import footprint, spatial, display_projection


class JointSpatialTests(unittest.TestCase):
    def test_eight_connected_components_and_exclusive_box(self):
        mask = np.zeros((6,8),dtype=bool)
        mask[1,2] = mask[2,3] = mask[3,4] = True
        mask[5,7] = True
        result = footprint(mask)
        self.assertEqual(result['pixels'],4)
        self.assertEqual(result['components_8_connected'],2)
        self.assertEqual(result['largest_component_pixels'],3)
        self.assertEqual(result['largest_component_box_xyxy'],[2,1,5,4])

    def test_bridge_merges_components_without_double_counting(self):
        mask = np.array([[1,0,0,0,1],[1,1,1,1,1]],dtype=bool)
        result = footprint(mask)
        self.assertEqual(result['components_8_connected'],1)
        self.assertEqual(result['largest_component_pixels'],7)
        self.assertEqual(footprint(np.zeros((2,3),bool))['largest_component_box_xyxy'],None)
        self.assertEqual(footprint(np.ones((2,3),bool))['largest_component_pixels'],6)

    def test_change_is_distinct_from_regression(self):
        reference = np.zeros((2,2,3))
        old = np.zeros_like(reference);new = old.copy()
        old[0,0] = .1;new[0,0] = .02  # large change, improvement
        new[1,1] = .03  # regression
        result = spatial(reference,old,new)['thresholds']['0.01']
        self.assertEqual(result['changed']['pixels'],2)
        self.assertEqual(result['worse']['pixels'],1)
        self.assertEqual(result['better']['pixels'],1)
        self.assertEqual(result['worse']['area_pct'],25.)

    def test_shared_projection_and_identity(self):
        x = np.array([[[0.,1.,2.]]])
        y = display_projection(x,2.)
        self.assertEqual(y[0,0,0],0.)
        self.assertAlmostEqual(y[0,0,2],1.)
        self.assertGreater(y[0,0,1],.5)
        self.assertEqual(spatial(y,y,y)['thresholds']['0.01']['changed']['pixels'],0)

    def test_geometry_mismatch_cannot_produce_a_footprint(self):
        with self.assertRaises(ValueError):
            spatial(np.zeros((2,2,3)),np.zeros((2,3,3)),np.zeros((2,2,3)))
