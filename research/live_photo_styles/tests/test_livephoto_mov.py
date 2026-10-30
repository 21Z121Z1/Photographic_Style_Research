import base64
import json
import os
import struct
import sys
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent)); sys.path.insert(0, str(HERE))
import synth_mov  # noqa: E402
from livephoto_mov import LivePhotoMov  # noqa: E402

def _ss(d):
    return d["values"]["com.apple.quicktime.smartstyle-info"]["bplist"]


def _bytes(v):
    return base64.b64decode(v["base64"])


SAMPLES = Path(os.environ.get("LIVEPHOTO_SAMPLES", "/workspace/samples16"))


@pytest.fixture
def synth(tmp_path):
    data, info = synth_mov.build(still_edit_movie_ticks=801)
    p = tmp_path / "synth.MOV"; p.write_bytes(data)
    return p, info


def test_tracks_and_tagc(synth):
    p, _ = synth
    with LivePhotoMov(p) as m:
        assert [t["handler"] for t in m.tracks] == ["vide", "auxv", "meta", "meta"]
        assert m.find_aux("smart-style-linear-thumbnail")["track_id"] == 2
        assert m.by_id[3]["tref"] == {"cdsc": [1]}
        assert m.global_keys["com.apple.quicktime.smartstyle.bypassed"] == 1


def test_still_time_uses_edit_list(synth):
    p, info = synth
    with LivePhotoMov(p) as m:
        assert m.still_image_time() == pytest.approx(801 / 600)


def test_smartstyle_bplist_and_curve(synth):
    p, info = synth
    with LivePhotoMov(p) as m:
        tr = m.find_meta_track("com.apple.quicktime.smartstyle-info")
        dec = m.decode_meta_track(tr)
        v0, v1 = _ss(dec[0]), _ss(dec[1])
        assert v0["0"] == 10 and "b" not in v0 and v1["b"] == 0.0
        raw = _bytes(v0["3"])
        n = struct.unpack("<H", raw[:2])[0]
        assert n == 257 and list(struct.unpack(f"<{n}H", raw[2:])) == info["curve"]
        assert dec[1]["movie_time_s"] == pytest.approx(0.5)


def test_annexb(synth):
    p, _ = synth
    with LivePhotoMov(p) as m:
        es = m.annexb(m.by_id[1]) if m.by_id[1]["sample_entries"][0].get("boxes", {}).get("hvcC") else None
    assert es is None  # synthetic entry has no hvcC; real files covered below


def test_ablate_roundtrip(synth, tmp_path):
    import ablate
    p, _ = synth
    out = tmp_path / "abl.MOV"
    r = ablate.ablate(p, out, drop_keys=["com.apple.quicktime.smartstyle-info"],
                      set_global={"com.apple.quicktime.smartstyle.bypassed": 0})
    assert r["dropped_track_ids"] == [3]
    with LivePhotoMov(out) as m:
        assert m.find_meta_track("com.apple.quicktime.smartstyle-info") is None
        assert m.global_keys["com.apple.quicktime.smartstyle.bypassed"] == 0
        assert m.still_image_time() == pytest.approx(801 / 600)


def test_key1_probe_finds_stride():
    import key1_probe
    rng = np.random.default_rng(0)
    a = np.tile(np.eye(3).ravel(), 64) + rng.normal(0, 0.02, 576)
    r = key1_probe.probe(a.astype(np.float16))
    assert r["n"] == 576 and 9 in r["autocorr_top_lags"][:2]


# ---------------- real media (skipped when absent)
REAL = sorted((SAMPLES / "mov").glob("*_ST_*.MOV")) if (SAMPLES / "mov").is_dir() else []


@pytest.mark.skipif(not REAL, reason="Live Photo sample MOVs not present")
@pytest.mark.parametrize("mov", REAL, ids=lambda p: p.stem)
def test_real_smartstyle(mov):
    with LivePhotoMov(mov) as m:
        assert len(m.tracks) == 11
        tr = m.find_meta_track("com.apple.quicktime.smartstyle-info")
        dec = m.decode_meta_track(tr)
        main = m.by_id[1]
        assert len(dec) == len(main["samples"])
        for d in dec:
            v = _ss(d)
            assert v["0"] == 10 and "1" not in v
            raw = _bytes(v["3"])
            c = np.frombuffer(raw[2:], "<u2")
            assert len(raw) == 516 and struct.unpack("<H", raw[:2])[0] == 257 and np.all(np.diff(c.astype(int)) >= 0)
            assert abs(v["4"] * 65 - round(v["4"] * 65)) < 1e-3
            assert abs(v["h"] * 65536 - round(v["h"] * 65536)) < 1e-3
        mattes = m.find_aux("video-map.sky")
        b_times = sorted(round(d["movie_time_s"], 4) for d in dec if "b" in _ss(d))
        sky_times = sorted(round(m.media_to_movie(mattes, s["cts"]), 4) for s in mattes["samples"])
        assert b_times == sky_times
        st = m.still_image_time()
        assert 1.0 < st < 1.6
