"""New scope: AIR13 interprocedural parameter aliases and two CPU blit islands.

No215-header rescan. Reports may-reach pointer paths, byte-span accesses and
unresolved escapes. A missing read in this bounded closure never means unused.
Raw AIR and CPU image stay outside Git. Existing CPU text SHA is admission.
"""
import argparse,hashlib,itertools,json,re
from pathlib import Path
from air_alpha import canonicalize
from leaf_host import short
from trace_tone_slots import TARGETS,width

EXPECTED='b56d7f51d4556af99356bf5963d270358b2422425b7ba929f056d1a4c95668ea'
PARAM_OFFSETS=(0,4,8,12,16,20,24,28,32,36,172,436,452,488,556,620,648,652,656,660,664,668)
CAST_OFFSETS=(0,4,8,12,16,20,24,36,48,60,64,68,72,84,96,108,112,116,120,124,128,132)


def split_args(s):
    parts=[];start=0;depth=0
    for i,c in enumerate(s):
        if c in '(<[{':depth+=1
        elif c in ')>]}':depth-=1
        elif c==','and depth==0:parts.append(s[start:i].strip());start=i+1
    parts.append(s[start:].strip());return parts


def gep_offset(ty,indices):
    if any(not re.fullmatch(r'-?\d+',i)for i in indices):return None
    ix=list(map(int,indices))
    if not ix:return None
    sizes={'SSRParams':672,'SSRBGAdjustment':68,'SSRFGAdjustment':64,'SSRCastAdjustments':136,'SSRToneAdjustments':264,'SSRColorAdjustments':16,'SSRHazeAdjustments':36,'SSRSemanticToneAdjustment':28,'i8':1,'float':4}
    ty=ty.removeprefix('%struct.')
    if ty not in sizes:return None
    offset=ix[0]*sizes[ty]
    if len(ix)>1:
        field=ix[1]
        if ty=='SSRParams':
            if not 0<=field<len(PARAM_OFFSETS):return None
            offset+=PARAM_OFFSETS[field]
            if len(ix)>2:
                if field==9:
                    if not 0<=ix[2]<len(CAST_OFFSETS):return None
                    offset+=CAST_OFFSETS[ix[2]]
                else:offset+=4*ix[2]
            if len(ix)>3:offset+=4*ix[3]
        elif ty=='SSRCastAdjustments':
            if not 0<=field<len(CAST_OFFSETS):return None
            offset+=CAST_OFFSETS[field]+(4*ix[2]if len(ix)>2 else 0)
        elif ty not in ['i8','float']:offset+=4*field
        else:return None
    return offset


def trace(source,root='generateColorCubes',root_parameter=4):
    functions={}
    for m in re.finditer(r'^define[^\n]*@([^ (]+)\(([^\n]*)\)[^\n]*\{\n.*?^}',source,re.M|re.S):
        header=m[0].splitlines()[0];args=split_args(header[header.index('(')+1:header.rindex(')')]);formals=[re.findall(r'%[\w.]+',a)[-1]for a in args];functions[m[1]]=(m[0],args,formals,source.count('\n',0,m.start())+1)
    if root not in functions:raise ValueError('Missing root')
    pending=[(root,{root_parameter:0})];visited=set();events=[];edges=[];unresolved=[];pointer_ops=[];bounded_loops=[]
    while pending:
        name,incoming=pending.pop();key=(name,tuple(sorted(incoming.items())))
        if key in visited:continue
        visited.add(key)
        if len(visited)>64:raise ValueError('Bounded closure context budget exceeded')
        body,args,formals,start=functions[name];pointers={formals[i]:v for i,v in incoming.items()};pointer_ranges={};index_ranges={}
        loop_lines=['%17 = phi i32 [ 0, %3 ], [ %34, %16 ]','%18 = zext i32 %17 to i64','%34 = add nuw nsw i32 %17, 1','%35 = icmp eq i32 %34, 3','br i1 %35, label %6, label %16']
        if short(name)=='renderWarmthCastAdjustments'and all(v in body for v in loop_lines):
            # Entry reaches16 with0; body increments1 and exits when next=3.
            # Hence header17 and zext18 range over0,1,2, with no wrap.
            index_ranges['%18']=(0,2);bounded_loops.append({'function':short(name),'index_SSA':18,'inclusive_index_range':[0,2],'selected_instruction_text_sha256':hashlib.sha256('\n'.join(loop_lines).encode()).hexdigest(),'proof':'0 entry, unit no-wrap increment, exit at next3, only header/self predecessors in exact admitted AIR13'})
        for rel,line in enumerate(body.splitlines()[1:],1):
            loc={'function':short(name),'line':start+rel,'instruction_sha256':hashlib.sha256(line.encode()).hexdigest()};assignment=re.match(r'\s*(%[\w.]+)\s*=\s*(.*)',line)
            if re.search(r'\b(?:store ptr|ret ptr|ptrtoint)\b',line)and any(v in pointers for v in re.findall(r'%[\w.]+',line)):unresolved.append(dict(loc,kind='parameter pointer stored/returned or converted to integer'))
            if assignment:
                dst,expr=assignment.groups();g=re.search(r'getelementptr(?: inbounds)? ([^,]+), ptr(?: addrspace\(\d+\))? (%[\w.]+), (.*)',expr)
                alias=re.search(r'(?:bitcast|addrspacecast) ptr(?: addrspace\(\d+\))? (%[\w.]+)',expr)
                if g and g[2]in pointers:
                    indices=re.findall(r'i\d+ (-?\d+|%[\w.]+)',g[3]);delta=gep_offset(g[1],indices);base=pointers[g[2]];pointers[dst]=None if delta is None or base is None else base+delta
                    if delta is None:
                        choices=[list(map(str,range(index_ranges[i][0],index_ranges[i][1]+1)))if i in index_ranges else[i]for i in indices];offsets=[gep_offset(g[1],v)for v in itertools.product(*choices)]
                        if base is not None and offsets and all(v is not None for v in offsets):pointer_ranges[dst]=(base+min(offsets),base+max(offsets));pointer_ops.append(dict(loc,kind='induction-bounded array GEP',offset_range=list(pointer_ranges[dst])))
                        else:unresolved.append(dict(loc,kind='dynamic or unsupported derived GEP',base=base))
                    if not g[1].startswith('%struct.'):pointer_ops.append(dict(loc,kind='untyped GEP',base=base,delta=delta))
                elif alias and alias[1]in pointers:pointers[dst]=pointers[alias[1]];pointer_ops.append(dict(loc,kind='cast alias',base=pointers[dst]))
                elif 'phi ptr'in expr or 'select 'in expr and 'ptr'in expr:
                    values=re.findall(r'\[\s*(%[\w.]+|null|poison|undef)\s*,',expr)if 'phi ptr'in expr else re.findall(r'ptr(?: addrspace\(\d+\))? (%[\w.]+|null|poison|undef)',expr)
                    if any(v in pointers for v in values):
                        refs=[pointers.get(v)for v in values];pointers[dst]=refs[0]if refs and refs[0]is not None and all(v==refs[0]for v in refs)else None
                        if pointers[dst]is None:unresolved.append(dict(loc,kind='divergent pointer join'))
            access=re.search(r'\b(load) ([^,]+), ptr(?: addrspace\(\d+\))? (%[\w.]+)',line)
            if not access:access=re.search(r'\b(store) (float|half|i8|i16|i32|i64|<\d+ x (?:float|half|i\d+)>) [^,]+, ptr(?: addrspace\(\d+\))? (%[\w.]+)',line)
            if access and access[3]in pointers:
                kind,ty,pointer=access.groups();size=width(ty);base=pointers[pointer]
                low,high=pointer_ranges.get(pointer,(base,base))
                if size is None or low is None:unresolved.append(dict(loc,kind='unknown parameter access span'))
                else:events.append(dict(loc,kind=kind,offset=low,offset_upper=high,bytes=size,target_fields=[v for o,v in TARGETS.items()if o<high+size and low<o+4]))
            call=re.search(r'@([^ (]+)\((.*)\)',line)
            if call:
                callee,raw=call.groups();passed={}
                for i,arg in enumerate(split_args(raw)):
                    if not arg.startswith('ptr'):continue
                    refs=re.findall(r'%[\w.]+',arg)
                    if not refs or refs[-1]not in pointers:continue
                    base=pointers[refs[-1]];passed[i]=base
                    span=re.search(r'dereferenceable\((\d+)\)',arg);span=int(span[1])if span else None
                    edges.append(dict(loc,caller=short(name),callee=short(callee),formal_index=i,base_offset=base,declared_span=span,target_fields=[v for o,v in TARGETS.items()if base is None or span is None or o<base+span and base<o+4]))
                if passed:
                    if callee in functions:pending.append((callee,passed))
                    else:unresolved.append(dict(loc,kind='derived pointer escapes to external call',callee=callee,bases=list(passed.values())))
    return {'root':root,'contexts':len(visited),'functions':sorted({short(k[0])for k in visited}),'parameter_accesses':events,'pointer_call_edges':edges,'derived_untyped_pointer_ops':pointer_ops,'bounded_induction_loops':bounded_loops,'unresolved':unresolved,'target_read_count':sum(v['kind']=='load'and bool(v['target_fields'])for v in events),'all_module_pointer_intrinsics':{p:len(re.findall(p,source))for p in ['@llvm.memcpy','@llvm.memmove','@llvm.memset','ptrtoint','inttoptr']},'scope':'syntactic interprocedural may-reach closure; no branch feasibility or global-unused proof'}


def check(source,output):
    if output.exists():raise FileExistsError(output)
    text=source.read_text();digest=hashlib.sha256(canonicalize(text)[0].encode()).hexdigest()
    if digest!=EXPECTED:raise ValueError('Exact AIR13 reference required')
    root=Path(__file__).parent;e=root/'evidence';result=trace(text)
    cpu=e/'cache-methods-24A446/style-engine-process.asm.txt';manifest=json.loads((cpu.parent/'manifest.json').read_text());meta=next(m for m in manifest['methods']if m['file']==cpu.name)
    if hashlib.sha256(cpu.read_bytes()).hexdigest()!=meta['text_sha256']:raise ValueError('Admitted CPU text SHA mismatch')
    c=cpu.read_text();copies=[]
    for address,description in [('1d42c67f0','source x21 unresolved; destination self(x20)+0x148 buffer; both offsets0; size destination.length'),('1d42c69c8','source self(x20)+0x148 buffer; destination bufferView of [sp+0x460]; both offsets0; size source.length')]:
        lines=c.splitlines();i=next(i for i,l in enumerate(lines)if l.startswith(address+':'));window='\n'.join(lines[i-10:i+1]);copies.append({'address':'0x'+address,'instruction_window_sha256':hashlib.sha256(window.encode()).hexdigest(),'argument_alias_facts':description,'bridge_to_SSRParams_not_proven':True})
    old=json.loads((e/'tone-slot-alias-trace.json').read_text());fields=[]
    for offset,name in TARGETS.items():
        fields.append({'field':name,'SSRParams_byte':offset,'known_writer':next(v for v in old['events']if name in v['fields']),'AIR13_root':'generateColorCubes argument4 / Metal buffer1; 672B declaration','AIR13_reachable_pointer_edges':[v for v in result['pointer_call_edges']if name in v['target_fields']],'AIR13_target_accesses':[v for v in result['parameter_accesses']if name in v['target_fields']],'breakpoint':'No target-byte read found in this closed AIR13 parameter-pointer traversal. CPU Proxy +0x1b0 array -> dynamic producer -> cube dispatch bridge remains unextracted; CPU blit island origins are unproved. Other modules/callers remain software work.','status':'unresolved global consumer; not unused'})
    image=root.parents[2]/'firmware-iphone17-3-systemos/decrypted/043-70113-711.dmg'
    out={'scope':__doc__,'hardware':'iPhone17,3','build':'24A446','AIR13_canonical_sha256':digest,'AIR13_kernel_params_binding':'argument4, Metal buffer1, declared672B; metadata22','new_scope_vs_S9':'call-argument origin propagation from generateColorCubes through recursive helpers, derived pointer/byte-span/copy escapes; two previously untraced CPU blit argument islands; no resource-header rescan','payloads_statically_inspected':1,'payload_headers_consumer_scanned':0,'closure':result,'CPU_copy_islands':copies,'CPU_source_sha256':hashlib.sha256(cpu.read_bytes()).hexdigest(),'fields':fields,'missing_CPU_image':{'relative_target':'../firmware-iphone17-3-systemos/decrypted/043-70113-711.dmg','exists':image.exists(),'expected_sha256':'bce06bf973fe4fcce39f5401be42352b96e2e052cf4c182d107ef8fd2d86fe18','blocked_action':'new byte-verified Proxy dynamic/cube CPU disassembly','reason':'previously acquired decrypted SystemOS image and dyld files absent in task cache; symbols/objc and selected text remain','status':'not attempted; missing input, not permission denied','download_or_mount_attempted':False},'CPU_proxy_next_symbols':['-[CMISmartStyleProxyRendererV1 _calculateDynamicRenderParameters] @0x1d437335c','-[CMISmartStyleProxyRendererV1 _generateColorCubes] @0x1d4373474'],'native_calls':0,'raw_AIR_uploaded':False,'global_unused_claim':False,'unfinished_software_consumers':9};output.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n');print(json.dumps({'contexts':result['contexts'],'functions':len(result['functions']),'target_reads':result['target_read_count'],'unresolved_aliases':len(result['unresolved']),'CPU_copy_islands':len(copies),'missing_image':not image.exists()}));return out


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('output',type=Path);a=p.parse_args();check(a.source,a.output)
