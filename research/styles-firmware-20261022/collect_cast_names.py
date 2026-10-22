"""Recover the actual initializer's key/value pairing, without executing ObjC.

Only the bounded straight-line construction of 16 dictionary keys/constant
integer objects is evaluated. Unsupported instructions fail rather than guess.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
from dyld_bytes import CacheBytes
from collect_cast_tables import verify_cache_identity


def collect(cache_root: Path,output: Path) -> dict:
    if output.exists():raise FileExistsError(output)
    cache=CacheBytes(cache_root);cache_uuid=verify_cache_identity(cache);root=Path(__file__).resolve().parent
    e=root/'evidence/cast-link-24A446';m=json.loads((e/'manifest.json').read_text());method=next(r for r in m['methods']if r['file']=='cast-index-dictionary.asm.txt')
    raw,_=cache.read(int(method['first_address'],16),method['checked_bytes'])
    if hashlib.sha256(raw).hexdigest()!=method['instructions_sha256']:raise ValueError('Original initializer changed')
    regs={};stack={};rows=[]
    for address,word,op,args in re.findall(r'^([0-9a-f]+): ([0-9a-f]{8})\s+(\S+)\s*(.*)$',(e/method['file']).read_text(),re.M):
        a=int(address,16)
        if a<0x1d4334f34:continue
        if a>=0x1d43350b4:break
        args=args.split(';',1)[0].strip()
        if op=='adrp':rd,v=args.split(', ');regs[rd]=int(v,0)
        elif op=='add':
            rd,rn,v=args.split(', ');regs[rd]=regs[rn]+int(v.lstrip('#'),0)
        elif op=='ldr':
            q=re.fullmatch(r'(x\d+), \[(x\d+)\]',args)
            if not q:raise ValueError('Unexpected initializer load')
            regs[q[1]]=cache.pointer_at(regs[q[2]])
        elif op=='stp':
            q=re.fullmatch(r'(x\d+), (x\d+), \[sp(?:, #(0x[0-9a-f]+))?\]',args)
            if not q:raise ValueError('Unexpected initializer store')
            off=int(q[3],0)if q[3]else 0;stack[off]=regs[q[1]];stack[off+8]=regs[q[2]]
        else:raise ValueError('Unmodeled straight-line initializer instruction')
    for i in range(16):
        key=stack[i*8];value=stack[0x80+i*8];name=cache.cfstring(key)
        cl=cache.pointer_at(value);ro=cache.pointer_at(cl+32)&~7;class_name=cache.text(cache.pointer_at(ro+24))
        if class_name!='NSConstantIntegerNumber' or not name:raise ValueError('Expected named constant integer value')
        number=struct.unpack('<q',cache.read(value+16,8)[0])[0]
        if number!=i+1:raise ValueError('Expected exact 1..16 constant integer payloads')
        rows.append({'name':name,'cast_index':number,'key_cfstring_address':hex(key),'number_object_address':hex(value),
                     'constant_class':class_name,'number_object_sha256':hashlib.sha256(cache.read(value,24)[0]).hexdigest()})
    mono=[]
    for pointer_slot in (0x1e1d7bd10,0x1e1d7bd18):
        mono.append(cache.cfstring(cache.pointer_at(pointer_slot)))
    if set(mono)!={'StarkBW','LongGray'}:raise ValueError('Monochrome set changed')
    g=root/'evidence/cast-number-24A446';gm=json.loads((g/'manifest.json').read_text());getter=gm['methods'][0]
    code,_=cache.read(int(getter['first_address'],16),getter['checked_bytes'])
    if hashlib.sha256(code).hexdigest()!=getter['instructions_sha256']:raise ValueError('Actual numeric getter changed')
    offset_raw,offset_source=cache.read(0x1e3f27718,4);numeric_offset=struct.unpack('<i',offset_raw)[0]
    if numeric_offset!=16:raise ValueError('Constant integer ivar offset changed')
    result={'hardware':'iPhone17,3','build':'24A446','cache_uuid':cache_uuid,'framework_uuid':m['frameworks']['CMImaging']['uuid'],
            'initializer_sha256':method['instructions_sha256'],'dictionary_call':'0x1d43350c8 dictionaryWithObjects:forKeys:count:; objects=sp+0x80, keys=sp, count=16',
            'rows':rows,'monochrome_cast_names':mono,'monochrome_set_source':'0x1d4334ec8..4edc setWithObjects:; nil terminator',
            'number_class_unsignedIntegerValue_implementation_verified':True,
            'numeric_getter':{'method_sha256':getter['instructions_sha256'],'Foundation_uuid':gm['frameworks']['Foundation']['uuid'],'actual_ivar_offset':numeric_offset,'ivar_offset_source':offset_source},
            'scope':'Exact static key/value pairing, constant integer class and unsignedIntegerValue reading the actual offset16 ivar. No initializer or iOS library execution.',
            'ObjC_initializer_executed':False,'raw_tables_uploaded':False}
    output.write_text(json.dumps(result,indent=2)+'\n');return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('cache_root',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args();r=collect(a.cache_root,a.output);print(json.dumps({'names':[(x['name'],x['cast_index'])for x in r['rows']],'monochrome':r['monochrome_cast_names']}))
