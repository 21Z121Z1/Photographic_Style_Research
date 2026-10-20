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

# Declarative default edit settings from the earlier native Standard contract.
# These select an edit mode; they do not describe exposure, ISO, lens or camera.
STANDARD_EDIT_MARKER = {'0': 1, '1': 0.0, '2': 0.0, '3': 1.0, '4': 1, '5': 1,
                        '6': 4, '7': 0, '8': 1, '9': 1.0, '10': 0.0, '11': False, '12': 1}


def derived_edit_exif():
    import struct
    settings = plistlib.dumps(STANDARD_EDIT_MARKER, fmt=plistlib.FMT_BINARY, sort_keys=True)
    note = b'Apple iOS\0\0\1MM' + struct.pack('>H', 1) + struct.pack('>HHII', 84, 7, len(settings), 32) + b'\0' * 4 + settings
    software = b'XDRemux derived Texture SPI research\0'
    exif_offset = 50 + len(software) + len(software) % 2
    maker_offset = exif_offset + 18
    entry = lambda tag, kind, count, value: struct.pack('<HHII', tag, kind, count, value)
    tiff = b'II' + struct.pack('<HI', 42, 8) + struct.pack('<H', 3)
    tiff += entry(0x0112, 3, 1, 1) + entry(0x0131, 2, len(software), 50) + entry(0x8769, 4, 1, exif_offset) + b'\0' * 4
    tiff += software + b'\0' * (len(software) % 2)
    tiff += struct.pack('<H', 1) + entry(0x927c, 7, len(note), maker_offset) + b'\0' * 4 + note
    return b'\0\0\0\6Exif\0\0' + tiff


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


def attach(source: bytes, texture: dict, native_masks=(), edit_marker=False, styles=None) -> tuple[bytes, dict]:
    top, meta, children, infos, refs, payloads, primary = parse(source)
    if any(TEXTURE_URI.encode() + b'\0' in item['raw'] for item in infos):
        raise ValueError('input already contains Texture metadata')
    old_payloads = dict(payloads)
    changed_metadata = []
    if edit_marker:
        exif_ids = [item['id'] for item in infos if item.get('type') == 'Exif']
        if len(exif_ids) > 1: raise ValueError('multiple original Exif items')
        if exif_ids:
            exif_id = exif_ids[0]; changed_metadata.append(exif_id)
        else:
            exif_id = max(payloads) + 1
            raw = B.make_box('infe', b'\2\0\0\1' + exif_id.to_bytes(2, 'big') + b'\0\0Exif\0')
            infos.append({'id': exif_id, 'raw': raw})
            refs.append({'type': 'cdsc', 'from': exif_id, 'to': [primary]})
        payloads[exif_id] = derived_edit_exif()
    properties, associations = iprp(source, children)
    mask_report = []
    for uri, codec in native_masks:
        _, _, mask_children, mask_infos, mask_refs, mask_payloads, codec_primary = parse(codec)
        mask_properties, mask_associations = iprp(codec, mask_children)
        candidates = [item for item, values in mask_associations.items()
                      if any(mask_properties[index - 1][4:8] == b'auxC' for index, _ in values)]
        ordinary_resource = not candidates
        if ordinary_resource: candidates = [codec_primary]
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
            raw[9:12] = b'\0\0\1'
            infos.append({'id': mapping[old], 'raw': bytes(raw)})
            payloads[mapping[old]] = mask_payloads[old]
            if old in mask_associations:
                associations[mapping[old]] = [(index + property_base, essential) for index, essential in mask_associations[old]]
        if ordinary_resource:
            properties.append(B.make_box('auxC', b'\0\0\0\0' + uri.encode() + b'\0'))
            associations[mapping[mask_primary]].append((len(properties), True))
        for ref in mask_refs:
            if ref['from'] in selected and all(item in selected for item in ref['to']):
                refs.append({'type': ref['type'], 'from': mapping[ref['from']], 'to': [mapping[item] for item in ref['to']]})
        final_aux = mapping[mask_primary]
        if uri.endswith(':styledeltamap'):
            image_info = next(info for info in mask_infos if info['id'] == mask_primary)
            if image_info['type'] != 'hvc1': raise ValueError('neutral delta codec must produce one hvc1 tile')
            tile_associations = [(index, essential) for index, essential in associations[final_aux] if properties[index-1][4:8] != b'auxC']
            associations[final_aux] = tile_associations
            tiles = [final_aux]
            for _ in range(29):
                tile = max(payloads) + 1; raw = bytearray(image_info['raw']); raw[12:14] = tile.to_bytes(2, 'big'); raw[9:12] = b'\0\0\1'
                infos.append({'id': tile, 'raw': bytes(raw)}); payloads[tile] = mask_payloads[mask_primary]; associations[tile] = list(tile_associations); tiles.append(tile)
            grid = max(payloads) + 1
            infos.append({'id': grid, 'raw': B.make_box('infe', b'\2\0\0\1' + grid.to_bytes(2, 'big') + b'\0\0grid\0')})
            payloads[grid] = b'\0\0\4\5' + (3072).to_bytes(2, 'big') + (2560).to_bytes(2, 'big')
            properties.append(B.make_box('ispe', b'\0'*4 + (3072).to_bytes(4,'big') + (2560).to_bytes(4,'big'))); grid_ispe = len(properties)
            properties.append(B.make_box('auxC', b'\0'*4 + uri.encode() + b'\0')); grid_aux = len(properties)
            associations[grid] = [(index, essential) for index, essential in tile_associations if properties[index-1][4:8] not in [b'ispe',b'hvcC']] + [(grid_ispe,False),(grid_aux,True)]
            refs.append({'type':'dimg','from':grid,'to':tiles}); final_aux = grid
        refs.append({'type': 'auxl', 'from': final_aux, 'to': [primary]})
        # The 2026 FSINC version describes the final resource's carrier schema.
        # Its HEVC probability pixels remain the actual native codec output.
        xmp = (b'<x:xmpmeta xmlns:x="adobe:ns:meta/"><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">'
               b'<rdf:Description rdf:about="" xmlns:fsincMattes="http://ns.apple.com/fsinc/1.0/">'
               b'<fsincMattes:FSINCMatteVersion>0</fsincMattes:FSINCMatteVersion></rdf:Description></rdf:RDF></x:xmpmeta>')
        if uri.endswith(':semanticpersoninstances'):
            xmp = xmp.replace(b'</rdf:Description>', b'<fsincMattes:InstanceMaskReferenceKey>DerivedVisionInstance1</fsincMattes:InstanceMaskReferenceKey></rdf:Description>')
        mime_ids = {info['id'] for info in mask_infos if info.get('type') == 'mime'}
        if uri.startswith('tag:apple.com,2026:'):
            for old in selected & mime_ids: payloads[mapping[old]] = xmp
        mask_report.append({'uri': uri, 'image_item': final_aux, 'codec_source_sha256': hashlib.sha256(codec).hexdigest(),
                            'codec_payload_sha256': hashlib.sha256(mask_payloads[mask_primary]).hexdigest()})
    style_item = None
    if styles is not None:
        style_item = max(payloads) + 1
        infos.append({'id': style_item, 'raw': B.make_uri_infe(style_item, 'metadata', 'tag:apple.com,2023:photo:metadata:styles')})
        payloads[style_item] = styles; refs.append({'type':'cdsc','from':style_item,'to':[primary]})
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
    assert all(actual[key] == value for key, value in old_payloads.items() if key not in changed_metadata)
    assert plistlib.loads(actual[item_id]) == texture
    return result, {'schema': 'texture-carrier-assembly-v1', 'input_sha256': hashlib.sha256(source).hexdigest(),
                    'output_sha256': hashlib.sha256(result).hexdigest(), 'primary_item': primary,
                    'texture_item': item_id, 'preserved_payload_count': len(old_payloads),
                    'changed_metadata_items': changed_metadata, 'declarative_edit_marker': STANDARD_EDIT_MARKER if edit_marker else None,
                    'styles_item': style_item,
                    'image_and_auxiliary_payloads_byte_identical': True, 'native_encoded_masks': mask_report, 'texture_metadata': texture}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('directory', type=Path); args = ap.parse_args(); root = args.directory
    production = json.loads((root / 'carrier-production.json').read_text())
    if production.get('stage') != 'finished' or not all(row['native_auxiliary_readback'] for row in production['native_mask_codec_controls']):
        raise ValueError('native auxiliary writing/readback did not finish')
    stats = json.loads((root / 'mattify-type1-Studio-EV0.json').read_text())
    values = stats.get('native_output_person_stats', {})
    if not (stats.get('stage') == 'finished' or stats.get('statistics_generation_completed')) or not any(v > 0 for v in values.get('AverageFaceColor', [])):
        raise ValueError('no measured, nonzero native statistics')
    person = stats['normalized_person_with_stats']
    for path in ['undereyebrighten-type1-Studio-EV0.json', 'skinsmoothstandalone-type1-Studio-EV0.json']:
        extra = json.loads((root / path).read_text())
        if extra.get('stage') == 'finished' and 'normalized_person_with_stats' in extra:
            person.setdefault('imageStats', {}).update(extra['normalized_person_with_stats'].get('imageStats', {}))
    person['instanceMaskReferenceKey'] = 'DerivedVisionInstance1'
    texture = {'HardwareModel': 'iPhone19,2', 'PortType': 'PortTypeBack', 'CaptureMode': 'Still', 'CaptureType': 'LF',
               'Preset': 'Standard', 'TextureStylePeopleDataVersion': 3, 'FilmGrainSeed': 0,
               'TextureStylePostProcessedPeopleData': [person]}
    source = (root / 'control.heic').read_bytes()
    codecs = {row['role']: row for row in production['native_mask_codec_controls']}
    native_masks = [(row['uri'], (root / codecs[row['role']]['file']).read_bytes()) for row in production['resources']]
    if production['instance_count'] != 1: raise ValueError('instance matching must be implemented before extending this one-person control')
    native_masks.append(('tag:apple.com,2026:photo:aux:semanticpersoninstances', (root / codecs['semanticpersonmatte']['file']).read_bytes()))
    native_masks.extend([('tag:apple.com,2023:photo:aux:linearthumbnail', (root / 'linear-thumbnail-codec.heic').read_bytes()),
                         ('tag:apple.com,2023:photo:aux:styledeltamap', (root / 'neutral-delta-codec.heic').read_bytes())])
    styles = (root / 'derived-styles.bplist').read_bytes()
    for name, dictionary, marker in [('texture-candidate.heic', texture, True), ('texture-without-marker-control.heic', texture, False), ('texture-no-people-control.heic', {k:v for k,v in texture.items() if k != 'TextureStylePostProcessedPeopleData'}, True)]:
        output, report = attach(source, dictionary, native_masks, marker, styles)
        (root / name).write_bytes(output)
        (root / (name + '.assembly.json')).write_text(json.dumps(report, indent=2) + '\n')
        print(name, report['output_sha256'], len(output))


if __name__ == '__main__':
    main()
