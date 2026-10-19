#!/usr/bin/env python3
"""B-stage static contract verifier and photograph-free illustrative previews.

The generated preview is an explicitly labelled numerical illustration.
It is not an Apple-rendered Texture Style or a claim about filter placement.
Run image generation only in the PSR macOS GitHub Actions runner.
"""
import argparse
import json
import math
import os
from pathlib import Path

EXPECTED={
    "Filmic":57,"Glowy":57,"Soft":57,"Standard":57,"Studio":57
}
EFFECTS={"Diffusion":23,"Glow":14,"Bloom":6,"Mattify":2,
         "SkinSmoothingStandalone":34,"FilmGrain":22,"Halation":11,
         "UnderEyeBrightening":5}

def check_inventory(data):
    assert data["schema"]=="psr-texture-source-inventory-v1"
    m=data["texture_model"]
    assert len(m["device_ids"])==4 and len(m["port_types"])==5
    assert set(m["capture_modes"])=={"LivePhoto","Preview","Still"}
    assert set(m["presets"])==set(EXPECTED)
    assert m["preset_counts"]==EXPECTED
    assert m["observed_model_port_capture_preset_rows"]==285
    assert sum(m["preset_counts"].values())==285
    assert len(set(m["device_ids"]))==4
    assert m["effect_parameter_key_counts"]==EFFECTS
    assert len(m["representative_effect_orders"])==5
    assert m["representative_effect_orders"]["Standard"][0]==[]
    assert m["representative_effect_orders"]["Filmic"][0]==["Diffusion","Glow"]
    assert m["effect_occurrence_counts"]["FilmGrain"]==95
    assert m["effects_used_for_processing_domain"] is None
    assert m["global_local_ltm_order"] is None
    assert m["linear_or_log_domain"] is None
    assert m["reversible_original_texture_pipeline"] is None
    t=data["smartstyle_mapping"]
    assert t["count"]==16 and len(t["presets_by_cast"])==16
    assert set(t["presets_by_cast"].values())=={"Standard","Soft","Studio","Filmic"}
    assert data["acceptance"]["synthetic_preview_only"] is True
    assert data["acceptance"]["native_texture_processing_order_verified"] is False
    assert data["acceptance"]["no_apple_log_change"] is True
    assert len(data["source"]["files"])==4
    assert all(len(row["sha256"])==64 for row in data["source"]["files"])
    return True

def render_synthetic(out_dir):
    assert os.environ.get("GITHUB_ACTIONS")=="true", "Preview computation is macOS runner-only"
    assert os.environ.get("RUNNER_OS")=="macOS", "Only PSR macOS runner may compute previews"
    W,H=192,128
    # Procedural chart: no imaging input of any kind.
    src=[]
    for y in range(H):
        row=[]
        for x in range(W):
            base=0.18+0.46*x/(W-1)+0.1*math.sin(y*.073)
            edge=0.16 if 44<=x<100 and 25<=y<103 else 0.0
            row.append(max(0,min(1,base+edge+0.028*math.sin(x*.9+y*.7))))
        src.append(row)
    def sample(x,y):
        return src[max(0,min(y,H-1))][max(0,min(x,W-1))]
    smoothed=[]
    for y in range(H):
        smoothed.append([sum(sample(x+dx,y+dy) for dx in (-1,0,1)
                  for dy in (-1,0,1))/9 for x in range(W)])
    def ppm(data,name):
        raw=bytearray()
        for y in range(H):
            for x in range(W):
                v=max(0,min(1,data[y][x]))
                q=int(round(255*v))
                raw.extend((q,q,q))
        (out_dir/name).write_bytes(f"P6\n{W} {H}\n255\n".encode()+raw)
    # Deterministic non-cryptographic noise for an illustrative grain axis.
    seed=17
    grain=[]
    for y in range(H):
        row=[]
        for x in range(W):
            seed=(seed*1664525+1013904223)&0xffffffff
            a=((seed>>16)&65535)/65535-.5
            row.append(src[y][x]+0.13*a)
        grain.append(row)
    ppm(src,"original-synthetic.ppm")
    ppm(smoothed,"diffusion-surrogate-synthetic.ppm")
    ppm(grain,"grain-surrogate-synthetic.ppm")
    return {"size":[W,H],"input":"only computed mathematical grayscale pattern",
            "diffusion":"3x3 box blur; not Apple's identified filter",
            "grain":"deterministic pseudo-noise; not Apple's identified grain",
            "reverse_inference":"none","Apple_style_preview":False}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--inventory",type=Path,default=Path("research/texture-styles/evidence/source-inventory.json"))
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    a.out.mkdir(parents=True,exist_ok=True)
    d=json.loads(a.inventory.read_text())
    check_inventory(d)
    diagram=render_synthetic(a.out)
    result={"inventory":"passed","source":"user supplied, offline static inspection",
            "source_hashes":[x["sha256"] for x in d["source"]["files"]],
            "model_port_capture_preset_rows":285,"cast_mappings":16,
            "preview":diagram,"validation_level":"runner CPU on purely synthetic illustration",
            "original_Apple_backend_invoked":False,"native_Apple_Texture_Style_verified":False,
            "texture_processing_domain":None,"position_relative_to_GTM_LTM":None,
            "texture_style_original_inverse_certified":False,
            "XDRemux_prod_metadata_provenance_verified":False}
    (a.out/"validation.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(result,ensure_ascii=False))
if __name__=="__main__": main()
