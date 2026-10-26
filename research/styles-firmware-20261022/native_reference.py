"""Collect a fresh Apple CPU/Metal capability reference, independent of S25/S33.

The runner executes synthetic input only. Public evidence contains JSON, source
hashes and our own disassembly; no system executable or photograph is exported.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import struct
import subprocess
import sys
import time
import urllib.request
import zlib

from image_chain_cli import git_identity, source_manifest
from pow_runtime_binding import BASE_SINGLE, EXPONENT_SINGLE, check_wrapper, single_value
from sqrt_double_round import COUNT, FIRST, LAST, sqrt32_rn
from square132_contract import rn, power_certificate, value

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]


def encoded(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)+'\n').encode()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def classify_math(raw: dict) -> dict:
    """Compare captured bits to the existing exact rational oracles."""
    if raw.get('schema') != 'psr-fresh-apple-cpu-v1' or raw.get('historical_sealed_image_loaded') is not False:
        raise ValueError('Fresh reference identity required; historical evidence cannot be substituted')
    if not re.fullmatch('[0-9a-f]{32}', raw.get('target_uuid', '')):
        raise ValueError('Actual loaded pow target UUID required')
    if any(not isinstance(raw.get(k), str) or not raw[k] for k in ('target_image', 'target_symbol')):
        raise ValueError('Actual pow symbol and image required')
    if type(raw.get('target_image_offset')) is not int or raw['target_image_offset'] < 0:
        raise ValueError('Actual pow target offset required')
    if type(raw.get('target_symbol_exact')) is not bool:
        raise ValueError('Symbol precision required')
    if type(raw.get('thread_before')) is not int or raw['thread_before'] <= 0 or raw['thread_before'] != raw.get('thread_after'):
        raise ValueError('Same observation thread required')
    if raw.get('pow_calls') != 1 or raw.get('sqrt_instructions') != COUNT:
        raise ValueError('Declared finite call counts required')

    def check_fpcr(before, after):
        if type(before) is not int or type(after) is not int or not 0 <= before < 2**64 or before != after:
            raise ValueError('Unchanged per-operation FPCR required')
        if before & ((3 << 22) | (1 << 26)):
            raise ValueError('RN and IEEE-half required; collector never sets FPCR')

    rows = raw.get('sqrt_rows')
    if not isinstance(rows, list) or len(rows) != COUNT:
        raise ValueError('All 2047 predeclared sqrt observations required')
    failures = []
    for expected_input, row in zip(range(FIRST, LAST+1), rows):
        if not isinstance(row, list) or len(row) != 5 or any(type(v) is not int for v in row) or row[0] != expected_input:
            raise ValueError('Ordered unique sqrt input rows required')
        code, single, half, before, after = row
        check_fpcr(before, after)
        expected_single = sqrt32_rn(code)
        expected_half = rn(single_value(expected_single))
        if single != expected_single or half != expected_half:
            failures.append({'input_half_bits':code, 'single_bits':single, 'half_bits':half,
                             'expected_single_bits':expected_single, 'expected_half_bits':expected_half})
    p = raw['power']
    if p['input_half_bits'] != [0x2b8f, 0x36aa] or p['input_single_bits'] != [BASE_SINGLE, EXPONENT_SINGLE]:
        raise ValueError('Exact predeclared half-to-f32 pow inputs required')
    check_fpcr(p['fpcr_before'], p['fpcr_after'])
    bits = p['output_single_bits']
    if type(bits) is not int or not 0 < bits < 0x7f7fffff:
        raise ValueError('Finite positive pow output required')
    x = single_value(bits)
    half = struct.unpack('<H', struct.pack('<e', float(x)))[0]
    if type(p['output_half_bits']) is not int or p['output_half_bits'] != half:
        raise ValueError('Observed RN narrowing must match the captured f32')
    lower = (single_value(bits-1)+x)/2
    upper = (x+single_value(bits+1))/2
    base, exponent = value(0x2b8f), value(0x36aa)
    target = base**exponent.numerator
    lo = target-lower**exponent.denominator
    hi = upper**exponent.denominator-target
    correct = (lo > 0 or lo == 0 and bits % 2 == 0) and (hi > 0 or hi == 0 and bits % 2 == 0)
    ideal_half = power_certificate(0x2b8f, 0x34ed)['power_half_bits']
    return {'scope':'new current Apple CPU only; not the historical sealed shim or GPU',
            'sqrt_input_half_domain':[FIRST,LAST], 'sqrt_observations':COUNT,
            'sqrt_single_or_half_mismatches':len(failures), 'sqrt_failure_examples':failures[:16],
            'pow_observations':1, 'pow_correctly_RN_f32_for_this_input':correct,
            'pow_matches_ideal_half_for_this_input':half == ideal_half,
            'pow_observed_single_bits':bits, 'pow_observed_half_bits':half,
            'original_sealed_image_verified':False, 'historical_calls_certified':False,
            'full_pipeline_verified':False}


def check_root_wrapper(disassembly: str) -> dict:
    match = re.search(r'^_probe_root:\s*\n(.*?)(?=^_\w[^\n]*:\s*$|\Z)', disassembly, re.M | re.S)
    if not match or re.search(r'\bmsr\s+FPCR\b', disassembly, re.I):
        raise ValueError('Root wrapper unavailable or FPCR write found')
    lines = match[1].splitlines()
    reads = [i for i, line in enumerate(lines) if re.search(r'\bmrs\s+[^,]+,\s*FPCR\b', line, re.I)]
    if len(reads) != 2:
        raise ValueError('Two root FPCR reads required')
    window = lines[reads[0]+1:reads[1]]
    operations = [token for token in ('fcvt', 'fsqrt') for line in window if re.search(r'\b'+token+r'\b', line)]
    if sorted(operations) != ['fcvt', 'fcvt', 'fsqrt'] or any(re.search(r'\b(?:bl|blr|blraa|blrab)\b', l) for l in window):
        raise ValueError('Root must contain two conversions and one direct FSQRT, without calls')
    return {'FPCR_reads':2, 'FPCR_writes':0, 'FSQRT_instructions':1, 'function_calls':0,
            'instruction_window_sha256':hashlib.sha256(encoded(window)).hexdigest()}


def envelope(report: dict) -> dict:
    raw = encoded(report)
    return {'encoding':'zlib+base64', 'uncompressed_bytes':len(raw),
            'sha256':hashlib.sha256(raw).hexdigest(),
            'payload':base64.b64encode(zlib.compress(raw, 9)).decode()}


def unpack(record: dict) -> dict:
    if record.get('encoding') != 'zlib+base64' or not 0 < record.get('uncompressed_bytes', 0) <= 2_000_000:
        raise ValueError('Bounded native reference envelope required')
    raw = zlib.decompress(base64.b64decode(record['payload'], validate=True))
    if len(raw) != record['uncompressed_bytes'] or hashlib.sha256(raw).hexdigest() != record['sha256']:
        raise ValueError('Native evidence length/SHA mismatch')
    return json.loads(raw)


def publish_check(report: dict, *, conclusion: str) -> dict:
    text = '```json\n'+encoded(envelope(report)).decode()+'```'
    if len(text.encode()) > 60_000:
        raise ValueError('Native evidence exceeds the GitHub Check text budget')
    body = {'name':'Styles fresh native reference', 'head_sha':os.environ['GITHUB_SHA'],
            'external_id':os.environ['GITHUB_RUN_ID']+'-'+os.environ['GITHUB_RUN_ATTEMPT'],
            'status':'completed', 'conclusion':conclusion,
            'output':{'title':'Fresh reference; historical S33 identity unchanged',
                      'summary':'CPU math and actual Metal availability. No private photos or system binaries.\n'
                                'The attached compressed JSON is SHA-bound, machine-readable text evidence.',
                      'text':text}}
    request = urllib.request.Request(
        os.environ['GITHUB_API_URL']+'/repos/'+os.environ['GITHUB_REPOSITORY']+'/check-runs',
        data=encoded(body), method='POST',
        headers={'Authorization':'Bearer '+os.environ['GH_TOKEN'], 'Accept':'application/vnd.github+json',
                 'Content-Type':'application/json', 'User-Agent':'psr-native-reference'})
    with urllib.request.urlopen(request, timeout=30) as response:
        result = json.load(response)
    return {'id':result['id'], 'html_url':result['html_url'], 'report_sha256':envelope(report)['sha256']}


def collect(output: Path, *, publish: bool = False) -> int:
    if platform.system() != 'Darwin' or platform.machine() != 'arm64':
        raise RuntimeError('Fresh native execution requires actual Darwin arm64; no emulated replacement')
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    report = {'schema':'psr-native-reference-v1', 'git':git_identity(),
              'system':{'system':platform.system(), 'machine':platform.machine(), 'python':sys.version,
                        'runner_image':os.environ.get('ImageOS'), 'runner_version':os.environ.get('ImageVersion')},
              'source_sha256':source_manifest(), 'commands':[], 'original_Apple_shim_calls':0,
              'original_sealed_image_available':False, 'full_pipeline_verified':False}

    def command(args: list[str], name: str) -> str:
        start = time.perf_counter()
        result = subprocess.run(args, cwd=REPO, text=True, capture_output=True, timeout=120)
        stdout, stderr = output/(name+'.stdout.txt'), output/(name+'.stderr.txt')
        stdout.write_text(result.stdout); stderr.write_text(result.stderr)
        report['commands'].append({'argv':args, 'returncode':result.returncode,
                                   'seconds':time.perf_counter()-start,
                                   'stdout_sha256':sha(stdout), 'stderr_sha256':sha(stderr)})
        if result.returncode:
            raise RuntimeError(name+' failed, exit '+str(result.returncode)+'; '+result.stderr[-1500:])
        return result.stdout

    conclusion = 'failure'
    try:
        report['system']['sw_vers'] = command(['sw_vers'], 'system')
        report['compiler_version'] = command(['xcrun','clang','--version'], 'compiler')
        compiler = Path(command(['xcrun','--find','clang'], 'compiler-path').strip()).resolve()
        report['compiler_sha256'] = sha(compiler)
        native = ROOT/'native-reference'
        math_exe, cap_exe = output/'math-probe', output/'capabilities'
        command(['xcrun','clang','-fobjc-arc','-O1','-framework','Foundation','-framework','Metal',
                 str(native/'capabilities.m'),'-o',str(cap_exe)], 'build-capabilities')
        report['capability_executable_sha256'] = sha(cap_exe)
        report['capabilities'] = json.loads(command([str(cap_exe)], 'capabilities'))
        command(['xcrun','clang','-arch','arm64','-std=c17','-O0','-frounding-math',
                 '-ffp-contract=off','-Wall','-Wextra','-Werror',str(native/'math_probe.c'),
                 '-o',str(math_exe)], 'build-math')
        asm = command(['xcrun','otool','-tvV',str(math_exe)], 'math-disassembly')
        report['math_disassembly'] = asm
        report['math_static_checks'] = {
            'pow':check_wrapper(asm.replace('_probe_power:', '_psr_pow_read_call:')),
            'sqrt':check_root_wrapper(asm)}
        report['math_executable_sha256'] = sha(math_exe)
        report['math_executable_UUID'] = command(['xcrun','dwarfdump','--uuid',str(math_exe)], 'math-uuid').strip()
        raw = json.loads(command([str(math_exe)], 'math-observation'))
        report['math_raw'] = raw
        report['math_comparison'] = classify_math(raw)
        report['status'] = 'fresh_CPU_observed_and_Metal_capabilities_recorded'
        conclusion = 'success' if report['math_comparison']['sqrt_single_or_half_mismatches'] == 0 else 'failure'
    except Exception as error:
        report['status'] = 'failed_with_retained_evidence'
        report['error'] = str(error)
    report['sources_unchanged'] = report['source_sha256'] == source_manifest()
    if not report['sources_unchanged']:
        conclusion = 'failure'
    report['conclusion'] = conclusion
    (output/'report.json').write_bytes(encoded(report))
    if publish:
        (output/'check.json').write_bytes(encoded(publish_check(report, conclusion=conclusion)))
    print(json.dumps({k:report.get(k) for k in ('status','error','math_comparison','capabilities','sources_unchanged')}, indent=2))
    return 0 if conclusion == 'success' else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--publish-check', action='store_true')
    args = parser.parse_args()
    sys.exit(collect(args.output, publish=args.publish_check))
