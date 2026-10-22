"""Read unslid instruction bytes from an owned, read-only dyld cache set.

MappingInfo is read directly from each cache header, not inferred from a name
or disassembler. Slide-v5 pointers are decoded only at confirmed chain slots;
no PAC authentication, signing, in-memory rebasing or library execution occurs.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
import re
import struct
import uuid


@dataclass(frozen=True)
class Mapping:
    path: Path
    uuid: str
    address: int
    size: int
    file_offset: int


class CacheBytes:
    def __init__(self, root: Path):
        if root.is_symlink():raise ValueError('Cache root must not be a symlink')
        self.root=root;self.mappings=[];self.files=[];self.slide_maps=[]
        for path in sorted(root.glob('dyld_shared_cache_arm64e*')):
            if path.is_symlink() or not path.is_file():continue
            with path.open('rb') as f:
                header=f.read(512)
                if len(header)<112 or not header.startswith(b'dyld_v'):continue
                offset,count=struct.unpack_from('<II',header,16)
                size=path.stat().st_size
                if count>256 or offset+32*count>size:raise ValueError('Cache mapping table bounds')
                uid=str(uuid.UUID(bytes=header[88:104])).upper()
                f.seek(offset);raw=f.read(32*count)
                for i in range(count):
                    addr,n,off,_,_=struct.unpack_from('<QQQII',raw,32*i)
                    if off+n>size:raise ValueError('Cache mapping file span')
                    self.mappings.append(Mapping(path,uid,addr,n,off))
                self.files.append({'name':path.name,'uuid':uid,'bytes':size,'mapping_count':count})
                if len(header)>=320 and offset>=320:
                    so,sn=struct.unpack_from('<II',header,312)
                    if sn>256 or so+56*sn>size:raise ValueError('Slide mapping table bounds')
                    f.seek(so);table=f.read(56*sn)
                    for i in range(sn):
                        addr,n,fo,info,infosize,_,_,_=struct.unpack_from('<6Q2I',table,56*i)
                        if not infosize:continue
                        if info+infosize>size:raise ValueError('Slide info bounds')
                        f.seek(info);head=f.read(24)
                        version,page_size,pages=struct.unpack_from('<III',head)
                        if version!=5:raise ValueError('Only observed slide-v5 supported')
                        if page_size not in (4096,16384) or 24+pages*2>infosize or pages>(n+page_size-1)//page_size:
                            raise ValueError('Slide-v5 page table bounds')
                        starts=struct.unpack('<'+'H'*pages,f.read(pages*2))
                        base=struct.unpack_from('<Q',head,16)[0]
                        self.slide_maps.append((addr,n,page_size,base,starts))
        if not self.mappings:raise ValueError('No cache mappings')
        self._chain_slots={}

    def u64(self,address: int) -> int:
        return struct.unpack('<Q',self.read(address,8)[0])[0]

    def pointer_at(self,address: int) -> int | None:
        """Unslid target only. Verify the source is an actual v5 chain member.

        Layout source: Apple dyld_cache_format.h slide_info5 and SDK
        mach-o/fixup-chains.h arm64e_shared_cache_rebase (34-bit offset).
        Do not decode arbitrary integers by masking them into the cache range.
        """
        raw=self.u64(address)
        for start,size,page_size,base,starts in self.slide_maps:
            if not start<=address<start+size:continue
            page=(address-start)//page_size
            if page>=len(starts):raise ValueError('Pointer outside slide pages')
            key=(start,page)
            if key not in self._chain_slots:
                # Apple fixupDataPages v5: initial page offset is bytes;
                # subsequent `next` fields have an eight-byte stride.
                slots=set();head=starts[page];at=start+page*page_size+head
                if head!=0xffff:
                    if head%8:raise ValueError('Unaligned slide chain head')
                    for _ in range(page_size//8):
                        if not start+page*page_size<=at<min(start+(page+1)*page_size,start+size):raise ValueError('Slide chain escaped page')
                        slots.add(at);word=self.u64(at);delta=(word>>52)&0x7ff
                        if not delta:break
                        at+=delta*8
                    else:raise ValueError('Slide chain budget')
                self._chain_slots[key]=slots
            if address in self._chain_slots[key]:
                target=base+(raw&((1<<34)-1))
                if not raw>>63:target|=((raw>>34)&255)<<56
                return target
        if raw==0:return None
        if any(m.address<=raw<m.address+m.size for m in self.mappings):return raw
        raise ValueError('Not a confirmed chain slot or mapped raw pointer')

    def text(self,address: int | None) -> str | None:
        if address is None:return None
        try:
            mapping=next(m for m in self.mappings if m.address<=address<m.address+m.size)
            raw=self.read(address,min(512,mapping.address+mapping.size-address))[0]
            end=raw.find(b'\0')
            if end<=0:return None
            return raw[:end].decode('utf-8')
        except (ValueError,StopIteration,UnicodeError):return None

    def cfstring(self,address: int) -> str | None:
        flags=self.u64(address+8)
        if flags not in (0x7c8,0x7d0):return None
        count=self.u64(address+24)
        if not 0<count<=512:return None
        target=self.pointer_at(address+16)
        if target is None:return None
        raw=self.read(target,count*(2 if flags==0x7d0 else 1))[0]
        return raw.decode('utf-16le' if flags==0x7d0 else 'utf-8')

    def macho_metadata(self,base: int) -> dict:
        """Reuse S106's LINKEDIT/ULEB method, directly checking this cache."""
        head=self.read(base,32)[0]
        if struct.unpack_from('<I',head)[0]!=0xfeedfacf:raise ValueError('Not Mach-O64')
        ncmds,cmdbytes=struct.unpack_from('<II',head,16)
        if ncmds>1024 or cmdbytes>1024*1024:raise ValueError('Mach-O command budget')
        commands=self.read(base+32,cmdbytes)[0];offset=0;link=None;starts=None;uid=None
        for _ in range(ncmds):
            if offset+8>len(commands):raise ValueError('Truncated Mach-O commands')
            cmd,size=struct.unpack_from('<II',commands,offset)
            if size<8 or offset+size>len(commands):raise ValueError('Mach-O command bounds')
            if cmd==0x19 and commands[offset+8:offset+24].split(b'\0',1)[0]==b'__LINKEDIT':
                link=struct.unpack_from('<QQQQ',commands,offset+24)
            if cmd==0x26:starts=struct.unpack_from('<II',commands,offset+8)
            if cmd==0x1b:uid=str(uuid.UUID(bytes=commands[offset+8:offset+24])).upper()
            offset+=size
        if offset!=cmdbytes or not link or not starts or not uid:raise ValueError('Missing exact Mach-O metadata')
        data=self.read(link[0]+starts[0]-link[2],starts[1])[0]
        addresses=[];value=base;shift=part=0;terminated=False
        for octet in data:
            part|=(octet&127)<<shift
            if octet&128:
                shift+=7
                if shift>=64:raise ValueError('ULEB budget')
                continue
            if not part:terminated=True;break
            value+=part;addresses.append(value);shift=part=0
        if not terminated or addresses!=sorted(set(addresses)):raise ValueError('Malformed function starts')
        return {'uuid':uid,'header_and_commands_sha256':hashlib.sha256(head+commands).hexdigest(),
                'function_starts_sha256':hashlib.sha256(data).hexdigest(),'function_starts':addresses}

    def read(self,address: int,count: int) -> tuple[bytes,dict]:
        if count<=0 or count>1024*1024:raise ValueError('VM read budget')
        hits=[m for m in self.mappings if m.address<=address and address+count<=m.address+m.size]
        if len(hits)!=1:raise ValueError('VM span must belong to exactly one mapping')
        m=hits[0];off=m.file_offset+address-m.address
        with m.path.open('rb') as f:f.seek(off);raw=f.read(count)
        if len(raw)!=count:raise ValueError('Short VM read')
        return raw,{'file':m.path.name,'cache_uuid':m.uuid,'file_offset':off,'vm_address':hex(address),'bytes':count,'sha256':hashlib.sha256(raw).hexdigest()}


def verify_disassembly(cache: CacheBytes,text: str) -> dict:
    rows=re.findall(r'^\s*(?:\S+:\s+)?(0x[0-9a-f]+):\s+((?:[0-9a-f]{2} ){3}[0-9a-f]{2})\s+(.*)$',text,re.M)
    if not rows:raise ValueError('No checked instructions')
    code=bytearray();previous=None;spans={}
    for address,word,_ in rows:
        addr=int(address,16)
        if previous is not None and addr!=previous+4:raise ValueError('Noncontiguous instruction sequence')
        expected=bytes.fromhex(word);actual,source=cache.read(addr,4)
        if actual!=expected:raise ValueError('Disassembly differs from original cache bytes')
        code.extend(actual);previous=addr;spans[source['file']]=source['cache_uuid']
    return {'first_address':rows[0][0],'last_address':rows[-1][0],'instruction_count':len(rows),
            'checked_bytes':len(code),'instructions_sha256':hashlib.sha256(code).hexdigest(),'source_cache_UUIDs':spans}
