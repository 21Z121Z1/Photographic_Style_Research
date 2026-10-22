"""Inject stores at selected original helper/root SSA without replacing math."""
import re,hashlib
from main_full_host import build as full_build
from leaf_host import short


def instrument(ir,function_label,points,label):
    body=next(m[0]for m in re.finditer(r'^define[^\n]*@([^ (]+)\([^\n]+\{\n.*?^}',ir,re.M|re.S)if short(m[1])==function_label);original=body;offset=0;layout=[]
    for ssa,ty,n in points:
        lines=body.splitlines();i=next(i for i,x in enumerate(lines)if x.startswith(f'  %{ssa} ='))
        if ' = phi 'in lines[i]:
            while i+1<len(lines)and ' = phi 'in lines[i+1]:i+=1
        extra=[]
        for lane in range(n):
            j=offset+lane;value=f'%{ssa}'
            if n>1:extra += [f'%{label}_v{j}=extractelement <{n} x {ty}> %{ssa},i32 {lane}'];value=f'%{label}_v{j}'
            if ty=='half':extra += [f'%{label}_f{j}=fpext half {value} to float'];value=f'%{label}_f{j}'
            extra += [f'%{label}_p{j}=getelementptr float,ptr @{label},i64 {j}',f'store float {value},ptr %{label}_p{j}']
        lines[i+1:i+1]=extra;body='\n'.join(lines);layout.append((ssa,ty,n,offset));offset+=n
    ir=f'@{label} = global [{offset} x float] zeroinitializer\n'+ir.replace(original,body);attrs=re.search(r'#(\d+) \{',body.splitlines()[0])[1];line=re.search(r'^attributes #'+attrs+r' = .*$',ir,re.M)[0];updated=re.sub(r'memory\([^)]*\)','memory(readwrite)',line);ir=ir.replace(line,updated)
    return ir,{'symbol':re.search(r'@([^ (]+)\(',original.splitlines()[0])[1],'original_selected_function_sha256':hashlib.sha256(original.encode()).hexdigest(),'layout':layout,'count':offset,'memory_summary_change':None if line==updated else'conservatively widened to readwrite for global observations','original_arithmetic_predicates_and_FP_attrs_changed':False}


def widen_callsites(ir,symbols):
    changes={}
    for symbol in symbols:
        for call in re.finditer(r'^.*call[^\n]*@'+re.escape(symbol)+r'\([^\n]*$',ir,re.M):
            for n in re.findall(r'#(\d+)',call[0]):
                line=re.search(r'^attributes #'+n+r' = .*$',ir,re.M)[0];updated=re.sub(r'memory\([^)]*\)','memory(readwrite)',line)
                if updated!=line:changes[n]='conservatively widened callsite to readwrite for global diagnostics';ir=ir.replace(line,updated)
    return ir,changes


def build(source,models):
    ir,meta=full_build(source);probes={}
    for name,(label,values)in models.items():
        points=[(ssa,'half'if v.precision=='h'else'float',1 if v.lo.shape==()else len(v.lo))for ssa,v in values.items()];ir,m=instrument(ir,label,points,'psr_trace_'+name);probes[name]=m
    ir,changes=widen_callsites(ir,[p['symbol']for p in probes.values()])
    return ir,{'original':meta,'probes':probes,'callsite_memory_summary_changes':changes}
