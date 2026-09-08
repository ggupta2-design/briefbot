"""Strict JSON loading for reusable readiness policies."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import BriefError
from .readiness import ReadinessPolicy


_POLICY_FIELDS = {
    "schema_version",
    "name",
    "min_context_items",
    "min_decisions",
    "min_actions",
    "require_action_owners",
    "require_action_due_dates",
    "require_risk_owners",
    "max_overdue_actions",
}


def policy_from_dict(payload: Any) -> ReadinessPolicy:
    """Build a validated policy from a strict JSON-compatible object."""

    if not isinstance(payload, dict) or set(payload) != _POLICY_FIELDS:
        raise BriefError("policy must contain exactly the supported fields")
    if payload["schema_version"] != 1:
        raise BriefError(f"unsupported policy schema_version: {payload['schema_version']}")
    return ReadinessPolicy(
        name=payload["name"],
        min_context_items=payload["min_context_items"],
        min_decisions=payload["min_decisions"],
        min_actions=payload["min_actions"],
        require_action_owners=payload["require_action_owners"],
        require_action_due_dates=payload["require_action_due_dates"],
        require_risk_owners=payload["require_risk_owners"],
        max_overdue_actions=payload["max_overdue_actions"],
    )


def load_policy(path: str | Path) -> ReadinessPolicy:
    """Read and validate one UTF-8 JSON readiness policy."""

    source = Path(path)
    if not source.exists():
        raise BriefError(f"policy file does not exist: {source}")
    if not source.is_file():
        raise BriefError(f"policy path is not a file: {source}")
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except UnicodeDecodeError as exc:
        raise BriefError(f"policy is not valid UTF-8: {source}") from exc
    except json.JSONDecodeError as exc:
        raise BriefError(f"policy is not valid JSON at line {exc.lineno}") from exc
    except OSError as exc:
        raise BriefError(f"could not read policy: {source}") from exc
    return policy_from_dict(payload)
