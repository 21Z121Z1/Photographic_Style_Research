import tempfile
import unittest
from pathlib import Path

from tools.heif_dump import parse_file
from tools.hevc10_encoder import payload_and_hvcc_from_annexb_hevc
from tools.inject_style_family import inject_style_family, load_heif


BASE_SIPS_FULL = Path("artifacts/constructed/apple_parity_styledeltamap/IMG_0342_preview_sips.heic")
BASE_SIPS_4032 = Path("/private/tmp/IMG_0342_preview_sips_4032.heic")
DONOR_V8 = Path(
    "artifacts/constructed/apple_parity_styledeltamap_v8_vt_linearthumb_q025/"
    "apple_parity_styledeltamap_v8_vt_linearthumb_q025.heic"
)
REPLACEMENT_LINEARTHUMB_HEVC = Path("artifacts/constructed/apple_parity_styledeltamap_v7_vt_linearthumb/linearthumbnail_vt.hevc")
PREVIEW_JPEG = Path("/Users/retriedstormtrooper/Downloads/03_图片素材/RAW_DNG照片/RAW_DNG_JPEG_批量导出/IMG_0342_preview.jpg")
TEMPLATE = Path("Apple_Native_Samples/IMG_0032.HEIC")


class StyleFamilyInjectorTests(unittest.TestCase):
    @unittest.skipUnless(BASE_SIPS_FULL.exists() and DONOR_V8.exists(), "base or donor artifact missing")
    def test_rejects_dimension_mismatch_between_base_primary_and_donor_tmap(self):
        with self.assertRaisesRegex(ValueError, "primary dimensions"):
            inject_style_family(BASE_SIPS_FULL, DONOR_V8)

    @unittest.skipUnless(BASE_SIPS_4032.exists() and DONOR_V8.exists(), "compatible sips base or donor missing")
    def test_injects_style_family_with_remapped_references(self):
        with tempfile.TemporaryDirectory(prefix="style_inject_test_", dir="/private/tmp") as tmpdir:
            output = Path(tmpdir) / "injected.heic"
            summary = inject_style_family(
                BASE_SIPS_4032,
                DONOR_V8,
                output_path=output,
                preview_jpeg=PREVIEW_JPEG,
                exif_template=TEMPLATE,
            )

            parsed = parse_file(output)
            primary_id = parsed["primary_item_id"]
            self.assertEqual(primary_id, 49)
            self.assertEqual(summary["base_primary_item_id"], primary_id)
            self.assertGreater(summary["injected_item_count"], 0)

            item_ids = [int(item_id) for item_id in parsed["items"]]
            self.assertEqual(len(item_ids), len(set(item_ids)))

            styledelta = parsed["items"][str(summary["styledeltamap_item_id"])]
            self.assertEqual(styledelta["item_type"], "grid")
            self.assertEqual(styledelta["aux_type"], "tag:apple.com,2023:photo:aux:styledeltamap")
            self.assertIn(
                {"type": "auxl", "to_item_ids": [primary_id, summary["tmap_item_id"]]},
                styledelta["references_from"],
            )

            linearthumb = parsed["items"][str(summary["linearthumbnail_item_id"])]
            self.assertEqual(linearthumb["item_type"], "hvc1")
            self.assertEqual(linearthumb["aux_type"], "tag:apple.com,2023:photo:aux:linearthumbnail")
            self.assertEqual(linearthumb["hvcC"]["bytes"], 105)
            self.assertIn(
                {"type": "auxl", "to_item_ids": [primary_id, summary["tmap_item_id"]]},
                linearthumb["references_from"],
            )

            tmap = parsed["items"][str(summary["tmap_item_id"])]
            self.assertEqual(tmap["item_type"], "tmap")
            self.assertIn(
                {"type": "dimg", "to_item_ids": [primary_id, summary["gainmap_item_id"]]},
                tmap["references_from"],
            )

            exif = parsed["items"][str(summary["base_exif_item_id"])]
            self.assertIn(
                {"type": "cdsc", "to_item_ids": [primary_id, summary["tmap_item_id"]]},
                exif["references_from"],
            )

    @unittest.skipUnless(
        BASE_SIPS_4032.exists() and DONOR_V8.exists() and REPLACEMENT_LINEARTHUMB_HEVC.exists(),
        "compatible base, donor, or replacement HEVC missing",
    )
    def test_can_replace_linearthumbnail_payload_and_hvcc(self):
        with tempfile.TemporaryDirectory(prefix="style_inject_replace_lt_", dir="/private/tmp") as tmpdir:
            output = Path(tmpdir) / "injected_replace_lt.heic"
            expected_payload, expected_hvcc = payload_and_hvcc_from_annexb_hevc(
                REPLACEMENT_LINEARTHUMB_HEVC.read_bytes(),
                item_payload_policy="single_idr",
            )
            summary = inject_style_family(
                BASE_SIPS_4032,
                DONOR_V8,
                output_path=output,
                preview_jpeg=PREVIEW_JPEG,
                exif_template=TEMPLATE,
                replace_linearthumb_hevc=REPLACEMENT_LINEARTHUMB_HEVC,
            )

            self.assertTrue(summary["replaced_linearthumbnail"])
            self.assertEqual(summary["replacement_linearthumbnail_payload_bytes"], len(expected_payload))
            self.assertEqual(summary["replacement_linearthumbnail_hvcc_bytes"], len(expected_hvcc))

            injected = load_heif(output)
            linearthumb_id = int(summary["linearthumbnail_item_id"])
            self.assertEqual(injected.item_payloads[linearthumb_id], expected_payload)

            parsed = parse_file(output)
            linearthumb = parsed["items"][str(linearthumb_id)]
            self.assertEqual(linearthumb["hvcC"]["bytes"], len(expected_hvcc))
