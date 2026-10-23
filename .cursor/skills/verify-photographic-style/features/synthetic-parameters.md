# Synthetic parameter outputs

The synthetic CLI computes a complete conditional source-to-writer model and reports how an internal raw parameter changes the persisted output.

## Sub-features

- `synthetic-source` generates a declared synthetic scene and procedural semantic masks.
- `parameter-effect` runs raw field3 values 0 and .125 against the same supplied context.
- `persistent-output` saves contexts, override requests, stage arrays, writer pixels and diagnostic images.

## How to get to it (user POV)

Run `research/styles-firmware-20261022/image_chain_cli.py` with explicit `--numerics experimental-portable` and a new `--output` directory. The CLI also accepts gradient, exposure, colors, edges and zero patterns.

## Driving it with verify.py

Preconditions:

- Doctor reports Python 3.13, NumPy 2.2.4, Pillow 11.1.0 and `portable_ready=true`.
- `/tmp/psr-verify-portable-new` does not exist.

- **Compute.** Run `/usr/bin/python3.13 .cursor/skills/verify-photographic-style/scripts/verify.py drive --feature portable-smoke --evidence /tmp/psr-verify-portable-new`. The command exits zero and `verification.json` reports two cases and two writers.
- **Read back.** Run `/usr/bin/python3.13 .cursor/skills/verify-photographic-style/scripts/verify.py inspect --evidence /tmp/psr-verify-portable-new/cli-output`. The helper verifies context, request and effective input hashes, stage arrays, output storage and model-only claims.
- **Probe false evidence.** Run the `reject-probes` command against that same `cli-output`. Both the forged Apple label and the stale source manifest must be rejected.
- **Cleanup.** Run the helper's cleanup command against `/tmp/psr-verify-portable-new`. `cleanup.json` reports retained evidence, and the manifest hashes still resolve.

## Gotchas

- Field3 is an internal ABI control. These values are not verified Apple UI endpoints.
- A portable writer does not prove Apple CPU, GPU, segmentation or full capture correctness.
- Changing source while the CLI runs produces an unbound report. Preserve it and run a new journey after source is stable.
- The helper refuses old evidence after checkout changes. Do not relabel an old report as a new HEAD.
