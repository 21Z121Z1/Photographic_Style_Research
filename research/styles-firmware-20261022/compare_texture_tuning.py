"""Compare one exact hardware/port/mode/preset table, not whole pipelines."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import plistlib


def compare(ios_tuning: Path, mac_tuning: Path) -> dict:
    records, selected = {}, {}
    for name, path in (("cached_ios24A446", ios_tuning), ("macos26A434", mac_tuning)):
        raw = path.read_bytes(); data = plistlib.loads(raw)
        studio = data["iPhone19,2"]["PortTypeBack"]["Still"]["Studio"]["Common"]
        selected[name] = studio
        records[name] = {"file_sha256": hashlib.sha256(raw).hexdigest(), "file_bytes": len(raw),
                         "labels_are_caller_supplied_provenance": True,
                         "selected_path": "iPhone19,2/PortTypeBack/Still/Studio/Common",
                         "selected_canonical_json_sha256": hashlib.sha256(json.dumps(studio, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
                         "effect_order": studio["EffectOrder"], "under_eye_brightness_mix": studio["UnderEyeBrightening"]["brightnessMix"],
                         "mattify_editing_strength": studio["Mattify"]["editingStrength"], "has_iphone17_3_exact_key": "iPhone17,3" in data}
    return {"sources": records, "selected_studio_dictionary_equal": selected["cached_ios24A446"] == selected["macos26A434"],
            "whole_plist_equal": records["cached_ios24A446"]["file_sha256"] == records["macos26A434"]["file_sha256"],
            "interpretation": "Table equality does not establish capture selection, original per-person statistics, firmware provenance or implementation identity. Missing exact key is not a device capability conclusion. FilmGrain can be skipped at grain zero.",
            "photo_inputs": 0}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("ios_tuning", type=Path); p.add_argument("mac_tuning", type=Path); p.add_argument("output", type=Path)
    a = p.parse_args()
    if a.output.exists():
        p.error("Output already exists")
    a.output.write_text(json.dumps(compare(a.ios_tuning, a.mac_tuning), indent=2) + "\n")
