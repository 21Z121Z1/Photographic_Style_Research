# Reconstruct a paired Smart Style Live Photo

Use an Apple Silicon Mac with Xcode command-line tools, Python 3, numpy, scipy, ffprobe, and exiftool. The input pair must contain the tested Smart Style 0.16 resource set and a native HDR still reference.

Run the entry point with two new output paths:

```bash
python3 /Users/retriedstormtrooper/Documents/Projects/Active/proxdrtest/artifacts/research/20261106-native-hdr-independent/src/run.py \
  /Users/retriedstormtrooper/Downloads/IMG_3673.HEIC \
  /Users/retriedstormtrooper/Downloads/IMG_3673.mov \
  /tmp/IMG_3673-independent-rebuild \
  /Users/retriedstormtrooper/Downloads/IMG_3673-independent-rebuild.pvt
```

The command builds the native helper, decodes the paired resources, fits the HDR look, renders the video, packages the Live Photo, and validates the packaged result. It stops if an output path already exists.

The last line starts with `Passed native, HDR look, HLG decode, timing and container checks`. Inspect `validation.json` in the new work directory. Every value under `checks` must be true.

Open the PVT with Quick Look to check native bundle recognition. Importing it into Photos and testing editing are separate operations.

The verified run for this sample is `verified-run/`. Its `manifest.json` records input hashes, implementation hashes, output hashes, and the exact commands. `stages.json` and each stage log preserve the execution results.

`src/native.m` owns the Apple framework calls. `src/fit.py` owns the fitted response and motion confidence policy. `src/package.py` writes the replacement track and PVT. `src/validate.py` checks the final decoded artifact. `src/run.py` runs those stages.

The implementation and measured limitations are explained in `IMPLEMENTATION.zh-CN.md`.
