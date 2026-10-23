"""Replay registry drift with an isolated copy of the selected coordinator bytes."""
from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import subprocess
import sys


REPO = Path(__file__).resolve().parents[4]
SOURCE = Path('research/agent-architecture-plan-20261023/prototypes/candidate_registry/coordinator.py')
REGISTRY = SOURCE.with_name('registry.json')


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--revision', help='Read the committed source with git show; default: working bytes')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    source = (subprocess.check_output(['git', 'show', f'{args.revision}:{SOURCE}'], cwd=REPO)
              if args.revision else (REPO/SOURCE).read_bytes())
    source_copy = output/'coordinator-under-test.py'
    source_copy.write_bytes(source)
    spec = importlib.util.spec_from_file_location('registry_drift_under_test', source_copy)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    input_file = output/'input.json'
    input_file.write_text(json.dumps({'pattern': 'colors', 'height': 2, 'width': 2,
                                      'field3': 0, 'selection': 'context'})+'\n')
    original_registry = (REPO/REGISTRY).read_bytes()

    def changed_registry(path: Path) -> None:
        raw = json.loads(path.read_bytes())
        raw['capabilities']['portable-image']['availability'] = 'prepared-only'
        path.write_text(json.dumps(raw, indent=2)+'\n')

    before = output/'before-registry.json'
    before.write_bytes(original_registry)
    old = module.Coordinator(repo=REPO, registry=before)
    changed_registry(before)
    loaded_hash = sha(original_registry)
    changed_hash = sha(before.read_bytes())
    prepare_error = None
    old_result = None
    try:
        request = old.prepare('portable-image', module.Intent.PORTABLE_MODEL,
                              input_file, output/'old-object-run')
    except ValueError as exc:
        prepare_error = str(exc)
    else:
        old_result = old.run(request)
    fresh = module.Coordinator(repo=REPO, registry=before)
    fresh_result = fresh.run(fresh.prepare('portable-image', module.Intent.PORTABLE_MODEL,
                                          input_file, output/'fresh-object-run'))

    after = output/'after-registry.json'
    after.write_bytes(original_registry)
    prepared = module.Coordinator(repo=REPO, registry=after)
    request = prepared.prepare('portable-image', module.Intent.PORTABLE_MODEL,
                               input_file, output/'after-prepare-run')
    changed_registry(after)
    after_result = prepared.run(request)
    before_rejected = (prepare_error is not None and not (output/'old-object-run').exists())
    fresh_blocked = fresh_result.status == 'blocked' and not (output/'fresh-object-run/cli').exists()
    after_blocked = after_result.status == 'blocked' and not (output/'after-prepare-run/cli').exists()
    old_snapshot = dict(old_result.source_snapshot) if old_result else {}
    relative_registry = str(before.relative_to(REPO))
    report = {
        'command': sys.argv,
        'repository_head_at_run': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip(),
        'source_revision': args.revision,
        'source_path': str(SOURCE),
        'source_sha256': sha(source),
        'loaded_registry_sha256': loaded_hash,
        'changed_registry_sha256': changed_hash,
        'system': platform.platform(), 'python': sys.version,
        'before_prepare': {
            'prepare_error': prepare_error,
            'old_object_result': asdict(old_result) if old_result else None,
            'old_snapshot_binds_changed_registry': old_snapshot.get(relative_registry) == changed_hash,
            'fresh_object_result': asdict(fresh_result),
            'rejected_before_output': before_rejected,
        },
        'after_prepare': {'result': asdict(after_result), 'blocked_without_cli': after_blocked},
        'checks': {'changed_before_prepare_rejected': before_rejected,
                   'fresh_object_uses_changed_policy': fresh_blocked,
                   'changed_after_prepare_blocked': after_blocked},
        'native_calls': 0,
        'scope': 'Actual 2x2 portable CLI when admitted; isolated registry copies; no Apple reference or native invocation',
    }
    report['passed'] = all(report['checks'].values())
    (output/'result.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({'passed': report['passed'], 'checks': report['checks'],
                      'source_sha256': report['source_sha256'], 'native_calls': 0}, indent=2))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
