"""QuickTime timing and Photographic Styles metadata.

Location keys are dropped and never returned. Presentation times are exact
rationals. Composition offsets are read as int32 because these Apple files
store negative offsets in a version-0 ctts box; the real-file check is that
the resulting presentation sequence matches ffprobe.
"""
from __future__ import annotations

import plistlib
import struct
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path

from .timebase import edit_presentation, rational


_LOCATION_MARKERS = ("location", "iso6709", "gps", "latitude", "longitude")
_METADATA_ALLOW = {
    "com.apple.quicktime.content.identifier",
    "com.apple.quicktime.smartstyle.bypassed",
    "com.apple.quicktime.smartstyle.rendering-version",
    "com.apple.quicktime.smartstyle.tone",
    "com.apple.quicktime.smartstyle.color",
    "com.apple.quicktime.smartstyle.intensity",
    "com.apple.quicktime.smartstyle.cast",
    "com.apple.quicktime.live-photo.auto",
    "com.apple.quicktime.make",
    "com.apple.quicktime.model",
    "com.apple.quicktime.software",
}


@dataclass
class SampleTiming:
    decode_index: int
    media_pts: int
    presentation: Fraction | None


@dataclass
class Track:
    index: int
    track_id: int
    handler: str
    width: int
    height: int
    media_timescale: int
    samples: list[SampleTiming]
    codec: str = ""
    apple_log: str | None = None
    colr: dict | None = None
    role: str | None = None
    metadata_keys: list[str] = field(default_factory=list)
    metadata_values: list[dict] = field(default_factory=list)

    @property
    def presentation_samples(self) -> list[SampleTiming]:
        present = [sample for sample in self.samples if sample.presentation is not None]
        return sorted(present, key=lambda sample: (sample.presentation, sample.decode_index))


@dataclass
class Movie:
    path: str
    movie_timescale: int
    movie_duration: int
    tracks: list[Track]
    metadata: dict

    def track_by_role(self, role: str) -> Track | None:
        matches = [track for track in self.tracks if track.role == role]
        if len(matches) != 1:
            return None
        return matches[0]


def _boxes(data: bytes, start: int, end: int):
    pos = start
    while pos + 8 <= end:
        size, kind = struct.unpack_from(">I4s", data, pos)
        header = 8
        if size == 1:
            size = struct.unpack_from(">Q", data, pos + 8)[0]
            header = 16
        if size == 0:
            size = end - pos
        if size < header or pos + size > end:
            break
        yield pos, header, kind, pos + size
        pos += size


def _child(data: bytes, start: int, end: int, name: bytes):
    for item in _boxes(data, start, end):
        if item[2] == name:
            return item
    return None


def _payload(data: bytes, box) -> tuple[int, int]:
    return box[0] + box[1], box[3]


def parse_movie(path: Path) -> Movie:
    data = path.read_bytes()
    moov = _child(data, 0, len(data), b"moov")
    if moov is None:
        raise ValueError(f"no moov atom: {path}")
    moov_start, moov_end = _payload(data, moov)
    mvhd = _child(data, moov_start, moov_end, b"mvhd")
    movie_scale, movie_duration = _movie_header(data, *_payload(data, mvhd))
    tracks = []
    index = 0
    for box in _boxes(data, moov_start, moov_end):
        if box[2] != b"trak":
            continue
        tracks.append(_track(data, box, index, movie_scale))
        index += 1
    _assign_roles(tracks)
    metadata = _movie_metadata(data, moov_start, moov_end)
    return Movie(str(path.resolve()), movie_scale, movie_duration, tracks, metadata)


def _movie_header(data: bytes, start: int, end: int) -> tuple[int, int]:
    version = data[start]
    if version == 0:
        scale, duration = struct.unpack_from(">II", data, start + 12)
    else:
        scale = struct.unpack_from(">I", data, start + 20)[0]
        duration = struct.unpack_from(">Q", data, start + 24)[0]
    return int(scale), int(duration)


def _track(data: bytes, box, index: int, movie_scale: int) -> Track:
    start, end = _payload(data, box)
    tkhd = _child(data, start, end, b"tkhd")
    track_id, width, height = _tkhd(data, *_payload(data, tkhd))
    edits = _edits(data, start, end)
    mdia = _child(data, start, end, b"mdia")
    mdia_start, mdia_end = _payload(data, mdia)
    hdlr = _child(data, mdia_start, mdia_end, b"hdlr")
    handler = data[_payload(data, hdlr)[0] + 8:_payload(data, hdlr)[0] + 12].decode("latin1")
    mdhd = _child(data, mdia_start, mdia_end, b"mdhd")
    media_scale = _mdhd_timescale(data, *_payload(data, mdhd))
    minf = _child(data, mdia_start, mdia_end, b"minf")
    stbl = _child(data, *_payload(data, minf), b"stbl")
    stbl_start, stbl_end = _payload(data, stbl)
    codec, apple_log, colr, metadata_keys = _sample_entry(data, stbl_start, stbl_end)
    decode_times, offsets = _timing_tables(data, stbl_start, stbl_end)
    samples = []
    for decode_index, (decode_time, offset) in enumerate(zip(decode_times, offsets)):
        presentation = edit_presentation(decode_time + offset, edits, media_scale, movie_scale)
        samples.append(SampleTiming(decode_index, decode_time + offset, presentation))
    values = []
    if handler == "meta" and metadata_keys:
        values = _metadata_values(data, stbl_start, stbl_end, metadata_keys)
    role = _udta_role(data, start, end)
    return Track(index, track_id, handler, width, height, media_scale, samples, codec, apple_log, colr, role, metadata_keys, values)


def _tkhd(data: bytes, start: int, end: int) -> tuple[int, int, int]:
    version = data[start]
    if version == 0:
        track_id = struct.unpack_from(">I", data, start + 12)[0]
        width, height = struct.unpack_from(">II", data, start + 76)
    else:
        track_id = struct.unpack_from(">I", data, start + 20)[0]
        width, height = struct.unpack_from(">II", data, start + 88)
    return int(track_id), int(width >> 16), int(height >> 16)


def _mdhd_timescale(data: bytes, start: int, end: int) -> int:
    version = data[start]
    offset = 12 if version == 0 else 20
    return int(struct.unpack_from(">I", data, start + offset)[0])


def _edits(data: bytes, start: int, end: int) -> list[tuple[int, int]]:
    edts = _child(data, start, end, b"edts")
    if edts is None:
        return []
    elst = _child(data, *_payload(data, edts), b"elst")
    if elst is None:
        return []
    payload, payload_end = _payload(data, elst)
    version = data[payload]
    count = struct.unpack_from(">I", data, payload + 4)[0]
    cursor = payload + 8
    edits = []
    for _ in range(count):
        if version == 1:
            duration, media_time = struct.unpack_from(">Qq", data, cursor)
            cursor += 16
        else:
            duration, media_time = struct.unpack_from(">Ii", data, cursor)
            cursor += 8
        cursor += 4
        edits.append((int(duration), int(media_time)))
    return edits


def _timing_tables(data: bytes, start: int, end: int) -> tuple[list[int], list[int]]:
    stts = _child(data, start, end, b"stts")
    payload, _ = _payload(data, stts)
    count = struct.unpack_from(">I", data, payload + 4)[0]
    cursor = payload + 8
    decode = []
    time = 0
    for _ in range(count):
        sample_count, delta = struct.unpack_from(">II", data, cursor)
        cursor += 8
        for _sample in range(sample_count):
            decode.append(time)
            time += delta
    offsets = [0] * len(decode)
    ctts = _child(data, start, end, b"ctts")
    if ctts is not None:
        payload, _ = _payload(data, ctts)
        count = struct.unpack_from(">I", data, payload + 4)[0]
        cursor = payload + 8
        offsets = []
        for _ in range(count):
            sample_count, offset = struct.unpack_from(">Ii", data, cursor)
            cursor += 8
            offsets.extend([int(offset)] * sample_count)
        if len(offsets) != len(decode):
            raise ValueError("ctts sample count does not match stts")
    return decode, offsets


def _sample_entry(data: bytes, start: int, end: int):
    stsd = _child(data, start, end, b"stsd")
    payload, payload_end = _payload(data, stsd)
    count = struct.unpack_from(">I", data, payload + 4)[0]
    cursor = payload + 8
    codec = ""
    apple_log = None
    colr = None
    keys: list[str] = []
    if count:
        size, kind = struct.unpack_from(">I4s", data, cursor)
        codec = kind.decode("latin1")
        entry_end = cursor + size
        extensions = cursor + 86 if codec in {"hvc1", "avc1", "hev1"} else cursor + 16
        for box in _boxes(data, extensions, entry_end):
            body = data[box[0] + box[1]:box[3]]
            if box[2] == b"logs":
                apple_log = body.split(b"\0", 1)[0].decode("latin1", "replace")
            elif box[2] == b"colr" and body[:4] == b"nclc" and len(body) >= 10:
                primaries, transfer, matrix = struct.unpack_from(">HHH", body, 4)
                colr = {"type": "nclc", "primaries": primaries, "transfer": transfer, "matrix": matrix, "fullRangeFlag": None}
            elif box[2] == b"colr" and body[:4] == b"nclx" and len(body) >= 11:
                primaries, transfer, matrix = struct.unpack_from(">HHH", body, 4)
                colr = {"type": "nclx", "primaries": primaries, "transfer": transfer, "matrix": matrix, "fullRangeFlag": bool(body[10] & 0x80)}
            elif box[2] == b"keys":
                keys = _keys(body)
    return codec, apple_log, colr, keys


def _keys(body: bytes) -> list[str]:
    count = struct.unpack_from(">I", body, 4)[0]
    cursor = 8
    names = []
    for _ in range(count):
        size = struct.unpack_from(">I", body, cursor)[0]
        token = body[cursor + 4:cursor + 8]
        name_at = 12 if token == b"keyd" else 8
        names.append(body[cursor + name_at:cursor + size].split(b"\0", 1)[0].decode("latin1", "replace"))
        cursor += size
    return names


def _sample_table(data: bytes, start: int, end: int) -> tuple[list[int], list[int]]:
    stsz = _child(data, start, end, b"stsz")
    payload, _ = _payload(data, stsz)
    sample_size, count = struct.unpack_from(">II", data, payload + 4)
    if sample_size:
        sizes = [int(sample_size)] * count
    else:
        sizes = list(struct.unpack_from(">" + "I" * count, data, payload + 12))
    stsc = _child(data, start, end, b"stsc")
    payload, _ = _payload(data, stsc)
    entries = struct.unpack_from(">I", data, payload + 4)[0]
    cursor = payload + 8
    runs = []
    for _ in range(entries):
        first, per_chunk, _description = struct.unpack_from(">III", data, cursor)
        cursor += 12
        runs.append((first, per_chunk))
    chunk_box = _child(data, start, end, b"stco") or _child(data, start, end, b"co64")
    payload, _ = _payload(data, chunk_box)
    chunk_count = struct.unpack_from(">I", data, payload + 4)[0]
    if chunk_box[2] == b"stco":
        chunks = list(struct.unpack_from(">" + "I" * chunk_count, data, payload + 8))
    else:
        chunks = list(struct.unpack_from(">" + "Q" * chunk_count, data, payload + 8))
    offsets = []
    sample_index = 0
    for run_index, (first, per_chunk) in enumerate(runs):
        last = runs[run_index + 1][0] - 1 if run_index + 1 < len(runs) else len(chunks)
        for chunk_number in range(first, last + 1):
            offset = chunks[chunk_number - 1]
            for _ in range(per_chunk):
                offsets.append(offset)
                offset += sizes[sample_index]
                sample_index += 1
    if sample_index != len(sizes):
        raise ValueError("sample-to-chunk map does not cover stsz")
    return sizes, offsets


def _metadata_values(data: bytes, start: int, end: int, keys: list[str]) -> list[dict]:
    sizes, offsets = _sample_table(data, start, end)
    values = []
    for size, offset in zip(sizes, offsets):
        raw = data[offset:offset + size]
        item = {}
        cursor = 0
        while cursor + 8 <= len(raw):
            atom, key_index = struct.unpack_from(">II", raw, cursor)
            if atom < 8 or cursor + atom > len(raw):
                break
            payload = raw[cursor + 8:cursor + atom]
            cursor += atom
            if not 1 <= key_index <= len(keys):
                continue
            name = keys[key_index - 1]
            if _sensitive(name):
                continue
            parsed = _small_metadata_value(payload)
            if parsed is not None:
                item[name] = parsed
        values.append(item)
    return values


def _small_metadata_value(payload: bytes):
    if payload.startswith(b"bplist00"):
        loaded = plistlib.loads(payload)
        return _public_plist(loaded)
    return {"bytes": len(payload)}


def _public_plist(value):
    if isinstance(value, dict):
        public = {}
        for key, item in value.items():
            name = str(key)
            if _sensitive(name):
                continue
            if isinstance(item, (int, float, str)) and not isinstance(item, bool):
                public[name] = item
            elif isinstance(item, bytes):
                public[name] = {"bytes": len(item)}
        return public
    if isinstance(value, (int, float, str)):
        return value
    return {"omitted": type(value).__name__}


def _udta_role(data: bytes, start: int, end: int) -> str | None:
    udta = _child(data, start, end, b"udta")
    if udta is None:
        return None
    for box in _boxes(data, *_payload(data, udta)):
        if box[2] == b"tagc":
            text = data[box[0] + box[1]:box[3]].split(b"\0", 1)[0].decode("latin1", "replace")
            if "linear-thumbnail" in text:
                return "scene-thumbnail"
            return text
    return None


def _assign_roles(tracks: list[Track]) -> None:
    for track in tracks:
        if track.apple_log and "apple-log" in track.apple_log:
            track.role = "scene-thumbnail"
        elif track.handler == "vide":
            track.role = "primary"
        elif any(key.endswith("smartstyle-info") for key in track.metadata_keys):
            track.role = "smartstyle-info"
        elif any(key.endswith("still-image-time") for key in track.metadata_keys):
            track.role = "still-image-time"
    primary = next((track for track in tracks if track.role == "primary"), None)
    if primary is None:
        return
    for track in tracks:
        if track.role or track.handler != "auxv":
            continue
        if track.width == primary.width and track.height == primary.height:
            transfer = (track.colr or {}).get("transfer")
            track.role = "delta-candidate" if transfer in {8, 14} else "fullsize-aux-unclassified"


def _movie_metadata(data: bytes, start: int, end: int) -> dict:
    meta = _child(data, start, end, b"meta")
    if meta is None:
        return {}
    meta_start, meta_end = _payload(data, meta)
    child_start = meta_start
    if meta_start + 8 <= meta_end:
        size, kind = struct.unpack_from(">I4s", data, meta_start)
        if kind not in {b"hdlr", b"keys", b"ilst"}:
            child_start = meta_start + 4
    keys_box = _child(data, child_start, meta_end, b"keys")
    ilst = _child(data, child_start, meta_end, b"ilst")
    if keys_box is None or ilst is None:
        return {}
    names = _keys(data[_payload(data, keys_box)[0]:keys_box[3]])
    public = {}
    for box in _boxes(data, *_payload(data, ilst)):
        index = int.from_bytes(box[2], "big")
        if not 1 <= index <= len(names):
            continue
        name = names[index - 1]
        if name not in _METADATA_ALLOW or _sensitive(name):
            continue
        body = data[box[0] + box[1]:box[3]]
        if len(body) < 16 or body[4:8] != b"data":
            continue
        public[name] = _data_atom(body)
    return public


def _data_atom(body: bytes):
    size = struct.unpack_from(">I", body, 0)[0]
    kind = struct.unpack_from(">I", body, 8)[0]
    value = body[16:size]
    if kind == 1:
        return value.decode("utf-8", "replace")
    if kind == 21:
        return int.from_bytes(value, "big", signed=True)
    if kind == 22:
        return int.from_bytes(value, "big", signed=False)
    if kind == 23 and len(value) == 4:
        return struct.unpack(">f", value)[0]
    if kind == 23 and len(value) == 8:
        return struct.unpack(">d", value)[0]
    return {"bytes": len(value), "type": kind}


def _sensitive(name: str) -> bool:
    lowered = name.lower()
    return any(marker in lowered for marker in _LOCATION_MARKERS)


def bypassed_flag(movie: Movie) -> bool | None:
    value = movie.metadata.get("com.apple.quicktime.smartstyle.bypassed")
    if value is None:
        return None
    if value not in (0, 1):
        raise ValueError(f"unexpected smartstyle.bypassed value {value!r}")
    return bool(value)


def content_identifier(movie: Movie) -> str | None:
    value = movie.metadata.get("com.apple.quicktime.content.identifier")
    return value if isinstance(value, str) else None


def still_time(movie: Movie) -> Fraction | None:
    track = movie.track_by_role("still-image-time")
    if track is None:
        return None
    present = track.presentation_samples
    if len(present) != 1:
        raise ValueError(f"expected one still-image presentation, found {len(present)}")
    return present[0].presentation


def presentation_times(track: Track) -> list[Fraction]:
    return [sample.presentation for sample in track.presentation_samples]


def style_h_by_presentation(movie: Movie) -> dict[Fraction, float]:
    track = movie.track_by_role("smartstyle-info")
    primary = movie.track_by_role("primary")
    if track is None or primary is None:
        return {}
    if len(track.samples) != len(track.metadata_values):
        raise ValueError("smartstyle sample count does not match parsed values")
    by_decode = {sample.decode_index: sample.presentation for sample in primary.samples}
    found = {}
    for sample, value in zip(track.samples, track.metadata_values):
        if sample.presentation is None:
            continue
        # Metadata stts follows the primary decode timeline. Pair the value to
        # the primary frame with the same presentation time when that time
        # exists; otherwise pair by shared decode index.
        presentation = sample.presentation if sample.presentation in by_decode.values() else by_decode.get(sample.decode_index)
        stored = value.get("com.apple.quicktime.smartstyle-info", value)
        if isinstance(stored, dict) and "h" in stored and presentation is not None:
            found[presentation] = float(stored["h"])
    return found


def fraction_record(value: Fraction) -> dict:
    return {"value": value.numerator, "scale": value.denominator, "decimal": float(value)}
