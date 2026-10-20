#!/usr/bin/env python3
"""Attach newly generated Texture metadata to a native ImageIO carrier.

The image and auxiliary codec payloads are copied exactly. Hardware/port/capture
fields select an Apple tuning profile for this derived file; no EXIF camera,
exposure, capture date, RAW, or original-camera claims are manufactured.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import plistlib
from pathlib import Path
import bmff as B

TEXTURE_URI = 'tag:apple.com,2026:photo:metadata:texture_styles'


def parse(data):
    top = list(B.boxes(data, 0, len(data)))
    meta = next(box for box in top if box['type'] == 'meta')
    children = list(B.boxes(data, meta['data_start'] + 4, meta['data_end']))
    by_type = {box['type']: box for box in children}
    _, infos = B.parse_iinf(data, by_type['iinf'])
    _, refs = B.parse_iref(data, by_type['iref']) if 'iref' in by_type else (0, [])
    locations = B.parse_iloc(data, by_type['iloc'])
    payloads = {entry['id']: B.item_payload(data, entry, by_type.get('idat')) for entry in locations['entries']}
    pitm = by_type['pitm']; pos = pitm['data_start']
    primary = B.u(data, pos + 4, 4 if data[pos] else 2)
    return top, meta, children, infos, refs, payloads, primary


def attach(source: bytes, texture: dict) -> tuple[bytes, dict]:
    top, meta, children, infos, refs, payloads, primary = parse(source)
    if any(TEXTURE_URI.encode() + b'\0' in item['raw'] for item in infos):
        raise ValueError('input already contains Texture metadata')
    item_id = max(payloads) + 1
    metadata = plistlib.dumps(texture, fmt=plistlib.FMT_BINARY, sort_keys=True)
    old_payloads = dict(payloads)
    payloads[item_id] = metadata
    infos.append({'id': item_id, 'raw': B.make_uri_infe(item_id, 'metadata', TEXTURE_URI)})
    refs.append({'type': 'cdsc', 'from': item_id, 'to': [primary]})
    # Repack all internal extents into one mdat, preserving their exact bytes.
    order = [item_id] + sorted(old_payloads)
    locations = {'version': 1, 'flags': b'\0\0\0', 'offset_size': 4, 'length_size': 4,
                 'base_offset_size': 0, 'index_size': 0, 'item_id_size': 2}
    entries = [{'id': key, 'construction_field': 0, 'method': 0, 'data_ref': 0,
                'base_offset': 0, 'extents': [{'offset': 0, 'length': len(payloads[key])}]} for key in order]

    def make_meta():
        replacements = {'iinf': B.make_iinf(0, [item['raw'] for item in infos]),
                        'iref': B.make_iref(0, refs), 'iloc': B.make_iloc(locations, entries)}
        parts = []
        for child in children:
            kind = child['type']
            if kind == 'idat':
                continue
            parts.append(replacements.pop(kind, source[child['pos']:child['data_end']]))
        parts.extend(replacements.values())
        return B.make_box('meta', source[meta['data_start']:meta['data_start'] + 4] + b''.join(parts))

    ftyp = next(box for box in top if box['type'] == 'ftyp')
    prefix = source[ftyp['pos']:ftyp['data_end']]
    provisional = make_meta()
    offset = len(prefix) + len(provisional) + 8
    for entry in entries:
        entry['extents'][0]['offset'] = offset
        offset += len(payloads[entry['id']])
    final_meta = make_meta()
    assert len(provisional) == len(final_meta)
    result = prefix + final_meta + B.make_box('mdat', b''.join(payloads[key] for key in order))
    *_, actual, actual_primary = parse(result)
    assert actual_primary == primary
    assert all(actual[key] == value for key, value in old_payloads.items())
    assert plistlib.loads(actual[item_id]) == texture
    return result, {'schema': 'texture-carrier-assembly-v1', 'input_sha256': hashlib.sha256(source).hexdigest(),
                    'output_sha256': hashlib.sha256(result).hexdigest(), 'primary_item': primary,
                    'texture_item': item_id, 'preserved_payload_count': len(old_payloads),
                    'image_and_auxiliary_payloads_byte_identical': True, 'texture_metadata': texture}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('directory', type=Path); args = ap.parse_args(); root = args.directory
    production = json.loads((root / 'carrier-production.json').read_text())
    if production.get('stage') != 'finished' or not all(row['native_auxiliary_readback'] for row in production['readback']):
        raise ValueError('native auxiliary writing/readback did not finish')
    stats = json.loads((root / 'mattify-type1-Studio-EV0.json').read_text())
    values = stats.get('native_output_person_stats', {})
    if stats.get('stage') != 'finished' or not any(v > 0 for v in values.get('AverageFaceColor', [])):
        raise ValueError('no measured, nonzero native statistics')
    person = stats['normalized_person_with_stats']
    person['instanceMaskReferenceKey'] = 'tag:apple.com,2026:photo:aux:semanticpersonmatte'
    texture = {'HardwareModel': 'iPhone19,2', 'PortType': 'PortTypeBack', 'CaptureMode': 'Still', 'CaptureType': 'LF',
               'Preset': 'Standard', 'TextureStylePeopleDataVersion': 3, 'FilmGrainSeed': 0,
               'TextureStylePostProcessedPeopleData': [person]}
    source = (root / 'inferred-mattes.heic').read_bytes()
    for name, dictionary in [('texture-candidate.heic', texture), ('texture-no-people-control.heic', {k:v for k,v in texture.items() if k != 'TextureStylePostProcessedPeopleData'})]:
        output, report = attach(source, dictionary)
        (root / name).write_bytes(output)
        (root / (name + '.assembly.json')).write_text(json.dumps(report, indent=2) + '\n')
        print(name, report['output_sha256'], len(output))


if __name__ == '__main__':
    main()
