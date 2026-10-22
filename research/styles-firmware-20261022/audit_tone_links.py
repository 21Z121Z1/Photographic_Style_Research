"""Bounded AIR11 store/schema and selected consumer read-site audit.

Records branch-filtered SSA data dependencies, not a general control-flow or
whole-pipeline proof. Private AIR text is read, never copied to the repository.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
from air_alpha import canonicalize
from tone_interface import BG_NAMES,FG_NAMES,SEM_NAMES

GROUPS={13:('bg','SSRBGAdjustment',BG_NAMES,488),14:('fg','SSRFGAdjustment',FG_NAMES,556),15:('semantic','SSRSemanticToneAdjustment',SEM_NAMES,620)}
SHA=lambda text:hashlib.sha256(text.encode()).hexdigest()


def store_dependencies(text: str,positive: bool) -> dict:
    defs=dict(re.findall(r'^\s*(%\d+) = (.*)$',text,re.M));branches={'124':'226','267':'339','419':'527'}
    def dependencies(value: str,seen=frozenset()):
        if not re.fullmatch(r'%\d+',value):return set()
        if value in seen:raise ValueError('Unexpected cyclic SSA in bounded coefficient function')
        line=defs[value];seen=seen|{value}
        if line.startswith('load '):
            pointer=re.search(r'ptr addrspace\(1\) (%\d+)',line)[1];gep=defs[pointer]
            root=re.search(r'getelementptr inbounds %struct\.(SSRParams|SSRStats),',gep)
            if not root:raise ValueError('Unexpected coefficient input pointer')
            # First i64 is struct-array index; retain subsequent fixed indices.
            tail=gep.split(', i64 ',1)[1].split(',',1)[1]
            indices=re.findall(r'i(?:32|64) (\d+)',tail)
            return {root[1]+''.join(f'[{i}]'for i in indices)}
        if line.startswith('phi '):
            incoming=re.findall(r'\[ ([^,\]]+), %(\d+) \]',line)
            labels={b for _,b in incoming}
            for negative_label,positive_label in branches.items():
                if negative_label in labels and positive_label in labels:
                    incoming=[x for x in incoming if x[1]==(positive_label if positive else negative_label)];break
            operands=[v.strip()for v,_ in incoming]
        else:operands=re.findall(r'%\d+',line)
        result=set()
        for operand in operands:result|=dependencies(operand,seen)
        return result
    rows={}
    for pointer,line in defs.items():
        m=re.search(r'getelementptr inbounds %struct\.SSRParams,.*?, i32 (13|14|15), i32 (\d+)$',line)
        if not m:continue
        store=re.search(r'^\s*store float ([^,]+), ptr addrspace\(1\) '+re.escape(pointer)+r',',text,re.M)
        if not store:raise ValueError('Every coefficient pointer must have its store')
        rows[(int(m[1]),int(m[2]))]={'store_pointer_SSA':pointer,'stored_value_SSA_or_literal':store[1],
                                       'data_dependencies':sorted(dependencies(store[1]))}
    if len(rows)!=40:raise ValueError('Expected exactly 40 coefficient stores')
    return rows


def audit(producer: Path,consumer: Path,output: Path):
    if output.exists():raise FileExistsError(output)
    root=Path(__file__).resolve().parent;source=producer.read_text();target=consumer.read_text()
    canonical=SHA(canonicalize(source)[0]);expected=json.loads((root/'evidence/render-params-air.json').read_text())
    if canonical!=expected['canonical_sha256']:raise ValueError('Exact source AIR11 required')
    comparison=json.loads((root/'evidence/cmi-air-alpha.json').read_text())
    cmi10=next(x for x in comparison['module_pairs']if x['ios_index']==10)
    target_canonical=SHA(canonicalize(target)[0])
    if target_canonical!=cmi10['ios_canonical_sha256']:raise ValueError('Exact selected consumer AIR10 required')
    for meta,names in [(24,BG_NAMES),(25,FG_NAMES),(26,SEM_NAMES)]:
        line=re.search(r'^!'+str(meta)+r' = (.*)$',source,re.M)[1]
        actual=tuple(re.findall(r'!"float", !"([^\"]+)"',line))
        if actual!=names:raise ValueError('Consumer field schema/name drift')
    positive=store_dependencies(source,True);negative=store_dependencies(source,False);read_sites={k:[]for k in positive};functions=[]
    by_struct={v[1]:k for k,v in GROUPS.items()}
    for f in re.finditer(r'^define[^\n]*?@("[^\"]+"|[^ (]+)\([^\n]+\{\n',target,re.M):
        end=target.index('\n}',f.end())+2;body=target[f.start():end];sites=[];first_line=target[:f.start()].count('\n')+1
        for line_index,line in enumerate(body.splitlines()):
            m=re.search(r'getelementptr inbounds %struct\.(SSRBGAdjustment|SSRFGAdjustment|SSRSemanticToneAdjustment),.*?, i64 0, i32 (\d+)',line)
            if m:key=(by_struct[m[1]],int(m[2]))
            else:
                m=re.search(r'getelementptr inbounds %struct\.SSRParams,.*?, i64 0, i32 (13|14|15), i32 (\d+)',line)
                if not m:continue
                key=tuple(map(int,m.groups()))
            site={'function':f[1],'line':first_line+line_index,'pointer_SSA':line.split('=',1)[0].strip()}
            read_sites[key].append(site);sites.append(site)
        if sites:
            callees=set()
            for symbol in re.findall(r'@([^ (]+)\(',body.split('\n',1)[1]):
                short=re.match(r'_Z(\d+)',symbol)
                if short:callees.add(symbol[short.end():short.end()+int(short[1])])
            functions.append({'name':f[1],'first_line':first_line,'last_line':first_line+len(body.splitlines())-1,'function_text_sha256':SHA(body),'direct_named_callees':sorted(callees)})
    fields=[]
    for group,(block,struct,names,offset)in GROUPS.items():
        for index,name in enumerate(names):
            key=(group,index);reused=group==14 and index in (9,10)
            fields.append({'name':f'{block}.{name}','struct':struct,'field':index,'byte_offset':offset+index*4,
                           'positive_coverage':'accepted S6 reused'if reused else 'new S8 coefficient model/host comparison',
                           'negative_coverage':'accepted S7 reused','positive':positive[key],'negative':negative[key],
                           'selected_consumer_read_sites':read_sites[key],
                           'independent_pixel_model':'existing semantic_skin_model.forward'if reused else 'not established by coefficient/interface tests'})
    r={'scope':__doc__,'hardware_reference':'iPhone17,3','build':'24A446','producer_AIR_canonical_sha256':canonical,'consumer_AIR_canonical_sha256':target_canonical,
       'producer_text_sha256':SHA(source),'consumer_text_sha256':SHA(target),'auditor_sha256':SHA(Path(__file__).read_text()),'fields':fields,'consumer_functions':functions,
       'counts':{'fields':40,'new_positive_fields':38,'reused_positive_fields':2,'reused_negative_fields':40,'fields_with_read_site_in_selected_consumer':sum(bool(x['selected_consumer_read_sites'])for x in fields)},
       'control_dependencies_not_in_data_SSA_sets':{'bg':['SSRParams[17] tuningType','SSRParams[2] tone sign','scene4 thresholds select brightness path'],
                                                   'fg':['SSRParams[0] castType','tone sign and .4/.5/tone^.75=.5 comparisons'],
                                                   'semantic':['tone sign','min/max/clamp choices']},
       'scene_scaling':{'source_method':'evidence/render-follow-24A446/render-static-parameters.asm.txt','block_start':'0x1d42f2328','block_end_exclusive':'0x1d42f236c',
                        'sceneType_byte_offset':32,'tuningType_byte_offset':652,'distinct_fields':True,
                        'scene_resolver_symbol_locator':'0x1d42f3ce4 _SSRSceneTypeEnumFromSemanticStyleSceneType',
                        'tuning_resolver_symbol_locator':'0x1d42f3a68 _SSRTuningTypeEnumFromString',
                        'resolver_implementations_modeled':False,
                        'resolved_scene_3_tone_color_intensity_tuning_indices':[59,60,61],
                        'resolved_scene_21_tone_color_intensity_tuning_indices':[62,63,64],
                        'other_scene_codes':'identity in selected block','clamp_in_selected_block':False},
       'unresolved_selected_read_fields':[x['name']for x in fields if not x['selected_consumer_read_sites']],
       'unmodeled_pixel_operators':[
           {'helper':'renderBGAdjustments','source_lines':[5589,5873],'status':'independent numeric pixel model not established','dependencies':['working RGB','curve texture','guide/luma inputs','half/fast arithmetic']},
           {'helper':'renderFGAdjustments','source_lines':[4590,4813],'status':'independent numeric pixel model not established','dependencies':['working RGB','original/background RGB','person/skin masks','guide','curve texture','half/fast arithmetic']},
           {'helper':'renderSemanticToneAdjustments','source_lines':[5976,6093],'status':'full pixel consumer not modeled; supplied-curve inverse utilities alone do not establish this helper','dependencies':['GTC texture/sampler','BG/FG exposure and LTM/HR coefficients','person weights','half arithmetic']},
           {'helper':'renderFinalAdjustments','source_lines':[54,737],'status':'outer sampling/color transforms/order/gates not a composed pixel model','dependencies':['actual bindings/function constants','working color/storage domain','matte/guide alignment']}],
       'iOS_or_GPU_execution':False,'full_pixel_pipeline_verified':False,'raw_AIR_uploaded':False}
    output.write_text(json.dumps(r,indent=2)+'\n');return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('producer',type=Path);p.add_argument('consumer',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args();r=audit(a.producer,a.consumer,a.output);print(json.dumps(r['counts']))
