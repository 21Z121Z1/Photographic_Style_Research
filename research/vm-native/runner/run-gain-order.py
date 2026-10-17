import pathlib,subprocess,json,sys,struct,hashlib
root=pathlib.Path.cwd();sys.path.insert(0,str(root));sys.path.insert(0,str(root/'research/vm-native'))
from tools.heif_dump import parse_heif,_payload_from_item_extents
from heif_standalone import standalone
src=root/'research/vm-native/runner';out=root/'out/native';out.mkdir(parents=True,exist_ok=True);rows=[]
def run(args,log):
 with log.open('w') as f:
  try:rc=subprocess.run([str(x) for x in args],stdout=f,stderr=subprocess.STDOUT,timeout=300).returncode
  except subprocess.TimeoutExpired:rc='timeout'
  except OSError as e:f.write(str(e));rc='spawn-error'
 rows.append({'args':[str(x) for x in args],'returncode':rc,'log':str(log.relative_to(root))});return rc
run(['clang','-fobjc-arc','-O1','-Wno-deprecated-declarations','-framework','Foundation','-framework','CoreImage','-framework','CoreGraphics','-framework','ImageIO',src/'gain_order_probe.m','-o','/tmp/gain-order'],out/'order-build.log')
for stem in ['IMG_2600','IMG_2604','IMG_2608','IMG_0032','IMG_0033']:
 case=out/'gain-order'/stem;case.mkdir(parents=True,exist_ok=True)
 original=root/('Apple_Native_Samples' if stem in ['IMG_0032','IMG_0033'] else 'research/vm-native/samples')/(stem+'.HEIC');carrier=root/'research/vm-native/carriers'/(stem+'.HEIC');config=json.loads(carrier.with_suffix('.json').read_text());data=carrier.read_bytes();h=parse_heif(data);gain=pathlib.Path('/tmp')/(stem+'-gain.heic');gain.write_bytes(standalone(data,config['identity']['gain_item_id']))
 metadata=_payload_from_item_extents(data,h['items'][str(config['identity']['tmap_item_id'])]);assert len(metadata)==62
 values=[n/d for n,d in struct.iter_unpack('>iI',metadata[6:])]
 (case/'tmap-parameters.json').write_text(json.dumps({'payload_sha256':hashlib.sha256(metadata).hexdigest(),'payload_hex':metadata.hex(),'rational_values':values,'min_ev':values[2],'max_ev':values[3],'offset':values[5]},indent=2)+'\n')
 run(['/tmp/gain-order',original,carrier,gain,values[2],values[3],values[5],case],case/'order.log')
(out/'status.json').write_text(json.dumps(rows,indent=2)+'\n');raise SystemExit(1 if any(r['returncode']!=0 for r in rows) else 0)
