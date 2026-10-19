#!/usr/bin/env python3
"""Isolate unpatched native calls. A crash cannot erase the other controls."""
import json
from pathlib import Path
import subprocess
import sys

binary, output = sys.argv[1], Path(sys.argv[2])
output.mkdir(parents=True, exist_ok=True)
rows = []
for name in ['inventory', 'settings', 'processor-preflight', 'processor-nil-queue', 'processor-metal-queue', 'requirements-1', 'requirements-2', 'requirements-3', 'synthetic-standard-control', 'synthetic-studio-control',
             'missing-hardware', 'unsupported-version', 'empty-dictionary']:
    directory = output / name
    command = [binary, str(directory), '--inventory'] if name == 'inventory' else [binary, str(directory), '--case', name]
    if name.startswith('requirements-'):
        command = [binary, str(directory), '--requirements', name.rsplit('-',1)[1]]
    if name in ['settings','processor-preflight']:
        command = [binary,str(directory),'--'+name]
    if name in ['processor-nil-queue','processor-metal-queue']:
        command = [binary,str(directory),'--processor-preflight','--queue-'+('nil' if name=='processor-nil-queue' else 'metal')]
    print('NATIVE_PROCESS_BEGIN', name, flush=True)
    try:
        p = subprocess.run(command, capture_output=True, text=True, timeout=60)
        code, stdout, stderr = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as e:
        code = 124
        stdout = (e.stdout or b'').decode(errors='replace') if isinstance(e.stdout, bytes) else (e.stdout or '')
        stderr = (e.stderr or b'').decode(errors='replace') if isinstance(e.stderr, bytes) else (e.stderr or '')
    print(stdout, end='', flush=True); print(stderr, end='', flush=True)
    (output / (name+'.stdout.log')).write_text(stdout)
    (output / (name+'.stderr.log')).write_text(stderr)
    rows.append({'case':name, 'command':command, 'exit_code':code})
    print('NATIVE_PROCESS_END', name, 'exit_code='+str(code), flush=True)
    (output/'process-results.json').write_text(json.dumps(rows,indent=2)+'\n')
if any(r['exit_code'] for r in rows):
    sys.exit('NATIVE_PROBE_PROCESS_FAILED: see explicit per-case exits')
