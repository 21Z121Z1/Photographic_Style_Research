"""Read small synthetic artifacts on runner, including partial/failed runs."""
from pathlib import Path
import hashlib,json,math,struct

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def values(root,item):
    raw=(root/item['file']).read_bytes();assert hashlib.sha256(raw).hexdigest()==item['sha256']
    code='e'if item['dtype']=='<f2'else'f'if item['dtype']=='<f4'else None
    assert code is not None
    return [x[0]for x in struct.iter_unpack('<'+code,raw)]
def population(v,channels=4):
    finite=[x for x in v if math.isfinite(x)]
    rgb=[x for i,x in enumerate(v)if i%channels<3]
    return {'components':len(v),'nonfinite':len(v)-len(finite),'finite_min':min(finite)if finite else None,'finite_max':max(finite)if finite else None,'nonzero':sum(x!=0 for x in v),'RGB_nonzero':sum(x!=0 for x in rgb),'all_bytes_numerically_zero':all(x==0 for x in v)}
def metrics(a,b):
    assert len(a)==len(b)
    if not all(math.isfinite(x)and math.isfinite(y)for x,y in zip(a,b)):return {'finite':False,'max_abs':None,'PSNR_dB':None}
    maximum=max(abs(x-y)for x,y in zip(a,b));mse=sum((x-y)**2 for x,y in zip(a,b))/len(a)
    return {'finite':True,'max_abs':maximum,'PSNR_dB':'Infinity'if mse==0 else -10*math.log10(mse)}
def analyze(root):
    root=Path(root);doc=json.loads((root/'native.json').read_text());cases=doc.get('cases',[]);callbacks=doc.get('callbacks',[])
    out={'native_completed':doc.get('completed',False),'exception_reason':doc.get('exception_reason'),'original_return_values':[{'case':r['case'],'value':r.get('original_return')}for r in callbacks],'cases_completed':len(cases),'callback_count':len(callbacks),'dispatch_count':len(doc.get('dispatches',[])),'all_source_SHA_unchanged':all(r['source_RGBAf_SHA_unchanged']for r in cases),'populations':[],'A_to_A':[],'A_phase_complete':False,'acceptance_complete':False,'native_return_YES_is_not_a_pixel_acceptance':True}
    for r in callbacks:
        item=r.get('output_readback',{})
        if'file'in item:out['populations'].append({'case':r['case'],'buffer':'original_MTL_output',**population(values(root,item),item['shape'][-1])})
    lookup={r['case']:r for r in cases}
    for r in cases:
        out['populations'].append({'case':r['case'],'buffer':'CI_RGBAf_output',**population(values(root,r['CI_output']))})
        if not r['case'].endswith('_r0'):continue
        key=r['case'][:-3]+'_r1'
        if key not in lookup:continue
        other=lookup[key];a=callbacks[slice(*r['callback_range'])];b=callbacks[slice(*other['callback_range'])]
        out['A_to_A'].append({'case':r['case'][:-3],**metrics(values(root,r['CI_output']),values(root,other['CI_output'])),'original_half_byte_exact':len(a)==len(b)and all(x.get('output_readback',{}).get('sha256')==y.get('output_readback',{}).get('sha256')and x.get('output_readback',{}).get('dtype')=='<f2'for x,y in zip(a,b))})
    statuses=doc.get('original_status_methods',[])
    out['status_returns']=[{k:r.get(k)for k in['case','call_index','selector','original_return_i32','original_exception']}for r in statuses]
    out['nonzero_status_returns']=[r for r in out['status_returns']if r.get('original_return_i32')not in[None,0]]
    functions={}
    for r in doc.get('dispatches',[]):
        key=r.get('PSO',{}).get('original_creation',{}).get('function_name','unresolved')
        functions[key]=functions.get(key,0)+1
    out['dispatches_by_original_function']=functions
    out['renderFinalAdjustments_dispatches_observed']=sum(n for key,n in functions.items()if key=='renderFinalAdjustments')
    out['diagnostic_nonconstant_RGB_present']=any(r['RGB_nonzero']>0 for r in out['populations']if r['buffer']=='original_MTL_output')
    out['full_domain_C01_C05_certified']=False
    return out
