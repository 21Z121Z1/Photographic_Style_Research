# Patch recovery

`recovered/recovery-manifest.json` replays `source-patches.jsonl` (SHA-256 `33b50f8ccdc08513282c48f40f9f5f1613967f6ae0789a5d879f237e272ce64f`). The replay added 25 files, updated 30, and seeded 2 unpatched copies.

Those two copies are the S12 raw L44 `cp` that the patch log does not contain:

- `LivePhotoHDR/src/validate.py` from the patched independent `validate.py`
- `LivePhotoHDR/src/extract.py` from the patched still/video `extract.py`

`LivePhotoHDR/src/{native.m,fit.py,package.py}` were seeded the same way and then received their recorded updates. No independent update failed. This is not a byte witness of the offline Mac disk.

Scene-guided grading files were left unmaterialized on purpose (3 patch operations). That work belongs to `research/livephoto-scene-grading-pilot-20261106`.

The recovered standalone `DecodeLog` evaluates the Apple Log decimals as float32. The portable curve uses the same decimal literals as float64, matching the handoff and `analyze.py`. Constants were not refit.
