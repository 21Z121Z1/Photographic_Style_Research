"""Re-run this candidate's actual CLI acceptance and historical failure shapes."""
from dataclasses import asdict, replace
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys

from coordinator import Coordinator, HERE, Intent, REPO


def main(output: Path):
    output.mkdir(parents=True, exist_ok=False)
    coordinator = Coordinator()
    input_file = output/'input.json'
    input_file.write_text(json.dumps({'pattern': 'colors', 'height': 2, 'width': 2,
                                    'field3': 0, 'selection': 'context'}, indent=2)+'\n')
    rows = []
    cases = [('portable_real_cli', 'portable-image', Intent.PORTABLE_MODEL),
             ('model_to_native_promotion', 'portable-image', Intent.APPLE_NATIVE),
             ('historical_runtime_mismatch', 'host-point-image', Intent.PORTABLE_MODEL),
             ('prepared_native_is_not_execution', 'sealed-pow', Intent.APPLE_NATIVE)]
    for name, capability, intent in cases:
        request = coordinator.prepare(capability, intent, input_file, output/name)
        result = coordinator.run(request)
        rows.append({'probe': name, **asdict(result)})
    dependency = 'research/hdr-native/guided_reference_v3.py'
    request = coordinator.prepare('portable-image', Intent.PORTABLE_MODEL, input_file, output/'missing_dependency')
    assert dependency in dict(request.source_snapshot)
    request = replace(request, source_snapshot=tuple((p, h) for p, h in request.source_snapshot if p != dependency))
    rows.append({'probe': 'missing_actual_dynamic_dependency', **asdict(coordinator.run(request))})
    manifest = coordinator.snapshot('portable-image')
    expected = {'portable_real_cli': 'model_only', 'model_to_native_promotion': 'blocked',
                'historical_runtime_mismatch': 'blocked', 'prepared_native_is_not_execution': 'blocked',
                'missing_actual_dynamic_dependency': 'blocked'}
    success = all(row['status'] == expected[row['probe']] for row in rows)
    result = {'candidate': 'registry-first',
              'repository_commit': subprocess.check_output(['git','rev-parse','HEAD'], cwd=REPO, text=True).strip(),
              'method': 'one accepted real 2x2 synthetic CLI invocation and four refused requests; no source mutation or Apple execution',
              'runtime': {'python': sys.version, 'system': platform.system(), 'machine': platform.machine()},
              'passed': success, 'rows': rows, 'portable_source_closure_count': len(manifest),
              'source_closure_contains_guided_dynamic_dependency': dependency in dict(manifest),
              'prototype_source_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                          for p in sorted(HERE.glob('*.py'))},
              'target_Apple_reference_compared': False,
              'limits': ['Closure is a conservative static overapproximation for imports and current literal Python file references, not arbitrary Python import proof',
                         'Original Apple execution is deliberately unavailable in this prototype',
                         'Python frozen values and runtime boundary checks are not a compiler proof of illegal-state exclusion']}
    (output/'probe-results.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({'passed': success, 'rows': [(r['probe'], r['status']) for r in rows],
                      'sources': len(manifest)}, indent=2))
    return 0 if success else 1


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    sys.exit(main(parser.parse_args().output))
