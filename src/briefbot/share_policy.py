"""Strict JSON loading for brief disclosure policies."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .disclosure import DisclosurePolicy
from .models import BriefError


_FIELDS = {
    "schema_version",
    "name",
    "include_objective",
    "include_context",
    "include_decisions",
    "include_risks",
    "include_actions",
    "include_owner_names",
    "include_due_dates",
}


def disclosure_policy_from_dict(payload: Any) -> DisclosurePolicy:
    """Build a disclosure policy from an exact versioned schema."""

    if not isinstance(payload, dict) or set(payload) != _FIELDS:
        raise BriefError(
            "disclosure policy must contain exactly the supported fields"
        )
    if payload["schema_version"] != 1:
        raise BriefError(
            "unsupported disclosure policy schema_version: "
            f"{payload['schema_version']}"
        )
    return DisclosurePolicy(
        name=payload["name"],
        include_objective=payload["include_objective"],
        include_context=payload["include_context"],
        include_decisions=payload["include_decisions"],
        include_risks=payload["include_risks"],
        include_actions=payload["include_actions"],
        include_owner_names=payload["include_owner_names"],
        include_due_dates=payload["include_due_dates"],
    )


def load_disclosure_policy(path: str | Path) -> DisclosurePolicy:
    """Read one UTF-8 disclosure policy from local storage."""

    source = Path(path)
    if not source.exists():
        raise BriefError(f"disclosure policy file does not exist: {source}")
    if not source.is_file():
        raise BriefError(f"disclosure policy path is not a file: {source}")
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except UnicodeDecodeError as exc:
        raise BriefError("disclosure policy is not valid UTF-8") from exc
    except json.JSONDecodeError as exc:
        raise BriefError(
            f"disclosure policy is not valid JSON at line {exc.lineno}"
        ) from exc
    except OSError as exc:
        raise BriefError("could not read disclosure policy") from exc
    return disclosure_policy_from_dict(payload)
