import unittest
import numpy as np
from test_semantic_tone import inputs
from test_bgfg_tone import packet
from tone_interface import evaluate,RendererControls,ResolvedSceneType
from test_tone_interface import frame
from tone_fragment_sets import forward


class FragmentSetTests(unittest.TestCase):
    def test_boundary_and_missing_operator_survive_composition(self):
        fields=evaluate(RendererControls(.5,float(np.float32(.5**(4/3))),0),ResolvedSceneType(0),frame())
        r=forward(inputs(),fields,cast_type=0,baseline_exposure=1,guide_texture8=.4,guide_texture9=.5,skin_weight=.2,texture6_present=False,texture7_present=True)
        self.assertEqual(r.status,'unknown_BG_operator');self.assertIsNone(r.output)
        self.assertTrue(any(b.state=='undetermined'for b in r.semantic.input_branches))
        self.assertEqual(r.bg.missing_operator,'whitesCurve_BG_mode0');self.assertIsNotNone(r.bg.missing_input_set)

    def test_neutral_controlled_fragment_emits_a_set_not_camera_certification(self):
        p=packet();v=p.values.copy();v[33:40]=[1,1,1,1,0,1,1]
        from tone_interface import ConsumerFields
        p=ConsumerFields(p.controls,p.branch,v,p.host_f32_absolute_allowance)
        r=forward(inputs(),p,cast_type=0,baseline_exposure=1,guide_texture8=.4,guide_texture9=.5,skin_weight=.2,texture6_present=False,texture7_present=False)
        self.assertEqual(r.status,'computed_fragment_set');self.assertTrue(np.all(r.output.lo<=r.output.hi));self.assertFalse(r.full_camera_pipeline_verified)

    def test_both_precomputed_textures_do_not_enter_the_fallback_helper_model(self):
        r=forward(inputs(),packet(),cast_type=0,baseline_exposure=1,guide_texture8=.4,guide_texture9=.5,skin_weight=.2,texture6_present=True,texture7_present=True)
        self.assertEqual(r.status,'unknown_precomputed_inputs');self.assertIsNone(r.semantic);self.assertIsNone(r.output)


if __name__=='__main__':unittest.main()
