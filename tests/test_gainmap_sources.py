import tempfile
import unittest
import shutil
from pathlib import Path

import numpy as np
from PIL import Image

from tools.gainmap_sources import extract_apple_heic_hdr_gainmap, extract_oppo_gainmap, load_gainmap_source


UHDR_SAMPLE = Path("/Users/retriedstormtrooper/Documents/proxdrtest/test-samples/uhdr/IMG20260424200116.heic")
LHDR_SAMPLE = Path("/Users/retriedstormtrooper/Documents/proxdrtest/test-samples/lhdr/IMG20240725150658.heic")
COMBINED_DNG_SAMPLE = Path("/Users/retriedstormtrooper/Documents/OPPO 互联/combine dng/IMG20260530190200.dng")
APPLE_HDR_SAMPLE = Path("Apple_Native_Samples/IMG_0032.HEIC")


class GainMapSourceTests(unittest.TestCase):
    def test_loads_plain_rgb_gainmap_image(self):
        arr = np.zeros((20, 30, 3), dtype=np.uint8)
        arr[..., 0] = np.linspace(0, 255, 30, dtype=np.uint8)
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            path = Path(tmp.name)
        try:
            Image.fromarray(arr, "RGB").save(path)
            source = load_gainmap_source(path, mode="image")
            self.assertEqual(source.mode, "image-rgb")
            self.assertEqual(source.image.mode, "RGB")
            self.assertEqual(source.image.size, (30, 20))
        finally:
            path.unlink(missing_ok=True)

    def test_loads_plain_mono_gainmap_image(self):
        arr = np.tile(np.linspace(0, 255, 30, dtype=np.uint8), (20, 1))
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            path = Path(tmp.name)
        try:
            Image.fromarray(arr, "L").save(path)
            source = load_gainmap_source(path, mode="image")
            self.assertEqual(source.mode, "image-mono")
            self.assertEqual(source.image.mode, "L")
        finally:
            path.unlink(missing_ok=True)

    @unittest.skipUnless(UHDR_SAMPLE.exists(), "OPPO UHDR sample not available")
    def test_extracts_oppo_uhdr_rgb_gainmap(self):
        source = extract_oppo_gainmap(UHDR_SAMPLE)
        self.assertEqual(source.mode, "oppo-uhdr-rgb")
        self.assertEqual(source.image.mode, "RGB")
        self.assertIn("uhdr_info", source.metadata)
        self.assertIn("ratioMax", source.metadata["uhdr_info"])
        self.assertGreater(source.raw_bytes_len, 0)

    @unittest.skipUnless(LHDR_SAMPLE.exists(), "OPPO LHDR sample not available")
    def test_extracts_oppo_lhdr_mono_gainmap(self):
        source = extract_oppo_gainmap(LHDR_SAMPLE)
        self.assertEqual(source.mode, "oppo-lhdr-mono")
        self.assertEqual(source.image.mode, "L")
        self.assertIn("lhdr_meta_floats", source.metadata)
        self.assertGreater(source.raw_bytes_len, 0)

    @unittest.skipUnless(COMBINED_DNG_SAMPLE.exists(), "combined DNG sample not available")
    def test_loads_dng_preview_mpf_gainmap(self):
        source = load_gainmap_source(COMBINED_DNG_SAMPLE, mode="auto")
        self.assertEqual(source.mode, "dng-preview-mpf-rgb")
        self.assertEqual(source.image.mode, "RGB")
        self.assertIn("preview_bytes", source.metadata)
        self.assertGreater(source.raw_bytes_len, 0)

    @unittest.skipUnless(
        APPLE_HDR_SAMPLE.exists() and shutil.which("heif-convert"),
        "Apple HDR HEIC sample or heif-convert not available",
    )
    def test_extracts_apple_heic_hdr_gainmap_structure_and_raster(self):
        source = extract_apple_heic_hdr_gainmap(APPLE_HDR_SAMPLE)
        self.assertEqual(source.mode, "apple-heic-hdrgainmap")
        self.assertEqual(source.image.mode, "L")
        self.assertEqual(source.metadata["aux_type"], "urn:com:apple:photo:2020:aux:hdrgainmap")
        self.assertIn("item_id", source.metadata)
        self.assertIn("derived_children", source.metadata)


if __name__ == "__main__":
    unittest.main()
