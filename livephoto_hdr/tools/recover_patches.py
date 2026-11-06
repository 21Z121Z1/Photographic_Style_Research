#!/usr/bin/env python3
"""Replay archival Codex apply_patch records into a recovered tree.

This is a recovery aid. It is not a claim that the result is byte-identical
to the offline Mac disk. Shell copies are seeded only where S12 raw L44
names the source, and only after that source has itself been patched.
Scene-guided grading files are recorded and then omitted: that work belongs
to branch research/livephoto-scene-grading-pilot-20261106.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

SKIP_PREFIXES = (
    "/Users/retriedstormtrooper/Documents/Projects/Active/proxdrtest/artifacts/research/20261106-scene-guided-grading/",
)
COPY_SEED = {
    "/Users/retriedstormtrooper/Downloads/LivePhotoHDR/src/native.m":
        "/Users/retriedstormtrooper/Documents/Projects/Active/proxdrtest/artifacts/research/20261106-native-hdr-independent/src/native.m",
    "/Users/retriedstormtrooper/Downloads/LivePhotoHDR/src/fit.py":
        "/Users/retriedstormtrooper/Documents/Projects/Active/proxdrtest/artifacts/research/20261106-native-hdr-independent/src/fit.py",
    "/Users/retriedstormtrooper/Downloads/LivePhotoHDR/src/package.py":
        "/Users/retriedstormtrooper/Documents/Projects/Active/proxdrtest/artifacts/research/20261106-native-hdr-independent/src/package.py",
}
DECLARED_UNPATCHED_COPIES = {
    "/Users/retriedstormtrooper/Downloads/LivePhotoHDR/src/validate.py":
        "/Users/retriedstormtrooper/Documents/Projects/Active/proxdrtest/artifacts/research/20261106-native-hdr-independent/src/validate.py",
    "/Users/retriedstormtrooper/Downloads/LivePhotoHDR/src/extract.py":
        "/Users/retriedstormtrooper/Documents/Projects/Active/proxdrtest/artifacts/research/20261106-still-video-linear-thumbnail-pair/src/extract.py",
}


def _rel(path: str) -> str:
    for prefix in (
        "/Users/retriedstormtrooper/Documents/Projects/Active/proxdrtest/",
        "/Users/retriedstormtrooper/Downloads/",
    ):
        if path.startswith(prefix):
            return path[len(prefix):]
    return path.lstrip("/")


def _hunks(body: str) -> list[list[str]]:
    hunks: list[list[str]] = []
    current: list[str] | None = None
    for raw in body.splitlines():
        if raw.startswith("***"):
            break
        if raw.startswith("@@"):
            if current is not None:
                hunks.append(current)
            current = []
            continue
        if current is None or raw.startswith("\\"):
            continue
        current.append(raw)
    if current is not None:
        hunks.append(current)
    return hunks


def _apply_update(text: str, body: str, label: str) -> str:
    content = text.splitlines()
    cursor = 0
    for hunk in _hunks(body):
        old: list[str] = []
        new: list[str] = []
        for raw in hunk:
            if raw.startswith("+"):
                new.append(raw[1:])
            elif raw.startswith("-"):
                old.append(raw[1:])
            elif raw.startswith(" "):
                old.append(raw[1:])
                new.append(raw[1:])
            else:
                raise RuntimeError(f"{label}: hunk line without a prefix: {raw!r}")
        if not old:
            raise RuntimeError(f"{label}: empty search hunk")
        found = []
        limit = len(content) - len(old) + 1
        for index in range(cursor, max(cursor, limit)):
            if content[index:index + len(old)] == old:
                found.append(index)
        if not found:
            preview = "\n".join(old[:6])
            raise RuntimeError(f"{label}: hunk not found after line {cursor}:\n{preview}")
        if len(found) > 1:
            raise RuntimeError(f"{label}: ambiguous hunk at {found}: {old[:2]!r}")
        at = found[0]
        content[at:at + len(old)] = new
        context_only = all(raw.startswith(" ") for raw in hunk)
        cursor = at if context_only else at + len(new)
    out = "\n".join(content)
    if text.endswith("\n"):
        out += "\n"
    return out


def recover(jsonl: Path) -> tuple[dict[str, str], list[dict]]:
    files: dict[str, str] = {}
    report: list[dict] = []
    for index, line in enumerate(jsonl.read_text().splitlines()):
        if not line.strip():
            continue
        record = json.loads(line)
        patch = record["patch"]
        header = None
        buf: list[str] = []
        ops: list[tuple[str, str]] = []
        for raw in patch.splitlines(keepends=True):
            if raw.startswith("*** Begin Patch") or raw.startswith("*** End Patch"):
                continue
            if raw.startswith("*** Add File:") or raw.startswith("*** Update File:") or raw.startswith("*** Delete File:"):
                if header:
                    ops.append((header, "".join(buf)))
                header = raw.strip()
                buf = []
            else:
                buf.append(raw)
        if header:
            ops.append((header, "".join(buf)))
        for op, body in ops:
            kind, path = op.split(":", 1)
            path = path.strip()
            skipped = path.startswith(SKIP_PREFIXES)
            entry = {
                "record": index,
                "rawLine": record["raw_line"],
                "timestampSgt": record["timestamp_sgt"],
                "patchSha256": record["patch_sha256"],
                "op": kind.replace("*** ", ""),
                "path": path,
            }
            if skipped:
                entry["result"] = "intentionally-not-materialized"
                entry["reason"] = "scene-guided grading pilot is owned by research/livephoto-scene-grading-pilot-20261106"
                report.append(entry)
                continue
            if kind.startswith("*** Add File"):
                lines = []
                for raw in body.splitlines():
                    if raw.startswith("\\"):
                        continue
                    if not raw.startswith("+"):
                        raise RuntimeError(f"record {index}: add line {raw!r}")
                    lines.append(raw[1:])
                files[path] = "\n".join(lines) + ("\n" if lines else "")
                entry["result"] = "added"
            elif kind.startswith("*** Update File"):
                if path not in files and path in COPY_SEED:
                    source = COPY_SEED[path]
                    if source not in files:
                        raise RuntimeError(f"record {index}: copy seed {source} is not recovered yet")
                    files[path] = files[source]
                    entry["preimage"] = "S12 raw L44 copy of the patched independent file; the cp itself is not a patch record"
                if path not in files:
                    entry["result"] = "missing-preimage"
                    report.append(entry)
                    continue
                files[path] = _apply_update(files[path], body, f"record {index} {path}")
                entry["result"] = "updated"
            else:
                entry["result"] = "unsupported-op"
            report.append(entry)
    for destination, source in DECLARED_UNPATCHED_COPIES.items():
        if destination in files:
            continue
        if source not in files:
            report.append({"path": destination, "result": "missing-preimage", "reason": f"{source} was not recovered"})
            continue
        files[destination] = files[source]
        report.append({
            "path": destination,
            "result": "seeded-unpatched-copy",
            "preimage": source,
            "reason": "S12 raw L44 copied this file and no later patch updates it",
        })
    return files, report


def write_tree(files: dict[str, str], report: list[dict], root: Path, jsonl: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    written = []
    for path, text in sorted(files.items()):
        if path.startswith(SKIP_PREFIXES):
            continue
        destination = root / _rel(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(text)
        written.append({
            "recoveredPath": str(destination.relative_to(root)),
            "sourcePath": path,
            "sha256": hashlib.sha256(text.encode()).hexdigest(),
            "bytes": len(text.encode()),
        })
    manifest = {
        "schema": "livephoto-hdr-patch-recovery-v1",
        "sourcePatchesSha256": hashlib.sha256(jsonl.read_bytes()).hexdigest(),
        "sourcePatchesBytes": jsonl.stat().st_size,
        "parallelBranchNotTouched": "research/livephoto-scene-grading-pilot-20261106",
        "files": written,
        "operations": report,
    }
    (root / "recovery-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("jsonl", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    files, report = recover(args.jsonl)
    failed = [item for item in report if item.get("result") in {"missing-preimage", "unsupported-op"}]
    if failed:
        raise SystemExit(json.dumps(failed, indent=2))
    write_tree(files, report, args.output, args.jsonl)
    print(f"recovered {len(files)} files into {args.output}")


if __name__ == "__main__":
    main()
