import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

from tools.apple_native_sample_inventory import (
    HDR_GAINMAP_AUX_TYPE,
    LINEARTHUMB_AUX_TYPE,
    SEMANTIC_SKY_MATTE_AUX_TYPE,
    STYLE_DELTA_AUX_TYPE,
    STYLE_METADATA_URI_TYPE,
    build_structure_signature,
    classify_unknown_items,
    compute_decoded_image_stats,
    extract_role_item_ids,
)


class AppleNativeSampleInventoryTests(unittest.TestCase):
    def _parsed_sample(self):
        return {
            "primary_item_id": 49,
            "ftyp": {
                "major_brand": "heic",
                "compatible_brands": ["mif1", "heic", "miaf", "tmap"],
            },
            "items": {
                "49": {
                    "item_id": 49,
                    "item_type": "grid",
                    "dimensions": {"width": 4032, "height": 3024},
                    "pixi": {"channels": 3, "bits": [8, 8, 8]},
                    "references_from": [{"type": "dimg", "to_item_ids": [1, 2]}],
                },
                "81": {
                    "item_id": 81,
                    "item_type": "grid",
                    "aux_type": STYLE_DELTA_AUX_TYPE,
                    "dimensions": {"width": 2880, "height": 2160},
                    "pixi": {"channels": 3, "bits": [10, 10, 10]},
                    "references_from": [{"type": "auxl", "to_item_ids": [49, 100]}],
                },
                "94": {
                    "item_id": 94,
                    "item_type": "grid",
                    "aux_type": HDR_GAINMAP_AUX_TYPE,
                    "dimensions": {"width": 2016, "height": 1512},
                    "pixi": {"channels": 1, "bits": [8]},
                },
                "95": {
                    "item_id": 95,
                    "item_type": "hvc1",
                    "aux_type": SEMANTIC_SKY_MATTE_AUX_TYPE,
                    "dimensions": {"width": 2016, "height": 1512},
                    "pixi": {"channels": 1, "bits": [8]},
                },
                "97": {
                    "item_id": 97,
                    "item_type": "hvc1",
                    "aux_type": LINEARTHUMB_AUX_TYPE,
                    "dimensions": {"width": 1024, "height": 768},
                    "pixi": {"channels": 3, "bits": [10, 10, 10]},
                },
                "100": {"item_id": 100, "item_type": "tmap"},
                "101": {
                    "item_id": 101,
                    "item_type": "uri ",
                    "uri_type": STYLE_METADATA_URI_TYPE,
                },
                "102": {"item_id": 102, "item_type": "Exif"},
                "120": {"item_id": 120, "item_type": "mime", "content_type": "application/octet-stream"},
            },
            "references": [
                {"type": "dimg", "from_item_id": 49, "to_item_ids": [1, 2]},
                {"type": "auxl", "from_item_id": 81, "to_item_ids": [49, 100]},
                {"type": "cdsc", "from_item_id": 101, "to_item_ids": [49, 100]},
            ],
        }

    def test_extract_role_item_ids_finds_style_family_roles(self):
        roles = extract_role_item_ids(self._parsed_sample())

        self.assertEqual(roles["primary"], 49)
        self.assertEqual(roles["styledeltamap"], 81)
        self.assertEqual(roles["hdr_gain_map"], 94)
        self.assertEqual(roles["semantic_sky_matte"], 95)
        self.assertEqual(roles["linearthumbnail"], 97)
        self.assertEqual(roles["tmap"], 100)
        self.assertEqual(roles["style_metadata"], 101)
        self.assertEqual(roles["exif"], 102)

    def test_compute_decoded_image_stats_reports_neutrality_and_low_frequency(self):
        data = np.full((8, 8, 3), 128, dtype=np.uint8)
        data[:4, :, 0] = 126
        data[4:, :, 0] = 130
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "styledeltamap.png"
            Image.fromarray(data, "RGB").save(path)

            stats = compute_decoded_image_stats(path, neutral_value=128)

        self.assertEqual(stats["size"], {"width": 8, "height": 8})
        self.assertEqual(stats["median"], [128.0, 128.0, 128.0])
        self.assertEqual(stats["neutral_abs_mean_offset"], [2.0, 0.0, 0.0])
        self.assertGreater(stats["low_frequency_energy_ratio"], 0.5)
        self.assertFalse(stats["is_constant"])

    def test_structure_signature_and_unknown_items_are_stable(self):
        parsed = self._parsed_sample()

        signature = build_structure_signature(parsed)
        unknown = classify_unknown_items(parsed, extract_role_item_ids(parsed))

        self.assertEqual(signature["item_count"], 9)
        self.assertEqual(signature["aux_types"], [HDR_GAINMAP_AUX_TYPE, LINEARTHUMB_AUX_TYPE, SEMANTIC_SKY_MATTE_AUX_TYPE, STYLE_DELTA_AUX_TYPE])
        self.assertEqual(signature["reference_types"], ["auxl", "cdsc", "dimg"])
        self.assertEqual(unknown[0]["item_id"], 120)
        self.assertEqual(unknown[0]["item_type"], "mime")


if __name__ == "__main__":
    unittest.main()
