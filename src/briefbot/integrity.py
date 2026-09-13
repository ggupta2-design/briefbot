"""Read-only, value-free integrity audits for project briefs."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import date
from enum import Enum

from .models import BriefInput


class IntegritySeverity(str, Enum):
    WARNING = "warning"
    ERROR = "error"


class IntegrityCode(str, Enum):
    DUPLICATE_CONTEXT = "duplicate_context"
    DUPLICATE_DECISION = "duplicate_decision"
    DUPLICATE_RISK = "duplicate_risk"
    DUPLICATE_ACTION = "duplicate_action"
    ACTION_OWNER_CONFLICT = "action_owner_conflict"
    ACTION_DUE_DATE_CONFLICT = "action_due_date_conflict"
    RISK_OWNER_CONFLICT = "risk_owner_conflict"
    RISK_ACTION_OVERLAP = "risk_action_overlap"


@dataclass(frozen=True)
class IntegrityFinding:
    """One aggregate finding without source values or positions."""

    code: IntegrityCode
    severity: IntegritySeverity
    count: int


@dataclass(frozen=True)
class BriefIntegrityResult:
    """Value-free integrity result for one validated brief."""

    as_of: date
    context_items: int
    decisions: int
    risks: int
    actions: int
    findings: tuple[IntegrityFinding, ...] = ()

    @property
    def clean(self) -> bool:
        return not self.findings

    @property
    def finding_count(self) -> int:
        return sum(item.count for item in self.findings)

    @property
    def error_count(self) -> int:
        return sum(
            item.count
            for item in self.findings
            if item.severity is IntegritySeverity.ERROR
        )

    @property
    def warning_count(self) -> int:
        return self.finding_count - self.error_count


def _text_key(value: str) -> str:
    return " ".join(value.split()).casefold()


def _duplicate_count(values) -> int:
    counts = Counter(values)
    return sum(count - 1 for count in counts.values() if count > 1)


def audit_brief_integrity(
    source: BriefInput,
    *,
    as_of: date,
) -> BriefIntegrityResult:
    """Detect duplicate entries without changing or retaining source values."""

    duplicate_counts = {
        IntegrityCode.DUPLICATE_CONTEXT: _duplicate_count(
            _text_key(item) for item in source.context
        ),
        IntegrityCode.DUPLICATE_DECISION: _duplicate_count(
            _text_key(item) for item in source.decisions
        ),
        IntegrityCode.DUPLICATE_RISK: _duplicate_count(
            (_text_key(item.description), _text_key(item.owner or ""))
            for item in source.risks
        ),
        IntegrityCode.DUPLICATE_ACTION: _duplicate_count(
            (
                _text_key(item.description),
                _text_key(item.owner or ""),
                item.due_on,
            )
            for item in source.actions
        ),
    }
    findings = tuple(
        IntegrityFinding(code, IntegritySeverity.WARNING, count)
        for code, count in sorted(
            duplicate_counts.items(),
            key=lambda item: item[0].value,
        )
        if count
    )
    return BriefIntegrityResult(
        as_of=as_of,
        context_items=len(source.context),
        decisions=len(source.decisions),
        risks=len(source.risks),
        actions=len(source.actions),
        findings=findings,
    )
