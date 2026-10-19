#!/usr/bin/env python3
"""Generate photo-free Float16 fixtures and audit native Apple Texture final units.

Only call generate and audit on the PSR macOS runner. User images,
person masks, metadata and original HEIC are never loaded. Unit tests do
not identify domain, whole-pipeline ordering, Apple filter kernels or an
inverse to the original camera's Texture Styles.
"""
import argparse
import hashlib
import json
import math
import os
import struct
from pathlib import Path

W, H = 512, 384
N = W * H
RGBA = ("original", "blur", "scaledblur", "precomputed", "gfA", "gfB", "zero")
SCALAR = ("skin", "person", "ones")

def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()

def only_runner():
    assert os.environ.get("GITHUB_ACTIONS") == "true"
    assert os.environ.get("RUNNER_OS") == "macOS"

def generate(base):
    only_runner()
    base.mkdir(parents=True, exist_ok=False)
    rgba = {k: bytearray() for k in RGBA}
    scalar = {k: bytearray() for k in SCALAR}
    pack4 = struct.Struct("<4e").pack
    pack1 = struct.Struct("<e").pack
    for y in range(H):
        fy = y / (H - 1)
        for x in range(W):
            fx = x / (W - 1)
            # Designed analytic chart only, RGB float values in [0,1].
            edge = .16 if 125 <= x < 310 and 75 <= y < 320 else 0.
            freq = .04 if ((x // 13 + y // 17) & 1) else -.04
            r = .10 + .50 * fx + edge + freq
            g = .12 + .46 * fy + .55 * edge + .6 * freq
            b = .17 + .30 * fx + .12 * fy + .25 * edge + .3 * freq
            smooth = (.10 + .50 * fx, .12 + .46 * fy, .17 + .30 * fx + .12 * fy)
            rgba["original"] += pack4(r, g, b, 1.)
            rgba["blur"] += pack4(*smooth, 1.)
            rgba["scaledblur"] += pack4(*tuple(t*.93 for t in smooth), 1.)
            rgba["precomputed"] += pack4(.5*r+.5*smooth[0],.5*g+.5*smooth[1],
                                          .5*b+.5*smooth[2],1.)
            rgba["gfA"] += pack4(.88,.88,.88,1.)
            rgba["gfB"] += pack4(.05,.05,.05,1.)
            rgba["zero"] += pack4(0.,0.,0.,0.)
            scalar["skin"] += pack1(.75)
            scalar["person"] += pack1(.85)
            scalar["ones"] += pack1(1.)
    rows=[]
    for name, buf in [*rgba.items(),*scalar.items()]:
        b=bytes(buf)
        expected=N*(8 if name in RGBA else 2)
        assert len(b)==expected, (name,expected,len(b))
        (base/(name+".f16")).write_bytes(b)
        rows.append({"name":name,"bytes":len(b),"sha256":sha_bytes(b)})
    (base/"fixture-manifest.json").write_text(json.dumps({
        "width":W,"height":H,"source":"analytic RGB+mask chart, not a photograph",
        "camera_calibrated":False,"input_files":rows},indent=2)+"\n")
    print(json.dumps({"synthetic_files":len(rows),"dimensions":[W,H],
                      "raw_bytes":sum(r["bytes"] for r in rows)}))

def unpack4(b):
    return struct.iter_unpack("<4e",b)

def compare(a,b):
    assert len(a)==len(b)==N*8
    finite=changed=eligible=failed=0
    max_abs=max_rel=0.
    sum_abs=0.
    for px,py in zip(unpack4(a),unpack4(b)):
        for x,y in zip(px[:3],py[:3]):
            if not math.isfinite(x) or not math.isfinite(y):
                continue
            finite+=1
            dist=abs(x-y)
            changed+=dist>0
            max_abs=max(max_abs,dist)
            sum_abs+=dist
            if x>1/255:
                eligible+=1
                rel=dist/x
                max_rel=max(max_rel,rel)
                failed+=rel>0.001
    return {"finite_rgb_pairs":finite,"changed_components":changed,
            "eligible_above_1_over_255":eligible,
            "components_over_1e_3":failed,
            "max_abs":max_abs,"max_relative":max_rel,
            "mean_abs":sum_abs/max(1,finite)}

def audit(base, native, output):
    only_runner()
    data=json.loads((native/"native.json").read_text())
    rows=data["rows"]
    assert len(rows)==6
    assert data["library_sha256"]=="16a8a119e3e0ae1649d32b2bbc8ea9136cb757a8d1f3eb451025821901edff11"
    assert "26A434" in data["os"]
    assert "Native final units only" in data["scope"]
    fixture=json.loads((base/"fixture-manifest.json").read_text())
    assert fixture["source"]=="analytic RGB+mask chart, not a photograph"
    for r in fixture["input_files"]:
        p=base/(r["name"]+".f16")
        assert p.stat().st_size==r["bytes"] and sha_bytes(p.read_bytes())==r["sha256"]
    source=(base/"original.f16").read_bytes()
    cases=[]
    for op in ("SkinSmooth","Mattify"):
        group=[r for r in rows if r["operator"]==op]
        assert [r["strength"] for r in group]==[0,.5,1]
        for r in group:
            assert r["context_frozen_during_inverse"] is True
            assert r["original_input_used_as_seed"] is False
            name=f'{op}-{r["strength"]:g}'
            forward=(native/(name+"-native.f16")).read_bytes()
            reverse=(native/(name+"-roundtrip.f16")).read_bytes()
            assert sha_bytes(source)==r["input_sha256"]
            assert sha_bytes(forward)==r["native_sha256"]
            assert sha_bytes(reverse)==r["roundtrip_sha256"]
            metrics=compare(forward,reverse)
            effect=compare(source,forward)
            assert metrics["finite_rgb_pairs"]>0 and effect["finite_rgb_pairs"]>0
            case={"operator":op,"strength":r["strength"],
                  "forward_changed_components":effect["changed_components"],
                  "forward_vs_source_max_abs":effect["max_abs"],
                  "roundtrip":metrics,
                  "native_forward_sha256":r["native_sha256"],
                  "native_roundtrip_sha256":r["roundtrip_sha256"],
                  "steps":len(r["steps"])}
            cases.append(case)
            print(json.dumps({k:case[k] for k in
                  ("operator","strength","forward_changed_components","roundtrip")}))
    out={"os":data["os"],"native_gpu":data["device"],
         "native_library_sha256":data["library_sha256"],
         "scope":"S24 native original final unit shaders, synthetic chart, frozen invented contexts; not original camera pipeline",
         "photos_used":False,"photo_related_metadata_used":False,
         "native_units":["SkinSmooth","Mattify"],
         "native_unit_kernels_invoked":True,
         "whole_original_texture_pipeline_invoked":False,
         "post_vs_pre_LTM_known":False,"linear_vs_Log_domain_known":False,
         "original_image_inverse_certified":False,
         "tuning_origin":"artificial S10 scalar buffers, not capture/device tuning",
         "metric_threshold":0.001,
         "rows":cases}
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")

def main():
    p=argparse.ArgumentParser()
    s=p.add_subparsers(dest="cmd",required=True)
    g=s.add_parser("generate");g.add_argument("dir",type=Path)
    a=s.add_parser("audit");a.add_argument("fixtures",type=Path)
    a.add_argument("native",type=Path);a.add_argument("summary",type=Path)
    v=p.parse_args()
    if v.cmd=="generate":generate(v.dir)
    else:audit(v.fixtures,v.native,v.summary)

if __name__=="__main__":main()
