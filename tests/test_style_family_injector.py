import tempfile
import unittest
import json
from pathlib import Path

from tools.heif_dump import parse_file
from tools.hevc10_encoder import payload_and_hvcc_from_annexb_hevc
from tools.inject_style_family import (
    _build_item_id_map,
    _required_base_hdr_roles,
    inject_style_family,
    load_heif,
    style_family_item_ids,
)


BASE_SIPS_FULL = Path("artifacts/constructed/apple_parity_styledeltamap/IMG_0342_preview_sips.heic")
BASE_SIPS_4032 = Path("/private/tmp/IMG_0342_preview_sips_4032.heic")
BASE_INJECTED_V1 = Path(
    "artifacts/constructed/apple_style_injected_from_preview_heic_v1/"
    "apple_style_injected_from_preview_heic_v1.heic"
)
DONOR_V8 = Path(
    "artifacts/constructed/apple_parity_styledeltamap_v8_vt_linearthumb_q025/"
    "apple_parity_styledeltamap_v8_vt_linearthumb_q025.heic"
)
REPLACEMENT_LINEARTHUMB_HEVC = Path("artifacts/constructed/apple_parity_styledeltamap_v7_vt_linearthumb/linearthumbnail_vt.hevc")
PREVIEW_JPEG = Path("/Users/retriedstormtrooper/Downloads/03_图片素材/RAW_DNG照片/RAW_DNG_JPEG_批量导出/IMG_0342_preview.jpg")
TEMPLATE = Path("Apple_Native_Samples/IMG_0032.HEIC")
HDR_TARGET_IMG_2911 = Path("Apple_Native_Samples/IMG_2911.HEIC")


class StyleFamilyInjectorTests(unittest.TestCase):
    @unittest.skipUnless(HDR_TARGET_IMG_2911.exists() and DONOR_V8.exists(), "HDR target or donor missing")
    def test_preserve_base_allocator_skips_entity_group_ids(self):
        base = load_heif(HDR_TARGET_IMG_2911)
        donor = load_heif(DONOR_V8)
        base_hdr_roles = _required_base_hdr_roles(base)
        donor_family = style_family_item_ids(donor, include_hdr_family=False)
        donor_item_ids = list(donor_family["item_ids"])  # type: ignore[arg-type]
        id_map = _build_item_id_map(
            base,
            donor,
            donor_item_ids,
            role_item_id_map={int(donor_family["tmap"]): base_hdr_roles["tmap"]},
        )

        remapped_item_ids = {id_map[item_id] for item_id in donor_item_ids}
        self.assertFalse(remapped_item_ids & base.entity_group_ids)
        self.assertEqual(min(remapped_item_ids), 68)

    @unittest.skipUnless(HDR_TARGET_IMG_2911.exists() and DONOR_V8.exists(), "HDR target or donor missing")
    def test_preserve_base_hdr_family_preserves_target_ftyp_for_hdr_target(self):
        with tempfile.TemporaryDirectory(prefix="style_inject_preserve_hdr_target_", dir="/private/tmp") as tmpdir:
            output = Path(tmpdir) / "preserve_hdr_target.heic"
            report = Path(tmpdir) / "preserve_hdr_target.report.json"
            base = load_heif(HDR_TARGET_IMG_2911)

            inject_style_family(
                HDR_TARGET_IMG_2911,
                DONOR_V8,
                output_path=output,
                preserve_base_hdr_family=True,
                preservation_report_path=report,
            )

            injected = load_heif(output)
            base_ftyp = base.data[base.ftyp_box["offset"] : base.ftyp_box["offset"] + base.ftyp_box["size"]]
            injected_ftyp = injected.data[
                injected.ftyp_box["offset"] : injected.ftyp_box["offset"] + injected.ftyp_box["size"]
            ]
            self.assertEqual(injected_ftyp, base_ftyp)
            report_data = json.loads(report.read_text())
            container = report_data["container_preservation"]
            self.assertEqual(container["base"]["entity_group_ids"], [67])
            self.assertEqual(container["output"]["id_collisions_with_entity_groups"], [])
            self.assertIn("meta_child_order", container["base"])
            self.assertIn("changed_base_item_iloc_records", container)

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

    @unittest.skipUnless(BASE_INJECTED_V1.exists() and DONOR_V8.exists(), "preserve-base target or donor missing")
    def test_preserve_base_hdr_family_reuses_target_gainmap_and_tmap_payloads(self):
        with tempfile.TemporaryDirectory(prefix="style_inject_preserve_hdr_", dir="/private/tmp") as tmpdir:
            output = Path(tmpdir) / "preserve_hdr.heic"
            base = load_heif(BASE_INJECTED_V1)
            base_gainmap_id = next(
                int(item_id)
                for item_id, item in base.parsed["items"].items()
                if item.get("aux_type") == "urn:com:apple:photo:2020:aux:hdrgainmap"
            )
            base_tmap_id = next(
                int(item_id)
                for item_id, item in base.parsed["items"].items()
                if item.get("item_type") == "tmap"
            )

            summary = inject_style_family(
                BASE_INJECTED_V1,
                DONOR_V8,
                output_path=output,
                preserve_base_hdr_family=True,
            )

            self.assertTrue(summary["preserve_base_hdr_family"])
            self.assertTrue(summary["reused_base_hdr_graph"])
            self.assertFalse(summary["copied_donor_hdr_family"])
            self.assertEqual(summary["gainmap_item_id"], base_gainmap_id)
            self.assertEqual(summary["tmap_item_id"], base_tmap_id)

            injected = load_heif(output)
            self.assertEqual(
                injected.data[injected.ftyp_box["offset"] : injected.ftyp_box["offset"] + injected.ftyp_box["size"]],
                base.data[base.ftyp_box["offset"] : base.ftyp_box["offset"] + base.ftyp_box["size"]],
            )
            self.assertEqual(injected.item_payloads[base_gainmap_id], base.item_payloads[base_gainmap_id])
            self.assertEqual(injected.item_payloads[base_tmap_id], base.item_payloads[base_tmap_id])

            styledelta = injected.parsed["items"][str(summary["styledeltamap_item_id"])]
            linearthumb = injected.parsed["items"][str(summary["linearthumbnail_item_id"])]
            expected_refs = {"type": "auxl", "to_item_ids": [base.parsed["primary_item_id"], base_tmap_id]}
            self.assertIn(expected_refs, styledelta["references_from"])
            self.assertIn(expected_refs, linearthumb["references_from"])

            report = output.parent / "style_injection_preservation_report.json"
            self.assertTrue(report.exists())
