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


def iprp(data, children):
    box = next(box for box in children if box['type'] == 'iprp')
    sub = list(B.boxes(data, box['data_start'], box['data_end']))
    ipco = next(box for box in sub if box['type'] == 'ipco')
    properties = [data[box['pos']:box['data_end']] for box in B.boxes(data, ipco['data_start'], ipco['data_end'])]
    ipma = next(box for box in sub if box['type'] == 'ipma'); pos = ipma['data_start']
    version, wide = data[pos], bool(B.u(data, pos + 1, 3) & 1); pos += 4
    count = B.u(data, pos, 4); pos += 4; associations = {}
    for _ in range(count):
        width = 4 if version else 2; item = B.u(data, pos, width); pos += width
        n = data[pos]; pos += 1; values = []
        for _ in range(n):
            width = 2 if wide else 1; value = B.u(data, pos, width); pos += width
            values.append((value & (0x7fff if wide else 0x7f), bool(value & (0x8000 if wide else 0x80))))
        associations[item] = values
    return properties, associations


def make_iprp(properties, associations):
    body = len(associations).to_bytes(4, 'big')
    for item, values in associations.items():
        body += item.to_bytes(2, 'big') + bytes([len(values)])
        body += b''.join((index | (0x8000 if essential else 0)).to_bytes(2, 'big') for index, essential in values)
    return B.make_box('iprp', B.make_box('ipco', b''.join(properties)) + B.make_box('ipma', b'\0\0\0\1' + body))


def attach(source: bytes, texture: dict, native_masks=()) -> tuple[bytes, dict]:
    top, meta, children, infos, refs, payloads, primary = parse(source)
    if any(TEXTURE_URI.encode() + b'\0' in item['raw'] for item in infos):
        raise ValueError('input already contains Texture metadata')
    old_payloads = dict(payloads)
    properties, associations = iprp(source, children)
    mask_report = []
    for uri, codec in native_masks:
        _, _, mask_children, mask_infos, mask_refs, mask_payloads, _ = parse(codec)
        mask_properties, mask_associations = iprp(codec, mask_children)
        candidates = [item for item, values in mask_associations.items()
                      if any(mask_properties[index - 1][4:8] == b'auxC' for index, _ in values)]
        if len(candidates) != 1:
            raise ValueError(f'expected one native encoded mask: {candidates}')
        mask_primary = candidates[0]; selected = {mask_primary}
        changed = True
        while changed:
            before = set(selected)
            for ref in mask_refs:
                if ref['type'] == 'dimg' and ref['from'] in selected: selected.update(ref['to'])
                if ref['type'] == 'cdsc' and any(item in selected for item in ref['to']): selected.add(ref['from'])
            changed = before != selected
        next_id = max(payloads) + 1
        mapping = {old: next_id + index for index, old in enumerate(sorted(selected))}
        property_base = len(properties)
        for raw in mask_properties:
            if raw[4:8] == b'auxC': raw = B.make_box('auxC', b'\0\0\0\0' + uri.encode() + b'\0')
            properties.append(raw)
        for info in mask_infos:
            old = info['id']
            if old not in selected: continue
            raw = bytearray(info['raw'])
            if raw[8] != 2: raise ValueError('native mask infe must be version 2')
            raw[12:14] = mapping[old].to_bytes(2, 'big')
            infos.append({'id': mapping[old], 'raw': bytes(raw)})
            payloads[mapping[old]] = mask_payloads[old]
            if old in mask_associations:
                associations[mapping[old]] = [(index + property_base, essential) for index, essential in mask_associations[old]]
        for ref in mask_refs:
            if ref['from'] in selected and all(item in selected for item in ref['to']):
                refs.append({'type': ref['type'], 'from': mapping[ref['from']], 'to': [mapping[item] for item in ref['to']]})
        refs.append({'type': 'auxl', 'from': mapping[mask_primary], 'to': [primary]})
        # The 2026 FSINC version describes the final resource's carrier schema.
        # Its HEVC probability pixels remain the actual native codec output.
        xmp = (b'<x:xmpmeta xmlns:x="adobe:ns:meta/"><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">'
               b'<rdf:Description rdf:about="" xmlns:fsincMattes="http://ns.apple.com/fsinc/1.0/">'
               b'<fsincMattes:FSINCMatteVersion>0</fsincMattes:FSINCMatteVersion></rdf:Description></rdf:RDF></x:xmpmeta>')
        mime_ids = {info['id'] for info in mask_infos if info.get('type') == 'mime'}
        for old in selected & mime_ids: payloads[mapping[old]] = xmp
        mask_report.append({'uri': uri, 'image_item': mapping[mask_primary], 'codec_source_sha256': hashlib.sha256(codec).hexdigest(),
                            'codec_payload_sha256': hashlib.sha256(mask_payloads[mask_primary]).hexdigest()})
    item_id = max(payloads) + 1
    metadata = plistlib.dumps(texture, fmt=plistlib.FMT_BINARY, sort_keys=True)
    payloads[item_id] = metadata
    infos.append({'id': item_id, 'raw': B.make_uri_infe(item_id, 'metadata', TEXTURE_URI)})
    refs.append({'type': 'cdsc', 'from': item_id, 'to': [primary]})
    # Repack all internal extents into one mdat, preserving their exact bytes.
    order = [item_id] + sorted(key for key in payloads if key != item_id)
    locations = {'version': 1, 'flags': b'\0\0\0', 'offset_size': 4, 'length_size': 4,
                 'base_offset_size': 0, 'index_size': 0, 'item_id_size': 2}
    entries = [{'id': key, 'construction_field': 0, 'method': 0, 'data_ref': 0,
                'base_offset': 0, 'extents': [{'offset': 0, 'length': len(payloads[key])}]} for key in order]

    def make_meta():
        replacements = {'iinf': B.make_iinf(0, [item['raw'] for item in infos]),
                        'iref': B.make_iref(0, refs), 'iloc': B.make_iloc(locations, entries),
                        'iprp': make_iprp(properties, associations)}
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
                    'image_and_auxiliary_payloads_byte_identical': True, 'native_encoded_masks': mask_report, 'texture_metadata': texture}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('directory', type=Path); args = ap.parse_args(); root = args.directory
    production = json.loads((root / 'carrier-production.json').read_text())
    if production.get('stage') != 'finished' or not all(row['native_auxiliary_readback'] for row in production['native_mask_codec_controls']):
        raise ValueError('native auxiliary writing/readback did not finish')
    stats = json.loads((root / 'mattify-type1-Studio-EV0.json').read_text())
    values = stats.get('native_output_person_stats', {})
    if stats.get('stage') != 'finished' or not any(v > 0 for v in values.get('AverageFaceColor', [])):
        raise ValueError('no measured, nonzero native statistics')
    person = stats['normalized_person_with_stats']
    for path in ['undereyebrighten-type1-Studio-EV0.json', 'skinsmoothstandalone-type1-Studio-EV0.json']:
        extra = json.loads((root / path).read_text())
        if extra.get('stage') == 'finished' and 'normalized_person_with_stats' in extra:
            person.setdefault('imageStats', {}).update(extra['normalized_person_with_stats'].get('imageStats', {}))
    person['instanceMaskReferenceKey'] = 'tag:apple.com,2026:photo:aux:semanticpersonmatte'
    texture = {'HardwareModel': 'iPhone19,2', 'PortType': 'PortTypeBack', 'CaptureMode': 'Still', 'CaptureType': 'LF',
               'Preset': 'Standard', 'TextureStylePeopleDataVersion': 3, 'FilmGrainSeed': 0,
               'TextureStylePostProcessedPeopleData': [person]}
    source = (root / 'control.heic').read_bytes()
    codecs = {row['role']: row for row in production['native_mask_codec_controls']}
    native_masks = [(row['uri'], (root / codecs[row['role']]['file']).read_bytes()) for row in production['resources']]
    for name, dictionary in [('texture-candidate.heic', texture), ('texture-no-people-control.heic', {k:v for k,v in texture.items() if k != 'TextureStylePostProcessedPeopleData'})]:
        output, report = attach(source, dictionary, native_masks)
        (root / name).write_bytes(output)
        (root / (name + '.assembly.json')).write_text(json.dumps(report, indent=2) + '\n')
        print(name, report['output_sha256'], len(output))


if __name__ == '__main__':
    main()
