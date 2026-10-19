"""Runner-only curve set inverse, checked against original ARM interpolate."""
from pathlib import Path
import sys,json,hashlib
import numpy as np
from unicorn import Uc,UC_ARCH_ARM64,UC_MODE_ARM
from unicorn.arm64_const import *
from semantic_curve_inverse import inverse_curve_pair

O=Path(sys.argv[1]);O.mkdir(exist_ok=True,parents=True);S=Path('research/semantic-styles/evidence')
metadata=json.loads((S/'producer-allocation-s19.json').read_text());block=next(b for b in metadata['blocks'] if b['symbol']=='interpolate');raw=b''.join(bytes.fromhex(i['bytes']) for i in block['instructions']);assert hashlib.sha256(raw).hexdigest()==block['sha256']
u=Uc(UC_ARCH_ARM64,UC_MODE_ARM);start=int(block['address'],16);u.mem_map(start&~4095,4096);u.mem_write(start,raw);u.mem_map(0x30000000,0x80000);u.mem_map(0x40000000,4096);u.mem_write(0x40000000,bytes.fromhex('1f2003d5'));u.reg_write(UC_ARM64_REG_CPACR_EL1,3<<20);u.reg_write(UC_ARM64_REG_FPCR,0)
def original_interpolate(knots,values,query):
 for address,data in [(0x30000000,knots),(0x30010000,values),(0x30020000,query)]:u.mem_write(address,np.asarray(data,'f4').tobytes())
 u.mem_write(0x30030000,bytes(len(query)*4))
 for reg,value in zip([UC_ARM64_REG_X0,UC_ARM64_REG_X1,UC_ARM64_REG_X2,UC_ARM64_REG_X3,UC_ARM64_REG_X4,UC_ARM64_REG_X5,UC_ARM64_REG_X6],[0,0x30000000,0x30010000,len(knots),0x30020000,0x30030000,len(query)]):u.reg_write(reg,value)
 u.reg_write(UC_ARM64_REG_LR,0x40000000);u.emu_start(start,0x40000000,count=2_000_000)
 assert u.reg_read(UC_ARM64_REG_PC)==0x40000000
 return np.frombuffer(bytes(u.mem_read(0x30030000,len(query)*4)),'f4').copy()

curves=json.loads((S/'allocation-curves-s19.synthetic.json').read_text());knots=np.linspace(0,1,129,dtype='f4');queries=np.unique(np.concatenate([np.linspace(-.05,1.05,515,dtype='f4'),knots])).astype('f4')
rows=[]
for i,case in enumerate(curves):
 base=np.asarray(case['baseline'],'f4');applied=np.asarray(case['beta'],'f4');observed=original_interpolate(knots,applied,queries);expected=original_interpolate(knots,base,queries)
 result=inverse_curve_pair(observed,knots,applied,base,storage='float32',forward_error_abs=2**-22)
 interval_bad=(expected<result['neutral_lower'])|(expected>result['neutral_upper']);input_bad=(queries<result['input_lower'])|(queries>result['input_upper']);mask=result['guaranteed_1e3_mask'];relative=abs(result['candidate'][mask]-expected[mask])/np.maximum(abs(expected[mask]),1e-12)
 assert not interval_bad.any() and not input_bad.any() and (relative<=1e-3).all()
 rows.append({'case':i,'profile':case['profile'],'target':case['target'],'budget':case['budget'],'observations':len(queries),'input_interval_misses':int(input_bad.sum()),'neutral_interval_misses':int(interval_bad.sum()),'guaranteed_pixels':int(mask.sum()),'guaranteed_coverage':float(mask.mean()),'max_relative_on_guaranteed':float(relative.max()) if len(relative) else None,'output_interval_width_max':float(np.max(result['neutral_upper']-result['neutral_lower'])),'input_unbounded_low':int(result['endpoint_low_mask'].sum()),'input_unbounded_high':int(result['endpoint_high_mask'].sum()),'plateau_observations':int(result['plateau_mask'].sum())})
# Explicit plateau has different neutral values at the same observation.
f=np.array([0,0,.5,.5,1],'f4');g=np.linspace(0,1,5,dtype='f4');x=np.linspace(0,1,5,dtype='f4');r=inverse_curve_pair(np.array([0,.5,1]),x,f,g,storage='exact')
assert r['input_lower'][1]<=.5 and r['input_upper'][1]>=.75 and r['neutral_lower'][1]<=.5 and r['neutral_upper'][1]>=.75
assert not r['guaranteed_1e3_mask'][1] and np.isnan(r['candidate'][1])
report={'os_build':'26A434','source_producer_build':'24A446 user-provided provenance; not sample-matching camera','scope':'Conditional monotone supplied-curve inverse; exact rational interval arithmetic, original ARM interpolate oracle. No original-camera curves/amplitude/domain supplied.','curve_cases':len(rows),'query_count_per_case':len(queries),'total_observations':sum(r['observations'] for r in rows),'input_interval_misses':sum(r['input_interval_misses'] for r in rows),'neutral_interval_misses':sum(r['neutral_interval_misses'] for r in rows),'max_relative_on_guaranteed':max(r['max_relative_on_guaranteed'] for r in rows if r['max_relative_on_guaranteed'] is not None),'minimum_guaranteed_coverage':min(r['guaranteed_coverage'] for r in rows),'threshold':1e-3,'implementation_error_bound_abs':2**-22,'bound_basis':'Uniform dyadic knots; subtraction/scale of query offset exact, one curve-value difference and one FMA. Explicit2^-22 covers f32 interpolation and endpoint conversion on normalized tables. It is a model error envelope, not an acceptance tolerance.','plateau_interval_test_pass':True,'camera_inverse_verified':False,'old_gate_modified':False,'rows':rows}
(O/'conditional-curve-inverse.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['rows','scope','bound_basis']}))
