import unittest
from dataclasses import replace
import numpy as np
from leaf_numeric import V,hc
from main_pre393 import mutate_semantic
from native_main_pre393_check import fixtures,model
from pre_skin_color import forward as color
from typed_bgfg import Fields,forward as bgfg


class Pre393Tests(unittest.TestCase):
    def test_cast2_zero_belongs_to_nonpositive_and_uncertain_sign_unions(self):
        from main_pre393 import Controls
        p=np.array([.6,.8,.9,1.1,.6,.3,.4],dtype='f4');c=Controls(2,0,*(V.value(v,'f')for v in [.7,0,0,.9,.8,-1,4]));zero=mutate_semantic(V.value(p,'f'),c);positive=mutate_semantic(V.value(p,'f'),replace(c,tone2=V.value(.1,'f')))
        self.assertLess(zero.lo[2],positive.lo[2]);self.assertEqual(positive.lo[2],float(p[2]))
        bounds=Controls(2,0,*(V.bounds(v,v,'f')for v in [.7,0,0,.9,.8,-1,4]));bounds=replace(bounds,tone2=V.bounds(-.1,.1,'f'));result=mutate_semantic(V.bounds(p,p,'f'),bounds)
        self.assertLessEqual(result.lo[2],zero.lo[2]);self.assertGreaterEqual(result.hi[2],positive.lo[2])

    def test_hint_invalid_divisor_fails_closed_and_black_leaf_stays_unknown(self):
        a=list(fixtures())[1];a['threshold']=np.float32(0);r=model(a,True);self.assertEqual(r.unknown_operator,'person/skin hint scaling');self.assertIn('zero',r.unknown_reason)
        black=model(list(fixtures())[-1],True);self.assertEqual(black.unknown_operator,'FG354');self.assertNotIn('output392',black.observations)

    def test_outer_color_keeps_actual_mask_and_internal_output(self):
        x=V.value([.2,.4,.8]);r=color(x,V.value(.5),V.value(0,'f'),V.value(4,'f'));self.assertEqual(float(r.person_mix389.lo),hc('3666'))
        a=color(x,V.value(0),V.value(.3,'f'),V.value(4,'f'));np.testing.assert_array_equal(a.output392.lo,a.saturated374.lo)
        b=color(x,V.value(.8),V.value(-.3,'f'),V.value(4,'f'));self.assertGreater(np.max(abs(a.saturated374.lo-b.saturated374.lo)),.01)

    def test_uncertain_helpers_cannot_enter_fixed_point_controller(self):
        f=list(fixtures())[0];p=Fields(V.bounds(f['bg'],f['bg'],'f'),V.bounds(f['fg'],f['fg'],'f'))
        with self.assertRaises(TypeError):bgfg('bg',V.value([.2,.4,.8]),V.value([.2,.4,.8]),p,guide=V.value(.4),person=V.value(.3),skin=V.value(.2),whites=None)


if __name__=='__main__':unittest.main()
