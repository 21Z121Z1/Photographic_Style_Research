"""Download one manifest-selected stored ZIP component with a fixed byte cap.

Only explicit, already-probed Apple metadata is accepted. No whole-IPSW
fallback, automatic retry or deletion; downloaded Apple bytes stay outside Git.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import struct
import urllib.request
import zlib

from firmware_probe import AppleRanges


def select_component(metadata: dict, role: str, variant: str) -> dict:
    names = {i["components"][role] for i in metadata["identities"]
             if i["variant"] == variant and role in i["components"]}
    if len(names) != 1:
        raise ValueError("Choose one unambiguous manifest filesystem role")
    entry = next(e for e in metadata["image_entries"] if e["name"] in names)
    if entry["method"] != 0 or entry["compressed_bytes"] != entry["uncompressed_bytes"]:
        raise ValueError("Only stored components supported")
    if Path(entry["name"]).name != entry["name"] or entry["compressed_bytes"] > 10 * 1024**3:
        raise ValueError("Unsafe component name or size budget exceeded")
    return entry


def download(metadata_path: Path, role: str, out: Path, variant: str) -> None:
    metadata = json.loads(metadata_path.read_text())
    url = metadata["source_url"]; AppleRanges.check_url(url)
    entry = select_component(metadata, role, variant)
    out.mkdir(parents=True, exist_ok=False)
    n = entry["compressed_bytes"]
    required = 3 * n + 4 * 1024**3
    free = shutil.disk_usage(out).free
    if free < required:
        raise ValueError(f"Need {required} free bytes including decrypt allowance; have {free}")
    state = {"source_url": url, "build": metadata["build"], "device": metadata["supported_product_types"],
             "build_manifest_sha256": metadata["build_manifest_sha256"], "variant": variant, "entry": entry, "disk_free_before": free,
             "disk_required": required, "received_bytes": 0, "completed": False, "whole_ipsw_downloaded": False}
    def save():
        (out / "download.json").write_text(json.dumps(state, indent=2) + "\n")
    def part(start: int, count: int) -> bytes:
        if not 0 < count <= 16 * 1024**2 or state["received_bytes"] + count > n + 4096:
            raise ValueError("Download budget exceeded")
        request = urllib.request.Request(url, headers={"Range": f"bytes={start}-{start+count-1}", "Accept-Encoding": "identity"})
        with urllib.request.urlopen(request, timeout=60) as response:
            AppleRanges.check_url(response.geturl())
            if response.status != 206 or response.headers.get("Content-Range") != f"bytes {start}-{start+count-1}/{metadata['ipsw_total_bytes']}":
                raise ValueError("Exact206 required; no whole-IPSW response fallback")
            data = response.read(count + 1)
            state["received_bytes"] += len(data)
            if len(data) != count:
                raise ValueError("Range body length mismatch")
            return data
    save()
    try:
        header = part(entry["local_header_offset"], 30)
        if header[:4] != b"PK\x03\x04" or struct.unpack_from("<H", header, 8)[0] != 0:
            raise ValueError("Component local-header mismatch")
        nn, en = struct.unpack_from("<HH", header, 26)
        if part(entry["local_header_offset"] + 30, nn).decode() != entry["name"]:
            raise ValueError("Component filename mismatch")
        offset = entry["local_header_offset"] + 30 + nn + en
        sha, crc = hashlib.sha256(), 0
        with (out / entry["name"]).open("xb") as target:
            for start in range(0, n, 16 * 1024**2):
                block = part(offset + start, min(16 * 1024**2, n - start))
                target.write(block); sha.update(block); crc = zlib.crc32(block, crc)
                state["component_written_bytes"] = start + len(block)
                if start % (256 * 1024**2) == 0:
                    save(); print(f"{state['component_written_bytes']}/{n}", flush=True)
        if f"{crc:08x}" != entry["crc32"]:
            raise ValueError("Downloaded component CRC mismatch")
        state.update(completed=True, sha256=sha.hexdigest(), zip_crc_verified=True)
        save()
    except Exception as error:
        state["error"] = str(error); save(); raise


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("metadata", type=Path); p.add_argument("role", choices=["OS", "Cryptex1,SystemOS"]); p.add_argument("output", type=Path)
    p.add_argument("--variant", default="Customer Erase Install (IPSW)")
    args = p.parse_args(); download(args.metadata, args.role, args.output, args.variant)
