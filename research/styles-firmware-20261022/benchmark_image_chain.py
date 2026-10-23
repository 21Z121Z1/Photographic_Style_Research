"""Report repeat costs on this machine; never infer speedup from missing baselines."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import resource
import statistics
import subprocess
import sys
import time

import numpy as np

from image_chain import run, BranchSelection, Numerics
from synthetic_inputs import make_context, SyntheticSpec, Pattern, describe


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]


def baseline(ref):
    commit = subprocess.check_output(['git', 'rev-parse', ref], cwd=REPO, text=True).strip()
    required = ['image_chain.py', 'synthetic_inputs.py', 'benchmark_image_chain.py']
    missing = [name for name in required if subprocess.run(
        ['git', 'cat-file', '-e', commit + ':' + str((ROOT / name).relative_to(REPO))],
        cwd=REPO, capture_output=True).returncode]
    # Current history has no comparable callable algorithm on master. Do not
    # replace it with an unrelated operation and advertise an optimization gain.
    return {'ref': ref, 'commit': commit, 'missing_required_modules': missing,
            'same_workload_available': not missing, 'timing_seconds': None,
            'status': 'unavailable' if missing else 'not_executed_by_this_cost_report',
            'speedup_claimed': False}


def benchmark(output, repeats, height, width):
    if output.exists():
        raise FileExistsError(output)
    if not 2 <= repeats <= 10:
        raise ValueError('Use 2..10 explicit repeated costs')
    spec = SyntheticSpec(Pattern.GRADIENT, height, width)
    context = make_context(spec)
    sources = sorted(ROOT.glob('*.py')) + [ROOT.parent/'hdr-native/guided_reference_v3.py',
                                          ROOT.parent/'semantic-styles/spatial_curve_retarget.py',
                                          ROOT.parent/'semantic-styles/semantic_curve_inverse.py']
    source_hashes = {str(p.relative_to(REPO)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    rows = []
    for selection in (BranchSelection.CONTEXT, BranchSelection.EXPERIMENTAL_BRIGHT16):
        elapsed = []
        hashes = []
        statuses = []
        for _ in range(repeats):
            begin = time.perf_counter()
            result = run(context, selection=selection,
                         numerics=Numerics.EXPERIMENTAL_PORTABLE_POINT)
            elapsed.append(time.perf_counter() - begin)
            statuses.append(result.status)
            writer = result.model.writer
            hashes.append(None if writer is None else hashlib.sha256(
                writer.output.pixels.lo.astype('<f2').tobytes()).hexdigest())
        rows.append({'selection': selection.value, 'wall_seconds': elapsed,
                     'median_seconds': statistics.median(elapsed),
                     'minimum_seconds': min(elapsed), 'maximum_seconds': max(elapsed),
                     'sample_stdev_seconds': statistics.stdev(elapsed),
                     'status_each_repeat': statuses, 'writer_sha256_each_repeat': hashes,
                     'raw_input_sha256': result.provenance['raw_input_sha256'],
                     'writer_repeatable': all(h is not None for h in hashes) and len(set(hashes)) == 1})
    result = {
        'git_HEAD': subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),
        'git_status_porcelain': subprocess.check_output(['git','status','--porcelain'],cwd=REPO,text=True).strip(),
        'source_sha256_before_execution': source_hashes,
        'sources_unchanged': all(hashlib.sha256((REPO/path).read_bytes()).hexdigest() == value
                                 for path,value in source_hashes.items()),
        'runtime': {'system': platform.system(), 'release': platform.release(),
                    'machine': platform.machine(), 'python': sys.version, 'numpy': np.__version__},
        'input': describe(spec), 'repeats_per_selection': repeats,
        'numerics': Numerics.EXPERIMENTAL_PORTABLE_POINT.value,
        'costs_include': 'source→producer→guided→consumer→writer and provenance/checkpoint construction; no CLI export or process startup',
        'process_peak_RSS_native_units': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'RSS_units': 'KiB on Linux, bytes on Darwin; process peak including imports and all repeats',
        'baseline_master': baseline('origin/master'),
        'baseline_research': baseline('e5d2bcd8db8b3eb6737237ed88167777b3c920ba'),
        'rows': rows, 'optimization_speedup_claimed': False,
        'different_machine_numbers_compared': False, 'Apple_reference_compared': False,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print(json.dumps(result, indent=2))
    return 0 if result['sources_unchanged'] and all(r['writer_repeatable'] for r in rows) else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--repeats', type=int, default=3)
    parser.add_argument('--height', type=int, default=8)
    parser.add_argument('--width', type=int, default=12)
    args = parser.parse_args()
    sys.exit(benchmark(args.output, args.repeats, args.height, args.width))
