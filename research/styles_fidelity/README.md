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
only numeric reports, hashes and logs.

## Promotion

Before moving the candidate into PR85, resolve the negative-Tone regressions and
repeat the joint Tone/Color controls on additional scene groups. Then verify
native reversal and final HDR Texture on real human samples independently.
The preserved HDR container fixes in PR85 have separate product regressions.
