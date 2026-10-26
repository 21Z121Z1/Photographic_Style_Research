"""Read native Check evidence through GitHub's API and independently replay checks.

No artifact URL, proxy change, system binary download or private photo is used.
The source hashes are checked against Git objects at the reported commit.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess

from native_reference import (REPO, check_root_wrapper, check_wrapper, classify_math,
                              encoded, unpack)
from native_texture_reference import compare_native, bit_mismatch_examples

NAMES = ('Styles fresh native reference','Styles native UnderEye reference capture')


def read_report(check: dict, head: str) -> dict:
    if check.get('head_sha') != head or check.get('status') != 'completed' or check.get('app',{}).get('slug') != 'github-actions':
        raise ValueError('Completed GitHub Actions check on the exact source HEAD required')
    text = check.get('output',{}).get('text')
    if not isinstance(text,str) or not text.startswith('```json\n') or not text.endswith('```'):
        raise ValueError('Machine-readable native evidence missing')
    report = unpack(json.loads(text[8:-3]))
    if report.get('git',{}).get('HEAD') != head:
        raise ValueError('Native report source HEAD differs from its Check')
    return report


def read(head: str, output: Path, repository: str) -> dict:
    if not re.fullmatch('[0-9a-f]{40}',head) or not re.fullmatch('[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',repository):
        raise ValueError('Exact 40-hex commit and owner/repository required')
    output.mkdir(parents=True,exist_ok=False)
    def github(path):
        return json.loads(subprocess.check_output(['gh','api',path],text=True))
    listing = github('repos/'+repository+'/commits/'+head+'/check-runs?per_page=100')
    reports = {}; checks = {}
    for name in NAMES:
        selected = sorted((c for c in listing['check_runs'] if c['name'] == name),key=lambda c:c['id'],reverse=True)
        if not selected: continue
        check = github('repos/'+repository+'/check-runs/'+str(selected[0]['id']))
        report = read_report(check,head)
        file = 'cpu' if name == NAMES[0] else 'texture'
        (output/(file+'-check.json')).write_bytes(encoded(check))
        (output/(file+'-report.json')).write_bytes(encoded(report))
        reports[file] = report
        checks[file] = {'id':check['id'],'url':check['html_url'],'conclusion':check['conclusion']}
    if 'cpu' not in reports:
        raise ValueError('CPU/capability reference check is absent')
    cpu = reports['cpu']; sources = cpu['source_sha256']
    for path,expected in sources.items():
        relative = PurePosixPath(path)
        if relative.is_absolute() or '..' in relative.parts:
            raise ValueError('Repository-relative source path required')
        raw = subprocess.check_output(['git','show',head+':'+path],cwd=REPO)
        if hashlib.sha256(raw).hexdigest() != expected:
            raise ValueError('Reported source differs from committed source: '+path)
    math = classify_math(cpu['math_raw'])
    if math != cpu['math_comparison'] or not cpu['sources_unchanged']:
        raise ValueError('CPU observations or source-mutation checks do not replay')
    asm = cpu['math_disassembly']
    if check_root_wrapper(asm) != cpu['math_static_checks']['sqrt'] or check_wrapper(asm.replace('_probe_power:','_psr_pow_read_call:')) != cpu['math_static_checks']['pow']:
        raise ValueError('Captured instruction checks do not replay')
    result = {'source_HEAD':head,'repository':repository,'checks':checks,
              'source_files_verified_against_git':len(sources),'CPU_math_replayed':math,
              'GPU_reference_replayed':False,'original_sealed_image_verified':False,
              'full_pipeline_verified':False}
    if 'texture_report_sha256' in cpu:
        if 'texture' not in reports:
            raise ValueError('Bound Texture report is missing')
        texture = reports['texture']
        if hashlib.sha256(encoded(texture)).hexdigest() != cpu['texture_report_sha256'] or texture['source_manifest_sha256'] != hashlib.sha256(encoded(sources)).hexdigest():
            raise ValueError('CPU/Texture evidence identities disagree')
        comparison = compare_native(texture['native'],texture['inputs'])
        if encoded(comparison) != encoded(texture['comparison']):
            raise ValueError('Native Texture comparison does not replay')
        result['GPU_reference_replayed'] = comparison['status'] == 'aligned_native_final_stage_observed'
        result['GPU_comparison'] = comparison
        result['GPU_half_bit_mismatch_examples'] = bit_mismatch_examples(texture['native'],texture['inputs'])
    (output/'verification.json').write_bytes(encoded(result))
    return result


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--head',required=True)
    parser.add_argument('--repository',default='21Z121Z1/Photographic_Style_Research')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    r=read(args.head,args.output,args.repository)
    print(json.dumps({k:v for k,v in r.items() if k not in ('GPU_comparison','GPU_half_bit_mismatch_examples')},indent=2))
