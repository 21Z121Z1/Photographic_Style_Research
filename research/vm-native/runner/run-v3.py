from pathlib import Path
import subprocess,json,sys
root=Path.cwd();src=root/'research/vm-native/runner';out=root/'out/guided-v3';out.mkdir(parents=True,exist_ok=True);rows=[]
def run(args,log):
 with log.open('w')as f:
  try:rc=subprocess.run([str(x)for x in args],stdout=f,stderr=subprocess.STDOUT,timeout=600).returncode
  except subprocess.TimeoutExpired:rc='timeout'
 rows.append({'args':[str(x)for x in args],'returncode':rc,'log':str(log.relative_to(root))});return rc
if run(['clang','-fobjc-arc','-O1','-framework','Foundation','-framework','Metal',src/'guided_oracle_v3.m','-o','/tmp/guided-v3'],out/'build.log')==0:
 for fixture in sorted((root/'research/vm-native/fixtures-v3').iterdir()):run(['/tmp/guided-v3',fixture,out/fixture.name],out/(fixture.name+'.log'))
(out/'status.json').write_text(json.dumps(rows,indent=2)+'\n');sys.exit(1 if any(x['returncode']!=0 for x in rows)else 0)
