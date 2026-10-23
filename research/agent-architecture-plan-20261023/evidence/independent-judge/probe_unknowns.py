"""Verify black-domain failure propagation with frozen public prototype code."""
from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
BASE = '611ac4f6fe525ad3ba80ba5025aa8b5f0a45a079'
CANDIDATE_COMMIT = 'bc00b741219e7b9bced7dd9cf1d1cf6d38cd918d'
PREFIX = 'research/agent-architecture-plan-20261023/prototypes/'


def main(output):
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    with tempfile.TemporaryDirectory(prefix='architecture-judge-unknown-') as folder:
        copied = Path(folder)/'repo'
        copied.mkdir()
        source_manifest = {}
        roots = ('research/styles-firmware-20261022/', 'research/semantic-styles/', 'research/hdr-native/')
        for commit, predicate in ((BASE, lambda name: name.endswith('.py') and name.startswith(roots)),
                                  (CANDIDATE_COMMIT, lambda name: name.startswith(PREFIX) and name.endswith(('.py', 'registry.json')))):
            names = subprocess.check_output(['git', 'ls-tree', '-rz', '--name-only', commit], cwd=REPO).split(b'\0')
            for value in names:
                name = value.decode()
                if not predicate(name):
                    continue
                data = subprocess.check_output(['git', 'show', commit+':'+name], cwd=REPO)
                destination = copied/name
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(data)
                source_manifest[name] = hashlib.sha256(data).hexdigest()
        subprocess.run(['git', 'init', '-q', str(copied)], check=True)
        subprocess.run(['git', '-C', str(copied), 'add', '.'], check=True)
        subprocess.run(['git', '-C', str(copied), '-c', 'user.name=Identity probe', '-c', 'user.email=probe@example.invalid', 'commit', '-qm', 'Frozen public sources for black-domain probe'], check=True)
        sys.path.insert(0, str(copied/PREFIX/'candidate_package'))
        from execution import Study, Selection
        sys.path.insert(0, str(copied/PREFIX/'candidate_registry'))
        from coordinator import Coordinator, Intent
        source = json.loads(subprocess.check_output(['git', 'show', BASE+':research/styles-firmware-20261022/evidence/complete-context-s15a.json'], cwd=REPO))
        for i in (0, 1):
            for row in source['images_half_bits'][i]:
                for pixel in row:
                    pixel[:3] = [0, 0, 0]
        path = output/'black-context.json'
        path.write_text(json.dumps(source, indent=2)+'\n')
        a = Study.portable(copied, path, selection=Selection.BRIGHT16).run(output/'a-unknown')
        spec = output/'black-spec.json'
        spec.write_text(json.dumps({'pattern': 'zero', 'height': 2, 'width': 2, 'field3': 0, 'selection': 'experimental-bright16'})+'\n')
        coord = Coordinator(copied, copied/PREFIX/'candidate_registry/registry.json')
        b = coord.run(coord.prepare('portable-image', Intent.PORTABLE_MODEL, spec, output/'b-unknown'))
        result = {'scope': 'frozen public sources, actual black-domain negative runs',
                  'model_baseline_commit': BASE, 'candidate_commit': CANDIDATE_COMMIT,
                  'source_manifest_sha256': hashlib.sha256(json.dumps(source_manifest, sort_keys=True).encode()).hexdigest(),
                  'candidate_source_sha256': {name: digest for name, digest in source_manifest.items() if name.startswith(PREFIX)},
                  'input_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (path, spec)},
                  'candidate_A_outcome': type(a).__name__, 'candidate_A_result': asdict(a),
                  'candidate_B_status': b.status, 'candidate_B_evidence_level': b.evidence_level,
                  'candidate_B_reason': b.reason,
                  'candidate_B_writer_count': json.loads((output/'b-unknown/cli/summary.json').read_text())['summary']['writers'],
                  'native_calls': 0, 'model_or_CLI_runs': 2}
        assert type(a).__name__ == 'UnresolvedModel' and b.status == 'unknown' and result['candidate_B_writer_count'] == 0
        (output/'source-manifest.json').write_text(json.dumps(source_manifest, indent=2)+'\n')
        (output/'unknown-results.json').write_text(json.dumps(result, indent=2)+'\n')
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage: probe_unknowns.py NEW_OUTPUT_DIRECTORY')
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    main(Path(sys.argv[1]))
