"""Export one named AIR module to owned private scratch, metadata only to Git.

Reuses air_compare's bounded wrapper parser. Refuses private output inside this
repository; it does not upload a metallib, bitcode or full shader text.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
from air_compare import payloads
from air_alpha import canonicalize


def extract(source: Path,name: str,expected_sha: str,private: Path,output: Path) -> dict:
    if private.resolve().is_relative_to(Path(__file__).resolve().parents[2]):raise ValueError('Private AIR must stay outside Git checkout')
    if source.stat().st_size>16*1024**2:raise ValueError('Metallib size budget')
    data=source.read_bytes()
    if hashlib.sha256(data).hexdigest()!=expected_sha:raise ValueError('Exact source metallib SHA required')
    if output.exists() or private.exists():raise FileExistsError('Output exists')
    matches=[(i,o,r)for i,o,r in payloads(data)if name.encode()in r]
    if len(matches)!=1:raise ValueError('One unambiguous named module required')
    i,o,raw=matches[0];private.mkdir();bc=private/f'{i:04d}.bc';bc.write_bytes(raw)
    text=subprocess.check_output(['/opt/homebrew/opt/llvm/bin/llvm-dis',str(bc),'-o','-'],text=True)
    if len(text.encode())>8*1024**2:raise ValueError('AIR text budget')
    if not re.search(r'^define .*?@'+re.escape(name)+r'\(',text,re.M):raise ValueError('Name is not a defined function')
    target=private/f'{i:04d}.ll.txt';target.write_text(text)
    canon,provenance=canonicalize(text)
    row={'source_metallib_sha256':expected_sha,'function':name,'index':i,'wrapper_offset':o,'payload_bytes':len(raw),
         'payload_sha256':hashlib.sha256(raw).hexdigest(),'canonical_sha256':hashlib.sha256(canon.encode()).hexdigest(),
         'private_text_bytes':len(text.encode()),'provenance':provenance,'private_AIR_or_bitcode_uploaded':False}
    output.write_text(json.dumps(row,indent=2)+'\n');return row


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('name');p.add_argument('expected_sha256');p.add_argument('private',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args();r=extract(a.source,a.name,a.expected_sha256,a.private,a.output)
    print(json.dumps({k:r[k]for k in ['function','index','payload_bytes','canonical_sha256']}))
