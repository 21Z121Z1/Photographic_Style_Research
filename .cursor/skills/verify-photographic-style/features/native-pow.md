# Native pow preflight

The native collector checks whether one new call of the exact sealed CPU-recompiled pow shim is possible. The Linux journey records why the target is unavailable.

## Sub-features

- `native-material-gate` checks the actual host and required artifact identity.
- `native-blocked` preserves absence of the private sealed artifact and expected Apple OS build.
- `native-call` remains a separate host-dependent journey, not executed here.

## How to get to it (user POV)

Run `research/styles-firmware-20261022/pow_runtime_binding.py preflight --output NEW.json`. A real native run requires `run --binary ORIGINAL --expected-os-build BUILD --private NEW_PRIVATE_DIR --output NEW.json` as documented in `NATIVE_POW_BINDING.zh-CN.md`.

## Driving it with verify.py

Preconditions:

- `/tmp/psr-verify-native-new` does not exist.
- No sealed binary is supplied by this Linux smoke journey.

- **Observe the actual gate.** Run `/usr/bin/python3.13 .cursor/skills/verify-photographic-style/scripts/verify.py drive --feature native-preflight --evidence /tmp/psr-verify-native-new`. The helper exits2 and `verification.json` reports `BLOCKED_native_material`.
- **Inspect blockers.** Read `native-preflight.json` and require actual OS and architecture, the required sealed SHA, explicit blockers, and zero native calls and compilations.
- **Cleanup.** Run cleanup against `/tmp/psr-verify-native-new`. Preserve the blocked report. A blocked preflight is a successfully observed gate, not a passed native-call acceptance test.

## Gotchas

- Linux libm, Python pow and another Apple OS cannot replace the exact target.
- Prior S33 evidence observes one sqrt input. It does not certify pow or historical FPCR.
- Standard macOS runners do not contain the absent private sealed artifact by default.
- Do not upload sealed binaries or private source material. Do not retry an uncertain native call automatically.
