import unittest
from pathlib import Path
import tempfile

import numpy as np
from PIL import Image

from tools.aux_generator import (
    generate_linearthumbnail_from_gainmap,
    generate_linearthumbnail_from_best_source,
    generate_linearthumbnail,
    generate_styledeltamap,
    generate_styledeltamap_from_gainmap,
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


def _make_test_gainmap(width: int = 400, height: int = 300, *, mono: bool = False) -> Path:
    x = np.linspace(0, 255, width, dtype=np.uint8)
    y = np.linspace(0, 255, height, dtype=np.uint8)
    xx, yy = np.meshgrid(x, y)
    if mono:
        arr = ((xx.astype(np.uint16) + yy.astype(np.uint16)) // 2).astype(np.uint8)
        img = Image.fromarray(arr, "L")
    else:
        arr = np.stack([xx, yy, np.full_like(xx, 128)], axis=2)
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

    def test_generates_linearthumbnail_from_rgb_gainmap(self):
        base_path = _make_test_image(640, 480)
        gainmap_path = _make_test_gainmap(320, 240)
        try:
            result = generate_linearthumbnail_from_gainmap(base_path, gainmap_path, max_dim=256, gainmap_mode="image")
            self.assertEqual(result.image.mode, "RGB")
            self.assertLessEqual(max(result.image.size), 256)
            self.assertEqual(result.stats["mode"], "gainmap_linearthumbnail")
            self.assertEqual(result.stats["gainmap_source_mode"], "image-rgb")
            arr_10bit = np.asarray(result.image, dtype=np.float64) * (1023.0 / 255.0)
            self.assertGreaterEqual(float(np.min(arr_10bit)), 250)
            self.assertLessEqual(float(np.max(arr_10bit)), 760)
        finally:
            base_path.unlink()
            gainmap_path.unlink()

    def test_best_source_uses_rgb_gainmap_when_dng_is_absent(self):
        base_path = _make_test_image(320, 240)
        gainmap_path = _make_test_gainmap(160, 120)
        try:
            result = generate_linearthumbnail_from_best_source(
                base_path=base_path,
                gainmap_path=gainmap_path,
                max_dim=128,
                gainmap_mode="image",
            )
            self.assertEqual(result.stats["source_priority"], "P1-rgb-gainmap-metadata-aware")
            self.assertEqual(result.stats["gainmap_source_mode"], "image-rgb")
            self.assertEqual(result.stats["selection_decisions"][-1]["priority"], "P1")
        finally:
            base_path.unlink()
            gainmap_path.unlink()

    def test_best_source_marks_mono_gainmap_as_fallback(self):
        base_path = _make_test_image(320, 240)
        gainmap_path = _make_test_gainmap(160, 120, mono=True)
        try:
            result = generate_linearthumbnail_from_best_source(
                base_path=base_path,
                gainmap_path=gainmap_path,
                max_dim=128,
                gainmap_mode="image",
            )
            self.assertEqual(result.stats["source_priority"], "P2-mono-gainmap-fallback")
            self.assertEqual(result.stats["source_confidence"], "luma-headroom-only-fallback, no-chroma-recovery")
        finally:
            base_path.unlink()
            gainmap_path.unlink()


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

    def test_generates_styledeltamap_from_rgb_gainmap(self):
        gainmap_path = _make_test_gainmap(64, 48)
        try:
            result = generate_styledeltamap_from_gainmap(
                gainmap_path,
                width=128,
                height=96,
                amplitude=4.0,
                gainmap_mode="image",
            )
            arr = np.asarray(result.image)
            self.assertEqual(arr.shape, (96, 128, 3))
            self.assertEqual(result.stats["mode"], "gainmap_styledeltamap")
            self.assertGreater(result.stats["unique_values"], 8)
            self.assertTrue(all(120 <= v <= 136 for v in result.stats["mean"]))
        finally:
            gainmap_path.unlink()

    def test_generates_dithered_styledeltamap_from_mono_gainmap(self):
        gainmap_path = _make_test_gainmap(64, 48, mono=True)
        try:
            result = generate_styledeltamap_from_gainmap(
                gainmap_path,
                width=64,
                height=48,
                amplitude=2.0,
                gainmap_mode="image",
            )
            arr = np.asarray(result.image)
            self.assertEqual(arr.shape, (48, 64, 3))
            self.assertGreater(result.stats["unique_values"], 2)
            self.assertTrue(np.all(arr[..., 0] == arr[..., 1]))
            self.assertTrue(np.all(arr[..., 1] == arr[..., 2]))
        finally:
            gainmap_path.unlink()


if __name__ == "__main__":
    unittest.main()
