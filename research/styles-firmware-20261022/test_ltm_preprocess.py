import unittest
import numpy as np
from leaf_numeric import V,DomainUnknown
from ltm_preprocess import Parameters,semantic_srl,forward
from ltm_gain import Parameters as GainParameters
from ltm_guided import forward as maps
from semantic_tone import Curve1D


class PreLTMTests(unittest.TestCase):
    def test_srl_strict_gates_and_black_preservation(self):
        rgb=V.value([.2,.4,.8]);matte=V.value(.3)
        for p in [-1,0,3]:self.assertIs(semantic_srl(rgb,V.value(p,'f'),matte),rgb)
        black=V.value([0,0,0]);self.assertIs(semantic_srl(black,V.value(.4,'f'),matte),black)
        self.assertGreater(np.max(abs(semantic_srl(rgb,V.value(.4,'f'),matte).lo-rgb.lo)),.05)

    def test_code6_black_is_model_domain_unknown(self):
        p=Parameters(V.value(-1,'f'),V.value(np.eye(3),'f'),6,False,False)
        with self.assertRaises(DomainUnknown):forward(V.value([0,0,0]),V.value(.3),p)

    def test_whole_maps_flow_to_both_guided_inputs(self):
        primary=np.full((2,3,3),.5);linear=np.full((2,3,3),.3);matte=V.bounds(np.full((2,3),.3),np.full((2,3),.3));pre=Parameters(V.bounds(-1,-1,'f'),V.bounds(np.eye(3),np.eye(3),'f'),0,False,False);gp=GainParameters(V.bounds(np.eye(3),np.eye(3),'f'),V.bounds(1,1,'f'),V.bounds([.6,.8,.7,1.2,.6,.3,.4],[.6,.8,.8,1.3,.6,.3,.4],'f'));guide=V.bounds(np.full((2,3,3),.4),np.full((2,3,3),.4));curve=Curve1D(tuple(np.linspace(0,1,17)),'supplied')
        r=maps(V.bounds(primary,primary),V.bounds(linear,linear),matte,guide,pre_parameters=pre,gain_parameters=gp,curve=curve,epsilon=V.bounds(.05,.05,'f'),output_shape=(2,3),working_domain='synthetic',input_branch_decisions=('pow boundary union',))
        self.assertEqual(r.unknowns,{});self.assertFalse(r.raw_bg.point);self.assertTrue(np.any(r.raw_bg.lo<r.raw_bg.hi));self.assertEqual(r.input_branch_decisions,('pow boundary union',))
        self.assertFalse(r.guided_bg['output'].point);self.assertFalse(r.guided_fg['output'].point);self.assertTrue(np.all(r.guided_fg['output'].hi>=r.guided_bg['output'].lo))


if __name__=='__main__':unittest.main()
