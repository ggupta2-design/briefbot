"""Safe, bounded discovery for folder-level brief audits."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .input import load_brief
from .models import BriefError
from .readiness import ReadinessPolicy, assess_readiness


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


@dataclass(frozen=True)
class BatchReadinessResult:
    """Aggregate, value-free readiness result for one folder."""

    as_of: date
    policy_name: str
    discovered: int
    valid: int
    invalid: int
    ready: int
    review_required: int

    @property
    def all_ready(self) -> bool:
        return self.discovered > 0 and self.invalid == 0 and self.review_required == 0


def audit_brief_folder(
    root: str | Path,
    *,
    as_of: date,
    policy: ReadinessPolicy | None = None,
    recursive: bool = False,
    max_files: int = 100,
) -> BatchReadinessResult:
    """Audit each discovered brief while isolating invalid files."""

    selected = policy or ReadinessPolicy()
    paths = discover_brief_files(
        root,
        recursive=recursive,
        max_files=max_files,
    )
    valid = ready = review_required = 0
    for path in paths:
        try:
            source = load_brief(path)
        except BriefError:
            continue
        valid += 1
        if assess_readiness(source, as_of=as_of, policy=selected).ready:
            ready += 1
        else:
            review_required += 1

    return BatchReadinessResult(
        as_of=as_of,
        policy_name=selected.name,
        discovered=len(paths),
        valid=valid,
        invalid=len(paths) - valid,
        ready=ready,
        review_required=review_required,
    )
