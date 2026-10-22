import importlib.util
from pathlib import Path
import unittest
import numpy as np
from leaf_numeric import V,DomainUnknown
from pixel_skin import forward,highlight_recover
from bgfg_tone import GATE


class SkinPrecisionTests(unittest.TestCase):
    def test_existing_continuous_algorithm_is_reused_with_explicit_precision_limit(self):
        path=Path(__file__).parent.parent/'semantic-styles/semantic_skin_model.py'
        spec=importlib.util.spec_from_file_location('legacy_skin_unchanged',path);old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
        rgb=[.7,.45,.3];point=forward(V.value(rgb),V.value(.8),V.value(.7),V.value(.2,'f'),V.value(.3,'f'))
        continuous=old.forward(rgb,.8,.7,.2,.3)
        self.assertLess(np.max(abs(point.lo-continuous)),.003)
        # This loose family regression does not certify either model as native.

    def test_skin_strict_f32_gate_keeps_equality_active_and_black_unknown(self):
        args=[V.value([0,0,0]),V.value(.8),V.value(.7)]
        below=np.nextafter(np.float32(GATE),np.float32(0))
        p=forward(*args,V.value(below,'f'),V.value(0,'f'));np.testing.assert_array_equal(p.lo,[0,0,0])
        with self.assertRaises(DomainUnknown):forward(*args,V.value(GATE,'f'),V.value(0,'f'))

    def test_known_skin_and_highlight_sets_cover_their_fixed_point_models(self):
        p=forward(V.value([.2,.4,.8]),V.value(.8),V.value(.7),V.value(.2,'f'),V.value(.3,'f'))
        b=forward(V.bounds([.2,.4,.8],[.2,.4,.8]),V.bounds(.8,.8),V.bounds(.7,.7),V.bounds(.2,.2,'f'),V.bounds(.3,.3,'f'))
        self.assertTrue(np.all(p.lo>=b.lo)and np.all(p.lo<=b.hi))
        p=highlight_recover(V.value([.2,.4,.8]),V.value(.7),V.value(2))
        b=highlight_recover(V.bounds([.2,.4,.8],[.2,.4,.8]),V.bounds(.7,.7),V.bounds(2,2))
        self.assertTrue(np.all(p.lo>=b.lo)and np.all(p.lo<=b.hi))

    def test_highlight_negative_working_domain_rejects_unproved_power(self):
        with self.assertRaises(DomainUnknown):highlight_recover(V.value([-1,-1,-1]),V.value(.4),V.value(2))


if __name__=='__main__':unittest.main()
