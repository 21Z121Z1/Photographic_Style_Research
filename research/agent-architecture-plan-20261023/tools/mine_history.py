"""Recompute a read-only structural inventory and replay public historical defects.

Counts describe committed files at an explicit ref. Keyword matches are search
signals, never a count of bugs or evidence of who authored a change. Replays run
historical Python generators on synthetic IR text, not Apple kernels.
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import re
import struct
import subprocess
import sys


REPO = Path(__file__).resolve().parents[3]
BASE = '611ac4f6fe525ad3ba80ba5025aa8b5f0a45a079'
FIRMWARE = 'research/styles-firmware-20261022/'


def git(*args: str) -> bytes:
    return subprocess.check_output(['git', *args], cwd=REPO)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def blob(ref: str, name: str) -> bytes:
    return git('show', ref+':'+name)


def committed_function(ref: str, name: str, function: str, namespace: dict):
    source = blob(ref, name)
    tree = ast.parse(source)
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == function)
    target = ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[]))
    exec(compile(target, ref+':'+name, 'exec'), namespace)
    return namespace[function], digest(source)


def replay_observer_contracts() -> list[dict]:
    """Replay two actual pre-fix generators without importing native harnesses."""
    fixed = 'd4dedf0a842b4c483485957dd4a8c8932f52f380'
    before = git('rev-parse', fixed+'^').decode().strip()
    rows = []
    cases = [
        ('bw_host.py', 'build', '_Z29renderBWAdjustmentsByCastType', [12, 67]),
        ('diagnose_local_gamma.py', 'instrument', '_Z19renderBGAdjustments', [89]),
    ]
    for name, function, symbol, sites in cases:
        lines = [f'define internal fastcc <3 x half> @{symbol}() unnamed_addr #0 {{']
        for site in sites:
            ty = '<3 x half>' if name == 'bw_host.py' else 'half'
            lines.append(f'  %{site} = fadd {ty} zeroinitializer, zeroinitializer')
        lines += ['  ret <3 x half> zeroinitializer', '}', 'attributes #0 = { memory(read) }']
        ir = '\n'.join(lines)+'\n'
        for ref, state in [(before, 'historical_before'), (fixed, 'historical_fixed')]:
            ns = {'re': re}
            ns['original_build'] = lambda source, selected: (source, {})
            run, source_hash = committed_function(ref, FIRMWARE+name, function, ns)
            out, _ = run(ir) if function == 'build' else run(ir, {89: 'half'})
            writes = 'store float ' in out and '@psr_' in out
            readonly = 'memory(read)' in out
            safe = writes and not readonly and 'memory(readwrite)' in out
            rows.append({'case': name, 'ref': ref, 'state': state,
                         'historical_source_sha256': source_hash,
                         'synthetic_IR_sha256': digest(ir.encode()),
                         'generated_IR_sha256': digest(out.encode()),
                         'trace_stores_inserted': writes,
                         'readonly_summary_retained': readonly,
                         'write_summary_consistent': safe,
                         'evidence_level': 'historical generator behavior on synthetic IR, no native compile or execution'})
    if [r['write_summary_consistent'] for r in rows] != [False, True, False, True]:
        raise AssertionError('Historical observer replay differs from documented before/fixed contracts')
    return rows


def replay_numeric_metadata(ref: str) -> dict:
    wrong_map = json.loads(blob(ref, FIRMWARE+'evidence/bright-machine-map-s29e.json'))
    fixed_map = json.loads(blob(ref, FIRMWARE+'evidence/bright-machine-map-s29e2.json'))
    half = struct.unpack('<e', struct.pack('<H', 0xca00))[0]
    old_label = wrong_map['SSA135_register']
    new_label = fixed_map['SSA135_register']
    target = '16244'
    row = '0x0000000000016244 136 _powf'
    previous = re.search(r'\b0*'+target+r'\b', row) is not None
    ns = {'re': re, 'hashlib': hashlib}
    resolve, source_hash = committed_function(ref, FIRMWARE+'verify_fpcr_binding.py', 'resolve_stub_rows', ns)
    text = 'Indirect symbols for (__TEXT,__stubs) 1 entries\n'+row+'\n'
    resolved = resolve(text, int(target, 16))
    if half != -12 or 'half-6)' not in old_label or 'half-12)' not in new_label:
        raise AssertionError('Historical half decoding evidence changed')
    if previous or len(resolved) != 1 or resolved[0]['symbol'] != '_powf' or resolved[0]['index'] != 136:
        raise AssertionError('Historical hex-address parser evidence changed')
    return {'half_constant': {'bits': '0xca00', 'decoded_by_IEEE_binary16': half,
                             'rejected_label': old_label, 'corrected_label': new_label,
                             'rejected_receipt_sha256': digest(blob(ref, FIRMWARE+'evidence/bright-machine-map-s29e.json')),
                             'corrected_receipt_sha256': digest(blob(ref, FIRMWARE+'evidence/bright-machine-map-s29e2.json'))},
            'hex_address': {'synthetic_row_matches_documented_saved_format': row,
                            'old_pattern_matches': previous, 'fixed_rows': resolved,
                            'fixed_parser_source_sha256': source_hash,
                            'old_pattern_from': 'audit_pow_stub.py rows expression'},
            'native_calls': 0, 'evidence_level': 'exact format decoding and historical parser behavior; no private metadata file or native pow replay'}


def inventory(ref: str) -> dict:
    commit = git('rev-parse', ref).decode().strip()
    files = [p.decode() for p in git('ls-tree', '-rz', '--name-only', commit).split(b'\0') if p]
    groups = defaultdict(Counter)
    signals = defaultdict(list)
    python_functions = Counter()
    python_test_files = Counter()
    swift_test_files = Counter()
    research_groups = defaultdict(Counter)
    runner_labels = Counter()
    runner_files = defaultdict(list)
    manifests = []
    code_hashes = {}
    package_markers = []
    swift_boundaries = []
    for name in files:
        top = name.split('/', 1)[0] if '/' in name else '(root)'
        ext = Path(name).suffix.lower() or '(none)'
        groups[top]['files'] += 1
        groups[top][ext] += 1
        if top == 'research' and '/' in name[9:]:
            research_groups['/'.join(name.split('/')[:2])][ext] += 1
            research_groups['/'.join(name.split('/')[:2])]['files'] += 1
        if name.endswith('/__init__.py'):
            package_markers.append(name)
        if ext not in {'.py', '.swift', '.yml', '.yaml'}:
            continue
        data = blob(commit, name)
        source = data.decode('utf-8')
        code_hashes[name] = digest(data)
        if ext == '.py':
            python_test_files[top] += int(Path(name).name.startswith('test_'))
            try:
                tree = ast.parse(source)
            except SyntaxError as error:
                signals['python_parse_errors'].append({'path': name, 'line': error.lineno})
                continue
            nodes = list(ast.walk(tree))
            python_functions[top] += sum(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name.startswith('test_') for n in nodes)
            if re.search(r'sys\.path\.(?:insert|append|extend)\s*\(', source):
                signals['sys_path_edit_files'].append(name)
            if any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'exec' for n in nodes):
                signals['dynamic_exec_files'].append(name)
            if 'ast.NodeTransformer' in source or 'FunctionType(' in source:
                signals['AST_or_function_clone_files'].append(name)
            if 'source_sha256' in source or 'source_manifest' in source or 'source_hashes' in source:
                signals['source_identity_writer_or_reader_files'].append(name)
            if (re.search(r"glob\(['\"]\*\.py['\"]\)", source) and
                    any(token in source for token in ('sha256', 'sha(', 'digest('))):
                manifests.append(name)
            if 'TemporaryDirectory' in source and re.search(r"\.ll['\"]", source):
                signals['temporary_IR_owner_files'].append(name)
        elif ext in {'.yml', '.yaml'} and name.startswith('.github/workflows/'):
            for label in re.findall(r'^\s*runs-on:\s*([^\n#]+)', source, re.M):
                label = label.strip().strip("'\"")
                runner_labels[label] += 1
                runner_files[label].append(name)
        elif ext == '.swift' and any(token in source for token in ('CommandSpec', 'Process()', 'arguments:')):
            swift_boundaries.append(name)
        if ext == '.swift' and top == 'tests':
            swift_test_files[top] += 1
    rows = [line.split('\x1f') for line in git('log', commit, '--format=%H%x1f%cI%x1f%s').decode().splitlines()]
    times = [datetime.fromisoformat(r[1]).astimezone(timezone.utc) for r in rows]
    heads = dict(line.split(' ',1) for line in git('for-each-ref','--format=%(refname) %(objectname)').decode().splitlines())
    keywords = ('fix', 'correct', 'repair', 'revert', 'failure')
    return {'schema': 'psr-committed-architecture-inventory-v1', 'baseline_commit': commit,
            'commands': ['git ls-tree -rz --name-only '+commit,
                         'git log '+commit+' --format=%H%x1f%cI%x1f%s',
                         'git show '+commit+':<each committed Python, Swift or workflow path>'],
            'reachable_commits': len(rows),
            'local_ref_heads_at_measurement': heads,
            'all_local_refs_reachable_commits': int(git('rev-list','--count',*sorted(set(heads.values())))),
            'commit_timestamp_range_UTC': [min(times).isoformat(), max(times).isoformat()],
            'subject_keyword_matches_not_bug_counts': {k:sum(bool(re.search(r'\b'+k+r'\w*', r[2], re.I)) for r in rows) for k in keywords},
            'explicit_revert_subjects': [{'commit': r[0], 'subject': r[2]} for r in rows if re.match('revert\b',r[2],re.I)],
            'committed_file_count': len(files),
            'per_top_level_path': {name:dict(counts) for name,counts in sorted(groups.items())},
            'per_research_directory': {name:dict(counts) for name,counts in sorted(research_groups.items())},
            'Python_test_filename_count_by_top_level_path': dict(python_test_files),
            'Swift_test_filename_count_by_top_level_path': dict(swift_test_files),
            'static_test_function_definitions_by_top_level_path': dict(python_functions),
            'structural_signals_not_defect_counts': dict(signals),
            'Python_glob_source_identity_owner_files': manifests,
            'Python_package_markers': package_markers,
            'Swift_process_or_command_boundary_files': swift_boundaries,
            'workflow_runner_label_occurrences': dict(runner_labels),
            'workflow_runner_files': dict(runner_files),
            'source_sha256': code_hashes,
            'authorship': 'Commit author identity and keywords do not establish agent involvement or a repeated defect.'}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ref', default=BASE)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    result = inventory(args.ref)
    result['mining_script_sha256'] = digest(Path(__file__).read_bytes())
    result['runtime'] = {'python':sys.version,'system':platform.system(),'machine':platform.machine()}
    replay = {'baseline_commit': result['baseline_commit'],
              'observer_memory_effects': replay_observer_contracts(),
              'numeric_metadata': replay_numeric_metadata(args.ref),
              'new_Apple_CPU_or_GPU_calls': 0,
              'missing_private_IR_restored': False}
    for name, data in [('inventory.json', result), ('historical-replays.json', replay)]:
        (args.output/name).write_text(json.dumps(data, indent=2, ensure_ascii=False)+'\n')
    print(json.dumps({'baseline':result['baseline_commit'],'commits':result['reachable_commits'],
                      'files':result['committed_file_count'],
                      'top_level_Python_counts':{k:v.get('.py',0)for k,v in result['per_top_level_path'].items()},
                      'observer_replay_contracts':[r['write_summary_consistent'] for r in replay['observer_memory_effects']],
                      'output':str(args.output)},indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
