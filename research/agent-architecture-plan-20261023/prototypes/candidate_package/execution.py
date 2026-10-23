"""Candidate A. One owner binds, executes and labels a research run.

This isolated prototype has no native success constructor. Native execution
must be implemented behind this owner before a native result type can exist.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import importlib
import json
from pathlib import Path
import platform
import subprocess
import sys
from typing import ClassVar, Literal

__all__ = ['Study', 'Selection', 'RenderedModel', 'UnresolvedModel', 'Rejected']
_CODE_SUFFIXES = {'.py', '.c', '.m', '.metal', '.swift'}


class Selection(Enum):
    CONTEXT = 'context'
    BRIGHT16 = 'experimental_bright16'


@dataclass(frozen=True)
class RenderedModel:
    writer_path: Path
    writer_sha256: str
    written_pixels: int
    warnings: tuple[str, ...]
    evidence_level: ClassVar[Literal['portable_model']] = 'portable_model'


@dataclass(frozen=True)
class UnresolvedModel:
    reasons: tuple[str, ...]
    warnings: tuple[str, ...]
    evidence_level: ClassVar[Literal['portable_model']] = 'portable_model'


@dataclass(frozen=True)
class Rejected:
    code: str
    reasons: tuple[str, ...]


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _git(repo: Path, *args: str) -> str:
    return subprocess.check_output(['git', '-C', str(repo), *args], text=True).strip()


@dataclass(frozen=True)
class _Inputs:
    path: Path
    payload: bytes
    sha256: str

    @classmethod
    def read(cls, path: Path) -> _Inputs:
        path = path.resolve()
        payload = path.read_bytes()
        if not isinstance(json.loads(payload), dict):
            raise TypeError('Object-shaped input JSON required')
        return cls(path, payload, _sha(payload))

    def unchanged(self) -> bool:
        return self.path.is_file() and _sha(self.path.read_bytes()) == self.sha256


@dataclass(frozen=True)
class _Sources:
    commit: str
    files: tuple[tuple[str, str], ...]

    @classmethod
    def capture(cls, repo: Path) -> _Sources:
        tracked = _git(repo, 'ls-files', '-z').split('\0')
        paths = {repo / name for name in tracked if name and Path(name).suffix in _CODE_SUFFIXES}
        paths.update(Path(__file__).parent.glob('*.py'))
        return cls(_git(repo, 'rev-parse', 'HEAD'), tuple(sorted(
            (str(p.relative_to(repo)) if p.is_relative_to(repo) else '@candidate/'+p.name,
             _sha(p.read_bytes())) for p in paths)))

    def unchanged(self, repo: Path) -> bool:
        try:
            return self == _Sources.capture(repo)
        except (OSError, subprocess.CalledProcessError):
            return False


@dataclass(frozen=True)
class _Plan:
    repo: Path
    sources: _Sources
    context: _Inputs
    selection: Selection
    intent: Literal['portable_model', 'apple_cpu_reference']
    precision: _Inputs | None = None
    sealed_binary: Path | None = None


def _modules(repo: Path):
    folder = repo / 'research/styles-firmware-20261022'
    sys.path.insert(0, str(folder))
    chain = importlib.import_module('image_chain')
    fixture = importlib.import_module('complete_fixture')
    if not Path(chain.__file__).resolve().is_relative_to(repo):
        raise ValueError('Loaded backend belongs to another checkout')
    return chain, fixture


@dataclass(frozen=True)
class Study:
    """Prepare immutable intent once, then run it into one new output directory.

    Callers supply raw context and intent. They cannot supply source lists,
    success booleans, a requested evidence level, or generated intermediate RGB.
    """
    _plan: _Plan

    @classmethod
    def portable(cls, repo: Path, context: Path, *, selection: Selection = Selection.CONTEXT) -> Study:
        if type(selection) is not Selection:
            raise TypeError('Selection enum required')
        repo = repo.resolve()
        return cls(_Plan(repo, _Sources.capture(repo), _Inputs.read(context), selection, 'portable_model'))

    @classmethod
    def reference(cls, repo: Path, context: Path, precision: Path, sealed_binary: Path) -> Study:
        repo = repo.resolve()
        profile = _Inputs.read(precision)
        value = json.loads(profile.payload)
        if not isinstance(value.get('profile', {}).get('runtime'), dict):
            raise ValueError('Explicit bound precision runtime required')
        return cls(_Plan(repo, _Sources.capture(repo), _Inputs.read(context), Selection.CONTEXT,
                         'apple_cpu_reference', profile, sealed_binary.resolve()))

    def run(self, output: Path) -> RenderedModel | UnresolvedModel | Rejected:
        p = self._plan
        output = output.resolve()
        output.mkdir(parents=True, exist_ok=False)
        outcome: RenderedModel | UnresolvedModel | Rejected
        if not p.sources.unchanged(p.repo):
            outcome = Rejected('source_identity_changed', ('The checkout or a bound source changed after preparation',))
        elif not p.context.unchanged() or p.precision is not None and not p.precision.unchanged():
            outcome = Rejected('input_identity_changed', ('An exact input changed after preparation',))
        elif p.intent == 'apple_cpu_reference':
            chain, _ = _modules(p.repo)
            host = importlib.import_module('output_code3').runtime_contract()
            expected = json.loads(p.precision.payload)['profile']['runtime']
            if host != expected:
                outcome = Rejected('reference_runtime_mismatch', tuple(k for k in expected if expected[k] != host.get(k)))
            elif not p.sealed_binary.is_file():
                outcome = Rejected('native_artifact_missing', ('The original sealed artifact is unavailable',))
            else:
                outcome = Rejected('native_backend_not_implemented', ('No native evidence is promoted by this prototype',))
        else:
            chain, fixture = _modules(p.repo)
            context = fixture.decode(json.loads(p.context.payload))
            selection = chain.BranchSelection.CONTEXT if p.selection is Selection.CONTEXT else chain.BranchSelection.EXPERIMENTAL_BRIGHT16
            model = chain.run(context, selection=selection, numerics=chain.Numerics.EXPERIMENTAL_PORTABLE_POINT)
            if not p.sources.unchanged(p.repo) or not p.context.unchanged():
                outcome = Rejected('identity_changed_during_run', ('Artifacts are retained but cannot be accepted as bound results',))
            elif model.model.writer is None:
                outcome = UnresolvedModel(tuple(f'{key}: {value}' for key, value in model.model.pixel_unknowns.items()),
                                          tuple(f'{key}: {value}' for key, value in model.model.internal_unknowns.items()))
            else:
                import numpy as np
                writer = model.model.writer
                path = output / 'writer.npy'
                array = writer.output.pixels.lo.astype('<f2')
                np.save(path, array, allow_pickle=False)
                outcome = RenderedModel(path, _sha(array.tobytes()), int(writer.written_pixels.sum()),
                                        tuple(f'{key}: {value}' for key, value in model.model.internal_unknowns.items()))
        record = {'schema': 'candidate-a-owned-run-v1',
                  'outcome': type(outcome).__name__, 'result': asdict(outcome),
                  'evidence_level': outcome.evidence_level if isinstance(outcome, (RenderedModel, UnresolvedModel)) else None,
                  'intent': p.intent, 'selection': p.selection.value,
                  'source_commit': p.sources.commit, 'source_sha256': dict(p.sources.files),
                  'input_sha256': p.context.sha256,
                  'precision_sha256': p.precision.sha256 if p.precision else None,
                  'runtime': {'system': platform.system(), 'release': platform.release(),
                              'machine': platform.machine(), 'python': sys.version},
                  'native_calls_performed': 0,
                  'scope': 'prototype portable run or explicit rejection; no native acceptance type exists'}
        (output / 'receipt.json').write_text(json.dumps(record, indent=2, default=str) + '\n')
        return outcome
