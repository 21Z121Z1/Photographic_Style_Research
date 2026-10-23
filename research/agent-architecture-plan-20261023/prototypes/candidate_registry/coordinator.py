"""Isolated registry-first experiment. No production module is migrated."""
from __future__ import annotations

import ast
from dataclasses import asdict, dataclass
from enum import Enum
import hashlib
import json
from pathlib import Path
import platform
import re
import subprocess
import sys
import time

import numpy as np


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]


class Intent(Enum):
    PORTABLE_MODEL = 'portable-model'
    APPLE_NATIVE = 'apple-native'


@dataclass(frozen=True)
class Request:
    capability: str
    intent: Intent
    input_file: Path
    input_sha256: str
    output: Path
    source_snapshot: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class RunRecord:
    capability: str
    status: str
    evidence_level: str | None
    reason: str | None
    input_sha256: str
    source_snapshot: tuple[tuple[str, str], ...]
    elapsed_seconds: float
    artifact_sha256: tuple[tuple[str, str], ...]
    target_Apple_reference_compared: bool = False


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Coordinator:
    """Own registry resolution, dependency snapshots and result admission."""

    def __init__(self, repo: Path = REPO, registry: Path = HERE/'registry.json'):
        self.repo, self.registry_file = repo.resolve(), registry.resolve()
        self._registry = json.loads(self.registry_file.read_text())
        if self._registry['schema'] != 'psr-capability-registry-prototype-v1':
            raise ValueError('Unsupported capability registry')

    def _inside(self, relative: str) -> Path:
        path = (self.repo/relative).resolve()
        if not path.is_relative_to(self.repo) or not path.is_file():
            raise ValueError('Declared repository artifact unavailable: '+relative)
        return path

    def source_paths(self, capability: str) -> tuple[Path, ...]:
        """Conservative static closure for this repository's current imports.

        Import statements include lazy branches. Literal Python file references
        cover current importlib file loads. This is not arbitrary Python import
        analysis; computed import paths require a declared capability extension.
        """
        entry = self._registry['capabilities'][capability]
        index: dict[str, set[Path]] = {}
        for root in self._registry['source_roots']:
            for path in (self.repo/root).glob('*.py'):
                index.setdefault(path.stem, set()).add(path.resolve())
        pending = [self._inside(entry['entrypoint'])]
        found: set[Path] = set()
        while pending:
            path = pending.pop()
            if path in found:
                continue
            found.add(path)
            tree = ast.parse(path.read_text(), filename=str(path))
            names = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    names.update(alias.name.split('.')[0] for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    names.add(node.module.split('.')[0])
                elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                    if node.value.endswith('.py'):
                        names.add(Path(node.value).stem)
            for name in names:
                pending.extend(index.get(name, ()))
        found.update((Path(__file__).resolve(), self.registry_file))
        if entry['runtime_profile']:
            found.add(self._inside(entry['runtime_profile']))
        return tuple(sorted(found))

    def snapshot(self, capability: str) -> tuple[tuple[str, str], ...]:
        return tuple((str(p.relative_to(self.repo)), digest(p)) for p in self.source_paths(capability))

    def prepare(self, capability: str, intent: Intent, input_file: Path, output: Path) -> Request:
        if type(intent) is not Intent or capability not in self._registry['capabilities']:
            raise TypeError('Registered capability and exact intent enum required')
        input_file = input_file.resolve()
        if not input_file.is_file():
            raise ValueError('Frozen input file required')
        return Request(capability, intent, input_file, digest(input_file), output.resolve(), self.snapshot(capability))

    def _reason(self, request: Request) -> str | None:
        entry = self._registry['capabilities'][request.capability]
        if request.intent.value != entry['intent']:
            return 'Capability cannot satisfy the requested evidence intent'
        if entry['availability'] != 'runnable':
            return 'Original sealed material and native execution are unavailable; collector is prepared only'
        if digest(request.input_file) != request.input_sha256:
            return 'Input bytes differ from the prepared request'
        if self.snapshot(request.capability) != request.source_snapshot:
            return 'Source bytes or complete dependency set differ from the prepared request'
        if entry['runtime_profile']:
            profile = json.loads(self._inside(entry['runtime_profile']).read_text())['profile']['runtime']
            actual = {'system': platform.system(), 'release': platform.release(),
                      'machine': platform.machine(), 'numpy': np.__version__}
            if any(profile.get(k) != v for k, v in actual.items()):
                return 'Current runtime differs from the exact historical host profile'
        return None

    @staticmethod
    def _synthetic_input(path: Path) -> dict:
        raw = json.loads(path.read_text())
        expected = {'pattern', 'height', 'width', 'field3', 'selection'}
        if set(raw) != expected or raw['pattern'] not in ('gradient', 'exposure', 'colors', 'edges', 'zero'):
            raise ValueError('Exact synthetic input schema required')
        if any(type(raw[n]) is not int or not 2 <= raw[n] <= 30 for n in ('height', 'width')):
            raise ValueError('Source tile dimensions must be integers in [2,30]')
        if type(raw['field3']) not in (int, float) or isinstance(raw['field3'], bool) or not np.isfinite(raw['field3']) or not 0 <= raw['field3'] <= 1:
            raise ValueError('Finite raw field3 in [0,1] required')
        if raw['selection'] not in ('context', 'experimental-bright16'):
            raise ValueError('Exact branch selection required')
        return raw

    def run(self, request: Request) -> RunRecord:
        if not isinstance(request, Request) or type(request.intent) is not Intent:
            raise TypeError('Prepared typed request required')
        if request.output.exists():
            raise FileExistsError('A run owns one new output directory')
        request.output.mkdir(parents=True)
        begin = time.perf_counter()
        reason = self._reason(request)
        result_level, status = None, 'blocked'
        if reason is None:
            entry = self._registry['capabilities'][request.capability]
            if entry['operation'] != 'synthetic-image' or entry['result_level'] != 'model_only':
                raise ValueError('No native certification implementation exists in this prototype')
            raw = self._synthetic_input(request.input_file)
            command = [sys.executable, str(self._inside(entry['entrypoint'])),
                       '--numerics', entry['numerics'], '--patterns', raw['pattern'],
                       '--height', str(raw['height']), '--width', str(raw['width']),
                       '--values', str(raw['field3']), '--selection', raw['selection'],
                       '--output', str(request.output/'cli')]
            completed = subprocess.run(command, cwd=self.repo, text=True, capture_output=True, timeout=45)
            (request.output/'command.json').write_text(json.dumps(command, indent=2)+'\n')
            (request.output/'command.log').write_text(completed.stdout+completed.stderr)
            report_path = request.output/'cli/summary.json'
            if completed.returncode not in (0, 2) or not report_path.is_file():
                reason = 'CLI did not complete a stable diagnostic run'
            else:
                report = json.loads(report_path.read_text())
                if (report.get('evidence_level') != 'model_only' or report.get('Apple_pipeline_verified') is not False
                        or not report.get('source_snapshot_stable')):
                    reason = 'Result did not preserve the model-only evidence contract'
                else:
                    reason = self._reason(request)
                    if reason is None:
                        result_level = 'model_only'
                        status = 'model_only' if completed.returncode == 0 else 'unknown'
        artifacts = tuple((str(p.relative_to(request.output)), digest(p))
                          for p in sorted(request.output.rglob('*')) if p.is_file())
        record = RunRecord(request.capability, status, result_level, reason,
                           request.input_sha256, request.source_snapshot,
                           time.perf_counter()-begin, artifacts)
        (request.output/'receipt.json').write_text(json.dumps(asdict(record), indent=2)+'\n')
        return record
