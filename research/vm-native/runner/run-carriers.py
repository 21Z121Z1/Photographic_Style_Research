"""Read back all five final research carriers; never touch original sources."""
import pathlib,subprocess,json
root=pathlib.Path.cwd();src=root/'research/vm-native/runner';out=root/'out/native';out.mkdir(parents=True,exist_ok=True);rows=[]
def run(args,log):
 with log.open('w') as f:
  try:rc=subprocess.run([str(x) for x in args],stdout=f,stderr=subprocess.STDOUT,timeout=300).returncode
  except subprocess.TimeoutExpired:rc='timeout'
 rows.append({'args':[str(x) for x in args],'log':str(log.relative_to(root)),'returncode':rc});return rc
flags=['clang','-fobjc-arc','-O1','-Wno-deprecated-declarations','-framework','Foundation','-framework','CoreImage','-framework','CoreMedia','-framework','ImageIO','-framework','Metal','-Wl,-undefined,dynamic_lookup']
for name in ['full_sdr_compare','readback_main']:run(flags+[src/(name+'.m'),'-o','/tmp/'+name],out/(name+'-build.log'))
for stem in ['IMG_2600','IMG_2604','IMG_2608','IMG_0032','IMG_0033']:
 case=out/'carriers'/stem;case.mkdir(parents=True,exist_ok=True)
 original=root/('Apple_Native_Samples' if stem in ['IMG_0032','IMG_0033'] else 'research/vm-native/samples')/(stem+'.HEIC')
 carrier=root/'research/vm-native/carriers'/(stem+'.HEIC')
 run(['/tmp/full_sdr_compare',original,carrier,case/'full-sdr.json'],case/'full-sdr.log')
 run(['/tmp/readback_main',carrier,case,'unused'],case/'readback.log')
 # Full-resolution equality is recorded independently, so do not upload a large
 # duplicate SDR float plane. HDR is required for model/transport comparison.
 (case/'published_sdr.f32').unlink(missing_ok=True)
(out/'status.json').write_text(json.dumps(rows,indent=2)+'\n')
raise SystemExit(1 if any(r['returncode']!=0 for r in rows) else 0)
