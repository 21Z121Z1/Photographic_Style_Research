"""Inventory an already-mounted owned OS image without following symlinks.

Resolve the plugin's Mach-O library ordinals as static import evidence. This
does not resolve Objective-C dispatch to method bodies or claim runtime loads.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import plistlib
import shutil
import stat
import struct

FRAMEWORKS = ["CMCapture", "CMCaptureCore", "CMImaging", "CameraColorProcessing", "PhotoImaging"]
INTEREST = ["CMISmartStyle", "CMIStyleEngine", "CMISubjectRelightingStage", "CMITexture"]


def imports(data: bytes) -> dict:
    if data[:4] != b"\xcf\xfa\xed\xfe":
        raise ValueError("Expected little-endian 64-bit Mach-O")
    count = struct.unpack_from("<I", data, 16)[0]
    pos, libraries, table = 32, [], None
    for _ in range(count):
        cmd, size = struct.unpack_from("<II", data, pos)
        if size < 8 or pos + size > len(data):
            raise ValueError("Malformed Mach-O command")
        if cmd in [0xc, 0x80000018, 0x8000001f, 0x80000023]:
            off = struct.unpack_from("<I", data, pos + 8)[0]
            name = data[pos+off:pos+size].split(b"\0", 1)[0].decode()
            libraries.append(name)
        if cmd == 2:
            table = struct.unpack_from("<IIII", data, pos + 8)
        pos += size
    selected = []
    if table:
        symoff, nsyms, stroff, strsize = table
        if symoff + 16*nsyms > len(data) or stroff + strsize > len(data):
            raise ValueError("Symbol table outside file")
        strings = data[stroff:stroff+strsize]
        for i in range(nsyms):
            index, kind, section, desc, value = struct.unpack_from("<IBBHQ", data, symoff+16*i)
            if kind & 0xe or not kind & 1 or value or index >= len(strings):
                continue
            name = strings[index:].split(b"\0", 1)[0].decode()
            if not any(t in name for t in INTEREST):
                continue
            ordinal = desc >> 8
            selected.append({"symbol": name, "library_ordinal": ordinal,
                             "library": libraries[ordinal-1] if 1 <= ordinal <= len(libraries) else None})
    return {"source_sha256": hashlib.sha256(data).hexdigest(), "load_dylibs": libraries, "selected_imports": selected,
            "dispatch_implementation_verified": False}


def inspect_node(root: Path, relative: str) -> dict:
    parts = Path(relative).parts
    if Path(relative).is_absolute() or ".." in parts:
        raise ValueError("Supply a contained relative path")
    node = root
    for index, part in enumerate(parts):
        node = node / part
        try:
            mode = node.lstat().st_mode
        except FileNotFoundError:
            return {"path": relative, "status": "absent", "first_missing": str(Path(*parts[:index+1]))}
        if stat.S_ISLNK(mode):
            return {"path": relative, "status": "symlink_not_followed", "at": str(Path(*parts[:index+1])), "target": os.readlink(node)}
    result = {"path": relative}
    if node.is_dir():
        children = sorted(p.name for p in node.iterdir())
        result.update(status="directory", children=children[:80], child_count=len(children))
    elif node.is_file():
        result.update(status="file", bytes=node.stat().st_size)
        if node.stat().st_size <= 32*1024**2:
            raw = node.read_bytes(); result["sha256"] = hashlib.sha256(raw).hexdigest()
            if node.suffix == ".plist":
                obj = plistlib.loads(raw)
                result["selected_info"] = {k: obj[k] for k in ["DTPlatformName", "DTSDKBuild", "DTSDKName", "CFBundleIdentifier"] if k in obj}
    else:
        result["status"] = "other"
    return result


def inventory(root: Path, scratch: Path, output: Path) -> dict:
    if not os.path.ismount(root):
        raise ValueError("Require an explicitly mounted owned image")
    if output.exists():
        raise FileExistsError(output)
    paths = ["System/Library/dyld", "System/Cryptexes/OS", "usr/lib/dyld"]
    for name in FRAMEWORKS:
        base = f"System/Library/PrivateFrameworks/{name}.framework"
        paths += [base, f"{base}/{name}", f"{base}/Info.plist", f"{base}/default.metallib"]
    paths += [f"System/Library/PrivateFrameworks/CMImaging.framework/{name}.plist"
              for name in ["SmartStyleTuning", "SmartStyleCastSpecificStyleEngineTuning", "StyleEngineTuning", "RendererTuning", "TextureStyleTuning"]]
    nodes = [inspect_node(root, path) for path in paths]
    bundle = "System/Library/VideoProcessors/SmartStyleV1.bundle"
    selected = scratch / "selected"; selected.mkdir(exist_ok=False)
    for relative in [f"{bundle}/{n}" for n in ["SmartStyleV1", "Info.plist", "SmartStyleProcessorV1-Tuning.plist", "default.metallib"]]:
        row = inspect_node(root, relative)
        if row["status"] != "file":
            raise ValueError("Actual plugin file unavailable without symlink traversal")
        target = selected / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(root / relative, target)
        if hashlib.sha256(target.read_bytes()).hexdigest() != row["sha256"]:
            raise ValueError("Owned selected-file copy mismatch")
    plugin = selected / bundle / "SmartStyleV1"
    imported = imports(plugin.read_bytes())
    if imported["source_sha256"] != "04dbdad52b959f848ba1d8de07f4fc81c85d1595c8843637a1dc905039112216":
        raise ValueError("Unexpected official plugin identity")
    resource_dir = "System/Library/PrivateFrameworks/CMImaging.framework"
    resources = []
    for name in ["SmartStyleTuning", "SmartStyleCastSpecificStyleEngineTuning", "StyleEngineTuning", "RendererTuning", "TextureStyleTuning"]:
        rel = f"{resource_dir}/{name}.plist"
        row = next(r for r in nodes if r["path"] == rel)
        if row["status"] == "file":
            obj = plistlib.loads((root / rel).read_bytes())
            resources.append({"path": rel, "sha256": row["sha256"], "top_level_keys": list(obj)[:30]})
    result = {"hardware": "iPhone17,3", "image_build": "24A446", "nodes": nodes,
              "plugin_imports": imported, "available_tuning": resources, "new_network_download_bytes": 0,
              "symlinks_followed": False, "ios_code_executed": False,
              "static_import_not_runtime_dispatch": True}
    output.write_text(json.dumps(result, indent=2) + "\n")
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("root", type=Path); p.add_argument("scratch", type=Path); p.add_argument("output", type=Path)
    a = p.parse_args(); result = inventory(a.root, a.scratch, a.output)
    print(json.dumps({"selected_imports": result["plugin_imports"]["selected_imports"], "new_network_download_bytes": 0}))
