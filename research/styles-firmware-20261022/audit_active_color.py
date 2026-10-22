"""Targeted original SSRParams pointer/dataflow audit for one color family."""
import argparse,hashlib,json,re
from pathlib import Path
import numpy as np
from active_color import Color,replace_color,half_cell
from complete_fixture import decode,encode
from native_semantic_tone_check import fragment
from air7_full_host import build as producer_build
from select_active_color import CONTEXT_SHA


def functions(text):return {m[1]:m[0]for m in re.finditer(r'^define[^\n]*@([^ (]+)\([^\n]+\{\n.*?^}',text,re.M|re.S)}
def uses(body,token):return [l for l in body.splitlines()[1:]if re.search(re.escape(token)+r'(?!\d)',l)]
def sha(b):return hashlib.sha256(b).hexdigest()


def check(source_dir,basefile,screenfile,output,context_output):
    if output.exists()or context_output.exists():raise FileExistsError('Do not overwrite evidence')
    main_text=(source_dir/'0010.ll.txt').read_text();fragment(main_text);prod_text=(source_dir/'0007.ll.txt').read_text();_,producer_identity=producer_build(prod_text);fs=functions(main_text);main=fs['renderFinalAdjustments'];ps=functions(prod_text)['createLTMGainMap'];rows=[]
    scopes=[('main','renderFinalAdjustments','%17',{477,493,567}),('producer','createLTMGainMap','%9',set())]
    for needle,arg in [('renderBWAdjustmentsByCastType','%4'),('renderVideoHazeCorrection','%2'),('renderChannelMixForBWCasts','%2'),('getBWChannelMixFromStats','%1')]:scopes.append(('helper',next(n for n in fs if needle in n),arg,{20,45}if needle=='renderChannelMixForBWCasts'else set()))
    for role,name,arg,calls in scopes:
        body=ps if role=='producer'else fs[name];fields=[];forward_calls=[]
        for line in uses(body,arg):
            m=re.fullmatch(r'  %(\d+) = getelementptr inbounds %struct.SSRParams, ptr addrspace\(1\) '+re.escape(arg)+r', i64 0, i32 (\d+)(?:, i32 \d+)?',line)
            if m:fields.append({'SSA':int(m[1]),'field':int(m[2]),'instruction_sha256':sha(line.encode())})
            else:
                m=re.match(r'  %(\d+) = tail call .*@([^ (]+)\(',line)
                if not m or int(m[1])not in calls:raise ValueError('Untracked raw SSRParams pointer alias/escape')
                forward_calls.append({'SSA':int(m[1]),'callee':m[2],'instruction_sha256':sha(line.encode())})
        color_geps=[v for v in fields if v['field']==3]
        if role=='main':
            if [v['SSA']for v in color_geps]!=[355]or len(forward_calls)!=3:raise ValueError('Main color entry changed')
        elif color_geps or len(forward_calls)!=len(calls):raise ValueError('Other raw pointer path reads color/escapes')
        rows.append({'role':role,'function':name,'raw_params_argument':arg,'function_sha256':sha(body.encode()),'fields':fields,'forwarded_full_params_calls':forward_calls})
    if len(uses(main,'%355'))!=2 or len(uses(main,'%356'))!=2:raise ValueError('Unexpected raw color pointer/load users')
    patterns={355:'%355 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 3',356:'%356 = load float, ptr addrspace(1) %355',357:'%357 = fptrunc float %356 to half',361:'%361 = fmul fast half %357, %357',364:'%364 = fadd fast half %363, 0xH3C00',365:'%365 = fcmp fast ogt half %357, 0xH0000',376:'%376 = fadd fast float %358, 0xBFE3333340000000',377:'%377 = tail call fast float @air.fast_fmax.f32(float %376, float 0x3FC99999A0000000)',384:'%384 = fptrunc float %383 to half'}
    instruction_checks={str(i):any(l.strip().startswith(pattern)for l in main.splitlines())for i,pattern in patterns.items()}
    if not all(instruction_checks.values()):raise ValueError('Color gain/protection precision contract changed')
    if sha(basefile.read_bytes())!=CONTEXT_SHA:raise ValueError('Frozen raw base required')
    screen=json.loads(screenfile.read_text());base=decode(json.loads(basefile.read_text()));values=[np.float32(0)]+[np.float32(v)for v in screen['selected_host_values']]
    if len(values)!=5 or len(set(int(v.view('u4'))for v in values))!=5:raise ValueError('Exactly baseline plus four screened host values')
    contexts=[]
    for v in values:
        control=Color(v);c=replace_color(base,control);changed=np.flatnonzero(c.params.view('u4')!=base.params.view('u4')).tolist()
        if changed not in ([],[3]):raise AssertionError('Multiple active raw fields')
        contexts.append({'control':control.record(),'changed_raw_fields':changed,'context':encode(c)})
    ctx={'scope':'five explicit paired raw contexts, same frozen source/auxiliary inputs; only post-scene raw color byte12 varies','base_context_sha256':CONTEXT_SHA,'screen_sha256':sha(screenfile.read_bytes()),'rows':contexts,'intermediate_outputs_supplied':False}
    context_output.write_text(json.dumps(ctx,indent=2,allow_nan=False)+'\n')
    low,high=np.float16(.01),np.float16(.02);square_high=np.float16(high*high);gain_midpoint=1+2**-11
    plateau={'raw_f32_closed_interval':[float(np.float32(.01)),float(np.float32(.02))],'half_color_bounds':[float(low),float(high)],'maximum_rounded_square':float(square_high),'one_plus_square_upper':1+float(square_high),'half_one_next_midpoint':gain_midpoint,'strictly_below_midpoint':1+float(square_high)<gain_midpoint,'positive_branch_for_whole_interval':True,'protection_f32_max_selects_constant_point2':float(high)-.6<.2,'gain364_bits':int(np.float16(1).view('u2')),'status':'conditional original instruction/IEEE interface equivalence; host witnesses below; original GPU unverified'}
    out={'scope':__doc__,'hardware':'iPhone17,3','build':'24A446','control':'SSRParams field3 byte12, post-scene f32; no UI mapping','original_pointer_paths':rows,'precision_checks':instruction_checks,'raw356_only_value_user':'fptrunc357; pointer355 only load356','producer_identity':producer_identity,'half_bin':half_cell(Color(np.float32(.3))),'plateau':plateau,'context_file_sha256':sha(context_output.read_bytes()),'context_count':5,'same_other_raw_inputs':True,'all_checks_pass':True,'new_native_calls':0,'GPU_verified':False,'scope_limit':'exact AIR7/AIR10 SSRParams roots, three full-buffer callees and nested BW stats callee; nine unresolved coefficient consumers remain unresolved'}
    output.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n');print(json.dumps({'pointer_paths':len(rows),'contexts':5,'plateau':plateau,'half_cell_values':out['half_bin']['f32_values']}));return out


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source_dir',type=Path);p.add_argument('base',type=Path);p.add_argument('screen',type=Path);p.add_argument('output',type=Path);p.add_argument('contexts',type=Path);a=p.parse_args();check(a.source_dir,a.base,a.screen,a.output,a.contexts)
