"""Follow selected capture callers; retain text only, never modify source cache."""
from pathlib import Path
import ast
import bisect
import hashlib
import importlib.util
import json
import re
import struct
import subprocess
import tempfile

C=Path(__file__).resolve().parent;R=Path('/home/Z121Z121/work/styles-gtm-ltm')
s=importlib.util.spec_from_file_location('cache',R/'iterations/20261018-v3/scripts/ios_cache_reader.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);c=m.Cache()
tree=ast.parse((C/'objc_locate.py').read_text());nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in ['ptr','named','selector_from_stub']];exec(compile(ast.Module(body=nodes,type_ignores=[]),'existing-selector-decoder','exec'))
tree=ast.parse((C/'trace_capture.py').read_text());nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in ['literal','sel']];stub_cache={};exec(compile(ast.Module(body=nodes,type_ignores=[]),'existing-literal-locators','exec'))
image=next(q for q in json.loads((C/'capture-locators.json').read_text())['images']if q['framework']=='CMCapture')
base=int(image['address'],16);head=c.read(base,32);ncmds,cmdbytes=struct.unpack_from('<II',head,16);commands=c.read(base+32,cmdbytes);offset=0
for _ in range(ncmds):
    cmd,size=struct.unpack_from('<II',commands,offset)
    if cmd==0x19 and commands[offset+8:offset+24].split(b'\0',1)[0]==b'__LINKEDIT':link=struct.unpack_from('<QQQQ',commands,offset+24)
    if cmd==0x26:starts_info=struct.unpack_from('<II',commands,offset+8)
    offset+=size
data=c.read(link[0]+starts_info[0]-link[2],starts_info[1]);addresses=[];value=base;shift=0;part=0
for octet in data:
    part|=(octet&127)<<shift
    if octet&128:shift+=7;continue
    if not part:break
    value+=part;addresses.append(value);shift=part=0
methods=json.loads((C/'utility-method-locators.json').read_text())['rows']
selected=[q for q in methods if q['framework']=='CMCapture'and (
    q['selector']=='_loadAndConfigureSmartStyleBundle'or
    (q['class']in ['BWSmartStyleTargetRenderer','BWApplySmartStyleRenderer','BWLearnSmartStyleRenderer','BWSmartStyleReversibilityRenderer']and q['selector']in ['prepareForRenderingWithParameters:inputVideoFormat:inputMediaPropertiesByAttachedMediaKey:','renderUsingParameters:inputPixelBuffer:inputSampleBuffer:processedPixelBuffer:completionHandler:'])or
    q['selector'].startswith('_asynchronouslyLearnWithContainer:'))]

def annotate(raw):
    out=[];registers={}
    for line in raw.splitlines():
        match=re.match(r'\s*([0-9a-f]+):\s+[0-9a-f]{8}\s+(\S+)\s*(.*)',line)
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
                except (ValueError,struct.error):pass
        if not updated:
            dest=re.match(r'(x|w)(\d+),',operands)
            if dest:registers.pop('x'+dest[2],None)
        if mnemonic=='bl':
            for i in range(19):registers.pop('x'+str(i),None)
        elif mnemonic=='b'or mnemonic.startswith('b.')or mnemonic in ['cbz','cbnz','tbz','tbnz','ret','retab','br','braa','brab']:registers.clear()
        out.append(line+(' ; '+' | '.join(notes)if notes else''))
    return '\n'.join(out)+'\n'

outdir=C/'follow';outdir.mkdir();records=[]
for index,q in enumerate(selected):
    start=int(q['IMP'],16);i=bisect.bisect_left(addresses,start);assert addresses[i]==start;stop=addresses[i+1];size=stop-start;assert size<250000
    code=c.read(start,size)
    header=struct.pack('<IIIIIIII',0xfeedfacf,0x0100000c,0,1,1,152,0,0)
    segment=struct.pack('<II16sQQQQIIII',0x19,152,b'__TEXT',start,size,184,size,7,5,1,0)
    section=struct.pack('<16s16sQQIIIIIIII',b'__text',b'__TEXT',start,size,184,2,0,0,0x80000400,0,0,0)
    with tempfile.TemporaryDirectory(prefix='static-follow-',dir=C)as temp:
        path=Path(temp)/'function.macho';path.write_bytes(header+segment+section+code)
        raw=subprocess.check_output(['/usr/bin/llvm-objdump','--disassemble','--arch-name=arm64','--print-imm-hex',str(path)],text=True,timeout=60).replace(str(path),'temporary-function-container.macho')
    path=outdir/(str(index)+'-'+q['class']+'.asm.txt')
    text='Reference iOS27 24A446/iPhone12,1; not IMG2810 matching build.\n'+q['class']+' '+q['selector']+'\nCMCapture UUID '+image['UUID_hex']+'; exact bounds LC_FUNCTION_STARTS. Annotations are locators, not dataflow proofs.\n'+annotate(raw)
    with path.open('x')as f:f.write(text)
    records.append({**q,'start':hex(start),'end_exclusive':hex(stop),'bytes':size,'instruction_SHA256':hashlib.sha256(code).hexdigest(),'text_file':str(path.relative_to(C)),'text_SHA256':hashlib.sha256(path.read_bytes()).hexdigest()})
assert c.unchanged()
result={'reference_build':'24A446 iPhone12,1','module_UUID_hex':image['UUID_hex'],'MachO_header_SHA256':hashlib.sha256(head+commands).hexdigest(),'whole_binary_SHA256_available':False,'functions':records,'cache_unchanged':True,'no_new_native_execution':True}
with (C/'follow-manifest.json').open('x')as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps({'functions':len(records),'code_bytes':sum(q['bytes']for q in records),'cache_unchanged':True}))
