"""Runner-only original ARM allocateTone replay with explicit synthetic context.

No native iOS claim and no camera-amplitude calibration. External powf comes
from runner libSystem, while memory/authentication hooks are enumerated.
"""
from pathlib import Path
import ctypes,hashlib,json,math,struct,sys
import numpy as np
from unicorn import Uc,UC_ARCH_ARM64,UC_MODE_ARM,UC_HOOK_CODE,UC_HOOK_MEM_INVALID
from unicorn.arm64_const import *

OUT=Path(sys.argv[1]);OUT.mkdir(parents=True,exist_ok=True)
meta=json.loads(Path('research/semantic-styles/evidence/producer-allocation-s19.json').read_text())
u=Uc(UC_ARCH_ARM64,UC_MODE_ARM);mapped=set();patches=[];recent=[];external={}
def map_region(a,n):
 for page in range(a&~4095,(a+n+4095)&~4095,4096):
  if page not in mapped:u.mem_map(page,4096);mapped.add(page)
def words(data):return np.frombuffer(bytes(data),'<f4').copy()
def fbits(x):return struct.unpack('<I',struct.pack('<f',x))[0]
for block in meta['blocks']:
 raw=b''.join(bytes.fromhex(i['bytes']) for i in block['instructions']);assert hashlib.sha256(raw).hexdigest()==block['sha256']
 a=int(block['address'],16);map_region(a,len(raw));u.mem_write(a,raw)
 for ins in block['instructions']:
  a=int(ins['address'],16);asm=ins['asm']
  if asm.startswith(('pacibsp','pac i','blraa')):
   u.mem_write(a,bytes.fromhex('1f2003d5'));patches.append({'address':hex(a),'original':asm,'replacement':'nop; authentication/stack probing only'})
  elif asm.startswith('retab'):
   u.mem_write(a,bytes.fromhex('c0035fd6'));patches.append({'address':hex(a),'original':asm,'replacement':'ret x30; no PAC authentication in emulator'})
lit=meta['literal_page'];raw=bytes.fromhex(lit['hex']);assert hashlib.sha256(raw).hexdigest()==lit['sha256'];map_region(int(lit['address'],16),len(raw));u.mem_write(int(lit['address'],16),raw)
map_region(0x27a5b9000,4096)  # Only read to resolve stack-probe pointer; BLRAA skipped.
for a in [0x258100870,0x258100920,0x258116bb0,0x40000000]:map_region(a,4);u.mem_write(a,bytes.fromhex('1f2003d5'))
map_region(0x30000000,0x100000);map_region(0x50000000,0x100000)
u.reg_write(UC_ARM64_REG_CPACR_EL1,3<<20);u.reg_write(UC_ARM64_REG_FPCR,0)
lib=ctypes.CDLL('/usr/lib/libSystem.B.dylib');lib.powf.argtypes=[ctypes.c_float,ctypes.c_float];lib.powf.restype=ctypes.c_float
def hook(uc,a,size,data):
 recent.append(hex(a));del recent[:-8]
 if a==0x40000000:uc.emu_stop();return
 if a in [0x258100870,0x258100920,0x258116bb0]:
  external[hex(a)]=external.get(hex(a),0)+1
  if a==0x258100870:
   dst,n=[uc.reg_read(r) for r in [UC_ARM64_REG_X0,UC_ARM64_REG_X1]];assert n<0x20000;uc.mem_write(dst,bytes(n))
  elif a==0x258100920:
   dst,src,n=[uc.reg_read(r) for r in [UC_ARM64_REG_X0,UC_ARM64_REG_X1,UC_ARM64_REG_X2]];assert n<0x20000;uc.mem_write(dst,bytes(uc.mem_read(src,n)))
  else:
   a0,a1=[struct.unpack('<f',struct.pack('<I',uc.reg_read(r)))[0] for r in [UC_ARM64_REG_S0,UC_ARM64_REG_S1]];uc.reg_write(UC_ARM64_REG_S0,fbits(lib.powf(a0,a1)))
  uc.reg_write(UC_ARM64_REG_PC,uc.reg_read(UC_ARM64_REG_LR))
u.hook_add(UC_HOOK_CODE,hook)
memfault=[]
def fault(uc,access,a,size,value,data):memfault.append({'access':access,'address':hex(a),'size':size,'pc':hex(uc.reg_read(UC_ARM64_REG_PC))});return False
u.hook_add(UC_HOOK_MEM_INVALID,fault)

OBJ,OUTPTR,HIST,TUNE,DISP,FRAME,BASE,V,DX= [0x30000000+i*0x10000 for i in range(9)]
F=np.float32
def replay(hist,vector,dx,n=128,tone_budget=1.,constraint=.01,shape_power=1.):
 u.mem_write(0x30000000,bytes(0x100000));u.mem_write(0x50000000,bytes(0x100000))
 def f32(a,v):u.mem_write(a,struct.pack('<f',v))
 u.mem_write(OBJ+0x14,struct.pack('<II',n+1,n));u.mem_write(OBJ+0x228,np.linspace(0,1,n+1,dtype='f4').tobytes())
 u.mem_write(HIST,np.asarray(hist,'f4').tobytes());u.mem_write(V,np.asarray(vector,'f4').tobytes());u.mem_write(DX,np.asarray(dx,'f4').tobytes());u.mem_write(BASE,np.full(n,constraint,'f4').tobytes())
 f32(TUNE+0x80,1.)
 for off,v in [(0x9b8,1e10),(0x9bc,1.),(0x9d4,shape_power),(0x9d8,shape_power),(0x9e8,float(n)),(0x9ec,1.)]:f32(FRAME+0x6000+off,v)
 f32(DISP+0x408,tone_budget)
 sp=0x500f0000;u.mem_write(sp,struct.pack('<4Q3B',V,DX,0,0,0,0,0))
 for reg,value in zip([UC_ARM64_REG_X0,UC_ARM64_REG_X1,UC_ARM64_REG_X2,UC_ARM64_REG_X3,UC_ARM64_REG_X4,UC_ARM64_REG_X5,UC_ARM64_REG_X6,UC_ARM64_REG_X7],[OBJ,OUTPTR,0,HIST,TUNE,DISP,FRAME,BASE]):u.reg_write(reg,value)
 for reg,value in zip([UC_ARM64_REG_S0,UC_ARM64_REG_S1,UC_ARM64_REG_S2],[0.,1.,float(n)]):u.reg_write(reg,fbits(value))
 u.reg_write(UC_ARM64_REG_X28,0)  # Clear incoming register state;0x256ba1400 overwrites w28 from tuning+0xc (zero in these synthetic cases).
 u.reg_write(UC_ARM64_REG_SP,sp);u.reg_write(UC_ARM64_REG_LR,0x40000000)
 u.emu_start(0x256ba11e4,0x40000004,count=2_000_000)
 assert u.reg_read(UC_ARM64_REG_PC)==0x40000000,'Instruction count exhausted'
 return words(u.mem_read(OUTPTR,(n+1)*4))

rows=[];curves=[]
try:
 n=128;grid=(np.arange(n,dtype='f8')+.5)/n;dx=np.full(n,1/n,'f4');beta=25/128
 for profile in ['uniform','dark','bright','bimodal']:
  hist={'uniform':np.ones(n),'dark':np.exp(-grid*12),'bright':np.exp((grid-1)*12),'bimodal':np.exp(-((grid-.15)/.04)**2)+np.exp(-((grid-.8)/.03)**2)}[profile];hist=(hist/hist.sum()).astype('f4')
  for target_profile in ['uniform','dark','bright']:
   target={'uniform':np.ones(n),'dark':np.exp(-grid*18),'bright':np.exp((grid-1)*18)}[target_profile];target=(target/target.sum()).astype('f4')
   for budget in [.25,.5,1.]:
    # These are declared synthetic vectors, not identified original frame B/T.
    results=[replay(hist,F(F(1)-F(w))*np.ones(n,dtype='f4')+F(w)*F(n)*target,dx,tone_budget=budget,constraint=.005,shape_power=1.) for w in [0.,beta]]
    a,b=results;finite=bool(np.isfinite(a).all() and np.isfinite(b).all());changed=int(np.count_nonzero(a.view('u4')!=b.view('u4')))
    positive=(a>0)&(b>0);ev=np.log2(b[positive].astype('f8')/a[positive].astype('f8'))
    rows.append({'profile':profile,'target_profile':target_profile,'budget':budget,'finite':finite,'max_abs_change':float(abs(a-b).max()) if finite else None,'changed_f32':changed,'curve_min':float(min(a.min(),b.min())) if finite else None,'curve_max':float(max(a.max(),b.max())) if finite else None,'nondecreasing':bool((np.diff(a)>=0).all() and (np.diff(b)>=0).all()),'positive_nodes':int(positive.sum()),'node_ratio_EV_min':float(ev.min()) if len(ev) else None,'node_ratio_EV_max':float(ev.max()) if len(ev) else None,'node_ratio_is_physical_pixel_EV':False})
    curves.append({'profile':profile,'target':target_profile,'budget':budget,'baseline':a.tolist(),'beta':b.tolist()})
except Exception as e:
 (OUT/'allocation-error.json').write_text(json.dumps({'exception':repr(e),'recent':recent,'memory_faults':memfault,'completed_cases':len(rows),'hooks':external},indent=2)+'\n');raise
report={'scope':'Original allocateTone and three helpers, synthetic statistics and explicit external hooks. Not native iOS, not IMG_2810 amplitude.','source_os_build':meta['os_build'],'rows':rows,'all_finite':all(r['finite'] for r in rows),'at_least_one_nonzero':any(r['changed_f32'] for r in rows),'patches':patches,'external_hooks':external,'powf_source':'runner libSystem powf, not captured iOS implementation','beta':beta,'j':281/256,'physical_pixel_EV_identified':False}
(OUT/'allocation-results.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');(OUT/'allocation-curves.synthetic.json').write_text(json.dumps(curves,indent=2,allow_nan=False)+'\n')
print(json.dumps({'completed_cases':len(rows),'nonzero_cases':sum(r['changed_f32']>0 for r in rows),'all_finite':report['all_finite']}))
