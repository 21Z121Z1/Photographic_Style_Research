from fractions import Fraction
from pathlib import Path
import struct
import tempfile
import unittest
import numpy as np

from gtc_texture import build_texture, round_nonnegative_fraction_f32
from component_inventory import imports, inspect_node


def record(header: int, values) -> bytes:
    return np.array([header, *values], dtype="<u2").tobytes()


class GenericGTCTests(unittest.TestCase):
    def test_exact_f32_rounding_avoids_double_round_at_midpoint(self):
        mid = Fraction(1) + Fraction(1, 2**24)
        self.assertEqual(round_nonnegative_fraction_f32(mid), 1.0)
        self.assertEqual(round_nonnegative_fraction_f32(mid + Fraction(1, 2**100)), float(np.nextafter(np.float32(1), np.float32(2))))
        self.assertEqual(round_nonnegative_fraction_f32(mid - Fraction(1, 2**100)), 1.0)

    def test_header_and_read_span_guards_preserve_nonfinite_obligation(self):
        for raw in [b"", b"x", record(64, [1]*63), record(129, [1]*127), record(4098, [1]*4097)]:
            with self.assertRaises(ValueError): build_texture(raw)
        with self.assertRaisesRegex(ValueError, "Zero normalization"):
            build_texture(record(129, [0]*128))

    def test_constant_texture_and_trailing_data_do_not_change_output(self):
        raw = record(129, [12345]*128)
        a = build_texture(raw); b = build_texture(raw + b"\xff\xff\x01\x00")
        np.testing.assert_array_equal(a.half_values, np.ones(256, dtype="f2"))
        np.testing.assert_array_equal(a.half_values, b.half_values)
        self.assertFalse(a.camera_inverse_verified)

    def test_normalization_scale_is_not_identifiable_from_texture(self):
        a = build_texture(record(129, np.arange(128)*100))
        b = build_texture(record(129, np.arange(128)*200))
        np.testing.assert_array_equal(a.half_values, b.half_values)
        np.testing.assert_array_equal(a.normalized_nodes, b.normalized_nodes)

    def test_step_resampling_has_a_local_transition(self):
        values = np.where(np.arange(128) < 64, 0, 65535)
        result = build_texture(record(129, values))
        self.assertEqual(float(result.half_values[0]), 0)
        self.assertEqual(float(result.half_values[-1]), 1)
        self.assertTrue(np.all(np.diff(result.half_values.astype('f4')) >= 0))
        self.assertGreater(int(((result.half_values > 0) & (result.half_values < 1)).sum()), 0)

    def test_finite_normalized_nodes_can_overflow_half_without_mask_deletion(self):
        values = np.full(64, 65535); values[-1] = 1
        result = build_texture(record(65, values))
        self.assertTrue(np.isfinite(result.normalized_nodes).all())
        self.assertGreater(int(np.isinf(result.half_values).sum()), 0)
        self.assertEqual(len(result.half_values), 256)


class InventoryTests(unittest.TestCase):
    def test_absolute_symlink_is_reported_without_host_traversal(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t); (root/'link').symlink_to('/System/Library')
            result = inspect_node(root, 'link/PrivateFrameworks')
            self.assertEqual(result['status'], 'symlink_not_followed')
            self.assertEqual(result['target'], '/System/Library')
            with self.assertRaises(ValueError): inspect_node(root, '../outside')

    def test_library_ordinal_resolves_import_not_defined_class(self):
        name = b'/test/CMImaging\0'; dylib = bytearray((24+len(name)+7)//8*8)
        struct.pack_into('<III', dylib, 0, 0xc, len(dylib), 24); dylib[24:24+len(name)] = name
        strings = b'\0_OBJC_CLASS_$_CMISmartStyleCCMPriorGenerator\0'
        symoff = 32 + len(dylib) + 24; stroff = symoff + 32
        symtab = struct.pack('<IIIIII', 2, 24, symoff, 2, stroff, len(strings))
        header = struct.pack('<IIIIIIII', 0xfeedfacf, 0x100000c, 0, 8, 2, len(dylib)+24, 0, 0)
        # One undefined external import; a defined external with the same name
        # must not be misclassified as another framework's implementation.
        data = header + dylib + symtab + struct.pack('<IBBHQ', 1, 1, 0, 1<<8, 0) + struct.pack('<IBBHQ', 1, 0xf, 1, 0, 123) + strings
        result = imports(data)
        self.assertEqual(len(result['selected_imports']), 1)
        self.assertEqual(result['selected_imports'][0]['library'], '/test/CMImaging')
        self.assertFalse(result['dispatch_implementation_verified'])


if __name__ == '__main__':
    unittest.main()
