import unittest
from dataclasses import replace
import numpy as np
from semantic_tone import Curve1D,SemanticInputs,forward_half,forward_set,from_consumer_fields,EPS
from semantic_caller import runtime_semantic_set
from tone_interface import evaluate,RendererControls,ResolvedSceneType
from test_tone_interface import frame


def inputs():return SemanticInputs((.2,.4,.8),(.25,.5,1),.3,Curve1D(tuple(np.linspace(0,1,17)),'supplied working RGB/GTC'))


class SemanticToneTests(unittest.TestCase):
    def test_sample_centers_clamp_and_nonmonotone_interval_range(self):
        c=Curve1D((0,.75,.25,.5,1),'test')
        np.testing.assert_array_equal(c.sample(np.array([-1,0,.25,.5,.75,1,2])),[0,0,.75,.25,.5,1,1])
        a,b=c.range(np.array([.1]),np.array([.9]));self.assertLess(a[0],.3);self.assertGreaterEqual(b[0],.75)

    def test_all_seven_fields_person_endpoints_and_reference_identity(self):
        inp=inputs();p=[1,1,1,1,0,1,1]
        np.testing.assert_array_equal(forward_half(inp,p),np.asarray(inp.reference_rgb,dtype='f2'))
        p=[0,0,.5,1,0,0,0]
        bg=forward_half(replace(inp,person_weight=0),p);fg=forward_half(replace(inp,person_weight=1),p)
        self.assertGreater(float(fg[0]),float(bg[0]))
        box=forward_set(inp,p,p);point=forward_half(inp,p)
        self.assertTrue(np.all(point>=box.lower)and np.all(point<=box.upper))

    def test_reference_threshold_is_strict_less_with_equality_retained(self):
        inp=inputs();p=[0,0,1,1,0,0,0];low=float(np.nextafter(np.float16(EPS),np.float16(0)))
        a=forward_half(replace(inp,reference_rgb=(low,low,low)),p)
        b=forward_half(replace(inp,reference_rgb=(EPS,EPS,EPS)),p)
        np.testing.assert_array_equal(a,[0,0,0]);self.assertGreater(float(b[0]),.19)

    def test_set_contract_survives_semantic_and_cast2_caller(self):
        t=float(np.float32(.5**(4/3)));f=frame();fields=evaluate(RendererControls(.5,t,0),ResolvedSceneType(0),f)
        self.assertFalse(fields.branch_determined)
        for result in [from_consumer_fields(inputs(),fields),runtime_semantic_set(inputs(),fields,cast_type=2,baseline_exposure=1)]:
            self.assertTrue(result.set_coverage_only);self.assertFalse(result.original_GPU_accuracy_verified)
            self.assertTrue(any(b.state=='undetermined'for b in result.input_branches))
            self.assertTrue(np.all(result.lower<=result.upper))

    def test_bad_domains_are_unknown_or_rejected_not_hardware_blockers(self):
        inp=inputs()
        for bad in [replace(inp,reference_rgb=(0,0,0)),replace(inp,person_weight=2),replace(inp,working_rgb=(np.nan,0,0))]:
            with self.assertRaises(ValueError):forward_half(bad,[1]*7)
        with self.assertRaises(ValueError):Curve1D((0,), 'test')
        with self.assertRaises(ValueError):Curve1D((0,1),'')
        with self.assertRaises(ValueError):forward_set(inp,[1]*7,[0]*7)
        extreme=replace(inp,curve=Curve1D((8,8),'finite domain negative test'),reference_rgb=(2**-10,)*3,working_rgb=(1,)*3)
        with self.assertRaises(ValueError):forward_half(extreme,[0,0,-8,-8,8,0,0])


if __name__=='__main__':unittest.main()
