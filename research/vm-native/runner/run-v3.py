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
subprocess.run(['log','show','--last','2m','--style','compact','--predicate','process == "guided-v3"'],stdout=(out/'unified.log').open('w'),stderr=subprocess.STDOUT,timeout=60)
# First full-resolution source plus a 2048 tile-render control. No Apple binaries exported.
import os,shutil
flags=['clang','-fobjc-arc','-O1','-framework','Foundation','-framework','CoreImage','-framework','CoreMedia','-framework','ImageIO','-framework','Metal','-Wl,-undefined,dynamic_lookup','-lz']
if run(flags+[src/'reverse_full_v3.m','-o','/tmp/reverse-full-v3'],out/'reverse-full-build.log')==0:
 stem='IMG_2600';photo=root/'research/vm-native/samples'/f'{stem}.HEIC';resources=Path(os.environ['RUNNER_TEMP'])/'full-v3'/stem
 if run(['python3',root/'research/vm-native/extract_inputs.py',photo,resources],out/'full-extract.log')==0:
  for edge in [2048,0]:
   case=root/'out/full-v3'/stem/('2048-control'if edge else'full');case.mkdir(parents=True,exist_ok=True)
   env=os.environ.copy();env['VM_DISABLE_RESIDENCY_SETS']='1'
   with(case/'reverse.log').open('w')as f:
    try:rc=subprocess.run(['/tmp/reverse-full-v3',str(photo),str(resources),str(edge)],stdout=f,stderr=subprocess.STDOUT,timeout=900,env=env).returncode
    except subprocess.TimeoutExpired:rc='timeout'
   rows.append({'photo':stem,'edge':edge,'returncode':rc,'stage':'full-source'})
   for p in list(resources.iterdir()):
    if p.is_file()and(p.suffix in['.json','.f32','.zlib']or p.name=='runtime-override.txt'):shutil.move(p,case/p.name)
(out/'status.json').write_text(json.dumps(rows,indent=2)+'\n');sys.exit(1 if any(x['returncode']!=0 for x in rows)else 0)
