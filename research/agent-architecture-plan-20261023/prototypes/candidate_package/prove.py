"""Rerun candidate A tests and CLI journeys into a new evidence directory."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def prove(output):
    output.mkdir(parents=True, exist_ok=False)
    sources = {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in HERE.glob('*.py')}
    commands = [
        ([sys.executable, '-m', 'unittest', 'discover', '-s', str(HERE), '-p', 'test_*.py', '-v'], 0),
        ([sys.executable, str(HERE/'demo.py'), '--output', str(output/'portable')], 0),
        ([sys.executable, str(HERE/'demo.py'), '--intent', 'apple-reference', '--sealed-binary',
          str(output/'absent-original.dylib'), '--output', str(output/'native-request')], 2),
    ]
    rows=[]
    for index, (command, expected) in enumerate(commands):
        result=subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=60)
        log=output/f'command-{index}.log'
        log.write_text(result.stdout+result.stderr)
        rows.append({'command':command,'expected_exit':expected,'actual_exit':result.returncode,
                     'log_sha256':hashlib.sha256(log.read_bytes()).hexdigest()})
    actual={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in HERE.glob('*.py')}
    portable=json.loads((output/'portable/receipt.json').read_text())
    native=json.loads((output/'native-request/receipt.json').read_text())
    report={'candidate':'package-owned-execution','source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'prototype_source_sha256':sources,'prototype_sources_unchanged':sources==actual,
            'runtime':{'system':platform.system(),'release':platform.release(),'machine':platform.machine(),'python':sys.version},
            'commands':rows,'actual_portable_writer_pixels':portable['result']['written_pixels'],
            'captured_source_files':len(portable['source_sha256']),
            'captured_guided_dependency':'research/hdr-native/guided_reference_v3.py' in portable['source_sha256'],
            'native_request_outcome':native['result'],'native_calls':0,
            'proof_scope':'portable behavior and rejection logic only; no Apple compiler, original CPU, GPU or full camera verification',
            'passed':sources==actual and all(r['actual_exit']==r['expected_exit'] for r in rows)}
    (output/'proof.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    return 0 if report['passed'] else 1


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    raise SystemExit(prove(parser.parse_args().output.resolve()))
