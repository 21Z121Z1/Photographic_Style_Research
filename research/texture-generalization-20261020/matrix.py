"""Run immutable XDRemux real-media fixtures through native Texture production."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
PRODUCER = HERE.parent / 'texture-producer-20261020'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(args, root, name, env=None, timeout=180):
    with (root / (name + '.stdout.log')).open('wb') as out, (root / (name + '.stderr.log')).open('wb') as err:
        try:
            result = subprocess.run([str(a) for a in args], stdout=out, stderr=err, timeout=timeout, env=env)
            code = result.returncode
        except subprocess.TimeoutExpired:
            code = 'timeout'
    return code


def compile_tools(build):
    build.mkdir(parents=True, exist_ok=True)
    for name, source in [('prepare', HERE / 'prepare_input.m')]:
        args = ['xcrun', 'clang', '-g', '-O0', '-fobjc-arc', '-fblocks', '-Wall', '-Wextra', source]
        for framework in ['Foundation', 'CoreGraphics', 'CoreImage', 'CoreVideo', 'ImageIO', 'Vision']:
            args += ['-framework', framework]
        args += ['-o', build / name]
        assert run(args, build, name + '-build', timeout=180) == 0, name + ' build failed'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('fixtures', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--phase', choices=['inventory', 'generate'], default='inventory')
    args = parser.parse_args()
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=True)
    build = out / '_build'; compile_tools(build)
    source_head = subprocess.check_output(['git', '-C', HERE, 'rev-parse', 'HEAD'], text=True).strip()
    fixture_head = subprocess.check_output(['git', '-C', args.fixtures, 'rev-parse', 'HEAD'], text=True).strip()
    rows = []; seen = {}
    for line in (args.fixtures / 'SHA256SUMS').read_text().splitlines():
        digest, relative = line.split(None, 1); relative = relative.strip()
        path = args.fixtures / relative
        assert sha(path) == digest, 'fixture digest mismatch: ' + relative
        case = relative.replace('/', '__').rsplit('.', 1)[0]
        row = {'id':case, 'fixture':relative, 'source_sha256':digest}
        if digest in seen:
            row['duplicate_of'] = seen[digest]; rows.append(row); continue
        seen[digest] = case
        directory = out / case; directory.mkdir()
        row['prepare_exit'] = run([build / 'prepare', path, directory, 1024], directory, 'prepare')
        if (directory / 'input.json').exists():
            row['input'] = json.loads((directory / 'input.json').read_text())
        rows.append(row)
        report = {'schema':'texture-fixture-matrix-v1', 'source_head':source_head, 'fixture_repository':'21Z121Z1/XDRemux', 'fixture_head':fixture_head, 'phase':args.phase, 'rows':rows}
        (out / 'matrix.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps({k:v for k,v in row.items() if k != 'input'}), flush=True)
    report['fixture_file_count'] = len(rows); report['unique_fixture_count'] = len(seen)
    report['all_native_inputs_prepared'] = all(r.get('prepare_exit', 0) == 0 for r in rows)
    (out / 'matrix.json').write_text(json.dumps(report, indent=2) + '\n')
    return 0 if report['all_native_inputs_prepared'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
