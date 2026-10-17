import pathlib,subprocess,json,sys
root=pathlib.Path.cwd();sys.path.insert(0,str(root));sys.path.insert(0,str(root/'research/vm-native'))
from tools.heif_dump import parse_heif
from heif_standalone import standalone
src=root/'research/vm-native/runner';out=root/'out/native';out.mkdir(parents=True,exist_ok=True);rows=[]
def run(args,log):
 with log.open('w') as f:
  try:rc=subprocess.run([str(x) for x in args],stdout=f,stderr=subprocess.STDOUT,timeout=300).returncode
  except subprocess.TimeoutExpired:rc='timeout'
 rows.append({'args':[str(x) for x in args],'returncode':rc,'log':str(log.relative_to(root))});return rc
run(['clang','-fobjc-arc','-O1','-Wno-deprecated-declarations','-framework','Foundation','-framework','CoreImage','-framework','ImageIO',src/'gain_order_probe.m','-o','/tmp/gain-order'],out/'order-build.log')
for stem in ['IMG_2600','IMG_2604','IMG_2608','IMG_0032','IMG_0033']:
 case=out/'gain-order'/stem;case.mkdir(parents=True,exist_ok=True)
 original=root/('Apple_Native_Samples' if stem in ['IMG_0032','IMG_0033'] else 'research/vm-native/samples')/(stem+'.HEIC');carrier=root/'research/vm-native/carriers'/(stem+'.HEIC');config=json.loads(carrier.with_suffix('.json').read_text());data=carrier.read_bytes();h=parse_heif(data);gain=pathlib.Path('/tmp')/(stem+'-gain.heic');gain.write_bytes(standalone(data,config['identity']['gain_item_id']))
 run(['/tmp/gain-order',original,carrier,gain,config['gain_min_ev'],config['gain_max_ev'],config['gain_offset'],case],case/'order.log')
(out/'status.json').write_text(json.dumps(rows,indent=2)+'\n');raise SystemExit(1 if any(r['returncode']!=0 for r in rows) else 0)
