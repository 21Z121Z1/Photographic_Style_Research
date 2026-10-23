"""Capture one diagnostic CLI profile. This script makes no speedup comparison."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import platform
import pstats
import subprocess
import sys

REPO = Path(__file__).resolve().parents[3]
CLI = REPO / 'research/styles-firmware-20261022/image_chain_cli.py'


def run(output: Path) -> None:
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    command = [sys.executable, '-m', 'cProfile', '-o', str(output / 'cli.pstats'),
               str(CLI), '--numerics', 'experimental-portable', '--patterns', 'gradient',
               '--height', '4', '--width', '6', '--values', '0', '--output', str(output / 'cli')]
    identity = {'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip(),
                'python': sys.version, 'system': platform.platform(), 'machine': platform.machine(),
                'load': subprocess.check_output(['uptime'], text=True).strip(),
                'cpu_count': subprocess.check_output(['nproc'], text=True).strip(),
                'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'command': command}
    p = subprocess.run(command, cwd=REPO, capture_output=True, text=True, timeout=60)
    (output / 'command.log').write_text(p.stdout + p.stderr)
    if p.returncode:
        raise RuntimeError(f'Actual CLI failed with code {p.returncode}; log retained at {output}')
    d = json.loads((output / 'cli/summary.json').read_text())
    if d['summary']['writers'] != 1 or d['summary']['blocked_or_unknown'] or not d['source_snapshot_stable']:
        raise RuntimeError('Profile did not execute the one complete bound writer requested')
    stats = pstats.Stats(str(output / 'cli.pstats'))
    rows = []
    for (filename, line, name), (primitive_calls, calls, self_seconds, cumulative_seconds, _) in stats.stats.items():
        if str(REPO) in filename:
            rows.append({'source': str(Path(filename).relative_to(REPO)), 'line': line, 'name': name,
                         'primitive_calls': primitive_calls, 'calls': calls,
                         'profile_self_seconds': self_seconds, 'profile_cumulative_seconds': cumulative_seconds})
    rows.sort(key=lambda x: x['profile_self_seconds'], reverse=True)
    report = {**identity, 'scope': 'one instrumented 4x6 synthetic portable CLI, diagnostic only',
              'profile_run_count': 1, 'comparison_or_speedup_claim': False,
              'profile_duration_is_not_production_latency': True,
              'actual_cli_summary': d['summary'], 'source_sha256': d['source_sha256_before'],
              'cli_summary_sha256': hashlib.sha256((output / 'cli/summary.json').read_bytes()).hexdigest(),
              'case_writer_sha256': d['runs'][0]['writer_sha256'],
              'profile_total_seconds': stats.total_tt, 'top_repository_functions_by_self_time': rows[:25]}
    (output / 'profile-summary.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'writers': d['summary']['writers'], 'top_functions': rows[:8]}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    run(parser.parse_args().output)
