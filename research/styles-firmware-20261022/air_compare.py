"""Compare exact AIR payloads in existing iOS and host Metal resources.

Reuses the S110/existing extractor's LLVM-wrapper layout, using installed
llvm-dis. Only hashes, function names and selected tuning scalars are public;
AIR text stays in the owned scratch. Equality is per payload, not a pipeline.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import tempfile

TOKENS = [b"CMISmartStyle", b"StyleEngine", b"CMIGuidedFilter", b"UnderEye", b"SkinSmooth", b"Mattify"]


def payloads(data: bytes):
    for index, match in enumerate(re.finditer(b"\xde\xc0\x17\x0b", data)):
        start = match.start()
        if start + 20 > len(data):
            continue
        _, _, offset, size, _ = struct.unpack_from("<5I", data, start)
        if offset < 20 or start + offset + size > len(data):
            continue
        raw = data[start+offset:start+offset+size]
        if raw[:4] == b"BC\xc0\xde":
            yield index, start, raw


def inventory(path: Path, scratch: Path, llvm_dis: str) -> dict:
    data = path.read_bytes(); rows = []; exported = 0
    scratch.mkdir(parents=True, exist_ok=False)
    with tempfile.TemporaryDirectory(prefix="psr-air-compare-") as temp:
        for index, offset, raw in payloads(data):
            row = {"index": index, "wrapper_offset": offset, "payload_bytes": len(raw),
                   "payload_sha256": hashlib.sha256(raw).hexdigest()}
            if any(t in raw for t in TOKENS):
                bc = Path(temp)/"module.bc"; bc.write_bytes(raw)
                text = subprocess.check_output([llvm_dis, str(bc), "-o", "-"], text=True)
                exported += len(text.encode())
                if exported > 64*1024**2:
                    raise ValueError("Private AIR text budget exceeded")
                target = scratch/f"{index:04d}.ll.txt"; target.write_text(text)
                row["functions"] = [a or b for a,b in re.findall(r'^define .*?@(?:"([^"]+)"|([^ (]+))', text, re.M)]
                row["target_triple"] = re.search(r'^target triple = "([^"]+)"', text, re.M).group(1)
            rows.append(row)
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(), "modules": rows,
            "selected_modules": sum("functions" in r for r in rows), "private_text_bytes": exported}


def compare(ios: Path, host: Path, scratch: Path, output: Path, llvm_dis: str) -> dict:
    if output.exists(): raise FileExistsError(output)
    a = inventory(ios, scratch/"ios", llvm_dis); b = inventory(host, scratch/"host", llvm_dis)
    def by_function(value):
        result = {}
        for row in value["modules"]:
            for name in row.get("functions", []): result.setdefault(name, []).append(row)
        return result
    af, bf = by_function(a), by_function(b)
    shared = []
    for name in sorted(af.keys() & bf.keys()):
        ah = {r["payload_sha256"] for r in af[name]}; bh = {r["payload_sha256"] for r in bf[name]}
        shared.append({"function": name, "ios_indices": [r["index"] for r in af[name]], "host_indices": [r["index"] for r in bf[name]],
                       "exact_payload_match": bool(ah & bh)})
    result = {"ios_reference": {"hardware": "iPhone17,3", "image_build": "24A446", **a},
              "host_reference": {"os_build": subprocess.check_output(["sw_vers", "-buildVersion"], text=True).strip(), **b},
              "shared_function_count": len(shared), "functions_with_exact_payload_match": sum(r["exact_payload_match"] for r in shared),
              "shared_functions": shared, "ios_only_selected_functions": sorted(af.keys()-bf.keys()),
              "host_only_selected_functions": sorted(bf.keys()-af.keys()), "whole_metallib_equal": a["sha256"] == b["sha256"],
              "native_GPU_equivalence_verified": False, "whole_pipeline_equivalence_verified": False,
              "new_download_bytes": 0, "private_AIR_text_uploaded": False,
              "scope": "Exact bitcode payload fingerprint comparison; matching function names alone prove no equivalence. Metadata, specialization, bindings and runtime remain separate."}
    output.write_text(json.dumps(result, indent=2) + "\n")
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__);p.add_argument("ios",type=Path);p.add_argument("host",type=Path);p.add_argument("scratch",type=Path);p.add_argument("output",type=Path);p.add_argument("--llvm-dis",default="/opt/homebrew/opt/llvm/bin/llvm-dis")
    a=p.parse_args();r=compare(a.ios,a.host,a.scratch,a.output,a.llvm_dis)
    print(json.dumps({k:r[k]for k in ["whole_metallib_equal","shared_function_count","functions_with_exact_payload_match"]}))
