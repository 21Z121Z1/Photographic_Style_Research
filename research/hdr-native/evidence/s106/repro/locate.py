"""Read-only, chunked string-pool and Mach-O header locator; no image work."""
from pathlib import Path
import importlib.util
import json
import struct

C = Path(__file__).resolve().parent
R = Path('/home/Z121Z121/work/styles-gtm-ltm')
spec = importlib.util.spec_from_file_location('readonly_cache', R / 'iterations/20261018-v3/scripts/ios_cache_reader.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
cache = module.Cache()
pool = next(q for q in cache.maps if q[0] <= 0x27f05e1f0 < q[1])
found = {}
overlap = b''
for start in range(pool[0], pool[1], 1024 * 1024):
    block = cache.read(start, min(1024 * 1024, pool[1] - start))
    raw = overlap + block
    lower = raw.lower()
    base = start - len(overlap)
    for term in [b'linearthumbnail', b'withoutfaceboost', b'faceboost']:
        position = 0
        while (position := lower.find(term, position)) >= 0:
            left = raw.rfind(b'\0', 0, position) + 1
            right = raw.find(b'\0', position)
            if right >= 0 and right - left <= 1200:
                try:
                    text = raw[left:right].decode()
                except UnicodeDecodeError:
                    text = None
                if text and all(c.isprintable() for c in text):
                    found[base + left] = text
            position += len(term)
    overlap = raw[-1200:]
main = Path('/tmp/dsc_full/dyld_shared_cache_arm64e').read_bytes()
images = []
for framework in ['CameraColorProcessing', 'CMImaging', 'CMPhoto', 'PhotoImaging', 'MediaToolbox', 'ImageIO', 'AppleJPEG']:
    term = ('/' + framework + '.framework/' + framework).encode()
    seek = 0
    while (position := main.find(term, seek)) >= 0:
        seek = position + len(term)
        left = main.rfind(b'\0', 0, position) + 1
        right = main.find(b'\0', position)
        path = main[left:right].decode()
        pattern = struct.pack('<II', left, 0)
        slot = 0
        while (slot := main.find(pattern, slot)) >= 0:
            before = slot - 24
            slot += len(pattern)
            if before < 0:
                continue
            address = struct.unpack_from('<Q', main, before)[0]
            try:
                header = cache.read(address, 32)
            except ValueError:
                continue
            if header[:4] != bytes.fromhex('cffaedfe'):
                continue
            ncmds, commands_bytes = struct.unpack_from('<II', header, 16)
            assert ncmds < 200 and commands_bytes < 100000
            commands = cache.read(address + 32, commands_bytes)
            offset = 0
            uuid = None
            sections = []
            for _ in range(ncmds):
                cmd, length = struct.unpack_from('<II', commands, offset)
                assert length >= 8 and offset + length <= len(commands)
                if cmd == 0x1b:
                    uuid = commands[offset+8:offset+24].hex()
                if cmd == 0x19:
                    count = struct.unpack_from('<I', commands, offset+64)[0]
                    for i in range(count):
                        q = offset + 72 + i*80
                        name = commands[q:q+16].split(b'\0',1)[0].decode()
                        segment = commands[q+16:q+32].split(b'\0',1)[0].decode()
                        va, size = struct.unpack_from('<QQ', commands, q+32)
                        if name in ['__text','__cstring','__objc_methname','__objc_classname','__objc_classlist']:
                            sections.append({'name': name,'segment':segment,'address':hex(va),'bytes':size})
                offset += length
            images.append({'framework':framework,'path':path,'address':hex(address),'UUID_hex':uuid,'header_validated':True,'selected_sections':sections})
assert cache.unchanged()
result = {'reference_only_build':'24A446 iPhone12,1 as supplied, not IMG2810 matching build','cache_modified':False,'pool_bytes_scanned':pool[1]-pool[0],'strings_are_locators_not_algorithm_evidence':True,'strings':[{'address':hex(a),'text':t} for a,t in sorted(found.items())],'images':images}
with (C/'locators.json').open('x') as f:
    json.dump(result,f,indent=2)
    f.write('\n')
print(json.dumps({'strings':len(found),'images':len(images),'scanned_bytes':result['pool_bytes_scanned'],'cache_unchanged':True}))
