"""Run a bounded original ARM64 arithmetic loop with synthetic records only.

The 33-instruction loop from the cached plugin contains no API calls, I/O,
privileged instructions or return into iOS. A macOS harness supplies pointers
and saves its own ABI state. No Apple library is loaded; no binary is retained
in Git. This checks one arithmetic branch, never the full capture pipeline.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform
import re
import subprocess
import sys
import tempfile
import numpy as np

C = Path(__file__).resolve().parent
sys.path.insert(0, str(C.parent / "hdr-native"))
from producer_curve_record_s54 import ios_gtc_input_ratios


def check(output: Path) -> dict:
    if platform.system() != "Darwin" or platform.machine() != "arm64":
        raise RuntimeError("Requires a local Apple Silicon macOS host")
    text = (C / "evidence/plugin-24A435/linear-4.asm.txt").read_text()
    rows = [(int(a, 16), bytes.fromhex(b)) for a, b in re.findall(
        r"^(0x[0-9a-f]+):\s+((?:[0-9a-f]{2} ){3}[0-9a-f]{2})\s", text, re.M)
        if 0x8eb0 <= int(a, 16) <= 0x8f30]
    if [a for a, _ in rows] != list(range(0x8eb0, 0x8f34, 4)):
        raise ValueError("Original arithmetic loop boundaries changed")
    original = b"".join(b for _, b in rows)
    if hashlib.sha256(original).hexdigest() != "136b3854b385fff4f7695d960808262eb814119d85bbba8ae55481287d7b2b9e":
        raise ValueError("Reviewed original instruction digest changed")
    # The only branch is the bounded backwards b.ne from the original loop.
    if rows[-1][1] != bytes.fromhex("c1fcff54"):
        raise ValueError("Unexpected loop branch")
    assembly = ".text\n.p2align 2\n.globl _psr_gtc257\n_psr_gtc257:\n"
    assembly += "stp x19, x30, [sp, #-16]!\nsub x19, x1, #0x30\n"
    assembly += "\n".join(f".long 0x{int.from_bytes(b, 'little'):08x}" for _, b in rows)
    assembly += "\nldp x19, x30, [sp], #16\nret\n"
    source = r'''
#include <stdint.h>
#include <stdio.h>
extern void psr_gtc257(const uint16_t *, uint16_t *);
int main(void) {
    uint16_t input[258], output[256];
    uint64_t fpcr = 0;
    __asm__ volatile("msr fpcr, %0" : : "r"(fpcr));
    for (;;) {
        size_t n = fread(input, sizeof(uint16_t), 258, stdin);
        if (!n && feof(stdin)) return 0;
        if (n != 258 || input[0] != 257 || !input[256]) return 2;
        psr_gtc257(input, output);
        if (fwrite(output, sizeof(uint16_t), 256, stdout) != 256) return 3;
    }
}
'''
    rng = np.random.default_rng(257)
    records = []
    # Structured and randomized records; the latter include non-monotone
    # tables, and ratios above one. They are arithmetic probes, not camera priors.
    for divisor in [1, 3, 257, 1023, 32768, 65535]:
        record = np.zeros(258, dtype="<u2"); record[0] = 257
        record[1:257] = np.linspace(0, divisor, 256).astype("<u2")
        record[256] = divisor; record[257] = 65535
        records.append(record)
    for _ in range(128):
        record = rng.integers(0, 65536, 258, dtype=np.uint16)
        record[0] = 257; record[256] = rng.integers(2, 65536)
        records.append(record.astype("<u2"))
    # Explicit proof that the trailing word is outside this branch's reads.
    duplicate = records[-1].copy(); duplicate[257] ^= 65535; records.append(duplicate)
    payload = b"".join(r.tobytes() for r in records)
    # S54's ratio decoder is reused, including its explicit zero-divisor stop.
    with np.errstate(over="ignore"):
        expected = np.array([ios_gtc_input_ratios(r.tobytes()) for r in records], dtype="float64").astype("<f2").view("<u2")
    with tempfile.TemporaryDirectory(prefix="psr-gtc-native-") as temp:
        work = Path(temp)
        (work / "loop.S").write_text(assembly)
        (work / "main.c").write_text(source)
        command = ["xcrun", "clang", "-arch", "arm64", "-O2", "-fno-fast-math", str(work / "main.c"), str(work / "loop.S"), "-o", str(work / "check")]
        build = subprocess.run(command, capture_output=True, text=True)
        if build.returncode:
            raise RuntimeError(build.stderr)
        run = subprocess.run([str(work / "check")], input=payload, capture_output=True)
        if run.returncode or len(run.stdout) != expected.nbytes:
            raise RuntimeError(f"Native arithmetic harness failed: rc={run.returncode}, bytes={len(run.stdout)}")
        actual = np.frombuffer(run.stdout, "<u2").reshape(expected.shape)
        mismatches = int(np.count_nonzero(actual != expected))
        if mismatches:
            raise AssertionError(f"Native half mismatch count: {mismatches}")
        if not np.array_equal(actual[-1], actual[-2]):
            raise AssertionError("Trailing word influenced output")
        receipt = {"host_os_build": subprocess.check_output(["sw_vers", "-buildVersion"], text=True).strip(),
                   "host_arch": platform.machine(), "compiler": subprocess.check_output(["xcrun", "clang", "--version"], text=True).splitlines()[0],
                   "source_plugin_uuid": "305C2ACD-593F-3B87-98A8-736D9362820D",
                   "source_plugin_sha256": "34c7ecc0c6355159edea3e0515571760a230911104eb042907f921c70eca919f",
                   "source_assembly_sha256": hashlib.sha256(text.encode()).hexdigest(), "original_address_range": ["0x8eb0", "0x8f30 inclusive"],
                   "original_instruction_bytes": len(original), "original_instruction_sha256": hashlib.sha256(original).hexdigest(),
                   "harness_source_sha256": hashlib.sha256(source.encode()).hexdigest(), "generated_assembly_sha256": hashlib.sha256(assembly.encode()).hexdigest(),
                   "local_executable_sha256": hashlib.sha256((work / "check").read_bytes()).hexdigest(),
                   "records": len(records), "half_outputs": int(expected.size), "half_bit_mismatches": mismatches,
                   "synthetic_input_sha256": hashlib.sha256(payload).hexdigest(), "native_output_sha256": hashlib.sha256(run.stdout).hexdigest(),
                   "trailing_word_control_passed": True, "reused_ratio_model": "hdr-native/producer_curve_record_s54.py::ios_gtc_input_ratios",
                   "fpcr": 0, "full_ios_library_loaded": False, "metal_executed": False, "photo_inputs": 0,
                   "complete_camera_inverse_verified": False,
                   "scope": "Original cached plugin's 257-header CPU normalization loop only. No texture/API/other-header/zero-divisor/native-GPU coverage."}
        if output.exists():
            raise FileExistsError(output)
        output.write_text(json.dumps(receipt, indent=2) + "\n")
    return receipt


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("output", type=Path)
    result = check(p.parse_args().output)
    print(json.dumps({k: result[k] for k in ("records", "half_outputs", "half_bit_mismatches", "host_os_build", "original_instruction_bytes")}))
