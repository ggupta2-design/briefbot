"""Readable and machine-readable BriefBot reports."""

from __future__ import annotations

import json
from typing import Any

from .batch import BatchReadinessResult
from .diffing import BriefDiff
from .disclosure import DisclosurePolicy, SharedBrief
from .planning import Brief, PlannedAction
from .readiness import ReadinessPolicy, ReadinessResult


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


def format_policy(policy: ReadinessPolicy, *, as_json: bool = False) -> str:
    """Format a validated readiness policy without reading brief content."""

    payload = {
        "valid": True,
        "name": policy.name,
        "thresholds": {
            "min_context_items": policy.min_context_items,
            "min_decisions": policy.min_decisions,
            "min_actions": policy.min_actions,
            "max_overdue_actions": policy.max_overdue_actions,
        },
        "requirements": {
            "action_owners": policy.require_action_owners,
            "action_due_dates": policy.require_action_due_dates,
            "risk_owners": policy.require_risk_owners,
        },
    }
    if as_json:
        return json.dumps(payload, indent=2, sort_keys=True)

    return (
        f"Readiness policy is valid: {policy.name}\n"
        f"Minimum context items: {policy.min_context_items}\n"
        f"Minimum decisions: {policy.min_decisions}\n"
        f"Minimum actions: {policy.min_actions}\n"
        f"Maximum overdue actions: {policy.max_overdue_actions}\n"
        f"Require action owners: {str(policy.require_action_owners).lower()}\n"
        f"Require action due dates: {str(policy.require_action_due_dates).lower()}\n"
        f"Require risk owners: {str(policy.require_risk_owners).lower()}"
    )


def format_diff(result: BriefDiff, *, as_json: bool = False) -> str:
    """Format a value-free comparison for people or automation."""

    sections = {
        name: {
            "added": section.added,
            "removed": section.removed,
            "unchanged": section.unchanged,
        }
        for name, section in (
            ("context", result.context),
            ("decisions", result.decisions),
            ("risks", result.risks),
            ("actions", result.actions),
        )
    }
    payload = {
        "changed": result.changed,
        "total_changes": result.total_changes,
        "metadata_changed": list(result.metadata_changed),
        "sections": sections,
    }
    if as_json:
        return json.dumps(payload, indent=2, sort_keys=True)

    lines = [
        "Brief version comparison",
        f"Status: {'changes detected' if result.changed else 'no changes'}",
        f"Total changes: {result.total_changes}",
        "Metadata changed: "
        + (", ".join(result.metadata_changed) if result.metadata_changed else "none"),
        "Sections:",
    ]
    lines.extend(
        f"- {name}: +{counts['added']} -{counts['removed']} "
        f"={counts['unchanged']} unchanged"
        for name, counts in sections.items()
    )
    return "\n".join(lines)


def format_batch_readiness(
    result: BatchReadinessResult,
    *,
    as_json: bool = False,
) -> str:
    """Format a path-free folder readiness summary."""

    payload = {
        "as_of": result.as_of.isoformat(),
        "policy": result.policy_name,
        "all_ready": result.all_ready,
        "summary": {
            "discovered": result.discovered,
            "valid": result.valid,
            "invalid": result.invalid,
            "ready": result.ready,
            "review_required": result.review_required,
        },
        "finding_count": result.finding_count,
        "findings": [
            {
                "code": item.code.value,
                "occurrences": item.occurrences,
                "briefs": item.briefs,
            }
            for item in result.findings
        ],
    }
    if as_json:
        return json.dumps(payload, indent=2, sort_keys=True)

    lines = [
        "Brief folder readiness audit",
        f"As of: {result.as_of.isoformat()}",
        f"Policy: {result.policy_name}",
        f"Status: {'all ready' if result.all_ready else 'review required'}",
        f"Discovered: {result.discovered}",
        f"Valid: {result.valid}",
        f"Invalid: {result.invalid}",
        f"Ready: {result.ready}",
        f"Review required: {result.review_required}",
        f"Finding occurrences: {result.finding_count}",
    ]
    if not result.findings:
        lines.append("Findings: none")
    else:
        lines.append("Findings:")
        lines.extend(
            f"- {item.code.value}: {item.occurrences} occurrence(s) "
            f"across {item.briefs} brief(s)"
            for item in result.findings
        )
    return "\n".join(lines)


def shared_brief_to_dict(brief: SharedBrief) -> dict[str, Any]:
    """Return only fields retained in a policy-controlled share view."""

    payload: dict[str, Any] = {
        "policy": brief.policy_name,
        "title": brief.title,
        "audience": brief.audience,
        "as_of": brief.as_of.isoformat(),
        "included_sections": list(brief.included_sections),
    }
    if "objective" in brief.included_sections:
        payload["objective"] = brief.objective
    if "context" in brief.included_sections:
        payload["context"] = list(brief.context)
    if "decisions" in brief.included_sections:
        payload["decisions"] = list(brief.decisions)
    if "risks" in brief.included_sections:
        payload["risks"] = [
            {"description": item.description, "owner": item.owner}
            for item in brief.risks
        ]
    if "actions" in brief.included_sections:
        payload["actions"] = [
            {
                "description": item.description,
                "owner": item.owner,
                "due_on": item.due_on.isoformat() if item.due_on else None,
            }
            for item in brief.actions
        ]
    return payload


def format_shared_brief(brief: SharedBrief, *, as_json: bool = False) -> str:
    """Format a policy-controlled share-ready brief."""

    if as_json:
        return json.dumps(shared_brief_to_dict(brief), indent=2, sort_keys=True)

    lines = [
        f"# {brief.title}",
        "",
        f"**Audience:** {brief.audience}",
        f"**As of:** {brief.as_of.isoformat()}",
        f"**Disclosure policy:** {brief.policy_name}",
    ]
    if "objective" in brief.included_sections:
        lines.extend(["", "## Objective", "", brief.objective or ""])
    for name, heading, values in (
        ("context", "Context", brief.context),
        ("decisions", "Decisions", brief.decisions),
    ):
        if name in brief.included_sections:
            lines.extend(["", *_bullet_section(heading, values)])
    if "risks" in brief.included_sections:
        lines.extend(["", "## Risks", ""])
        lines.extend(
            f"- {item.description}"
            + (f" — Owner: {item.owner}" if item.owner else "")
            for item in brief.risks
        )
        if not brief.risks:
            lines.append("- None recorded.")
    if "actions" in brief.included_sections:
        lines.extend(["", "## Actions", ""])
        for item in brief.actions:
            metadata = []
            if item.owner:
                metadata.append(f"owner: {item.owner}")
            if item.due_on:
                metadata.append(f"due: {item.due_on.isoformat()}")
            suffix = f" ({'; '.join(metadata)})" if metadata else ""
            lines.append(f"- {item.description}{suffix}")
        if not brief.actions:
            lines.append("- None recorded.")
    return "\n".join(lines) + "\n"


def format_disclosure_policy(
    policy: DisclosurePolicy,
    *,
    as_json: bool = False,
) -> str:
    """Format a validated disclosure policy without reading a brief."""

    payload = {
        "valid": True,
        "name": policy.name,
        "sections": {
            "objective": policy.include_objective,
            "context": policy.include_context,
            "decisions": policy.include_decisions,
            "risks": policy.include_risks,
            "actions": policy.include_actions,
        },
        "metadata": {
            "owner_names": policy.include_owner_names,
            "due_dates": policy.include_due_dates,
        },
    }
    if as_json:
        return json.dumps(payload, indent=2, sort_keys=True)
    permitted = [
        name for name, enabled in payload["sections"].items() if enabled
    ]
    return (
        f"Disclosure policy is valid: {policy.name}\n"
        f"Included sections: {', '.join(permitted) if permitted else 'none'}\n"
        f"Include owner names: {str(policy.include_owner_names).lower()}\n"
        f"Include due dates: {str(policy.include_due_dates).lower()}"
    )
