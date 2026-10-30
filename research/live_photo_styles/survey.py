"""Build the small derived evidence JSON for a set of Live Photo MOV(+HEIC) pairs.

    python3 survey.py --mov-dir /path/mov --heic-dir /path/heic --out evidence/

Writes per-file ``<name>.tracks.json`` (structure, no media), ``<name>.smartstyle.json``
(per-frame scalar keys + key-3 curve summaries), ``<name>.aux_compare.json`` and a
``survey.json`` roll-up.  Nothing derived here contains pixels beyond summary statistics.
"""
from __future__ import annotations

import argparse
import json
import plistlib
import struct
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parents[1]))
from livephoto_mov import LivePhotoMov, _jsonable  # noqa: E402

SMARTSTYLE = "com.apple.quicktime.smartstyle-info"


def key3_curve(b: bytes) -> tuple[int, np.ndarray]:
    n = struct.unpack("<H", b[:2])[0]
    return n, np.frombuffer(b[2:2 + 2 * n], "<u2").astype(np.float64)


def heic_styles_plist(heic: Path) -> dict | None:
    from tools.heif_dump import parse_heif, _payload_from_item_extents
    d = heic.read_bytes(); h = parse_heif(d)
    st = [i for i in h["items"].values() if i.get("uri_type") == "tag:apple.com,2023:photo:metadata:styles"]
    return plistlib.loads(_payload_from_item_extents(d, st[0])) if st else None


def word_variation(blobs: list[bytes]) -> list[dict]:
    """For fixed-size binary samples: which 32-bit LE words vary across frames."""
    n = min(len(b) for b in blobs) // 4
    A = np.array([np.frombuffer(b[:4 * n], "<u4") for b in blobs])
    F = A.view("<f4")
    out = []
    for i in range(n):
        col = A[:, i]
        out.append({"byte_offset": 4 * i, "distinct": int(len(set(col.tolist()))), "first_hex": f"{int(col[0]):08x}",
                    "as_f32_first": float(F[0, i]) if np.isfinite(F[0, i]) else None,
                    "as_f32_range": [float(F[:, i].min()), float(F[:, i].max())] if np.isfinite(F[:, i]).all() else None})
    return out


def smartstyle_report(m: LivePhotoMov, heic_plist: dict | None) -> dict:
    tr = m.find_meta_track(SMARTSTYLE)
    if tr is None:
        return {"present": False}
    ts = tr["mdhd"]["timescale"]
    frames = []
    for s in sorted(tr["samples"], key=lambda s: s["cts"]):
        raw = m.sample_bytes(s)
        # mebx sample = [u32 size][u32 local key id][bplist]
        size, local = struct.unpack(">II", raw[:8])
        p = plistlib.loads(raw[8:size])
        frames.append({"movie_time_s": m.media_to_movie(tr, s["cts"]), "file_offset": s["offset"], "sample_size": s["size"],
                       "box_local_key": local, "plist": p})
    keys = sorted(set().union(*[f["plist"] for f in frames]))
    st = m.still_image_time(); si = int(np.argmin([abs(f["movie_time_s"] - st) for f in frames]))
    rep: dict = {"present": True, "track_id": tr["track_id"], "samples": len(frames), "timescale": ts,
                 "still_image_time_s": st, "still_frame_index": si, "keys": {}}
    for k in keys:
        vals = [f["plist"].get(k) for f in frames]
        nn = [v for v in vals if v is not None]
        e = {"present_in": len(nn), "python_types": sorted({type(v).__name__ for v in nn})}
        if all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in nn):
            e.update({"min": min(nn), "max": max(nn), "distinct": len(set(nn)), "at_still": vals[si],
                      "per_frame": vals})
            if all(isinstance(v, float) for v in nn):
                e["all_exact_float16"] = all(float(np.float16(v)) == v for v in nn)
                for q in (65, 65536):
                    e[f"all_multiples_of_1_{q}"] = all(abs(v * q - round(v * q)) < 1e-3 for v in nn)
        elif all(isinstance(v, bytes) for v in nn):
            e.update({"byte_lengths": sorted({len(v) for v in nn}), "distinct": len({bytes(v) for v in nn})})
        elif all(isinstance(v, bool) for v in nn):
            e.update({"values": sorted(set(nn))})
        rep["keys"][k] = e
    if "3" in keys:
        C = np.array([key3_curve(f["plist"]["3"])[1] for f in frames])
        n0 = {key3_curve(f["plist"]["3"])[0] for f in frames}
        rep["key3"] = {"count_header_values": sorted(n0), "samples_per_curve": int(C.shape[1]),
                       "first_value": sorted(set(C[:, 0].tolist())), "last_value": sorted(set(C[:, -1].tolist())),
                       "monotonic_nondecreasing_all_frames": bool((np.diff(C, axis=1) >= 0).all()),
                       "frame_to_frame_rms": [round(float(x), 2) for x in np.sqrt((np.diff(C, axis=0) ** 2).mean(1))],
                       "still_frame_curve_every_16th": C[si, ::16].astype(int).tolist()}
        if heic_plist is not None and "3" in heic_plist:
            hn, hc = key3_curve(heic_plist["3"])
            d = np.abs(C - hc).max(1); r = np.sqrt(((C - hc) ** 2).mean(1))
            rep["key3"]["vs_heic"] = {"heic_count_header": hn, "maxabs_at_still": float(d[si]), "rms_at_still": float(r[si]),
                                      "rms_min_frame": int(r.argmin()), "rms_min": float(r.min()),
                                      "rms_per_frame": [round(float(x), 1) for x in r],
                                      "heic_curve_every_16th": hc[::16].astype(int).tolist()}
    if "b" in keys:
        btimes = [round(f["movie_time_s"], 4) for f in frames if "b" in f["plist"]]
        mt = m.find_aux("sky") or m.find_aux("person") or m.find_aux("skin")
        mtimes = sorted(round(m.media_to_movie(mt, s["cts"]), 4) for s in mt["samples"]) if mt else []
        rep["key_b_vs_matte_frames"] = {"b_frames": len(btimes), "matte_frames": len(mtimes), "identical_times": btimes == mtimes}
    if heic_plist is not None:
        hp = {k: v for k, v in heic_plist.items()}
        rep["heic_styles_plist"] = {"keys": sorted(hp), "0": hp.get("0"), "4": hp.get("4"), "5": hp.get("5"), "h": hp.get("h"),
                                    "i": hp.get("i"), "1_bytes": len(hp["1"]) if isinstance(hp.get("1"), bytes) else None,
                                    "c_bytes": len(hp.get("c", b"")), "d_bytes": len(hp.get("d", b"")), "e": hp.get("e"), "f": hp.get("f"),
                                    "g": hp.get("g"), "g_fourcc": struct.pack(">I", hp["g"]).decode("latin1") if isinstance(hp.get("g"), int) else None}
        sf = frames[si]["plist"]
        rep["still_frame_vs_heic"] = {k: {"mov": sf.get(k), "heic": hp.get(k)} for k in ("0", "4", "5", "h")}
        if "h" in sf and "h" in hp:
            rep["still_frame_vs_heic"]["heic_h_over_mov_h"] = hp["h"] / sf["h"]
        if isinstance(hp.get("i"), dict) and "Gain" in hp["i"] and "h" in hp:
            rep["still_frame_vs_heic"]["heic_i_gain_over_heic_h"] = hp["i"]["Gain"] / hp["h"]
    return rep


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--mov-dir", required=True); ap.add_argument("--heic-dir"); ap.add_argument("--out", required=True)
    ap.add_argument("--no-aux", action="store_true")
    a = ap.parse_args(argv)
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    roll = []
    for mov in sorted(Path(a.mov_dir).glob("*.MOV")):
        heic = next(iter(Path(a.heic_dir).rglob(mov.stem + ".HEIC")), None) if a.heic_dir else None
        with LivePhotoMov(mov) as m:
            summ = m.summary("none")
            # public repo: never commit GPS from the samples
            summ["global_metadata"] = {k: ("<redacted>" if "location" in k else v) for k, v in summ["global_metadata"].items()}
            (out / f"{mov.stem}.tracks.json").write_text(json.dumps(_jsonable(summ), indent=1))
            meta = {}
            for t in m.metadata_tracks():
                for k in m.track_key_names(t):
                    meta[k] = {"track_id": t["track_id"], "samples": len(t["samples"])}
            row = {"file": mov.name, "heic": heic.name if heic else None, "duration_s": m.mvhd["duration_s"],
                   "still_image_time_s": m.still_image_time(),
                   "tracks": [{"id": t["track_id"], "handler": t["handler"], "format": t["sample_entries"][0]["format"],
                               "video_map": t.get("aux_video_map_types"), "tref": t.get("tref"), "samples": len(t["samples"]),
                               "w": t["sample_entries"][0].get("width"), "h": t["sample_entries"][0].get("height"),
                               "bit_depth": t["sample_entries"][0].get("bit_depth")} for t in m.tracks],
                   "metadata_keys": meta,
                   "global_smartstyle_keys": {k: v for k, v in m.global_keys.items() if "style" in k},
                   "global_model": m.global_keys.get("com.apple.quicktime.model"),
                   "global_software": m.global_keys.get("com.apple.quicktime.software")}
            # small per-file decodes of the single-sample tracks
            for key in ("com.apple.quicktime.live-photo-still-image-transform",
                        "com.apple.quicktime.live-photo-still-image-transform-reference-dimensions",
                        "com.apple.quicktime.still-image-time", "com.apple.quicktime.video-orientation"):
                t = m.find_meta_track(key)
                if t:
                    row.setdefault("single_sample_tracks", {})[key] = m.decode_meta_track(t, "first")[0]["values"][key]
            lp = m.find_meta_track("com.apple.quicktime.live-photo-info")
            if lp and m.find_meta_track(SMARTSTYLE):
                blobs = [m.sample_bytes(s)[8:] for s in lp["samples"]]
                (out / f"{mov.stem}.live_photo_info_words.json").write_text(json.dumps(
                    {"sample_payload_bytes": sorted({len(b) for b in blobs}), "words": word_variation(blobs)}, indent=1))
            if m.find_meta_track(SMARTSTYLE):
                hpl = heic_styles_plist(heic) if heic else None
                ss = smartstyle_report(m, hpl)
                (out / f"{mov.stem}.smartstyle.json").write_text(json.dumps(_jsonable(ss), indent=1))
                row["smartstyle"] = {k: ss[k] for k in ("samples", "still_frame_index") if k in ss}
                row["smartstyle"]["keys"] = sorted(ss["keys"])
        if heic and not a.no_aux and row.get("smartstyle"):
            from compare_aux import compare, have_ffmpeg
            if have_ffmpeg():
                cmp = compare(mov, heic)
                (out / f"{mov.stem}.aux_compare.json").write_text(json.dumps(cmp, indent=1, default=float))
        roll.append(row)
    (out / "survey.json").write_text(json.dumps(_jsonable(roll), indent=1))
    print(json.dumps(_jsonable(roll), indent=1)[:4000])


if __name__ == "__main__":
    main()
