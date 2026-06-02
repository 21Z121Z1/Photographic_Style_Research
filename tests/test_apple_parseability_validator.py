import json
import unittest

from tools.validate_apple_parseability import parse_imageio_result, parse_sips_result, summarize_hard_failures


class AppleParseabilityValidatorTests(unittest.TestCase):
    def test_parse_sips_result_extracts_dimensions(self):
        parsed = parse_sips_result(
            "/tmp/sample.heic\n"
            "  pixelWidth: 4284\n"
            "  pixelHeight: 5712\n"
            "  format: heic\n"
        )

        self.assertEqual(parsed["pixelWidth"], 4284)
        self.assertEqual(parsed["pixelHeight"], 5712)
        self.assertEqual(parsed["format"], "heic")
        self.assertTrue(parsed["ok"])

    def test_parse_sips_result_marks_nil_dimensions_failed(self):
        parsed = parse_sips_result(
            "/tmp/sample.heic\n"
            "  pixelWidth: <nil>\n"
            "  pixelHeight: <nil>\n"
            "  format: heic\n"
        )

        self.assertIsNone(parsed["pixelWidth"])
        self.assertIsNone(parsed["pixelHeight"])
        self.assertFalse(parsed["ok"])

    def test_parse_imageio_result_reads_swift_json(self):
        parsed = parse_imageio_result(json.dumps({"ok": True, "count": 1, "pixelWidth": 10, "pixelHeight": 20}))

        self.assertTrue(parsed["ok"])
        self.assertEqual(parsed["count"], 1)
        self.assertEqual(parsed["pixelWidth"], 10)

    def test_hard_failures_include_apple_native_gates(self):
        failures = summarize_hard_failures(
            {
                "heif_info": {"exit_code": 0},
                "sips": {"parsed": {"ok": False}},
                "imageio": {"parsed": {"ok": False}},
                "quicklook": {"skipped": False, "thumbnail_created": False},
            }
        )

        self.assertEqual(
            failures,
            [
                "sips did not report primary pixel dimensions",
                "ImageIO validator did not decode the primary image",
                "QuickLook did not create a thumbnail",
            ],
        )


if __name__ == "__main__":
    unittest.main()
