"""Meaningful diagnostics tests: alignment, masking, exact effect and input domains."""
import unittest
import json
from pathlib import Path
import tempfile
from dataclasses import replace
import numpy as np
from image_chain_metrics import compare_rgb
from synthetic_inputs import Pattern,MaskPattern,SyntheticSpec,rgb_pattern,semantic_masks,make_context


class DiagnosticMetricsTests(unittest.TestCase):
    def test_rmse_and_mask_exclude_unwritten_border_and_alpha(self):
        a=np.zeros((2,3,4),dtype='f2');b=a.copy();a[0,0,:3]=[1,2,3]
        a[1,2]=[8,8,8,8];a[0,1,3]=99
        mask=np.zeros((2,3),dtype=bool);mask[0,0]=True;mask[0,1]=True
        m=compare_rgb(a,b,pixel_mask=mask,threshold=1.5)
        self.assertEqual(m.components,6);self.assertEqual(m.pixels,2)
        self.assertEqual(m.max_absolute_error,3);self.assertAlmostEqual(m.rmse,np.sqrt(14/6))
        self.assertEqual(m.half_bit_mismatches,3);self.assertEqual(m.exceedance_components,2)
        self.assertEqual(sum(row['count']for row in m.histogram),6)
        self.assertEqual(m.exceedance_examples[0]['channel'],1)

    def test_reject_shape_nonfinite_empty_and_integer_masks(self):
        a=np.zeros((2,3,3),dtype='f2')
        with self.assertRaises(TypeError):compare_rgb(a,np.zeros((3,2,3)))
        with self.assertRaises(TypeError):compare_rgb(a,a,pixel_mask=np.zeros((2,3),dtype=bool))
        with self.assertRaises(TypeError):compare_rgb(a,a,pixel_mask=np.ones((2,3),dtype='u1'))
        for invalid in (np.inf,-np.inf,np.nan):
            b=a.copy();b[0,0,0]=invalid
            with self.assertRaises(ValueError):compare_rgb(b,a)
        with self.assertRaises(ValueError):compare_rgb(a,a,threshold=np.nan)
        with self.assertRaises(ValueError):compare_rgb(np.full((2,3,3),1e10),a)

    def test_half_bits_distinguish_signed_zero_without_inventing_numeric_error(self):
        a=np.zeros((1,1,3),dtype='f2');b=a.copy();b[0,0,0]=-0.
        m=compare_rgb(a,b)
        self.assertEqual(m.max_absolute_error,0);self.assertEqual(m.half_bit_mismatches,1)


class SyntheticInputsTests(unittest.TestCase):
    def test_all_scene_sources_masks_and_roi_have_explicit_finite_storage(self):
        fingerprints=set()
        for pattern in Pattern:
            spec=SyntheticSpec(pattern)
            c=make_context(spec)
            self.assertEqual(c.images[0].shape,(8,12,4));self.assertEqual(c.output_initial.shape,(10,14,4))
            self.assertEqual(c.producer_shape,(4,6));self.assertEqual(c.images[0].dtype,np.dtype('f2'))
            self.assertTrue(np.isfinite(c.images[0]).all());self.assertFalse(c.images[0].flags.writeable)
            self.assertEqual(list(c.roi.view('u2')[80:82]),[1,1])
            fingerprints.add(c.images[0].tobytes())
            for mask in semantic_masks(spec):
                self.assertTrue(np.all((mask>=0)&(mask<=1)))
        self.assertEqual(len(fingerprints),len(Pattern))

    def test_exposure_staircase_and_chromatic_edge_have_real_boundaries(self):
        x=rgb_pattern(SyntheticSpec(Pattern.EXPOSURE,4,16))
        self.assertLess(x[0,0,0],.001);self.assertGreater(x[0,-1,0],.7)
        np.testing.assert_array_equal(x[:,0],x[:,1])
        edge=rgb_pattern(SyntheticSpec(Pattern.EDGES,4,6))
        self.assertLess(edge[0,2,0],.04);self.assertGreater(edge[0,3,0],.8)
        self.assertGreater(edge[2,0,2],edge[0,0,2])

    def test_mask_endpoints_and_zero_nonfinite_negatives(self):
        for pattern,expected in [(MaskPattern.ZERO,0),(MaskPattern.ONE,1)]:
            for mask in semantic_masks(SyntheticSpec(Pattern.COLORS,masks=pattern)):
                np.testing.assert_array_equal(mask,expected)
        c=make_context(SyntheticSpec(Pattern.ZERO));np.testing.assert_array_equal(c.images[0][...,:3],0)
        images=list(c.images);images[0]=images[0].copy();images[0][0,0,0]=np.nan
        with self.assertRaises(TypeError):replace(c,images=tuple(images))
        with self.assertRaises(TypeError):SyntheticSpec('gradient')
        with self.assertRaises(ValueError):SyntheticSpec(Pattern.GRADIENT,31,8)


class CLIPersistenceTests(unittest.TestCase):
    def test_full_computation_persists_raw_inputs_stages_and_written_rgb_effect(self):
        from image_chain import Numerics,BranchSelection
        from image_chain_cli import execute
        with tempfile.TemporaryDirectory()as folder:
            path=Path(folder)/'run'
            report=execute(path,patterns=(Pattern.COLORS,),height=2,width=2,
                           mask_pattern=MaskPattern.SPATIAL,missing_masks=(),
                           values=(np.float32(0),np.float32(.125)),
                           numerics=Numerics.EXPERIMENTAL_PORTABLE_POINT,
                           selection=BranchSelection.CONTEXT,threshold=1e-3)
            self.assertEqual(report['summary']['writers'],2)
            self.assertFalse(report['Apple_pipeline_verified']);self.assertEqual(report['native_calls'],0)
            self.assertEqual(len(report['parameter_effects']),1)
            metric=report['parameter_effects'][0]['metric']
            self.assertEqual(metric['pixels'],4);self.assertEqual(metric['components'],12)
            first=np.load(path/'colors-0/checkpoints.npz')
            self.assertIn('raw_BG__lo',first);self.assertIn('output600__lo',first)
            self.assertEqual(first['writer__lo'].shape,(4,4,4))
            self.assertEqual(int(first['writer__written_mask'].sum()),4)
            saved=json.loads((path/'summary.json').read_text())
            self.assertEqual(saved['runs'][0]['input_context_sha256'],report['runs'][0]['input_context_sha256'])
            self.assertTrue((path/'colors-0/source-diagnostic.png').is_file())
            self.assertTrue((path/'colors-0/writer-diagnostic.png').is_file())
            with self.assertRaises(FileExistsError):
                execute(path,patterns=(Pattern.COLORS,),height=2,width=2,
                        mask_pattern=MaskPattern.SPATIAL,missing_masks=(),values=(np.float32(0),),
                        numerics=Numerics.EXPERIMENTAL_PORTABLE_POINT,
                        selection=BranchSelection.CONTEXT,threshold=1e-3)


if __name__=='__main__':unittest.main()
