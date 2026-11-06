"""Expose the original compressed LinearThumbnail as a standalone HEIF image.

The derivative contains one image and its original codec/color properties.
Compressed image bytes are copied verbatim. Originals are opened read-only.
"""
import argparse
import hashlib
import json
import plistlib
import struct
from pathlib import Path

def boxes(data, start, end):
    pos = start
    while pos < end:
        size, kind = struct.unpack_from('>I4s', data, pos); header = 8
        if size == 1: size = struct.unpack_from('>Q', data, pos + 8)[0]; header = 16
        if size == 0: size = end - pos
        if size < header or pos + size > end: raise ValueError('Invalid box extent')
        yield dict(kind=kind.decode('latin1'), start=pos, data=pos + header, end=pos + size)
        pos += size

def take(data, cursor, size):
    value = int.from_bytes(data[cursor:cursor + size], 'big') if size else 0
    return value, cursor + size

def box(kind, payload):
    return struct.pack('>I4s',len(payload)+8,kind)+payload

def run(source: Path, output: Path):
    output.mkdir(exist_ok=False)
    data = source.read_bytes()
    meta = next(b for b in boxes(data, 0, len(data)) if b['kind'] == 'meta')
    children = {b['kind']:b for b in boxes(data, meta['data'] + 4, meta['end'])}
    iprp = children['iprp']; props = {b['kind']:b for b in boxes(data, iprp['data'], iprp['end'])}
    properties = list(boxes(data, props['ipco']['data'], props['ipco']['end']))
    wanted = {i + 1 for i,p in enumerate(properties) if p['kind'] == 'auxC' and
              b'tag:apple.com,2023:photo:aux:linearthumbnail' in data[p['data']:p['end']]}
    ipma = props['ipma']; cursor = ipma['data']; version = data[cursor]; flags = int.from_bytes(data[cursor + 1:cursor + 4], 'big'); cursor += 4
    count, cursor = take(data, cursor, 4); associated = {}
    for _ in range(count):
        item, cursor = take(data, cursor, 2 if version == 0 else 4)
        n, cursor = take(data, cursor, 1); indices=[]
        for _ in range(n):
            value, cursor = take(data, cursor, 2 if flags & 1 else 1)
            indices.append(value & (0x7fff if flags & 1 else 0x7f))
        associated[item] = indices
    candidates = [item for item, indices in associated.items() if wanted.intersection(indices)]
    if len(candidates) != 1: raise ValueError(f'Expected one LinearThumbnail, got {candidates}')
    linear_id = candidates[0]
    iinf=children['iinf']; version=data[iinf['data']]; start=iinf['data'] + (6 if version == 0 else 8)
    information=[]
    for entry in boxes(data,start,iinf['end']):
        if entry['kind']!='infe':continue
        p=entry['data'];v=data[p];id_size=2 if v==2 else 4
        item=int.from_bytes(data[p+4:p+4+id_size],'big');kind=data[p+6+id_size:p+10+id_size]
        information.append((item,kind,data[p:entry['end']]))
    style_ids=[item for item,_,payload in information if b'tag:apple.com,2023:photo:metadata:styles\0' in payload]
    if len(style_ids)!=1:raise ValueError(f'Expected one style metadata item, got {style_ids}')
    iloc=children['iloc'];p=iloc['data'];v=data[p];p+=4
    off_size,len_size=data[p]>>4,data[p]&15;base_size,index_size=data[p+1]>>4,data[p+1]&15;p+=2
    n,p=take(data,p,2 if v<2 else 4);locations={}
    for _ in range(n):
        item,p=take(data,p,2 if v<2 else 4);method=0
        if v in (1,2):method,p=take(data,p,2);method&=15
        ref,p=take(data,p,2);base,p=take(data,p,base_size);extents,p=take(data,p,2);pieces=[]
        if ref:raise ValueError('External data reference unsupported')
        for _ in range(extents):
            if v in (1,2) and index_size:_,p=take(data,p,index_size)
            offset,p=take(data,p,off_size);length,p=take(data,p,len_size)
            origin=0 if method==0 else children['idat']['data'] if method==1 else None
            if origin is None:raise ValueError('Unsupported item construction method')
            begin=origin+base+offset;pieces.append(data[begin:begin+length])
        locations[item]=b''.join(pieces)
    style=locations[style_ids[0]]; parsed=plistlib.loads(style)
    (output/'styles.plist').write_bytes(style)
    pitm=children['pitm'];pos=pitm['data'];width=2 if data[pos]==0 else 4;pos+=4
    original_id=int.from_bytes(data[pos:pos+width],'big')
    # A primary image must not retain its original hidden/auxiliary role.
    # Rebuild a minimal one-image container instead of merely changing pitm.
    item_type=next(kind for item,kind,_ in information if item==linear_id)
    if item_type!=b'hvc1':raise ValueError(f'Expected a single HEVC item, got {item_type!r}')
    retained=[properties[i-1] for i in associated[linear_id] if properties[i-1]['kind'] not in ['auxC','irot','imir']]
    ipco=box(b'ipco',b''.join(data[p['start']:p['end']]for p in retained))
    ipma=box(b'ipma',bytes(4)+struct.pack('>IHB',1,1,len(retained))+bytes(range(1,len(retained)+1)))
    ftyp=next(b for b in boxes(data,0,len(data))if b['kind']=='ftyp');ftyp=data[ftyp['start']:ftyp['end']]
    hdlr=children['hdlr'];hdlr=data[hdlr['start']:hdlr['end']]
    payload=locations[linear_id]
    def container_meta(offset):
        iloc=box(b'iloc',bytes(4)+b'\x44\x00'+struct.pack('>HHHHII',1,1,0,1,offset,len(payload)))
        infe=box(b'infe',b'\x02\0\0\0'+struct.pack('>HH',1,0)+b'hvc1\0')
        return box(b'meta',bytes(4)+hdlr+box(b'pitm',bytes(4)+struct.pack('>H',1))+iloc+box(b'iinf',bytes(4)+struct.pack('>H',1)+infe)+box(b'iprp',ipco+ipma))
    initial=container_meta(0);meta=container_meta(len(ftyp)+len(initial)+8)
    patched=ftyp+meta+box(b'mdat',payload)
    derivative=output/'linear-isolated.heic';derivative.write_bytes(patched)
    dims=[]
    for idx in associated[linear_id]:
        prop=properties[idx-1]
        if prop['kind']=='ispe':dims=list(struct.unpack_from('>II',data,prop['data']+4))
    report=dict(source=str(source.resolve()),sourceSHA256=hashlib.sha256(data).hexdigest(),
                originalPrimary=original_id,linearItem=linear_id,linearDimensions=dims,
                compressedItemPayloadSHA256=hashlib.sha256(locations[linear_id]).hexdigest(),
                stylesItem=style_ids[0],metadataVersion=parsed['0'],encoding=parsed.get('i'),
                compressedPayloadBytes=len(payload),retainedProperties=[p['kind']for p in retained],
                derivative=str(derivative.resolve()),derivativeSHA256=hashlib.sha256(patched).hexdigest())
    assert patched[-len(payload):]==payload
    (output/'extract.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('output',type=Path);a=p.parse_args();run(a.source,a.output)
