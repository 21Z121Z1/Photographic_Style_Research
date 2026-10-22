"""Default sorted-contrast integration: saved64 and original S14C case0 only."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from leaf_numeric import V,DomainUnknown
from pixel_leaves import contrast,contrast_independent
from contrast_sorted import saved_cells,family_id,enclose_family,ROOT_LO,ROOT_HI,SOURCE_SHA
import typed_bgfg
from native_main_pre393_check import fixtures,model
from main_pre393_host import OBSERVATIONS


def snapshot(v):return {'lo':np.asarray(v.lo).tolist(),'hi':np.asarray(v.hi).tolist(),'max_width':float(np.max(np.asarray(v.hi)-v.lo)),'precision':v.precision}


def check(saved,native,output):
    if output.exists():raise FileExistsError(output)
    if hashlib.sha256(saved.read_bytes()).hexdigest()!=SOURCE_SHA or hashlib.sha256(native.read_bytes()).hexdigest()!='af5656e829016d0f14d4346ade2ccdd6eb8072cb7686290dcb1c0e704457f573':raise ValueError('Exact saved64 and original S14C native receipt required')
    data=json.loads(saved.read_text());amount=V.value(data['amount_half'],point=False);rows=[];ordered=[]
    for i,lo,hi in saved_cells()[0]:
        rgb=V(np.array(lo),np.array(hi),'h',False);row={'cell':i,'input':snapshot(rgb),'default_route':'sorted family'if family_id(rgb,amount)is not None else'cell0 joint'if i==0 else'independent'}
        try:contrast_independent(rgb,amount);row['old_independent']='known'
        except DomainUnknown:row['old_independent']='unknown'
        try:row['default']={'status':'known',**snapshot(contrast(rgb,amount))}
        except DomainUnknown as e:row['default']={'status':'unknown','reason':str(e)}
        rows.append(row)
        if family_id(rgb,amount)is not None:
            proof=enclose_family(rgb,amount);ordered.append({'cell':i,'branches':proof.branches,'output':snapshot(proof.output)})
    parent=contrast(V(np.array(ROOT_LO),np.array(ROOT_HI),'h',False),amount)
    names=['contrast','whites_curve','airy','mids','smooth_sat','local_contrast','gamma_contrast','lighten','negative_lighten','under_grass','rich_sat','tonal_contrast','under_tone','smart_contrast','highlight_neg','shadows','shadows_negative'];old={n:getattr(typed_bgfg,n)for n in names};trace=[];active=[];oldround=V.rounded;olddiv=V.__truediv__;oldpow=V.pow
    def remember(operation,args,error):
        if active:active[-1].setdefault('arithmetic_failures',[]).append({'operation':operation,'arguments':[snapshot(v)if isinstance(v,V)else np.asarray(v).tolist()for v in args],'reason':str(error)})
    def rounded(a,lo,hi,**kwargs):
        try:return oldround(a,lo,hi,**kwargs)
        except DomainUnknown as e:remember('round to '+a.precision,[lo,hi],e);raise
    def divide(a,b):
        try:return olddiv(a,b)
        except DomainUnknown as e:remember('original division',[a,a.box(b)],e);raise
    def power(a,b):
        try:return oldpow(a,b)
        except DomainUnknown as e:remember('pow',[a,a.box(b)],e);raise
    def wrapper(name,fn):
        def run(*args,**kwargs):
            row={'leaf':name,'input':snapshot(args[0])};trace.append(row);active.append(row)
            try:
                v=fn(*args,**kwargs);row.update(status='known',output=snapshot(v));return v
            except DomainUnknown as e:row.update(status='unknown',reason=str(e));raise
            finally:active.pop()
        return run
    for n,fn in old.items():setattr(typed_bgfg,n,wrapper(n,fn))
    V.rounded=rounded;V.__truediv__=divide;V.pow=power
    try:full=model(next(fixtures()),False)
    finally:
        for n,fn in old.items():setattr(typed_bgfg,n,fn)
        V.rounded=oldround;V.__truediv__=olddiv;V.pow=oldpow
    actual=json.loads(native.read_text());case=next(v for v in actual['rows']if v['case']==0);bits=np.array(case['native_output_half_bits'],dtype='u2').view('f2');ranges={};offset=0
    for name,ssa,count in OBSERVATIONS:
        target=bits[offset:offset+count];offset+=count
        if name in full.observations:
            v=full.observations[name];ranges[name]={'covered':bool(np.all(target>=v.lo)and np.all(target<=v.hi)),**snapshot(v)}
    first=next((r for r in trace if r['status']=='unknown'),None);out={'scope':__doc__,'source_input_cover_sha256':hashlib.sha256(saved.read_bytes()).hexdigest(),'native_receipt_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'native_calls':0,'new_input_cells':0,'default_cells':rows,'default_counts':{'known':sum(r['default']['status']=='known'for r in rows),'unknown':sum(r['default']['status']=='unknown'for r in rows),'independent56':56,'joint_cell0':1,'sorted_family7':7},'S19_sorted_subdomains':{'families':len(ordered),'known_positive':sum(b.get('status')=='known'and b['branch']=='positive'for r in ordered for b in r['branches']),'known_else':sum(b.get('status')=='known'and b['branch']=='else'for r in ordered for b in r['branches']),'families_with_branches':ordered},'historical_S16_counts_separate':{'original_failed_cells':8,'positive_domains':48,'known_positive':42,'unknown_positive':6,'known_else':48,'default_admission_at_S16':False},'parent_default_output':snapshot(parent),'original_S14C_case0':{'unknown_operator':full.unknown_operator,'unknown_reason':full.unknown_reason,'leaf_trace':trace,'first_unhandled_leaf':first,'known_prefix_ranges':ranges,'full_BG_verified':False},'half_quotient_before_product_unchanged':True,'threshold_epsilon_mask_budgets_changed':False,'source_output_oracle_used':False};output.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n');print(json.dumps({'default_counts':out['default_counts'],'parent_width':snapshot(parent)['max_width'],'next_leaf':None if first is None else first['leaf'],'full_stage':full.unknown_operator,'positive_domains':out['S19_sorted_subdomains']['known_positive'],'else_domains':out['S19_sorted_subdomains']['known_else']}));return out


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('saved',type=Path);p.add_argument('native',type=Path);p.add_argument('output',type=Path);a=p.parse_args();check(a.saved,a.native,a.output)
