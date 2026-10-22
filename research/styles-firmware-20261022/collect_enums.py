"""Actual matched enum tables, dictionary pairing and unknown-path evidence."""
from __future__ import annotations
import argparse,hashlib,json,re,struct
from pathlib import Path
from dyld_bytes import CacheBytes
from collect_cast_tables import verify_cache_identity


def collect(cache_root: Path,output: Path):
    if output.exists():raise FileExistsError(output)
    root=Path(__file__).resolve().parent;cache=CacheBytes(cache_root);uuid=verify_cache_identity(cache)
    manifests=[root/'evidence/enum-24A446/manifest.json',root/'evidence/enum-number-24A446/manifest.json'];checked=[]
    for path in manifests:
        for row in json.loads(path.read_text())['methods']:
            raw,_=cache.read(int(row['first_address'],16),row['checked_bytes'])
            if hashlib.sha256(raw).hexdigest()!=row['instructions_sha256']:raise ValueError('Enum method source changed')
            checked.append({'file':str((path.parent/row['file']).relative_to(root)),'bytes':len(raw),'sha256':row['instructions_sha256']})
    text=(root/'evidence/enum-24A446/tuning-dictionary.asm.txt').read_text();regs={};stack={}
    for address,op,args in re.findall(r'^([0-9a-f]+): [0-9a-f]{8}\s+(\S+)\s*(.*)$',text,re.M):
        if not 0x1d43369c8<=int(address,16)<0x1d4336a88:continue
        args=args.split(';',1)[0].strip()
        if op=='adrp':rd,v=args.split(', ');regs[rd]=int(v,0)
        elif op=='add':rd,rn,v=args.split(', ');regs[rd]=regs[rn]+int(v.lstrip('#'),0)
        elif op=='ldr':rd,rn=re.fullmatch(r'(x\d+), \[(x\d+)\]',args).groups();regs[rd]=cache.pointer_at(regs[rn])
        elif op=='stp':
            a,b,off=re.fullmatch(r'(x\d+), (x\d+), \[sp(?:, #(0x[0-9a-f]+))?\]',args).groups();off=int(off,0)if off else 0
            stack[off]=regs[a];stack[off+8]=regs[b]
        else:raise ValueError('Unmodeled dictionary construction')
    rows=[]
    for i in range(8):
        key=stack[8*i];value=stack[0x40+8*i];cl=cache.pointer_at(value);ro=cache.pointer_at(cl+32)&~7
        if cache.text(cache.pointer_at(ro+24))!='NSConstantIntegerNumber':raise ValueError('Constant numeric class required')
        rows.append({'name':cache.cfstring(key),'value':struct.unpack('<i',cache.read(value+16,4)[0])[0],'key_address':hex(key),'number_address':hex(value)})
    numeric_offset=struct.unpack('<i',cache.read(0x1e3f27718,4)[0])[0]
    if numeric_offset!=16:raise ValueError('Getter offset mismatch')
    table,source=cache.read(0x1d44e3ce0,12);values=struct.unpack('<3I',table)
    r={'scope':__doc__,'hardware':'iPhone17,3','build':'24A446','cache_uuid':uuid,'checked_methods':checked,
       'scene':{'input_type':'uint32 semanticStyleSceneType','output_SSR_byte':32,'mapping':{str(i+1):v for i,v in enumerate(values)},'unknown_fallback':4,'table_source':source,'table_sha256':hashlib.sha256(table).hexdigest(),
                'resolved_21_reachable_from_this_resolver':False,'code21_scaling_test_is_counterfactual':True},
       'tuning':{'input_type':'exact dictionary key/string equality; case sensitive','output_SSR_byte':652,'rows':rows,'numeric_intValue_ivar_offset':numeric_offset,
                 'unknown_fallback':None,'unknown_result':'error/assertion cold path, not a default enum','reserved_invalid_value':9,'assert_condition':cache.text(0x1d44ce911),
                 'source_unknown_branch':'0x1d42f3aa8 cbz /0x1d42f3ab8 eq9 ->0x1d42f3ae4 ->cold2 0x1d4475e08; no normal return from that path'},
       'ObjC_or_assertion_executed':False,'raw_binary_uploaded':False}
    output.write_text(json.dumps(r,indent=2)+'\n');return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('cache_root',type=Path);p.add_argument('output',type=Path);a=p.parse_args();r=collect(a.cache_root,a.output)
    print(json.dumps({'scene':r['scene']['mapping'],'tuning':r['tuning']['rows'],'unknown_tuning':r['tuning']['unknown_result']}))
