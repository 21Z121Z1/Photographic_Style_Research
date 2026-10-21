"""Stream canonical filesystem metadata; retain matching path context only."""
from pathlib import Path
import hashlib
import json
import struct
import urllib.request
import zlib

C=Path(__file__).resolve().parent
inventory=json.loads((C/'firmware-filesystems-s110.json').read_text());URL=inventory['firmware_URL'];total=inventory['IPSW_total_bytes_NOT_downloaded']
entry=next(q for q in inventory['all_dmg_entries']if q['name'].endswith('.mtree'))
assert entry['compressed_bytes']<40*1024*1024 and entry['uncompressed_bytes']<40*1024*1024
received=0
def request(start,n):
    req=urllib.request.Request(URL,headers={'Range':f'bytes={start}-{start+n-1}'})
    r=urllib.request.urlopen(req,timeout=30)
    assert r.status==206 and r.headers['Content-Range']==f'bytes {start}-{start+n-1}/{total}'
    return r
with request(entry['local_header_offset'],30)as r:h=r.read(31);received+=len(h)
assert len(h)==30
nn,en=struct.unpack_from('<HH',h,26);start=entry['local_header_offset']+30+nn+en
decoder=zlib.decompressobj(-15)if entry['method']==8 else None;assert entry['method']in[0,8]
sha=hashlib.sha256();crc=0;uncompressed=0;overlap=b'';matches=[];magic=None
def consume(raw):
    global crc,uncompressed,overlap,magic
    if magic is None:magic=raw[:64].hex()
    sha.update(raw);crc=zlib.crc32(raw,crc);uncompressed+=len(raw);assert uncompressed<=40*1024*1024
    data=overlap+raw;base=uncompressed-len(data)
    for term in [b'SmartStyle',b'VideoProcessors',b'linearthumbnail']:
        p=0
        while True:
            p=data.lower().find(term.lower(),p)
            if p<0:break
            lo=max(0,p-300);hi=min(len(data),p+1500)
            context=data[lo:hi].decode('utf8','backslashreplace')
            if not any(q['offset']==base+p and q['term']==term.decode()for q in matches):matches.append({'offset':base+p,'term':term.decode(),'context':context})
            p+=len(term)
    overlap=data[-2048:]
with request(start,entry['compressed_bytes'])as r:
    remaining=entry['compressed_bytes']
    while remaining:
        raw=r.read(min(1024*1024,remaining));assert raw;remaining-=len(raw);received+=len(raw)
        if decoder:
            pending=raw
            while pending:
                consume(decoder.decompress(pending,2*1024*1024));pending=decoder.unconsumed_tail
        else:consume(raw)
    assert not r.read(1)
if decoder:consume(decoder.flush());assert decoder.eof
assert uncompressed==entry['uncompressed_bytes']and f'{crc&0xffffffff:08x}'==entry['CRC32']
result={'BuildVersion':'24A446','reference_device':'iPhone12,1','source_URL':URL,'source_entry':entry,'received_body_bytes':received,'uncompressed_SHA256':sha.hexdigest(),'ZIP_uncompressed_CRC32_verified':True,'uncompressed_bytes':uncompressed,'first_64_bytes_hex':magic,'matching_path_contexts':matches,'firmware_DMG_downloaded':False,'Apple_binary_uploaded':False,'note':'Canonical metadata locators only, not extracted executable, kernel formula or proof of matching IMG2810 device.'}
with(C/'canonical-paths-s110.json').open('x')as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps({'metadata_body_bytes':received,'matches':len(matches),'SHA256':sha.hexdigest(),'DMG_bytes':0}))
