"""Fresh field3 dependency contract from the NEW persisted host IR files.

No historical module equality is inferred. Output contains contracts and hashes,
never proprietary IR text. Unrecognized raw-parameter aliases fail closed.
"""
import hashlib,re
from pathlib import Path


def functions(text):return {m[1]:m[0]for m in re.finditer(r'^define[^\n]*@([^ (]+)\([^\n]+\{\n.*?^}',text,re.M|re.S)}
def sha(text):return hashlib.sha256(text.encode()).hexdigest()
def uses(body,token):return [line for line in body.splitlines()[1:]if re.search(re.escape(token)+r'(?![A-Za-z0-9_])',line)]


def raw_scope(body,arg,*,allowed_calls=()):
    fields=[];calls=[]
    for line in uses(body,arg):
        m=re.fullmatch(r'  %(\d+) = getelementptr inbounds %struct.SSRParams, ptr addrspace\(1\) '+re.escape(arg)+r', i64 0, i32 (\d+)(?:, i32 (\d+))?',line)
        if m:fields.append({'SSA':int(m[1]),'field':int(m[2]),'subfield':None if m[3]is None else int(m[3]),'instruction_sha256':sha(line)})
        else:
            m=re.match(r'  %(\d+) = tail call .*@([^ (]+)\(',line)
            if not m or int(m[1])not in allowed_calls:raise ValueError('Untracked raw SSRParams pointer alias/escape')
            calls.append({'SSA':int(m[1]),'callee':m[2],'instruction_sha256':sha(line)})
    if len(calls)!=len(allowed_calls):raise ValueError('Missing expected full-parameter call')
    return {'function_sha256':sha(body),'raw_params_argument':arg,'fields':fields,'forwarded_full_buffer_calls':calls}


def observation_only(body,line,value):
    m=re.fullmatch(r'%(obs_f\d+)\s*=fpext half '+re.escape(value)+r' to float',line.strip())
    if not m:return False
    name='%'+m[1];suffix=m[1][5:];dest='%obs_p'+suffix;matches=uses(body,name)
    return len(matches)==2 and len(uses(body,dest))==2 and any(re.fullmatch(r'store float '+re.escape(name)+r',ptr '+re.escape(dest),x.strip())for x in matches)and any(re.fullmatch(re.escape(dest)+r'\s*=getelementptr float,ptr %observations,i64 '+suffix,x.strip())for x in body.splitlines())


def value_users(body,value,allowed):
    result=[]
    for line in uses(body,value):
        m=re.match(r'\s*(%[A-Za-z0-9_]+)\s*=',line)
        if m and m[1]==value:continue
        if m and m[1]in allowed:result.append({'SSA':m[1],'kind':'logical control','instruction_sha256':sha(line)})
        elif observation_only(body,line,value):result.append({'SSA':m[1],'kind':'isolated observation store','instruction_sha256':sha(line)})
        else:raise ValueError('Extra field3-derived data consumer')
    if {r['SSA']for r in result if r['kind']=='logical control'}!=set(allowed):raise ValueError('Expected field3 consumers absent')
    return result


def main_contract(text):
    fs=functions(text);main=fs['psrMainFull'];scopes=[('psrMainFull','%17',{477,493,567})]
    for needle,arg in [('renderBWAdjustmentsByCastType','%4'),('renderVideoHazeCorrection','%2'),('renderChannelMixForBWCasts','%2'),('getBWChannelMixFromStats','%1')]:scopes.append((next(n for n in fs if needle in n),arg,{20,45}if needle=='renderChannelMixForBWCasts'else set()))
    rows=[]
    for name,arg,calls in scopes:
        row=raw_scope(fs[name],arg,allowed_calls=calls);color=[r for r in row['fields']if r['field']==3]
        if (name=='psrMainFull'and [r['SSA']for r in color]!=[355])or(name!='psrMainFull'and color):raise ValueError('Unexpected field3 access')
        rows.append(dict(row,function=name))
    required={355:'%355 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 3',356:'%356 = load float, ptr addrspace(1) %355',357:'%357 = fptrunc float %356 to half',358:'%358 = fpext half %357 to float',361:'%361 = fmul fast half %357, %357',364:'%364 = fadd fast half %363, 0xH3C00',365:'%365 = fcmp fast ogt half %357, 0xH0000',376:'%376 = fadd fast float %358, 0xBFE3333340000000',377:'%377 = tail call fast float @air.fast_fmax.f32(float %376, float 0x3FC99999A0000000)',384:'%384 = fptrunc float %383 to half'}
    checks={str(i):any(l.strip().startswith(p)for l in main.splitlines())for i,p in required.items()}
    if not all(checks.values())or len(uses(main,'%355'))!=2:raise ValueError('Actual main color precision/load contract changed')
    users={'raw356':value_users(main,'%356',{'%357'}),'half357':value_users(main,'%357',{'%358','%359','%361','%365'}),'extended358':value_users(main,'%358',{'%360','%376','%379'})}
    wrapper=fs['psr_main_full']
    if len(uses(wrapper,'%params'))!=1 or len(uses(wrapper,'%params1'))!=2 or 'addrspacecast ptr %params to ptr addrspace(1)'not in wrapper:raise ValueError('Actual main wrapper parameter ABI changed')
    return {'file_sha256':sha(text),'raw_pointer_scopes':rows,'field3_precision_checks':checks,'derived_consumers':users,'wrapper_function_sha256':sha(wrapper),'control_contract':'sole raw field3 load ->half357 ->branch/gain364/protect384; observer conversions are checked sinks','historical_module_equality_assumed':False}


def check(files):
    producer=Path(files['producer']).read_text();fs=functions(producer);body=fs['createLTMGainMap'];row=raw_scope(body,'%9')
    if [(r['field'],r['subfield'])for r in row['fields']]!=[(6,None),(15,4),(15,3),(15,2)]:raise ValueError('Producer raw parameter dependency changed')
    for entry in row['fields']:
        p='%'+str(entry['SSA']);lines=uses(body,p)
        if len(lines)!=2 or not any(re.search(r'= load float, ptr addrspace\(1\) '+re.escape(p)+r',',line)for line in lines):raise ValueError('Producer member pointer escapes scalar load')
    wrapper=fs['psr_produce']
    if len(uses(wrapper,'%params'))!=1 or len(uses(wrapper,'%params1'))!=2 or 'addrspacecast ptr %params to ptr addrspace(1)'not in wrapper:raise ValueError('Producer wrapper parameter ABI changed')
    guided=[]
    for i,path in enumerate(files['guided']):
        text=Path(path).read_text();f=functions(text);w=f['psr_guided_'+str(i)]
        if '%params'in w or '%struct.SSRParams'in w:raise ValueError('Guided wrapper unexpectedly depends on raw params')
        guided.append({'file_sha256':sha(text),'wrapper_sha256':sha(w),'raw_color_parameter_binding':False})
    for text in [producer,Path(files['main']).read_text(),Path(files['plain']).read_text()]:
        if '%struct.SSRParams = type { i32, float, float, float,'not in text:raise ValueError('Field3 byte12 layout prefix changed')
    result={'scope':__doc__,'producer':dict(row,file_sha256=sha(producer),wrapper_function_sha256=sha(wrapper),raw_field3_read=False),'guided':guided,'observed_main':main_contract(Path(files['main']).read_text()),'plain_main':main_contract(Path(files['plain']).read_text()),'field3_byte_offset':12,'prefix_reuse_permitted_for_fixed_other_inputs':True,'actual_persisted_files_audited':True,'all_checks_pass':True,'historical_whole_module_equality':False,'GPU_or_UI_mapping_verified':False}
    return result
