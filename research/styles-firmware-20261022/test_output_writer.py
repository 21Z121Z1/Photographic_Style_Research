import unittest
import numpy as np
from leaf_numeric import V,DomainUnknown
from texture_numeric import Texture,PixelFormat
from output_writer import Controls,forward,from_output_grid
from native_output_writer_check import fixtures


class WriterTests(unittest.TestCase):
    def test_clip_mask_alpha_and_no_implicit_clamp(self):
        _,c,rgb,frame=list(fixtures())[2];r=forward(Texture(V.value(frame),PixelFormat.RGBA16Float,'target'),V.value(rgb),c)
        self.assertEqual(r.copy_extent614,(2,1));self.assertEqual(int(r.written_pixels.sum()),2);np.testing.assert_array_equal(r.output.pixels.lo[2,3],[-.25,.5,2,1]);self.assertEqual(float(r.output.pixels.lo[0,0,0]),-.75)

    def test_zero_extent_unsigned_underflow_and_destination_wrap(self):
        cases=list(fixtures())
        for index,count,dest in [(3,0,(3,2)),(4,6,(3,2)),(6,6,(1,1))]:
            _,c,rgb,frame=cases[index];r=forward(Texture(V.value(frame),PixelFormat.RGBA16Float,'target'),V.value(rgb),c);self.assertEqual(int(r.written_pixels.sum()),count);self.assertEqual(r.leader_destination27,dest)

    def test_whole_rgb_box_is_written_without_center_and_alpha_is_exact(self):
        _,c,rgb,frame=next(fixtures());r=forward(Texture(V.bounds(frame,frame),PixelFormat.RGBA16Float,'target'),V.bounds(rgb-.01,rgb+.01),c);mask=r.written_pixels
        self.assertTrue(np.all(r.output.pixels.lo[mask,:3]<r.output.pixels.hi[mask,:3]));np.testing.assert_array_equal(r.output.pixels.lo[mask,3],1);np.testing.assert_array_equal(r.output.pixels.hi[mask,3],1)

    def test_unsupported_address_and_wrong_control_types_fail_closed(self):
        _,c,rgb,frame=next(fixtures())
        with self.assertRaises(TypeError):Controls((1.,1),(2,1),(8,6),False)
        with self.assertRaises(DomainUnknown):forward(Texture(V.value(frame),PixelFormat.RGBA16Float,'target'),V.value(rgb),Controls((20,20),(0,0),(30,30),False))

    def test_output600_interface_preserves_whole_boxes_and_branch_labels(self):
        from pixel_output import Parameters,forward as output
        p=Parameters(V.bounds(1,1),V.bounds(.4,.4,'f'),V.bounds(np.eye(3),np.eye(3),'f'),3,0);up=output(V.bounds([.2,.4,.8],[.21,.41,.81]),p);frame=Texture(V.bounds(np.zeros((2,2,4)),np.zeros((2,2,4))),PixelFormat.RGBA16Float,'output storage');r,decisions=from_output_grid(frame,[[up]],Controls((0,0),(0,0),(2,2),False),input_branch_decisions=('upstream boundary unresolved',))
        self.assertFalse(r.output.pixels.point);self.assertTrue(np.all(r.output.pixels.lo[0,0,:3]<r.output.pixels.hi[0,0,:3]));self.assertEqual(decisions,('upstream boundary unresolved',))


if __name__=='__main__':unittest.main()
