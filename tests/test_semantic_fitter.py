import unittest
from pathlib import Path

from tools.semantic_fitter import build_report


V3C = Path("artifacts/constructed/apple_parity_styledeltamap_v3c/apple_parity_styledeltamap_v3c.heic")
V4 = Path("artifacts/constructed/apple_parity_styledeltamap_v4/apple_parity_styledeltamap_v4.heic")
V5 = Path("artifacts/constructed/apple_parity_styledeltamap_v5/apple_parity_styledeltamap_v5.heic")
TEMPLATE = Path("Apple_Native_Samples/IMG_0032.HEIC")


class SemanticFitterReportTests(unittest.TestCase):
    @unittest.skipUnless(V3C.exists() and V4.exists(), "v3c/v4 artifacts not available")
    def test_v4_report_flags_malformed_irot_regression(self):
        report = build_report(V4, reference_path=V3C, template_path=TEMPLATE)

        self.assertTrue(any("irot property 4" in warning for warning in report["hard_warnings"]))
        self.assertTrue(report["comparisons"]["reference"]["payload_hash_equal"]["101"])
        self.assertFalse(report["comparisons"]["reference"]["payload_hash_equal"]["97"])

    @unittest.skipUnless(V3C.exists(), "v3c artifact not available")
    def test_v3c_report_has_valid_irot_payloads(self):
        report = build_report(V3C, template_path=TEMPLATE)

        self.assertFalse(report["hard_warnings"])
        self.assertEqual(report["key_items"]["81"]["aux_type"], "tag:apple.com,2023:photo:aux:styledeltamap")

    def test_template_report_includes_linearthumbnail_hevc_profile(self):
        report = build_report(TEMPLATE)
        linearthumb = report["key_items"]["97"]

        self.assertEqual(linearthumb["hevc_nals"]["nal_types"], [20])
        self.assertEqual(linearthumb["hevc_nals"]["nal_count"], 1)
        self.assertEqual(linearthumb["hvcC_raw"]["bytes"], 105)
        self.assertIn({"type": "auxl", "to_item_ids": [49, 100]}, linearthumb["references_from"])

    @unittest.skipUnless(V5.exists(), "v5 artifact not available")
    def test_v5_report_flags_multi_nal_linearthumbnail_regression(self):
        report = build_report(V5, template_path=TEMPLATE)
        linearthumb = report["key_items"]["97"]

        self.assertIn(32, linearthumb["hevc_nals"]["nal_types"])
        self.assertTrue(
            any("linearthumbnail item payload" in warning for warning in report["hard_warnings"]),
            report["hard_warnings"],
        )


if __name__ == "__main__":
    unittest.main()
