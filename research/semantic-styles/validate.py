#!/usr/bin/env python3
"""S22 acceptance gate for public synthetic native Metal results.

Validates what was actually run, and rejects attempts to promote it to a
whole-program interval proof, original consumer rewrite or real camera EV.
"""
import argparse
import json
import math
from pathlib import Path

def check(path: Path) -> dict:
    d=json.loads(path.read_text())
    assert "26A434" in d["os"], "Native OS build changed; do not silently reuse S21 bounds"
    assert d["original_metallib_sha256"] == "16a8a119e3e0ae1649d32b2bbc8ea9136cb757a8d1f3eb451025821901edff11"
    p=d["original_pso"]
    assert p["created"] and p["function"]=="renderFinalAdjustments"
    assert p["useImageBlock"] is False and p["useSrlVersion"]==0
    assert p["math_mode_overridden"] is False and p["whole_original_consumer_recompiled"] is False
    assert p["original_pixel_dispatch_performed"] is False
    assert d["photo_inputs"] is False and d["person_media_generated"] is False
    assert d["actual_photo_processed"] is False
    assert d["global_inverse_certified"] is False and d["camera_face_ev_identified"] is False
    assert d["modes_apply_to"]=="synthetic kernels only"
    modes=d["mode_rows"]
    assert [r["mode"] for r in modes]==["safe","relaxed","fast"]
    for row in modes:
        assert len(row["pow_cases"])==8 and len(row["samples"])==2
        pairs=row["pow_cases"]
        for case in pairs:
            x,y=case["x"],case["y"]
            assert math.isfinite(case["half_pow"]) and math.isfinite(case["float_pow"])
            assert abs(case["half_pow"]-x**y)<=max(0.02,abs(x**y)*0.02), case
            assert abs(case["float_pow"]-x**y)<=max(0.005,abs(x**y)*0.005), case
        s=row["samples"]
        assert s[0]["filter"]=="nearest" and s[1]["filter"]=="linear"
        for entry in s:
            assert entry["clamp_to_edge"] is True
            assert len(entry["RGBA_flat"])==16
            assert all(math.isfinite(x) for x in entry["RGBA_flat"])
        nearest=s[0]["RGBA_flat"]
        linear=s[1]["RGBA_flat"]
        def near(a,b):return abs(a-b)<=0.002
        assert near(nearest[0],0) and near(nearest[1],0)
        assert near(nearest[4],1) and near(nearest[5],0)
        assert near(nearest[12],0) and near(nearest[13],1)
        assert near(linear[8],0.5) and near(linear[9],0.5)
    first=[r["pow_cases"][6] for r in modes]  # x=0.25, exponent=1
    assert abs(first[0]["float_cancellation"])<1e-7
    assert abs(first[1]["float_cancellation"]-.25)<1e-7
    assert abs(first[2]["float_cancellation"]-.25)<1e-7
    return {"test":"s22_native_numeric","status":"pass",
            "original_pso_compiled":True,
            "synthetic_modes":3,"sampler_modes_per_math_mode":2,
            "half_pow_native":True,"mode_reassociation_observed":True,
            "global_skin_hull":False,"camera_EV":False,
            "scope":"Native Metal public synthetic probe only; not original consumer full-domain proof"}

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("result",type=Path)
    a=ap.parse_args()
    result=check(a.result)
    out=a.result.parent/"validation.json"
    out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(result,ensure_ascii=False))
