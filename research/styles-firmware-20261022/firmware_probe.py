"""Bounded Apple IPSW metadata reader. No filesystem image download or mount.

Adapted from hdr-native/evidence/s110/repro/firmware_metadata_s110.py.
Separate product/build identity from bundle, SDK and photo metadata versions.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import plistlib
import struct
from typing import Callable
import urllib.request
from urllib.parse import urlsplit
import zlib


@dataclass(frozen=True)
class Entry:
    name: str
    method: int
    crc: int
    compressed: int
    uncompressed: int
    offset: int


def central_entries(raw: bytes, count: int) -> list[Entry]:
    entries: list[Entry] = []
    p = 0
    while p < len(raw):
        if raw[p:p + 4] != b"PK\x01\x02" or p + 46 > len(raw):
            raise ValueError("Malformed central directory")
        method = struct.unpack_from("<H", raw, p + 10)[0]
        crc, comp, size = struct.unpack_from("<III", raw, p + 16)
        nn, en, cn = struct.unpack_from("<HHH", raw, p + 28)
        off = struct.unpack_from("<I", raw, p + 42)[0]
        end = p + 46 + nn + en + cn
        if end > len(raw):
            raise ValueError("Truncated directory entry")
        name = raw[p + 46:p + 46 + nn].decode("utf-8")
        extra = raw[p + 46 + nn:p + 46 + nn + en]
        q = 0
        while q < len(extra):
            if q + 4 > len(extra):
                raise ValueError("Truncated extra field")
            tag, n = struct.unpack_from("<HH", extra, q)
            value = extra[q + 4:q + 4 + n]
            if len(value) != n:
                raise ValueError("Truncated extra value")
            if tag == 1:
                k = 0
                values = [size, comp, off]
                for i, v in enumerate(values):
                    if v == 0xffffffff:
                        values[i] = struct.unpack_from("<Q", value, k)[0]
                        k += 8
                size, comp, off = values
            q += 4 + n
        entries.append(Entry(name, method, crc, comp, size, off))
        p = end
    if len(entries) != count or len({e.name for e in entries}) != count:
        raise ValueError("Directory count or duplicate-name mismatch")
    return entries


class AppleRanges:
    def __init__(self, url: str, *, budget: int = 2 * 1024**2):
        self.check_url(url)
        self.url, self.budget, self.received = url, budget, 0
        with urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=30) as r:
            self.check_url(r.geturl())
            self.size = int(r.headers["Content-Length"])

    @staticmethod
    def check_url(url: str) -> None:
        u = urlsplit(url)
        if (u.scheme != "https" or u.hostname != "updates.cdn-apple.com"
                or u.username or u.password or u.query or u.fragment or u.port not in (None, 443)):
            raise ValueError("Only a public HTTPS Apple firmware CDN URL is accepted")

    def part(self, start: int, n: int) -> bytes:
        if not 0 < n <= 1024**2 or start < 0 or start + n > self.size:
            raise ValueError("Invalid or oversized range")
        if self.received + n > self.budget:
            raise ValueError("Metadata byte budget exceeded")
        request = urllib.request.Request(self.url, headers={"Range": f"bytes={start}-{start+n-1}", "Accept-Encoding": "identity"})
        with urllib.request.urlopen(request, timeout=45) as r:
            self.check_url(r.geturl())
            if r.status != 206 or r.headers.get("Content-Range") != f"bytes {start}-{start+n-1}/{self.size}":
                raise ValueError("Exact HTTP 206 required; no full-file fallback")
            data = r.read(n + 1)
            self.received += len(data)
            if len(data) != n:
                raise ValueError("Short or oversized range body")
            return data


def inspect(size: int, part: Callable[[int, int], bytes], device: str, build: str) -> dict:
    tail_size = min(size, 65557)
    tail = part(size - tail_size, tail_size)
    pos = tail.rfind(b"PK\x05\x06")
    if pos < 0 or pos + 22 > len(tail):
        raise ValueError("ZIP end record unavailable")
    _, disk, cd_disk, _, count, cd_size, cd_off, comment = struct.unpack_from("<IHHHHIIH", tail, pos)
    if disk or cd_disk or pos + 22 + comment != len(tail):
        raise ValueError("Unsupported split ZIP or malformed end record")
    if cd_off == 0xffffffff or cd_size == 0xffffffff or count == 65535:
        locator = pos - 20
        if tail[locator:locator+4] != b"PK\x06\x07":
            raise ValueError("ZIP64 locator unavailable")
        _, disk64, off64, disks = struct.unpack_from("<IIQI", tail, locator)
        if disk64 or disks != 1:
            raise ValueError("Split ZIP64 unsupported")
        record = part(off64, 56)
        if record[:4] != b"PK\x06\x06":
            raise ValueError("Invalid ZIP64 record")
        count, cd_size, cd_off = struct.unpack_from("<QQQ", record, 32)
    directory = part(cd_off, cd_size)
    entries = central_entries(directory, count)
    manifest = next(e for e in entries if e.name == "BuildManifest.plist")
    if manifest.uncompressed > 32 * 1024**2:
        raise ValueError("Manifest output exceeds budget")
    header = part(manifest.offset, 30)
    if header[:4] != b"PK\x03\x04" or struct.unpack_from("<H", header, 8)[0] != manifest.method:
        raise ValueError("Local-header mismatch")
    nn, en = struct.unpack_from("<HH", header, 26)
    local_name = part(manifest.offset + 30, nn)
    if local_name.decode() != manifest.name:
        raise ValueError("Local filename mismatch")
    payload = part(manifest.offset + 30 + nn + en, manifest.compressed)
    if manifest.method == 8:
        d = zlib.decompressobj(-15)
        raw = d.decompress(payload, manifest.uncompressed + 1)
        if not d.eof or d.unconsumed_tail or d.unused_data:
            raise ValueError("Invalid compressed manifest")
    elif manifest.method == 0:
        raw = payload
    else:
        raise ValueError("Unsupported manifest compression")
    if len(raw) != manifest.uncompressed or zlib.crc32(raw) != manifest.crc:
        raise ValueError("Manifest length/CRC mismatch")
    bm = plistlib.loads(raw)
    if device not in bm["SupportedProductTypes"] or bm["ProductBuildVersion"] != build:
        raise ValueError("Firmware device/build does not match requested identity")
    identities = []
    for ident in bm["BuildIdentities"]:
        info = ident.get("Info", {})
        components = {k: v.get("Info", {}).get("Path") for k, v in ident.get("Manifest", {}).items()
                      if k in ("OS", "Cryptex1,SystemOS", "Cryptex1,AppOS")}
        identities.append({"device_class": info.get("DeviceClass"), "variant": info.get("Variant"), "components": components})
    return {"product_version": bm["ProductVersion"], "build": build, "supported_product_types": bm["SupportedProductTypes"],
            "build_manifest_sha256": hashlib.sha256(raw).hexdigest(), "central_directory_sha256": hashlib.sha256(directory).hexdigest(),
            "zip_crc_verified": True, "ipsw_total_bytes": size, "whole_ipsw_sha256": None,
            "identities": identities, "filesystem_image_bytes_downloaded": 0, "plugin_presence_verified": False,
            "sample_capture_build_verified": False}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("url"); p.add_argument("device"); p.add_argument("build"); p.add_argument("output", type=Path)
    a = p.parse_args()
    if a.output.exists():
        p.error("Output already exists")
    remote = AppleRanges(a.url)
    result = inspect(remote.size, remote.part, a.device, a.build)
    result.update(source_url=a.url, metadata_body_bytes=remote.received)
    with a.output.open("x") as f:
        json.dump(result, f, indent=2); f.write("\n")
    print(json.dumps({k: result[k] for k in ("supported_product_types", "build", "metadata_body_bytes", "filesystem_image_bytes_downloaded")}))


if __name__ == "__main__":
    main()
