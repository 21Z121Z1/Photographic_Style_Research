---
name: verify-photographic-style
description: Drive Photographic Style Research's real synthetic image CLI, inspect persisted checkpoints and evidence claims, and identify blocked Apple, HEIF, or macOS app journeys. Use before claiming a research or CLI change works.
---

# Verify Photographic Style Research

This skill verifies the explicit portable research CLI on Linux. Apple CPU, Apple GPU, HEIF structural conformance, and Photos or app behavior are separate journeys. A successful portable run does not certify those journeys. The feature map records their own preconditions.

The project-local skill was generated from `cursor/plugins` source commit `00d5decc6f05669044fd092dec73da9ef6f7eec0`. Its presence does not register a ChatGPT slash command or claim a global Cursor plugin installation.

## Launch

Run commands from the repository root. Use Python 3.13 with NumPy 2.2.4 and Pillow 11.1.0. The verified environment supplies `/usr/bin/python3.13`. On another environment, create a disposable virtual environment and install those exact versions before invoking this helper. Do not change the user's Python or global packages.

```sh
/usr/bin/python3.13 .cursor/skills/verify-photographic-style/scripts/verify.py doctor
```

Ready means `portable_ready` is true and every dependency requirement is true. The CLI is short-lived. The helper starts each drive in its own PTY, waits for the exact child PID, captures the exit code, and reaps that child. No server, database, port, login, seed photograph, or background process is needed.

Allocate a fresh evidence directory for each drive. The helper refuses an existing directory. Concurrent drives must use different directories. Never reuse a directory from another run.

## Doctor

The `doctor` command is read-only. It reports the actual OS, architecture, executable runtime versions, checkout SHA, and source identity of the helper. It reports the native journey as blocked until an exact sealed artifact and expected Apple OS build are supplied. Darwin alone does not establish a matching Apple target.

If a run looks wrong, rerun doctor before editing code. A failed dependency check is an environment failure. It must not be silently reclassified as a passing algorithm test.

## Drive

Read [the feature index](features/README.md), then select a matching journey. This default journey drives the actual user CLI with two independently supplied internal color values.

```sh
/usr/bin/python3.13 .cursor/skills/verify-photographic-style/scripts/verify.py drive \
  --feature portable-smoke --evidence /tmp/psr-verify-portable-new
/usr/bin/python3.13 .cursor/skills/verify-photographic-style/scripts/verify.py inspect \
  --evidence /tmp/psr-verify-portable-new/cli-output
/usr/bin/python3.13 .cursor/skills/verify-photographic-style/scripts/verify.py reject-probes \
  --evidence /tmp/psr-verify-portable-new/cli-output
```

The drive invokes `research/styles-firmware-20261022/image_chain_cli.py` through a PTY. It does not call internal setters or replace any pipeline helper. `portable-smoke` uses a program-generated 2×2 gradient and internal field3 values 0 and .125. This is a quick journey, not a resolution or photograph acceptance test. Use the CLI's documented 8×12 default batch for the broader synthetic matrix, retaining its unknown cases and exit2.

`bright-smoke` explicitly selects experimental raw cast16. `zero-input` proves that the unsupported black domain stays unknown. `missing-masks` requests the explicit synthetic zero-mask fallback. `native-preflight` invokes the real pow preflight without a binary and preserves its blocked result. It does not compile, load or invoke an Apple target.

## Evidence

The evidence directory contains `doctor.json`, `command.json`, `terminal.log`, `verification.json`, `negative-probes.json`, `manifest.json`, and the CLI's raw contexts, run requests, checkpoint NPZ files, diagnostic PNG files and per-case results.

The helper checks the following observable contracts.

- The report's exact checkout SHA matches the current checkout. The before and after source manifests agree with the current source bytes.
- The raw context and override request are persisted separately. The context declares that it precedes overrides. The helper recomputes each effective raw-input hash from those arrays and the declared cast and missing-mask changes.
- Portable output remains `model_only`, with Apple validation false, native and GPU calls zero, and no injected native intermediate values or inherited S25, S29 or S30 certification.
- A claimed writer has finite half storage, the reported written pixel count, alpha one on those pixels, and actual producer, guided and final checkpoints. Unknown cases have no persisted writer.
- The selected404 checkpoint equals the selected skin or bright checkpoint. The helper does not infer that the unselected branch reached the writer.
- A forged Apple validation label and a stale source manifest are rejected using in-memory copies of the new report. Historical evidence is never edited by these probes.

Diagnostic PNG files clamp raw code values for display. They are not a calibrated color rendering. A max error or RMSE in the report measures an internal parameter change against the same run's reference. It is not Apple accuracy.

`inspect` checks the current checkout against the saved report. If the checkout changed, retain the old evidence under its original SHA and run a fresh journey for the new checkout. Do not update the old report's SHA to make inspection pass.

This helper verifies files and subprocess behavior. It does not audit network packets. The synthetic CLI requires no service or credential. Do not call the helper a network-isolation proof.

## Cleanup

```sh
/usr/bin/python3.13 .cursor/skills/verify-photographic-style/scripts/verify.py cleanup \
  --evidence /tmp/psr-verify-portable-new
```

Cleanup removes only the helper's owned `.scratch` directory. The exact child process was already synchronously reaped by `drive`. Cleanup checks all manifest hashes again, writes `cleanup.json`, and leaves the evidence in place. Never kill processes by name and never remove the evidence directory as cleanup.

Run cleanup after a failed drive as well. If no manifest exists because the drive failed early, preserve the partial command and terminal evidence and report the failure. Do not call that partial journey verified.

## Helpers

`/usr/bin/python3.13 .cursor/skills/verify-photographic-style/scripts/verify.py --help` lists the executable helper's commands. The helper is executable, but an explicit Python 3.13 interpreter keeps runtime selection visible.

Follow `/maintain-verification-skill` when CLI options, evidence fields or entry points change. The feature map is a review artifact until the architecture plan is approved. No formal migration or auto-merge is implied.
