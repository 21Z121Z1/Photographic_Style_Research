"""Export only the next reviewed call-binding methods from an owned plugin.

Reuses the existing Mach-O mapper and checks every disassembled instruction
against the verified official plugin bytes; no iOS code is loaded or executed.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess

from inspect_cached_plugin import digest, macho_layout

METHODS = [
    ("setup", "-[CMISmartStyleProcessorV1 setup]"),
    ("prepare", "-[CMISmartStyleProcessorV1 prepareToProcess:]"),
    ("target-input", "-[CMISmartStyleProcessorV1 _configureStyleEngineTargetThumbnailPixelBuffer:inputTargetThumbnailPixelBuffer:]"),
    ("linear-input", "-[CMISmartStyleProcessorV1 _configureInputLinearPixelBufferForPixelBufferRenderer:withinputLinearCropRect:]"),
    ("unstyled-gtc", "-[CMISmartStyleProcessorUtilitiesV1 createUnstyledThumbnailFromMetadata:ltmThumbnailPixelBuffer:cameraInfo:applyGDC:toPixelBuffer:]"),
    ("stills-reversibility", "+[CMISmartStyleProcessorV1 getDefaultProcessorConfigurationForStillsReversibility]"),
]


def export(binary: Path, output: Path) -> dict:
    raw = binary.read_bytes()
    if digest(raw) != "04dbdad52b959f848ba1d8de07f4fc81c85d1595c8843637a1dc905039112216":
        raise ValueError("Require the verified iPhone17,3/24A446 plugin")
    uid, segments = macho_layout(raw)
    output.mkdir(parents=True, exist_ok=False)
    rows = []
    try:
        for name, symbol in METHODS:
            text = subprocess.check_output(["ipsw", "macho", "disass", "--symbol", symbol, "--cache", str(output/"symbols.a2s"), str(binary)], text=True).rstrip() + "\n"
            instructions = re.findall(r"^(0x[0-9a-f]+):\s+((?:[0-9a-f]{2} ){3}[0-9a-f]{2})\s", text, re.M)
            checked = bytearray()
            for address, value in instructions:
                a = int(address, 16); code = bytes.fromhex(value)
                vm, off, _ = next(s for s in segments if s[0] <= a < s[0]+s[2])
                if raw[off+a-vm:off+a-vm+4] != code: raise ValueError("Disassembly byte mismatch")
                checked.extend(code)
            if not checked: raise ValueError("No instructions for selected method")
            target = output / f"{name}.asm.txt"; target.write_text(text)
            rows.append({"method": symbol, "start": instructions[0][0], "last_instruction": instructions[-1][0],
                         "instruction_bytes": len(checked), "instruction_sha256": digest(checked),
                         "text": target.name, "text_sha256": digest(target.read_bytes())})
    finally:
        (output/"symbols.a2s").unlink(missing_ok=True)
    result = {"hardware": "iPhone17,3", "os_build": "24A446", "source_uuid": uid, "source_sha256": digest(raw),
              "methods": rows, "source_instructions_checked": True, "ios_code_executed": False,
              "runtime_dispatch_verified": False}
    (output/"manifest.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("binary", type=Path); p.add_argument("output", type=Path)
    a = p.parse_args(); r = export(a.binary, a.output)
    print(json.dumps({"methods": len(r["methods"]), "instruction_bytes": sum(m["instruction_bytes"] for m in r["methods"])}))
