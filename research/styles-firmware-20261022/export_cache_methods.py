"""Export bounded actual cache methods; reuse the existing S106 annotations.

Annotations are locators, not dataflow proofs. Original instructions are checked
against independent cache mapping bytes before any text reformatting/annotation.
"""
from __future__ import annotations

import argparse
import ast
import bisect
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess

from dyld_bytes import CacheBytes,verify_disassembly

SELECTED={
 'cmi':[
  ('prior-main','+[CMISmartStyleCCMPriorGenerator calculatePriorCCMforCast:tone:color:intensity:priorStrength:isStartupPrior:]'),
  ('prior-wrapper','+[CMISmartStyleCCMPriorGenerator calculatePriorCCMforCast:tone:color:intensity:priorStrength:]'),
  ('prior-conversion','_ssccmpg_float3x4FromMatrix'),
  ('engine-configuration','-[CMIStyleEngineCommonSettings configurationForUseCase:]'),
  ('engine-tuning','-[CMIStyleEngineCommonSettings tuningParametersForUseCase:]'),
  ('engine-tuning-load','-[CMIStyleEngineCommonSettings loadTuningParameters]'),
  ('pixel-renderer-process','-[CMISmartStylePixelBufferRendererV1 process]'),
  ('style-engine-process','-[CMIStyleEngineProcessor process]'),
  ('engine-polynomial-count','-[CMIStyleEngineProcessor _linearSystemNumberOfPolynomials]'),
  ('engine-system-size','-[CMIStyleEngineProcessor _linearSystemSize]')],
 'capture':[
  ('load-bundle','_BWLoadProcessorBundle'),
  ('learning-loader','-[BWSmartStyleLearningNode _loadAndConfigureSmartStyleBundle]'),
  ('encoder-loader','-[BWPhotoEncoderController _loadCreateAndSetupSmartStyleRenderingProcessor]'),
  ('controller-loader','-[BWSmartStyleRenderingProcessorController _loadSetupAndPrepareSmartStyleRenderingProcessor:]')]
}


def annotation_functions(cache: CacheBytes,repo: Path):
    # Only selected function definitions execute; old top-level hardcoded paths
    # and Linux cache constructor are deliberately never imported/executed.
    class View:
        def read(self,a,n):return cache.read(a,n)[0]
        def u64(self,a):return cache.pointer_at(a)
        def decode_pointer(self,v):return v
        def text(self,a):return cache.text(a)
        def cfstring(self,a):return cache.cfstring(a)
    namespace={'c':View(),'struct':struct,'re':re,'stub_cache':{}}
    sources=[];root=repo/'research/hdr-native/evidence/s106/repro'
    for name,names in [('objc_locate.py',['ptr','named','selector_from_stub']),('trace_capture.py',['literal','sel']),('trace_follow.py',['annotate'])]:
        path=root/name;raw=path.read_bytes();tree=ast.parse(raw)
        nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
        if len(nodes)!=len(names):raise ValueError('Expected existing S106 functions changed')
        exec(compile(ast.Module(body=nodes,type_ignores=[]),'existing-s106-'+name,'exec'),namespace)
        sources.append({'path':str(path.relative_to(repo)),'sha256':hashlib.sha256(raw).hexdigest(),'functions':names})
    return namespace['annotate'],sources


def select_symbol(text: str,name: str,address: int | None=None) -> int:
    hits={int(m[1],16)for m in re.finditer(r'^(0x[0-9a-f]+):[^\n]*?\t([^\t\n]+)\t?$',text,re.M)if m[2]==name}
    if address is not None:hits={a for a in hits if a==address}
    if len(hits)!=1:raise ValueError('Symbol must resolve unambiguously; specify its verified address for duplicate local names')
    return hits.pop()


def export(scratch: Path,output: Path,repo: Path,selection: dict | None=None) -> dict:
    if output.exists():raise FileExistsError(output)
    root=scratch/'mount/System/Library/Caches/com.apple.dyld';cache=CacheBytes(root)
    info=json.loads((scratch/'cache-info.json').read_text());annotate,reuse=annotation_functions(cache,repo)
    output.mkdir()
    result={'hardware':'iPhone17,3','image_build':'24A446','cache_uuid':info['uuid'],
            'cache_platform':info['platform'],'source_reuse':reuse,'frameworks':{},'methods':[],
            'exporter_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'original_iOS_code_executed':False,'binary_uploaded':False,'actual_runtime_loader_verified':False}
    total=0
    for label,methods in (selection if selection is not None else SELECTED).items():
        paths={'cmi':('CMImaging','PrivateFrameworks'),'capture':('CMCapture','PrivateFrameworks'),'foundation':('Foundation','Frameworks')}
        if label not in paths:raise ValueError('Unsupported source framework')
        framework,group=paths[label]
        image=next(x for x in info['dylibs'] if x['name']==f'/System/Library/{group}/{framework}.framework/{framework}')
        meta=cache.macho_metadata(image['load_address'])
        if meta['uuid']!=image['uuid']:raise ValueError('Framework UUID mismatch')
        cli=[int(l,16)for l in (scratch/f'{label}-starts.private.txt').read_text().splitlines() if l.startswith('0x')]
        if meta['function_starts']!=cli:raise ValueError('Independent function starts differ from CLI')
        result['frameworks'][framework]={**image,**{k:v for k,v in meta.items()if k!='function_starts'}}
        symbols=(scratch/f'{label}-symbols.private.txt').read_text()
        for item in methods:
            if len(item)not in (2,3):raise ValueError('Selection needs file/name and optional exact local-symbol address')
            short,name=item[:2];requested=int(item[2],0)if len(item)==3 else None
            if not re.fullmatch('[a-z0-9-]{1,80}',short):raise ValueError('Unsafe output filename')
            start=select_symbol(symbols,name,requested);i=bisect.bisect_left(cli,start)
            if i>=len(cli)-1 or cli[i]!=start:raise ValueError('Symbol is not a function start')
            end=cli[i+1];size=end-start
            if not 0<size<=128*1024 or size%4:raise ValueError('Function byte budget')
            total+=size
            if total>512*1024:raise ValueError('Export total budget')
            raw=subprocess.check_output(['ipsw','dyld','disass',str(root/'dyld_shared_cache_arm64e'),'--vaddr',hex(start),'--count',str(size//4),'--quiet'],text=True,stderr=subprocess.PIPE,timeout=60)
            checked=verify_disassembly(cache,raw)
            if checked['checked_bytes']!=size:raise ValueError('Incomplete function export')
            def word(m):return f'{int(m[1],16):x}: {int.from_bytes(bytes.fromhex(m[2]),"little"):08x}\t{m[3]}'
            reformatted=re.sub(r'^(0x[0-9a-f]+):\s+((?:[0-9a-f]{2} ){3}[0-9a-f]{2})\s+(.*)$',word,raw,flags=re.M)
            text=f'iPhone17,3 /24A446; {framework} UUID {meta["uuid"]}\n{name}\nComplete bounds independently decoded from LC_FUNCTION_STARTS. All original instruction words verified. Annotations are locators, not algorithm/runtime proofs.\n'+annotate(reformatted)
            path=output/f'{short}.asm.txt';path.write_text(text)
            result['methods'].append({'name':name,'framework':framework,'file':path.name,'end_exclusive':hex(end),**checked,'text_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    result['total_checked_bytes']=total
    (output/'manifest.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('scratch',type=Path);p.add_argument('output',type=Path);p.add_argument('--selection',type=Path)
    a=p.parse_args();r=export(a.scratch,a.output,Path(__file__).resolve().parents[2],json.loads(a.selection.read_text()) if a.selection else None)
    print(json.dumps({'methods':len(r['methods']),'checked_bytes':r['total_checked_bytes']}))
