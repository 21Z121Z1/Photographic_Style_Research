import unittest
import os
import shutil
from pathlib import Path

from tools.apple_template_writer import (
    Hevc10Tile,
    LINTHUMB_HVCC_PROPERTY_INDEX,
    ReplacementTile,
    _load_template,
    build_apple_template_parity_heif,
    prepare_primary_grid_tiles,
    prepare_styledeltamap_tiles,
)
from tools.heif_dump import STYLE_DELTA_AUX_TYPE, parse_file, parse_heif
from tools.hevc10_encoder import encode_hevc10_still_videotoolbox, encode_hevc10_tile, parse_length_prefixed_nals


APPLE_SAMPLE = Path("Apple_Native_Samples/IMG_0032.HEIC")
PREVIOUS_ARTIFACT = Path("artifacts/constructed/iso_aux_styledeltamap/iso_aux_styledeltamap.heic")


def assert_apple_parity_features(testcase: unittest.TestCase, parsed: dict) -> None:
    primary_id = str(parsed["primary_item_id"])
    primary = parsed["items"][primary_id]
    testcase.assertEqual(primary["item_type"], "grid")
    testcase.assertEqual(primary["dimensions"], {"width": 4032, "height": 3024})
    testcase.assertEqual(primary["pixi"], {"channels": 3, "bits": [8, 8, 8]})
    testcase.assertEqual(len(primary["derived_child_item_ids"]), 48)

    styledelta = parsed["styledeltamap"]
    style_id = str(styledelta["item_id"])
    style_item = parsed["items"][style_id]
    testcase.assertEqual(style_item["item_type"], "grid")
    testcase.assertTrue(style_item["hidden"])
    testcase.assertEqual(style_item["aux_type"], STYLE_DELTA_AUX_TYPE)
    testcase.assertEqual(style_item["pixi"], {"channels": 3, "bits": [10, 10, 10]})
    testcase.assertEqual(style_item["grid"]["rows"], 5)
    testcase.assertEqual(style_item["grid"]["columns"], 6)
    testcase.assertEqual(len(style_item["derived_child_item_ids"]), 30)

    refs = {(ref["type"], ref["from_item_id"]): ref["to_item_ids"] for ref in parsed["references"]}
    testcase.assertEqual(refs[("auxl", int(style_id))], [int(primary_id), 100])
    testcase.assertEqual(refs[("dimg", 100)], [int(primary_id), 94])
    testcase.assertEqual(len(refs[("dimg", 94)]), 12)

    testcase.assertEqual(parsed["items"]["94"]["aux_type"], "urn:com:apple:photo:2020:aux:hdrgainmap")
    testcase.assertEqual(
        parsed["items"]["94"]["grid"],
        {
            "version": 0,
            "flags": 0,
            "rows": 3,
            "columns": 4,
            "output_width": 2016,
            "output_height": 1512,
        },
    )
    testcase.assertEqual(parsed["items"]["100"]["item_type"], "tmap")
    testcase.assertEqual(parsed["items"]["100"]["tmap"], {"payload_bytes": 62})
    testcase.assertEqual(parsed["items"]["101"]["item_type"], "uri ")
    testcase.assertEqual(parsed["items"]["101"]["uri_type"], "tag:apple.com,2023:photo:metadata:styles")
    testcase.assertEqual(parsed["items"]["102"]["item_type"], "Exif")
    testcase.assertEqual(refs[("cdsc", 101)], [int(primary_id), 100])
    testcase.assertEqual(refs[("cdsc", 102)], [int(primary_id), 100])


def item_payload(path: Path, item_id: str) -> bytes:
    parsed = parse_file(path)
    data = path.read_bytes()
    item = parsed["items"][item_id]
    payload = bytearray()
    for extent in item.get("extents", []):
        offset = extent.get("absolute_offset", extent.get("offset", 0))
        payload.extend(data[offset : offset + extent["length"]])
    return bytes(payload)


class AppleTemplateWriterTests(unittest.TestCase):
    def test_previous_iso_aux_artifact_is_missing_apple_parity_families(self):
        parsed = parse_file(PREVIOUS_ARTIFACT)

        with self.assertRaises(AssertionError):
            assert_apple_parity_features(self, parsed)

    def test_apple_native_sample_satisfies_parity_feature_contract(self):
        parsed = parse_file(APPLE_SAMPLE)

        assert_apple_parity_features(self, parsed)

    def test_apple_native_linearthumbnail_payload_is_single_idr_nal(self):
        payload = item_payload(APPLE_SAMPLE, "97")
        nals = parse_length_prefixed_nals(payload)

        self.assertEqual([nal.nal_type for nal in nals], [20])
        self.assertEqual(len(nals[0].payload), len(payload) - 4)

    def test_apple_native_linearthumbnail_hvcc_is_stable_main10_record(self):
        template = _load_template(APPLE_SAMPLE)
        hvcc_box = template.ipco_property_boxes[LINTHUMB_HVCC_PROPERTY_INDEX - 1]
        self.assertEqual(hvcc_box[4:8], b"hvcC")
        hvcc = hvcc_box[8:]

        self.assertEqual(len(hvcc), 105)
        self.assertEqual(hvcc[0], 1)
        self.assertEqual(hvcc[1] & 0x1F, 2)
        self.assertEqual(hvcc[12], 93)

    def test_builds_apple_template_parity_graph_with_replacement_primary_tiles(self):
        replacement_tiles = [
            ReplacementTile(payload=f"tile-{index}".encode("ascii"), hvcc=fake_hvcc(level_idc=90))
            for index in range(48)
        ]

        parsed = parse_heif(
            build_apple_template_parity_heif(
                template_path=APPLE_SAMPLE,
                primary_tiles=replacement_tiles,
            )
        )

        assert_apple_parity_features(self, parsed)
        self.assertEqual(parsed["items"]["1"]["extents"][0]["length"], len(b"tile-0"))
        self.assertEqual(parsed["items"]["48"]["extents"][0]["length"], len(b"tile-47"))
        self.assertEqual(parsed["items"]["1"]["hvcC"]["bit_depth_luma"], 8)

    def test_builds_apple_template_parity_graph_with_replacement_gainmap_tiles(self):
        replacement_tiles = [
            ReplacementTile(payload=f"tile-{index}".encode("ascii"), hvcc=fake_hvcc(level_idc=90))
            for index in range(48)
        ]
        gainmap_tiles = [
            ReplacementTile(payload=f"gm-{index}".encode("ascii"), hvcc=fake_hvcc(level_idc=77))
            for index in range(12)
        ]

        parsed = parse_heif(
            build_apple_template_parity_heif(
                template_path=APPLE_SAMPLE,
                primary_tiles=replacement_tiles,
                gainmap_tiles=gainmap_tiles,
            )
        )

        assert_apple_parity_features(self, parsed)
        self.assertEqual(parsed["items"]["82"]["extents"][0]["length"], len(b"gm-0"))
        self.assertEqual(parsed["items"]["93"]["extents"][0]["length"], len(b"gm-11"))
        self.assertEqual(parsed["items"]["82"]["hvcC"]["general_level_idc"], 77)

    def test_replaces_exif_item_payload_when_provided(self):
        replacement_tiles = [
            ReplacementTile(payload=f"tile-{index}".encode("ascii"), hvcc=fake_hvcc(level_idc=90))
            for index in range(48)
        ]
        exif_payload = b"\x00\x00\x00\x06Exif\x00\x00MM\x00*\x00\x00\x00\x08"

        parsed = parse_heif(
            build_apple_template_parity_heif(
                template_path=APPLE_SAMPLE,
                primary_tiles=replacement_tiles,
                exif_item_payload=exif_payload,
            )
        )

        self.assertEqual(parsed["items"]["102"]["extents"][0]["length"], len(exif_payload))

    def test_prepare_primary_grid_tiles_matches_apple_primary_grid_shape(self):
        tiles = prepare_primary_grid_tiles(Path("NoFusion_Samples/extract_py_img_0.png"), quality=70)

        self.assertEqual(len(tiles), 48)
        self.assertTrue(all(tile.width == 512 and tile.height == 512 for tile in tiles))
        self.assertTrue(all(tile.payload for tile in tiles))
        self.assertTrue(all(tile.hvcc for tile in tiles))


def fake_hvcc(level_idc: int = 90) -> bytes:
    payload = bytearray(23)
    payload[0] = 1
    payload[1] = 3
    payload[12] = level_idc
    payload[16] = 0xFC | 1
    payload[17] = 0xF8
    payload[18] = 0xF8
    payload[21] = 0x08
    payload[22] = 3
    return bytes(payload)


class Hevc10EncoderTests(unittest.TestCase):
    def test_encode_hevc10_tile_produces_main10_hvcc(self):
        from PIL import Image

        img = Image.new("RGB", (512, 512), (128, 128, 128))
        payload, hvcc = encode_hevc10_tile(img)

        self.assertGreater(len(payload), 0)
        self.assertGreater(len(hvcc), 0)
        # hvcC starts with configurationVersion=1
        self.assertEqual(hvcc[0], 1)
        # profile_idc=2 (Main 10)
        self.assertEqual(hvcc[1] & 0x1F, 2)

    def test_encode_hevc10_tile_payload_is_length_prefixed(self):
        from PIL import Image

        img = Image.new("RGB", (512, 512), (128, 128, 128))
        payload, _ = encode_hevc10_tile(img)

        # Length-prefixed: first 4 bytes are NAL length (not 00000001 Annex B start code)
        self.assertNotEqual(payload[:4], b"\x00\x00\x00\x01")
        nal_length = int.from_bytes(payload[:4], "big")
        self.assertGreater(nal_length, 0)
        self.assertLess(nal_length, len(payload))

    def test_encode_hevc10_tile_can_emit_apple_still_item_payload(self):
        from PIL import Image

        img = Image.new("RGB", (512, 512), (128, 128, 128))
        payload, _ = encode_hevc10_tile(img, item_payload_policy="single_idr")
        nals = parse_length_prefixed_nals(payload)

        self.assertEqual(len(nals), 1)
        self.assertIn(nals[0].nal_type, (19, 20))

    def test_videotoolbox_quality_is_validated_before_subprocess(self):
        from PIL import Image

        img = Image.new("RGB", (16, 16), (128, 128, 128))
        with self.assertRaises(ValueError):
            encode_hevc10_still_videotoolbox(img, quality=0.0)
        with self.assertRaises(ValueError):
            encode_hevc10_still_videotoolbox(img, quality=1.1)

    @unittest.skipUnless(
        os.environ.get("RUN_VIDEOTOOLBOX_SUBPROCESS_TESTS") == "1"
        and shutil.which("swift")
        and shutil.which("MP4Box"),
        "VideoToolbox subprocess test is opt-in because Codex Python sandbox can block IOSurface allocation",
    )
    def test_videotoolbox_encoder_produces_apple_like_linearthumb_payload(self):
        from PIL import Image

        img = Image.new("RGB", (1024, 768), (128, 128, 128))
        payload, hvcc = encode_hevc10_still_videotoolbox(img, quality=0.25)
        nals = parse_length_prefixed_nals(payload)

        self.assertEqual(len(nals), 1)
        self.assertIn(nals[0].nal_type, (19, 20))
        self.assertEqual(len(hvcc), 105)
        self.assertEqual(hvcc[1] & 0x1F, 2)
        self.assertEqual(hvcc[12], 93)


class StyledeltaMapTileGenerationTests(unittest.TestCase):
    def test_prepare_styledeltamap_tiles_produces_30_tiles(self):
        preview = Path(
            "/Users/retriedstormtrooper/Downloads/03_图片素材/RAW_DNG照片/RAW_DNG_JPEG_批量导出/IMG_0342_preview.jpg"
        )
        if not preview.exists():
            self.skipTest("preview JPEG not available")

        tiles = prepare_styledeltamap_tiles(preview)

        self.assertEqual(len(tiles), 30)
        self.assertTrue(all(isinstance(t, Hevc10Tile) for t in tiles))
        self.assertTrue(all(len(t.payload) > 0 for t in tiles))
        self.assertTrue(all(len(t.hvcc) > 0 for t in tiles))

    def test_prepare_styledeltamap_tiles_hvcc_is_main10(self):
        preview = Path(
            "/Users/retriedstormtrooper/Downloads/03_图片素材/RAW_DNG照片/RAW_DNG_JPEG_批量导出/IMG_0342_preview.jpg"
        )
        if not preview.exists():
            self.skipTest("preview JPEG not available")

        tiles = prepare_styledeltamap_tiles(preview)
        hvcc = tiles[0].hvcc

        # profile_idc=2 (Main 10)
        self.assertEqual(hvcc[1] & 0x1F, 2)
        # All tiles share the same hvcC
        self.assertTrue(all(t.hvcc == hvcc for t in tiles))

    def test_builds_styledeltamap_with_generated_tiles(self):
        preview = Path(
            "/Users/retriedstormtrooper/Downloads/03_图片素材/RAW_DNG照片/RAW_DNG_JPEG_批量导出/IMG_0342_preview.jpg"
        )
        if not preview.exists():
            self.skipTest("preview JPEG not available")

        primary_tiles = [
            ReplacementTile(payload=f"tile-{i}".encode(), hvcc=fake_hvcc()) for i in range(48)
        ]
        styledeltamap_tiles = prepare_styledeltamap_tiles(preview)

        parsed = parse_heif(
            build_apple_template_parity_heif(
                template_path=APPLE_SAMPLE,
                primary_tiles=primary_tiles,
                styledeltamap_tiles=styledeltamap_tiles,
            )
        )

        assert_apple_parity_features(self, parsed)
        # styledeltamap tiles should have Main 10 hvcC
        self.assertEqual(parsed["items"]["51"]["hvcC"]["general_profile_idc"], 2)
        self.assertEqual(parsed["items"]["51"]["hvcC"]["bit_depth_luma"], 10)

    def test_landscape_mode_sets_irot_zero_and_tmap_ispe(self):
        preview = Path(
            "/Users/retriedstormtrooper/Downloads/03_图片素材/RAW_DNG照片/RAW_DNG_JPEG_批量导出/IMG_0342_preview.jpg"
        )
        if not preview.exists():
            self.skipTest("preview JPEG not available")

        primary_tiles = [
            ReplacementTile(payload=f"tile-{i}".encode(), hvcc=fake_hvcc()) for i in range(48)
        ]
        styledeltamap_tiles = prepare_styledeltamap_tiles(preview)

        parsed = parse_heif(
            build_apple_template_parity_heif(
                template_path=APPLE_SAMPLE,
                primary_tiles=primary_tiles,
                styledeltamap_tiles=styledeltamap_tiles,
                landscape=True,
            )
        )

        assert_apple_parity_features(self, parsed)
        # Landscape: irot should be 0°
        for assoc in parsed["items"]["49"].get("property_associations", []):
            if assoc.get("type") == "irot":
                self.assertEqual(assoc["parsed"]["angle_ccw_degrees"], 0)
                self.assertEqual(assoc["parsed"]["payload_bytes"], 1)
                self.assertNotIn("parse_warning", assoc["parsed"])
        # Landscape: tmap ispe should be 4032x3024
        for assoc in parsed["items"]["100"].get("property_associations", []):
            if assoc.get("type") == "ispe":
                self.assertEqual(assoc["parsed"], {"width": 4032, "height": 3024})


if __name__ == "__main__":
    unittest.main()
