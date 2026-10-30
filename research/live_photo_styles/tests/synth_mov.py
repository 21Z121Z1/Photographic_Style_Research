"""Build a tiny synthetic Live-Photo-like MOV in memory (no real media)."""
from __future__ import annotations

import plistlib
import struct


def box(t: bytes, p: bytes) -> bytes:
    return struct.pack(">I4s", 8 + len(p), t) + p


def fbox(t: bytes, p: bytes, v=0, fl=0) -> bytes:
    return box(t, struct.pack(">I", (v << 24) | fl) + p)


def tkhd(tid, w=0, h=0):
    m = struct.pack(">9I", 0x10000, 0, 0, 0, 0x10000, 0, 0, 0, 0x40000000)
    return fbox(b"tkhd", struct.pack(">IIIII", 0, 0, tid, 0, 600) + b"\0" * 8 + struct.pack(">hhhh", 0, 0, 0, 0) + m
                + struct.pack(">II", w << 16, h << 16), fl=15)


def mdhd(ts=600, dur=600):
    return fbox(b"mdhd", struct.pack(">IIIIHH", 0, 0, ts, dur, 0x55c4, 0))


def hdlr(h):
    return fbox(b"hdlr", struct.pack(">I4s", 0, h) + b"\0" * 12 + b"\0")


def stbl(entry: bytes, sizes, deltas, offsets, sync=None):
    n = len(sizes)
    stts = fbox(b"stts", struct.pack(">I", len(deltas)) + b"".join(struct.pack(">II", 1, d) for d in deltas))
    stsc = fbox(b"stsc", struct.pack(">IIII", 1, 1, 1, 1))
    stsz = fbox(b"stsz", struct.pack(">II", 0, n) + b"".join(struct.pack(">I", s) for s in sizes))
    stco = fbox(b"stco", struct.pack(">I", n) + b"".join(struct.pack(">I", o) for o in offsets))
    body = fbox(b"stsd", struct.pack(">I", 1) + entry) + stts + stsc + stsz + stco
    if sync is not None:
        body += fbox(b"stss", struct.pack(">I", len(sync)) + b"".join(struct.pack(">I", s) for s in sync))
    return box(b"stbl", body)


def mebx_entry(keys: dict[int, str], dtyp=None):
    dtyp = dtyp or {}
    ks = b""
    for kid, name in keys.items():
        inner = box(b"keyd", b"mdta" + name.encode())
        if kid in dtyp:
            inner += box(b"dtyp", struct.pack(">II", 0, dtyp[kid]))
        ks += box(struct.pack(">I", kid), inner)
    return box(b"mebx", b"\0" * 6 + struct.pack(">H", 1) + box(b"keys", ks))


def visual_entry(fmt=b"hvc1", w=64, h=48):
    p = b"\0" * 6 + struct.pack(">H", 1) + b"\0" * 16 + struct.pack(">HH", w, h) + struct.pack(">II", 0x480000, 0x480000)
    p += struct.pack(">IH", 0, 1) + b"\0" * 32 + struct.pack(">hh", 24, -1)
    p += box(b"colr", b"nclc" + struct.pack(">HHH", 12, 2, 6))
    return box(fmt, p)


def mebx_sample(local_id: int, payload: bytes) -> bytes:
    return struct.pack(">II", 8 + len(payload), local_id) + payload


def curve(n=257, scale=65534):
    vals = [round(scale * (i / (n - 1)) ** 0.8) for i in range(n)]
    return struct.pack("<H", n) + struct.pack(f"<{n}H", *vals), vals


def build(still_edit_movie_ticks=600):
    """Return (bytes, info). Tracks: 1 vide, 2 auxv tagc thumbnail, 3 smartstyle-info, 4 still-image-time."""
    c, vals = curve()
    ss = [plistlib.dumps({"0": 10, "3": c, "4": 367 / 65, "5": 2, "h": 37204 / 65536}, fmt=plistlib.FMT_BINARY),
          plistlib.dumps({"0": 10, "3": c, "4": 392 / 65, "5": 2, "h": 37204 / 65536, "b": 0.0}, fmt=plistlib.FMT_BINARY)]
    samples = {1: [b"\0\0\0\x02\x26\x01", b"\0\0\0\x02\x02\x01"], 2: [b"\0\0\0\x02\x26\x01"] * 2,
               3: [mebx_sample(1, s) for s in ss], 4: [mebx_sample(1, b"\xff")]}
    mdat_payload = b""; offs = {}
    hdr = 8 + 8  # ftyp(8) placeholder below + mdat header
    ftyp = box(b"ftyp", b"qt  " + struct.pack(">I", 0) + b"qt  ")
    base = len(ftyp) + 8
    for tid, ss_ in samples.items():
        offs[tid] = []
        for s in ss_:
            offs[tid].append(base + len(mdat_payload)); mdat_payload += s
    mdat = box(b"mdat", mdat_payload)

    def trak(tid, h, entry, extra=b"", edts=b"", sync=None, deltas=(300, 300)):
        sz = [len(s) for s in samples[tid]]
        minf = box(b"minf", stbl(entry, sz, list(deltas)[:len(sz)], offs[tid], sync))
        return box(b"trak", tkhd(tid) + edts + extra + box(b"mdia", mdhd() + hdlr(h) + minf))

    tagc = box(b"udta", box(b"tagc", b"com.apple.quicktime.video-map.smart-style-linear-thumbnail"))
    tref = box(b"tref", box(b"cdsc", struct.pack(">I", 1)))
    elst = box(b"edts", fbox(b"elst", struct.pack(">I", 2) + struct.pack(">IiI", still_edit_movie_ticks, -1, 0x10000)
                                + struct.pack(">IiI", 1, 0, 0x10000)))
    traks = (trak(1, b"vide", visual_entry(), sync=[1]) +
             trak(2, b"auxv", visual_entry(w=32, h=24), extra=tagc) +
             trak(3, b"meta", mebx_entry({1: "com.apple.quicktime.smartstyle-info"}), extra=tref) +
             trak(4, b"meta", mebx_entry({1: "com.apple.quicktime.still-image-time"}, {1: 77}), extra=tref, edts=elst, deltas=(1,)))
    mvhd = fbox(b"mvhd", struct.pack(">IIII", 0, 0, 600, 600) + struct.pack(">IH", 0x10000, 0x100) + b"\0" * 10
                + struct.pack(">9I", 0x10000, 0, 0, 0, 0x10000, 0, 0, 0, 0x40000000) + b"\0" * 24 + struct.pack(">I", 5))
    keyname = b"com.apple.quicktime.smartstyle.bypassed"
    keys = fbox(b"keys", struct.pack(">I", 1) + box(b"mdta", keyname))
    ilst = box(b"ilst", box(struct.pack(">I", 1), box(b"data", struct.pack(">II", 21, 0) + b"\x01")))
    meta = fbox(b"meta", fbox(b"hdlr", struct.pack(">I4s", 0, b"mdta") + b"\0" * 12 + b"\0") + keys + ilst)
    moov = box(b"moov", mvhd + traks + meta)
    return ftyp + mdat + moov, {"curve": vals, "still_s": still_edit_movie_ticks / 600}
