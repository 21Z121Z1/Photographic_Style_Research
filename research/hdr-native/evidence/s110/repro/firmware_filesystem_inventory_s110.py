"""Extend the cost inventory to all filesystem roles before choosing any DMG."""
from pathlib import Path
C=Path(__file__).resolve().parent
source=(C/'firmware_metadata_s110.py').read_text()
old="with(C/'firmware-metadata-s110.json').open('x')as f:json.dump(result,f,indent=2);f.write('\\n')"
new="""result['all_dmg_entries']=[e for e in entries if '.dmg' in e['name']]
result['all_filesystem_roles']=[{'DeviceClass':ident.get('Info',{}).get('DeviceClass'),'Variant':ident.get('Info',{}).get('Variant'),'components':{k:v.get('Info',{}).get('Path') for k,v in ident.get('Manifest',{}).items() if '.dmg' in v.get('Info',{}).get('Path','')}}for ident in bm['BuildIdentities']]
with(C/'firmware-filesystems-s110.json').open('x')as f:json.dump(result,f,indent=2);f.write('\\n')"""
assert source.count(old)==1
source=source.replace(old,new)
exec(compile(source,'bounded-public-manifest-filesystem-roles','exec'))
