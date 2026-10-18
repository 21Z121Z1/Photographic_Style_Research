from pathlib import Path
import subprocess,json,sys
root=Path.cwd();src=root/'research/vm-native/runner';out=root/'out/guided-full-v3';out.mkdir(parents=True,exist_ok=True);rows=[]
with(out/'build.log').open('w')as f:rc=subprocess.run(['clang','-fobjc-arc','-O1','-framework','Foundation','-framework','Metal','-lz',str(src/'guided_full_v3.m'),'-o','/tmp/guided-full-v3'],stdout=f,stderr=subprocess.STDOUT).returncode
rows.append({'stage':'compile','returncode':rc})
if rc==0:
 for case in sorted((root/'research/vm-native/full-fixtures-v3').iterdir()):
  if not(case/'fixture.json').exists():continue
  dest=out/case.name;dest.mkdir();log=dest/'run.log'
  with log.open('w')as f:
   try:rc=subprocess.run(['/tmp/guided-full-v3',str(case),str(dest)],stdout=f,stderr=subprocess.STDOUT,timeout=240).returncode
   except subprocess.TimeoutExpired:rc='timeout'
  rows.append({'case':case.name,'returncode':rc});print(case.name,rc,flush=True)
(out/'status.json').write_text(json.dumps(rows,indent=2)+'\n');sys.exit(1 if any(x['returncode']!=0 for x in rows)else 0)
