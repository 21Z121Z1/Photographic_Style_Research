import unittest
import numpy as np
from leaf_numeric import V,DomainUnknown
from pixel_selective import SelectiveTexture
from native_selective_check import texture,cases,model
from cast_chain import forward as cast_chain
from post_skin_branches import Result


class SelectiveTests(unittest.TestCase):
    def test_rgba_row_channels_and_exact_declared_shape(self):
        a=np.zeros((4,360,4),dtype='f2')
        for i in range(4):a[i]=[i*.1,i*.2,i*.3,i*.4]
        t=SelectiveTexture(a,'synthetic exact rows');q=t.sample_row(V.value(.5,'f'),2)
        np.testing.assert_array_equal(q.lo,a[2,0].astype('f8'))
        with self.assertRaises(ValueError):SelectiveTexture(np.zeros((3,360,4)),'wrong shape')

    def test_nonmonotonic_texture_range_covers_interior_samples(self):
        t=texture();a=t.sample_row(V.bounds(.2,.25,'f'),1)
        for u in np.linspace(.2,.25,9):
            p=t.sample_row(V.value(u,'f'),1);self.assertTrue(np.all(p.lo>=a.lo)and np.all(p.lo<=a.hi))

    def test_nonzero_texture_changes_color_without_offset_flags(self):
        data=next(cases());active=model(data,texture(),True);zero=model(data,SelectiveTexture(np.zeros((4,360,4)),'explicit zero coefficient texture'),True)
        self.assertGreater(np.max(abs(active.lo-zero.lo)),.001)

    def test_black_remains_unknown_instead_of_mask_or_center_fallback(self):
        data=next(cases());data[:3]=0
        with self.assertRaises(DomainUnknown):model(data,texture(),False)

    def test_unknown_upstream_is_preserved_before_any_cast_leaf(self):
        prior=Result(None,None,None,None,{'skin393':'unknown'},())
        r=cast_chain(prior,cast=None,person=None,skin=None,sky=None,output_mix=None,enabled_neutralizing=True,use_skin=True,stats=None,texture=texture())
        self.assertEqual(r.unknown_operator,'upstream404');self.assertIsNone(r.output413);self.assertFalse(r.full_camera_pipeline_verified)


if __name__=='__main__':unittest.main()
