"""Compile only requested original leaf functions with explicit host AIR shims.

No abort/identity placeholders: unsupported intrinsic dependencies are errors.
The host libm/dot/sampler semantics are declared, not original GPU behavior.
"""
import hashlib,json,re
from pathlib import Path
from native_semantic_tone_check import fragment,SAMPLER_C


def short(name):
    q=re.match(r'_Z(\d+)',name)
    return name[q.end():q.end()+int(q[1])]if q else name


MATH_C=SAMPLER_C+'\nfloat psr_pow_scalar(float a,float b){return powf(a,b);}\nfloat psr_sqrt_scalar(float a){return sqrtf(a);}\n'
MATH_C+='\n'.join('float psr_'+n+'_scalar(float a){return '+n+'f(a);}'for n in ['sin','cos','exp'])+'\nfloat psr_atan2_scalar(float a,float b){return atan2f(a,b);}\n'
MATH_C+='float psr_fmod_scalar(float a,float b){return fmodf(a,b);}\n'


def shims(names):
    out=['declare float @psr_pow_scalar(float,float)','declare float @psr_sqrt_scalar(float)','declare float @psr_sample(ptr,float)','declare float @llvm.fabs.f32(float)'];done=set()
    out += ['declare float @psr_'+n+'_scalar(float)'for n in ['sin','cos','exp']]+['declare float @psr_atan2_scalar(float,float)']
    out += ['declare float @psr_fmod_scalar(float,float)']
    def add(name):
        if name in done:return
        done.add(name)
        operation=name.replace('air.fast_','air.')
        if name=='air.convert.u.i1.f.f32':out.append('define i1 @air.convert.u.i1.f.f32(float %a){\n%r=fcmp une float %a,0.0\nret i1 %r\n}');return
        conversion=re.fullmatch(r'air.convert.f.v(\d+)f(16|32).f.v\1f(16|32)',name)
        if conversion:
            n,dst,src=conversion.groups();a=f'<{n} x '+('half'if src=='16'else'float')+'>';b=f'<{n} x '+('half'if dst=='16'else'float')+'>';op='fpext'if dst=='32'else'fptrunc'
            out.append(f'define {b} @{name}({a} %a){{\n%r={op} {a} %a to {b}\nret {b} %r\n}}');return
        dot=re.fullmatch(r'air.dot.v(\d+)f(16|32)',name)
        if dot:
            n,b=dot.groups();n=int(n);scalar='half'if b=='16'else'float';ty=f'<{n} x {scalar}>';lines=[f'define {scalar} @{name}({ty} %a,{ty} %b){{']
            for i in range(n):lines += [f'%a{i}=extractelement {ty} %a,i32 {i}',f'%b{i}=extractelement {ty} %b,i32 {i}',f'%p{i}=fmul fast {scalar} %a{i},%b{i}']
            prev='%p0'
            for i in range(1,n):lines += [f'%s{i}=fadd fast {scalar} {prev},%p{i}'];prev=f'%s{i}'
            lines += [f'ret {scalar} {prev}','}'];out.append('\n'.join(lines));return
        vector=None if name=='air.sample_texture_2d.v4f16'else re.search(r'\.v(\d+)f(16|32)$',name);bits='half'if name.endswith('f16')else'float';ty=bits
        if vector:
            n,b=vector.groups();n=int(n);scalar=name[:vector.start()]+f'.f{b}';add(scalar);ty=f'<{n} x {"half"if b=="16"else"float"}>'
            arity=3 if any(x in operation for x in ['.mix.','.clamp.'])else 2 if any(x in operation for x in ['.pow.','.fmin.','.fmax.','.atan2.'])else 1
            params=','.join(f'{ty} %a{i}'for i in range(arity));lines=[f'define {ty} @{name}({params}){{']
            for lane in range(n):
                for i in range(arity):lines.append(f'%x{lane}_{i}=extractelement {ty} %a{i},i32 {lane}')
                lines.append(f'%v{lane}=call {"half"if b=="16"else"float"} @{scalar}('+','.join(f'{"half"if b=="16"else"float"} %x{lane}_{i}'for i in range(arity))+')')
                lines.append(f'%r{lane}=insertelement {ty} '+('poison'if lane==0 else f'%r{lane-1}')+f',{"half"if b=="16"else"float"} %v{lane},i32 {lane}')
            lines+= [f'ret {ty} %r{n-1}','}'];out.append('\n'.join(lines));return
        if name=='air.get_width_texture_2d':out.append('define i32 @air.get_width_texture_2d(ptr addrspace(1) %p,i32 %lod){\n%n=load i32,ptr addrspace(1) %p\nret i32 %n\n}');return
        if name.startswith('air.convert.f.f16.'):
            op='sitofp'if'.s.i32'in name else'uitofp';out.append(f'define half @{name}(i32 %a){{\n%r={op} i32 %a to half\nret half %r\n}}');return
        if '.mix.'in name:
            out.append(f'define {ty} @{name}({ty} %a,{ty} %b,{ty} %w){{\n%d=fsub fast {ty} %b,%a\n%p=fmul fast {ty} %d,%w\n%r=fadd fast {ty} %a,%p\nret {ty} %r\n}}');return
        if any(x in name for x in ['.fmax3.','.fmin3.']):
            base=name.replace('3.','.');add(base);out.append(f'define {ty} @{name}({ty} %a,{ty} %b,{ty} %c){{\n%x=call {ty} @{base}({ty} %a,{ty} %b)\n%r=call {ty} @{base}({ty} %x,{ty} %c)\nret {ty} %r\n}}');return
        if any(x in operation for x in ['.fmin.','.fmax.']):
            pred='olt'if'.fmin.'in operation else'ogt';out.append(f'define {ty} @{name}({ty} %a,{ty} %b){{\n%c=fcmp {pred} {ty} %a,%b\n%r=select i1 %c,{ty} %a,{ty} %b\nret {ty} %r\n}}');return
        if '.clamp.'in operation or '.saturate.'in operation:
            base=name[:name.rindex('.')];prefix='air.fast_'if'fast_'in name else'air.';mn=prefix+'fmin.'+('f16'if ty=='half'else'f32');mx=prefix+'fmax.'+('f16'if ty=='half'else'f32');add(mn);add(mx)
            sat='.saturate.'in operation;params=f'{ty} %a'if sat else f'{ty} %a,{ty} %lo,{ty} %hi';lo='0xH0000'if ty=='half'else'0.0';hi='0xH3C00'if ty=='half'else'1.0'
            out.append(f'define {ty} @{name}({params}){{\n%x=call {ty} @{mx}({ty} %a,{ty} '+(lo if sat else'%lo')+f')\n%r=call {ty} @{mn}({ty} %x,{ty} '+(hi if sat else'%hi')+f')\nret {ty} %r\n}}');return
        if '.fabs.'in operation:
            pre='%x=fpext half %a to float\n'if ty=='half'else'';x='%x'if ty=='half'else'%a';post='%r=fptrunc float %f to half\nret half %r'if ty=='half'else'ret float %f'
            out.append(f'define {ty} @{name}({ty} %a){{\n'+pre+f'%f=call float @llvm.fabs.f32(float {x})\n'+post+'\n}');return
        if '.sign.'in operation:
            zero='0xH0000'if ty=='half'else'0.0';one='0xH3C00'if ty=='half'else'1.0';neg='0xHBC00'if ty=='half'else'-1.0'
            out.append(f'define {ty} @{name}({ty} %a){{\n%p=fcmp ogt {ty} %a,{zero}\n%n=fcmp olt {ty} %a,{zero}\n%x=select i1 %n,{ty} {neg},{ty} {zero}\n%r=select i1 %p,{ty} {one},{ty} %x\nret {ty} %r\n}}');return
        math=next((n for n in ['pow','sqrt','sin','cos','atan2','exp','fmod']if'.'+n+'.'in operation),None)
        if math:
            arity=2 if math in ['pow','atan2','fmod']else 1;params=','.join(f'{ty} %a{i}'for i in range(arity));lines=[f'define {ty} @{name}({params}){{']
            for i in range(arity):
                if ty=='half':lines.append(f'%x{i}=fpext half %a{i} to float')
            args=','.join(f'float %'+(f'x{i}'if ty=='half'else f'a{i}')for i in range(arity));lines.append(f'%f=call float @psr_{math}_scalar({args})')
            lines += ['%r=fptrunc float %f to half','ret half %r']if ty=='half'else['ret float %f'];lines+=['}'];out.append('\n'.join(lines));return
        if name=='air.dot.v3f16':
            lines=['define half @air.dot.v3f16(<3 x half> %a,<3 x half> %b){']
            for i in range(3):lines += [f'%a{i}=extractelement <3 x half> %a,i32 {i}',f'%b{i}=extractelement <3 x half> %b,i32 {i}',f'%p{i}=fmul fast half %a{i},%b{i}']
            lines+=['%s=fadd fast half %p0,%p1','%r=fadd fast half %s,%p2','ret half %r','}'];out.append('\n'.join(lines));return
        if name=='air.sample_texture_2d.v4f16':
            out.append('define {<4 x half>,i8} @air.sample_texture_2d.v4f16(ptr addrspace(1) %p,ptr addrspace(2) %s,<2 x float> %xy,i1 %a,<2 x i32> %o,i1 %b,float %c,float %d,i32 %e){\n%u=extractelement <2 x float> %xy,i32 0\n%t=addrspacecast ptr addrspace(1) %p to ptr\n%f=call float @psr_sample(ptr %t,float %u)\n%h=fptrunc float %f to half\n%v=insertelement <4 x half> zeroinitializer,half %h,i32 0\n%r=insertvalue {<4 x half>,i8} zeroinitializer,<4 x half> %v,0\nret {<4 x half>,i8} %r\n}');return
        raise ValueError('Unimplemented host intrinsic: '+name)
    # Dot must be handled before generic vector decomposition.
    if 'air.dot.v3f16'in names:
        names=set(names);names.remove('air.dot.v3f16');body=['define half @air.dot.v3f16(<3 x half> %a,<3 x half> %b){']
        for i in range(3):body += [f'%a{i}=extractelement <3 x half> %a,i32 {i}',f'%b{i}=extractelement <3 x half> %b,i32 {i}',f'%p{i}=fmul fast half %a{i},%b{i}']
        body += ['%s=fadd fast half %p0,%p1','%r=fadd fast half %s,%p2','ret half %r','}'];out.append('\n'.join(body));done.add('air.dot.v3f16')
    for name in sorted(names):add(name)
    return '\n'.join(out)


def inline_functions(source):
    """Original straight-line BG blocks, with only bijective SSA renaming.

    Gate/f32->half is intentionally outside each half-input block. Parent SHA
    and exact selected text SHA make this distinction independently checkable.
    """
    parent=next(m[0]for m in re.finditer(r'^define[^\n]*@_Z19renderBGAdjustments[^\n]+\{\n.*?^}',source,re.M|re.S))
    additions=[];metadata={}
    for name,start,stop,rgb,amount in [('BG.localContrast_inline',90,142,83,89),('BG.gammaContrast_inline',151,174,144,150)]:
        body=re.search(r'^  %'+str(start)+r' = .*?^  %'+str(stop)+r' = [^\n]+',parent,re.M|re.S)[0]
        mapping={str(rgb):'rgb','1':'guide',str(amount):'amount'}
        renamed=re.sub(r'%(\d+)',lambda m:'%'+mapping.get(m[1],'v'+m[1]),body)
        text=f'define internal fastcc <3 x half> @_Z{len(name)}{name}(<3 x half> %rgb,half %guide,half %amount) #10 {{\n'+renamed+f'\nret <3 x half> %v{stop}\n}}'
        additions.append(text);metadata[name]={'parent_function_sha256':hashlib.sha256(parent.encode()).hexdigest(),'original_selected_text_sha256':hashlib.sha256(body.encode()).hexdigest(),'original_SSA_inclusive':[start,stop],'external_SSA_mapping':mapping,'arithmetic_or_intrinsics_changed':False,'excludes_f32_gate_and_half_conversion':True,'renamed_wrapper_sha256':hashlib.sha256(text.encode()).hexdigest()}
    return '\n'.join(additions),metadata


def build(source,names,*,extra_functions='',emit_wrappers=True):
    fragment(source)  # Exact source identity check only.
    if extra_functions:source+='\n'+extra_functions+'\n'
    if any(n.startswith('BG.')for n in names):source+='\n'+inline_functions(source)[0]+'\n'
    functions={}
    for m in re.finditer(r'^define[^\n]*?@([^ (]+)\([^\n]+\{\n',source,re.M):functions[m[1]]=source[m.start():source.index('\n}',m.end())+2]
    roots=[next(n for n in functions if short(n)==name)for name in names];selected=set(roots);pending=list(roots)
    while pending:
        for n in re.findall(r'@(_Z[^ (]+)\(',functions[pending.pop()]):
            if n not in selected:selected.add(n);pending.append(n)
    bodies=[functions[n]for n in sorted(selected)];used=set(re.findall(r'@(air\.[^ (]+)\(', '\n'.join(bodies)));definitions=dict(re.findall(r'^!(\d+) = (.*)$',source,re.M));ids=set(re.findall(r'!(\d+)', '\n'.join(bodies)));pending=list(ids)
    while pending:
        for n in re.findall(r'!(\d+)',definitions[pending.pop()]):
            if n not in ids:ids.add(n);pending.append(n)
    attrs=set(re.findall(r'#(\d+)', '\n'.join(bodies)));wrappers=[]
    for index,name in enumerate(roots):
        if not emit_wrappers:continue
        w=[f'define void @psr_leaf_{index}(ptr %input,ptr %texture,ptr %output){{']
        for n in range(6):w += [f'%p{n}=getelementptr float,ptr %input,i64 {n}',f'%f{n}=load float,ptr %p{n}',f'%h{n}=fptrunc float %f{n} to half']
        w += ['%x0=insertelement <3 x half> poison,half %h0,i32 0','%x1=insertelement <3 x half> %x0,half %h1,i32 1','%x=insertelement <3 x half> %x1,half %h2,i32 2','%t=addrspacecast ptr %texture to ptr addrspace(1)']
        if short(name)in ['renderBGAdjustments','renderFGAdjustments']:
            w += ['%coeff=getelementptr float,ptr %input,i64 9','%coeff1=addrspacecast ptr %coeff to ptr addrspace(1)']
            if short(name)=='renderBGAdjustments':args='<3 x half> %x,half %h3,half undef,half %h4,ptr addrspace(1) %coeff1,ptr addrspace(1) %t'
            else:
                for i in range(3):w += [f'%sp{i}=getelementptr float,ptr %input,i64 {6+i}',f'%sf{i}=load float,ptr %sp{i}',f'%sh{i}=fptrunc float %sf{i} to half',f'%sv{i}=insertelement <3 x half> '+('poison'if i==0 else f'%sv{i-1}')+f',half %sh{i},i32 {i}']
                args='<3 x half> %x,<3 x half> %sv2,half %h4,half undef,half %h5,half %h3,ptr addrspace(1) %coeff1,ptr addrspace(1) %t'
        elif short(name)=='renderSelectiveColorAdjustments':
            w += ['%cp=getelementptr float,ptr %input,i64 7','%cast=addrspacecast ptr %cp to ptr addrspace(1)','%mp=getelementptr float,ptr %input,i64 6','%mf=load float,ptr %mp','%mh=fptrunc float %mf to half']
            args='<3 x half> %x,ptr addrspace(1) %cast,ptr addrspace(1) %t,half %h3,half %h4,half %h5,half %mh'
        elif short(name)=='renderWarmthCastAdjustments':
            w += ['%cp=getelementptr float,ptr %input,i64 4','%cast=addrspacecast ptr %cp to ptr addrspace(1)']
            args='<3 x half> %x,ptr addrspace(1) %cast,half %h3'
        elif short(name)=='renderNeutralizingAdjustments':
            w += ['%cp=getelementptr float,ptr %input,i64 10','%cast=addrspacecast ptr %cp to ptr addrspace(1)','%enabled=fcmp une float %f5,0.0','%up=getelementptr float,ptr %input,i64 6','%uf=load float,ptr %up','%use=fcmp une float %uf,0.0','%stats=alloca %struct.SSRStats,align 4','store %struct.SSRStats zeroinitializer,ptr %stats','%stats1=addrspacecast ptr %stats to ptr addrspace(1)']
            for i,group in enumerate([2,3,4]):w += [f'%stp{i}=getelementptr float,ptr %input,i64 {7+i}',f'%stf{i}=load float,ptr %stp{i}',f'%stg{i}=getelementptr %struct.SSRStats,ptr %stats,i64 0,i32 1,i64 {group},i32 4',f'store float %stf{i},ptr %stg{i}']
            args='<3 x half> %x,i1 %enabled,ptr addrspace(1) %cast,half %h3,half %h4,i1 %use,ptr addrspace(1) %stats1'
        elif short(name)in ['deRed','deYellow','deRedNeutralOnly','skinWarmthFilter']:
            for i in range(3):w += [f'%sp{i}=getelementptr float,ptr %input,i64 {6+i}',f'%sf{i}=load float,ptr %sp{i}',f'%sh{i}=fptrunc float %sf{i} to half',f'%sv{i}=insertelement <3 x half> '+('poison'if i==0 else f'%sv{i-1}')+f',half %sh{i},i32 {i}']
            if short(name)=='deRed':args='<3 x half> %x,half %h3,half %h5,<3 x half> %sv2,half %h4'
            elif short(name)=='deYellow':args='<3 x half> %x,half %h3,half undef,<3 x half> %sv2,half %h4'
            else:
                w += ['%up=getelementptr float,ptr %input,i64 9','%uf=load float,ptr %up','%uh=fptrunc float %uf to half']
                args='<3 x half> %x,half %h3,half %h5,<3 x half> %sv2,half %uh,half %h4'if short(name)=='skinWarmthFilter'else'<3 x half> %x,half %h3,half undef,<3 x half> %sv2,half %h4,half %h5,half %uh'
        elif short(name)=='renderBrightAndContrast':
            w += ['%stats=alloca %struct.SSRStats,align 4','store %struct.SSRStats zeroinitializer,ptr %stats','%stats1=addrspacecast ptr %stats to ptr addrspace(1)']
            for i,(group,field)in enumerate([(2,4),(3,4),(5,0),(6,6),(6,4)]):
                w += [f'%stp{i}=getelementptr float,ptr %input,i64 {9+i}',f'%stf{i}=load float,ptr %stp{i}',f'%stg{i}=getelementptr %struct.SSRStats,ptr %stats,i64 0,i32 1,i64 {group},i32 {field}',f'store float %stf{i},ptr %stg{i}']
            for i in range(3):w += [f'%sp{i}=getelementptr float,ptr %input,i64 {6+i}',f'%sf{i}=load float,ptr %sp{i}',f'%sh{i}=fptrunc float %sf{i} to half',f'%sv{i}=insertelement <3 x half> '+('poison'if i==0 else f'%sv{i-1}')+f',half %sh{i},i32 {i}']
            args='<3 x half> %x,<3 x half> %sv2,half %h3,half %h4,half %h5,ptr addrspace(1) %stats1'
        elif short(name)=='renderSkinAdjustments':
            w += ['%coeff=getelementptr float,ptr %input,i64 9','%coeff1=addrspacecast ptr %coeff to ptr addrspace(1)']
            args='<3 x half> %x,ptr addrspace(1) %coeff1,half %h5,half %h3'
        elif short(name)=='highlightRecover':args='<3 x half> %x,half %h3,half undef,half undef,half %h4'
        elif short(name)=='whitesCurve':args='<3 x half> %x,ptr addrspace(1) %t,half %h4,half %h5'
        elif short(name)in ['contrastFilter','airyFilter','smoothSatFilter']:args='<3 x half> %x,half %h4'
        elif short(name)=='RichSat':args='<3 x half> %x,half %h4,half undef,half %h5'
        else:args='<3 x half> %x,half %h3,half %h4'
        w += [f'%r=call fastcc <3 x half> @{name}({args})']
        for n in range(3):w += [f'%o{n}=extractelement <3 x half> %r,i32 {n}',f'%of{n}=fpext half %o{n} to float',f'%op{n}=getelementptr float,ptr %output,i64 {n}',f'store float %of{n},ptr %op{n}']
        w += ['ret void','}'];wrappers.append('\n'.join(w))
    globals_=re.findall(r'^@__air_sampler_state(?:\.\d+)? = .*$',source,re.M)
    llvm_used=set(re.findall(r'@(llvm\.[^ (]+)\(', '\n'.join(bodies)))
    llvm_decls=[re.sub(r' #\d+\s*$','',line)for line in source.splitlines()if line.startswith('declare ')and any('@'+name+'('in line for name in llvm_used)]
    text='\n'.join([*re.findall(r'^%[^\n]+ = type [^\n]+$',source,re.M),*globals_,*bodies,*llvm_decls,shims(used),*wrappers,*[re.search(r'^attributes #'+n+r' = .*$',source,re.M)[0]for n in attrs],*[f'!{n} = {definitions[n]}'for n in sorted(ids,key=int)]])+'\n'
    return text,{short(n):hashlib.sha256(functions[n].encode()).hexdigest()for n in selected}
