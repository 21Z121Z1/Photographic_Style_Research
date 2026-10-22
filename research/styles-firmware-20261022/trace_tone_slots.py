"""Bounded named-struct/constant-offset alias trace for nine unresolved slots.

Scans all 215 payload headers for typed/name markers, then disassembles only
matches. Records loads/stores/vector spans/copies and unresolved escapes.
Absence in this bounded inventory never means a field is globally unused.
"""
import argparse,hashlib,json,re,subprocess,tempfile
from pathlib import Path
from air_compare import payloads
from air_alpha import canonicalize

TARGETS={512:'bg.airy',536:'bg.warmthMatchI',540:'bg.warmthMatchQ',544:'bg.warmthMatchSkyI',548:'bg.warmthMatchSkyQ',552:'bg.bgGlobalMix',560:'fg.airy',604:'fg.faceI',608:'fg.faceQ'}


def width(t):
    types={'float':4,'half':2,'i8':1,'i16':2,'i32':4,'i64':8,'double':8}
    if t in types:return types[t]
    v=re.fullmatch(r'<(\d+) x (float|half|i8|i16|i32|i64)>',t)
    return int(v[1])*types[v[2]]if v else None


def trace(source: Path,output: Path):
    if output.exists():raise FileExistsError(output)
    raw=source.read_bytes();digest=hashlib.sha256(raw).hexdigest()
    if digest!='f6d825a7e5c00d0eec2e4721c51bdb7a6b9554073dc632273dec825ae1bf705f':raise ValueError('Exact matched metallib required')
    all_payloads=list(payloads(raw));selected=[x for x in all_payloads if any(s in x[2]for s in [b'SSRBGAdjustment',b'SSRFGAdjustment',b'warmthMatchSkyI',b'bgGlobalMix',b'faceQ'])]
    if len(selected)>32:raise ValueError('Targeted module budget')
    modules=[];events=[];unresolved=[]
    with tempfile.TemporaryDirectory(prefix='psr-slot-trace-')as t:
        for index,offset,payload in selected:
            bc=Path(t)/f'{index}.bc';bc.write_bytes(payload)
            text=subprocess.check_output(['/opt/homebrew/opt/llvm/bin/llvm-dis',str(bc),'-o','-'],text=True,timeout=30)
            modules.append({'index':index,'payload_bytes':len(payload),'payload_sha256':hashlib.sha256(payload).hexdigest(),'canonical_sha256':hashlib.sha256(canonicalize(text)[0].encode()).hexdigest()})
            pointers={};function='';module_events=[]
            for n,line in enumerate(text.splitlines(),1):
                if line.startswith('define '):
                    function=line.split('@',1)[1].split('(',1)[0];pointers={}
                    for size,pointer in re.findall(r'dereferenceable\((672|68|64)\)[^%]*(%\d+)',line):
                        pointers[pointer]=0 if size=='672'else 488 if size=='68'else 556
                assignment=re.match(r'\s*(%\d+) = (.*)',line)
                if assignment:
                    dst,expr=assignment.groups()
                    typed=re.search(r'getelementptr inbounds %struct\.(SSRParams|SSRBGAdjustment|SSRFGAdjustment), ptr addrspace\(1\) (%\d+), i64 [^,]+, i32 (\d+)(?:, i32 (\d+))?',expr)
                    if typed:
                        ty,base,field,sub=typed.groups();field=int(field)
                        if ty=='SSRParams':
                            offsets={0:0,1:4,2:8,3:12,4:16,5:20,6:24,7:28,8:32,9:36,10:172,11:436,12:452,13:488,14:556,15:620,16:648,17:652,18:656,19:660,20:664,21:668}
                            pointers[dst]=offsets[field]+(4*int(sub)if sub else 0)
                        else:pointers[dst]=(488 if ty=='SSRBGAdjustment'else 556)+4*field
                    else:
                        alias=re.search(r'(?:bitcast|addrspacecast) ptr(?: addrspace\(\d+\))? (%\d+)',expr)
                        gep=re.search(r'getelementptr(?: inbounds)? i8, ptr(?: addrspace\(\d+\))? (%\d+), i64 (-?\d+)',expr)
                        if alias and alias[1]in pointers:pointers[dst]=pointers[alias[1]]
                        elif gep and gep[1]in pointers:pointers[dst]=pointers[gep[1]]+int(gep[2])
                        elif ('phi ptr' in expr or 'select 'in expr and 'ptr'in expr):
                            origins={pointers[x]for x in re.findall(r'%\d+',expr)if x in pointers}
                            if len(origins)==1:pointers[dst]=origins.pop()
                            elif origins:unresolved.append({'module':index,'function':function,'line':n,'kind':'divergent pointer alias'})
                access=re.search(r'\b(load) ([^,]+), ptr(?: addrspace\(\d+\))? (%\d+)',line)
                if not access:
                    access=re.search(r'\b(store) (float|half|i8|i16|i32|i64|double|<\d+ x (?:float|half|i8|i16|i32|i64)>) [^,]+, ptr(?: addrspace\(\d+\))? (%\d+)',line)
                if access:
                    kind,ty,pointer=access.groups();size=width(ty)
                    if pointer in pointers:
                        if size is None:unresolved.append({'module':index,'function':function,'line':n,'kind':'unknown load/store width'})
                        else:
                            start=pointers[pointer];hits=[name for off,name in TARGETS.items()if off<start+size and off+4>start]
                            if hits:module_events.append({'module':index,'function':function,'line':n,'kind':kind,'offset':start,'bytes':size,'fields':hits})
                if '@llvm.memcpy' in line or '@llvm.memmove' in line:
                    refs=[pointers[x]for x in re.findall(r'%\d+',line)if x in pointers]
                    if refs:unresolved.append({'module':index,'function':function,'line':n,'kind':'parameter alias passed to copy intrinsic','offsets':refs})
            events.extend(module_events)
    root=Path(__file__).resolve().parent
    cpu=[]
    for group in ['render-follow-24A446','enum-24A446']:
        manifest=json.loads((root/'evidence'/group/'manifest.json').read_text())
        for row in manifest['methods']:
            if not any(x in row['file']for x in ['static','setup-params','dynamic']):continue
            text=(root/'evidence'/group/row['file']).read_text()
            cpu.append({'file':f'evidence/{group}/{row["file"]}','instructions_sha256':row['instructions_sha256'],'checked_bytes':row['checked_bytes'],
                        'literal_offset_candidates':[line.split(';',1)[0]for line in text.splitlines()if any(f'#0x{x:x}' in line for x in TARGETS)],
                        'candidate_offsets_are_not_proven_parameter_base_aliases':True})
    r={'scope':__doc__,'source_metallib_sha256':digest,'payload_headers_scanned':len(all_payloads),'selected_typed_modules':modules,'events':events,'unresolved_aliases_or_copies':unresolved,'cpu_candidates':cpu,
       'known_CPU_tuning_copies':{'cast':[36,172],'tone':[172,436],'color':[436,452],'note':'These exact getValue:size: spans stop before the nine output slots; proxy uses the same spans and 672B array stride.'},
       'fields':{name:{'offset':off,'reads':sum(x['kind']=='load'and name in x['fields']for x in events),'writes':sum(x['kind']=='store'and name in x['fields']for x in events),'status':'unresolved consumer; not unused'}for off,name in TARGETS.items()},
       'trace_complete_for_all_possible_CPU_or_untyped_shader_aliases':False,'raw_AIR_uploaded':False,'auditor_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    output.write_text(json.dumps(r,indent=2)+'\n');return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('output',type=Path);a=p.parse_args();r=trace(a.source,a.output)
    print(json.dumps({'headers':r['payload_headers_scanned'],'modules':len(r['selected_typed_modules']),'fields':r['fields'],'unresolved_aliases':len(r['unresolved_aliases_or_copies'])}))
