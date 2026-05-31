import unittest

import numpy as np
from PIL import Image

from tools.styledeltamap_diagnostics import compute_image_stats


class StyledeltaDiagnosticsTests(unittest.TestCase):
    def test_compute_image_stats_reports_channel_metrics(self):
        data = np.array(
            [
                [[0, 10, 20], [10, 20, 30]],
                [[20, 30, 40], [30, 40, 50]],
            ],
            dtype=np.uint8,
        )
        stats = compute_image_stats(Image.fromarray(data, "RGB"))

        self.assertEqual(stats["mode"], "RGB")
        self.assertEqual(stats["size"], {"width": 2, "height": 2})
        self.assertEqual(stats["dtype"], "uint8")
        self.assertEqual(stats["min"], [0, 10, 20])
        self.assertEqual(stats["max"], [30, 40, 50])
        self.assertEqual(stats["mean"], [15.0, 25.0, 35.0])
        self.assertEqual(stats["unique_values_sample"], 6)


if __name__ == "__main__":
    unittest.main()
