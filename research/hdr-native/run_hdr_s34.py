"""Original installed RGB LTM-map materialization, synthetic branch isolation.

No photographs, no parameter fitting, and no claim of scene recovery. Native
host, direct installed kernels, and the pinned guided reference stay separate.
"""
from pathlib import Path
import hashlib,json,math,os,struct,subprocess,sys
import numpy as np
sys.path.insert(0,str(Path('research/hdr-native').resolve()))
import guided_reference_v3 as guided

W=Path(os.environ['W']); O=W/'out'; O.mkdir(exist_ok=True)
D=Path('research/hdr-native')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def writej(p,v):p.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
assert subprocess.check_output(['sw_vers','-buildVersion'],text=True).strip()=='26A434'
sources=[D/x for x in ['ltm_materialize_s34.m','run_hdr_s34.py','guided_reference_v3.py']]
sources += [Path('research/vm-native/runner')/x for x in ['guided_oracle_v3.m','encoder_capture_v2.inc']]
writej(O/'freeze.json',{'scope':'Three synthetic RGB-LTM materialization cases; no re-fit of frozen consumer','source_sha256':{str(p):sha(p) for p in sources},'native_library':{'path':'/System/Library/PrivateFrameworks/CMImaging.framework/Versions/A/Resources/default.metallib','sha256':sha('/System/Library/PrivateFrameworks/CMImaging.framework/Versions/A/Resources/default.metallib')},'guided_source':'Unmodified iterations/20261018-v3/guided.py copied under a distinct research name','matrix':'Four identity float3x3 matrices; input transfer=0 as in previous captured context','cases':['identity-2x','gtc-4x','edges-5p5x'],'modes':['host','direct-plain','direct-imageblock'],'half_differences':'Report without fitting; original half-bit gate unchanged','true_photographs':0,'acceptance_complete':False})
with (O/'build.log').open('w') as f:
 subprocess.run(['clang','-O2','-g','-fobjc-arc','-framework','Foundation','-framework','Metal',D/'ltm_materialize_s34.m','-o',W/'probe'],stdout=f,stderr=subprocess.STDOUT,check=True)

def field(h,w):
 x=np.broadcast_to((np.arange(w)+.5)/w,(h,w));y=np.broadcast_to(((np.arange(h)+.5)/h)[:,None],(h,w))
 # All structure is synthetic and declared before any oracle observation.
 edge=(x>.5).astype(float);disk=((x-.72)**2+(y-.45)**2<.12**2).astype(float)
 return np.stack([.015+.45*x+.18*edge,.02+.4*y+.18*disk,.025+.28*(1-x)+.12*edge],-1)
def rgba(a):return np.concatenate([a,np.ones(a.shape[:2]+(1,))],-1).astype('<f2')
def h(a):return np.asarray(a).astype('f2').astype('f4')
def metric(a,b):
 a=np.asarray(a,'f8');b=np.asarray(b,'f8');good=np.isfinite(a)&np.isfinite(b);n=int((~good).sum())
 if n:return {'nonfinite_components':n,'max_abs':None,'psnr_peak1_db':None,'half_different_components':int(np.count_nonzero(a.astype('f2').view('u2')!=b.astype('f2').view('u2')))}
 d=a-b;mse=float(np.mean(d*d));pos=(a>0)&(b>0);ev=np.log2(a[pos]/b[pos])
 return {'nonfinite_components':0,'max_abs':float(abs(d).max()),'psnr_peak1_db':-10*math.log10(mse) if mse else 'inf','max_relative_ref_gt_1e-6':float((abs(d[b>1e-6])/b[b>1e-6]).max()) if (b>1e-6).any() else None,'half_different_components':int(np.count_nonzero(a.astype('f2').view('u2')!=b.astype('f2').view('u2'))),'positive_pair_components':int(pos.sum()),'max_abs_EV_positive':float(abs(ev).max()) if ev.size else None,'rms_EV_positive':float(np.sqrt(np.mean(ev*ev))) if ev.size else None}
def small_reference(main,linear,gtc,gain,be,fe,weight):
 sh=linear.shape[:2];ux=(np.arange(sh[1],dtype='f4')[None,:]+np.float32(.5))/np.float32(sh[1]);uy=(np.arange(sh[0],dtype='f4')[:,None]+np.float32(.5))/np.float32(sh[0]);a=guided.normalized_sample(main,ux,uy)[...,:3];x=h(h(linear[...,:3])*np.float16(gain));answers={}
 for name,exposure in [('bg-small',be),('fg-small',fe)]:
  u=np.minimum(h(x*np.float16(exposure)),np.float16(1));coord=h(u*np.float16(255));curved=np.concatenate([guided.sample(gtc,coord[...,k],np.zeros(sh,'f4')) for k in range(3)],-1)
  # Readable fixed half rounding. Compiler contraction remains oracle-tested.
  z=h(u.astype('f8')+(curved.astype('f8')-u.astype('f8'))*float(np.float16(weight)))
  with np.errstate(divide='ignore',invalid='ignore'):q=h(z/a)
  q=np.where(h(a-np.float16(1/255))<0,0,q)
  answers[name]=rgba(q)
 return answers
def edge_metrics(q,guide,small):
 v=q[...,:3].astype('f8');g=guide[...,:3].astype('f8');dx=np.diff(v,axis=1);dy=np.diff(v,axis=0);gx=np.max(abs(np.diff(g,axis=1)),axis=-1);gy=np.max(abs(np.diff(g,axis=0)),axis=-1)
 edge_x=gx>.08;edge_y=gy>.08;lo=np.min(small[...,:3].astype('f8'),axis=(0,1));hi=np.max(small[...,:3].astype('f8'),axis=(0,1));pos=v>0
 return {'mean_abs_gradient_x':float(abs(dx).mean()),'mean_abs_gradient_y':float(abs(dy).mean()),'max_abs_gradient':float(max(abs(dx).max(),abs(dy).max())),'edge_jump_mean':float(np.concatenate([abs(dx)[edge_x].reshape(-1),abs(dy)[edge_y].reshape(-1)]).mean()) if edge_x.any() or edge_y.any() else None,'below_small_global_min_components':int((v<lo).sum()),'above_small_global_max_components':int((v>hi).sum()),'positive_components':int(pos.sum()),'interpretation':'Diagnostics against the same synthetic field; gradients alone do not certify fewer halos or physical recovery'}
cases=[('identity-2x',128,128,1.,.5,1.5,0.),('gtc-4x',192,256,1.5,.75,1.25,1.),('edges-5p5x',256,352,2.,.75,1.25,.5)]
rows=[]
for name,hh,ww,gain,be,fe,weight in cases:
 root=O/name;root.mkdir();main=rgba(field(hh,ww));linear=rgba(field(64,64)*.7)
 # Exercise the original near-black branch without deleting it from metrics.
 main[:,:max(1,ww//32),:3]=np.array([0,.001,.003],dtype='f2')
 t=np.linspace(0,1,256,dtype='f8');gtc=(t**1.7).astype('<f2')[None,:,None]
 params=bytearray(672);color=bytearray(320)
 for offset,val in [(24,gain),(28,1.),(620,.3),(624,.6),(628,be),(632,fe),(636,weight)]:struct.pack_into('<f',params,offset,val)
 for start in range(0,320,80):
  for c in range(3):struct.pack_into('<f',color,start+16+16*c+4*c,1.)
 (root/'params.bin').write_bytes(params);(root/'color.bin').write_bytes(color)
 fixture={}
 for key,arr in [('main',main),('linear',linear),('gtc',gtc)]:
  arr.tofile(root/(key+'.f16'));fixture[key]={'file':key+'.f16','shape':list(arr.shape),'dtype':'<f2'}
 writej(root/'fixture.json',fixture)
 reference=small_reference(main,linear,gtc,gain,be,fe,weight)
 for key,arr in reference.items():arr.tofile(root/(key+'-reference.f16'))
 modes={}
 for mode in ['host','direct-plain','direct-imageblock']:
  out=root/mode;out.mkdir()
  with (out/'native.log').open('w') as f:
   try:rc=subprocess.run([W/'probe',root,out,mode],stdout=f,stderr=subprocess.STDOUT,timeout=240).returncode
   except subprocess.TimeoutExpired:rc=124
  native=json.loads((out/'native.json').read_text()) if (out/'native.json').exists() else {'success':False,'checkpoint':json.loads((out/'checkpoint.json').read_text()) if (out/'checkpoint.json').exists() else None}
  item={'native_returncode':rc,'native':native,'small_reference_comparison':{},'guided_reference_comparison':{},'bilinear_comparison':{},'edge_diagnostics':{}}
  modes[mode]=item
  if rc!=0:continue
  def load(key):
   spec=native['textures'][key];return np.fromfile(out/spec['file'],dtype=spec['dtype']).reshape(spec['shape'])
  for branch in ['bg','fg']:
   small=load(branch+'-small');full=load(branch+'-full');item['small_reference_comparison'][branch]=metric(small[...,:3],reference[branch+'-small'][...,:3])
   pred=guided.upsample(small,main,rows=32)
   item['guided_reference_comparison'][branch]=metric(pred[...,:3],full[...,:3])
   ux=(np.arange(ww,dtype='f4')[None,:]+np.float32(.5))/np.float32(ww);uy=(np.arange(hh,dtype='f4')[:,None]+np.float32(.5))/np.float32(hh)
   bilinear=guided.normalized_sample(small,ux,uy)
   item['bilinear_comparison'][branch]=metric(bilinear[...,:3],full[...,:3]);item['edge_diagnostics'][branch]={'native_guided':edge_metrics(full,main,small),'bilinear':edge_metrics(bilinear,main,small)}
   # Same footprint area average, reported without imposing the former
   # anchor correction, which is not an Apple host operation.
   xx=(np.arange(64,dtype='f4')[None,:]+np.float32(.5))/64;yy=(np.arange(64,dtype='f4')[:,None]+np.float32(.5))/64
   item['edge_diagnostics'][branch]['center_sample_anchor']=metric(guided.normalized_sample(full,xx,yy)[...,:3],small[...,:3])
  item['params_unchanged']=native['params_SHA_before']==native['params_SHA_after']==sha(root/'params.bin')
 row={'case':name,'main_shape':list(main.shape),'linear_shape':list(linear.shape),'parameters':{'linearBaseGain':gain,'bgExposureGain':be,'fgExposureGain':fe,'GTC':weight},'modes':modes,'native_mode_comparison':{}}
 for left,right in [('host','direct-imageblock'),('host','direct-plain'),('direct-plain','direct-imageblock')]:
  if all(modes[x]['native_returncode']==0 for x in [left,right]):
   pairs={}
   for key in ['bg-small','fg-small','bg-full','fg-full']:
    def readmode(m):
     spec=modes[m]['native']['textures'][key];return np.fromfile(root/m/spec['file'],dtype=spec['dtype']).reshape(spec['shape'])
    pairs[key]=metric(readmode(left)[...,:3],readmode(right)[...,:3])
   row['native_mode_comparison'][left+'__'+right]=pairs
 rows.append(row)
writej(O/'analysis-s34.json',{'os_build':'26A434','image_version':os.environ.get('ImageVersion'),'scope':'Original RGB LTM creation and RGB guided materialization branch only; synthetic controlled context, SRL false, transfer0','rows':rows,'true_photographs':0,'global_inverse_complete':False,'local_inverse_complete':False,'acceptance_complete':False})
print(json.dumps({'cases':len(rows),'mode_returncodes':{r['case']:{k:v['native_returncode'] for k,v in r['modes'].items()} for r in rows},'acceptance_complete':False}))
