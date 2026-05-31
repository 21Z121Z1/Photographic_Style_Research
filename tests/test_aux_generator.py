import unittest
from pathlib import Path

import numpy as np
from PIL import Image

from tools.aux_generator import (
    generate_linearthumbnail,
    generate_styledeltamap,
    _compute_affine_params,
    _resize_fit,
)


PREVIEW_PATH = Path("/Users/retriedstormtrooper/Downloads/03_图片素材/RAW_DNG照片/RAW_DNG_JPEG_批量导出/IMG_0342_preview.jpg")


def _make_test_image(width: int = 800, height: int = 600) -> Path:
    """Create a small test image with a gradient for testing."""
    import tempfile

    arr = np.zeros((height, width, 3), dtype=np.uint8)
    for y in range(height):
        for x in range(width):
            arr[y, x, 0] = int(x / width * 255)
            arr[y, x, 1] = int(y / height * 255)
            arr[y, x, 2] = 128
    img = Image.fromarray(arr, "RGB")
    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    img.save(tmp.name)
    return Path(tmp.name)


class ResizeFitTests(unittest.TestCase):
    def test_resize_preserves_aspect_ratio(self):
        img = Image.new("RGB", (2000, 1000), (128, 128, 128))
        result = _resize_fit(img, 1024)
        self.assertEqual(result.size[0], 1024)
        self.assertEqual(result.size[1], 512)

    def test_no_resize_when_within_limit(self):
        img = Image.new("RGB", (500, 300), (128, 128, 128))
        result = _resize_fit(img, 1024)
        self.assertEqual(result.size, (500, 300))

    def test_resize_tall_image(self):
        img = Image.new("RGB", (1000, 2000), (128, 128, 128))
        result = _resize_fit(img, 1024)
        self.assertEqual(result.size[1], 1024)
        self.assertEqual(result.size[0], 512)


class AffineParamsTests(unittest.TestCase):
    def test_affine_params_produce_reasonable_range(self):
        arr = np.random.randint(20, 240, (100, 100, 3), dtype=np.uint8)
        slope, intercept = _compute_affine_params(arr)

        self.assertGreater(slope, 0.5)
        self.assertLess(slope, 5.0)

        # Check that the midpoint maps near 500
        mid_8bit = float(np.mean(arr))
        mid_10bit = slope * mid_8bit + intercept
        self.assertGreater(mid_10bit, 400)
        self.assertLess(mid_10bit, 600)

    def test_affine_params_dark_scene(self):
        arr = np.random.randint(5, 80, (100, 100, 3), dtype=np.uint8)
        slope, intercept = _compute_affine_params(arr)

        # Dark scenes should have larger slope (more amplification)
        self.assertGreater(slope, 1.0)

    def test_affine_params_bright_scene(self):
        arr = np.random.randint(180, 250, (100, 100, 3), dtype=np.uint8)
        slope, intercept = _compute_affine_params(arr)

        # Bright scenes should have reasonable slope
        self.assertGreater(slope, 0.5)
        self.assertLessEqual(slope, 5.0)


class LinearThumbnailGeneratorTests(unittest.TestCase):
    def test_generates_image_with_correct_size(self):
        test_path = _make_test_image(1600, 1200)
        try:
            result = generate_linearthumbnail(test_path, max_dim=1024)
            self.assertLessEqual(max(result.image.size), 1024)
            self.assertEqual(result.image.mode, "RGB")
        finally:
            test_path.unlink()

    def test_output_10bit_range_is_in_apple_band(self):
        test_path = _make_test_image(800, 600)
        try:
            result = generate_linearthumbnail(test_path, max_dim=1024)
            arr = np.asarray(result.image, dtype=np.float64)
            arr_10bit = arr * (1023.0 / 255.0)

            mean_10bit = float(np.mean(arr_10bit))
            # Should be centered near 500 (Apple-native range)
            self.assertGreater(mean_10bit, 350)
            self.assertLess(mean_10bit, 650)
        finally:
            test_path.unlink()

    def test_stats_contain_affine_params(self):
        test_path = _make_test_image(400, 300)
        try:
            result = generate_linearthumbnail(test_path, max_dim=1024)
            self.assertIn("affine", result.stats)
            self.assertIn("slope", result.stats["affine"])
            self.assertIn("intercept", result.stats["affine"])
            self.assertIn("output_10bit_stats", result.stats)
        finally:
            test_path.unlink()

    @unittest.skipUnless(PREVIEW_PATH.exists(), "Preview JPG not available")
    def test_with_real_preview_jpg(self):
        result = generate_linearthumbnail(PREVIEW_PATH, max_dim=1024)

        self.assertEqual(result.image.mode, "RGB")
        arr = np.asarray(result.image, dtype=np.float64)
        arr_10bit = arr * (1023.0 / 255.0)

        mean_10bit = float(np.mean(arr_10bit))
        std_10bit = float(np.std(arr_10bit))

        # Should be centered near 500 with moderate spread
        self.assertGreater(mean_10bit, 400)
        self.assertLess(mean_10bit, 600)
        self.assertGreaterEqual(float(np.min(arr_10bit)), 250)
        self.assertLessEqual(float(np.max(arr_10bit)), 760)
        self.assertGreater(std_10bit, 10)
        self.assertLess(std_10bit, 200)


class StyleDeltaMapGeneratorTests(unittest.TestCase):
    def test_generates_constant_neutral_image(self):
        result = generate_styledeltamap(width=2880, height=2160)

        arr = np.asarray(result.image)
        self.assertEqual(arr.shape, (2160, 2880, 3))
        self.assertTrue(np.all(arr == 128))

    def test_default_dimensions_match_apple(self):
        result = generate_styledeltamap()
        self.assertEqual(result.image.size, (2880, 2160))

    def test_custom_dimensions(self):
        result = generate_styledeltamap(width=1024, height=768)
        arr = np.asarray(result.image)
        self.assertEqual(arr.shape, (768, 1024, 3))

    def test_stats_report_mode(self):
        result = generate_styledeltamap()
        self.assertEqual(result.stats["mode"], "neutral")
        self.assertEqual(result.stats["neutral_value_8bit"], 128)

    def test_custom_neutral_value(self):
        result = generate_styledeltamap(neutral_8bit=130)
        arr = np.asarray(result.image)
        self.assertTrue(np.all(arr == 130))
        self.assertEqual(result.stats["neutral_value_8bit"], 130)


if __name__ == "__main__":
    unittest.main()
