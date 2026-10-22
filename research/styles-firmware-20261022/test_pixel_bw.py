import unittest
import numpy as np
from leaf_numeric import V
from pixel_bw import Parameters,forward
from computed_bw_outer import forward as complete
from semantic_tone import Curve1D


class BWTests(unittest.TestCase):
    def curve(self):return Curve1D(tuple(np.linspace(0,1,17)**.8),'explicit synthetic whites')
    def parameters(self,code,point):
        f=lambda x:V.value(x,'f')if point else V.bounds(x,x,'f')
        return Parameters(f(.3),f(.4),f(.3),code,5)

    def test_unselected_internal_unknown_is_visible_without_false_output_unknown(self):
        r=forward(V.value([0,0,0]),V.value(.1),V.value(.2),self.parameters(0,True),self.curve())
        self.assertIsNotNone(r.output477);self.assertIsNone(r.tonal67);self.assertIn('tonal67',r.unknowns)

    def test_selected_black_tonal_remains_unknown(self):
        r=forward(V.value([0,0,0]),V.value(.1),V.value(.2),self.parameters(15,True),self.curve())
        self.assertIsNone(r.output477);self.assertFalse(r.full_camera_pipeline_verified)

    def test_complete_graph_computes_bw_without_oracle_and_preserves_decisions(self):
        h=lambda x:V.bounds(x,x);f=lambda x:V.bounds(x,x,'f');marker=('pow-boundary-unresolved',)
        r=complete(h([.2,.4,.8]),h([.3,.5,.7]),h(.8),h(.8),f(.25),f(.75),parameters=self.parameters(4,False),raw_cast_type245=2,whites=self.curve(),input_branch_decisions=marker)
        self.assertIsNotNone(r.bw.output477);self.assertIsNotNone(r.output492);self.assertFalse(r.BW_output_supplied_externally);self.assertEqual(r.input_branch_decisions,marker)
        with self.assertRaises(TypeError):complete(h([.2,.4,.8]),h([.3,.5,.7]),h(.8),h(.8),f(.25),f(.75),parameters=self.parameters(4,False),raw_cast_type245=2,whites=self.curve(),bw477=h([0,0,0]))

    def test_tuning_failure_witness_retains_distinct_internal_results(self):
        import json
        from pathlib import Path
        w=json.loads((Path(__file__).parent/'evidence/tuning-failure-witness-s12a.json').read_text())
        self.assertNotEqual(w['failed_tonal468'],w['correct_tonal468'])
        with self.assertRaises(TypeError):Parameters(V.value(.3),V.value(.4),V.value(.3),4,5)


if __name__=='__main__':unittest.main()
