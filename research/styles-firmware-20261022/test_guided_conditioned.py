import unittest
import numpy as np
from guided_conditioned import Inputs,forward,forward_set
from native_guided_check import fixtures
from leaf_numeric import DomainUnknown


class GuidedTests(unittest.TestCase):
    def test_grid_and_precision_contract(self):
        inputs,_=next(fixtures());r=forward(inputs)
        self.assertEqual(r['a'].shape,(4,5,1));self.assertEqual(r['output'].shape,(6,7,1));self.assertEqual(r['a'].dtype,np.dtype('f2'))
        with self.assertRaises(TypeError):Inputs(inputs.input_gain,inputs.guide,inputs.output_shape,1,.05,'test')
        with self.assertRaises(ValueError):Inputs(inputs.input_gain,inputs.guide,inputs.output_shape,2,np.float32(.05),'test')

    def test_point_and_set_unknown_are_separate(self):
        inputs,_=list(fixtures())[-1]
        with self.assertRaises(DomainUnknown):forward(inputs)
        with self.assertRaises(DomainUnknown):forward_set(inputs)

    def test_whole_input_sets_are_propagated(self):
        from leaf_numeric import V
        inputs,_=next(fixtures());point=forward(inputs)['output'];a=forward_set(inputs);wide=V.bounds(inputs.input_gain-.001,inputs.input_gain+.001);b=forward_set(inputs,gain=wide)
        self.assertTrue(np.all(point>=a['output'].lo)and np.all(point<=a['output'].hi));self.assertGreater(np.max(b['output'].hi-b['output'].lo),np.max(a['output'].hi-a['output'].lo))

    def test_scalar_guide_is_not_three_scalar_calls(self):
        inputs,_=list(fixtures())[2];rgb=forward(inputs)['output'];split=[]
        for i in range(3):split.append(forward(Inputs(inputs.input_gain[...,i:i+1],inputs.guide,inputs.output_shape,1,inputs.epsilon_f32,'test'))['output'])
        separated=np.concatenate(split,axis=2)
        np.testing.assert_array_equal(rgb[...,0],separated[...,0]);self.assertGreater(np.max(abs(rgb[...,1:]-separated[...,1:])),.05)


if __name__=='__main__':unittest.main()
