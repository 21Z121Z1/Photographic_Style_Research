import unittest
import numpy as np
from tone_interface import ConsumerFields,ScaledControls,ResolvedSceneType
from tone_boundaries import decide
from semantic_tone import I
from bgfg_tone import run,mids_half,PixelContext,GATE


def packet():
    v=np.zeros(40);v[11]=v[8]=1;v[17+5]=1
    return ConsumerFields(ScaledControls(np.float32(.5),np.float32(.3),np.float32(0),ResolvedSceneType(4)),'synthetic_control',v,np.zeros(40))


class BgFgTests(unittest.TestCase):
    def test_bg_and_fg_mids_have_separate_order_and_preserve_sets(self):
        p=packet();v=p.values.copy();v[7]=.3;v[19]=.2
        p=ConsumerFields(p.controls,p.branch,v,p.host_f32_absolute_allowance)
        rgb=I.point(np.array([.2,.4,.8]));context=PixelContext(.4,1,.2)
        for block,amount in [('bg',.3),('fg',.2)]:
            r=run(block,rgb,p,context,semantic_rgb=rgb)
            self.assertEqual(r.status,'computed_set');point=mids_half(rgb.lo,amount)
            self.assertTrue(np.all(point>=r.output.lo)and np.all(point<=r.output.hi))
            self.assertFalse(r.full_helper_numeric_verified)

    def test_missing_leaf_returns_unknown_not_identity_or_center(self):
        p=packet();v=p.values.copy();v[1]=.4;v[21]=.4;p=ConsumerFields(p.controls,p.branch,v,p.host_f32_absolute_allowance)
        for block,missing in [('bg','contrastFilter'),('fg','whitesCurve_FG_mode1')]:
            r=run(block,I.point([.2,.4,.8]),p,PixelContext(.4,.5),semantic_rgb=I.point([.2,.4,.8]))
            self.assertEqual(r.status,'unknown_operator');self.assertEqual(r.missing_operator,missing);self.assertIsNone(r.output)

    def test_undetermined_producer_and_gate_branch_not_discarded(self):
        p=packet();v=p.values.copy();v[19]=.175;e=p.host_f32_absolute_allowance.copy();e[19]=.075
        b=decide('FG.r_mids','olt',.49999997,.50000006,.5,[19]);p=ConsumerFields(p.controls,p.branch,v,e,branch_decisions=(b,))
        r=run('fg',I.point([.2,.4,.8]),p,PixelContext(.4,1),semantic_rgb=I.point([.2,.4,.8]))
        self.assertEqual(r.input_branches[0].state,'undetermined');self.assertGreater(float(np.max(r.output.hi-r.output.lo)),.01)


if __name__=='__main__':unittest.main()
