"""Strict JSON loading for BriefBot source notes."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from .models import ActionItem, BriefError, BriefInput, RiskItem


_ROOT_FIELDS = {
    "schema_version",
    "title",
    "audience",
    "objective",
    "context",
    "decisions",
    "risks",
    "actions",
}


def _require_list(value: Any, field_name: str) -> list[Any]:
    if not isinstance(value, list):
        raise BriefError(f"{field_name} must be a list")
    return value


def _parse_optional_date(value: Any, field_name: str) -> date | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise BriefError(f"{field_name} must be an ISO date or null")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise BriefError(f"{field_name} must use YYYY-MM-DD") from exc


def brief_from_dict(payload: Any) -> BriefInput:
    """Build validated brief input from a strict JSON-compatible object."""

    if not isinstance(payload, dict) or set(payload) != _ROOT_FIELDS:
        raise BriefError("brief must contain exactly the supported fields")
    if payload["schema_version"] != 1:
        raise BriefError(f"unsupported schema_version: {payload['schema_version']}")

    context = _require_list(payload["context"], "context")
    decisions = _require_list(payload["decisions"], "decisions")
    risk_payloads = _require_list(payload["risks"], "risks")
    action_payloads = _require_list(payload["actions"], "actions")

    risks: list[RiskItem] = []
    for index, item in enumerate(risk_payloads):
        if not isinstance(item, dict) or set(item) != {"description", "owner"}:
            raise BriefError(f"risks[{index}] has missing or unknown fields")
        risks.append(RiskItem(description=item["description"], owner=item["owner"]))

    actions: list[ActionItem] = []
    for index, item in enumerate(action_payloads):
        if not isinstance(item, dict) or set(item) != {
            "description",
            "owner",
            "due_on",
        }:
            raise BriefError(f"actions[{index}] has missing or unknown fields")
        actions.append(
            ActionItem(
                description=item["description"],
                owner=item["owner"],
                due_on=_parse_optional_date(
                    item["due_on"],
                    f"actions[{index}].due_on",
                ),
            )
        )

    return BriefInput(
        title=payload["title"],
        audience=payload["audience"],
        objective=payload["objective"],
        context=tuple(context),
        decisions=tuple(decisions),
        risks=tuple(risks),
        actions=tuple(actions),
    )


def load_brief(path: str | Path) -> BriefInput:
    """Read and validate one UTF-8 JSON brief from local storage."""

    source = Path(path)
    if not source.exists():
        raise BriefError(f"brief file does not exist: {source}")
    if not source.is_file():
        raise BriefError(f"brief path is not a file: {source}")
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except UnicodeDecodeError as exc:
        raise BriefError(f"brief is not valid UTF-8: {source}") from exc
    except json.JSONDecodeError as exc:
        raise BriefError(f"brief is not valid JSON at line {exc.lineno}") from exc
    except OSError as exc:
        raise BriefError(f"could not read brief: {source}") from exc
    return brief_from_dict(payload)
