"""Narrow static disassembly of actual capture producer/encoder entry points.

No Apple code execution, image processing, binary download or binary upload.
Small synthetic Mach-O containers exist only as owned temporary files, then
are deleted. Retain text, hashes and header UUIDs only.
"""
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
cache=c
tree=ast.parse((C/'objc_locate.py').read_text())
nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in['ptr','named','selector_from_stub']]
exec(compile(ast.Module(body=nodes,type_ignores=[]),'existing-calibrated-selector-decoder-only','exec'))
image=next(q for q in json.loads((C/'capture-locators.json').read_text())['images']if q['framework']=='CMCapture')
base=int(image['address'],16);head=c.read(base,32);ncmds,cmdbytes=struct.unpack_from('<II',head,16);commands=c.read(base+32,cmdbytes);offset=0;link=None;starts_info=None
for _ in range(ncmds):
    cmd,size=struct.unpack_from('<II',commands,offset)
    if cmd==0x19:
        name=commands[offset+8:offset+24].split(b'\0',1)[0]
        if name==b'__LINKEDIT':link=struct.unpack_from('<QQQQ',commands,offset+24)
    if cmd==0x26:starts_info=struct.unpack_from('<II',commands,offset+8)
    offset+=size
assert link and starts_info and 0<starts_info[1]<1000000
data=c.read(link[0]+starts_info[0]-link[2],starts_info[1]);addresses=[];value=base;shift=0;part=0
for octet in data:
    part|=(octet&127)<<shift
    if octet&128:shift+=7;assert shift<64;continue
    if part==0:break
    value+=part;addresses.append(value);shift=0;part=0
assert addresses==sorted(set(addresses))
methods=json.loads((C/'capture-objc-locators.json').read_text())['rows']
selectors=['_asynchronouslyRenderSampleBuffer:outputLinearThumbnailSampleBuffer:outputUnstyledThumbnailSampleBuffer:outputWeightSegmentMapSampleBuffer:synchronizingEvent:','_createSmartStyleContainerFromSampleBuffer:unstyledThumbnailSampleBuffer:linearThumbnailSampleBuffer:weightSegmentMapSampleBuffer:to:','_addSmartStyleLinearThumbnailForEncodingScheme:sampleBuffer:primaryOutputAspectRatio:','_getContainerAssetsFromSampleBuffer:outputUnstyledThumbnailSampleBuffer:outputLinearThumbnailSampleBuffer:outputWeightSegmentMapSampleBuffer:','_setupGlowForPersonMask:metadataDict:linearThumbnail:linearThumbnailMetadata:intensity:effectsToRender:statistics:']
result=[];stub_cache={}

def sel(target):
    if target not in stub_cache:
        try:
            _,name=selector_from_stub(target)
            stub_cache[target]=name if re.fullmatch('[A-Za-z_][A-Za-z0-9_:]*',name)else None
        except (ValueError,struct.error):stub_cache[target]=None
    return stub_cache[target]

def literal(address):
    try:
        v=c.cfstring(address)
        if v:return 'CFString '+repr(v)
        v=c.text(address)
        if v and len(v)>3 and re.fullmatch(r'[A-Za-z_][A-Za-z0-9_ :./+<>-]*',v):return 'cstring '+repr(v)
    except(ValueError,struct.error):pass
    return None

def annotate(text):
    out=[];registers={}
    for line in text.splitlines():
        match=re.match(r'\s*([0-9a-f]+):\s+(?:[0-9a-f]{2}\s+){4}\s*(\S+)\s*(.*)',line)
        if not match:out.append(line);continue
        address=int(match[1],16);mnemonic=match[2];operands=match[3].split(';',1)[0].strip();notes=[];updated=False
        if mnemonic=='bl':
            target=re.search('0x([0-9a-f]+)',operands)
            if target:
                name=sel(int(target[1],16))
                if name:notes.append('SELECTOR '+name)
        if mnemonic=='adrp':
            op=re.fullmatch(r'(x\d+), #(0x[0-9a-f]+|\d+)',operands)
            if op:registers[op[1]]=int(op[2],0);updated=True
        elif mnemonic=='add':
            op=re.fullmatch(r'(x\d+), (x\d+), #(0x[0-9a-f]+|\d+)(?:, lsl #(\d+))?',operands)
            if op and op[2]in registers:
                p=registers[op[2]]+(int(op[3],0)<<(int(op[4])if op[4]else 0));registers[op[1]]=p;updated=True
                value=literal(p)
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
            dest=re.match('(x|w)(\d+),',operands)
            if dest:registers.pop('x'+dest[2],None)
        if mnemonic=='bl':
            for i in range(19):registers.pop('x'+str(i),None)
        elif mnemonic=='b'or mnemonic.startswith('b.')or mnemonic in['cbz','cbnz','tbz','tbnz','ret','retab','br','braa','brab']:
            registers.clear()
        out.append(line+(' ; '+ ' | '.join(notes)if notes else''))
    return '\n'.join(out)+'\n'

outdir=C/'trace';outdir.mkdir()
for index,selector in enumerate(selectors):
    method=next(q for q in methods if q['selector']==selector);start=int(method['IMP'],16);i=bisect.bisect_left(addresses,start);assert addresses[i]==start;stop=addresses[i+1];size=stop-start;assert 0<size<250000
    code=c.read(start,size)
    # MH_OBJECT / one executable __text section, with original VM addresses.
    header=struct.pack('<IIIIIIII',0xfeedfacf,0x0100000c,0,1,1,152,0,0)
    segment=struct.pack('<II16sQQQQIIII',0x19,152,b'__TEXT',start,size,184,size,7,5,1,0)
    section=struct.pack('<16s16sQQIIIIIIII',b'__text',b'__TEXT',start,size,184,2,0,0,0x80000400,0,0,0)
    assert len(header+segment+section)==184
    with tempfile.TemporaryDirectory(prefix='styles-static-s106-',dir=C)as temp:
        binary=Path(temp)/'window.macho';binary.write_bytes(header+segment+section+code)
        process=subprocess.run(['/usr/bin/llvm-objdump','--disassemble','--arch-name=arm64','--print-imm-hex',str(binary)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True,timeout=60)
        # Disassembler first filename is temporary; record its role, not a path
        # which disappears. The complete function instruction bytes are hashed.
        raw=process.stdout.decode().replace(str(binary),'temporary-function-container.macho')
    file=outdir/(str(index)+'-'+method['class']+'.asm.txt')
    text='Reference iOS27 24A446/iPhone12,1; not IMG2810 matching build.\n'+method['class']+' '+selector+'\nCMCapture UUID '+image['UUID_hex']+'\nFunction bounds from cached LC_FUNCTION_STARTS. All instruction bytes read directly from unchanged cache. Selector/literal annotations are static locators; inspect dataflow before drawing algorithm conclusions.\n'+annotate(raw)
    with file.open('x')as f:f.write(text)
    result.append({'class':method['class'],'selector':selector,'start':hex(start),'end_exclusive':hex(stop),'bytes':size,'instruction_SHA256':hashlib.sha256(code).hexdigest(),'text_file':str(file.relative_to(C)),'text_SHA256':hashlib.sha256(file.read_bytes()).hexdigest(),'complete_function_bounds_from_LC_FUNCTION_STARTS':True})
assert c.unchanged()
manifest={'reference_build':'24A446 iPhone12,1 supplied cache','module':'CMCapture','module_UUID_hex':image['UUID_hex'],'MachO_header_SHA256':hashlib.sha256(head+commands).hexdigest(),'whole_extracted_binary_SHA256_available':False,'reason':'No new whole Mach-O extracted or uploaded; source is existing cache, selected code/header hashes supplied','functions':result,'cache_unchanged':True,'new_images_or_native_execution':False,'llvm_version':subprocess.check_output(['/usr/bin/llvm-objdump','--version'],text=True).splitlines()[0]}
with(C/'trace-manifest.json').open('x')as f:json.dump(manifest,f,indent=2);f.write('\n')
print(json.dumps({'functions_traced':len(result),'bytes_disassembled':sum(r['bytes']for r in result),'cache_unchanged':True,'whole_binary_uploaded':False}))
