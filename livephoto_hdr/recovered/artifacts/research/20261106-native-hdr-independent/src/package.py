"""Replace only the main MOV track and create a new Live Photo bundle.

Original MOV bytes stay at their old offsets; its old moov becomes free.
Only a new primary track sample table and newly appended main samples are used.
The other tracks' compressed bytes and tables are retained verbatim.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import plistlib
import struct
import subprocess
import uuid
from pathlib import Path

def boxes(data: bytes):
    offset = 0
    while offset < len(data):
        if offset + 8 > len(data): raise ValueError('Truncated box header')
        size, kind = struct.unpack_from('>I4s', data, offset); header = 8
        if size == 1:
            size = struct.unpack_from('>Q', data, offset + 8)[0]; header = 16
        if size == 0: size = len(data) - offset
        if size < header or offset + size > len(data): raise ValueError('Invalid box size')
        yield kind, data[offset + header:offset + size], data[offset:offset + size], offset, header
        offset += size

def box(kind: bytes, data: bytes) -> bytes:
    return struct.pack('>I4s', len(data) + 8, kind) + data

def child(data: bytes, kind: bytes) -> bytes:
    matches = [p for t, p, _, _, _ in boxes(data) if t == kind]
    if len(matches) != 1: raise ValueError(f'Expected one {kind!r}, found {len(matches)}')
    return matches[0]

def patch(data: bytes, kind: bytes, replacement: bytes) -> bytes:
    count = 0; output = []
    for t, p, raw, _, _ in boxes(data):
        if t == kind: output.append(box(t, replacement)); count += 1
        else: output.append(raw)
    if count != 1: raise ValueError(f'Expected one replacement for {kind!r}')
    return b''.join(output)

def handler(trak: bytes) -> bytes:
    return child(child(trak, b'mdia'), b'hdlr')[8:12]

def rebase_chunks(stbl: bytes, ranges: list[tuple[int, int, int]]) -> bytes:
    result = []
    for kind, payload, raw, _, _ in boxes(stbl):
        if kind not in (b'stco', b'co64'): result.append(raw); continue
        count = struct.unpack_from('>I', payload, 4)[0]; fmt = '>I' if kind == b'stco' else '>Q'; stride = 4 if kind == b'stco' else 8
        values = []
        for i in range(count):
            old = struct.unpack_from(fmt, payload, 8 + i * stride)[0]
            match = [(begin, new) for begin, end, new in ranges if begin <= old < end]
            if len(match) != 1: raise ValueError('Chunk offset lies outside encoded mdat')
            begin, new = match[0]; values.append(new + old - begin)
        result.append(box(b'co64', payload[:4] + struct.pack('>I', count) + b''.join(struct.pack('>Q', v) for v in values)))
    return b''.join(result)

def sha(path: Path) -> str:
    with path.open('rb') as f: return hashlib.file_digest(f, 'sha256').hexdigest()

def ffprobe(path: Path, what: str) -> dict:
    command = ['ffprobe', '-v', 'error', f'-show_{what}']
    if what == 'packets': command += ['-show_data_hash', 'sha256']
    return json.loads(subprocess.check_output(command + ['-of', 'json', str(path)]))

def packet_groups(path: Path) -> dict[int, list]:
    groups = {}
    for p in ffprobe(path, 'packets')['packets']:
        groups.setdefault(p['stream_index'], []).append(tuple(p.get(k) for k in ['pts_time', 'dts_time', 'duration_time', 'size', 'data_hash']))
    return groups

def run(args):
    photo, original, video, output = args.photo.resolve(), args.original.resolve(), args.video.resolve(), args.output.resolve()
    before = {str(p): sha(p) for p in [photo, original]}
    source_bytes, encoded_bytes = original.read_bytes(), video.read_bytes()
    source_top, encoded_top = list(boxes(source_bytes)), list(boxes(encoded_bytes))
    sm = next(x for x in source_top if x[0] == b'moov'); em = next(x for x in encoded_top if x[0] == b'moov')
    source_tracks = [p for t, p, *_ in boxes(sm[1]) if t == b'trak']
    st = next(t for t in source_tracks if handler(t) == b'vide')
    et = next(p for t, p, *_ in boxes(em[1]) if t == b'trak' and handler(p) == b'vide')
    # Appending preserves every original non-primary chunk offset.
    base = bytearray(source_bytes); base[sm[3] + 4:sm[3] + 8] = b'free'
    appended = bytearray(); ranges = []
    for kind, payload, raw, offset, header in encoded_top:
        if kind == b'mdat':
            ranges.append((offset + header, offset + len(raw), len(base) + len(appended) + header)); appended.extend(raw)
    estbl = child(child(child(et, b'mdia'), b'minf'), b'stbl')
    smdia = child(st, b'mdia'); sminf = child(smdia, b'minf')
    nminf = patch(sminf, b'stbl', rebase_chunks(estbl, ranges))
    emdia = child(et, b'mdia'); nmdia = patch(patch(smdia, b'minf', nminf), b'mdhd', child(emdia, b'mdhd'))
    source_tkhd, encoded_tkhd = child(st, b'tkhd'), bytearray(child(et, b'tkhd'))
    si = 20 if source_tkhd[0] == 1 else 12; ei = 20 if encoded_tkhd[0] == 1 else 12
    encoded_tkhd[ei:ei + 4] = source_tkhd[si:si + 4]
    new_track = []
    for t, p, raw, _, _ in boxes(st):
        if t == b'tkhd': new_track.append(box(t, bytes(encoded_tkhd)))
        elif t == b'mdia': new_track.append(box(t, nmdia))
        elif t == b'edts':
            candidate = [raw for kind, _, raw, _, _ in boxes(et) if kind == b'edts']
            new_track.extend(candidate)
        elif t == b'tapt': continue
        else: new_track.append(raw)
    ntrak = b''.join(new_track)
    nmoov = b''.join(box(t, ntrak) if t == b'trak' and p == st else raw for t, p, raw, _, _ in boxes(sm[1]))
    paired = bytes(base + appended) + box(b'moov', nmoov)
    ids = json.loads(subprocess.check_output(['exiftool', '-j', '-ContentIdentifier', str(photo), str(original)]))
    old = ids[0]['ContentIdentifier']; assert ids[1]['ContentIdentifier'] == old
    new = str(uuid.uuid4()).upper(); old_bytes, new_bytes = old.encode(), new.encode()
    pb = photo.read_bytes(); assert pb.count(old_bytes) == 1 and paired.count(old_bytes) == 2
    output.mkdir(exist_ok=False)
    pp, vp = output / f'{photo.stem}_dynamic.heic', output / f'{photo.stem}_dynamic.mov'
    pp.write_bytes(pb.replace(old_bytes, new_bytes)); vp.write_bytes(paired.replace(old_bytes, new_bytes))
    (output / 'metadata.plist').write_bytes(plistlib.dumps({'PFVideoComplementMetadataVersionKey': '1'}, fmt=plistlib.FMT_BINARY))
    a, b = packet_groups(original), packet_groups(vp)
    tracks = [dict(stream=i, sourcePackets=len(a.get(i, [])), identical=a.get(i) == b.get(i)) for i in a if i != 0]
    source_pts = sorted(p[0] for p in a[0]); final_pts = sorted(p[0] for p in b[0]); assert source_pts == final_pts
    streams = ffprobe(vp, 'streams')['streams']; main = streams[0]
    assert len(streams) == len(source_tracks) and all(t['identical'] for t in tracks)
    assert main['profile'] == 'Main 10' and main['color_transfer'] == 'arib-std-b67'
    assert {str(p): sha(p) for p in [photo, original]} == before
    assert pp.read_bytes().replace(new_bytes, old_bytes) == pb
    report = dict(schema='independent-live-photo-package-v1', package=str(output), uuid=new,
                  sources=before, outputSHA256={p.name:sha(p) for p in output.iterdir()},
                  photoOnlyUUIDChanged=True, mainPTSMatch=True, preservedTracks=tracks,
                  streams=len(streams), main={k: main.get(k) for k in ['codec_name', 'profile', 'width', 'height', 'pix_fmt', 'color_primaries', 'color_transfer', 'color_space', 'duration', 'nb_frames']},
                  claims='Local packet, timing, color-signaling and pairing checks only; Photos editing behavior requires separate acceptance.')
    args.report.write_text(json.dumps(report, indent=2) + '\n'); print(json.dumps(report, indent=2))

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['photo', 'original', 'video', 'output', 'report']: p.add_argument(name, type=Path)
    run(p.parse_args())
