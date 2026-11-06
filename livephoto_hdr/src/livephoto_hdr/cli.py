"""Portable commands. They do not replace input files."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import NATIVE_BLOCK
from .regression import run


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("native-status")
    temporal = sub.add_parser("temporal")
    temporal.add_argument("--mov", type=Path, required=True)
    temporal.add_argument("--heic", type=Path, required=True)
    temporal.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "native-status":
        print(json.dumps(NATIVE_BLOCK, indent=2))
        return
    report = run(args.mov, args.heic, args.output)
    print(json.dumps({
        "output": str(args.output),
        "sha256": report["inputs"]["sha256"],
        "mode": report["classification"]["mode"],
        "nativeExecuted": report["native"]["executed"],
        "longGaps": report["timing"]["longGaps"],
        "heldOutMaeEV": report["heldOutThumbnails"]["summary"],
        "follow": {
            mode: {
                "dxError": values["frame55MinusMainDxCoded"],
                "dyError": values["frame55MinusMainDyCoded"],
            } for mode, values in report["spatialFollow"].get("methods", {}).items()
        },
    }, indent=2))


if __name__ == "__main__":
    main()
