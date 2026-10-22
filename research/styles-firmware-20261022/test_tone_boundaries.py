import unittest
import numpy as np
from tone_boundaries import decide,positive_decisions
from test_tone_interface import frame
from tone_interface import evaluate,RendererControls,ResolvedSceneType


class BoundaryContractTests(unittest.TestCase):
    def test_actual_f32_comparison_and_equality_ownership(self):
        for predicate,states in [('olt',['true','false','false']),('ugt',['false','false','true']),('ole',['true','true','false']),('oge',['false','true','true'])]:
            values=[np.nextafter(np.float32(.5),np.float32(0)),np.float32(.5),np.nextafter(np.float32(.5),np.float32(1))]
            self.assertEqual([decide('test',predicate,x,x,.5,[19]).state for x in values],states)

    def test_pow_boundary_is_set_coverage_not_center_agreement(self):
        edge=np.float32(.5**(4/3))
        for t in [np.nextafter(edge,np.float32(0)),edge,np.nextafter(edge,np.float32(1))]:
            r=evaluate(RendererControls(.5,float(t),0),ResolvedSceneType(0),frame())
            self.assertFalse(r.branch_determined)
            self.assertLess(r.output_lower[19],.101);self.assertGreater(r.output_upper[19],.249)
            with self.assertRaises(ValueError):r.ssr_block_f32()
            self.assertEqual(len(r.ssr_block_f32(allow_approximation=True)),160)
            self.assertFalse(r.named_fields()['fg.mids']['branch_determined'])

    def test_stable_branch_and_zero_are_determined_and_gap_rejected(self):
        for t in [0.,.1,.8]:self.assertTrue(all(b.state!='undetermined'for b in positive_decisions(t)))
        with self.assertRaises(ValueError):evaluate(RendererControls(.5,-2**-25,0),ResolvedSceneType(0),frame())


if __name__=='__main__':unittest.main()
