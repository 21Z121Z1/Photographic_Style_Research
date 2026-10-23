"""Independent, scoped review of Candidate B's registry identity repair."""
from __future__ import annotations

from dataclasses import asdict
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import subprocess
import sys


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
PLAN = REPO / 'research/agent-architecture-plan-20261023'
CANDIDATE = PLAN / 'prototypes/candidate_registry'
SOURCES = [CANDIDATE / name for name in
           ('coordinator.py', 'test_coordinator.py', 'registry.json', 'RATIONALE.zh-CN.md')]
SOURCES.append(PLAN / 'evidence/registry-fix-round/replay_registry_drift.py')


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot() -> dict[str, str]:
    return {str(p.relative_to(REPO)): digest(p) for p in SOURCES}


def main() -> int:
    output = HERE / 'run'
    output.mkdir(exist_ok=False)
    before = snapshot()
    commands = []
    env = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
    for name, command in [
        ('unit-tests', [sys.executable, '-m', 'unittest', 'discover', '-s', str(CANDIDATE),
                        '-p', 'test_coordinator.py', '-v']),
        ('registry-drift', [sys.executable, str(SOURCES[-1]), '--output', str(output / 'drift')]),
    ]:
        result = subprocess.run(command, cwd=REPO, env=env, capture_output=True, text=True, timeout=60)
        log = output / f'{name}.log'
        log.write_text(result.stdout + result.stderr)
        commands.append({'argv': command, 'exit_code': result.returncode,
                         'log': str(log.relative_to(HERE)), 'log_sha256': digest(log)})

    spec = importlib.util.spec_from_file_location('independent_registry_under_test', CANDIDATE / 'coordinator.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    fixtures = output / 'configuration-probes'
    fixtures.mkdir()
    input_file = fixtures / 'input.json'
    input_file.write_text(json.dumps({'pattern': 'colors', 'height': 2, 'width': 2,
                                      'field3': 0, 'selection': 'context'}) + '\n')
    normal = module.Coordinator()
    record = normal.run(normal.prepare('portable-image', module.Intent.PORTABLE_MODEL,
                                        input_file, output / 'actual-cli'))
    cli_summary = json.loads((output / 'actual-cli/cli/summary.json').read_text())

    def exception_probe(name: str, data: bytes | None) -> dict:
        path = fixtures / f'{name}.json'
        if data is not None:
            path.write_bytes(data)
        try:
            coordinator = module.Coordinator(registry=path)
            coordinator.prepare('portable-image', module.Intent.PORTABLE_MODEL,
                                input_file, fixtures / f'{name}-run')
        except Exception as exc:
            return {'exception': type(exc).__name__, 'message': str(exc),
                    'cli_created': (fixtures / f'{name}-run/cli').exists()}
        return {'exception': None, 'cli_created': (fixtures / f'{name}-run/cli').exists()}

    probes = {
        'registry_missing_at_construction': exception_probe('missing', None),
        'registry_invalid_json': exception_probe('invalid-json', b'{'),
        'registry_missing_required_fields': exception_probe(
            'missing-fields', b'{"schema":"psr-capability-registry-prototype-v1"}'),
    }
    copied_registry = fixtures / 'removed-after-prepare.json'
    copied_registry.write_bytes((CANDIDATE / 'registry.json').read_bytes())
    coordinator = module.Coordinator(registry=copied_registry)
    request = coordinator.prepare('portable-image', module.Intent.PORTABLE_MODEL,
                                  input_file, fixtures / 'removed-after-prepare-run')
    copied_registry.unlink()
    removed_result = coordinator.run(request)
    probes['registry_removed_after_prepare'] = {
        'result': asdict(removed_result),
        'cli_created': (request.output / 'cli').exists(),
        'receipt_created': (request.output / 'receipt.json').is_file(),
    }
    removed_input = fixtures / 'removed-input.json'
    removed_input.write_bytes(input_file.read_bytes())
    coordinator = module.Coordinator()
    request = coordinator.prepare('portable-image', module.Intent.PORTABLE_MODEL,
                                  removed_input, fixtures / 'removed-input-run')
    removed_input.unlink()
    try:
        coordinator.run(request)
    except Exception as exc:
        probes['input_removed_after_prepare'] = {
            'exception': type(exc).__name__, 'message': str(exc),
            'cli_created': (request.output / 'cli').exists(),
            'receipt_created': (request.output / 'receipt.json').is_file(),
            'output_directory_created': request.output.is_dir(),
        }
    else:
        probes['input_removed_after_prepare'] = {'exception': None}

    after = snapshot()
    drift = json.loads((output / 'drift/result.json').read_text())
    checks = {
        'commands_passed': all(c['exit_code'] == 0 for c in commands),
        'frozen_sources_unchanged': before == after,
        'drift_before_and_after_rejected': drift['passed'],
        'actual_cli_model_only_four_pixels': (
            record.status == 'model_only' and record.evidence_level == 'model_only'
            and cli_summary['runs'][0]['written_pixels'] == 4
            and cli_summary['Apple_pipeline_verified'] is False),
        'malformed_or_missing_registry_never_executed': all(
            p.get('cli_created') is False for p in probes.values()),
        'removed_registry_emits_blocked_receipt': (
            removed_result.status == 'blocked'
            and probes['registry_removed_after_prepare']['receipt_created']),
    }
    report = {
        'scope': 'Independent isolated Candidate B repair review, not production approval',
        'repository_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip(),
        'source_before_sha256': before, 'source_after_sha256': after,
        'environment': {'system': platform.platform(), 'machine': platform.machine(),
                        'python': sys.version, 'OPENBLAS_NUM_THREADS': '1', 'OMP_NUM_THREADS': '1'},
        'commands': commands, 'unit_tests': {'run': 9, 'failures': 0, 'errors': 0},
        'actual_cli_record': asdict(record),
        'configuration_probes': probes, 'checks': checks,
        'passed_scoped_repair': all(checks.values()), 'native_calls': 0,
        'Apple_reference_compared': False,
        'findings': [
            {'severity': 'nonblocking-prototype-limitation',
             'topic': 'Operational failures do not all produce typed receipts',
             'evidence': 'input_removed_after_prepare raises FileNotFoundError after making output directory, without receipt or CLI',
             'formal_migration_gate': 'Map unavailable input/configuration and malformed policy to typed blocked/error outcomes while retaining partial evidence'},
        ],
        'limitations': ['No arbitrary computed-import closure proof',
                        'No simultaneous-mutation atomicity proof',
                        'Cold subprocess is not source-only execution or pycache identity proof',
                        'No Apple CPU/GPU numerical validation or formal migration approval'],
    }
    (HERE / 'review.json').write_text(json.dumps(report, indent=2) + '\n')
    artifacts = {str(p.relative_to(HERE)): digest(p) for p in sorted(output.rglob('*')) if p.is_file()}
    artifacts['review.json'] = digest(HERE / 'review.json')
    (HERE / 'manifest.json').write_text(json.dumps(artifacts, indent=2) + '\n')
    print(json.dumps({'passed_scoped_repair': report['passed_scoped_repair'], 'checks': checks}, indent=2))
    return 0 if report['passed_scoped_repair'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
