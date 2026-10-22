import unittest
import numpy as np
from leaf_numeric import V
from pixel_haze import Parameters,forward,select_video


class HazeTests(unittest.TestCase):
    def test_original_guide211_changes_active_local_branch(self):
        p=Parameters(V.value([.05,.8,.6,.1,-.1,.5,.1,.1],'f'),True);rgb=V.value([.2,.4,.8]);person=V.value(.2)
        a=forward(rgb,V.value(.1),person,p);b=forward(rgb,V.value(.8),person,p)
        self.assertGreater(np.max(abs(a.lo-b.lo)),.005)

    def test_tuning_and_enable_select_do_not_hide_internal_unknown(self):
        p=Parameters(V.value([.05,0,.6,.1,-.1,.5,.1,.1],'f'),True);rgb=V.value([.2,.4,.8])
        a=select_video(rgb,V.value(.4),V.value(.5),p,tuning_type17=2);b=select_video(rgb,V.value(.4),V.value(.5),p,tuning_type17=7)
        self.assertIs(a.output501,rgb);self.assertIsNone(a.haze493);self.assertIsNotNone(a.unknown_reason);self.assertIsNone(b.output501)
        disabled=Parameters(p.fields1_8,False);c=select_video(rgb,V.value(.4),V.value(.5),disabled,tuning_type17=7);self.assertIs(c.output501,rgb)

    def test_matching_haze_set_covers_fixed_point_and_requires_raw_parameters(self):
        values=[.05,.8,.6,.1,-.1,.5,.1,.1];p=forward(V.value([.2,.4,.8]),V.value(.1),V.value(.2),Parameters(V.value(values,'f'),True));b=forward(V.bounds([.2,.4,.8],[.2,.4,.8]),V.bounds(.1,.1),V.bounds(.2,.2),Parameters(V.bounds(values,values,'f'),True))
        self.assertTrue(np.all(p.lo>=b.lo)and np.all(p.lo<=b.hi))
        with self.assertRaises(TypeError):Parameters(V.value(values),True)


if __name__=='__main__':unittest.main()
