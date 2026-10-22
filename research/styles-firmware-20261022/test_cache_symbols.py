import unittest
from export_cache_methods import select_symbol


class CacheSymbolTests(unittest.TestCase):
    def test_repeated_local_names_require_exact_verified_address(self):
        text='0x1234:  (__TEXT,__text) private\t_OUTLINED_FUNCTION_28\t\n0x5678:  (__TEXT,__text) private\t_OUTLINED_FUNCTION_28\t\n'
        with self.assertRaises(ValueError):select_symbol(text,'_OUTLINED_FUNCTION_28')
        self.assertEqual(select_symbol(text,'_OUTLINED_FUNCTION_28',0x1234),0x1234)
        with self.assertRaises(ValueError):select_symbol(text,'_OUTLINED_FUNCTION_28',0x9999)


if __name__=='__main__':unittest.main()
