"""Freeze finite CI ROI controls; original method oracle, no images/PSOs."""
from pathlib import Path
import hashlib,json,os,subprocess,sys
D=Path('research/hdr-native');W=Path(os.environ['W']);O=W/'out'
assert subprocess.check_output(['sw_vers','-buildVersion'],text=True).strip()=='26A434'
parent=(D/'probe_consumer_bindings_s72.m').read_text();prefix=parent[:parent.index('int main(int argc,char**argv)')];(W/'consumer_cpu_prefix_s73.inc').write_text(prefix)
base=[[0,0,1024,768],[0,0,256,192],[0,0,32,24],[0,0,128,96],[0,0,64,48],[0,0,32,32],[0,0,256,1],[0,0,512,384],[0,0,256,192]]
shift=[[100,200,1024,768],[10,-20,256,192],[-5,8,32,24],[17,23,128,96],[-2,-3,64,48],[3,4,32,32],[50,60,256,1],[12,13,512,384],[14,15,256,192]]
cases=[{'id':'aligned_full','extents':base,'output':[0,0,1024,768]},{'id':'fractional_tile','extents':base,'output':[123.25,87.5,322.5,258.25]},{'id':'translated_extent_tile','extents':shift,'output':[223.25,287.5,322.5,258.25]}]
def reference(case,index):
    out=case['output'];src=case['extents'][0];dst=case['extents'][index]
    if index==0:return out[:]
    if 6<=index<=8:return dst[:]
    return [dst[0]+(out[0]-src[0])*dst[2]/src[2],dst[1]+(out[1]-src[1])*dst[3]/src[3],out[2]*dst[2]/src[2],out[3]*dst[3]/src[3]]
expected=[{'case':c['id'],'input_index':i,'useLightMap':light,'reference_ROI':reference(c,i)}for c in cases for light in [False,True]for i in range(9)]
freeze={'os_build':'26A434','image_version':os.environ.get('ImageVersion'),'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in[D/'probe_consumer_roi_s73.m',D/'probe_consumer_bindings_s72.m',D/'probe_headroom_s66.m',D/'run_hdr_s73.py']},'derived_prefix_sha256':hashlib.sha256(prefix.encode()).hexdigest(),'cases':cases,'expected':expected,'hypothesis_frozen_before_native':'index0 identity;6/7/8 entire source extent;1..5 proportional affine map of output between extent0 and extenti, no pixel clipping/roundout','CPU_ROI_max_abs_gate':1e-12,'legacy_pixel_thresholds_masks_unchanged':True,'no_photo_or_image_dispatch':True,'scope':'Finite CPU ROI controls only; actual CI allocated regions, sampler and full-domain33-point certificate remain separate','acceptance_complete':False}
with(O/'freeze.json').open('x')as f:json.dump(freeze,f,separators=(',',':'));f.write('\n')
with(W/'cases.json').open('x')as f:json.dump({'cases':cases},f,separators=(',',':'));f.write('\n')
with(O/'build.log').open('x')as log:subprocess.run(['clang','-I',str(D),'-I',str(W),'-O2','-fobjc-arc','-framework','Foundation','-framework','CoreFoundation','-framework','CoreImage','-framework','CoreGraphics',str(D/'probe_consumer_roi_s73.m'),'-o',str(W/'probe')],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240)
with(O/'native.log').open('x')as log:rc=subprocess.run([str(W/'probe'),str(W/'cases.json'),str(O/'native.json')],stdout=log,stderr=subprocess.STDOUT,timeout=240).returncode
native=json.loads((O/'native.json').read_text())if(O/'native.json').exists()else{}
analysis={'native_returncode':rc,'native_completed':native.get('completed',False),'rows':[],'gate':1e-12,'new_photos':0,'new_image_dispatches':0,'A_phase_complete':False,'acceptance_complete':False}
if rc==0:
    assert len(native['rows'])==len(expected)==54
    for a,b in zip(native['rows'],expected,strict=True):
        assert all(a[k]==b[k]for k in ['case','input_index','useLightMap'])
        analysis['rows'].append({**b,'native_ROI':a['native_ROI'],'max_abs':max(abs(x-y)for x,y in zip(a['native_ROI'],b['reference_ROI'],strict=True))})
    analysis['max_abs']=max(r['max_abs']for r in analysis['rows']);analysis['finite_CPU_ROI_model_gate_passed']=analysis['max_abs']<=1e-12
with(O/'analysis.json').open('x')as f:json.dump(analysis,f,separators=(',',':'));f.write('\n')
print(json.dumps({k:v for k,v in analysis.items()if k!='rows'}))
sys.exit(rc if rc else 0 if analysis['finite_CPU_ROI_model_gate_passed']else 1)
