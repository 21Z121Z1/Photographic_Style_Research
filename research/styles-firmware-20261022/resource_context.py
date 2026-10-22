"""Extract a small, explicit configuration context from verified local resources.

Key names and numeric values do not establish the runtime selection or units.
The caller supplies the independently verified component provenance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import plistlib


def summarize(root: Path) -> dict:
    sources = {}
    def load(name):
        raw = (root/name).read_bytes()
        sources[name] = {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
        return plistlib.loads(raw)
    smart = load('SmartStyleTuning.plist')['V1']['Default']
    engine = load('StyleEngineTuning.plist')['StyleEngineV1']['12']
    texture = load('TextureStyleTuning.plist')
    studio = texture['iPhone19,2']['PortTypeBack']['Still']['Studio']['Common']
    return {"sources": sources, "hardware_container": "iPhone17,3", "image_build": "24A446",
            "selected": {
                "SmartStyleTuning/V1/Default": smart,
                "StyleEngineTuning/StyleEngineV1/12": engine,
                "TextureStyleTuning/iPhone19,2/PortTypeBack/Still/Studio/Common": {
                    "canonical_dictionary_sha256": hashlib.sha256(json.dumps(studio,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
                    "EffectOrder": studio['EffectOrder'],
                    "UnderEyeBrightening.brightnessMix": studio['UnderEyeBrightening']['brightnessMix'],
                    "Mattify.editingStrength": studio['Mattify']['editingStrength']}},
            "texture_whole_file_matches_host_reference_sha256": sources['TextureStyleTuning.plist']['sha256'] == '9a0963e5a58aaa8c8c7fb42ccb75a254a9e1012ba594135b991ed8e1f191d31e',
            "exact_iphone17_3_texture_key_present": 'iPhone17,3' in texture,
            "runtime_useCase12_to_plist_key12_mapping_verified": False,
            "selected_tuning_to_runtime_units_verified": False,
            "original_per_person_stats_recovered": False,
            "scope": "Selected scalar configuration only. SRL MaxBoost names are not measured pixel gains or EV. Key 12 is a candidate for the observed useCase12 getter; the external CommonSettings implementation is still absent. A device key in a cross-device plist is not capture selection."}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('root',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    a.output.write_text(json.dumps(summarize(a.root),indent=2)+'\n')
