"""Project encoded masks from the final HEIC into standalone decoder inputs.

The selected HEVC payloads and codec properties are copied exactly. No raw
pre-encoding masks enter this final-file replay.
"""
import copy
import hashlib
import json
from pathlib import Path
import sys
import bmff as B
from pack_carrier import parse, iprp, make_iprp


def project(source, uri, reference_key=None):
    top, meta, children, infos, refs, payloads, _ = parse(source)
    properties, associations = iprp(source, children)
    matching = [item for item, values in associations.items() if any(properties[index-1][4:8] == b'auxC' and uri.encode() + b'\0' in properties[index-1] for index, _ in values)]
    if reference_key is not None:
        marker = ('<fsincMattes:InstanceMaskReferenceKey>' + reference_key + '</fsincMattes:InstanceMaskReferenceKey>').encode()
        matching = [item for item in matching if any(ref['type']=='cdsc' and item in ref['to'] and marker in payloads[ref['from']] for ref in refs)]
    if len(matching) != 1: raise ValueError('missing or ambiguous final mask ' + uri)
    primary = matching[0]; selected = {primary}
    while True:
        before = set(selected)
        for ref in refs:
            if ref['type'] == 'dimg' and ref['from'] in selected: selected.update(ref['to'])
        if before == selected: break
    chosen_infos = []
    for info in infos:
        if info['id'] not in selected: continue
        raw = bytearray(info['raw']); raw[9:12] = b'\0\0\0' if info['id'] == primary else b'\0\0\1'; chosen_infos.append(bytes(raw))
    chosen_associations = {item: [(index, flag) for index, flag in values if properties[index-1][4:8] != b'auxC'] for item, values in associations.items() if item in selected}
    chosen_refs = [ref for ref in refs if ref['type'] == 'dimg' and ref['from'] in selected]
    iloc = {'version':1,'flags':b'\0'*3,'offset_size':4,'length_size':4,'base_offset_size':0,'index_size':0,'item_id_size':2}
    entries = [{'id':item,'construction_field':0,'method':0,'data_ref':0,'base_offset':0,'extents':[{'offset':0,'length':len(payloads[item])}]} for item in sorted(selected)]
    def metadata():
        parts = []
        for child in children:
            if child['type'] in ['hdlr','dinf']: parts.append(source[child['pos']:child['data_end']])
        parts += [B.make_box('pitm', b'\0'*4 + primary.to_bytes(2,'big')), B.make_iinf(0,chosen_infos), B.make_iref(0,chosen_refs), make_iprp(properties,chosen_associations), B.make_iloc(iloc,entries)]
        return B.make_box('meta', b'\0'*4 + b''.join(parts))
    ftyp = next(box for box in top if box['type']=='ftyp'); prefix = source[ftyp['pos']:ftyp['data_end']]
    first = metadata(); offset = len(prefix) + len(first) + 8
    for entry in entries: entry['extents'][0]['offset'] = offset; offset += entry['extents'][0]['length']
    result = prefix + metadata() + B.make_box('mdat', b''.join(payloads[entry['id']] for entry in entries))
    *_, actual, actual_primary = parse(result)
    assert actual_primary == primary and all(actual[item] == payloads[item] for item in selected)
    return result, {'uri':uri,'encoded_payloads_preserved':True,'projection_sha256':hashlib.sha256(result).hexdigest()}


def main(root):
    source = (root/'texture-candidate.heic').read_bytes()
    admission = json.loads((root/'texture-candidate.heic.admission.json').read_text())
    people = admission.get('native_person_data_readback', [])
    production = json.loads((root/'carrier-production.json').read_text())
    if 'people' in production:
        by_key = {p['instanceMaskReferenceKey']:p for p in people}
        people = [by_key[p['instance_reference_key']] for p in production['people']]
    width, height = admission['decoded_width'], admission['decoded_height']
    for index, native in enumerate(people):
        person = copy.deepcopy(native)
        for key in ['faceROI','faceSkinROI','instanceROI']:
            for name, scale in [('x',width),('width',width),('y',height),('height',height)]: person[key][name] *= scale
        for landmark in person['faceLandmarks']: landmark['point']['x'] *= width; landmark['point']['y'] *= height
        person.pop('faceROIAndLandmarksROIRelativeScalingROI',None)
        (root/('stored-person-'+str(index)+'-pixels.json')).write_text(json.dumps(person,indent=2)+'\n')
        if index == 0: (root/'stored-person-pixels.json').write_text(json.dumps(person,indent=2)+'\n')
    reports = []
    roles = {'skin':'semanticskinmattev2','face':'semanticfaceskinmatte','instance':'semanticpersoninstances' if people else 'semanticpersonmatte','person':'semanticpersonmatte','hair':'semantichairmatte','glasses':'semanticglassesmattev2','teeth':'semanticteethmattev2','nose':'semanticnosematte','lips':'semanticlipsmatte','eyebrows':'semanticeyebrowsmatte','body':'semanticnonfaceskinmatte','hands':'semantichandsmatte','ears':'semanticearsmatte','tattoo':'semantictattoomatte'}
    for name,role in roles.items():
        uri = 'urn:com:apple:photo:2019:aux:semantichairmatte' if name=='hair' else 'tag:apple.com,2026:photo:aux:'+role
        output,report=project(source,uri, people[0]['instanceMaskReferenceKey'] if name=='instance' and people else None)
        report['role']=name
        (root/('stored-'+name+'.heic')).write_bytes(output);reports.append(report)
    for index, person in enumerate(people):
        name='instance-'+str(index)
        output,report=project(source,'tag:apple.com,2026:photo:aux:semanticpersoninstances',person['instanceMaskReferenceKey'])
        report['role']=name
        (root/('stored-'+name+'.heic')).write_bytes(output);reports.append(report)
    (root/'final-mask-projections.json').write_text(json.dumps({'final_carrier_sha256':hashlib.sha256(source).hexdigest(),'resources':reports},indent=2)+'\n')


if __name__=='__main__':main(Path(sys.argv[1]))
