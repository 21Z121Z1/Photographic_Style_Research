"""Make ablation variants of a Live Photo MOV for on-device Photos experiments.

Only the ``moov`` box is rewritten; ``mdat`` bytes are copied unchanged, so this
works when ``moov`` is the last top-level box (true for every native file seen).
Removed tracks simply stop being referenced; their samples stay as dead bytes.

    python3 ablate.py IN.MOV OUT.MOV --drop-key com.apple.quicktime.smartstyle-info
    python3 ablate.py IN.MOV OUT.MOV --drop-video-map sky --drop-video-map person
    python3 ablate.py IN.MOV OUT.MOV --set-global com.apple.quicktime.smartstyle.bypassed=0

Global values are patched in place and must keep their byte size.
"""
from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from livephoto_mov import LivePhotoMov, child, iter_boxes  # noqa: E402


def _box(typ: bytes, payload: bytes) -> bytes:
    return struct.pack(">I4s", 8 + len(payload), typ) + payload


def ablate(src: Path, dst: Path, drop_ids=(), drop_keys=(), drop_maps=(), set_global: dict | None = None) -> dict:
    with LivePhotoMov(src) as m:
        buf = m.buf
        moov_p, moov_e = m.moov
        moov_start = moov_p - 8
        if moov_e != m.size:
            raise ValueError("moov is not the last top-level box; refusing to rewrite")
        drop = set(drop_ids)
        for t in m.tracks:
            if any(k in drop_keys for k in (m.track_key_names(t) if t in m.metadata_tracks() else [])):
                drop.add(t["track_id"])
            if any(x.rsplit(".", 1)[-1] in drop_maps or x.endswith("." + y) for x in t.get("aux_video_map_types", []) for y in drop_maps):
                drop.add(t["track_id"])
        if 1 in drop:
            raise ValueError("refusing to drop the main video track")
        parts = []
        for t, b, p, e in iter_boxes(buf, moov_p, moov_e):
            if t == b"trak":
                tk = child(buf, p, e, b"tkhd")
                ver = buf[tk[0]]
                tid = struct.unpack(">I", buf[tk[0] + (20 if ver else 12):tk[0] + (24 if ver else 16)])[0]
                if tid in drop:
                    continue
            parts.append(bytes(buf[b:e]))
        moov = bytearray(_box(b"moov", b"".join(parts)))
        patched = {}
        for key, val in (set_global or {}).items():
            # find the ilst entry for this key and patch its data payload in place
            meta = child(moov, 8, len(moov), b"meta")
            mp = meta[0] + (4 if moov[meta[0]:meta[0] + 4] == b"\0\0\0\0" and moov[meta[0] + 4:meta[0] + 8] != b"hdlr" else 0)
            kr = child(moov, mp, meta[1], b"keys"); n = struct.unpack(">I", moov[kr[0] + 4:kr[0] + 8])[0]; q = kr[0] + 8; idx = None
            for i in range(n):
                sz = struct.unpack(">I", moov[q:q + 4])[0]
                if bytes(moov[q + 8:q + sz]).decode() == key:
                    idx = i + 1
                q += sz
            if idx is None:
                raise KeyError(key)
            lr = child(moov, mp, meta[1], b"ilst")
            for t, b, p, e in iter_boxes(moov, *lr):
                if struct.unpack(">I", t)[0] != idx:
                    continue
                d = child(moov, p, e, b"data"); typ = struct.unpack(">I", moov[d[0]:d[0] + 4])[0] & 0xFFFFFF
                raw_len = d[1] - d[0] - 8
                if typ == 23 and raw_len == 4:
                    new = struct.pack(">f", float(val))
                elif typ in (21, 22, 65, 66, 67, 75, 76, 77):
                    new = int(val).to_bytes(raw_len, "big", signed=typ in (21, 65, 66, 67))
                else:
                    raise ValueError(f"unsupported type {typ} for {key}")
                moov[d[0] + 8:d[1]] = new
                patched[key] = val
        with open(dst, "wb") as f:
            f.write(buf[:moov_start])
            f.write(moov)
    return {"dropped_track_ids": sorted(drop), "patched_globals": patched}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("dst")
    ap.add_argument("--drop-track", type=int, action="append", default=[])
    ap.add_argument("--drop-key", action="append", default=[])
    ap.add_argument("--drop-video-map", action="append", default=[])
    ap.add_argument("--set-global", action="append", default=[])
    a = ap.parse_args(argv)
    sg = dict(x.split("=", 1) for x in a.set_global)
    print(ablate(Path(a.src), Path(a.dst), a.drop_track, a.drop_key, a.drop_video_map, sg))


if __name__ == "__main__":
    main()
