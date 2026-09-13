"""Read-only, value-free integrity audits for project briefs."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import date
from enum import Enum
from pathlib import Path

from .batch import discover_brief_files
from .input import load_brief
from .models import BriefError, BriefInput


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
    """Detect duplicate and inconsistent entries without retaining values."""

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
    action_owners: dict[str, set[str | None]] = {}
    action_dates: dict[str, set[date | None]] = {}
    for item in source.actions:
        key = _text_key(item.description)
        action_owners.setdefault(key, set()).add(
            _text_key(item.owner) if item.owner else None
        )
        action_dates.setdefault(key, set()).add(item.due_on)

    risk_owners: dict[str, set[str | None]] = {}
    for item in source.risks:
        key = _text_key(item.description)
        risk_owners.setdefault(key, set()).add(
            _text_key(item.owner) if item.owner else None
        )

    error_counts = {
        IntegrityCode.ACTION_OWNER_CONFLICT: sum(
            len(owners) > 1 for owners in action_owners.values()
        ),
        IntegrityCode.ACTION_DUE_DATE_CONFLICT: sum(
            len(dates) > 1 for dates in action_dates.values()
        ),
        IntegrityCode.RISK_OWNER_CONFLICT: sum(
            len(owners) > 1 for owners in risk_owners.values()
        ),
    }
    overlap_count = len(set(action_owners) & set(risk_owners))
    warning_counts = {
        **duplicate_counts,
        IntegrityCode.RISK_ACTION_OVERLAP: overlap_count,
    }
    findings = tuple(
        IntegrityFinding(code, severity, count)
        for severity, counts in (
            (IntegritySeverity.ERROR, error_counts),
            (IntegritySeverity.WARNING, warning_counts),
        )
        for code, count in counts.items()
        if count
    )
    findings = tuple(sorted(findings, key=lambda item: item.code.value))
    return BriefIntegrityResult(
        as_of=as_of,
        context_items=len(source.context),
        decisions=len(source.decisions),
        risks=len(source.risks),
        actions=len(source.actions),
        findings=findings,
    )


@dataclass(frozen=True)
class PortfolioIntegrityFinding:
    """One aggregate finding code across a portfolio."""

    code: IntegrityCode
    severity: IntegritySeverity
    occurrences: int
    briefs: int


@dataclass(frozen=True)
class PortfolioIntegrityResult:
    """Path-free integrity audit for a bounded folder."""

    as_of: date
    discovered: int
    valid: int
    invalid: int
    clean_briefs: int
    affected_briefs: int
    findings: tuple[PortfolioIntegrityFinding, ...] = ()

    @property
    def clean(self) -> bool:
        return self.discovered > 0 and self.invalid == 0 and self.affected_briefs == 0

    @property
    def finding_count(self) -> int:
        return sum(item.occurrences for item in self.findings)

    @property
    def error_count(self) -> int:
        return sum(
            item.occurrences
            for item in self.findings
            if item.severity is IntegritySeverity.ERROR
        )

    @property
    def warning_count(self) -> int:
        return self.finding_count - self.error_count


def audit_brief_folder_integrity(
    root: str | Path,
    *,
    as_of: date,
    recursive: bool = False,
    max_files: int = 100,
) -> PortfolioIntegrityResult:
    """Aggregate integrity findings without retaining paths or source values."""

    paths = discover_brief_files(root, recursive=recursive, max_files=max_files)
    valid = clean_briefs = affected_briefs = 0
    occurrences: dict[IntegrityCode, int] = {}
    briefs: dict[IntegrityCode, int] = {}
    severities: dict[IntegrityCode, IntegritySeverity] = {}
    for path in paths:
        try:
            source = load_brief(path)
        except BriefError:
            continue
        valid += 1
        result = audit_brief_integrity(source, as_of=as_of)
        if result.clean:
            clean_briefs += 1
        else:
            affected_briefs += 1
        for finding in result.findings:
            occurrences[finding.code] = (
                occurrences.get(finding.code, 0) + finding.count
            )
            briefs[finding.code] = briefs.get(finding.code, 0) + 1
            severities[finding.code] = finding.severity

    return PortfolioIntegrityResult(
        as_of=as_of,
        discovered=len(paths),
        valid=valid,
        invalid=len(paths) - valid,
        clean_briefs=clean_briefs,
        affected_briefs=affected_briefs,
        findings=tuple(
            PortfolioIntegrityFinding(
                code=code,
                severity=severities[code],
                occurrences=occurrences[code],
                briefs=briefs[code],
            )
            for code in sorted(occurrences, key=lambda item: item.value)
        ),
    )
