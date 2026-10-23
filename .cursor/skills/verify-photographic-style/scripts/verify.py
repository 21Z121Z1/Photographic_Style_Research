#!/usr/bin/env python3
"""Drive the real synthetic CLI and independently inspect persisted evidence."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import pty
import select
import shutil
import subprocess
import sys
import time

REPO = Path(__file__).resolve().parents[4]
MODEL = REPO / 'research/styles-firmware-20261022'


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path):
    def reject(value):
        raise ValueError('Nonfinite JSON number: ' + value)
    return json.loads(path.read_text(), parse_constant=reject)


def write(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n')


def revision() -> str:
    return subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip()


def local_path(root: Path, relative: str) -> Path:
    if type(relative) is not str or Path(relative).is_absolute():
        raise ValueError('Relative evidence path required')
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError('Evidence file is absent or outside the declared root: ' + relative)
    return path


def doctor() -> dict:
    import numpy as np
    import PIL
    required = {'Python 3.13': sys.version_info[:2] == (3, 13),
                'math.fma': hasattr(math, 'fma'),
                'NumPy 2.2.4': np.__version__ == '2.2.4',
                'Pillow 11.1.0': PIL.__version__ == '11.1.0',
                'synthetic CLI': (MODEL / 'image_chain_cli.py').is_file()}
    return {'repository': str(REPO), 'git_HEAD': revision(),
            'system': platform.system(), 'architecture': platform.machine(),
            'python': sys.version, 'numpy': np.__version__, 'pillow': PIL.__version__,
            'requirements': required, 'portable_ready': all(required.values()),
            'native_journey_status': 'BLOCKED until exact sealed binary and expected Apple OS build are explicitly supplied',
            'native_validation_performed': False, 'helper_sha256': sha(Path(__file__))}


def terminal(command: list[str], timeout: float = 60) -> dict:
    master, slave = pty.openpty()
    started = time.monotonic()
    env = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
    process = subprocess.Popen(command, cwd=REPO, stdin=subprocess.DEVNULL,
                               stdout=slave, stderr=slave, env=env)
    os.close(slave)
    chunks = []
    timed_out = False
    try:
        while True:
            if time.monotonic() - started > timeout and process.poll() is None:
                timed_out = True
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
            ready, _, _ = select.select([master], [], [], .1)
            if ready:
                try:
                    part = os.read(master, 65536)
                except OSError:
                    break
                if not part:
                    break
                chunks.append(part)
            elif process.poll() is not None:
                break
        code = process.wait(timeout=5)
    finally:
        os.close(master)
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=5)
    return {'command': command, 'cwd': str(REPO), 'child_pid': process.pid,
            'child_reaped': process.poll() is not None, 'exit_code': code,
            'timed_out': timed_out, 'elapsed_seconds': time.monotonic() - started,
            'transcript': b''.join(chunks).decode('utf-8', errors='replace')}


def effective_input_sha(context_data: dict, request: dict) -> str:
    import numpy as np
    sys.path.insert(0, str(MODEL))
    from complete_fixture import decode
    c = decode(context_data)
    images = list(c.images)
    for index, name in ((6, 'person'), (7, 'skin'), (8, 'sky')):
        if name in request['missing_masks']:
            images[index] = np.zeros_like(images[index])
    params = c.params.copy()
    if request['selection'] == 'experimental_raw_cast16':
        params.view('u4')[0] = 16
    digest = hashlib.sha256()
    for array in (*images, c.management, params, c.stats, c.roi, c.srl, c.output_initial):
        digest.update(str(array.shape).encode())
        digest.update(array.dtype.str.encode())
        digest.update(array.tobytes())
    digest.update(repr((c.gtc.red_samples, c.gtc.coordinate_space, c.whites.red_samples,
                        c.whites.coordinate_space, c.producer_shape,
                        int(np.array(c.epsilon).view('u4')), c.version, c.hardware, c.build)).encode())
    return digest.hexdigest()


def verify_summary(summary: dict, folder: Path) -> dict:
    import numpy as np
    if summary.get('git', {}).get('HEAD') != revision():
        raise ValueError('Evidence HEAD differs from the checked-out HEAD')
    if summary.get('source_snapshot_stable') is not True or summary.get('source_changes_during_run'):
        raise ValueError('Source snapshot changed during the original run')
    before, after = summary['source_sha256_before'], summary['source_sha256_after']
    if not before or before != after:
        raise ValueError('Before and after source manifests disagree')
    for path, expected in after.items():
        if sha(local_path(REPO, path)) != expected:
            raise ValueError('Stale source hash: ' + path)
    truth = {'evidence_level': 'model_only', 'Apple_pipeline_verified': False,
             'native_calls': 0, 'GPU_calls': 0, 'numerics': 'experimental_portable_point'}
    for key, expected in truth.items():
        if type(summary.get(key)) is not type(expected) or summary[key] != expected:
            raise ValueError('Invalid portable evidence claim: ' + key)
    writers, unknowns = 0, 0
    for row in summary['runs']:
        case = folder / row['id']
        if Path(row['id']).name != row['id']:
            raise ValueError('Invalid case path')
        if load(case / 'result.json') != row:
            raise ValueError('Summary differs from the persisted case result')
        for filename, expected in row['files_sha256'].items():
            if Path(filename).name != filename or sha(local_path(case, filename)) != expected:
                raise ValueError('Case artifact hash differs: ' + filename)
        request = load(case / 'run-request.json')
        if sha(case / 'context.json') != row['input_context_sha256'] or sha(case / 'run-request.json') != row['input_request_sha256']:
            raise ValueError('Raw context or request identity differs')
        if request['input_context_sha256'] != row['input_context_sha256'] or request['context_json_is_before_declared_overrides'] is not True:
            raise ValueError('Raw context does not declare its override boundary')
        for name in ('selection', 'numerics', 'missing_masks'):
            if request[name] != summary[name]:
                raise ValueError('Request differs from actual invocation: ' + name)
        if row.get('evidence_level') != 'model_only' or row.get('native_reference_compared') is not False or row.get('Apple_accuracy_validated') is not False:
            raise ValueError('Portable case promotes its evidence level')
        provenance = row.get('provenance', {})
        for key, expected in {'native_calls': 0, 'GPU_calls': 0, 'native_intermediates_used': False,
                              'native_reference_compared': False,
                              'inherits_S25_S29_S30_bit_certification': False}.items():
            if type(provenance.get(key)) is not type(expected) or provenance[key] != expected:
                raise ValueError('Portable case claims a native source: ' + key)
        if effective_input_sha(load(case / 'context.json'), request) != provenance['raw_input_sha256']:
            raise ValueError('Effective input identity does not match raw arrays and declared overrides')
        with np.load(case / 'checkpoints.npz', allow_pickle=False) as archive:
            if 'writer_sha256' not in row:
                unknowns += 1
                if 'writer__lo' in archive:
                    raise ValueError('Unknown case persisted a final writer')
                continue
            writers += 1
            pixels, written = archive['writer__lo'], archive['writer__written_mask']
            if pixels.dtype != np.dtype('f2') or written.dtype != np.dtype(bool) or written.shape != pixels.shape[:2]:
                raise ValueError('Writer storage contract differs')
            if not np.isfinite(pixels).all() or int(written.sum()) != row['written_pixels']:
                raise ValueError('Written extent or finite output differs')
            if sha_bytes(pixels.tobytes()) != row['writer_sha256'] or not np.all(pixels[written, 3] == 1):
                raise ValueError('Writer pixels or written alpha differ')
            for name in ('raw_BG__lo', 'BG_output__lo', 'output600__lo'):
                if name not in archive:
                    raise ValueError('Missing source-to-writer checkpoint: ' + name)
            selected = next(branch for branch in row['branches'] if branch['destination'] == 'selected404')['selected']
            expected_selected = 'bright400' if summary['selection'] == 'experimental_raw_cast16' else 'skin393'
            if selected != expected_selected or not np.array_equal(archive['selected404__lo'], archive[selected + '__lo']):
                raise ValueError('Persisted selected branch does not match the requested route')
    if writers != summary['summary']['writers'] or unknowns != summary['summary']['blocked_or_unknown']:
        raise ValueError('Batch counts differ from persisted case states')
    return {'status': 'PASS_portable_artifact_journey', 'verified_HEAD': revision(),
            'cases': len(summary['runs']), 'writers': writers, 'unknowns': unknowns,
            'source_files_checked': len(after), 'Apple_validation': False,
            'native_calls': 0, 'effective_input_hashes_recomputed': True}


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def inspect(folder: Path) -> dict:
    return verify_summary(load(folder / 'summary.json'), folder)


def rejection_probes(folder: Path) -> dict:
    summary = load(folder / 'summary.json')
    bad_claim = copy.deepcopy(summary)
    bad_claim['Apple_pipeline_verified'] = True
    stale = copy.deepcopy(summary)
    first = next(iter(stale['source_sha256_before']))
    stale['source_sha256_before'][first] = '0' * 64
    stale['source_sha256_after'][first] = '0' * 64
    results = []
    for name, forged in [('portable_result_labelled_Apple', bad_claim), ('stale_source_manifest', stale)]:
        try:
            verify_summary(forged, folder)
        except ValueError as error:
            results.append({'probe': name, 'rejected': True, 'reason': str(error)})
        else:
            raise ValueError('Negative probe was accepted: ' + name)
    return {'status': 'PASS_negative_evidence_checks', 'probes': results,
            'historical_artifacts_modified': False,
            'scope': 'adversarial mutations of an in-memory copy of this new real CLI report'}


def seal_manifest(evidence: Path, feature: str) -> None:
    manifest = {str(path.relative_to(evidence)): sha(path) for path in sorted(evidence.rglob('*'))
                if path.is_file() and '.scratch' not in path.parts}
    write(evidence / 'manifest.json', {'source_commit': revision(), 'feature': feature,
                                     'files_sha256': manifest})


def drive(evidence: Path, feature: str) -> int:
    state = doctor()
    if not state['portable_ready']:
        raise ValueError('Doctor failed; inspect dependencies before driving')
    evidence.mkdir(parents=True, exist_ok=False)
    write(evidence / 'doctor.json', state)
    scratch = evidence / '.scratch'
    scratch.mkdir()
    write(scratch / 'owned.json', {'helper': str(Path(__file__)), 'pid': os.getpid()})
    output = evidence / 'cli-output'
    if feature == 'native-preflight':
        command = [sys.executable, str(MODEL / 'pow_runtime_binding.py'), 'preflight', '--output', str(evidence / 'native-preflight.json')]
    else:
        command = [sys.executable, str(MODEL / 'image_chain_cli.py'), '--numerics', 'experimental-portable',
                   '--patterns', 'zero' if feature == 'zero-input' else 'gradient', '--height', '2', '--width', '2',
                   '--values', '0', '.125', '--output', str(output)]
        if feature in ('bright-smoke', 'zero-input', 'missing-masks'):
            command += ['--selection', 'experimental-bright16']
        if feature == 'missing-masks':
            command += ['--missing-masks', 'person', 'skin', 'sky']
    capture = terminal(command)
    (evidence / 'terminal.log').write_text(capture.pop('transcript'))
    write(evidence / 'command.json', capture)
    if not capture['child_reaped'] or capture['timed_out']:
        raise ValueError('CLI did not complete; retained command and terminal evidence')
    if feature == 'native-preflight':
        result = load(evidence / 'native-preflight.json')
        if capture['exit_code'] != 0 or result['status'] != 'blocked_before_compile_load_or_call' or result['native_calls'] != 0 or result['compilations'] != 0:
            raise ValueError('This journey must not compile or invoke an absent native target')
        write(evidence / 'verification.json', {'status': 'BLOCKED_native_material',
              'native_validation_performed': False, 'blockers': result['blockers'],
              'preflight_executed': True})
        seal_manifest(evidence, feature)
        return 2
    expected_exit = 2 if feature == 'zero-input' else 0
    if capture['exit_code'] != expected_exit:
        raise ValueError('Unexpected CLI exit; see retained terminal.log')
    verified = inspect(output)
    if feature == 'zero-input' and verified['writers'] != 0:
        raise ValueError('Black-domain negative journey unexpectedly produced a writer')
    write(evidence / 'verification.json', verified)
    write(evidence / 'negative-probes.json', rejection_probes(output))
    seal_manifest(evidence, feature)
    return 0


def cleanup(evidence: Path) -> dict:
    owned = load(evidence / '.scratch/owned.json')
    if owned['helper'] != str(Path(__file__)):
        raise ValueError('Scratch owner differs; refusing cleanup')
    manifest = load(evidence / 'manifest.json') if (evidence / 'manifest.json').is_file() else None
    shutil.rmtree(evidence / '.scratch')
    preserved = manifest is None or all(sha(local_path(evidence, path)) == expected
                                     for path, expected in manifest['files_sha256'].items())
    status = ('PASS_cleanup_evidence_retained' if manifest else 'CLEANUP_partial_evidence_retained') if preserved else 'FAIL_evidence_changed'
    result = {'status': status,
              'process_action': 'none; the exact child PID was synchronously reaped by drive',
              'removed': '.scratch only', 'evidence_retained': preserved,
              'manifest_sha256': sha(evidence / 'manifest.json') if manifest else None}
    write(evidence / 'cleanup.json', result)
    if not preserved:
        raise ValueError('Cleanup changed proof artifacts')
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='mode', required=True)
    sub.add_parser('doctor')
    for mode in ('inspect', 'reject-probes', 'cleanup'):
        sub.add_parser(mode).add_argument('--evidence', type=Path, required=True)
    task = sub.add_parser('drive')
    task.add_argument('--evidence', type=Path, required=True)
    task.add_argument('--feature', choices=['portable-smoke', 'bright-smoke', 'zero-input', 'missing-masks', 'native-preflight'], default='portable-smoke')
    args = parser.parse_args()
    if args.mode == 'doctor':
        result = doctor()
        print(json.dumps(result, indent=2))
        return 0 if result['portable_ready'] else 2
    if args.mode == 'drive':
        return drive(args.evidence.resolve(), args.feature)
    result = cleanup(args.evidence.resolve()) if args.mode == 'cleanup' else rejection_probes(args.evidence.resolve()) if args.mode == 'reject-probes' else inspect(args.evidence.resolve())
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
