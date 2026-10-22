import unittest
from types import SimpleNamespace
import numpy as np
from leaf_numeric import V,DomainUnknown
from cast_values import CastValues
from pixel_neutral_root import NeutralStats
from pixel_channel_mix import forward as channel
from pixel_postprotect import forward as protect
from pixel_haze import Parameters as Haze
from pixel_post_chain import forward as chain


class PostTests(unittest.TestCase):
    def test_channel_default_and_black_cast15(self):
        rgb=V.value([0,0,0]);person=V.value(1);stats=NeutralStats(*(V.value(.4,'f')for _ in range(3)))
        self.assertIs(channel(rgb,person,cast_type0=0,tone17_19=None,stats=None),rgb)
        with self.assertRaises(DomainUnknown):channel(rgb,person,cast_type0=15,tone17_19=None,stats=stats)
        with self.assertRaises(TypeError):channel(rgb,person,cast_type0=True,tone17_19=None,stats=stats)
        with self.assertRaises(TypeError):channel(rgb,person,cast_type0=4,tone17_19=V.value([.3,.6,.1]),stats=stats)

    def test_raw_f32_threshold_and_texture_presence(self):
        rgb=V.value([.2,.4,.8]);color=V.value([.8,.2,.1]);raw=np.zeros(34,dtype='f4');raw[31]=np.nextafter(np.float32(.01),np.float32(0))
        self.assertIs(protect(rgb,color,CastValues(V.value(raw,'f')),None,texture10_present=True),rgb)
        raw[31]=np.float32(.01)
        with self.assertRaises(DomainUnknown):protect(rgb,color,CastValues(V.value(raw,'f')),None,texture10_present=True)
        self.assertIs(protect(rgb,color,CastValues(V.value(raw,'f')),None,texture10_present=False),rgb)
        raw[31]=-.4
        self.assertIs(protect(rgb,color,CastValues(V.value(raw,'f')),None,texture10_present=True),rgb)

    def test_boundary_set_cannot_fall_back_to_center(self):
        rgb=V.bounds([.2,.4,.8],[.2,.4,.8]);color=V.bounds([.8,.2,.1],[.8,.2,.1]);lo=np.zeros(34);hi=np.zeros(34);lo[31]=.009;hi[31]=.011
        with self.assertRaises(DomainUnknown):protect(rgb,color,CastValues(V.bounds(lo,hi,'f')),None,texture10_present=True)

    def test_post_chain_preserves_sets_and_unselected_haze_unknown(self):
        rgb=V.bounds([.2,.4,.8],[.21,.41,.81]);raw=CastValues(V.bounds(np.zeros(34),np.zeros(34),'f'));haze=Haze(V.bounds([.05,0,.6,.1,-.1,.5,.1,.1],[.05,0,.6,.1,-.1,.5,.1,.1],'f'),True)
        upstream=SimpleNamespace(output492=rgb,outer=SimpleNamespace(color476=rgb),input_branch_decisions=('pow boundary unresolved',))
        r=chain(upstream,V.bounds(.4,.4),V.bounds(.5,.5),haze=haze,tuning_type17=2,cast=raw,stats=None,texture10_present=False,cast_type0=0,tone17_19=None)
        self.assertIs(r.output567,rgb);self.assertFalse(r.output567.point);self.assertIsNotNone(r.haze_internal_unknown);self.assertEqual(r.input_branch_decisions,upstream.input_branch_decisions)


if __name__=='__main__':unittest.main()
