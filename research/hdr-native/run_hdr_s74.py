"""Freeze source-derived integer ROI model after literal-only read, before controls."""
from pathlib import Path
import hashlib,json,math,os,subprocess,sys
D=Path('research/hdr-native');W=Path(os.environ['W']);O=W/'out'
assert subprocess.check_output(['sw_vers','-buildVersion'],text=True).strip()=='26A434'
def save(name,value):
    with(O/name).open('x')as f:json.dump(value,f,separators=(',',':'));f.write('\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
parent=(D/'probe_consumer_bindings_s72.m').read_text();prefix=parent[:parent.index('int main(int argc,char**argv)')]
(W/'consumer_cpu_prefix_s73.inc').write_text(prefix)
parent=(D/'probe_consumer_roi_s73.m').read_text();prefix74=parent[:parent.index('int main(int argc,char**argv)')]
(W/'consumer_cpu_prefix_s74.inc').write_text(prefix74)
recipe={'os_build':'26A434','image_version':os.environ.get('ImageVersion'),'source_sha256':{p.name:sha(p)for p in[D/'probe_consumer_pixelrect_s74.m',D/'run_hdr_s74.py',D/'probe_consumer_roi_s73.m',D/'probe_consumer_bindings_s72.m',D/'probe_headroom_s66.m']},'derived_prefix_sha256':sha(W/'consumer_cpu_prefix_s73.inc'),'derived_prefix74_sha256':sha(W/'consumer_cpu_prefix_s74.inc'),'frozen_before_any_native_execution':'Policy0: floor(min+C_a),ceil(max+C_b); x,y,w=hi_x-lo_x,h=hi_y-lo_y. Positive scaling separately multiplies integer origin and size, adds to form max, repeats policy0. Flip: x=minX(r)-minX(bounds), y=maxY(bounds)-maxY(r), width/height unchanged. C_a/C_b are unguessed original literal bits.','fixture_recipe':'5 positive-size integer/fractional/translated rects x6 positive scales; 2 axes x2 bound kinds x2 integers x3 nextafter neighbors around original constants.','integer_gate':'all four signed int64 fields identical, no tolerance','finite_CGRect_gate':1e-12,'scope':'finite positive-size,positive-scale CPU primitives; not CI allocation/sampler/full declared domain/pixel or camera proof','legacy_pixel_masks_thresholds_unchanged':True,'A_phase_complete':False,'acceptance_complete':False}
save('recipe.json',recipe)
with(O/'build.log').open('x')as log:
    subprocess.run(['clang','-I',str(D),'-I',str(W),'-O2','-fobjc-arc','-framework','Foundation','-framework','CoreFoundation','-framework','CoreImage','-framework','CoreGraphics',str(D/'probe_consumer_pixelrect_s74.m'),'-o',str(W/'probe')],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240)
with(O/'metadata.log').open('x')as log:
    rc=subprocess.run([str(W/'probe'),'metadata','unused',str(O/'metadata.json')],stdout=log,stderr=subprocess.STDOUT,timeout=240).returncode
if rc:sys.exit(rc)
meta=json.loads((O/'metadata.json').read_text());assert meta['completed']and meta['primitive_calls']==0
ca,cb=(row['value']for row in meta['metadata']['rounding_literals'])
assert math.isfinite(ca)and math.isfinite(cb)and abs(ca)<.1 and abs(cb)<.1
def outward(r):
    x,y,w,h=r;lo_x,lo_y=math.floor(x+ca),math.floor(y+ca)
    hi_x,hi_y=math.ceil((x+w)+cb),math.ceil((y+h)+cb)
    return[lo_x,lo_y,hi_x-lo_x,hi_y-lo_y]
def reference(c):
    a=outward(c['rect']);sx,sy=c['scale'];x,y,w,h=a
    left,top=float(x)*sx,float(y)*sy;right,bottom=left+float(w)*sx,top+float(h)*sy
    lo_x,lo_y=math.floor(left+ca),math.floor(top+ca);hi_x,hi_y=math.ceil(right+cb),math.ceil(bottom+cb)
    b=[lo_x,lo_y,hi_x-lo_x,hi_y-lo_y];bx,by,bw,bh=map(float,b);rx,ry,rw,rh=c['bounds']
    return{'case':c['id'],'from_pixel_rect':a,'from_CGRect':list(map(float,a)),'scaled_pixel_rect':b,'scaled_CGRect':list(map(float,b)),'flipped_CGRect':[bx-rx,(ry+rh)-(by+bh),bw,bh]}
cases=[]
rects=[[0.,0.,1024.,768.],[123.25,87.5,322.5,258.25],[-17.25,-9.5,33.5,22.25],[17.,29.,32.,24.],[-.25,.25,.5,.5]]
scales=[[1.,1.],[5712/1024,4284/768],[4032/1024,3024/768],[1/32,1/32],[32.,32.],[.25,1.5]]
for i,r in enumerate(rects):
    for j,s in enumerate(scales):cases.append({'id':f'base_{i}_{j}','rect':r,'scale':s,'bounds':[100.,200.,5712.,4284.]if i==2 else[0.,0.,5712.,4284.]})
for axis in[0,1]:
    for bound in['min','max']:
        for k in[17.,1024.]:
            at=k-(ca if bound=='min'else cb)
            for n,v in enumerate([math.nextafter(at,-math.inf),at,math.nextafter(at,math.inf)]):
                r=[0.,0.,32.25,24.5]
                r[axis if bound=='min'else axis+2]=v
                cases.append({'id':f'edge_{axis}_{bound}_{int(k)}_{n}','rect':r,'scale':[5712/1024,4032/1024],'bounds':[-100.,200.,5712.,4284.]})
assert len(cases)==54
expected=[reference(c)for c in cases]
with(W/'cases.json').open('x')as f:json.dump({'cases':cases},f,separators=(',',':'));f.write('\n')
save('freeze.json',{'recipe_sha256':sha(O/'recipe.json'),'metadata_sha256':sha(O/'metadata.json'),'literal_binding':'Only literal VM reads and symbol/selector bindings precede frozen controls; metadata mode calls no ROI primitives.','cases':cases,'expected':expected,'all_controls_frozen_before_native_oracle':True})
cases_before=sha(W/'cases.json')
with(O/'native.log').open('x')as log:
    rc=subprocess.run([str(W/'probe'),'evaluate',str(W/'cases.json'),str(O/'native.json')],stdout=log,stderr=subprocess.STDOUT,timeout=240).returncode
native=json.loads((O/'native.json').read_text())if(O/'native.json').exists()else{}
analysis={'native_returncode':rc,'rows':[],'cases_SHA_unchanged':sha(W/'cases.json')==cases_before,'native_completed':native.get('completed',False),'new_photos':0,'new_image_dispatches':0,'A_phase_complete':False,'acceptance_complete':False}
if rc==0:
    assert native['metadata']==meta['metadata']
    assert len(native['rows'])==len(expected)==54
    for actual,predicted in zip(native['rows'],expected,strict=True):
        assert actual['case']==predicted['case']
        integers=all(actual[k]==predicted[k]for k in['from_pixel_rect','scaled_pixel_rect'])
        absolute=max(abs(a-b)for k in['from_CGRect','scaled_CGRect','flipped_CGRect']for a,b in zip(actual[k],predicted[k],strict=True))
        analysis['rows'].append({'case':actual['case'],'integer_exact':integers,'max_CGRect_abs':absolute,'integer_inputs_unchanged':actual['integer_inputs_unchanged']})
    analysis['integer_fields_compared']=54*8;analysis['CGRect_fields_compared']=54*12
    analysis['integer_exact']=all(r['integer_exact']for r in analysis['rows'])
    analysis['max_CGRect_abs']=max(r['max_CGRect_abs']for r in analysis['rows'])
    analysis['gate_passed']=analysis['integer_exact']and analysis['max_CGRect_abs']<=1e-12 and analysis['cases_SHA_unchanged']and all(r['integer_inputs_unchanged']for r in analysis['rows'])
save('analysis.json',analysis)
print(json.dumps({k:v for k,v in analysis.items()if k!='rows'}))
sys.exit(rc if rc else 0 if analysis['gate_passed']else 1)
