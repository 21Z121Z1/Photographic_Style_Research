"""Runner ARM64 instruction replay of the scalar j-dependent spatial cap."""
from pathlib import Path
import json,struct,sys
import numpy as np
from unicorn import Uc,UC_ARCH_ARM64,UC_MODE_ARM
from unicorn.arm64_const import UC_ARM64_REG_CPACR_EL1,UC_ARM64_REG_FPCR,UC_ARM64_REG_X8,UC_ARM64_REG_S0,UC_ARM64_REG_S1
data=json.loads(Path(sys.argv[1]).read_text());F=np.float32
u=Uc(UC_ARCH_ARM64,UC_MODE_ARM);pc=int(data['address'],16);end=int(data['end'],16);u.mem_map(pc&~4095,4096);u.mem_write(pc,bytes.fromhex(data['instruction_bytes_le']));u.mem_map(0x30000000,4096);u.reg_write(UC_ARM64_REG_CPACR_EL1,3<<20);u.reg_write(UC_ARM64_REG_FPCR,0);u.reg_write(UC_ARM64_REG_X8,0x30000000)
bits=lambda v:struct.unpack('<I',struct.pack('<f',v))[0]
def model(n,j):
 if np.isneginf(n):a=F(1)
 else:
  with np.errstate(invalid='ignore',divide='ignore'):a=F(F(-1)/F(F(data['kappa'])*F(np.sqrt(F(n)))))
  a=F(min(max(F(a+F(1)),F(0)),F(1)))
 b=F(F(1)-a);b=F(b+b);v=F(float(b)*float(F(F(j)-F(1)))+float(a))
 return F(min(max(v,F(0)),F(1)))
rows=[]
for n in [0,.0001,.001,.01,.05,.25,1,4,16,20,32,64,256,1024,4096,float('-inf')]:
 for j in [.8,1,1.09765625,1.2]:
  u.mem_write(0x30000000,struct.pack('<f',n));u.mem_write(0x3000001c,struct.pack('<f',j));u.reg_write(UC_ARM64_REG_S0,bits(data['kappa']));u.reg_write(UC_ARM64_REG_S1,bits(float('-inf')));u.emu_start(pc,end,count=100)
  a=struct.unpack('<f',struct.pack('<I',u.reg_read(UC_ARM64_REG_S0)))[0];b=float(model(n,j));rows.append({'N':n if np.isfinite(n) else '-inf','j':j,'ARM64':a,'formula':b,'different_f32':bits(a)!=bits(b),'max_abs':abs(a-b)})
result={'os_build':data['os_build'],'instruction_sha256':data['instruction_sha256'],'kappa':data['kappa'],'cases':rows,'different_f32':sum(r['different_f32'] for r in rows),'max_abs':max(r['max_abs'] for r in rows),'native_iOS_execution':False,'scope':'Unicorn replay of statically extracted 20-instruction scalar block against float32/FMA algebra; not camera output validation.'}
Path(sys.argv[2]).write_text(json.dumps(result,indent=2)+'\n')
