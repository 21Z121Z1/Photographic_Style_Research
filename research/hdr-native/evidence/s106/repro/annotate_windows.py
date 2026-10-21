"""Annotate the existing LLVM text; no repeat disassembly or native run."""
from pathlib import Path
import ast
import hashlib
import importlib.util
import json
import re
import struct

C=Path(__file__).resolve().parent;R=Path('/home/Z121Z121/work/styles-gtm-ltm')
s=importlib.util.spec_from_file_location('cache',R/'iterations/20261018-v3/scripts/ios_cache_reader.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);c=m.Cache()
tree=ast.parse((C/'objc_locate.py').read_text());nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in['ptr','named','selector_from_stub']];exec(compile(ast.Module(body=nodes,type_ignores=[]),'existing-selector-decoder-only','exec'))
tree=ast.parse((C/'trace_capture.py').read_text());nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in['literal','sel']];stub_cache={};exec(compile(ast.Module(body=nodes,type_ignores=[]),'existing-literal-decoder-only','exec'))
manifest=json.loads((C/'trace-manifest.json').read_text());target=C/'annotated';target.mkdir();records=[]
for record in manifest['functions']:
    source=C/record['text_file'];assert hashlib.sha256(source.read_bytes()).hexdigest()==record['text_SHA256'];out=[];registers={};annotations=0
    for line in source.read_text().splitlines():
        match=re.match(r'\s*([0-9a-f]+):\s+(?:(?:[0-9a-f]{2}\s+){4}|[0-9a-f]{8}\s+)\s*(\S+)\s*(.*)',line)
        if not match:out.append(line);continue
        mnemonic=match[2];operands=match[3].split(';',1)[0].split(' <',1)[0].strip();notes=[];updated=False
        if mnemonic=='bl':
            t=re.search('0x([0-9a-f]+)',operands)
            if t:
                name=sel(int(t[1],16))
                if name:notes.append('SELECTOR '+name)
        if mnemonic=='adrp':
            op=re.fullmatch(r'(x\d+), #?(0x[0-9a-f]+|\d+)',operands)
            if op:registers[op[1]]=int(op[2],0);updated=True
        elif mnemonic=='add':
            op=re.fullmatch(r'(x\d+), (x\d+), #(0x[0-9a-f]+|\d+)(?:, lsl #(\d+))?',operands)
            if op and op[2]in registers:
                p=registers[op[2]]+(int(op[3],0)<<(int(op[4])if op[4]else 0));registers[op[1]]=p;updated=True;value=literal(p)
                if value:notes.append(hex(p)+' '+value)
        elif mnemonic=='ldr':
            op=re.fullmatch(r'(x\d+), \[(x\d+)(?:, #(0x[0-9a-f]+|\d+))?\]',operands)
            if op and op[2]in registers:
                p=registers[op[2]]+(int(op[3],0)if op[3]else 0)
                try:
                    v=ptr(c.u64(p))
                    if v is not None:
                        registers[op[1]]=v;updated=True;value=literal(v)
                        if value:notes.append(hex(v)+' '+value)
                except(ValueError,struct.error):pass
        if not updated:
            dest=re.match(r'(x|w)(\d+),',operands)
            if dest:registers.pop('x'+dest[2],None)
        if mnemonic=='bl':
            for i in range(19):registers.pop('x'+str(i),None)
        elif mnemonic=='b'or mnemonic.startswith('b.')or mnemonic in['cbz','cbnz','tbz','tbnz','ret','retab','br','braa','brab']:registers.clear()
        annotations+=len(notes);out.append(line+(' ; '+' | '.join(notes)if notes else''))
    path=target/source.name
    with path.open('x')as f:f.write('\n'.join(out)+'\n')
    records.append({**record,'raw_text_file':record['text_file'],'raw_text_SHA256':record['text_SHA256'],'text_file':str(path.relative_to(C)),'text_SHA256':hashlib.sha256(path.read_bytes()).hexdigest(),'annotations':annotations})
assert c.unchanged()
result={**manifest,'functions':records,'annotation_format':'LLVM18 one32-bit instruction word or4byte groups; source instruction bytes unchanged; selectors/literals are locators pending dataflow review'}
with(C/'annotated-manifest.json').open('x')as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps({'functions':len(records),'annotations':sum(r['annotations']for r in records),'cache_unchanged':True}))
