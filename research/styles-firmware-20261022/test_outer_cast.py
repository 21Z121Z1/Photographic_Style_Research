import unittest
import numpy as np
from leaf_numeric import V
from outer_cast import forward
from native_outer_cast_check import cases,result
from cast_chain import Result as CastResult
from outer_cast_chain import forward as extend
from post_skin_branches import Result as SkinResult


class OuterCastTests(unittest.TestCase):
    def test_cast_three_and_four_keep_distinct_bw_and_color_inputs(self):
        data=next(cases());data[12]=3;a=result(data,False);data[12]=4;b=result(data,False)
        self.assertIs(a.bw_input472,a.tonal468)
        np.testing.assert_array_equal(a.color476.lo,V.value(data[3:6]).lo)
        np.testing.assert_array_equal(b.bw_input472.lo,V.value(data[:3]).lo)
        self.assertIs(b.color476,b.bw_input472)

    def test_missing_bw_is_unknown_even_with_zero_blend_weight(self):
        h=lambda x:V.bounds(x,x);f=lambda x:V.bounds(x,x,'f')
        r=forward(h([.2,.4,.8]),h([.3,.5,.7]),h(.4),f(.3),f(.4),f(0),f(0),tuning_type415=5,raw_cast_type245=4,bw477=None)
        self.assertIsNone(r.output492);self.assertIn('BW477',r.unknowns);self.assertFalse(r.BW_algorithm_verified)

    def test_selected_cast_four_does_not_require_unselected_highlight(self):
        h=lambda x:V.bounds(x,x);f=lambda x:V.bounds(x,x,'f')
        r=forward(h([.2,.4,.8]),None,h(.4),f(.3),f(.4),f(.25),f(.75),tuning_type415=5,raw_cast_type245=4,bw477=h([.6,.3,.2]))
        self.assertIsNotNone(r.output492);self.assertFalse(r.full_camera_pipeline_verified)

    def test_upstream_unknown_and_decision_metadata_are_preserved(self):
        marker=('boundary-undetermined',);chain=CastResult(None,'warmth409',None,'domain unknown',marker)
        r=extend(chain,SkinResult(None,None,None,None,{},marker),None,None,None,None,None,tuning_type415=5,raw_cast_type245=4,bw477=None)
        self.assertEqual(r.input_branch_decisions,marker);self.assertEqual(r.upstream_unknown,'warmth409');self.assertIsNone(r.outer)


if __name__=='__main__':unittest.main()
