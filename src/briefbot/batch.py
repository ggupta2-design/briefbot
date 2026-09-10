"""Safe, bounded discovery for folder-level brief audits."""

from __future__ import annotations

from pathlib import Path

from .models import BriefError


def _file_limit(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 1000:
        raise BriefError("max_files must be an integer from 1 to 1000")
    return value


def discover_brief_files(
    root: str | Path,
    *,
    recursive: bool = False,
    max_files: int = 100,
) -> tuple[Path, ...]:
    """Return deterministic JSON files without following symbolic links."""

    limit = _file_limit(max_files)
    directory = Path(root)
    if not directory.exists():
        raise BriefError(f"brief folder does not exist: {directory}")
    if directory.is_symlink():
        raise BriefError("brief folder cannot be a symbolic link")
    if not directory.is_dir():
        raise BriefError(f"brief folder is not a directory: {directory}")

    pending = [directory]
    found: list[Path] = []
    while pending:
        current = pending.pop()
        for entry in sorted(current.iterdir(), key=lambda path: path.name.casefold()):
            if entry.is_symlink():
                continue
            if entry.is_dir():
                if recursive:
                    pending.append(entry)
                continue
            if entry.is_file() and entry.suffix.casefold() == ".json":
                found.append(entry)
                if len(found) > limit:
                    raise BriefError(
                        f"brief folder contains more than max_files={limit} JSON files"
                    )

    return tuple(
        sorted(
            found,
            key=lambda path: path.relative_to(directory).as_posix().casefold(),
        )
    )
