from __future__ import annotations

import io
import plistlib
import struct
import unittest
from unittest.mock import patch
import zipfile
import numpy as np

from firmware_probe import AppleRanges, central_entries, inspect
from download_component import select_component
from thumbnail_model import SampleContext, conditional_inverse, forward, inverse_supplied_curve


class MetadataTests(unittest.TestCase):
    def test_exact_variant_does_not_select_recovery_os(self):
        m = {"identities": [{"variant": "Customer Erase Install (IPSW)", "components": {"OS": "main"}},
                            {"variant": "Recovery Customer Install", "components": {"OS": "recovery"}}],
             "image_entries": [{"name": n, "method": 0, "compressed_bytes": z, "uncompressed_bytes": z}
                               for n, z in [("main", 9000), ("recovery", 200)]]}
        self.assertEqual(select_component(m, "OS", "Customer Erase Install (IPSW)")["name"], "main")
        with self.assertRaisesRegex(ValueError, "unambiguous"):
            select_component(m, "OS", "missing")

    def fixture(self) -> bytes:
        output = io.BytesIO()
        manifest = {"ProductVersion": "27.0.1", "ProductBuildVersion": "24A446",
                    "SupportedProductTypes": ["iPhone17,3"], "BuildIdentities": []}
        with zipfile.ZipFile(output, "w") as z:
            z.writestr("BuildManifest.plist", plistlib.dumps(manifest), compress_type=zipfile.ZIP_DEFLATED)
            z.writestr("OS.dmg.aea", b"DO NOT DOWNLOAD" * 6000)
        return output.getvalue()

    def test_manifest_only_and_mismatch(self):
        data = self.fixture()
        reads = []
        def part(start, n):
            reads.append((start, n))
            return data[start:start+n]
        report = inspect(len(data), part, "iPhone17,3", "24A446")
        self.assertTrue(report["zip_crc_verified"])
        self.assertEqual(report["filesystem_image_bytes_downloaded"], 0)
        self.assertLess(sum(n for _, n in reads), len(data))
        for device, build in [("iPhone19,2", "24A446"), ("iPhone17,3", "24A435")]:
            with self.assertRaisesRegex(ValueError, "does not match"):
                inspect(len(data), part, device, build)

    def test_crc_and_directory_corruption(self):
        data = bytearray(self.fixture())
        off = data.find(b"PK\x01\x02")
        data[off + 16] ^= 1
        with self.assertRaisesRegex(ValueError, "CRC"):
            inspect(len(data), lambda start, n: bytes(data[start:start+n]), "iPhone17,3", "24A446")
        with self.assertRaises(ValueError):
            central_entries(b"broken", 1)

    def test_zip64_extra_offsets(self):
        header = bytearray(46)
        header[:4] = b"PK\x01\x02"
        struct.pack_into("<III", header, 16, 0, 0xffffffff, 0xffffffff)
        struct.pack_into("<HHH", header, 28, 1, 28, 0)
        struct.pack_into("<I", header, 42, 0xffffffff)
        entry = central_entries(bytes(header) + b"x" + struct.pack("<HHQQQ", 1, 24, 9, 7, 2**33), 1)[0]
        self.assertEqual((entry.uncompressed, entry.compressed, entry.offset), (9, 7, 2**33))

    def test_http200_is_rejected_before_body_read(self):
        r = AppleRanges.__new__(AppleRanges)
        r.url = "https://updates.cdn-apple.com/test.ipsw"
        r.budget, r.received, r.size = 100, 0, 1000
        class Response:
            status, headers = 200, {}
            def geturl(self): return r.url
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read(self, n): raise AssertionError("Must not read a full-file response")
        with patch("urllib.request.urlopen", return_value=Response()):
            with self.assertRaisesRegex(ValueError, "206"):
                r.part(0, 20)
        with self.assertRaisesRegex(ValueError, "budget"):
            r.part(0, 101)
        for bad in ["http://updates.cdn-apple.com/x", "https://example.com/x", "https://u:p@updates.cdn-apple.com/x"]:
            with self.assertRaises(ValueError):
                AppleRanges.check_url(bad)


class OperatorTests(unittest.TestCase):
    def test_single_variable_ratio_clamp_and_interior(self):
        post = np.array([[.2, .4, .6]] * 5)
        context = SampleContext(np.ones((5, 3)), np.array([[.5]*3, [2.]*3, [0.]*3, [.7]*3, [.7]*3]),
                                np.array([False, False, False, True, False]))
        y = forward(post, context)
        np.testing.assert_allclose(y, [post[0]*.5, post[1], post[2]*0, [.7]*3, post[4]*.7])
        r = conditional_inverse(y, context, prior_lower=0, prior_upper=2)
        np.testing.assert_array_equal(r["unique_in_model_mask"], [True, True, False, False, True])
        np.testing.assert_allclose(r["candidate"][[0, 1, 4]], post[[0, 1, 4]])
        np.testing.assert_array_equal(r["lower"][[2, 3]], 0)
        np.testing.assert_array_equal(r["upper"][[2, 3]], 2)

    def test_random_holdout_conditional_roundtrip(self):
        rng = np.random.default_rng(101)
        post = rng.uniform(-.02, 1.25, (1000, 3))
        context = SampleContext(rng.uniform(.01, 1, (1000, 3)), rng.uniform(.01, 1, (1000, 3)),
                                rng.random(1000) < .25)
        y = forward(post, context)
        result = conditional_inverse(y, context, prior_lower=-.02, prior_upper=1.25)
        unique = result["unique_in_model_mask"]
        np.testing.assert_allclose(result["candidate"][unique], post[unique], atol=1e-15, rtol=1e-15)
        self.assertTrue(result["valid_mask"].all())
        self.assertFalse(result["camera_inverse_verified"])

    def test_same_observation_different_hidden_input(self):
        context = SampleContext(np.ones((1, 3)), np.array([[.7]*3]), np.array([True]))
        np.testing.assert_array_equal(forward(np.zeros((1, 3)), context), forward(np.ones((1, 3)), context))
        r = conditional_inverse(np.array([[.7]*3]), context, prior_lower=-.02, prior_upper=1.25)
        self.assertFalse(r["unique_in_model_mask"][0])
        np.testing.assert_array_equal(r["lower"], -.02)
        np.testing.assert_array_equal(r["upper"], 1.25)

    def test_existing_s20_plateau_set_is_preserved(self):
        x = np.linspace(0, 1, 5)
        r = inverse_supplied_curve(np.array([.5]), x, np.array([0, 0, .5, .5, 1]), x,
                                  storage="exact", implementation_error_abs=0)
        self.assertLessEqual(r["neutral_lower"][0], .5)
        self.assertGreaterEqual(r["neutral_upper"][0], .75)
        self.assertFalse(r["guaranteed_1e3_mask"][0])
        self.assertTrue(np.isnan(r["candidate"][0]))


if __name__ == "__main__":
    unittest.main()
