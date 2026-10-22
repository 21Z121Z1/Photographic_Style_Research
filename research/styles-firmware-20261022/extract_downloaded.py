"""Decrypt one verified owned component, read-only mount, export plugin text.

Consumes download_component.py's completed receipt. No automatic redownload,
installation, firmware execution, credentials or changes to system settings.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import plistlib
import shutil
import subprocess
import time

from inspect_cached_plugin import inspect


def sha_file(path: Path) -> str:
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def extract(scratch: Path, output: Path) -> None:
    scratch, output = scratch.resolve(), output.resolve()
    download = json.loads((scratch / "download.json").read_text())
    if not download["completed"] or not download["zip_crc_verified"]:
        raise ValueError("Download has not passed complete CRC verification")
    encrypted = scratch / download["entry"]["name"]
    if encrypted.stat().st_size != download["entry"]["compressed_bytes"] or sha_file(encrypted) != download["sha256"]:
        raise ValueError("Downloaded component identity changed")
    if output.exists():
        raise FileExistsError(output)
    output.mkdir(parents=True)
    state = {"firmware_build": download["build"], "hardware": download["device"],
             "source_url": download["source_url"], "build_manifest_sha256": download["build_manifest_sha256"],
             "encrypted_component_sha256": download["sha256"], "source_component": download["entry"],
             "completed": False, "ios_library_executed": False, "apple_binary_uploaded": False}
    def save():
        (output / "extraction.json").write_text(json.dumps(state, indent=2) + "\n")
    def run(args: list[str], log: Path, timeout: int) -> None:
        with log.open("w") as f:
            result = subprocess.run(args, stdout=f, stderr=subprocess.STDOUT, timeout=timeout)
        if result.returncode:
            raise RuntimeError(f"{args[0]} failed rc={result.returncode}; inspect private scratch log {log.name}")
    mount = scratch / "mount"
    started = time.monotonic()
    try:
        if shutil.disk_usage(scratch).free < 2 * encrypted.stat().st_size + 4 * 1024**3:
            raise ValueError("Insufficient decrypt workspace and reserve")
        decrypted = scratch / "decrypted"; decrypted.mkdir(exist_ok=False)
        state["stage"] = "public-AEA-decrypt"; save()
        run(["ipsw", "fw", "aea", str(encrypted), "--pem-db", str(scratch / "fcs-keys.json"),
             "--output", str(decrypted)], scratch / "decrypt.log", 900)
        images = list(decrypted.glob("*.dmg"))
        if len(images) != 1:
            raise ValueError("Expected one decrypted image")
        image = images[0]
        state.update(decrypted_image_bytes=image.stat().st_size, decrypted_image_sha256=sha_file(image), stage="readonly-mount")
        save(); mount.mkdir(exist_ok=False)
        attached = subprocess.run(["hdiutil", "attach", "-readonly", "-nobrowse", "-plist", "-mountpoint", str(mount), str(image)],
                                  capture_output=True, timeout=180)
        (scratch / "mount.stderr").write_bytes(attached.stderr)
        if attached.returncode:
            raise RuntimeError(f"Read-only image attachment failed rc={attached.returncode}")
        plist = plistlib.loads(attached.stdout)
        (scratch / "attachment.plist").write_bytes(attached.stdout)
        if not any(q.get("mount-point") == str(mount) for q in plist["system-entities"]):
            raise ValueError("Unexpected attachment mountpoint")
        state["read_only_attachment"] = True
        sv = mount / "System/Library/CoreServices/SystemVersion.plist"
        if sv.exists():
            version = plistlib.loads(sv.read_bytes())
            state["image_system_version"] = {k: version.get(k) for k in ("ProductVersion", "ProductBuildVersion")}
            if version.get("ProductBuildVersion") != download["build"]:
                raise ValueError("Mounted image build mismatch")
        parent = mount / "System/Library/VideoProcessors"
        state["video_processor_children"] = sorted(p.name for p in parent.iterdir()) if parent.exists() else []
        candidates = [parent / n for n in ("SmartStyleV1.bundle", "SmartStyleV2.bundle", "SmartStyle.bundle") if (parent / n).is_dir()]
        state["actual_candidate_bundles"] = [p.name for p in candidates]; save()
        if not candidates:
            raise RuntimeError("No target plugin in verified OS image; no substitute claimed")
        for bundle in candidates:
            inventory = inspect(bundle, output / bundle.name, "/opt/homebrew/opt/llvm/bin/llvm-dis")
            inventory.update(cache_origin_is_historical_assertion=False, container_membership_independently_verified=True,
                             official_container_build=download["build"], official_container_hardware=download["device"],
                             official_container_component_sha256=download["sha256"])
            (output / bundle.name / "inventory.json").write_text(json.dumps(inventory, indent=2) + "\n")
        state["completed"] = True
        state["scope"] = "Verified official component to plugin static text; actual loader selection and sample capture build remain separate"
        save()
    except Exception as error:
        state["error"] = str(error); save(); raise
    finally:
        if os.path.ismount(mount):
            detached = subprocess.run(["hdiutil", "detach", str(mount)], capture_output=True, timeout=120)
            (scratch / "detach.log").write_bytes(detached.stdout + detached.stderr)
            state["owned_mount_detached"] = detached.returncode == 0
        state["elapsed_seconds"] = round(time.monotonic() - started, 3)
        save()


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("scratch", type=Path); p.add_argument("output", type=Path)
    args = p.parse_args(); extract(args.scratch, args.output)
