import unittest
import numpy as np
from leaf_numeric import V
from pixel_bright import BrightStats,forward
from native_bright_check import cases,model
from post_skin_branches import Inputs,forward as fork
from test_bgfg_tone import packet


class BrightTests(unittest.TestCase):
    def test_raw_stats_require_typed_scalars_and_matching_backends(self):
        with self.assertRaises(TypeError):BrightStats(*[.3]*5)
        with self.assertRaises(TypeError):BrightStats(*[V.value(.3,'f')]*4,V.bounds(.4,.4,'f'))

    def test_real_input_stats_change_fixed_point_output(self):
        data=next(cases());a=model(data,True);bdata=data.copy();bdata[9:14]=[.8,.1,.8,.8,.1];bdata[5]=8;b=model(bdata,True)
        self.assertGreater(np.max(abs(a.lo-b.lo)),.01)

    def test_known_bright_box_contains_its_point_without_claiming_tightness(self):
        data=next(cases());p=model(data,True);b=model(data,False)
        self.assertTrue(np.all(p.lo>=b.lo)and np.all(p.lo<=b.hi));self.assertGreater(np.max(b.hi-b.lo),.01)

    def test_fork_bright_uses_skin_and_keeps_highlight_on_separate_cast_branch(self):
        data=next(cases());h=lambda x:V.bounds(x,x)
        stats=BrightStats(*[V.bounds(x,x,'f')for x in data[9:14]])
        inputs=Inputs(h(data[:3]),h(data[6:9]),h(data[3]),h(data[4]),h(.1),h(data[5]),stats)
        a=fork(inputs,packet(),raw_cast_type245=2);b=fork(inputs,packet(),raw_cast_type245=16)
        np.testing.assert_array_equal(a.bright400.lo,b.bright400.lo)
        self.assertIs(a.neutralizing_input404,a.skin393);self.assertIs(b.neutralizing_input404,b.bright400)
        self.assertIs(b.highlight398,b.skin393);self.assertFalse(a.full_camera_pipeline_verified)
        with self.assertRaises(TypeError):Inputs(V.value(data[:3]),*[getattr(inputs,k)for k in ['working286','person96','skin95','guide350','exposure399','stats18']])


if __name__=='__main__':unittest.main()
