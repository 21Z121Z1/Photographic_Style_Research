import struct
import tempfile
import unittest
from pathlib import Path

from tools.heif_dump import extract_item_payloads, parse_heif


def box(box_type, payload=b""):
    return struct.pack(">I4s", 8 + len(payload), box_type.encode("ascii")) + payload


def full_box(box_type, version=0, flags=0, payload=b""):
    header = struct.pack(">B3s", version, flags.to_bytes(3, "big"))
    return box(box_type, header + payload)


def cstr(value):
    return value.encode("utf-8") + b"\0"


class HeifDumpTests(unittest.TestCase):
    def test_preserves_iloc_extents_when_iinf_appears_later(self):
        ftyp = box("ftyp", b"heic" + struct.pack(">I", 0) + b"mif1heic")
        hdlr = full_box(
            "hdlr",
            payload=b"\0\0\0\0" + b"pict" + b"\0" * 12 + cstr("PictureHandler"),
        )
        pitm = full_box("pitm", payload=struct.pack(">H", 1))
        iloc_payload = (
            bytes([0x44, 0x40])
            + struct.pack(">H", 1)
            + struct.pack(">HHI", 1, 0, 500)
            + struct.pack(">HII", 1, 0, 12)
        )
        iloc = full_box("iloc", payload=iloc_payload)
        item = full_box(
            "infe",
            version=2,
            flags=1,
            payload=struct.pack(">HH4s", 1, 0, b"hvc1") + cstr("primary"),
        )
        iinf = full_box("iinf", payload=struct.pack(">H", 1) + item)
        meta = full_box("meta", payload=hdlr + pitm + iloc + iinf)

        parsed = parse_heif(ftyp + meta + box("free", b"x" * 600))

        self.assertEqual(parsed["items"]["1"]["item_type"], "hvc1")
        self.assertTrue(parsed["items"]["1"]["hidden"])
        self.assertEqual(parsed["items"]["1"]["extents"][0]["absolute_offset"], 500)
        self.assertEqual(parsed["items"]["1"]["extents"][0]["length"], 12)

    def test_extracts_construction_method_one_payload_from_idat(self):
        ftyp = box("ftyp", b"heic" + struct.pack(">I", 0) + b"mif1heic")
        hdlr = full_box(
            "hdlr",
            payload=b"\0\0\0\0" + b"pict" + b"\0" * 12 + cstr("PictureHandler"),
        )
        pitm = full_box("pitm", payload=struct.pack(">H", 1))
        item = full_box(
            "infe",
            version=2,
            payload=struct.pack(">HH4s", 1, 0, b"grid") + cstr("styledelta"),
        )
        iinf = full_box("iinf", payload=struct.pack(">H", 1) + item)
        idat = box("idat", b"GRIDDATA")
        iloc_payload = (
            bytes([0x44, 0x00])
            + struct.pack(">H", 1)
            + struct.pack(">HH", 1, 1)
            + struct.pack(">H", 0)
            + struct.pack(">H", 1)
            + struct.pack(">II", 0, 8)
        )
        iloc = full_box("iloc", version=1, payload=iloc_payload)
        meta = full_box("meta", payload=hdlr + pitm + iinf + idat + iloc)
        data = ftyp + meta

        parsed = parse_heif(data)

        self.assertEqual(parsed["items"]["1"]["construction_method"], 1)
        self.assertEqual(parsed["items"]["1"]["extents"][0]["length"], 8)
        with tempfile.TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "sample.heic"
            output_dir = Path(tmp) / "items"
            input_path.write_bytes(data)
            written = extract_item_payloads(parsed, input_path, output_dir)

            self.assertEqual(len(written), 1)
            self.assertEqual(written[0].read_bytes(), b"GRIDDATA")

    def test_parses_item_graph_properties_and_aux_reference(self):
        ftyp = box("ftyp", b"heic" + struct.pack(">I", 0) + b"mif1heic")

        hdlr = full_box(
            "hdlr",
            payload=(
                b"\0\0\0\0"
                + b"pict"
                + b"\0" * 12
                + cstr("PictureHandler")
            ),
        )
        pitm = full_box("pitm", payload=struct.pack(">H", 49))
        primary = full_box(
            "infe",
            version=2,
            payload=struct.pack(">HH4s", 49, 0, b"hvc1") + cstr("primary"),
        )
        styledelta = full_box(
            "infe",
            version=2,
            payload=struct.pack(">HH4s", 50, 0, b"hvc1") + cstr("styledelta"),
        )
        tile = full_box(
            "infe",
            version=2,
            payload=struct.pack(">HH4s", 51, 0, b"hvc1") + cstr("tile"),
        )
        iinf = full_box("iinf", payload=struct.pack(">H", 3) + primary + styledelta + tile)

        ispe = full_box("ispe", payload=struct.pack(">II", 4032, 3024))
        pixi = full_box("pixi", payload=bytes([3, 10, 10, 10]))
        auxc = full_box(
            "auxC",
            payload=cstr("tag:apple.com,2023:photo:aux:styledeltamap"),
        )
        hvcc_payload = bytearray(23)
        hvcc_payload[0] = 1
        hvcc_payload[1] = 4
        hvcc_payload[12] = 90
        hvcc_payload[16] = 0xFC | 3
        hvcc_payload[17] = 0xF8 | 2
        hvcc_payload[18] = 0xF8 | 2
        hvcc_payload[21] = 0x08
        hvcc_payload[22] = 3
        hvcc = box("hvcC", bytes(hvcc_payload))
        ipco = box("ipco", ispe + pixi + auxc + hvcc)
        ipma_payload = (
            struct.pack(">I", 3)
            + struct.pack(">HB", 49, 2)
            + bytes([0x80 | 1, 2])
            + struct.pack(">HB", 50, 3)
            + bytes([0x80 | 1, 2, 3])
            + struct.pack(">HB", 51, 1)
            + bytes([4])
        )
        ipma = full_box("ipma", payload=ipma_payload)
        iprp = box("iprp", ipco + ipma)

        auxl = box("auxl", struct.pack(">HHH", 49, 1, 50))
        dimg = box("dimg", struct.pack(">HHH", 50, 1, 51))
        iref = full_box("iref", payload=auxl + dimg)

        iloc_payload = (
            bytes([0x44, 0x00])
            + struct.pack(">H", 3)
            + struct.pack(">HH", 49, 0)
            + struct.pack(">H", 1)
            + struct.pack(">II", 100, 20)
            + struct.pack(">HH", 50, 0)
            + struct.pack(">H", 1)
            + struct.pack(">II", 200, 30)
            + struct.pack(">HH", 51, 0)
            + struct.pack(">H", 1)
            + struct.pack(">II", 230, 42)
        )
        iloc = full_box("iloc", payload=iloc_payload)

        meta = full_box("meta", payload=hdlr + pitm + iinf + iprp + iref + iloc)
        parsed = parse_heif(ftyp + meta + box("mdat", b"x" * 260))

        self.assertEqual(parsed["ftyp"]["major_brand"], "heic")
        self.assertEqual(parsed["primary_item_id"], 49)
        self.assertEqual(parsed["handler"]["handler_type"], "pict")
        self.assertEqual(parsed["items"]["50"]["name"], "styledelta")
        self.assertEqual(
            parsed["styledeltamap"]["aux_type"],
            "tag:apple.com,2023:photo:aux:styledeltamap",
        )
        self.assertEqual(parsed["items"]["50"]["dimensions"], {"width": 4032, "height": 3024})
        self.assertEqual(parsed["items"]["50"]["pixi"], {"channels": 3, "bits": [10, 10, 10]})
        self.assertEqual(parsed["references"][0]["type"], "auxl")
        self.assertEqual(parsed["references"][0]["from_item_id"], 49)
        self.assertEqual(parsed["references"][0]["to_item_ids"], [50])
        self.assertEqual(parsed["items"]["50"]["extents"][0]["length"], 30)
        self.assertEqual(parsed["items"]["50"]["derived_child_item_ids"], [51])
        self.assertEqual(parsed["items"]["50"]["derived_payload_bytes"], 42)
        self.assertEqual(parsed["items"]["51"]["hvcC"]["chroma_format"], 3)
        self.assertEqual(parsed["items"]["51"]["hvcC"]["bit_depth_luma"], 10)
        self.assertEqual(parsed["items"]["51"]["hvcC"]["bit_depth_chroma"], 10)

    def test_flags_malformed_irot_payload_size(self):
        ftyp = box("ftyp", b"heic" + struct.pack(">I", 0) + b"mif1heic")
        hdlr = full_box(
            "hdlr",
            payload=b"\0\0\0\0" + b"pict" + b"\0" * 12 + cstr("PictureHandler"),
        )
        pitm = full_box("pitm", payload=struct.pack(">H", 1))
        item = full_box(
            "infe",
            version=2,
            payload=struct.pack(">HH4s", 1, 0, b"hvc1") + cstr("primary"),
        )
        iinf = full_box("iinf", payload=struct.pack(">H", 1) + item)
        malformed_irot = box("irot", b"\0\0\0\0\0")
        ipco = box("ipco", malformed_irot)
        ipma = full_box(
            "ipma",
            payload=struct.pack(">I", 1) + struct.pack(">HB", 1, 1) + bytes([1]),
        )
        iprp = box("iprp", ipco + ipma)
        meta = full_box("meta", payload=hdlr + pitm + iinf + iprp)

        parsed = parse_heif(ftyp + meta)
        irot = parsed["items"]["1"]["irot"]

        self.assertEqual(irot["payload_bytes"], 5)
        self.assertEqual(irot["parse_warning"], "irot payload should be exactly 1 byte")


if __name__ == "__main__":
    unittest.main()
