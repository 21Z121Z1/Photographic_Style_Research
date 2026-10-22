"""Keep product, firmware, plugin and HEIC versions independent at admission.

This gate records evidence, never discovers missing provenance or infers a
product generation from a class suffix. Passing static admission is not a
runtime, image-accuracy or unique-inverse claim.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Firmware:
    hardware: str
    build: str


@dataclass(frozen=True)
class Plugin:
    firmware: Firmware
    bundle_path: str
    class_name: str
    bundle_version: str
    sha256: str
    official_image_membership_verified: bool


@dataclass(frozen=True)
class Loader:
    firmware: Firmware
    selected_bundle_path: str
    selected_class_name: str
    selection_dataflow_verified: bool
    class_in_plugin_verified: bool


@dataclass(frozen=True)
class Sample:
    hardware: str
    capture_build: str | None
    product_generation: int | None
    styles_metadata_version: int
    texture_people_metadata_version: int | None


def admit_static_sample_chain(sample: Sample, plugin: Plugin, loader: Loader,
                              *, target_product_generation: int) -> dict:
    reasons = []
    if sample.product_generation is None:
        reasons.append("sample product generation not independently established")
    elif sample.product_generation != target_product_generation:
        reasons.append("sample product generation differs from requested product generation")
    if sample.capture_build is None:
        reasons.append("exact sample capture build unavailable")
    if (sample.hardware, sample.capture_build) != (plugin.firmware.hardware, plugin.firmware.build):
        reasons.append("plugin firmware does not match sample hardware/build")
    if plugin.firmware != loader.firmware:
        reasons.append("loader and plugin firmware identities differ")
    if not plugin.official_image_membership_verified:
        reasons.append("plugin membership in official image not verified")
    if not loader.selection_dataflow_verified:
        reasons.append("actual loader selection dataflow not verified")
    if (loader.selected_bundle_path, loader.selected_class_name) != (plugin.bundle_path, plugin.class_name):
        reasons.append("selected bundle/class does not match plugin")
    if not loader.class_in_plugin_verified:
        reasons.append("selected class not independently found in plugin")
    if len(plugin.sha256) != 64 or any(c not in "0123456789abcdef" for c in plugin.sha256):
        reasons.append("complete plugin SHA256 unavailable")
    return {"static_version_chain_admitted": not reasons, "reasons": reasons,
            "runtime_loaded_verified": False, "camera_inverse_verified": False,
            "version_numbers_not_equated": {"product": sample.product_generation, "bundle": plugin.bundle_version,
                                            "heic_styles": sample.styles_metadata_version,
                                            "heic_texture_people": sample.texture_people_metadata_version}}
