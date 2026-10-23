"""Reproduce the bounded planning claims; never certify an Apple pipeline."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time


REPO = Path(__file__).resolve().parents[3]
PLAN = Path(__file__).resolve().parents[1]
INITIAL = 'bc00b741219e7b9bced7dd9cf1d1cf6d38cd918d'


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot() -> dict:
    paths = subprocess.check_output(['git', 'ls-files', '-z'], cwd=REPO).split(b'\0')
    suffixes = {'.py', '.c', '.m', '.swift', '.metal', '.yml', '.yaml'}
    sources = {p.decode(): sha(REPO/p.decode()) for p in paths
               if p and Path(p.decode()).suffix in suffixes}
    return {'HEAD': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip(),
            'sources_sha256': sources}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path,
                        help='A new directory inside this checkout, usually artifacts/architecture-plan-new')
    args = parser.parse_args()
    output = args.output.resolve()
    if not output.is_relative_to(REPO):
        parser.error('Output must be inside the checkout for isolated registry-copy identities')
    output.mkdir(parents=True, exist_ok=False)
    before = snapshot()
    (output/'before.json').write_text(json.dumps(before, indent=2)+'\n')
    steps = []

    def run(name: str, argv: list[str | Path], expected: int = 0) -> None:
        begin = time.perf_counter()
        process = subprocess.run(list(map(str, argv)), cwd=REPO, capture_output=True, text=True,
                                 timeout=240, env={**os.environ, 'OPENBLAS_NUM_THREADS': '1',
                                                  'OMP_NUM_THREADS': '1', 'PYTHONDONTWRITEBYTECODE': '1'})
        log = output/(name+'.log')
        log.write_text(process.stdout+process.stderr)
        steps.append({'name': name, 'argv': list(map(str, argv)), 'exit_code': process.returncode,
                      'expected_exit_code': expected, 'matches_expected': process.returncode == expected,
                      'elapsed_seconds': time.perf_counter()-begin, 'log_sha256': sha(log)})
        print(name+': '+str(process.returncode), flush=True)

    python = sys.executable
    for candidate, test in [('candidate_package', 'test_execution.py'), ('candidate_registry', 'test_coordinator.py')]:
        run(candidate, [python, '-m', 'unittest', 'discover', '-s', PLAN/'prototypes'/candidate,
                        '-p', test, '-v'])
    run('historical_replays', [python, PLAN/'tools/mine_history.py', '--output', output/'history'])
    run('initial_candidate_failures', [python, PLAN/'evidence/independent-judge/reproduce_boundaries.py',
                                      output/'initial-candidate-failures', '--candidate-commit', INITIAL])
    replay = PLAN/'evidence/registry-fix-round/replay_registry_drift.py'
    run('registry_red', [python, replay, '--revision', INITIAL, '--output', output/'registry-red'], 1)
    run('registry_green', [python, replay, '--output', output/'registry-green'])
    for folder, expected in [('registry-red', False), ('registry-green', True)]:
        result_file = output/folder/'result.json'
        valid = result_file.is_file() and json.loads(result_file.read_text())['passed'] is expected
        steps.append({'name': folder+'_semantic_result', 'matches_expected': valid})
    run('unsupported_black', [python, PLAN/'evidence/independent-judge/probe_unknowns.py', output/'unsupported-black'])
    helper = REPO/'.cursor/skills/verify-photographic-style/scripts/verify.py'
    run('doctor', [python, helper, 'doctor'])
    portable = output/'portable'
    run('portable_drive', [python, helper, 'drive', '--feature', 'portable-smoke', '--evidence', portable])
    run('portable_inspect', [python, helper, 'inspect', '--evidence', portable/'cli-output'])
    run('portable_reject_probes', [python, helper, 'reject-probes', '--evidence', portable/'cli-output'])
    run('portable_cleanup', [python, helper, 'cleanup', '--evidence', portable])
    native = output/'native-preflight'
    run('native_preflight_expected_block', [python, helper, 'drive', '--feature', 'native-preflight', '--evidence', native], 2)
    run('native_cleanup', [python, helper, 'cleanup', '--evidence', native])
    after = snapshot()
    (output/'after.json').write_text(json.dumps(after, indent=2)+'\n')
    stable = before == after
    report = {'schema': 'psr-architecture-plan-check-v1', 'source_commit': before['HEAD'],
              'python': sys.version, 'system': platform.platform(), 'machine': platform.machine(),
              'source_snapshot_stable': stable, 'steps': steps,
              'scoped_checks_match_expectations': stable and all(s['matches_expected'] for s in steps),
              'scope': 'planning prototypes, exact historical Python replays, real synthetic CLI and evidence helper',
              'original_Apple_calls': 0, 'Apple_pipeline_verified': False,
              'native_preflight_is_expected_blocked': True,
              'full_repository_suite_run': False,
              'artifacts_sha256': {str(p.relative_to(output)): sha(p) for p in sorted(output.rglob('*')) if p.is_file()}}
    (output/'receipt.json').write_text(json.dumps(report, indent=2)+'\n')
    return 0 if report['scoped_checks_match_expectations'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
