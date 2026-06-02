#!/usr/bin/env python3
"""Run Apple-native HEIF parseability gates and write a structured report."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


def _json_from_text(text: str) -> dict[str, Any]:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        return {"ok": False, "error": "no JSON object in output", "raw": text}
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError as exc:
        return {"ok": False, "error": str(exc), "raw": text}


def parse_imageio_result(stdout: str) -> dict[str, Any]:
    parsed = _json_from_text(stdout)
    parsed["ok"] = bool(parsed.get("ok")) and int(parsed.get("count", 0) or 0) > 0
    return parsed


def parse_sips_result(stdout: str) -> dict[str, Any]:
    result: dict[str, Any] = {"pixelWidth": None, "pixelHeight": None, "format": None}
    for raw_line in stdout.splitlines():
        line = raw_line.strip()
        if ":" not in line:
            continue
        key, value = [part.strip() for part in line.split(":", 1)]
        if key in {"pixelWidth", "pixelHeight"}:
            result[key] = None if value == "<nil>" else int(value)
        elif key == "format":
            result["format"] = value
    result["ok"] = isinstance(result["pixelWidth"], int) and isinstance(result["pixelHeight"], int)
    return result


def run_command(command: list[str], *, timeout: float = 30.0) -> dict[str, Any]:
    try:
        completed = subprocess.run(command, capture_output=True, text=True, timeout=timeout, check=False)
        return {
            "command": command,
            "exit_code": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "timed_out": False,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": command,
            "exit_code": None,
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
            "timed_out": True,
        }
    except FileNotFoundError as exc:
        return {
            "command": command,
            "exit_code": None,
            "stdout": "",
            "stderr": str(exc),
            "timed_out": False,
            "missing_command": True,
        }


def summarize_hard_failures(report: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    heif_info = report.get("heif_info", {})
    if heif_info.get("exit_code") != 0:
        failures.append("heif-info failed")
    if not report.get("sips", {}).get("parsed", {}).get("ok"):
        failures.append("sips did not report primary pixel dimensions")
    if not report.get("imageio", {}).get("parsed", {}).get("ok"):
        failures.append("ImageIO validator did not decode the primary image")
    quicklook = report.get("quicklook", {})
    if not quicklook.get("skipped") and not quicklook.get("thumbnail_created"):
        failures.append("QuickLook did not create a thumbnail")
    return failures


def run_quicklook(image: Path, *, output_dir: Path | None, timeout: float) -> dict[str, Any]:
    owns_temp_dir = output_dir is None
    temp_dir: tempfile.TemporaryDirectory[str] | None = None
    if output_dir is None:
        temp_dir = tempfile.TemporaryDirectory(prefix="apple_parseability_ql_")
        output_dir = Path(temp_dir.name)
    output_dir.mkdir(parents=True, exist_ok=True)
    before = {path.name for path in output_dir.iterdir()}
    command_result = run_command(["qlmanage", "-t", "-s", "512", "-o", str(output_dir), str(image)], timeout=timeout)
    after_paths = list(output_dir.iterdir())
    created = sorted(path.name for path in after_paths if path.name not in before)
    result = {
        **command_result,
        "output_dir": str(output_dir),
        "created_files": created,
        "thumbnail_created": bool(created) and command_result.get("exit_code") == 0,
        "skipped": False,
    }
    if owns_temp_dir and temp_dir is not None:
        temp_dir.cleanup()
    return result


def validate_image(
    image: Path,
    *,
    swift_validator: Path,
    quicklook_output_dir: Path | None,
    quicklook_timeout: float,
    skip_quicklook: bool,
    heif_json: Path | None,
    heif_md: Path | None,
    semantic_json: Path | None,
    semantic_md: Path | None,
) -> dict[str, Any]:
    report: dict[str, Any] = {"image": str(image)}
    report["heif_info"] = run_command(["heif-info", str(image)], timeout=30)
    sips = run_command(["sips", "-g", "pixelWidth", "-g", "pixelHeight", "-g", "format", str(image)], timeout=30)
    sips["parsed"] = parse_sips_result(sips.get("stdout", ""))
    report["sips"] = sips
    imageio = run_command(["swift", str(swift_validator), str(image)], timeout=30)
    imageio["parsed"] = parse_imageio_result(imageio.get("stdout", ""))
    report["imageio"] = imageio
    if skip_quicklook:
        report["quicklook"] = {"skipped": True, "thumbnail_created": None}
    else:
        report["quicklook"] = run_quicklook(image, output_dir=quicklook_output_dir, timeout=quicklook_timeout)

    if heif_json is not None or heif_md is not None:
        command = [sys.executable, "tools/heif_dump.py", str(image)]
        if heif_json is not None:
            command += ["--json", str(heif_json)]
        if heif_md is not None:
            command += ["--md", str(heif_md)]
        report["heif_dump"] = run_command(command, timeout=30)
    if semantic_json is not None or semantic_md is not None:
        command = [sys.executable, "tools/semantic_fitter.py", str(image)]
        if semantic_json is not None:
            command += ["--json", str(semantic_json)]
        if semantic_md is not None:
            command += ["--md", str(semantic_md)]
        report["semantic_fitter"] = run_command(command, timeout=60)

    report["hard_failures"] = summarize_hard_failures(report)
    report["ok"] = not report["hard_failures"]
    return report


def _markdown(report: dict[str, Any]) -> str:
    sips = report.get("sips", {}).get("parsed", {})
    imageio = report.get("imageio", {}).get("parsed", {})
    quicklook = report.get("quicklook", {})
    lines = [
        "# Apple Parseability Report",
        "",
        f"- Image: `{report.get('image')}`",
        f"- Overall: {'PASS' if report.get('ok') else 'FAIL'}",
        f"- Hard failures: {', '.join(report.get('hard_failures', [])) or 'none'}",
        f"- heif-info exit: {report.get('heif_info', {}).get('exit_code')}",
        f"- sips: {sips.get('pixelWidth')}x{sips.get('pixelHeight')} format={sips.get('format')}",
        f"- ImageIO: ok={imageio.get('ok')} count={imageio.get('count')} "
        f"size={imageio.get('pixelWidth')}x{imageio.get('pixelHeight')}",
        f"- QuickLook: skipped={quicklook.get('skipped')} thumbnail_created={quicklook.get('thumbnail_created')}",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--swift-validator", type=Path, default=Path("tools/apple_imageio_validate.swift"))
    parser.add_argument("--json", type=Path)
    parser.add_argument("--md", type=Path)
    parser.add_argument("--skip-quicklook", action="store_true")
    parser.add_argument("--quicklook-output-dir", type=Path)
    parser.add_argument("--quicklook-timeout", type=float, default=20.0)
    parser.add_argument("--heif-json", type=Path)
    parser.add_argument("--heif-md", type=Path)
    parser.add_argument("--semantic-json", type=Path)
    parser.add_argument("--semantic-md", type=Path)
    args = parser.parse_args()

    report = validate_image(
        args.image,
        swift_validator=args.swift_validator,
        quicklook_output_dir=args.quicklook_output_dir,
        quicklook_timeout=args.quicklook_timeout,
        skip_quicklook=args.skip_quicklook,
        heif_json=args.heif_json,
        heif_md=args.heif_md,
        semantic_json=args.semantic_json,
        semantic_md=args.semantic_md,
    )
    if args.json is not None:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    if args.md is not None:
        args.md.parent.mkdir(parents=True, exist_ok=True)
        args.md.write_text(_markdown(report))
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
