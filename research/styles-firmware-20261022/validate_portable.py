"""Run explicitly scoped portable regressions with source/log/runtime bindings.

Success is limited to the named tests. The historical full suite has native-only
requirements and is deliberately not relabelled as portable or silently skipped.
"""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

import numpy as np


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
SUITES = (
    'test_under_eye_half', 'test_read_native_reference', 'test_native_texture_reference', 'test_native_reference', 'test_validation_binding', 'test_image_chain', 'test_image_chain_cli', 'test_module_sensitivity', 'test_pow_runtime_binding',
    'test_texture_style_adapter', 'test_skin_smoothing_final', 'test_bright_saved', 'test_connected_bright',
    'test_square_contract', 'test_sqrt_double_round', 'test_texture_numeric',
    'test_output_writer', 'test_ltm_gain', 'test_ltm_preprocess',
    'test_precomputed_semantic', 'test_pixel_skin',
)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sources():
    paths = sorted({*ROOT.glob('*.py'), *ROOT.glob('*.c'),
                    *(ROOT/'native-reference').glob('*.c'), *(ROOT/'native-reference').glob('*.m'),
                    *(ROOT.parent / 'semantic-styles').glob('*.py'),
                    ROOT.parent / 'hdr-native/guided_reference_v3.py'})
    return {str(p.relative_to(REPO)): digest(p) for p in paths}


def evidence_manifest(root: Path, repository: Path) -> dict[str, str]:
    """Bind every nested evidence file, including additions and removals."""
    return {str(p.relative_to(repository)): digest(p)
            for p in sorted(root.rglob('*')) if p.is_file()}


def git(*args):
    return subprocess.check_output(['git', *args], cwd=REPO, text=True).strip()


def run(output):
    output = Path(output).resolve()
    evidence_root = ROOT / 'evidence'
    if output.is_relative_to(evidence_root.resolve()):
        raise ValueError('Validation output must be outside the input evidence tree')
    output.mkdir(parents=True, exist_ok=False)
    before = sources()
    input_hashes = evidence_manifest(evidence_root, REPO)
    pre = {
        'scope': 'named portable and public-certificate regressions only',
        'git_HEAD': git('rev-parse', 'HEAD'),
        'git_status_porcelain': git('status', '--porcelain'),
        'source_sha256': before,
        'input_evidence_sha256': input_hashes,
        'runtime': {'system': platform.system(), 'release': platform.release(),
                    'machine': platform.machine(), 'python': sys.version,
                    'numpy': np.__version__, 'executable': sys.executable},
        'suites': list(SUITES),
        'full_historical_suite_requested': False,
        'original_native_calls_requested': 0,
    }
    (output / 'before.json').write_text(json.dumps(pre, indent=2) + '\n')
    command = [sys.executable, '-m', 'unittest', '-v', *SUITES]
    start = time.perf_counter()
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=240)
    elapsed = time.perf_counter() - start
    log = output / 'tests.log'
    log.write_text(completed.stdout + completed.stderr)
    unchanged = before == sources()
    inputs_unchanged = input_hashes == evidence_manifest(evidence_root, REPO)
    result = {
        'git_HEAD': pre['git_HEAD'], 'command': command,
        'cwd_relative_to_repository': str(ROOT.relative_to(REPO)),
        'exit_code': completed.returncode, 'elapsed_seconds': elapsed,
        'sources_unchanged': unchanged,
        'input_evidence_unchanged': inputs_unchanged,
        'before_sha256': digest(output / 'before.json'),
        'log_sha256': digest(log),
        'named_regressions_passed': completed.returncode == 0 and unchanged and inputs_unchanged,
        'full_historical_suite_passed': None,
        'Apple_CPU_validation_performed': False,
        'Apple_GPU_validation_performed': False,
        'full_camera_pipeline_verified': False,
    }
    (output / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    print(completed.stdout + completed.stderr)
    print(json.dumps(result, indent=2))
    return 0 if result['named_regressions_passed'] else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path, help='new directory; existing output is never overwritten')
    sys.exit(run(parser.parse_args().output))
