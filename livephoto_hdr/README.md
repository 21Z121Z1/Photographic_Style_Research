# Live Photo HDR portable baseline

Linux-side recovery of the 2026-11-06 independent HDR baseline and the IMG_8148 temporal regression. This directory is separate from the scene-guided grading pilot on `research/livephoto-scene-grading-pilot-20261106`.

Native Core Image, Metal, Vision, and CMImaging are not executed here. `python3 -m livephoto_hdr.cli native-status` reports that block. It is not a success.

```bash
PYTHONPATH=livephoto_hdr/src python3 -m unittest discover -s livephoto_hdr/tests
PYTHONPATH=livephoto_hdr/src python3 -m livephoto_hdr.cli temporal \
  --mov /path/IMG_8148.MOV --heic /path/IMG_8148.HEIC --output /path/new-directory
```

The output directory is created only when it does not already exist. Inputs are not replaced.

Recovered Mac sources are under `recovered/` with `recovery-manifest.json`. The portable entry point is `src/livephoto_hdr/`. Numeric results from this host are in `results/`.
