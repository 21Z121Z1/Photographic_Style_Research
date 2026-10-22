import struct
import unittest

from air_compare import payloads
from air_alpha import canonicalize


SAMPLE = '''; ModuleID = '/private/temp/module.bc'
source_filename = "test"
target datalayout = "e-p:64:64"
target triple = "air64_v29-apple-ios27.0.0"
%"struct.layout.11" = type { half, i32 }
@gate.10 = internal addrspace(2) global i8 0, align 1
@sampler = internal constant i64 34901797601020416
define half @kernel(%"struct.layout.11" %0, half %1) {
  %2 = fmul fast half %1, 0xH3800
  ret half %2
}
!llvm.ident = !{!9}
!9 = !{!"Apple metal version 32023.921 (metalfe-32023.921.6)"}
!10 = !{ptr addrspace(2) @gate.10, !"air.location_index", i32 15}
!11 = !{!"%struct.layout.11 @gate.10 stays a string"}
'''


class AirComparisonTests(unittest.TestCase):
    def test_wrapper_bounds_and_magic(self):
        raw = b'BC\xc0\xdeabcd'
        valid = struct.pack('<5I', 0xb17c0de, 0, 20, len(raw), 0) + raw
        self.assertEqual(list(payloads(valid))[0][2], raw)
        for value in [valid[:19], valid[:-1], struct.pack('<5I', 0xb17c0de, 0, 19, len(raw), 0)+raw, valid[:20]+b'bad!abcd']:
            self.assertEqual(list(payloads(value)), [])

    def test_only_provenance_and_bijective_labels_can_match(self):
        other = SAMPLE.replace("'/private/temp/module.bc'", "'/elsewhere/bc'").replace('apple-ios', 'apple-macosx').replace('metalfe-32023.921.6', 'metalfe-32023.921.4')
        # Replace symbol tokens while deliberately preserving the metadata string.
        other = other.replace('%"struct.layout.11"', '%"struct.layout.22"').replace('@gate.10 =', '@gate.13 =').replace(') @gate.10,', ') @gate.13,')
        a, provenance = canonicalize(SAMPLE); b, _ = canonicalize(other)
        self.assertEqual(a, b)
        self.assertIn('!"%struct.layout.11 @gate.10 stays a string"', a)
        self.assertEqual(provenance['target_triple'], 'air64_v29-apple-ios27.0.0')

    def test_semantic_constants_layout_flags_bindings_and_sampler_survive(self):
        base, _ = canonicalize(SAMPLE)
        for old, new in [('0xH3800', '0xH3C00'), ('half, i32', 'half, i64'), ('fmul fast', 'fmul'), ('i32 15}', 'i32 14}'), ('34901797601020416', '34901797601020489'), ('global i8 0', 'global i8 1'), ('e-p:64:64', 'e-p:32:32')]:
            self.assertNotEqual(base, canonicalize(SAMPLE.replace(old, new))[0], (old, new))

    def test_reserved_symbol_collision_rejected(self):
        with self.assertRaisesRegex(ValueError, 'collides'):
            canonicalize(SAMPLE + '@"psr.internal.0" = external global i8\n')


if __name__ == '__main__': unittest.main()
