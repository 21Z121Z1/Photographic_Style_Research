"""Check the newly modeled non-257 GTC branch with its original ARM loops.

Only the two arithmetic loops are copied to an owned ABI harness. The original
stack-allocation and ObjC/Metal calls are excluded and no iOS library is loaded.
The previously accepted257-header test is deliberately not rerun here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform
import re
import subprocess
import tempfile
import numpy as np

from gtc_texture import build_texture

C = Path(__file__).resolve().parent
BLOCKS = [(0x8f64, 0x8f90, "639059e92b192885e53f7e1207def3cb59e0d9f443177ae876c8e95a8412a9de"),
          (0x8f94, 0x8ffc, "6159b7b8475d0e5895cb219c8ba4cf50f0cc86c1d12489cc703e6a994d2dfef5")]


def check(output: Path) -> dict:
    if platform.system() != "Darwin" or platform.machine() != "arm64":
        raise RuntimeError("Requires local Apple Silicon macOS")
    if output.exists():
        raise FileExistsError(output)
    evidence = C / "evidence/plugin-iphone17-3-24A446/SmartStyleV1.bundle"
    text = (evidence / "linear-4.asm.txt").read_text()
    instructions = [(int(a, 16), bytes.fromhex(b)) for a, b in re.findall(r"^(0x[0-9a-f]+):\s+((?:[0-9a-f]{2} ){3}[0-9a-f]{2})\s", text, re.M)]
    selected = []
    for start, end, expected in BLOCKS:
        rows = [(a, b) for a, b in instructions if start <= a <= end]
        raw = b"".join(b for _, b in rows)
        if [a for a, _ in rows] != list(range(start, end+4, 4)) or hashlib.sha256(raw).hexdigest() != expected:
            raise ValueError("Reviewed original block changed")
        selected.append(raw)
    assembly = ".text\n.p2align 2\n.globl _psr_gtc_generic\n_psr_gtc_generic:\n"
    assembly += "stp x19, x30, [sp, #-16]!\nsub x19, x2, #0x30\nmov x8, x1\nmov w12, w3\nsub w13, w3, #1\n"
    for raw in selected:
        assembly += "\n".join(f".long 0x{int.from_bytes(raw[i:i+4], 'little'):08x}" for i in range(0, len(raw), 4)) + "\n"
    assembly += "ldp x19, x30, [sp], #16\nret\n"
    source = r'''
#include <stdint.h>
#include <stdio.h>
extern void psr_gtc_generic(const uint16_t *, float *, uint16_t *, uint32_t);
int main(void) {
    uint16_t input[4097], output[256]; float nodes[4096]; uint64_t fpcr=0;
    __asm__ volatile("msr fpcr, %0" : : "r"(fpcr));
    for (;;) {
        if (fread(input,2,1,stdin)!=1) return feof(stdin)?0:2;
        unsigned h=input[0];
        if(h<65||h>4097||h==257||fread(input+1,2,h-1,stdin)!=h-1||!input[h-1])return 3;
        psr_gtc_generic(input,nodes,output,h);
        if(fwrite(nodes,4,h-1,stdout)!=h-1||fwrite(output,2,256,stdout)!=256)return 4;
    }
}
'''
    rng = np.random.default_rng(20261022)
    records, tags = [], []
    for h in [65, 66, 129, 130, 255, 256, 258, 259, 513, 1025, 4097]:
        for kind in ["ramp", "step", "alternating", "random"]:
            for divisor in [1, 257, 65535]:
                r = np.empty(h, dtype="<u2"); r[0] = h
                if kind == "ramp": r[1:] = np.linspace(0, divisor, h-1).astype("<u2")
                elif kind == "step": r[1:] = np.where(np.arange(h-1) < (h-1)//2, 0, divisor)
                elif kind == "alternating": r[1:] = np.where(np.arange(h-1) % 2, divisor, 0)
                else: r[1:] = rng.integers(0, 65536, h-1, dtype=np.uint16)
                r[-1] = divisor
                records.append(r); tags.append({"header": h, "kind": kind, "divisor": divisor})
    # Finite integer inputs can overflow half after normalization. Retain and
    # compare those exact Inf codes rather than removing them from a mask.
    overflow = np.full(65, 65535, dtype="<u2"); overflow[0] = 65; overflow[-1] = 1
    records.append(overflow); tags.append({"header": 65, "kind": "half_overflow_probe", "divisor": 1})
    payload = b"".join(r.tobytes() for r in records)
    expected = [build_texture(r.tobytes()) for r in records]
    with tempfile.TemporaryDirectory(prefix="psr-gtc-generic-") as temp:
        work = Path(temp); (work/"loop.S").write_text(assembly); (work/"main.c").write_text(source)
        build = subprocess.run(["xcrun", "clang", "-arch", "arm64", "-O2", "-fno-fast-math", str(work/"main.c"), str(work/"loop.S"), "-o", str(work/"check")], capture_output=True, text=True)
        if build.returncode: raise RuntimeError(build.stderr)
        native = subprocess.run([str(work/"check")], input=payload, capture_output=True)
        if native.returncode: raise RuntimeError(f"Native harness rc={native.returncode}")
        offset, node_bad, half_bad = 0, 0, 0
        rows = []
        for tag, model in zip(tags, expected):
            count = model.header - 1
            nodes = np.frombuffer(native.stdout, "<u4", count=count, offset=offset); offset += count*4
            half = np.frombuffer(native.stdout, "<u2", count=256, offset=offset); offset += 512
            nb = int(np.count_nonzero(nodes != model.normalized_nodes.view("<u4")))
            hb = int(np.count_nonzero(half != model.half_values.view("<u2")))
            node_bad += nb; half_bad += hb
            rows.append({**tag, "f32_node_mismatches": nb, "half_output_mismatches": hb,
                         "half_nonfinite_outputs": int((~np.isfinite(half.view("<f2"))).sum())})
        if offset != len(native.stdout) or node_bad or half_bad:
            raise AssertionError(f"Original generic branch mismatch: nodes={node_bad}, half={half_bad}, parsed={offset}/{len(native.stdout)}")
        report = {"hardware_reference": "iPhone17,3", "firmware_build": "24A446", "plugin_sha256": "04dbdad52b959f848ba1d8de07f4fc81c85d1595c8843637a1dc905039112216",
                  "host_build": subprocess.check_output(["sw_vers", "-buildVersion"], text=True).strip(), "fpcr": 0,
                  "original_blocks": [{"start": hex(a), "end_inclusive": hex(b), "sha256": h} for a,b,h in BLOCKS],
                  "records": len(records), "normalized_f32_nodes": sum(m.header-1 for m in expected),
                  "half_outputs": len(records)*256, "f32_node_mismatches": node_bad, "half_output_mismatches": half_bad,
                  "headers": sorted(set(t["header"] for t in tags)), "synthetic_input_sha256": hashlib.sha256(payload).hexdigest(),
                  "native_output_sha256": hashlib.sha256(native.stdout).hexdigest(), "executable_sha256": hashlib.sha256((work/"check").read_bytes()).hexdigest(),
                  "harness_c_sha256": hashlib.sha256(source.encode()).hexdigest(), "harness_assembly_sha256": hashlib.sha256(assembly.encode()).hexdigest(),
                  "model_source_sha256": hashlib.sha256((C/"gtc_texture.py").read_bytes()).hexdigest(),
                  "ios_library_loaded": False, "native_gpu_executed": False, "photo_inputs": 0,
                  "old257_test_repeated": False, "complete_camera_inverse_verified": False,
                  "scope": "Only generic-header CPU normalize and256-sample interpolation loops. Explicit finite nonzero-normalizer records. No complete ObjC/Metal pipeline or capture-domain proof.", "rows": rows}
        output.write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("output", type=Path)
    r = check(p.parse_args().output)
    print(json.dumps({k:r[k] for k in ["records", "normalized_f32_nodes", "half_outputs", "f32_node_mismatches", "half_output_mismatches"]}))
