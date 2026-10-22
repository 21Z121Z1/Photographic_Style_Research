import unittest
from dataclasses import replace
import numpy as np
from precomputed_semantic import Texture2D,PrecomputedInputs,forward_half,forward_set
from tone_fragment_sets import forward
from test_bgfg_tone import packet
from tone_interface import ConsumerFields


def inputs():
    a=np.array([[[.5,.75,1],[1,1.25,1.5]],[[1.5,1,.5],[2,1.5,1]]])
    return PrecomputedInputs((0,0),Texture2D(a,'conditional gain RGB'),Texture2D(a[::-1].copy(),'conditional gain RGB'),(.5,.5,0,0),(.5,.5,0,0),(.25,.5,.75),.3)


class PrecomputedTests(unittest.TestCase):
    def test_normalized_texel_centers_edges_and_f32_roi_layout(self):
        inp=inputs();np.testing.assert_array_equal(inp.coordinates(),[[.25,.25],[.25,.25]])
        np.testing.assert_array_equal(inp.texture6.sample((.25,.25)),inp.texture6.values[0,0])
        np.testing.assert_array_equal(inp.texture6.sample((-1,2)),inp.texture6.values[-1,0])
        np.testing.assert_array_equal(inp.texture6.sample((.5,.5)),np.mean(inp.texture6.values.astype('f4'),axis=(0,1)).astype('f2'))

    def test_precomputed_branch_does_not_reapply_gtc_or_exposure_coefficients(self):
        inp=inputs();p=np.array([.6,.8,.5,1.5,.7,.5,.9]);a=forward_half(inp,p);p[2:5]=[2,3,0]
        np.testing.assert_array_equal(forward_half(inp,p),a)
        box=forward_set(inp,p,p);self.assertTrue(np.all(a>=box.lower)and np.all(a<=box.upper))

    def test_both_texture_branch_removes_unknown_when_inputs_are_supplied(self):
        p=packet();v=p.values.copy();v[33:40]=[1,1,1,1,0,1,1];p=ConsumerFields(p.controls,p.branch,v,p.host_f32_absolute_allowance)
        r=forward(inputs(),p,cast_type=0,baseline_exposure=1,guide_texture8=.4,guide_texture9=.5,skin_weight=.2,texture6_present=True,texture7_present=True)
        self.assertEqual(r.status,'computed_fragment_set');self.assertIsNotNone(r.output);self.assertFalse(r.full_camera_pipeline_verified)

    def test_wrong_domains_shapes_and_missing_branch_inputs_do_not_guess(self):
        with self.assertRaises(ValueError):Texture2D(np.zeros((2,2,4)),'x')
        with self.assertRaises(ValueError):replace(inputs(),roi_field5=(np.nan,0,0,0)).validate()
        with self.assertRaises(ValueError):replace(inputs(),grid=(-1,0)).validate()
        with self.assertRaises(ValueError):forward(inputs(),packet(),cast_type=0,baseline_exposure=1,guide_texture8=.4,guide_texture9=.5,skin_weight=.2,texture6_present=False,texture7_present=True)


if __name__=='__main__':unittest.main()
