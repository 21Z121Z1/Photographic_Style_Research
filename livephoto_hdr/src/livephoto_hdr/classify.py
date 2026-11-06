"""Bypass, Delta, and fallback classification.

The recovered standalone helper treats a missing bypass flag as false.
This portable contract does not. An explicit smartstyle.bypassed value is
required before a sample is called bypassed or not bypassed.
"""
from __future__ import annotations


MODES = (
    "bypassed",
    "native-delta-coefficients",
    "styled-scene-fallback",
    "bypass-flag-absent",
    "incomplete-resources",
)


def classify(*, bypassed: bool | None, delta_present: bool, style_metadata_present: bool, scene_thumbnail_present: bool) -> dict:
    if bypassed is None:
        mode = "bypass-flag-absent"
    elif bypassed is True:
        mode = "bypassed"
    elif delta_present and style_metadata_present:
        mode = "native-delta-coefficients"
    elif style_metadata_present and scene_thumbnail_present and not delta_present:
        mode = "styled-scene-fallback"
    else:
        mode = "incomplete-resources"
    return {
        "mode": mode,
        "bypassed": bypassed,
        "deltaPresent": bool(delta_present),
        "styleMetadataPresent": bool(style_metadata_present),
        "sceneThumbnailPresent": bool(scene_thumbnail_present),
        "nativeInverseExecuted": False,
        "recoveredStandaloneAbsentFlag": (
            "LivePhotoHDR StyleBypassed returns false when the key is absent, "
            "which can select native-delta-coefficients or styled-scene-fallback. "
            "This portable classifier returns bypass-flag-absent instead."
        ),
    }
