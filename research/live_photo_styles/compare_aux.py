"""Decode Live Photo MOV auxiliary video tracks at the still-image time and compare
them numerically with the paired HEIC's linear thumbnail and semantic mattes.

Both sides go through the same path: length-prefixed HEVC samples -> Annex-B
(parameter sets from hvcC) -> ``ffmpeg -f hevc`` -> raw planar YUV codes.  No
proprietary libraries.  Only small JSON summaries are written; no frames.

    python3 compare_aux.py MOV HEIC [--out summary.json]
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1]))
from livephoto_mov import LivePhotoMov, parse_hvcc  # noqa: E402

PAIRS = {  # MOV video-map suffix -> HEIC auxC type
    "smart-style-linear-thumbnail": "tag:apple.com,2023:photo:aux:linearthumbnail",
    "sky": "urn:com:apple:photo:2020:aux:semanticskymatte",
    "person": "urn:com:apple:photo:2018:aux:portraiteffectsmatte",
    "skin": "urn:com:apple:photo:2019:aux:semanticskinmatte",
    "smart-style-delta-map": "tag:apple.com,2023:photo:aux:styledeltamap",
}


def have_ffmpeg() -> bool:
    return shutil.which("ffmpeg") is not None


def decode_hevc(annexb: bytes, w: int, h: int, bit_depth: int, chroma: int = 1) -> list[tuple[np.ndarray, ...]]:
    """Decode an Annex-B HEVC stream to a list of (Y, Cb, Cr) code planes in output order."""
    pix = {(8, 1): "yuv420p", (10, 1): "yuv420p10le", (8, 0): "gray", (10, 0): "gray10le"}[(bit_depth, chroma)]
    out = subprocess.run(["ffmpeg", "-v", "error", "-f", "hevc", "-i", "pipe:0", "-f", "rawvideo", "-pix_fmt", pix, "pipe:1"],
                         input=annexb, capture_output=True, check=True).stdout
    dt = np.uint16 if bit_depth > 8 else np.uint8
    a = np.frombuffer(out, dt)
    ysz = w * h; csz = (w // 2) * (h // 2) if chroma else 0
    fs = ysz + 2 * csz
    frames = []
    for i in range(len(a) // fs):
        f = a[i * fs:(i + 1) * fs]
        y = f[:ysz].reshape(h, w)
        if chroma:
            frames.append((y, f[ysz:ysz + csz].reshape(h // 2, w // 2), f[ysz + csz:].reshape(h // 2, w // 2)))
        else:
            frames.append((y,))
    return frames


def box_down(a: np.ndarray, H: int, W: int) -> np.ndarray:
    h, w = a.shape
    if h % H == 0 and w % W == 0:
        return a.astype(np.float64).reshape(H, h // H, W, w // W).mean((1, 3))
    ys = np.linspace(0, h, H + 1).astype(int); xs = np.linspace(0, w, W + 1).astype(int)
    return np.array([[a[ys[j]:ys[j + 1], xs[i]:xs[i + 1]].mean() for i in range(W)] for j in range(H)])


def heic_aux_planes(heic: Path, aux_type: str):
    from tools.heif_dump import parse_heif, _payload_from_item_extents
    d = heic.read_bytes(); h = parse_heif(d)
    items = [i for i in h["items"].values() if i.get("aux_type") == aux_type]
    if not items:
        return None
    it = items[0]
    props = [h["properties"][x["property_index"] - 1] for x in it["property_associations"]]
    hv = [p for p in props if p["type"] == "hvcC"]
    if it.get("item_type") != "hvc1" or not hv:
        return {"item_type": it.get("item_type"), "decoded": False}
    raw = d[hv[0]["offset"] + 8:hv[0]["offset"] + hv[0]["size"]]
    cfg = parse_hvcc(raw)
    sc = b"\0\0\0\1"
    bs = b"".join(sc + bytes.fromhex(n) for a in cfg["arrays"] for n in a["nalus_hex"])
    pay = _payload_from_item_extents(d, it); q = 0; L = cfg["length_size"]
    while q + L <= len(pay):
        n = int.from_bytes(pay[q:q + L], "big"); bs += sc + pay[q + L:q + L + n]; q += L + n
    w, hh = it["dimensions"]["width"], it["dimensions"]["height"]
    fr = decode_hevc(bs, w, hh, cfg["bit_depth_luma"], cfg["chroma_format_idc"])
    rot = [p["parsed"].get("angle_ccw_degrees") for p in props if p["type"] == "irot"]
    return {"item_id": it["item_id"], "width": w, "height": hh, "bit_depth": cfg["bit_depth_luma"],
            "chroma_format_idc": cfg["chroma_format_idc"], "profile": cfg["general_profile"], "irot": rot[0] if rot else 0,
            "colr": [p.get("parsed") for p in props if p["type"] == "colr"], "planes": fr[0]}


# Apple Log (from XDRemux apple_log_encode): code = C + A*log2(L + B) above the toe.
AL_A, AL_B, AL_C = 0.08550479263067245, 0.009640520438551903, 0.693369448184967


def apple_log_decode(code01: np.ndarray) -> np.ndarray:
    return np.power(2.0, (code01 - AL_C) / AL_A) - AL_B


def apple_log_luma_relation(mov_y: np.ndarray, heic_y: np.ndarray, bit_depth: int) -> dict:
    """Approximate: treats the log-encoded luma code as a log-encoded luminance."""
    mx = (1 << bit_depth) - 1
    lm = apple_log_decode(mov_y.astype(np.float64) / mx); lh = apple_log_decode(heic_y.astype(np.float64) / mx)
    ok = (lm > 0.01) & (lh > 0.01)
    if ok.sum() < 50:
        return {"usable_pixels": int(ok.sum())}
    ratio = lm[ok] / lh[ok]
    sl, ic = np.polyfit(np.log2(lh[ok]), np.log2(lm[ok]), 1)
    return {"usable_pixels": int(ok.sum()), "median_linear_ratio_mov_over_heic": float(np.median(ratio)),
            "median_stops": float(np.log2(np.median(ratio))), "loglog_slope": float(sl), "loglog_intercept_stops": float(ic),
            "note": "approximation: luma code treated as Apple-Log-encoded luminance; toe pixels (L<=0.01) excluded"}


def fit(x: np.ndarray, y: np.ndarray) -> dict:
    x = x.ravel().astype(np.float64); y = y.ravel().astype(np.float64)
    A = np.stack([x, np.ones_like(x)], 1); (s, c), *_ = np.linalg.lstsq(A, y, rcond=None)
    r = float(np.corrcoef(x, y)[0, 1]) if x.std() > 0 and y.std() > 0 else None
    return {"pearson_r": r, "slope": float(s), "intercept": float(c), "rmse_raw": float(np.sqrt(((x - y) ** 2).mean())),
            "rmse_after_affine": float(np.sqrt(((A @ [s, c] - y) ** 2).mean())), "mean_mov": float(x.mean()), "mean_heic": float(y.mean())}


def compare(mov_path: Path, heic_path: Path) -> dict:
    res = {"mov": mov_path.name, "heic": heic_path.name}
    with LivePhotoMov(mov_path) as m:
        st = m.still_image_time(); res["still_image_time_s"] = st
        main = [t for t in m.tracks if t["handler"] == "vide"][0]
        res["main_video"] = {"width": main["sample_entries"][0]["width"], "height": main["sample_entries"][0]["height"],
                             "frame_at_still": m.nearest_sample(main, st)}
        tr_tf = m.find_meta_track("com.apple.quicktime.live-photo-still-image-transform")
        if tr_tf:
            res["still_image_transform"] = m.decode_meta_track(tr_tf, "first")[0]["values"]
        res["tracks"] = {}
        for suffix, aux in PAIRS.items():
            tr = m.find_aux(suffix)
            entry: dict = {"mov_track": tr["track_id"] if tr else None}
            if tr is None:
                entry["present_in_mov"] = False
                res["tracks"][suffix] = entry
                continue
            se = tr["sample_entries"][0]; cfg = se["boxes"]["hvcC"]
            frames = decode_hevc(m.annexb(tr), se["width"], se["height"], cfg["bit_depth_luma"], cfg["chroma_format_idc"])
            pts = sorted(m.media_to_movie(tr, s["cts"]) for s in tr["samples"])
            k = int(np.argmin([abs(p - st) for p in pts]))
            entry.update({"present_in_mov": True, "width": se["width"], "height": se["height"], "bit_depth": cfg["bit_depth_luma"],
                          "decoded_frames": len(frames), "samples": len(tr["samples"]), "frame_index_at_still": k,
                          "frame_time_at_still_s": pts[k], "colr": se["boxes"].get("colr"), "logs": se["boxes"].get("logs")})
            hp = heic_aux_planes(heic_path, aux)
            if hp is None or "planes" not in hp:
                entry["heic"] = hp or {"present": False}
                res["tracks"][suffix] = entry
                continue
            entry["heic"] = {k2: v for k2, v in hp.items() if k2 != "planes"}
            names = ["Y", "Cb", "Cr"]
            per = {}
            for pi, hplane in enumerate(hp["planes"]):
                mp = frames[k][pi]
                hd = box_down(hplane, *mp.shape)
                if hp["bit_depth"] != cfg["bit_depth_luma"]:
                    hd = hd * (2 ** cfg["bit_depth_luma"]) / (2 ** hp["bit_depth"])
                per[names[pi]] = fit(mp, hd)
            entry["still_frame_vs_heic"] = per
            if "apple-log" in str(se["boxes"].get("logs", "")):
                hd0 = box_down(hp["planes"][0], *frames[k][0].shape)
                if hp["bit_depth"] != cfg["bit_depth_luma"]:
                    hd0 = hd0 * (2 ** cfg["bit_depth_luma"]) / (2 ** hp["bit_depth"])
                entry["apple_log_luma_relation"] = apple_log_luma_relation(frames[k][0], hd0, cfg["bit_depth_luma"])
            # temporal: scale-free match of every MOV frame against the HEIC (Pearson r of luma codes)
            hdY = box_down(hp["planes"][0], *frames[0][0].shape)
            rs = [float(np.corrcoef(f[0].ravel().astype(float), hdY.ravel())[0, 1]) if f[0].std() > 0 else 0.0 for f in frames]
            entry["luma_pearson_r_by_frame"] = [round(v, 4) for v in rs]
            entry["best_frame_index"] = int(np.argmax(rs)); entry["best_frame_time_s"] = pts[int(np.argmax(rs))]
            res["tracks"][suffix] = entry
    return res


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("mov"); ap.add_argument("heic"); ap.add_argument("--out")
    a = ap.parse_args(argv)
    r = compare(Path(a.mov), Path(a.heic))
    s = json.dumps(r, indent=1, default=float)
    Path(a.out).write_text(s) if a.out else print(s)


if __name__ == "__main__":
    main()
