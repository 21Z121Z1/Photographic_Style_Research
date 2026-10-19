#!/usr/bin/env python3
"""Run the unpatched native CI kernel; never equate it with Photos activation."""
import json
from pathlib import Path
import shutil
import subprocess
import sys

probe, manifest, metrics, work, evidence, semantic_control = map(Path,sys.argv[1:])
work.mkdir(parents=True,exist_ok=False)
evidence.mkdir(parents=True,exist_ok=True)
rows=[]

def echo(path,name):
    print('TEXTURE_JSON_BEGIN '+name,flush=True)
    print(path.read_text(),end='',flush=True)
    print('TEXTURE_JSON_END '+name,flush=True)

for strength in ['0','0.5','1']:
    name='intensity'+strength
    native=work/name
    public=evidence/name;public.mkdir()
    args=[str(probe),str(native),'--render-bloom',str(manifest),strength,
          '--semantic-control',str(semantic_control)]
    try:
        p=subprocess.run(args,capture_output=True,text=True,timeout=120)
        code,stdout,stderr=p.returncode,p.stdout,p.stderr
    except subprocess.TimeoutExpired:
        code,stdout,stderr=124,'','native render timed out'
    (public/'native.stdout.log').write_text(stdout)
    (public/'native.stderr.log').write_text(stderr)
    print('BLOOM_NATIVE_PROCESS',name,'exit_code='+str(code),flush=True)
    print(stderr,end='',flush=True)
    # Keep native assertion messages visible without replaying checkpoint JSON
    # under ambiguous names. Do not replace Apple's assertion implementation.
    in_json=False
    for line in stdout.splitlines():
        if line.startswith('TEXTURE_JSON_BEGIN '): in_json=True
        elif line.startswith('TEXTURE_JSON_END '): in_json=False
        elif not in_json: print('BLOOM_NATIVE_STDOUT '+line,flush=True)
    row={'intensity':float(strength),'native_process_exit':code,'render_completed':False}
    report=native/'render-bloom.json'
    if report.exists():
        shutil.copyfile(report,public/'render-bloom.json')
        data=json.loads(report.read_text());row['render_completed']=data.get('render_completed',False)
        echo(public/'render-bloom.json',name+'/render-bloom.json')
    if row['render_completed']:
        subprocess.run([str(metrics),str(native/'baseline.rgba32f'),str(native/'rendered.rgba32f'),str(public/'metrics.json')],check=True)
        row['metrics']=json.loads((public/'metrics.json').read_text())
        echo(public/'metrics.json',name+'/metrics.json')
    rows.append(row)
    if code < 0 and strength == '0.5':
        # Launch only our public synthetic-input process. A debugger refusal is
        # evidence of a diagnostic limit; do not alter security policy or retry
        # with elevated privileges. No breakpoints or Apple code changes.
        debug=['xcrun','lldb','--batch','-o','run','-o','thread backtrace all','--',*args]
        try:
            d=subprocess.run(debug,capture_output=True,text=True,timeout=90)
            diagnostic={'command':debug,'debugger_exit':d.returncode,
                        'stdout':d.stdout,'stderr':d.stderr,
                        'scope':'diagnostic child launch only; debugger exit is not render success'}
        except subprocess.TimeoutExpired:
            diagnostic={'command':debug,'debugger_exit':124,'scope':'diagnostic timed out; no security-policy changes'}
        path=public/'native-diagnostic.json'
        path.write_text(json.dumps(diagnostic,indent=2)+'\n')
        echo(path,name+'/native-diagnostic.json')
if all(r['render_completed'] for r in rows):
    path=evidence/'parameter-response.json'
    subprocess.run([str(metrics),str(work/'intensity0/rendered.rgba32f'),str(work/'intensity1/rendered.rgba32f'),str(path)],check=True)
    echo(path,'parameter-response.json')
summary={'scope':'single original native Bloom CI processor and controlled tuning context only; no full producer or Photos admission',
         'photos_used':False,'original_capture_information':False,'linear_thumbnail_resource_created':False,
         'semantic_auxiliary_roles_synthesized':False,'apple_implementations_patched':False,'rows':rows}
(evidence/'bloom-matrix.json').write_text(json.dumps(summary,indent=2)+'\n')
echo(evidence/'bloom-matrix.json','bloom-matrix.json')
if any(r['native_process_exit'] or not r['render_completed'] for r in rows):
    sys.exit('NATIVE_BLOOM_CONTEXT_OR_RENDER_FAILURE: do not claim successful editing')
