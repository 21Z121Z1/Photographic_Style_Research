"""Inspect only seven validated images' small __cstring sections."""
from pathlib import Path
import importlib.util
import json

C=Path(__file__).resolve().parent
R=Path('/home/Z121Z121/work/styles-gtm-ltm')
s=importlib.util.spec_from_file_location('cache',R/'iterations/20261018-v3/scripts/ios_cache_reader.py')
m=importlib.util.module_from_spec(s);s.loader.exec_module(m);c=m.Cache()
images=json.loads((C/'locators.json').read_text())['images']
rows=[];scanned=0
for image in images:
    for section in image['selected_sections']:
        if section['name']!='__cstring':continue
        address=int(section['address'],16);raw=c.read(address,section['bytes']);scanned+=len(raw);offset=0
        for b in raw.split(b'\0'):
            if any(q in b.lower()for q in [b'linearthumbnail',b'linear thumbnail',b'withoutfaceboost',b'faceboost',b'face boost']):
                text=b.decode('utf8',errors='replace');rows.append({'framework':image['framework'],'module_UUID_hex':image['UUID_hex'],'address':hex(address+offset),'text':text})
            offset+=len(b)+1
assert c.unchanged()
with (C/'cstring-locators.json').open('x')as f:json.dump({'scanned_bytes':scanned,'locators_not_algorithm_proof':True,'rows':rows,'cache_unchanged':True},f,indent=2);f.write('\n')
print(json.dumps({'scanned_bytes':scanned,'matches':len(rows),'cache_unchanged':True}))
