# Live Photo MOV: Photographic Styles (`smartstyle-info`) — working spec

Status labels used below:

* **PROVEN**: reproduced by `livephoto_mov.py` / `survey.py` / `compare_aux.py` on the files listed, with the evidence JSON named.
* **OBSERVED-n**: true in every file we have (n files), but the sample is small or from one source.
* **REPORTED**: taken from the IMG_3940 (iPhone 18 Pro, iOS 27.2) notes; that file is **not** in this repo's sample set and has not been re-parsed here.
* **HYPOTHESIS**: an interpretation not yet tested.

Sample set used for PROVEN/OBSERVED claims: Apple's three iPhone 16 marketing Live Photo pairs
(`240718_Demo-Uno-Calpe_ST_i071293`, `…_i080897`, `240725_Demo-Uno-Yaiza_ST_i072079`, HEIC+MOV).
Evidence: `evidence/ios18_marketing/*.json` (no pixels; location keys redacted).
Caveat: these MOVs carry global `model = "iPhone 7"`, `software = 18.0` while the paired HEIC EXIF says iPhone 16,
so they may have been re-muxed by Apple tooling. Seven other non-style MOVs in the sample folder (A01A…/B02B…/C03C…, 4K HLG/Dolby Vision)
contain **no** smartstyle tracks, keys or auxv tracks (`evidence/ios18_marketing/A01A*/B02B*/C03C*.tracks.json`).

## 1. Track layout (iOS 18 marketing files) — PROVEN (3/3, `*.tracks.json`, `survey.json`)

| id | handler / format | identity | size, depth | samples |
|---|---|---|---|---|
| 1 | `vide` / `hvc1` | main video | 1920×1440, Main 8-bit, full range, `colr nclc 12/1/6` | 84 / 88 / 80 |
| 2 | `auxv` / `hvc1` | `udta/tagc` = `com.apple.quicktime.video-map.sky` | 256×192 8-bit 4:2:0 | 42 / 35 / 32 |
| 3 | `auxv` / `hvc1` | `…video-map.smart-style-linear-thumbnail` | 128×96 (coded 160×96, cropped), **Main10**, `colr nclc 12/2/6`, `logs` box = `com.apple.rec2020.apple-log` | = main |
| 4 | `auxv` / `hvc1` | `…video-map.person` | 256×192 8-bit | = sky |
| 5 | `auxv` / `hvc1` | `…video-map.skin` | 256×192 8-bit | = sky |
| 6–11 | `meta` / `mebx` | one key each: `video-orientation`, `live-photo-info`, `smartstyle-info`, `still-image-time`, `live-photo-still-image-transform`, `…-reference-dimensions` | – | 1 / per-frame / per-frame / 1 / 1 / 1 |

(Yaiza orders the meta tracks differently: `smartstyle-info` is track 7.)

* The aux video type is carried **only** by `udta/tagc` on these files. **No `tref` on auxv tracks** (PROVEN 3/3).
  IMG_3940 is REPORTED to use `tref/vmap` → track 1 on its auxv tracks; a writer should emit both (see checklist).
* Every `meta` track has `tref/cdsc` → 1 (PROVEN 3/3).
* The linear-thumbnail track has the same sample count, timestamps and sync-sample pattern as the main video (PROVEN 3/3).
  IMG_3940 REPORTS it at 15 fps — so the rate is not fixed.
* Matte tracks run at a lower, variable rate: mean 14.8 / 11.6 / 11.3 Hz, gaps 1–5 main frames (PROVEN, `timing.pts_delta_s` in `tracks.json`); main video ≈ 28.4–29.7 fps with occasional dropped-frame gaps.
* **Not present** in any iOS 18 file: `smart-style-delta-map` track, `texturestyle-info`, an audio track, key `1`/`2`/`m` (PROVEN 3/3).

### Still-image time — PROVEN
`still-image-time` is a single int8 `-1` sample at media time 0 **behind an empty edit** (`elst` media_time −1 for N movie ticks).
Still time = N / movie timescale (600) = **1.335 s / 1.4667 s / 1.265 s** → main frames 40 / 44 / 38.
Validation: the MOV linear-thumbnail frame that best correlates with the HEIC linear thumbnail is frame 40 / 43 / 39
(`aux_compare.json → best_frame_index`), i.e. the still frame ±1. Reading the sample at t=0 (ignoring the edit list) is wrong.

### Global metadata (`moov/meta`, `mdta` keys) — PROVEN 3/3
`smartstyle.rendering-version = 1`, `cast = 1`, `tone = 0.0`, `color = 0.0`, `intensity = 1.0`, `bypassed = 1`.
IMG_3940 is REPORTED to have `cast 0, tone 0.18, bypassed 0` plus `texturestyle.*` keys.
HYPOTHESIS: `bypassed = 1` means the motion was *not* rendered through the style pipeline, which would explain why these files lack
key `1`, key `2` and the delta-map track that IMG_3940 has.

## 2. `com.apple.quicktime.smartstyle-info` sample format

* mebx sample = `[u32 BE size][u32 BE local key id][payload]`; key's `dtyp` is absent/well-known-raw; payload begins `bplist00` (PROVEN 3/3, every sample).
* One sample per main-video frame, identical presentation times (PROVEN 3/3: 84/84, 88/88, 80/80).

| key | type | iOS 18 MOV (3 files) | relation to paired HEIC Styles plist | status |
|---|---|---|---|---|
| `0` | int | always **10** | HEIC `0` = 8 / 8 / 9 | PROVEN values; meaning (format version?) HYPOTHESIS. IMG_3940 REPORTS 65552 (0x10010). |
| `3` | data, 516 B | `u16 LE count = 257` + 257 × `u16 LE`, first 0, last 65534, monotonic non-decreasing in every frame; distinct per frame (84/84, 87/88, 78/80); frame-to-frame RMS 0–15 codes | HEIC `3` has the same layout. At the still frame RMS diff = **200.7 / 270.8 / 46.8** codes, max abs 889 / 1226 / 222; the closest frame is *not* the still frame (83 / 32 / 45) | Layout PROVEN. Tone curve on a 0..65534 scale: HYPOTHESIS. MOV ≠ HEIC at still: PROVEN. |
| `4` | float (real) | 5.646 / 6.0→6.031 / 5.646→8.062 (varies inside a clip) | **equal** to HEIC `4` at the still frame (3/3) | PROVEN. Every value is an exact multiple of 1/65 (MOV 3/3 files, all frames; HEIC corpus 504/504). Meaning (exposure/gain normaliser; XDRemux uses it as the linear divisor for the thumbnail) HYPOTHESIS. |
| `5` | int | 2 / 0 / 2 | **equal** to HEIC `5` (3/3) | PROVEN. |
| `h` | float | 0.4976–0.5791, slowly varying | HEIC h / MOV h at still = 4.025 / 4.030 / 4.622 → **no fixed ratio** | Values are exact multiples of 1/65536 (PROVEN 3/3). Meaning UNKNOWN. |
| `b` | float | always 0.0 | – | Present **exactly** on the frames that have matte samples (sky/person/skin share times): 42/42, 35/35, 32/32 (PROVEN 3/3). Samples with `b` are 638 B, without 625 B. IMG_3940 REPORTS `b` on 25/49 frames, consistent with its 15 fps mattes. |
| `1` | – | **absent** | HEIC `1` = 51840 B (12×9×8×3×10 f16) | Absence PROVEN. IMG_3940 REPORTS 1152 B (576 f16) per frame. |
| `2`, `m` | – | absent | – | IMG_3940 REPORTS `2` = true, `m` float. |

HEIC-only side finding (PROVEN on the 503-file corpus): HEIC Styles plist `i.Gain == 4 × h` exactly in 503/503 files that have `i`.

### Key `1` (576 coefficients) — HYPOTHESES ONLY
No file in this repo has it. 576 = 2⁶·3². Candidate layouts (none tested):

1. 64 cells × 3×3 colour matrix (e.g. 8×8 spatial grid or 64 luminance bins).
2. 4×3 spatial grid × 8 luminance planes × 3 outputs × 2 terms (gain/offset) — i.e. HEIC's 12×9×8×3×10 with a 3×3 spatial reduction and 10→2 basis.
3. 8 planes × 3 outputs × 4 terms (1, r, g, b affine) × 6 cells.
4. 192 × 3 (64 nodes × RGB × 3) or 24 × 24.
5. 16×12 grid × 3 outputs (per-cell scalar gain).

`key1_probe.py` scores factorizations on a real vector without a paired HEIC (stride of ≈1.0 values + autocorrelation + per-cell explained variance).
Decisive test: a native MOV with key `1` *and* a known neutral style (tone 0, colour 0) — identity terms reveal the stride.

## 3. Aux tracks vs HEIC at the still time — PROVEN (`*.aux_compare.json`)

Decode path for both sides: HEVC samples → Annex-B (parameter sets from `hvcC`) → `ffmpeg -f hevc` → raw YUV codes; HEIC is box-downsampled to the MOV size.

| track | HEIC counterpart | luma Pearson r at still (Calpe 071293 / Calpe 080897 / Yaiza) |
|---|---|---|
| smart-style-linear-thumbnail (128×96 10-bit) | `linearthumbnail` 1024×768 Main10 | 0.990 / 0.981 / 0.976 |
| sky | `semanticskymatte` | 0.988 / 0.992 / 0.996 |
| person | `portraiteffectsmatte` | 0.916 / 0.925 / 0.929 |
| skin | `semanticskinmatte` | 0.627 / 0.864 / 0.368 (MOV skin region larger) |

Linear thumbnail level: MOV codes are lower. Treating luma codes as Apple-Log (`L = 2^((v−C)/A) − B`, constants from XDRemux),
median linear ratio MOV/HEIC = **0.452 / 0.526 / 0.485 (≈ −1 stop)**, log-log slope 0.92 / 0.87 / 0.90 (`apple_log_luma_relation`; approximation, toe excluded).
Key `4` is identical on both sides, so it does not explain the offset. Cause (different capture/exposure path, or a different normaliser) UNKNOWN.
The `colr` on the MOV thumbnail says P3 primaries while `logs` says `rec2020.apple-log`; a P3-vs-2020 test on chroma was inconclusive.

## 4. Other metadata

* `live-photo-info`: 200 B binary per frame; word 0 = 3 (version?). Per-word variation logged in `*.live_photo_info_words.json`; semantics UNKNOWN.
* `live-photo-still-image-transform`: dtyp well-known 83, 72 B = 3×3 BE float64, near identity (PROVEN layout by value plausibility; meaning REPORTED/standard).
* `…-reference-dimensions`: 1920×1440 (float pair).
* `video-orientation`: int16 6.
