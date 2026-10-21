"""Resolve class/category methods for the real thumbnail producer receivers.

Read-only reference iOS cache. Narrow metadata only; no photos or native code.
"""
from pathlib import Path
import ast
import importlib.util
import json
import re
import struct

C=Path(__file__).resolve().parent
R=Path('/home/Z121Z121/work/styles-gtm-ltm')
s=importlib.util.spec_from_file_location('cache',R/'iterations/20261018-v3/scripts/ios_cache_reader.py')
m=importlib.util.module_from_spec(s);s.loader.exec_module(m);c=m.Cache()
tree=ast.parse((C/'objc_locate.py').read_text())
nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in ['ptr','named','entries','method_lists']]
exec(compile(ast.Module(body=nodes,type_ignores=[]),'readonly-existing-method-parser','exec'))
base=json.loads((C/'objc-locators.json').read_text())['calibrations'][0]['shared_selector_base']
images=json.loads((C/'locators.json').read_text())['images']+json.loads((C/'capture-locators.json').read_text())['images']
rows=[];unknown=[];counts={};all_classes=[]

def class_name(cl):
    if not cl:return None
    ro=ptr(c.u64(cl+32)&~7)
    return named(ptr(c.u64(ro+24))) if ro else None

def methods(raw,owner,role,category=None):
    for q in entries(raw):
        name=named(q['absolute_name'])if'absolute_name'in q else named(base+q['relative_name'])if q['flags']&0x40000000 else named(ptr(c.u64(q['entry']+q['relative_name'])))
        if not name:continue
        selected=('SmartStyle'in owner or'linearThumbnail'in name or'LinearThumbnail'in name or'UnstyledThumbnail'in name or'WithoutFaceBoost'in name)
        if selected:
            rows.append({'framework':image['framework'],'class':owner,'role':role,'category':category,'selector':name,'IMP':hex(q['IMP'])if q['IMP']else None,'method_entry':hex(q['entry'])})

for image in images:
    address=int(image['address'],16);header=c.read(address,32);n,sz=struct.unpack_from('<II',header,16)
    commands=c.read(address+32,sz);pos=0;sections={}
    for _ in range(n):
        cmd,size=struct.unpack_from('<II',commands,pos)
        if cmd==0x19:
            for k in range(struct.unpack_from('<I',commands,pos+64)[0]):
                a=pos+72+80*k;name=commands[a:a+16].split(b'\0',1)[0].decode();va,z=struct.unpack_from('<QQ',commands,a+32)
                if name in ['__objc_classlist','__objc_catlist','__objc_nlcatlist']:sections[name]=(va,z)
        pos+=size
    counts[image['framework']]={}
    for section,(va,size) in sections.items():
        counts[image['framework']][section]=size//8
        for k in range(0,size,8):
            obj=ptr(c.u64(va+k))
            try:
                if section=='__objc_classlist':
                    owner=class_name(obj)
                    if owner:all_classes.append({'class':owner,'framework':image['framework'],'address':hex(obj)})
                    for role,cl in [('instance',obj),('class',ptr(c.u64(obj)))]:
                        ro=ptr(c.u64(cl+32)&~7);methods(c.u64(ro+32),owner,role)
                else:
                    category=named(ptr(c.u64(obj)));owner=class_name(ptr(c.u64(obj+8)))
                    if owner:
                        methods(c.u64(obj+16),owner,'instance',category)
                        methods(c.u64(obj+24),owner,'class',category)
            except (ValueError,TypeError,AssertionError,struct.error) as e:
                unknown.append({'framework':image['framework'],'section':section,'address':hex(obj)if obj else None,'error':type(e).__name__})
assert c.unchanged()
out={'build':'24A446 iPhone12,1 reference only','selector_base':base,'section_counts':counts,'unknown':unknown,'rows':rows,'selected_class_addresses':[q for q in all_classes if 'SmartStyle'in q['class']],'cache_unchanged':True}
with (C/'utility-method-locators.json').open('x') as f:json.dump(out,f,indent=2);f.write('\n')
print(json.dumps({'method_locators':len(rows),'category_sections':sum('catlist'in key for val in counts.values()for key in val),'unknown':len(unknown),'thumbnail_producers':[q for q in rows if 'createLinearThumbnail' in q['selector']]}))
