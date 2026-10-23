# HEIF structural reports

The existing inspection tools write the HEIF item graph and semantic consistency reports for a supplied candidate file. Structure inspection does not certify Photos UI activation or reconstruction accuracy.

## Sub-features

- `heif-graph` records boxes, item links and auxiliary identities.
- `semantic-report` writes JSON and Markdown consistency reports.
- `preserve-input` leaves the supplied original input unchanged.

## How to get to it (user POV)

Run `tools/heif_dump.py INPUT --json OUTPUT.json --md OUTPUT.md`. Run `tools/semantic_fitter.py INPUT --json SEMANTIC.json --md SEMANTIC.md` for the semantic report. The macOS app also exposes these through its Validation workflow.

## Driving it with verify.py

Preconditions:

- An explicitly authorized synthetic HEIF candidate exists. This Linux skill run has not been supplied one.
- Output paths are new and distinct from the input.
- Python dependencies from the repository README are installed for the selected tool.

- **Inspect structure.** Invoke `/usr/bin/python3.13 tools/heif_dump.py "$PSR_SYNTHETIC_HEIF" --json "$PSR_EVIDENCE/heif.json" --md "$PSR_EVIDENCE/heif.md"` from the repository root, with the two variables pointing to the authorized file and a fresh owned evidence directory.
- **Inspect semantic consistency.** Invoke `/usr/bin/python3.13 tools/semantic_fitter.py "$PSR_SYNTHETIC_HEIF" --json "$PSR_EVIDENCE/semantic.json" --md "$PSR_EVIDENCE/semantic.md"`.
- **Read back.** Open both saved JSON reports, preserve command output and exit status, compare the input SHA before and after, and retain warnings as failures or explicit unresolved fields. The portable image helper does not drive this feature.

## Gotchas

- This journey is unexecuted in the generated skill's smoke receipt because no authorized synthetic HEIF file was supplied.
- Do not use a private photograph merely to make this journey executable.
- A compatible item graph is not full Apple image-processing reproduction or Photos product acceptance.
