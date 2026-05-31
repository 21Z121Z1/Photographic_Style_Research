import tempfile
import unittest
from pathlib import Path

import numpy as np

from tools.proraw_residual_probe import discover_pairs, generate_candidate_maps


class ProRawResidualProbeTests(unittest.TestCase):
    def test_discover_pairs_matches_converted_dng_with_preview_jpg(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "IMG_0001_converted.DNG").write_bytes(b"dng")
            (root / "IMG_0001_preview.jpg").write_bytes(b"jpg")
            (root / "IMG_0002_converted.DNG").write_bytes(b"dng")

            pairs = discover_pairs(root)

            self.assertEqual(list(pairs), ["IMG_0001"])
            self.assertEqual(pairs["IMG_0001"].dng.name, "IMG_0001_converted.DNG")
            self.assertEqual(pairs["IMG_0001"].preview.name, "IMG_0001_preview.jpg")

    def test_generate_candidate_maps_are_neutral_centered_rgb_uint8(self):
        high = np.array(
            [
                [[0.6, 0.5, 0.4], [0.7, 0.6, 0.5]],
                [[0.3, 0.4, 0.5], [0.2, 0.3, 0.4]],
            ],
            dtype=np.float32,
        )
        base = np.full((2, 2, 3), 0.5, dtype=np.float32)

        candidates = generate_candidate_maps(high, base, amplitude=4)

        self.assertEqual(set(candidates), {"neutral", "luma_residual", "chroma_luma_residual"})
        for candidate in candidates.values():
            self.assertEqual(candidate.image.dtype, np.uint8)
            self.assertEqual(candidate.image.shape, (2, 2, 3))
            self.assertLessEqual(candidate.image.max(), 132)
            self.assertGreaterEqual(candidate.image.min(), 124)
            self.assertIn("unique_values_sample", candidate.stats)
            self.assertIn("base_luma_corr_by_channel", candidate.stats)


if __name__ == "__main__":
    unittest.main()
