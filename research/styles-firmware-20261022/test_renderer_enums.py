import unittest
from renderer_enums import resolve_scene_type,resolve_tuning_type,UnknownTuningType,TUNING_TYPES


class RendererEnumTests(unittest.TestCase):
    def test_scene_table_and_unknown_fallback_are_not_tuning_codes(self):
        self.assertEqual([resolve_scene_type(x).code for x in [0,1,2,3,4,21,2**32-1]],[4,3,7,10,4,4,4])
        self.assertNotIn(21,[resolve_scene_type(x).code for x in range(100)])

    def test_tuning_exact_keys_and_unknown_have_no_default_return(self):
        self.assertEqual(set(map(resolve_tuning_type,TUNING_TYPES)),set(range(1,9)))
        self.assertEqual(resolve_tuning_type('DefaultParameters'),1)
        for name in ['defaultparameters','Unknown','',None,9]:
            with self.assertRaises(UnknownTuningType):resolve_tuning_type(name)


if __name__=='__main__':unittest.main()
