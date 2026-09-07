"""Non-overwriting atomic output for generated briefs."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from .models import BriefError


def write_output(path: str | Path, content: str) -> Path:
    """Write UTF-8 text atomically while refusing to replace any file."""

    destination = Path(path)
    if destination.exists():
        raise BriefError(f"output already exists: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=destination.parent,
            prefix=f".{destination.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
            temporary = Path(handle.name)
        os.link(temporary, destination)
        temporary.unlink()
    except FileExistsError as exc:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
        raise BriefError(f"output already exists: {destination}") from exc
    except OSError as exc:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
        raise BriefError(f"could not write output: {destination}") from exc
    return destination
