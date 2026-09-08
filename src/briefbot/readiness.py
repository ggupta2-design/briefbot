"""Configurable, value-free readiness checks for project briefs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum

from .models import BriefError, BriefInput, validate_text


class ReadinessSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"


class ReadinessCode(str, Enum):
    CONTEXT_BELOW_MINIMUM = "context_below_minimum"
    DECISIONS_BELOW_MINIMUM = "decisions_below_minimum"
    ACTIONS_BELOW_MINIMUM = "actions_below_minimum"
    UNOWNED_ACTION = "unowned_action"
    UNSCHEDULED_ACTION = "unscheduled_action"
    UNOWNED_RISK = "unowned_risk"
    OVERDUE_ACTION_LIMIT = "overdue_action_limit"


def _non_negative(value: int, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise BriefError(f"{field_name} must be a non-negative integer")
    return value


@dataclass(frozen=True)
class ReadinessPolicy:
    """Reusable thresholds for deciding whether a brief needs review."""

    name: str = "default"
    min_context_items: int = 1
    min_decisions: int = 1
    min_actions: int = 1
    require_action_owners: bool = True
    require_action_due_dates: bool = True
    require_risk_owners: bool = True
    max_overdue_actions: int = 0

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "name",
            validate_text(self.name, "policy name", max_length=200),
        )
        for field_name in (
            "min_context_items",
            "min_decisions",
            "min_actions",
            "max_overdue_actions",
        ):
            object.__setattr__(
                self,
                field_name,
                _non_negative(getattr(self, field_name), field_name),
            )
        for field_name in (
            "require_action_owners",
            "require_action_due_dates",
            "require_risk_owners",
        ):
            if not isinstance(getattr(self, field_name), bool):
                raise BriefError(f"{field_name} must be true or false")


@dataclass(frozen=True)
class ReadinessFinding:
    """Aggregate count for one readiness category."""

    code: ReadinessCode
    severity: ReadinessSeverity
    count: int


@dataclass(frozen=True)
class ReadinessResult:
    """Value-free outcome for a policy check."""

    as_of: date
    policy_name: str
    context_items: int
    decisions: int
    risks: int
    actions: int
    findings: tuple[ReadinessFinding, ...]

    @property
    def ready(self) -> bool:
        return not self.findings

    @property
    def finding_count(self) -> int:
        return sum(item.count for item in self.findings)

    @property
    def error_count(self) -> int:
        return sum(
            item.count
            for item in self.findings
            if item.severity == ReadinessSeverity.ERROR
        )

    @property
    def warning_count(self) -> int:
        return sum(
            item.count
            for item in self.findings
            if item.severity == ReadinessSeverity.WARNING
        )


def assess_readiness(
    source: BriefInput,
    *,
    as_of: date,
    policy: ReadinessPolicy | None = None,
) -> ReadinessResult:
    """Evaluate a brief without retaining or returning its text values."""

    selected = policy or ReadinessPolicy()
    findings: list[ReadinessFinding] = []

    minimums = (
        (
            len(source.context),
            selected.min_context_items,
            ReadinessCode.CONTEXT_BELOW_MINIMUM,
        ),
        (
            len(source.decisions),
            selected.min_decisions,
            ReadinessCode.DECISIONS_BELOW_MINIMUM,
        ),
        (
            len(source.actions),
            selected.min_actions,
            ReadinessCode.ACTIONS_BELOW_MINIMUM,
        ),
    )
    for actual, minimum, code in minimums:
        if actual < minimum:
            findings.append(
                ReadinessFinding(code, ReadinessSeverity.ERROR, minimum - actual)
            )

    checks = (
        (
            selected.require_action_owners,
            sum(item.owner is None for item in source.actions),
            ReadinessCode.UNOWNED_ACTION,
        ),
        (
            selected.require_action_due_dates,
            sum(item.due_on is None for item in source.actions),
            ReadinessCode.UNSCHEDULED_ACTION,
        ),
        (
            selected.require_risk_owners,
            sum(item.owner is None for item in source.risks),
            ReadinessCode.UNOWNED_RISK,
        ),
    )
    for enabled, count, code in checks:
        if enabled and count:
            findings.append(
                ReadinessFinding(code, ReadinessSeverity.WARNING, count)
            )

    overdue = sum(
        item.due_on is not None and item.due_on < as_of
        for item in source.actions
    )
    if overdue > selected.max_overdue_actions:
        findings.append(
            ReadinessFinding(
                ReadinessCode.OVERDUE_ACTION_LIMIT,
                ReadinessSeverity.ERROR,
                overdue,
            )
        )

    return ReadinessResult(
        as_of=as_of,
        policy_name=selected.name,
        context_items=len(source.context),
        decisions=len(source.decisions),
        risks=len(source.risks),
        actions=len(source.actions),
        findings=tuple(
            sorted(
                findings,
                key=lambda item: (item.severity.value, item.code.value),
            )
        ),
    )
