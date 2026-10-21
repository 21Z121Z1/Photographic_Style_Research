"""Bounded public Apple ZIP/manifest metadata only; never download any DMG."""
from pathlib import Path
import hashlib
import json
import plistlib
import struct
import urllib.request
import zlib

C=Path(__file__).resolve().parent
URL='https://updates.cdn-apple.com/2026FallFCS/0ff99efa-0099-463a-85d0-8d0c83b3a7a1/iPhone12,1_27.0.1_24A446_Restore.ipsw'
TARGET='043-69708-712.dmg.aea'
received=0
with urllib.request.urlopen(urllib.request.Request(URL,method='HEAD'),timeout=30)as r:size=int(r.headers['Content-Length'])

def part(start,n):
    global received
    assert 0<n<=4*1024*1024 and 0<=start and start+n<=size
    req=urllib.request.Request(URL,headers={'Range':f'bytes={start}-{start+n-1}'})
    with urllib.request.urlopen(req,timeout=30)as r:
        assert r.status==206 and r.headers.get('Content-Range')==f'bytes {start}-{start+n-1}/{size}', 'Range response required; no full-file fallback'
        raw=r.read(n+1);assert len(raw)==n;received+=len(raw);return raw

tail=part(size-65557,65557);i=tail.rfind(b'PK\x05\x06');assert i>=0
_,_,_,_,count,cd_size,cd_off,_=struct.unpack('<IHHHHIIH',tail[i:i+22])
if cd_off==0xffffffff or cd_size==0xffffffff or count==65535:
    j=tail.rfind(b'PK\x06\x06');assert j>=0
    count,cd_size,cd_off=struct.unpack_from('<QQQ',tail,j+32)
cd=part(cd_off,cd_size);entries=[];p=0
while p<len(cd):
    assert cd[p:p+4]==b'PK\x01\x02'
    method=struct.unpack_from('<H',cd,p+10)[0];crc,comp,uncomp=struct.unpack_from('<III',cd,p+16);nn,en,cn=struct.unpack_from('<HHH',cd,p+28);off=struct.unpack_from('<I',cd,p+42)[0];name=cd[p+46:p+46+nn].decode();extra=cd[p+46+nn:p+46+nn+en]
    q=0
    while q<len(extra):
        tag,n=struct.unpack_from('<HH',extra,q);v=extra[q+4:q+4+n]
        if tag==1:
            k=0
            if uncomp==0xffffffff:uncomp=struct.unpack_from('<Q',v,k)[0];k+=8
            if comp==0xffffffff:comp=struct.unpack_from('<Q',v,k)[0];k+=8
            if off==0xffffffff:off=struct.unpack_from('<Q',v,k)[0]
        q+=4+n
    entries.append({'name':name,'method':method,'CRC32':f'{crc:08x}','compressed_bytes':comp,'uncompressed_bytes':uncomp,'local_header_offset':off});p+=46+nn+en+cn
assert len(entries)==count
manifest=next(e for e in entries if e['name']=='BuildManifest.plist');target=next(e for e in entries if e['name']==TARGET)
h=part(manifest['local_header_offset'],30);nn,en=struct.unpack_from('<HH',h,26);blob=part(manifest['local_header_offset']+30+nn+en,manifest['compressed_bytes'])
if manifest['method']==8:
    d=zlib.decompressobj(-15);raw=d.decompress(blob,32*1024*1024);assert d.eof and not d.unconsumed_tail
else:assert manifest['method']==0;raw=blob
assert len(raw)==manifest['uncompressed_bytes']and f'{zlib.crc32(raw)&0xffffffff:08x}'==manifest['CRC32']
bm=plistlib.loads(raw);assert bm['ProductBuildVersion']=='24A446'and'iPhone12,1'in bm['SupportedProductTypes']
identities=[]
for ident in bm['BuildIdentities']:
    selected={k:v.get('Info',{}).get('Path')for k,v in ident.get('Manifest',{}).items()if v.get('Info',{}).get('Path')==TARGET}
    if selected:identities.append({'DeviceClass':ident.get('Info',{}).get('DeviceClass'),'Variant':ident.get('Info',{}).get('Variant'),'manifest_components':selected})
assert identities
result={'firmware_URL':URL,'IPSW_total_bytes_NOT_downloaded':size,'BuildVersion':bm['ProductBuildVersion'],'ProductVersion':bm['ProductVersion'],'SupportedProductTypes':bm['SupportedProductTypes'],'BuildManifest_SHA256':hashlib.sha256(raw).hexdigest(),'central_directory_SHA256':hashlib.sha256(cd).hexdigest(),'metadata_received_body_bytes':received,'partial_SystemOS_entry':target,'matching_build_identities':identities,'downloaded_DMG_bytes':0,'new_large_download_location':'macOS runner only if pursued; never HK or Japan/HK backhaul','plugin_presence_inside_image_not_yet_verified':True,'schema':'Metadata cost estimate, not Apple plugin code or IMG2810 production proof'}
with(C/'firmware-metadata-s110.json').open('x')as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps({k:result[k]for k in ['BuildVersion','metadata_received_body_bytes','partial_SystemOS_entry','downloaded_DMG_bytes']}))
