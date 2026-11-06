"""New-output default. Originals are never replaced or opened for write."""
from __future__ import annotations

from pathlib import Path


class OutputRefused(FileExistsError):
    pass


def allocate_output(path: Path, protected: list[Path] | None = None) -> Path:
    """Create a new directory. Refuse an existing path or a protected input."""
    destination = path.expanduser().resolve()
    if destination.exists():
        raise OutputRefused(f"refusing to overwrite existing path: {destination}")
    if destination.is_symlink():
        raise OutputRefused(f"refusing to follow a symlink output: {destination}")
    for source in protected or []:
        protected_path = source.expanduser().resolve()
        if destination == protected_path or _is_relative_to(destination, protected_path):
            raise OutputRefused(f"refusing to write inside protected input: {protected_path}")
        if _is_relative_to(protected_path, destination):
            raise OutputRefused(f"refusing to use an output that contains protected input: {protected_path}")
    destination.mkdir(parents=True)
    return destination


def assert_inputs_unchanged(paths: list[Path], digests: dict[str, str], digest) -> None:
    for path in paths:
        current = digest(path)
        previous = digests[str(path.resolve())]
        if current != previous:
            raise RuntimeError(f"input changed during the run: {path}")


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True
