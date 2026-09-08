"""Readable and machine-readable BriefBot reports."""

from __future__ import annotations

import json
from typing import Any

from .planning import Brief, PlannedAction
from .readiness import ReadinessResult


def _action_payload(item: PlannedAction) -> dict[str, Any]:
    return {
        "description": item.action.description,
        "owner": item.action.owner,
        "due_on": item.action.due_on.isoformat() if item.action.due_on else None,
        "state": item.state.value,
        "days_until": item.days_until,
    }


def brief_to_dict(brief: Brief) -> dict[str, Any]:
    """Return a stable JSON-compatible brief payload."""

    return {
        "title": brief.title,
        "audience": brief.audience,
        "objective": brief.objective,
        "as_of": brief.as_of.isoformat(),
        "summary": {
            "context_items": len(brief.context),
            "decisions": len(brief.decisions),
            "risks": len(brief.risks),
            "actions": len(brief.actions),
        },
        "context": list(brief.context),
        "decisions": list(brief.decisions),
        "risks": [
            {"description": item.description, "owner": item.owner}
            for item in brief.risks
        ],
        "actions": [_action_payload(item) for item in brief.actions],
    }


def _bullet_section(heading: str, items: tuple[str, ...]) -> list[str]:
    lines = [f"## {heading}", ""]
    if items:
        lines.extend(f"- {item}" for item in items)
    else:
        lines.append("- None recorded.")
    return lines


def format_brief(brief: Brief, *, as_json: bool = False) -> str:
    """Format a complete brief as deterministic Markdown or JSON."""

    if as_json:
        return json.dumps(brief_to_dict(brief), indent=2, sort_keys=True)

    lines = [
        f"# {brief.title}",
        "",
        f"**Audience:** {brief.audience}",
        f"**As of:** {brief.as_of.isoformat()}",
        "",
        "## Objective",
        "",
        brief.objective,
        "",
        *_bullet_section("Context", brief.context),
        "",
        *_bullet_section("Decisions", brief.decisions),
        "",
        "## Risks",
        "",
    ]
    if brief.risks:
        for risk in brief.risks:
            owner = f" — Owner: {risk.owner}" if risk.owner else ""
            lines.append(f"- {risk.description}{owner}")
    else:
        lines.append("- None recorded.")

    lines.extend(["", "## Actions", ""])
    if brief.actions:
        for item in brief.actions:
            action = item.action
            metadata = [item.state.value.replace("_", " ")]
            if action.owner:
                metadata.append(f"owner: {action.owner}")
            if action.due_on:
                metadata.append(f"due: {action.due_on.isoformat()}")
            lines.append(f"- {action.description} ({'; '.join(metadata)})")
    else:
        lines.append("- None recorded.")
    return "\n".join(lines) + "\n"


def format_readiness(
    result: ReadinessResult,
    *,
    as_json: bool = False,
) -> str:
    """Format value-free readiness findings for people or automation."""

    payload = {
        "as_of": result.as_of.isoformat(),
        "policy": result.policy_name,
        "ready": result.ready,
        "summary": {
            "context_items": result.context_items,
            "decisions": result.decisions,
            "risks": result.risks,
            "actions": result.actions,
        },
        "finding_count": result.finding_count,
        "error_count": result.error_count,
        "warning_count": result.warning_count,
        "findings": [
            {
                "code": item.code.value,
                "severity": item.severity.value,
                "count": item.count,
            }
            for item in result.findings
        ],
    }
    if as_json:
        return json.dumps(payload, indent=2, sort_keys=True)

    lines = [
        "Brief readiness check",
        f"As of: {result.as_of.isoformat()}",
        f"Policy: {result.policy_name}",
        f"Status: {'ready' if result.ready else 'review required'}",
        f"Errors: {result.error_count}",
        f"Warnings: {result.warning_count}",
    ]
    if not result.findings:
        lines.append("Findings: none")
    else:
        lines.append("Findings:")
        lines.extend(
            f"- {item.code.value}: {item.count} ({item.severity.value})"
            for item in result.findings
        )
    return "\n".join(lines)
