from __future__ import annotations

import io
import hashlib
import json
from pathlib import Path
import plistlib
import struct
import tempfile
from dataclasses import replace
import unittest
from unittest.mock import patch
import zipfile
import zlib
import numpy as np

from firmware_probe import AppleRanges, central_entries, inspect
from download_component import download, select_component
from extract_downloaded import extract
from thumbnail_model import SampleContext, conditional_inverse, forward, inverse_supplied_curve
from version_gate import Firmware, Plugin, Loader, Sample, admit_static_sample_chain


class MetadataTests(unittest.TestCase):
    def test_extraction_stops_before_tools_on_incomplete_or_changed_component(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t); out = root / "output"
            (root / "download.json").write_text(json.dumps({"completed": False}))
            with patch("extract_downloaded.subprocess.run", side_effect=AssertionError("Must not invoke native tools")):
                with self.assertRaisesRegex(ValueError, "complete CRC"):
                    extract(root, out)
                (root / "image.aea").write_bytes(b"changed")
                (root / "download.json").write_text(json.dumps({"completed": True, "zip_crc_verified": True,
                    "entry": {"name": "image.aea", "compressed_bytes": 7}, "sha256": "0"*64}))
                with self.assertRaisesRegex(ValueError, "identity changed"):
                    extract(root, out)
            self.assertFalse(out.exists())

    def test_component_resume_uses_owned_prefix_and_checks_complete_crc(self):
        prefix = 16 * 1024**2
        body = bytes(range(256)) * (prefix // 256 + 1)
        name = b"system.dmg.aea"
        local = bytearray(30); local[:4] = b"PK\x03\x04"
        struct.pack_into("<HH", local, 26, len(name), 0)
        archive = bytes(local) + name + body
        entry = {"name": name.decode(), "method": 0, "compressed_bytes": len(body),
                 "uncompressed_bytes": len(body), "local_header_offset": 0, "crc32": f"{zlib.crc32(body):08x}"}
        url = "https://updates.cdn-apple.com/synthetic.ipsw"
        metadata = {"source_url": url, "identities": [{"variant": "Customer", "components": {"OS": name.decode()}}],
                    "image_entries": [entry], "build": "synthetic", "supported_product_types": ["synthetic"],
                    "build_manifest_sha256": "synthetic", "ipsw_total_bytes": len(archive)}
        requests = []
        class Response:
            status = 206
            def __init__(self, start, stop):
                self.start, self.stop = start, stop
                self.headers = {"Content-Range": f"bytes {start}-{stop}/{len(archive)}"}
            def geturl(self): return url
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read(self, n): return archive[self.start:self.stop+1]
        def open_range(request, timeout):
            start, stop = map(int, request.headers["Range"].split("=")[1].split("-"))
            requests.append((start, stop))
            return Response(start, stop)
        with tempfile.TemporaryDirectory() as t:
            root = Path(t); mp = root / "metadata.json"; mp.write_text(json.dumps(metadata))
            out = root / "component"; out.mkdir()
            (out / name.decode()).write_bytes(body[:prefix])
            (out / "download.json").write_text(json.dumps({"entry": entry, "source_url": url, "completed": False}))
            with patch("urllib.request.urlopen", side_effect=open_range):
                download(mp, "OS", out, "Customer", resume=True)
            result = json.loads((out / "download.json").read_text())
            self.assertTrue(result["completed"])
            self.assertEqual(result["sha256"], hashlib.sha256(body).hexdigest())
            self.assertEqual((out / name.decode()).read_bytes(), body)
            self.assertEqual(requests[-1][0], len(local) + len(name) + prefix)
            self.assertEqual(len(requests), 3)

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


class VersionTests(unittest.TestCase):
    def setUp(self):
        self.firmware = Firmware("synthetic-hardware", "synthetic-build")
        self.plugin = Plugin(self.firmware, "/VideoProcessors/SmartStyleV1.bundle", "CMISmartStyleProcessorV1", "1", "a"*64, True)
        self.loader = Loader(self.firmware, self.plugin.bundle_path, self.plugin.class_name, True, True)
        self.sample = Sample(self.firmware.hardware, self.firmware.build, 2, 16, 3)

    def test_product2_can_use_internal_v1_and_metadata16(self):
        r = admit_static_sample_chain(self.sample, self.plugin, self.loader, target_product_generation=2)
        self.assertTrue(r["static_version_chain_admitted"])
        self.assertFalse(r["runtime_loaded_verified"])
        self.assertFalse(r["camera_inverse_verified"])

    def test_name_change_to_v2_cannot_fix_missing_build_or_origin(self):
        sample = replace(self.sample, capture_build=None)
        plugin = replace(self.plugin, bundle_path="/VideoProcessors/SmartStyleV2.bundle", bundle_version="2",
                         official_image_membership_verified=False)
        r = admit_static_sample_chain(sample, plugin, self.loader, target_product_generation=2)
        self.assertFalse(r["static_version_chain_admitted"])
        self.assertIn("exact sample capture build unavailable", r["reasons"])

    def test_same_os_build_on_different_hardware_does_not_match(self):
        loader = replace(self.loader, firmware=Firmware("another-hardware", self.firmware.build))
        r = admit_static_sample_chain(self.sample, self.plugin, loader, target_product_generation=2)
        self.assertFalse(r["static_version_chain_admitted"])
        self.assertIn("loader and plugin firmware identities differ", r["reasons"])

    def test_generation3_sample_does_not_prove_generation2(self):
        r = admit_static_sample_chain(replace(self.sample, product_generation=3), self.plugin, self.loader,
                                     target_product_generation=2)
        self.assertFalse(r["static_version_chain_admitted"])


if __name__ == "__main__":
    unittest.main()
