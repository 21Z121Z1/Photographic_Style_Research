import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

from tools.heif_dump import parse_file


APPLE_TEMPLATE = Path("Apple_Native_Samples/IMG_0032.HEIC")


class StyleSpatialAblationTests(unittest.TestCase):
    def test_role_inventory_finds_expected_apple_template_items(self):
        from tools.style_spatial_ablation import build_role_inventory

        inventory = build_role_inventory(APPLE_TEMPLATE)

        self.assertEqual(inventory["primary"].item_id, 49)
        self.assertEqual(inventory["styledeltamap"].item_id, 81)
        self.assertEqual(inventory["hdrgainmap"].item_id, 94)
        self.assertEqual(inventory["semanticskymatte"].item_id, 95)
        self.assertEqual(inventory["linearthumbnail"].item_id, 97)
        self.assertEqual(inventory["tmap"].item_id, 100)
        self.assertEqual(inventory["style_metadata"].item_id, 101)
        self.assertEqual(inventory["exif"].item_id, 102)

    def test_manifest_entry_records_manual_photos_fields(self):
        from tools.style_spatial_ablation import build_manual_photos_fields, manifest_entry

        entry = manifest_entry(
            name="neutral_linearthumb_only",
            output=Path("out/neutral_linearthumb_only.heic"),
            perturbation="neutral",
            changed_roles=["linearthumbnail"],
            validation={"heif_dump": {"ok": True}},
        )

        self.assertEqual(entry["name"], "neutral_linearthumb_only")
        self.assertEqual(entry["changed_roles"], ["linearthumbnail"])
        self.assertEqual(entry["manual_photos_verification"], build_manual_photos_fields())

    def test_payload_hash_summary_marks_changed_and_preserved_roles(self):
        from tools.style_spatial_ablation import compare_role_hashes

        before = {"primary": "aaa", "linearthumbnail": "bbb"}
        after = {"primary": "aaa", "linearthumbnail": "ccc"}

        self.assertEqual(
            compare_role_hashes(before, after),
            {
                "primary": {"before": "aaa", "after": "aaa", "changed": False},
                "linearthumbnail": {"before": "bbb", "after": "ccc", "changed": True},
            },
        )

    def test_baseline_copy_is_byte_identical(self):
        from tools.style_spatial_ablation import copy_baseline_variant

        with tempfile.TemporaryDirectory(prefix="style_ablation_test_") as tmpdir:
            output = Path(tmpdir) / "baseline_original.heic"

            copy_baseline_variant(APPLE_TEMPLATE, output)

            self.assertEqual(output.read_bytes(), APPLE_TEMPLATE.read_bytes())

    def test_neutral_rgb_image_has_one_value(self):
        from tools.style_spatial_ablation import neutral_rgb_image

        image = neutral_rgb_image((12, 8), value=127)
        arr = np.asarray(image)

        self.assertEqual(image.mode, "RGB")
        self.assertEqual(image.size, (12, 8))
        self.assertEqual(np.unique(arr.reshape(-1, 3), axis=0).tolist(), [[127, 127, 127]])

    def test_shift_image_x_wraps_pixels(self):
        from tools.style_spatial_ablation import shift_image_x

        image = Image.new("L", (4, 1), 0)
        image.putpixel((0, 0), 10)
        image.putpixel((1, 0), 20)
        image.putpixel((2, 0), 30)
        image.putpixel((3, 0), 40)

        shifted = shift_image_x(image, 1)

        self.assertEqual([shifted.getpixel((x, 0)) for x in range(4)], [40, 10, 20, 30])

    def test_replacing_payload_rewrites_item_length(self):
        from tools.style_spatial_ablation import build_role_inventory, write_with_replaced_payloads

        inventory = build_role_inventory(APPLE_TEMPLATE)
        replacement = b"bplist-ablation-test"

        with tempfile.TemporaryDirectory(prefix="style_ablation_payload_") as tmpdir:
            output = Path(tmpdir) / "style_metadata_replaced.heic"
            write_with_replaced_payloads(
                APPLE_TEMPLATE,
                output,
                {inventory["style_metadata"].item_id: replacement},
            )

            parsed = parse_file(output)
            item = parsed["items"][str(inventory["style_metadata"].item_id)]
            self.assertEqual(item["extents"][0]["length"], len(replacement))


if __name__ == "__main__":
    unittest.main()
