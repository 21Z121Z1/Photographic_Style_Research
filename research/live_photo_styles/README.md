# Live Photo video: Photographic Styles metadata

Pure-Python tools for the style data inside the MOV half of an Apple Live Photo.

| file | what it does |
|---|---|
| `livephoto_mov.py` | mmap QuickTime parser: tracks, `tagc` aux types, `tref`, edit lists, codec/colour boxes, every mebx sample (bplist / typed values), global `mdta` keys, still-image time. `python3 livephoto_mov.py X.MOV --samples first --out x.json` |
| `compare_aux.py` | decodes aux HEVC tracks with `ffmpeg` and compares them with the paired HEIC linear thumbnail / mattes at the still time |
| `survey.py` | runs everything over a folder and writes the small JSONs in `evidence/` |
| `ablate.py` | makes MOV variants without selected tracks / with patched global keys, for on-device tests |
| `key1_probe.py` | hypothesis tool for the 576-value key `1` reported on iOS 27 |
| `SPEC.md` | format notes with PROVEN / REPORTED / HYPOTHESIS labels |
| `XDREMUX_CHECKLIST.md` | what a writer should emit, by evidence level, plus the next device experiment |

Tests: `python3 -m pytest research/live_photo_styles/tests` — synthetic MOV fixtures always run; real-media tests use
`$LIVEPHOTO_SAMPLES` (default `/workspace/samples16`, expects `mov/*_ST_*.MOV`) and skip when absent.

Reproduce evidence: `python3 survey.py --mov-dir <mov> --heic-dir <heic> --out evidence/ios18_marketing` (needs `numpy`, `ffmpeg`, and `tools/heif_dump.py` from this repo).
No media, frames or GPS are committed.
