# Blind Styles reconstruction and final Texture replay

English | [简体中文](README.zh-CN.md)

Experiments, candidate code and numeric evidence live in this research repository.
XDRemux PR85 receives verified product fixes. The histogram candidate remains here
because its negative-Tone error is worse on all three measured controls.

The scripts isolate a reference photo's coded SDR/HDR base, regenerate Styles
resources with XDRemux's Rust producer, and compare native edit responses. The
original Styles resources become available only to the evaluator. Candidate
comparison uses no reference-resource substitution. Diagnostic mode deliberately
substitutes resource groups and labels those substitutions separately.

## Retained native result

[Raw numeric report](evidence/20261029-histogram/native-report.json) and
[source binding](evidence/20261029-histogram/provenance.json) identify the measured
producer, renderer and artifact. These are the original measurements, retained
unchanged when the harness moved repositories.

| Control | Split | Default mean RMSE | Histogram mean RMSE | Reduction |
| --- | --- | ---: | ---: | ---: |
| IMG_2600 | Calibration | 0.0330819025 | 0.0308088261 | 6.87% |
| IMG_2604 | Calibration | 0.0287555617 | 0.0252179764 | 12.30% |
| IMG_2608 | Holdout | 0.0352662714 | 0.0326951252 | 7.29% |

The metric averages Tone -0.5 and +0.5. Combined calibration RMSE falls 9.40%.
Negative-Tone RMSE rises 0.39%, 6.09% and 2.65%, respectively. Neutral Tone and
Color -0.5/+0.5 have zero error against the reference. Native full-resolution
SDR/HDR base comparisons also have zero error for all three isolated inputs and
six regenerated files. These public controls had prior research exposure; the
holdout is a fixed scene split, not a newly collected unseen dataset.

The histogram writer uses local quantized medians and the ordered half writer
in `research/hdr-native/lightmap_model_s55.py`. Its d guide uses GTC-mapped RGB.
The 269 native synthetic comparisons in `evidence/s56/tail-summary.json` validate
the historical conditional writer, not the complete camera color/statistics/ROI
pipeline. Image-derived normalizers, arithmetic RGB guides and integer cell
footprints remain approximations.

The forward consumer is `PISemanticStyleFilter useStyleEngine=NO` on macOS build
26A434. This result does not establish full-engine, native reversal, key-1/Delta,
or Photos save/reopen equivalence. Earlier native reversal failed with
`desc != nil`. The public Texture control contains shop mannequins; it does not
validate skin effects on the supplied human portraits.

## Reproduce

Use a disposable XDRemux checkout at `cf1e790e33e04202745bc34e52f1e414c02e290d`. Apply
[`xdremux-research.patch`](xdremux-research.patch) only in that checkout. It adds
the opt-in calibration entry point and histogram candidate to the same Rust
producer; it contains no second producer. PR85 does not carry these experiments.

```bash
git -C /absolute/path/XDRemux apply --check /absolute/path/Photographic_Style_Research/research/styles_fidelity/xdremux-research.patch
git -C /absolute/path/XDRemux apply /absolute/path/Photographic_Style_Research/research/styles_fidelity/xdremux-research.patch
cargo build --manifest-path /absolute/path/XDRemux/Cargo.toml --locked -p xdremux-runtime --features styles-research --example styles_fidelity
swift build --package-path /absolute/path/XDRemux --product xdremux-apple-adapter
```

Run Python from this research repository. `PYTHONPATH` points to that external
XDRemux checkout because the harness reuses its HEIF inspector and consumer
compatibility helper. The renderer sources and reference media come from a
separate checkout of this repository at `37dd551a949047ed14580efa0c0a2556922791b5`.

```bash
PYTHONPATH=/absolute/path/XDRemux python3 -m unittest discover -s research/styles_fidelity/tests -t . -v
PYTHONPATH=/absolute/path/XDRemux python3 -m research.styles_fidelity.tone_attribution \
  --compare-histogram-light-maps \
  --adapter /absolute/path/xdremux-apple-adapter \
  --generator /absolute/path/XDRemux/target/debug/examples/styles_fidelity \
  --research-root /absolute/path/pinned-consumer \
  --input /absolute/path/pinned-consumer/research/vm-native/samples/IMG_2600.HEIC \
  --input /absolute/path/pinned-consumer/research/vm-native/samples/IMG_2604.HEIC \
  --holdout /absolute/path/pinned-consumer/research/vm-native/samples/IMG_2608.HEIC \
  --output /absolute/path/new-measurement-directory
```

NumPy and Pillow are required. Native execution additionally needs macOS, the
Apple adapter and the native HEVC provider. The existing
[`styles-native-reference.yml`](../../.github/workflows/styles-native-reference.yml)
workflow owns the migrated checks. Its source-binding JSON distinguishes the
unpatched product commit from the applied candidate patch.

`corpus`, `isolate` and `split` provide archive inventory, source-only projection
and fixed scene splits. `blind` retains the joint exposure/gain experiment.
`texture` replays stored and recomputed statistics from final encoded resources;
its `--research-root` must be a separate checkout at
`2bc4e3d16fc2c6028cdf708f06d79cf3be42a6d5`. Each module exposes `--help`.
Keep supplied portrait media outside public Git and Actions artifacts. Upload
only numeric reports, hashes and logs unless the user requests previews of the
fixed, already-public controls. Supplied private portraits remain excluded.

## Separate c/d and joint calibration experiment

Add `--isolate-light-maps` to `--compare-histogram-light-maps`. The existing
workflow runs seven evaluator variants on the same two calibration scenes and
one held-out scene: default, candidate c only, candidate d only, candidate c+d,
a joint source-generated candidate, the original brightness bundle, and original
renderer-input closure. The joint candidate fixes baseline/gain scales to 0.75
using the earlier exposure/gain experiment; it retains the default baseline cap.
It is frozen before this run and is not a new search or an unseen-data claim.
All three complete generations finish before original resources are extracted.

The c-only/d-only variants copy just the selected map from the source-generated
candidate, leaving the other map, curve, thumbnail, exposure and coefficients
at default. Per-variant hashes and scalar metadata expose the actual inputs.
Both Tone signs retain decoded-input observations. The last two variants use
original resources only for diagnosis, with `oracle_resources_used` recorded for
each variant. Closure must reproduce all three reference Tone points exactly.
Experiment completion does not mean candidate fidelity acceptance.

The same workflow also replays all existing Texture effects from a final HDR
product file and compares stored/recomputed statistics in SDR and HDR. Its
public control depicts mannequins; human-skin validation remains separate.
Only numeric reports are uploaded. No product defaults or PR85 code change.

## Promotion

Before moving the candidate into PR85, resolve the negative-Tone regressions and
repeat the joint Tone/Color controls on additional scene groups. Then verify
native reversal and final HDR Texture on real human samples independently.
The preserved HDR container fixes in PR85 have separate product regressions.

## Joint candidate spatial acceptance measurement

The current native workflow runs only default versus the frozen joint candidate,
with 1024-edge native renders on the same three scenes and the two nonzero Tone points.
`joint_spatial` reports per-pixel candidate changes separately from regressions
against the original reference. Error is max absolute RGB-channel distance;
regression is candidate error minus default error. Thresholds 0.005/0.01/0.02
include pixel fraction, 8-connected component count, largest area and its box.
This measures area and magnitude, rather than rejecting a candidate on one maximum.

Both linear P3 and a fixed diagnostic display projection are reported. The
projection divides every variant by the same source headroom, clips to [0,1],
and applies the Display P3 transfer. Clipped fractions are retained. A 0.01
threshold means one percent of code range in that projection, not one percent
relative luminance or a perceptual just-noticeable difference. This is not an
actual Photos HDR display or full-resolution pixel evaluation. Only numeric
summaries are exported. The previous c/d and Texture experiment is retained in
`evidence/run-40855897150`; it is not repeated by this focused workflow.

The 2048 experiment produced indistinguishable outputs without retained signal
observations, so its zero distances are not acceptance evidence. The focused
1024 measurement requires spatially varying RGB and a nonzero reference edit
response, retaining image hashes/ranges. White-anchored SDR projection is reported
separately from the headroom-scaled view. This round does not repeat the previous
neutral/Color/Texture controls; it targets the nonzero-Tone regression footprint.

`--export-previews` retains the same measured reference/default/joint images as
white-anchored SDR PNGs with the host's Display P3 ICC profile embedded. All
variants use the same projection, without auto exposure or difference boosting.
The fixed public controls in the workflow export these previews on user request;
this does not change generation parameters, render dimensions or score inputs.

## Complete editable HEIC export

The user's Photos comparison uses `python3 -m research.styles_fidelity.editable`,
which exports the three original public HEICs and six complete generated HEICs
in `01_original`, `02_fixed_default`, and `03_fixed_joint` folders. It uses the
same producer and frozen joint calibration, without baking a Tone edit into the
photo. Native full-resolution SDR/HDR base readbacks must match the source
exactly; Styles resources and file hashes are retained in the report. The
current workflow publishes `xdremux-key1-lightness-editable-heic-*` for this request. Actual
Photos UI editing remains for the user's device test; the previously observed
abnormal probe previews are not fidelity evidence.

The common key-1 fitter previously clipped each term after an unconstrained
solve. This breaks the fitted RGB correspondence when correlated terms hit
different bounds, producing spatial color patches even in the default variant.
`key1-regression.patch` exercises a representable uniform-color correspondence;
the native job requires that the original fitter fails this check, then applies
`key1-bounded.patch` and reruns all engine tests before exporting files. The
repair keeps the same polynomial, regularization and bounds, solving the box
constraints jointly. This is separate from exposure/gain or c/d calibration.

The producer previously fitted key 1 to the raw linear thumbnail code. That code
is scene light divided by baseline exposure and multiplied by base gain, so the
exposure and tone scale already carried by the linear metadata, global tone
curve and semantic tone resources were absorbed a second time: removing the
style darkened every block and pinned most coefficients at their bounds.
`key1-lightness-regression.patch` checks that a revert keeps the primary
luminance and transfers the thumbnail chromaticity on a uniform scene whose
thumbnail is darker than the primary; the native job requires that the previous
target fails it, then applies `key1-lightness.patch`, which keeps the
thumbnail chroma at the primary luminance, and reruns the runtime Styles tests.
