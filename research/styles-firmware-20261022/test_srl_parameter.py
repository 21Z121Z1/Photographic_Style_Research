import unittest
import numpy as np
from srl_parameter import adjust_parameter


class SRLParameterTests(unittest.TestCase):
    def test_open_interval_and_nonfinite_sentinel(self):
        for x in [-np.inf,-1.,-0.,0.,1.,2.,np.inf,np.nan]:
            self.assertEqual(adjust_parameter(x,0),-1)
        x=np.nextafter(np.float32(0),np.float32(1))
        self.assertEqual(adjust_parameter(x,0).view('u4'),x.view('u4'))

    def test_integer_field_is_converted_then_added_and_can_lose_fraction(self):
        self.assertEqual(adjust_parameter(.25,2),2.25)
        self.assertEqual(adjust_parameter(.25,0xffffffff),np.float32(2**32))
        self.assertEqual(adjust_parameter(.75,0xffffffff),np.float32(2**32))
        for bad in [-1,2**32,1.0]:
            with self.assertRaises(ValueError):adjust_parameter(.5,bad)


if __name__=='__main__':unittest.main()
