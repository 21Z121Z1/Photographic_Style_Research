import unittest

from tools.heif_aux_writer import EncodedImage, build_styledeltamap_heif, grid_payload
from tools.heif_dump import STYLE_DELTA_AUX_TYPE, parse_heif


def fake_hvcc(bit_depth: int = 8) -> bytes:
    payload = bytearray(23)
    payload[0] = 1
    payload[1] = 3
    payload[12] = 30
    payload[16] = 0xFC | 1
    payload[17] = 0xF8 | (bit_depth - 8)
    payload[18] = 0xF8 | (bit_depth - 8)
    payload[21] = 0x08
    payload[22] = 3
    return bytes(payload)


class HeifAuxWriterTests(unittest.TestCase):
    def test_grid_payload_matches_heif_derived_grid_shape(self):
        self.assertEqual(grid_payload(rows=2, columns=3, width=1024, height=768), b"\0\0\x01\x02\x04\0\x03\0")

    def test_builds_styledeltamap_grid_auxiliary_item_graph(self):
        primary = EncodedImage(
            payload=b"primary-hevc",
            hvcc=fake_hvcc(),
            width=1024,
            height=768,
            pixi_bits=(8, 8, 8),
        )
        tiles = [
            EncodedImage(
                payload=f"tile-{index}".encode("ascii"),
                hvcc=fake_hvcc(),
                width=512,
                height=512,
                pixi_bits=(8, 8, 8),
            )
            for index in range(4)
        ]

        parsed = parse_heif(
            build_styledeltamap_heif(
                primary=primary,
                style_tiles=tiles,
                grid_width=1024,
                grid_height=768,
                grid_rows=2,
                grid_columns=2,
            )
        )

        self.assertEqual(parsed["ftyp"]["major_brand"], "heic")
        self.assertIn("mif1", parsed["ftyp"]["compatible_brands"])
        self.assertIn("heic", parsed["ftyp"]["compatible_brands"])
        self.assertEqual(parsed["handler"]["handler_type"], "pict")
        self.assertEqual(parsed["primary_item_id"], 1)
        self.assertEqual(parsed["items"]["1"]["item_type"], "hvc1")
        self.assertIn("hvcC", parsed["items"]["1"])
        self.assertIn("colr", parsed["items"]["1"])
        self.assertEqual(parsed["items"]["2"]["item_type"], "grid")
        self.assertEqual(
            parsed["items"]["2"]["grid"],
            {
                "version": 0,
                "flags": 0,
                "rows": 2,
                "columns": 2,
                "output_width": 1024,
                "output_height": 768,
            },
        )
        self.assertTrue(parsed["items"]["2"]["hidden"])
        self.assertIn("colr", parsed["items"]["2"])
        self.assertEqual(parsed["items"]["2"]["aux_type"], STYLE_DELTA_AUX_TYPE)
        self.assertEqual(parsed["items"]["2"]["derived_child_item_ids"], [3, 4, 5, 6])
        self.assertIn("hvcC", parsed["items"]["3"])
        self.assertIn("colr", parsed["items"]["3"])
        self.assertEqual(
            [ref for ref in parsed["references"] if ref["type"] == "auxl"],
            [
                {
                    "version": 0,
                    "flags": 0,
                    "type": "auxl",
                    "from_item_id": 2,
                    "to_item_ids": [1],
                }
            ],
        )
        self.assertEqual(parsed["styledeltamap"]["aux_type"], STYLE_DELTA_AUX_TYPE)
        self.assertEqual(parsed["styledeltamap"]["derived_child_count"], 4)


if __name__ == "__main__":
    unittest.main()
