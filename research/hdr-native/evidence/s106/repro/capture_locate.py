"""Reuse header locator on four capture modules; skip the old common pool scan."""
from pathlib import Path
import ast
import importlib.util
import json
import struct

C=Path(__file__).resolve().parent;R=Path('/home/Z121Z121/work/styles-gtm-ltm')
s=importlib.util.spec_from_file_location('cache',R/'iterations/20261018-v3/scripts/ios_cache_reader.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);c=m.Cache()
tree=ast.parse((C/'locate.py').read_text())
start=next(i for i,n in enumerate(tree.body)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='main'for t in n.targets))
end=next(i for i,n in enumerate(tree.body[start:],start)if isinstance(n,ast.Assert))
nodes=tree.body[start:end]
loop=next(n for n in nodes if isinstance(n,ast.For))
loop.iter=ast.List(elts=[ast.Constant(value=n)for n in['CMCapture','CMCaptureCore','CMCaptureDevice','AVFCapture']],ctx=ast.Load())
scope={'Path':Path,'struct':struct,'cache':c}
exec(compile(ast.fix_missing_locations(ast.Module(body=nodes,type_ignores=[])),'existing-header-locator-selected-modules','exec'),scope)
images=scope['images'];rows=[];scanned=0
for image in images:
    section=next(q for q in image['selected_sections']if q['name']=='__cstring')
    address=int(section['address'],16);raw=c.read(address,section['bytes']);scanned+=len(raw);offset=0
    for text in raw.split(b'\0'):
        if any(q in text.lower()for q in[b'linearthumbnail',b'linear thumbnail',b'withoutfaceboost',b'faceboost',b'face boost']):
            rows.append({'framework':image['framework'],'address':hex(address+offset),'text':text.decode('utf8',errors='replace')})
        offset+=len(text)+1
assert c.unchanged()
result={'reference_build_only':'24A446 iPhone12,1','images':images,'strings':rows,'cstring_bytes_scanned':scanned,'cache_unchanged':True,'locators_not_algorithm_or_file_binding_proof':True}
with(C/'capture-locators.json').open('x')as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps({'modules':len(images),'cstring_bytes':scanned,'matches':len(rows),'cache_unchanged':True}))
