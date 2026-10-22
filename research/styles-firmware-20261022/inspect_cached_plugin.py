"""Read an existing iOS bundle; retain identities and selected static text only.

Never loads/executes the iOS library. ipsw disassembly bytes are checked back
against LC_SEGMENT_64 file mappings. AIR extraction reuses the S110 wrapper
layout and the already installed llvm-dis; no package installation is needed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import plistlib
import re
import struct
import subprocess
import tempfile
import uuid

SELECTORS = [
    "createLinearThumbnailFromMetadata:ltmThumbnailPixelBuffer:cameraInfo:applyGDC:toPixelBuffer:",
    "createLinearThumbnailFromMetadata:preLTMThumbnailPixelBuffer:postLTMThumbnailPixelBuffer:cameraInfo:applyGDC:cropToPreLTMBounds:toPixelBuffer:",
    "createLinearThumbnailFromMetadata:postLTMThumbnailPixelBuffer:cameraInfo:applyGDC:cropToPreLTMBounds:toPixelBuffer:",
    "_compileShaders",
    "_createGlobalToneCurveTextureFromMetadataDict:",
]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def macho_layout(data: bytes) -> tuple[str, list[tuple[int, int, int]]]:
    if data[:4] != b"\xcf\xfa\xed\xfe":
        raise ValueError("Expected little-endian 64-bit Mach-O")
    ncmds = struct.unpack_from("<I", data, 16)[0]
    pos, uid, segments = 32, "", []
    for _ in range(ncmds):
        cmd, size = struct.unpack_from("<II", data, pos)
        if size < 8 or pos + size > len(data):
            raise ValueError("Invalid load command")
        if cmd == 0x1b:
            uid = str(uuid.UUID(bytes=data[pos+8:pos+24])).upper()
        if cmd == 0x19:
            vm, _, off, length = struct.unpack_from("<QQQQ", data, pos + 24)
            segments.append((vm, off, length))
        pos += size
    if not uid:
        raise ValueError("No LC_UUID")
    return uid, segments


def inspect(bundle: Path, out: Path, llvm_dis: str) -> dict:
    info = plistlib.loads((bundle / "Info.plist").read_bytes())
    binary = bundle / info["CFBundleExecutable"]
    data = binary.read_bytes()
    uid, segments = macho_layout(data)
    out.mkdir(parents=True, exist_ok=False)
    result = {"bundle_name": bundle.name, "binary_bytes": len(data), "binary_sha256": digest(data), "uuid": uid,
              "info": {k: info.get(k) for k in ("CFBundleIdentifier", "CFBundleVersion", "CFBundleShortVersionString", "DTSDKBuild", "MinimumOSVersion")},
              "cache_origin_is_historical_assertion": True, "container_membership_independently_verified": False,
              "ios_code_executed": False, "sample_matching_verified": False, "methods": [], "air": [], "files": []}
    for index, selector in enumerate(SELECTORS):
        symbol = f"-[CMISmartStyleProcessorUtilitiesV1 {selector}]"
        text = subprocess.check_output(["ipsw", "macho", "disass", "--symbol", symbol,
                                        "--cache", str(out / "symbols.a2s"), str(binary)], text=True)
        instructions = re.findall(r"^(0x[0-9a-f]+):\s+((?:[0-9a-f]{2} ){3}[0-9a-f]{2})\s", text, re.M)
        checked = bytearray()
        for addr, code in instructions:
            address = int(addr, 16)
            vm, off, _ = next(s for s in segments if s[0] <= address < s[0] + s[2])
            raw = bytes.fromhex(code)
            if data[off + address - vm:off + address - vm + 4] != raw:
                raise ValueError("Disassembler bytes do not match source file")
            checked.extend(raw)
        if not instructions:
            raise ValueError(f"No instructions for {symbol}")
        name = f"linear-{index}.asm.txt"
        (out / name).write_text(text)
        result["methods"].append({"symbol": symbol, "start": instructions[0][0], "last_instruction": instructions[-1][0],
                                  "checked_instruction_bytes": len(checked), "instruction_sha256": digest(checked), "text": name})
    lib = (bundle / "default.metallib").read_bytes()
    result["metallib_sha256"] = digest(lib)
    result["llvm_version"] = subprocess.check_output([llvm_dis, "--version"], text=True).splitlines()[0]
    with tempfile.TemporaryDirectory(prefix="psr-air-") as temp:
        for index, match in enumerate(re.finditer(b"\xde\xc0\x17\x0b", lib)):
            start = match.start()
            if start + 20 > len(lib):
                continue
            _, _, offset, size, _ = struct.unpack_from("<5I", lib, start)
            payload = lib[start+offset:start+offset+size]
            if payload[:4] != b"BC\xc0\xde" or len(payload) != size:
                continue
            bc = Path(temp) / "module.bc"
            bc.write_bytes(payload)
            name = f"air-{index}.ll.txt"
            text = subprocess.check_output([llvm_dis, str(bc), "-o", "-"], text=True)
            # LLVM's ModuleID contains the private scratch path, not source identity.
            text = re.sub(r"^; ModuleID = .*\n", "; ModuleID = 'cached-plugin-payload'\n", text)
            functions = re.findall(r'^define .*?@(?:"([^"]+)"|([^ (]+))', text, re.M)
            # Only retain three relevant shader modules; inventory the remainder.
            selected = any(token in text for token in ("smartStyleExtractLTMThumbnail", "smartStyleCreateLinearThumbnail"))
            row = {"index": index, "wrapper_offset": start, "payload_bytes": size, "payload_sha256": digest(payload),
                   "functions": [a or b for a, b in functions], "selected": selected}
            if selected:
                (out / name).write_text(text)
                row["text"] = name
            result["air"].append(row)
    for path in (out / "symbols.a2s",):
        path.unlink(missing_ok=True)
    for path in sorted(bundle.glob("*.plist")):
        raw = path.read_bytes()
        result["files"].append({"name": path.name, "sha256": digest(raw), "bytes": len(raw)})
    for path in sorted(out.iterdir()):
        result["files"].append({"name": path.name, "sha256": digest(path.read_bytes()), "bytes": path.stat().st_size})
    (out / "inventory.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("bundle", type=Path); p.add_argument("output", type=Path)
    p.add_argument("--llvm-dis", default="/opt/homebrew/opt/llvm/bin/llvm-dis")
    args = p.parse_args()
    report = inspect(args.bundle, args.output, args.llvm_dis)
    print(json.dumps({"uuid": report["uuid"], "methods": len(report["methods"]), "air_modules": len(report["air"]),
                      "checked_instruction_bytes": sum(r["checked_instruction_bytes"] for r in report["methods"])}))
