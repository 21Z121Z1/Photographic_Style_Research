"""S67: original host geometry with synthetic inputs; export original AIR text only."""
from pathlib import Path
import hashlib,json,os,re,struct,subprocess,sys,shutil
import llvmlite.binding as llvm
D=Path('research/hdr-native');W=Path(os.environ['W']);O=W/'out'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,j):
    with p.open('x')as f:json.dump(j,f,separators=(',',':'),allow_nan=False);f.write('\n')
assert subprocess.check_output(['sw_vers','-buildVersion'],text=True).strip()=='26A434'
lib=Path('/System/Library/PrivateFrameworks/CMImaging.framework/Versions/A/Resources/default.metallib');blob=lib.read_bytes();assert sha(lib)=='16a8a119e3e0ae1649d32b2bbc8ea9136cb757a8d1f3eb451025821901edff11'
index=[]
for n,m in enumerate(re.finditer(b'\xde\xc0\x17\x0b',blob)):
    at=m.start();_,version,offset,size,cpu=struct.unpack_from('<5I',blob,at);raw=blob[at+offset:at+offset+size]
    if raw[:4]!=b'BC\xc0\xde' or not any(s in raw.lower()for s in[b'globalhistogram',b'globalstats']):continue
    text=str(llvm.parse_bitcode(raw));p=O/f'air-{n:04d}.ll';p.write_text(text);index.append({'wrapper':n,'offset':at,'payload_bytes':size,'payload_sha256':hashlib.sha256(raw).hexdigest(),'text':p.name,'text_sha256':sha(p),'functions':re.findall(r'^define .*?@([^ (]+)',text,re.M)})
save(O/'air-index.json',{'metallib_sha256':sha(lib),'llvmlite':__import__('llvmlite').__version__,'LLVM':list(llvm.llvm_version_info),'modules':index});del blob
# Execute the exact archived S63 body derivation; no host/shader edits.
s=(D/'run_hdr_s63.py').read_text();part=s[s.index('# Keep S60 historical'):s.index('derived=W/')];scope={'D':D};exec(part,scope);body=scope['body'];(W/'stats_body_s63.inc').write_text(body)
save(O/'freeze.json',{'os_build':'26A434','image_version':os.environ.get('ImageVersion'),'synthetic_only':True,'photos':0,'host_parent_sha256':sha(D/'stats_host_s60.m'),'S63_derivation_sha256':sha(D/'run_hdr_s63.py'),'derived_body_sha256':hashlib.sha256(body.encode()).hexdigest(),'probe_sha256':sha(D/'stats_trace_s63.m'),'new_source_sha256':sha(D/'run_hdr_s67.py'),'sizes':[[1024,768],[5712,4284],[4032,3024]],'main_linear_RGB':0.25,'base_gain':1,'baseline_exposure':1,'mattes':{},'GTC':'256-entry identity half','model':'1024*sum(min(W//32,1024-32*y) for y=0..31)','model_status':'hypothesis frozen before native execution','production_stats_size_binding_proven':False})
with(O/'build.log').open('x')as log:subprocess.run(['clang','-I',str(D),'-I',str(W),'-O2','-Wno-deprecated-declarations','-fobjc-arc','-framework','Foundation','-framework','CoreGraphics','-framework','Metal',str(D/'stats_trace_s63.m'),'-o',str(W/'probe')],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240)
rows=[]
for w,h in [(1024,768),(5712,4284),(4032,3024)]:
    case=W/f'case-{w}';case.mkdir();out=case/'result';out.mkdir();p=case/'constant.f16';pixel=struct.pack('<4e',.25,.25,.25,1);chunk=pixel*(w*32)
    with p.open('xb')as f:
        for y in range(0,h,32):f.write(chunk[:w*min(32,h-y)*8])
    (case/'gtc.f16').write_bytes(struct.pack('<256e',*(i/255 for i in range(256))))
    tex={'file':p.name,'shape':[h,w,4],'dtype':'<f2'};save(case/'stats-fixture.json',{'main':tex,'linear':tex,'gtc':{'file':'gtc.f16','shape':[1,256,1],'dtype':'<f2'},'base_gain':1,'baseline_exposure':1,'mattes':{}})
    with(O/f'native-{w}.log').open('x')as log:rc=subprocess.run([str(W/'probe'),str(case),str(out)],stdout=log,stderr=subprocess.STDOUT,timeout=900).returncode
    host=json.loads((out/'host-traced.json').read_text())if(out/'host-traced.json').exists()else{};row={'W':w,'H':h,'returncode':rc,'host':{k:host.get(k)for k in ['completed','CMImaging','main_shape','linear_shape','dispatches','resolved_geometry','barrier_queue_matches_supplied','input_textures_SHA_unchanged','inputStyle_class','tuning_parameter_variant','variant_is_DigitalFlash_pointer','reduction_calls','SRL_before_stats','exception_reason']}};rows.append(row)
    if rc==0:
        raw=(out/'_statsBuf.bin').read_bytes();assert len(raw)==10640
        stats=struct.unpack('<2660I',raw);row['histogram_sums']=[sum(stats[k*256:(k+1)*256])for k in range(10)];row['global_stats']=[list(struct.unpack_from('<9f',raw,10240+k*36))for k in range(10)];row['predicted_hist0_sum']=1024*sum(min(w//32,1024-32*y)for y in range(32));row['hist0_model_equal']=row['histogram_sums'][0]==row['predicted_hist0_sum'];row['global_stats']=[[x if abs(x)<float('inf')else str(x)for x in a]for a in row['global_stats']];(O/f'stats-{w}.bin').write_bytes(raw)
    save(O/'synthetic.json',{'rows':rows})if len(rows)==1 else (O/'synthetic.json').write_text(json.dumps({'rows':rows},separators=(',',':'),allow_nan=False)+'\n')
    shutil.rmtree(case)
    if rc:raise RuntimeError('Native host failed; inspect checkpoint/log before retry')
assert len(index)>=2,'Missing original global histogram/stats AIR'
print(json.dumps({'synthetic_cases':len(rows),'hist0_model_matches':sum(r['hist0_model_equal']for r in rows),'physical_camera_binding':False,'acceptance_complete':False}))
