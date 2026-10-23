# Bright selection and negative domains

The explicit experimental cast16 path selects computed bright400 into selected404. Unsupported selected values must leave the writer absent. Missing masks use a separately declared synthetic zero fallback.

## Sub-features

- `bright-selected` observes the actual chosen checkpoint in a portable model.
- `black-unknown` preserves the all-black selected-branch failure.
- `missing-masks` records explicit zero replacements for person, skin and sky.

## How to get to it (user POV)

Add `--selection experimental-bright16` to the real image CLI. Add `--patterns zero` for the black domain. Add `--missing-masks person skin sky` for the declared zero-mask fallback.

## Driving it with verify.py

Preconditions:

- Doctor passes for portable execution.
- Each evidence directory below is new.

- **Select bright.** Run `/usr/bin/python3.13 .cursor/skills/verify-photographic-style/scripts/verify.py drive --feature bright-smoke --evidence /tmp/psr-verify-bright-new`. The writer exists, the branch record chooses bright400, and selected404 storage equals bright400 storage.
- **Retain unknown.** Run the helper with `--feature zero-input --evidence /tmp/psr-verify-zero-new`. The actual image CLI exits2. The helper verifies that the persisted unknown cases have no writer. The helper itself exits zero after checking this expected negative behavior.
- **Request fallback.** Run the helper with `--feature missing-masks --evidence /tmp/psr-verify-masks-new`. Each request lists person, skin and sky omissions, and its recomputed effective input hash matches the actual result.
- **Cleanup.** Run cleanup separately for each directory and retain its report and manifest.

## Gotchas

- Saved cast0 writer equality historically proved a skin branch. It must not be used as evidence for selected bright.
- Selecting bright with supplied coefficients does not prove actual cast16 renderer coefficient production.
- A synthetic mask fallback proves processing logic. It does not establish real segmentation quality or every native nil-texture path.
- Unselected internal errors remain reported even when a writer exists.
