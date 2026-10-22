import unittest
from types import SimpleNamespace
import numpy as np
from leaf_numeric import V,DomainUnknown,hc
from pixel_transfer import forward as transfer
from pixel_output import Parameters,forward,from_post_chain


class OutputTests(unittest.TestCase):
    def test_raw_transfer_fallback_and_actual_undefined_branch(self):
        np.testing.assert_array_equal(transfer(V.value([.2,-.4,.8]),99,to_linear=True).lo,[0,0,0])
        with self.assertRaises(DomainUnknown):transfer(V.value([.2,.4,.8]),8,to_linear=True)
        eps=hc('1800');np.testing.assert_array_equal(transfer(V.value([eps,0,-eps]),8,to_linear=True).lo,[eps,0,-eps])
        with self.assertRaises(TypeError):transfer(V.value([0,0,0]),True,to_linear=True)

    def test_negative_log_input_branch_and_log_domain(self):
        expected=hc('ab38');v=transfer(V.value([-.1,-.01,0]),7,to_linear=True);np.testing.assert_array_equal(v.lo,[expected]*3)
        with self.assertRaises(DomainUnknown):V.bounds(-.1,.1).log()

    def test_output_matrix_has_no_implicit_clamp(self):
        p=Parameters(V.value(.5),V.value(.4,'f'),V.value(np.diag([2,1,-1]),'f'),6,0);r=forward(V.value([.2,.4,.8]),p)
        self.assertLess(r.output600.lo[2],-1);self.assertEqual(float(r.gain577.lo),2)
        with self.assertRaises(DomainUnknown):forward(V.value([.2,.4,.8]),Parameters(V.value(0),p.parameter2,p.output_CCM_columns,6,0))

    def test_output_connection_requires_whole_sets_and_preserves_decisions(self):
        a=V.bounds([.2,.4,.8],[.21,.41,.81]);p=Parameters(V.bounds(1,1),V.bounds(.4,.4,'f'),V.bounds(np.eye(3),np.eye(3),'f'),3,0);chain=SimpleNamespace(output567=a,input_branch_decisions=('unresolved boundary',));r,d=from_post_chain(chain,p)
        self.assertFalse(r.output600.point);self.assertEqual(d,chain.input_branch_decisions)
        chain.output567=V.value([.2,.4,.8])
        with self.assertRaises(TypeError):from_post_chain(chain,p)


if __name__=='__main__':unittest.main()
