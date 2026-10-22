import unittest
import numpy as np
from bgfg_fixed import ExactHelperFields,forward
from native_bgfg_complete_check import packet,BG_POS
from native_bgfg_coupled_check import coupled_cases
from all_pixel_leaves import models
from bgfg_tone import run,PixelContext
from leaf_numeric import V
from semantic_tone import I,Curve1D


class FixedHelperTests(unittest.TestCase):
    def test_exact_fields_cannot_silently_accept_uncertain_producer_or_double(self):
        p=packet('bg',BG_POS)
        with self.assertRaises(TypeError):ExactHelperFields('bg',p,'uncertain producer')
        with self.assertRaises(TypeError):ExactHelperFields('bg',np.zeros(17,dtype='f8'),'wrong type')
        with self.assertRaises(ValueError):ExactHelperFields('bg',np.zeros(17,dtype='f4'),'')
        a=np.zeros(17,dtype='f4');f=ExactHelperFields('bg',a,'explicit synthetic');a[0]=1
        self.assertEqual(f.values[0],0)
        with self.assertRaises(ValueError):f.values[0]=2

    def test_point_entry_rejects_box_even_when_it_has_a_center(self):
        f=ExactHelperFields('bg',np.zeros(17,dtype='f4'),'explicit synthetic')
        with self.assertRaises(TypeError):forward(V.bounds([.2,.4,.8],[.2,.4,.8]),V.value([.3,.5,.7]),f,guide=V.value(.4),person=V.value(.5),skin=V.value(.3),whites=None)

    def test_multi_leaf_unknown_is_retained_and_never_replaced_by_fixed_result(self):
        p=packet('bg',BG_POS);r=run('bg',I.point([.2,.4,.8]),p,PixelContext(.4,.5,.3),leaf_models=models(Curve1D(tuple(np.linspace(0,1,17)**.8),'test')))
        self.assertEqual(r.status,'unknown_operator');self.assertIn('domain unknown:',r.missing_operator);self.assertIsNone(r.output)
        with self.assertRaises(TypeError):forward(V.value([.2,.4,.8]),V.value([.3,.5,.7]),p,guide=V.value(.4),person=V.value(.5),skin=V.value(.3),whites=None)

    def test_coupled_models_keep_sets_through_complete_controller(self):
        curve=Curve1D(tuple(np.linspace(0,1,17)**.8),'test')
        for block in ['bg','fg']:
            for _,p,data in coupled_cases(block):
                start=0 if block=='bg'else 17;n=17 if block=='bg'else 16
                f=ExactHelperFields(block,p.values[start:start+n].astype('f4'),'explicit synthetic')
                q=forward(V.value(data[:3]),V.value(data[6:9]),f,guide=V.value(data[3]),person=V.value(data[4]),skin=V.value(data[5]),whites=curve)
                r=run(block,I.point(data[:3]),p,PixelContext(*map(float,data[3:6])),semantic_rgb=I.point(data[6:9]),leaf_models=models(curve))
                self.assertEqual(r.status,'computed_set');self.assertTrue(np.all(q.lo>=r.output.lo)and np.all(q.lo<=r.output.hi));self.assertFalse(r.full_helper_numeric_verified)


if __name__=='__main__':unittest.main()
