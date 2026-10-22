"""Read only selected cast tables from the already verified matching cache.

Tables stay in owned private scratch. Public evidence contains only addresses,
sizes, ranges, hashes and static cast-index/startup selection, never raw tables.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import numpy as np
from dyld_bytes import CacheBytes


def verify_cache_identity(cache: CacheBytes) -> str:
    evidence=Path(__file__).resolve().parent/'evidence/systemos-cache.json'
    expected=json.loads(evidence.read_text())
    if cache.files!=expected['cache_files']:raise ValueError('Exact reference cache file UUID/size set required')
    with (cache.root/'dyld_shared_cache_arm64e').open('rb')as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
    if digest!=expected['used_instruction_cache_sha256']['dyld_shared_cache_arm64e']:raise ValueError('Reference main cache SHA mismatch')
    return expected['cache_uuid']


def collect(cache_root: Path,private: Path,output: Path) -> dict:
    repo=Path(__file__).resolve().parents[2]
    if private.resolve().is_relative_to(repo):raise ValueError('Raw cast tables must stay outside Git')
    if output.exists() or private.exists():raise FileExistsError('Output exists')
    e=Path(__file__).resolve().parent/'evidence/cache-methods-24A446';manifest=json.loads((e/'manifest.json').read_text())
    method=next(r for r in manifest['methods']if r['file']=='prior-main.asm.txt');cache=CacheBytes(cache_root);cache_uuid=verify_cache_identity(cache)
    raw,_=cache.read(int(method['first_address'],16),method['checked_bytes'])
    if hashlib.sha256(raw).hexdigest()!=method['instructions_sha256']:raise ValueError('Actual prior method bytes changed')
    rows={int(a,16):(op,args)for a,_,op,args in re.findall(r'^([0-9a-f]+): ([0-9a-f]{8})\s+(\S+)\s*(.*)$',(e/'prior-main.asm.txt').read_text(),re.M)}
    raw_jump,jump_source=cache.read(0x1d42edac0,64);jump=struct.unpack('<16i',raw_jump)
    result={'hardware':'iPhone17,3','build':'24A446','cache_uuid':cache_uuid,'framework_uuid':manifest['frameworks']['CMImaging']['uuid'],
            'prior_method_sha256':method['instructions_sha256'],'jump_table':jump_source,'selection':[],'unique_tables':{},
            'cast_name_to_index_mapping_verified':False,'monochrome_set_membership_verified':False,
            'raw_tables_uploaded':False,'iOS_library_executed':False}
    private.mkdir()
    for cast_index,delta in enumerate(jump,1):
        for startup in (False,True):
            pc=0x1d42ed6b8+delta;registers={};address=None
            for _ in range(32):
                if pc==0x1d42ed6e8:break
                if pc==0x1d42ed844:address=registers['x21'];break
                op,args=rows[pc];args=args.split(';',1)[0].strip();next_pc=pc+4
                if op=='adrp':
                    rd,val=args.split(', ');registers[rd]=int(val,0)
                elif op=='add':
                    rd,rn,val=args.split(', ');registers[rd]=registers[rn]+int(val.lstrip('#'),0)
                elif op=='b':next_pc=int(args,0)
                elif op=='tbz':
                    if args!='w21, #0, 0x1d42ed6e8':raise ValueError('Unexpected startup branch')
                    if not startup:next_pc=0x1d42ed6e8
                elif op=='cmp':
                    if args!='w21, #0':raise ValueError('Unexpected condition')
                elif op=='csel':
                    if args!='x21, x9, x8, ne':raise ValueError('Unexpected table select')
                    registers['x21']=registers['x9' if startup else 'x8']
                else:raise ValueError(f'Unmodeled selector instruction {op}')
                pc=next_pc
            else:raise ValueError('Static table selection budget')
            selected={'cast_index':cast_index,'startup':startup,'table_sha256':None}
            if address is not None:
                raw,source=cache.read(address,2400);digest=hashlib.sha256(raw).hexdigest();values=np.frombuffer(raw,dtype='<f4')
                if not np.isfinite(values).all():raise ValueError('Nonfinite actual table')
                selected.update(table_sha256=digest,address=hex(address))
                if digest not in result['unique_tables']:
                    (private/(digest+'.f32')).write_bytes(raw)
                    result['unique_tables'][digest]={**source,'shape':[5,5,2,3,4],'min':float(values.min()),'max':float(values.max())}
            result['selection'].append(selected)
    (private/'selection.json').write_text(json.dumps(result,indent=2)+'\n')
    output.write_text(json.dumps(result,indent=2)+'\n');return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('cache_root',type=Path);p.add_argument('private',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args();r=collect(a.cache_root,a.private,a.output);print(json.dumps({'selection_rows':len(r['selection']),'unique_tables':len(r['unique_tables'])}))
