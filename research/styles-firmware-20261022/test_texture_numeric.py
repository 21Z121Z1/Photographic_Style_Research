import unittest
import numpy as np
from leaf_numeric import V
from texture_numeric import Texture,PixelFormat,producer_uv,sample_normalized,ROI,consume_block290


class TextureContractTests(unittest.TestCase):
    def test_producer_uses_destination_grid_not_source_size(self):
        uv=producer_uv((1,0),(2,3),point=True);np.testing.assert_array_equal(uv.lo,[.5,.25])
        data=np.zeros((4,6,4),dtype='f2');data[...,0]=np.arange(6);data[...,3]=1;t=Texture(V.value(data),PixelFormat.RGBA16Float,'synthetic')
        self.assertEqual(float(sample_normalized(t,uv).lo[0]),2.5)

    def test_format_and_uncertain_coordinate_hull_do_not_use_center(self):
        data=np.zeros((1,2,4));data[0,1,:3]=1;data[...,3]=1
        with self.assertRaises(TypeError):Texture(V.value(data),115,'synthetic')
        t=Texture(V.bounds(data,data),PixelFormat.RGBA16Float,'synthetic');v=sample_normalized(t,V.bounds([.24,.5],[.76,.5],'f'))
        self.assertLessEqual(v.lo[0],0);self.assertGreaterEqual(v.hi[0],1)

    def test_consumer_roi5_and_roi6_are_independent_logical_transforms(self):
        bg=np.array([[[.2,.2,.2,1],[.8,.8,.8,1]]]);fg=np.array([[[.1,.1,.1,1],[.9,.9,.9,1]]]);a=Texture(V.value(bg),PixelFormat.RGBA16Float,'gain');b=Texture(V.value(fg),PixelFormat.RGBA16Float,'gain');roi=ROI((0,0),V.value([0,0,.25,.5],'f'),V.value([0,0,.75,.5],'f'));p=V.value([0,0,1,1,0,0,0],'f')
        r=consume_block290(a,b,roi,V.value([1,1,1]),V.value(0),p);s=consume_block290(a,b,roi,V.value([1,1,1]),V.value(1),p)
        np.testing.assert_array_equal(r['sample305'].lo,np.array([.2]*3,dtype='f2'));np.testing.assert_array_equal(s['sample308'].lo,np.array([.9]*3,dtype='f2'))
        # Original half mix is a+half(half(b-a)*w). Even at w=1 the two
        # intermediate roundings can differ from b; retain that actual order.
        np.testing.assert_array_equal(r['output335'].lo,np.array([.2]*3,dtype='f2'));np.testing.assert_array_equal(s['output335'].lo,[.900390625]*3)


if __name__=='__main__':unittest.main()
