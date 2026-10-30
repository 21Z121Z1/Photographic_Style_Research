"""Pure-Python QuickTime/ISOBMFF parser for Apple Live Photo MOV companions.

Dumps every track (handler, aux video-map type from udta/tagc, tref links, timing,
edit lists, codec + bit depth + colour description) and decodes every timed
metadata (mebx) sample, plus the movie-level QuickTime ``mdta`` keys.

No proprietary dependencies: only the standard library.  Large files are
memory-mapped, so 250 MB ProRes/HEVC clips are fine.

CLI:
    python3 livephoto_mov.py FILE.MOV [--samples all|first|none] [--out out.json]
"""
from __future__ import annotations

import argparse
import base64
import json
import mmap
import plistlib
import struct
import sys
from pathlib import Path
from typing import Any, Iterator

CONTAINERS = {b"moov", b"trak", b"mdia", b"minf", b"stbl", b"dinf", b"edts", b"udta", b"tref", b"gmhd", b"tapt"}

# QuickTime "well-known" data types (QTFF, Metadata, table "Well-known data types").
WELL_KNOWN = {
    0: "reserved", 1: "utf8", 2: "utf16", 3: "sjis", 4: "utf8_sort", 5: "utf16_sort",
    13: "jpeg", 14: "png", 21: "be_signed_int", 22: "be_unsigned_int", 23: "be_float32",
    24: "be_float64", 27: "bmp", 28: "qt_metadata_atom", 65: "int8", 66: "be_int16",
    67: "be_int32", 70: "be_pointf32", 71: "be_dimensionsf32", 72: "be_rectf32",
    74: "be_int64", 75: "uint8", 76: "be_uint16", 77: "be_uint32", 78: "be_uint64",
    79: "be_affine_transform_f64",
    # Not in the public table we had at hand; observed on Apple's
    # live-photo-still-image-transform key as a 72-byte payload = 9 BE float64
    # (row-major 3x3 perspective matrix).  Decoded by size, labelled as inferred.
    83: "be_float64_3x3_matrix_inferred",
}

# ISO/IEC 23091-2 code points (subset that Apple uses).
PRIMARIES = {1: "BT.709", 2: "unspecified", 9: "BT.2020", 11: "DCI-P3", 12: "Display-P3 (SMPTE EG 432-1)"}
TRANSFER = {1: "BT.709", 2: "unspecified", 8: "linear", 13: "sRGB/IEC61966-2-1", 14: "BT.2020-10", 16: "PQ (SMPTE 2084)", 18: "HLG (ARIB STD-B67)"}
MATRIX = {0: "identity/RGB", 1: "BT.709", 2: "unspecified", 6: "BT.601 (SMPTE 170M)", 9: "BT.2020 NCL"}


def iter_boxes(buf, start: int, end: int) -> Iterator[tuple[bytes, int, int, int]]:
    """Yield (type, box_start, payload_start, box_end)."""
    pos = start
    while pos + 8 <= end:
        size, typ = struct.unpack(">I4s", buf[pos:pos + 8])
        hdr = 8
        if size == 1:
            size = struct.unpack(">Q", buf[pos + 8:pos + 16])[0]
            hdr = 16
        elif size == 0:
            size = end - pos
        if size < hdr or pos + size > end:
            break
        yield typ, pos, pos + hdr, pos + size
        pos += size


def child(buf, start, end, typ):
    for t, b, p, e in iter_boxes(buf, start, end):
        if t == typ:
            return p, e
    return None


def path(buf, start, end, *types):
    rng = (start, end)
    for t in types:
        rng = child(buf, rng[0], rng[1], t)
        if rng is None:
            return None
    return rng


def fourcc(b: bytes) -> str:
    return b.decode("latin1")


def fixed16_16(v: int) -> float:
    return (v - (1 << 32) if v & 0x80000000 else v) / 65536.0


def mac_epoch(v: int) -> str:
    import datetime as _dt
    return (_dt.datetime(1904, 1, 1, tzinfo=_dt.timezone.utc) + _dt.timedelta(seconds=v)).isoformat()


# ---------------------------------------------------------------- headers
def parse_mvhd(buf, p, e):
    ver = buf[p]
    if ver == 1:
        ct, mt, ts, dur = struct.unpack(">QQIQ", buf[p + 4:p + 32]); q = p + 32
    else:
        ct, mt, ts, dur = struct.unpack(">IIII", buf[p + 4:p + 20]); q = p + 20
    next_id = struct.unpack(">I", buf[e - 4:e])[0]
    return {"creation_time": mac_epoch(ct), "timescale": ts, "duration": dur,
            "duration_s": dur / ts if ts else None, "next_track_id": next_id}


def parse_tkhd(buf, p, e):
    ver, flags = buf[p], int.from_bytes(buf[p + 1:p + 4], "big")
    if ver == 1:
        tid = struct.unpack(">I", buf[p + 20:p + 24])[0]; dur = struct.unpack(">Q", buf[p + 28:p + 36])[0]; q = p + 36
    else:
        tid = struct.unpack(">I", buf[p + 12:p + 16])[0]; dur = struct.unpack(">I", buf[p + 20:p + 24])[0]; q = p + 24
    q += 8
    layer, alt, vol = struct.unpack(">hhh", buf[q:q + 6]); q += 8
    m = struct.unpack(">9i", buf[q:q + 36]); q += 36
    w, h = struct.unpack(">II", buf[q:q + 8])
    matrix = [m[0] / 65536, m[1] / 65536, m[2] / (1 << 30), m[3] / 65536, m[4] / 65536, m[5] / (1 << 30),
              m[6] / 65536, m[7] / 65536, m[8] / (1 << 30)]
    return {"track_id": tid, "flags": flags, "enabled": bool(flags & 1), "in_movie": bool(flags & 2),
            "in_preview": bool(flags & 4), "duration_movie_ts": dur, "layer": layer, "alternate_group": alt,
            "volume": vol / 256, "matrix": matrix, "width": w / 65536, "height": h / 65536}


def parse_mdhd(buf, p, e):
    ver = buf[p]
    if ver == 1:
        ts, dur = struct.unpack(">IQ", buf[p + 20:p + 32]); q = p + 32
    else:
        ts, dur = struct.unpack(">II", buf[p + 12:p + 20]); q = p + 20
    lang = struct.unpack(">H", buf[q:q + 2])[0]
    return {"timescale": ts, "duration": dur, "duration_s": dur / ts if ts else None, "language_code": lang}


def parse_hdlr(buf, p, e):
    comp_type, sub = buf[p + 4:p + 8], buf[p + 8:p + 12]
    name = bytes(buf[p + 24:e])
    if name[:1] and name[0] == len(name) - 1:  # pascal string (QuickTime)
        name = name[1:]
    return {"component_type": fourcc(comp_type), "handler": fourcc(sub), "name": name.rstrip(b"\0").decode("utf8", "replace")}


def parse_elst(buf, p, e):
    ver = buf[p]; n = struct.unpack(">I", buf[p + 4:p + 8])[0]; q = p + 8; out = []
    for _ in range(n):
        if ver == 1:
            dur, mt = struct.unpack(">Qq", buf[q:q + 16]); q += 16
        else:
            dur, mt = struct.unpack(">Ii", buf[q:q + 8]); q += 8
        rate = fixed16_16(struct.unpack(">I", buf[q:q + 4])[0]); q += 4
        out.append({"segment_duration_movie_ts": dur, "media_time": mt, "rate": rate, "empty": mt == -1})
    return out


def parse_tapt(buf, p, e):
    out = {}
    for t, b, q, f in iter_boxes(buf, p, e):
        w, h = struct.unpack(">II", buf[q + 4:q + 12])
        out[fourcc(t)] = [w / 65536, h / 65536]
    return out


# ---------------------------------------------------------------- codec boxes
def parse_hvcc(raw: bytes) -> dict:
    if len(raw) < 23:
        return {"raw_hex": raw.hex()}
    r = {
        "configuration_version": raw[0],
        "general_profile_space": raw[1] >> 6,
        "general_tier_flag": (raw[1] >> 5) & 1,
        "general_profile_idc": raw[1] & 0x1F,
        "general_profile": {1: "Main", 2: "Main10", 3: "MainStillPicture", 4: "RExt"}.get(raw[1] & 0x1F, "?"),
        "general_profile_compatibility_flags": raw[2:6].hex(),
        "general_constraint_indicator_flags": raw[6:12].hex(),
        "general_level_idc": raw[12],
        "chroma_format_idc": raw[16] & 3,
        "bit_depth_luma": (raw[17] & 7) + 8,
        "bit_depth_chroma": (raw[18] & 7) + 8,
        "avg_frame_rate": struct.unpack(">H", raw[19:21])[0],
        "length_size": (raw[21] & 3) + 1,
    }
    n = raw[22]; q = 23; arrays = []
    for _ in range(n):
        nal_type = raw[q] & 0x3F; cnt = struct.unpack(">H", raw[q + 1:q + 3])[0]; q += 3
        nals = []
        for _ in range(cnt):
            ln = struct.unpack(">H", raw[q:q + 2])[0]; nals.append(raw[q + 2:q + 2 + ln].hex()); q += 2 + ln
        arrays.append({"nal_unit_type": nal_type, "nalus_hex": nals})
    r["arrays"] = arrays
    return r


def parse_avcc(raw: bytes) -> dict:
    r = {"profile_idc": raw[1], "level_idc": raw[3], "length_size": (raw[4] & 3) + 1}
    nsps = raw[5] & 0x1F; q = 6; sps = []
    for _ in range(nsps):
        ln = struct.unpack(">H", raw[q:q + 2])[0]; sps.append(raw[q + 2:q + 2 + ln].hex()); q += 2 + ln
    npps = raw[q]; q += 1; pps = []
    for _ in range(npps):
        ln = struct.unpack(">H", raw[q:q + 2])[0]; pps.append(raw[q + 2:q + 2 + ln].hex()); q += 2 + ln
    r["sps_hex"], r["pps_hex"] = sps, pps
    r["bit_depth_luma"] = 8 if r["profile_idc"] in (66, 77, 88) else None
    return r


def parse_colr(raw: bytes) -> dict:
    kind = fourcc(raw[:4])
    if kind in ("nclc", "nclx"):
        pr, tr, mx = struct.unpack(">HHH", raw[4:10])
        r = {"type": kind, "primaries": pr, "primaries_name": PRIMARIES.get(pr, "?"),
             "transfer": tr, "transfer_name": TRANSFER.get(tr, "?"), "matrix": mx, "matrix_name": MATRIX.get(mx, "?")}
        if kind == "nclx" and len(raw) > 10:
            r["full_range"] = bool(raw[10] & 0x80)
        return r
    return {"type": kind, "icc_bytes": len(raw) - 4}


def parse_visual_entry(buf, p, e, fmt):
    w, h = struct.unpack(">HH", buf[p + 24:p + 28])
    hres, vres = struct.unpack(">II", buf[p + 28:p + 36])
    nlen = buf[p + 42]
    comp = bytes(buf[p + 43:p + 43 + min(nlen, 31)]).decode("latin1")
    depth = struct.unpack(">H", buf[p + 74:p + 76])[0]
    r = {"format": fmt, "width": w, "height": h, "compressor_name": comp, "depth": depth, "boxes": {}}
    for t, b, q, f in iter_boxes(buf, p + 78, e):
        raw = bytes(buf[q:f]); k = fourcc(t)
        if t == b"hvcC":
            r["boxes"][k] = parse_hvcc(raw)
            r["bit_depth"] = r["boxes"][k].get("bit_depth_luma")
        elif t == b"avcC":
            r["boxes"][k] = parse_avcc(raw)
            r["bit_depth"] = r["boxes"][k].get("bit_depth_luma")
        elif t == b"colr":
            r["boxes"][k] = parse_colr(raw)
        elif t == b"pasp":
            r["boxes"][k] = dict(zip(("h_spacing", "v_spacing"), struct.unpack(">II", raw[:8])))
        elif t == b"clap":
            v = struct.unpack(">8I", raw[:32])
            r["boxes"][k] = {"width": [v[0], v[1]], "height": [v[2], v[3]], "h_off": [v[4], v[5]], "v_off": [v[6], v[7]]}
        elif t == b"fiel":
            r["boxes"][k] = {"fields": raw[0], "detail": raw[1]}
        elif t == b"clli":
            r["boxes"][k] = dict(zip(("max_cll", "max_fall"), struct.unpack(">HH", raw[:4])))
        elif t == b"mdcv":
            r["boxes"][k] = {"raw_hex": raw.hex()}
        elif t == b"logs":
            r["boxes"][k] = {"string": raw.rstrip(b"\0").decode("utf8", "replace")}
        elif len(raw) <= 256 and all(32 <= c < 127 for c in raw.rstrip(b"\0")) and raw:
            r["boxes"][k] = {"string": raw.rstrip(b"\0").decode("ascii")}
        else:
            r["boxes"][k] = {"size": len(raw), "head_hex": raw[:64].hex()}
    return r


def parse_dtyp(raw: bytes) -> dict:
    ns = struct.unpack(">I", raw[:4])[0]
    if ns == 0:
        code = struct.unpack(">I", raw[4:8])[0]
        return {"namespace": 0, "well_known": code, "name": WELL_KNOWN.get(code, f"well_known_{code}")}
    return {"namespace": ns, "name": raw[4:].rstrip(b"\0").decode("utf8", "replace")}


def parse_mebx_entry(buf, p, e):
    r = {"format": "mebx", "keys": {}}
    k = child(buf, p + 8, e, b"keys")
    if k:
        for t, b, q, f in iter_boxes(buf, k[0], k[1]):
            local = struct.unpack(">I", t)[0]; ent = {"local_id": local}
            for t2, b2, q2, f2 in iter_boxes(buf, q, f):
                raw = bytes(buf[q2:f2])
                if t2 == b"keyd":
                    ent["key_namespace"] = fourcc(raw[:4]); ent["key"] = raw[4:].decode("utf8", "replace")
                elif t2 == b"dtyp":
                    ent["dtyp"] = parse_dtyp(raw)
                elif t2 == b"loca":
                    ent["locale"] = raw.hex()
                else:
                    ent[fourcc(t2)] = raw.hex()
            r["keys"][local] = ent
    return r


# ---------------------------------------------------------------- sample tables
def _full_table(buf, rng, fmt, entry):
    if rng is None:
        return None
    p, e = rng
    n = struct.unpack(">I", buf[p + 4:p + 8])[0]
    sz = struct.calcsize(fmt)
    return [struct.unpack(fmt, buf[p + 8 + i * sz:p + 8 + (i + 1) * sz]) for i in range(n)]


def parse_sample_table(buf, p, e):
    stsz = child(buf, p, e, b"stsz")
    fixed, n = struct.unpack(">II", buf[stsz[0] + 4:stsz[0] + 12])
    sizes = [fixed] * n if fixed else list(struct.unpack(f">{n}I", buf[stsz[0] + 12:stsz[0] + 12 + 4 * n]))
    co = child(buf, p, e, b"stco")
    if co:
        m = struct.unpack(">I", buf[co[0] + 4:co[0] + 8])[0]
        chunks = list(struct.unpack(f">{m}I", buf[co[0] + 8:co[0] + 8 + 4 * m]))
    else:
        co = child(buf, p, e, b"co64")
        m = struct.unpack(">I", buf[co[0] + 4:co[0] + 8])[0]
        chunks = list(struct.unpack(f">{m}Q", buf[co[0] + 8:co[0] + 8 + 8 * m]))
    stsc = _full_table(buf, child(buf, p, e, b"stsc"), ">III", None)
    offsets = []; si = 0
    for ci, off in enumerate(chunks):
        per = [s[1] for s in stsc if s[0] <= ci + 1][-1]
        for _ in range(per):
            if si < n:
                offsets.append(off); off += sizes[si]; si += 1
    dts = []; t = 0
    for c, d in _full_table(buf, child(buf, p, e, b"stts"), ">II", None) or []:
        for _ in range(c):
            dts.append(t); t += d
    total_dur = t
    ctts_rng = child(buf, p, e, b"ctts")
    cts = list(dts)
    if ctts_rng:
        ver = buf[ctts_rng[0]]
        i = 0
        for c, o in _full_table(buf, ctts_rng, ">Ii" if ver else ">II", None):
            if not ver and o & 0x80000000:
                o -= 1 << 32
            for _ in range(c):
                cts[i] += o; i += 1
    stss_rng = child(buf, p, e, b"stss")
    sync = None
    if stss_rng:
        m = struct.unpack(">I", buf[stss_rng[0] + 4:stss_rng[0] + 8])[0]
        sync = set(struct.unpack(f">{m}I", buf[stss_rng[0] + 8:stss_rng[0] + 8 + 4 * m]))
    cslg = child(buf, p, e, b"cslg")
    shift = 0
    if cslg:
        shift = struct.unpack(">i", buf[cslg[0] + 4:cslg[0] + 8])[0]  # compositionToDTSShift
    samples = [{"index": i, "offset": offsets[i], "size": sizes[i], "dts": dts[i], "cts": cts[i],
                "sync": (sync is None) or (i + 1 in sync)} for i in range(n)]
    return samples, total_dur, shift


# ---------------------------------------------------------------- mebx sample values
def decode_value(raw: bytes, dtyp: dict | None) -> Any:
    if raw[:8] == b"bplist00":
        try:
            return {"bplist": _jsonable(plistlib.loads(raw))}
        except Exception as ex:  # pragma: no cover
            return {"bplist_error": repr(ex), "hex": raw.hex()}
    name = (dtyp or {}).get("name")
    try:
        if name in ("utf8", "utf8_sort"):
            return raw.decode("utf8")
        if name == "be_float32":
            return list(struct.unpack(f">{len(raw)//4}f", raw)) if len(raw) != 4 else struct.unpack(">f", raw)[0]
        if name == "be_float64":
            return struct.unpack(">d", raw)[0]
        if name in ("be_signed_int", "int8", "be_int16", "be_int32", "be_int64"):
            return int.from_bytes(raw, "big", signed=True)
        if name in ("be_unsigned_int", "uint8", "be_uint16", "be_uint32", "be_uint64"):
            return int.from_bytes(raw, "big", signed=False)
        if name in ("be_affine_transform_f64", "be_float64_3x3_matrix_inferred") and len(raw) == 72:
            v = struct.unpack(">9d", raw)
            return [list(v[0:3]), list(v[3:6]), list(v[6:9])]
        if name in ("be_pointf32", "be_dimensionsf32", "be_rectf32"):
            return list(struct.unpack(f">{len(raw)//4}f", raw))
    except Exception:
        pass
    return {"hex": raw.hex()} if len(raw) <= 512 else {"size": len(raw), "base64": base64.b64encode(raw).decode()}


def _jsonable(o):
    if isinstance(o, dict):
        return {str(k): _jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_jsonable(v) for v in o]
    if isinstance(o, bytes):
        return {"bytes": len(o), "base64": base64.b64encode(o).decode()}
    if isinstance(o, float) and o != o:
        return None
    if hasattr(o, "isoformat"):
        return o.isoformat()
    return o


def decode_mebx_sample(raw: bytes, keys: dict) -> dict:
    out = {}
    for t, b, q, f in iter_boxes(raw, 0, len(raw)):
        local = struct.unpack(">I", t)[0]
        k = keys.get(local, {})
        out[k.get("key", f"local:{local}")] = decode_value(bytes(raw[q:f]), k.get("dtyp"))
    return out


# ---------------------------------------------------------------- movie-level metadata
def parse_meta_keys(buf, p, e):
    """moov/meta (mdta) keys + ilst."""
    if buf[p + 4:p + 8] != b"hdlr" and buf[p:p + 4] == b"\0\0\0\0":
        p += 4  # full-box variant
    keys = {}
    kr = child(buf, p, e, b"keys")
    if kr:
        n = struct.unpack(">I", buf[kr[0] + 4:kr[0] + 8])[0]; q = kr[0] + 8
        for i in range(n):
            sz = struct.unpack(">I", buf[q:q + 4])[0]
            keys[i + 1] = bytes(buf[q + 8:q + sz]).decode("utf8", "replace"); q += sz
    out = {}
    lr = child(buf, p, e, b"ilst")
    if lr:
        for t, b, q, f in iter_boxes(buf, lr[0], lr[1]):
            idx = struct.unpack(">I", t)[0]
            for t2, b2, q2, f2 in iter_boxes(buf, q, f):
                if t2 != b"data":
                    continue
                typ = struct.unpack(">I", buf[q2:q2 + 4])[0] & 0xFFFFFF
                raw = bytes(buf[q2 + 8:f2])
                out[keys.get(idx, str(idx))] = decode_value(raw, {"name": WELL_KNOWN.get(typ, str(typ))})
    return out


# ---------------------------------------------------------------- top level
class LivePhotoMov:
    def __init__(self, path_: str | Path):
        self.path = Path(path_)
        self._f = open(self.path, "rb")
        self.buf = mmap.mmap(self._f.fileno(), 0, access=mmap.ACCESS_READ)
        self.size = len(self.buf)
        self.top = [(fourcc(t), b, e - b) for t, b, p, e in iter_boxes(self.buf, 0, self.size)]
        moov = child(self.buf, 0, self.size, b"moov")
        if moov is None:
            raise ValueError("no moov")
        self.moov = moov
        b = self.buf
        self.mvhd = parse_mvhd(b, *child(b, *moov, b"mvhd"))
        meta = child(b, *moov, b"meta")
        self.global_keys = parse_meta_keys(b, *meta) if meta else {}
        self.tracks = [self._track(p, e) for t, _, p, e in iter_boxes(b, *moov) if t == b"trak"]
        self.by_id = {t["track_id"]: t for t in self.tracks}

    def close(self):
        self.buf.close(); self._f.close()

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()

    def _track(self, p, e):
        b = self.buf
        tk = parse_tkhd(b, *child(b, p, e, b"tkhd"))
        tr: dict[str, Any] = {"track_id": tk["track_id"], "tkhd": tk}
        if (r := child(b, p, e, b"tapt")):
            tr["tapt"] = parse_tapt(b, *r)
        if (r := path(b, p, e, b"edts", b"elst")):
            tr["edit_list"] = parse_elst(b, *r)
        if (r := child(b, p, e, b"tref")):
            tr["tref"] = {fourcc(t): list(struct.unpack(f">{(f-q)//4}I", b[q:f])) for t, _, q, f in iter_boxes(b, *r)}
        if (r := child(b, p, e, b"udta")):
            ud = {}
            for t, _, q, f in iter_boxes(b, *r):
                raw = bytes(b[q:f])
                ud.setdefault(fourcc(t), []).append(raw.rstrip(b"\0").decode("utf8", "replace") if all(32 <= c < 127 for c in raw.rstrip(b"\0")) else raw.hex())
            tr["udta"] = ud
            if "tagc" in ud:
                tr["aux_video_map_types"] = ud["tagc"]
        mdia = child(b, p, e, b"mdia")
        tr["mdhd"] = parse_mdhd(b, *child(b, *mdia, b"mdhd"))
        tr["hdlr"] = parse_hdlr(b, *child(b, *mdia, b"hdlr"))
        tr["handler"] = tr["hdlr"]["handler"]
        stbl = path(b, *mdia, b"minf", b"stbl")
        stsd = child(b, *stbl, b"stsd")
        entries = []
        for t, _, q, f in iter_boxes(b, stsd[0] + 8, stsd[1]):
            if t == b"mebx":
                entries.append(parse_mebx_entry(b, q, f))
            elif tr["handler"] in ("vide", "auxv"):
                entries.append(parse_visual_entry(b, q, f, fourcc(t)))
            elif tr["handler"] == "soun":
                ch, bits = struct.unpack(">HH", b[q + 16:q + 20]); sr = struct.unpack(">I", b[q + 24:q + 28])[0] >> 16
                entries.append({"format": fourcc(t), "channels": ch, "sample_size": bits, "sample_rate": sr})
            else:
                entries.append({"format": fourcc(t)})
        tr["sample_entries"] = entries
        samples, total, shift = parse_sample_table(b, *stbl)
        ts = tr["mdhd"]["timescale"]
        tr["samples"] = samples
        tr["composition_to_dts_shift"] = shift
        tr["timing"] = self._timing(samples, ts, total)
        return tr

    @staticmethod
    def _timing(samples, ts, total):
        if not samples:
            return {"sample_count": 0}
        pts = sorted(s["cts"] for s in samples)
        d = [b - a for a, b in zip(pts, pts[1:])]
        r = {"sample_count": len(samples), "media_duration_s": total / ts, "first_pts_s": pts[0] / ts,
             "last_pts_s": pts[-1] / ts, "sync_samples": sum(s["sync"] for s in samples),
             "sizes": {"min": min(s["size"] for s in samples), "max": max(s["size"] for s in samples)}}
        if d:
            r["pts_delta_s"] = {"min": min(d) / ts, "max": max(d) / ts, "mean": sum(d) / len(d) / ts}
            r["mean_rate_hz"] = (len(pts) - 1) / ((pts[-1] - pts[0]) / ts) if pts[-1] > pts[0] else None
        return r

    # -------- time mapping
    def media_to_movie(self, tr, media_t: int) -> float | None:
        """Map a media-timescale time to movie seconds through the edit list."""
        mts, ts = self.mvhd["timescale"], tr["mdhd"]["timescale"]
        el = tr.get("edit_list") or [{"segment_duration_movie_ts": None, "media_time": 0, "rate": 1.0, "empty": False}]
        movie = 0.0
        for seg in el:
            dur_s = None if seg["segment_duration_movie_ts"] is None else seg["segment_duration_movie_ts"] / mts
            if seg["empty"]:
                movie += dur_s or 0; continue
            start = seg["media_time"] / ts
            t = media_t / ts
            if t >= start and (dur_s is None or t < start + dur_s + 1e-9):
                return movie + (t - start)
            movie += dur_s or 0
        return None

    def sample_bytes(self, s) -> bytes:
        return bytes(self.buf[s["offset"]:s["offset"] + s["size"]])

    def metadata_tracks(self):
        return [t for t in self.tracks if t["sample_entries"] and t["sample_entries"][0]["format"] == "mebx"]

    def track_key_names(self, tr):
        return [k.get("key") for k in tr["sample_entries"][0]["keys"].values()]

    def find_meta_track(self, key: str):
        for t in self.metadata_tracks():
            if key in self.track_key_names(t):
                return t
        return None

    def find_aux(self, suffix: str):
        for t in self.tracks:
            if any(x.endswith(suffix) for x in t.get("aux_video_map_types", [])):
                return t
        return None

    def decode_meta_track(self, tr, which="all"):
        keys = tr["sample_entries"][0]["keys"]
        idx = range(len(tr["samples"])) if which == "all" else ([0] if which == "first" and tr["samples"] else [])
        out = []
        for i in idx:
            s = tr["samples"][i]
            out.append({"index": i, "pts_s": s["cts"] / tr["mdhd"]["timescale"],
                        "movie_time_s": self.media_to_movie(tr, s["cts"]), "offset": s["offset"], "size": s["size"],
                        "values": decode_mebx_sample(self.sample_bytes(s), keys)})
        return out

    def still_image_time(self) -> float | None:
        """Movie-time seconds of the still-image-time marker (honours its edit list)."""
        tr = self.find_meta_track("com.apple.quicktime.still-image-time")
        if not tr or not tr["samples"]:
            return None
        return self.media_to_movie(tr, tr["samples"][0]["cts"])

    def nearest_sample(self, tr, movie_t: float) -> int:
        best, bi = None, 0
        for i, s in enumerate(tr["samples"]):
            mt = self.media_to_movie(tr, s["cts"])
            if mt is None:
                continue
            d = abs(mt - movie_t)
            if best is None or d < best:
                best, bi = d, i
        return bi

    def summary(self, samples: str = "first") -> dict:
        out = {"file": self.path.name, "file_size": self.size, "top_level_boxes": self.top, "mvhd": self.mvhd,
               "global_metadata": self.global_keys, "still_image_time_s": self.still_image_time(), "tracks": []}
        for t in self.tracks:
            d = {k: v for k, v in t.items() if k != "samples"}
            if samples != "none" and t in self.metadata_tracks():
                d["decoded_samples"] = self.decode_meta_track(t, samples)
            out["tracks"].append(d)
        return out

    # -------- elementary stream extraction (for decoding aux video with ffmpeg)
    def annexb(self, tr, indices=None) -> bytes:
        """Return an Annex-B HEVC/AVC elementary stream for the given samples (decode order)."""
        ent = tr["sample_entries"][0]
        cfg = ent["boxes"].get("hvcC") or ent["boxes"].get("avcC")
        sc = b"\x00\x00\x00\x01"
        ps = b""
        if "arrays" in cfg:
            for a in cfg["arrays"]:
                for n in a["nalus_hex"]:
                    ps += sc + bytes.fromhex(n)
        else:
            for n in cfg["sps_hex"] + cfg["pps_hex"]:
                ps += sc + bytes.fromhex(n)
        L = cfg["length_size"]
        out = bytearray(ps)
        for i in (indices if indices is not None else range(len(tr["samples"]))):
            raw = self.sample_bytes(tr["samples"][i]); q = 0
            while q + L <= len(raw):
                n = int.from_bytes(raw[q:q + L], "big"); out += sc + raw[q + L:q + L + n]; q += L + n
        return bytes(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("mov")
    ap.add_argument("--samples", choices=["all", "first", "none"], default="all")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    with LivePhotoMov(a.mov) as m:
        s = json.dumps(_jsonable(m.summary(a.samples)), indent=1)
    if a.out:
        Path(a.out).write_text(s)
    else:
        print(s)
    return 0


if __name__ == "__main__":
    sys.exit(main())
