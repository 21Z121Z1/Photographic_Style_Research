# What XDRemux must write into a Live Photo MOV for Photographic Styles

Nothing on this list is yet **proven required**: no ablation has been run on a device. "Proven required" is therefore empty, and the
items are split by how much evidence we have that a native file carries them. Run the experiment at the bottom to move items up.

## A. Proven required (device-tested)
*None yet.* Generic Live Photo pairing (outside Styles) is known to need the shared `com.apple.quicktime.content.identifier`
and a `still-image-time` track; XDRemux already writes those — not re-tested here.

## B. Present in every native styled Live Photo MOV we parsed
(3 iOS 18 files PROVEN; IMG_3940 iOS 27.2 REPORTED.)

| item | exact form observed | notes for the writer |
|---|---|---|
| Global `mdta` keys | `com.apple.quicktime.smartstyle.{rendering-version=1, cast, tone, color, intensity, bypassed}` | iOS 18: bypassed=1; iOS 27: bypassed=0 + `texturestyle.*` (REPORTED) |
| `smartstyle-info` mebx track | 1 sample per main frame, same PTS; bplist with `0, 3, 4, 5, h` (+ `b` on matte frames); `tref cdsc→1` | key 4 must equal HEIC key 4 at the still frame; key 5 = HEIC key 5; key 3 = 257-point u16 curve |
| `smart-style-linear-thumbnail` auxv | HEVC Main10 128×96, `colr nclc 12/2/6`, `logs`=`com.apple.rec2020.apple-log`, `udta/tagc` | ≈ HEIC linear thumbnail −1 stop; sample rate 30 fps (iOS 18) or 15 fps (iOS 27 REPORTED) |
| `sky`, `person`, `skin` auxv | HEVC 8-bit 256×192 4:2:0 at a reduced rate, `udta/tagc` | matte times = frames with key `b` |
| `still-image-time` | int8 −1 at media 0 behind an empty edit | edit length sets the still frame |
| `live-photo-info` | 200 B/frame | opaque; copy from a native template |
| still-image-transform (+ reference dimensions) | 3×3 f64 + dimensions | identity is plausible |

## C. Seen only in iOS 27.2 IMG_3940 (REPORTED, not re-parsed)
* `smartstyle-info` key `1` (576 f16 per frame), key `2` (bool true), `m` (float); key `0` = 65552.
* `smart-style-delta-map` auxv, full resolution, 10-bit, linear transfer, P3.
* `texturestyle-info` mebx track + `texturestyle.*` globals.
* `tref vmap → 1` on auxv tracks and `cdep` on meta tracks. (iOS 18 files have neither, so writing both is the safe superset.)

## D. Unknown — needs a device test
1. Does Photos re-render **motion** when Tone/Color/Cast change, or only the still? Under which `bypassed` value?
2. Is `smartstyle-info` required for the Styles UI to appear on a Live Photo, or is the HEIC alone enough?
3. Are the auxv tracks (thumbnail / mattes) read for video re-rendering, or only kept for future use?
4. Which keys are mandatory per frame (`3`? `h`? `b`?) and whether `0` must be 10 vs 65552 for a given iOS.
5. Whether key `1` / delta map are needed for an *un-bypassed* video, and their layout.
6. The −1 stop offset between MOV and HEIC linear thumbnails.

## Next device experiment (recommended)
1. On an iPhone 16+ capture one Live Photo with a non-default style (e.g. Amber, Tone −0.5) on the newest iOS available; AirDrop it to a Mac
   with "All Photos Data" so the original HEIC+MOV pair is preserved. Parse with `livephoto_mov.py` — check `bypassed`, key `1`, delta-map.
2. Re-import ablation variants made with `ablate.py` (only `moov` is rewritten):
   * `--drop-key com.apple.quicktime.smartstyle-info`
   * `--drop-video-map smart-style-linear-thumbnail`, then `--drop-video-map sky --drop-video-map person --drop-video-map skin`
   * `--set-global com.apple.quicktime.smartstyle.bypassed=0` (and `=1`)
3. For each: does the Styles control appear; after changing Tone/Color, export **"Save as Video"** and compare 3 frames with the original export
   (PSNR / mean ΔE). The variant whose motion stops following the style tells us which item is required.
