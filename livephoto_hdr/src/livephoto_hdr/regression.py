"""IMG_8148 temporal regression and the same measurement on other local pairs.

Native rendering is not claimed. Numbers in the written JSON come from this
process and name the input SHA-256.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import plistlib
import subprocess
import tempfile
from fractions import Fraction
from pathlib import Path

import numpy as np

from . import NATIVE_BLOCK
from .apple_log import piecewise_inverse, unpack_code
from .classify import classify
from .color import REC2020_KB, REC2020_KR, rgb_from_yuv420p10
from .metrics import HISTORICAL_ROIS, log_luma_from_log_rgb, mae_ev, structure, translation, upsample_bilinear
from .observe import compensate
from .qt import (
    bypassed_flag,
    content_identifier,
    fraction_record,
    parse_movie,
    presentation_times,
    still_time,
    style_h_by_presentation,
)
from .safe_output import allocate_output
from .timebase import bracket

MODES = ("hold_nearest", "fixed_log", "motion_gated", "motion_ungated")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _ffprobe_pts(path: Path, stream_index: int) -> list[int]:
    raw = subprocess.check_output(
        ["ffprobe", "-v", "error", "-select_streams", str(stream_index),
         "-show_entries", "frame=pts", "-of", "csv=p=0", str(path)],
        text=True,
    )
    return [int(line.strip().strip(",")) for line in raw.splitlines() if line.strip().strip(",")]


def _area(image: np.ndarray, factor: int) -> np.ndarray:
    height, width = image.shape
    trimmed_h = height // factor * factor
    trimmed_w = width // factor * factor
    return image[:trimmed_h, :trimmed_w].reshape(trimmed_h // factor, factor, trimmed_w // factor, factor).mean(axis=(1, 3))


def _extract_still(heic: Path, work: Path) -> dict:
    source = Path(__file__).resolve().parents[2] / "recovered/artifacts/research/20261106-still-video-linear-thumbnail-pair/src/extract.py"
    spec = importlib.util.spec_from_file_location("recovered_extract", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.run(heic, work / "still-extract")
    plist = plistlib.loads((work / "still-extract" / "styles.plist").read_bytes())
    encoding = plist.get("i") or {}
    return {
        "h": float(plist["h"]) if "h" in plist else None,
        "version": plist.get("0"),
        "gain": float(encoding["Gain"]) if "Gain" in encoding else None,
        "originalRangeMin": float(encoding["OriginalRangeMin"]) if "OriginalRangeMin" in encoding else None,
        "originalRangeMax": float(encoding["OriginalRangeMax"]) if "OriginalRangeMax" in encoding else None,
        "isolated": work / "still-extract" / "linear-isolated.heic",
    }


def run(mov: Path, heic: Path, output: Path) -> dict:
    output = allocate_output(output, protected=[mov.parent, heic.parent, mov, heic])
    digests = {str(mov.resolve()): sha256(mov), str(heic.resolve()): sha256(heic)}
    movie = parse_movie(mov)
    primary = movie.track_by_role("primary")
    scene = movie.track_by_role("scene-thumbnail")
    if primary is None or scene is None:
        raise RuntimeError("primary video or apple-log scene thumbnail track was not found")
    main_times = presentation_times(primary)
    scene_times = presentation_times(scene)
    scale = movie.movie_timescale
    probe_main = _ffprobe_pts(mov, primary.index)
    probe_scene = _ffprobe_pts(mov, scene.index)
    ours_main = [int(time * scale) for time in main_times]
    ours_scene = [int(time * scale) for time in scene_times]
    if ours_main != probe_main or ours_scene != probe_scene:
        raise RuntimeError("rational PTS does not match ffprobe; refusing to score")
    h_by_time = style_h_by_presentation(movie)
    if any(time not in h_by_time for time in scene_times):
        raise RuntimeError("a scene thumbnail PTS has no exact smartstyle h")
    intervals = [later - earlier for earlier, later in zip(scene_times, scene_times[1:]) if later > earlier]
    gaps = []
    for index, (left, right) in enumerate(zip(scene_times, scene_times[1:])):
        inside = [time for time in main_times if left < time < right]
        record = bracket(scene_times, inside[len(inside) // 2] if inside else left)
        gaps.append({
            "afterThumbnail": index,
            "left": fraction_record(left),
            "right": fraction_record(right),
            "duration": fraction_record(right - left),
            "mainFramesInside": len(inside),
            "longGap": bool(record["longGap"] or (intervals and (right - left) > 2 * sorted(intervals)[len(intervals) // 2])),
        })
    # longGap on the gap itself, not on a midpoint that might fall on a thumbnail.
    median = sorted(intervals)[len(intervals) // 2]
    for gap, (left, right) in zip(gaps, zip(scene_times, scene_times[1:])):
        gap["longGap"] = (right - left) > 2 * median
    still = still_time(movie)
    with tempfile.TemporaryDirectory(prefix="livephoto-hdr-") as temporary:
        work = Path(temporary)
        analysis_w = 384 if primary.width % 384 == 0 else 192
        analysis_h = primary.height * analysis_w // primary.width
        luma_path = work / "luma.raw"
        subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-i", str(mov), "-map", f"0:{primary.index}",
             "-fps_mode", "passthrough",
             "-vf", f"scale={analysis_w}:{analysis_h}:flags=area,format=gray",
             "-f", "rawvideo", str(luma_path)],
            check=True,
        )
        luma = np.fromfile(luma_path, dtype=np.uint8).reshape(len(main_times), analysis_h, analysis_w).astype(np.float64) / 255.0
        scene_raw_path = work / "scene.yuv"
        subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-i", str(mov), "-map", f"0:{scene.index}",
             "-fps_mode", "passthrough",
             "-f", "rawvideo", "-pix_fmt", "yuv420p10le", str(scene_raw_path)],
            check=True,
        )
        scene_raw = np.fromfile(scene_raw_path, dtype="<u2")
        scene_w, scene_h = scene.width, scene.height
        y_count = scene_w * scene_h
        frame_samples = y_count * 3 // 2
        luma_codes = np.array([scene_raw[i * frame_samples:i * frame_samples + y_count] for i in range(len(scene_times))])
        code_min = int(luma_codes.min())
        code_max = int(luma_codes.max())
        stream_color = json.loads(subprocess.check_output(
            ["ffprobe", "-v", "error", "-select_streams", str(scene.index),
             "-show_entries", "stream=color_range,color_space,color_primaries,color_transfer",
             "-of", "json", str(mov)],
            text=True,
        ))["streams"][0]
        if stream_color.get("color_range") != "pc":
            raise RuntimeError(
                f"refusing to unpack Apple Log codes; ffprobe color_range is {stream_color.get('color_range')!r}, "
                f"nclc fullRangeFlag is {(scene.colr or {}).get('fullRangeFlag')}, luma codes are {code_min}..{code_max}"
            )
        code_range_reason = (
            "ffprobe color_range=pc on this run. The nclc box has no range bit. "
            f"Luma codes {code_min}..{code_max} also fit the legal 64..940 window, so the pc tag is the deciding evidence. "
            "Legal-range unpacking is not applied. The bt709 transfer tag is not the scene EOTF; the logs box says apple-log."
        )
        rgb = rgb_from_yuv420p10(scene_raw, scene_w, scene_h, len(scene_times), REC2020_KR, REC2020_KB)
        linear = piecewise_inverse(rgb)
        log_scene = []
        for index, time in enumerate(scene_times):
            scaled = linear[index] * h_by_time[time]
            log_scene.append(np.log2(np.maximum(scaled, 1e-8)))
        factor = analysis_w // scene_w
        flow_luma = np.stack([_area(frame, factor) for frame in luma], axis=0)
        main_index = {time: index for index, time in enumerate(main_times)}
        def at_time(time: Fraction, mode: str):
            info = bracket(scene_times, time)
            left = scene_times.index(info["left"])
            right = scene_times.index(info["right"])
            image, stats = compensate(
                log_scene[left], log_scene[right],
                flow_luma[main_index[info["left"]]], flow_luma[main_index[info["right"]]],
                flow_luma[main_index[time]] if time in main_index else flow_luma[main_index[_nearest(main_times, time)]],
                float(info["alpha"]), mode, info["policy"], info["longGap"],
                float(info["medianInterval"]), float(info["gap"]),
            )
            stats.update(policy=info["policy"], longGap=info["longGap"], alpha=fraction_record(info["alpha"]))
            return image, stats

        heldout = []
        for index in range(1, len(scene_times) - 1):
            time = scene_times[index]
            left_time, right_time = scene_times[index - 1], scene_times[index + 1]
            span = right_time - left_time
            alpha = Fraction(time - left_time, span)
            long_gap = span > 2 * median
            scores = {}
            stats = None
            for mode in MODES:
                image, stats = compensate(
                    log_scene[index - 1], log_scene[index + 1],
                    flow_luma[main_index[left_time]], flow_luma[main_index[right_time]],
                    flow_luma[main_index[time]],                     float(alpha), mode,
                    "interpolation", long_gap, float(median), float(span),
                )
                scores[mode] = mae_ev(image, log_scene[index])
            heldout.append({
                "thumbnail": index,
                "pts": fraction_record(time),
                "bracket": {"left": fraction_record(left_time), "right": fraction_record(right_time), "longGap": long_gap},
                "motionGated": {key: stats[key] for key in ("timeConfidence", "lowConfidenceFraction", "meanFlowConfidence")},
                "scores": scores,
            })
        follow = _follow(main_times, luma, at_time, analysis_w, primary.width)
        still_report = _still(heic, work, still, scene_times, main_times, h_by_time, at_time)
    if sha256(mov) != digests[str(mov.resolve())] or sha256(heic) != digests[str(heic.resolve())]:
        raise RuntimeError("input bytes changed during the run")
    positive_gaps = [gap for gap in gaps if gap["longGap"]]
    report = {
        "schema": "livephoto-hdr-temporal-regression-v1",
        "native": NATIVE_BLOCK,
        "inputs": {
            "mov": str(mov.resolve()),
            "heic": str(heic.resolve()),
            "sha256": {path.name: digest for path, digest in ((mov, digests[str(mov.resolve())]), (heic, digests[str(heic.resolve())]))},
        },
        "identity": {"contentIdentifier": content_identifier(movie)},
        "classification": classify(
            bypassed=bypassed_flag(movie),
            delta_present=any(track.role == "delta-candidate" for track in movie.tracks),
            style_metadata_present=movie.track_by_role("smartstyle-info") is not None,
            scene_thumbnail_present=True,
        ),
        "timing": {
            "movieTimescale": scale,
            "mainFrames": len(main_times),
            "sceneThumbnails": len(scene_times),
            "ptsMatchesFfprobe": True,
            "stillTime": fraction_record(still) if still is not None else None,
            "stillInsideLongGap": bool(still is not None and positive_gaps and positive_gaps[0]["left"]["decimal"] < float(still) < positive_gaps[0]["right"]["decimal"]),
            "longGaps": positive_gaps,
            "sceneTrack": {
                "appleLog": scene.apple_log,
                "width": scene.width,
                "height": scene.height,
                "colr": scene.colr,
                "lumaCodeMin": code_min,
                "lumaCodeMax": code_max,
                "codeRange": "full",
                "codeRangeReason": code_range_reason,
                "ffprobe": stream_color,
            },
            "hVideo": {
                "count": len(h_by_time),
                "first": h_by_time[main_times[0]],
                "last": h_by_time[main_times[-1]],
                "min": min(h_by_time.values()),
                "max": max(h_by_time.values()),
            },
        },
        "heldOutThumbnails": {
            "limitation": "Hiding one native thumbnail doubles that interval. It is a stress test, not ground truth for frames that never had a thumbnail.",
            "exposureFit": False,
            "space": "Rec.2020 linear after the piecewise Apple Log inverse, scaled by each thumbnail's own h. No P3 matrix.",
            "summary": {mode: _mean([row["scores"][mode]["maeEV"] for row in heldout]) for mode in MODES},
            "rows": heldout,
        },
        "spatialFollow": follow,
        "stillObservation": still_report,
        "gtmLtm": "not inverted; the scene thumbnail is a low-frequency reference, not a GTM or LTM inverse",
    }
    (output / "temporal.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    return report


def _nearest(times: list[Fraction], time: Fraction) -> Fraction:
    return min(times, key=lambda candidate: abs(candidate - time))


def _mean(values: list[float]) -> float:
    return float(np.mean(values)) if values else float("nan")


def _follow(main_times, luma, at_time, analysis_w, coded_w) -> dict:
    if len(main_times) != 56:
        return {"status": "not-applicable", "reason": f"{len(main_times)} main frames; the 46-55 window is the 56-frame IMG_8148 pan measurement"}
    start, end = 46, 55
    scale = coded_w / analysis_w
    main_struct = [structure(np.log2(np.maximum(luma[index], 1 / 255))) for index in range(start, end + 1)]
    method_luma = {}
    for mode in ("fixed_log", "motion_gated", "hold_nearest"):
        fields = []
        for index in range(start, end + 1):
            image, _stats = at_time(main_times[index], mode)
            small = log_luma_from_log_rgb(image)
            fields.append(structure(upsample_bilinear(small, luma.shape[1], luma.shape[2])))
        method_luma[mode] = fields
    def shifts(series):
        rows = []
        for offset in range(1, len(series)):
            full = translation(series[0], series[offset])
            rows.append({
                "fromFrame": start,
                "toFrame": start + offset,
                "dxCoded": full["dx"] * scale,
                "dyCoded": full["dy"] * scale,
                "peak": full["peak"],
                "rois": [_roi_shift(series[0], series[offset], roi, scale) for roi in HISTORICAL_ROIS],
            })
        return rows
    main_rows = shifts(main_struct)
    compared = {}
    for mode, series in method_luma.items():
        rows = shifts(series)
        headline = rows[-1]
        main_headline = main_rows[-1]
        compared[mode] = {
            "rows": rows,
            "frame55MinusMainDxCoded": headline["dxCoded"] - main_headline["dxCoded"],
            "frame55MinusMainDyCoded": headline["dyCoded"] - main_headline["dyCoded"],
        }
    return {
        "status": "measured",
        "frames": [start, end],
        "analysisSize": [analysis_w, luma.shape[1]],
        "codedPixelsPerAnalysisPixel": scale,
        "main": main_rows,
        "methods": compared,
        "note": "Follow error is method shift minus main-luma shift over presentation frames 46 to 55. It is not the historical gain-map displacement, which was not in the uploaded inputs.",
    }


def _roi_shift(earlier, later, roi, scale) -> dict:
    y0, y1, x0, x1 = roi
    found = translation(earlier[y0:y1, x0:x1], later[y0:y1, x0:x1])
    return {"roi": [y0, y1, x0, x1], "dxCoded": found["dx"] * scale, "dyCoded": found["dy"] * scale, "peak": found["peak"]}


def _still(heic, work, still, scene_times, main_times, h_by_time, at_time) -> dict:
    try:
        from .heif_linear import decode_isolated_rgb
        extracted = _extract_still(heic, work)
        rgb, facts = decode_isolated_rgb(extracted["isolated"], work)
        codes = np.clip(rgb, 0, None)
        linear = piecewise_inverse(codes)
        if extracted["gain"]:
            linear = np.clip(linear / extracted["gain"], extracted["originalRangeMin"], extracted["originalRangeMax"])
        small = linear.reshape(96, 8, 128, 8, 3).mean(axis=(1, 3))
        image, stats = at_time(still, "motion_gated")
        video = np.exp2(image)
        # h_photo puts the video observation into the still's normalization only as a ratio.
        # The still was divided by its own Gain, which is a different contract from h.
        ratio = None
        if extracted["h"]:
            nearest = min(main_times, key=lambda time: abs(time - still))
            video = video * (1.0 / extracted["h"])
            ratio = h_by_time[nearest] / extracted["h"]
        pred = np.log2(np.maximum(video @ np.array([0.2627, 0.6780, 0.0593]), 1e-8))
        ref = np.log2(np.maximum(small @ np.array([0.2627, 0.6780, 0.0593]), 1e-8))
        finite = np.isfinite(pred) & np.isfinite(ref)
        error = (pred - ref)[finite]
        return {
            "status": "decoded-unregistered",
            "acceptance": False,
            "reason": "Still and video thumbnails are not in one recovered color basis, and no SDR geometry registration was run. This MAE is not the acceptance metric.",
            "photoH": extracted["h"],
            "photoGain": extracted["gain"],
            "photoRange": [extracted["originalRangeMin"], extracted["originalRangeMax"]],
            "nearestVideoHOverPhotoH": ratio,
            "decode": facts,
            "unregisteredLumaMaeEV": float(np.mean(np.abs(error))) if error.size else None,
            "unregisteredFinitePixels": int(finite.sum()),
            "interpolation": stats,
        }
    except Exception as exc:
        return {"status": "blocked", "acceptance": False, "error": f"{type(exc).__name__}: {exc}"}
