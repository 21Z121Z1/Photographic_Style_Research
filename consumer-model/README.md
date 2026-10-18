# Photographic Styles consumer reference model (macOS 26A434)

This directory holds the reconstructed **consumer** side of Apple Photographic Styles:
the final semantic-style render kernel. It was published from the research archive
`~/work/styles-gtm-ltm` so it can be used for tone-response comparisons, for example
XDRemux tone ±1 checks. It is a research model. Apple's native renderer remains the oracle.

## Provenance

- OS build **26A434** (macOS 27.0.1 per the runner's `sw_vers`). Path: `PISemanticStyleFilter` → CMImaging
  `CMISmartStyleMetalRendererV1` → the final Metal compute shader recovered as AIR text `0010.ll`
  (sha256 `9ce57aea…d523c1`, recovered in run 39052427081 with
  `research/vm-native/runner/extract_air.py`; the AIR text is not committed here).
- `msl/consumer-model.metal` was produced by `python/scripts/air_to_msl.py`, which translates the
  bounded SSA of kernel `f1` into MSL. It is newly compiled code, not Apple's binary.
  sha256 `0686309165c4b230e45b7ebcba4cd2bd66906840ac20c7fb3b293d6d3ba5c7ed`. This file is
  byte-identical to `research/vm-native/runner/consumer-model.metal` on `research/vm-native-20261018`
  (commit 7626c18).
- The model was frozen at 2026-10-17T22:24:01Z (`msl/model-freeze.json`) before the held-out photos
  IMG_0032 and IMG_0033 entered consumer validation.

## Validated scope (and what is NOT validated)

| Claim | Status | Evidence |
|---|---|---|
| tone=0: the reconstructed MSL matches Apple's original output **half bit-exactly** on 5 full 512×384 frames (IMG_2600/2604/2608 discovery, IMG_0032/0033 held out), 589,824 RGB components each, 0 differing | verified | `evidence/claims.json` C18 (line 330); `evidence/validation-summary.json` `compiled_msl_forward` lines 29, 272, 515, 759, 1003 |
| Non-zero tone (**±0.35 only**): **not** bit-exact. Max abs 0.0059–0.0073, PSNR (peak 1) 63.20 / 63.34 (IMG_2600 −0.35 / +0.35), 63.94 (IMG_0032 +0.35), 64.28 (IMG_0033 +0.35) | verified, acceptance=false | C20 (line 368); `evidence/msl-checkpoints-contrast-sum.json` lines 8, 234; `evidence/msl-checkpoints-heldout.json` lines 121, 347 |
| NumPy reference (`python/forward.py`) is **not** bit-exact (about 79–82 dB) because of atan2/FMA lowering | verified, acceptance=false | C19 (line 347) |
| Full native round-trip (inverse) | **not passing** | C35 (`evidence/claims.json`) |
| tone ±1 | **never measured** | — |

Scope limits: the 5 captured parameter/matte/ROI cases only, at a 512 max edge
(`XD_TONE_MAX_EDGE=512`), on the BG/FG-LTM-less branch of the kernel. The PSNR figures do not stand in for
bit-exactness.

## Layout

- `msl/consumer-model.metal`: kernel `f1`, plus a `sentinel` kernel. Bindings match the native dispatch:
  textures 0,1,2,5–12,21,22 in and 13 (output),14 out; buffers 0,1,3,5,8; debug `float4*` at buffer 30
  (512×17 checkpoints).
- `msl/consumer-model.json`, `msl/model-freeze.json`: the AIR/source hashes, checkpoint SSA ids, and freeze record.
- `harness/native_renderer_trace.m` (+ `native_filter_probe.m`, `encoder_capture.inc`, `msl_replay.inc`):
  this runs the real `PISemanticStyleFilter`, swizzles `CMISmartStyleMetalRendererV1 -process`, captures every
  final dispatch binding, and then (`msl_replay.inc`) recompiles `VM_CONSUMER_MSL` with fastMath, runs it on the
  **same bound textures/buffers**, and writes `msl-output.f16` next to Apple's `_outputImageTexture.bin`.
  These are copies of the files under `research/vm-native/runner/`.
- `harness/run_tone_sweep.py`: a new convenience driver (adapted from `run-discovery.py`, **not yet run on a runner**).
- `python/forward.py`, `inverse.py`, `air_numpy.py`: a NumPy interpreter of the AIR, plus a consumer-conditioned inverse.
  `python/scripts/air_to_msl.py` generates the MSL. `python/scripts/compare_checkpoints.py` compares the model with the native output and
  the NumPy checkpoints. It expects the archive layout `runs/<id>/artifacts/vm-native-text/native/...` and
  `runs/39052427081/.../air/0010.ll`.
- `evidence/`: `claims.json`, `validation-summary.json`, `msl-checkpoints-*.json`, copied verbatim. Evidence paths
  inside them refer to the archive layout.

## Inputs and parameters

The harness needs a macOS host with the private CMImaging/PhotoImaging frameworks (the GitHub `xcode-27`
runner image on build 26A434 was used) and an Apple HEIC carrying Photographic Styles metadata and aux images
(LinearThumbnail, semantic mattes, gain map). Samples are on this branch: `Apple_Native_Samples/IMG_0032.HEIC`,
`IMG_0033.HEIC`, `research/vm-native/samples/IMG_2600.HEIC` (and 2604/2608).

Pipeline per photo: `research/vm-native/extract_inputs.py <photo.HEIC> <resources_dir>` →
`native_renderer_trace <photo.HEIC> <resources_dir> <out_dir>`, with these environment variables:

- `VM_CONSUMER_MSL`: path to `msl/consumer-model.metal` (enables replay)
- `XD_TONE_BIAS`: the filter's `inputToneBias` (validated: 0, ±0.35)
- `XD_TONE_THUMB_MODE=native-stage-mirror`, `XD_TONE_MAX_EDGE=512`, `XD_TONE_GUIDED_REPLAY=0` (the validated settings)

Outputs in `<out_dir>/renderer-0/`: `_outputImageTexture.bin` (Apple, half RGBA little-endian, H×W×4),
`msl-output.f16` (the model, same layout), `msl-checkpoints.f32` (512×17×4), `msl.json`, `trace.json`, `dispatches.json`,
and all bound input textures as `.bin`.

## Run

```bash
# macOS runner, repository root of this branch
python3 consumer-model/harness/run_tone_sweep.py out/tone-sweep \
  Apple_Native_Samples/IMG_0032.HEIC Apple_Native_Samples/IMG_0033.HEIC \
  --tones -1 -0.35 0 0.35 1
# -> out/tone-sweep/tone-sweep.json : differing_components / max_abs / psnr_peak1_db per photo × tone (RGB)
```

Sanity gate: at tone 0 the model should report `differing_components: 0`. If not, the host build or binding differs
from 26A434 and the ±1 numbers are not comparable.

NumPy replay of a captured case (Linux works; needs `0010.ll`):

```bash
python3 consumer-model/python/forward.py --capture <out_dir>/renderer-0 --air <path>/0010.ll --out fwd.npy --chunk 8192
```

Any workflow added for this must use `actions/upload-artifact` with `retention-days: 1`.
