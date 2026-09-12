"""Value-free action workload forecasts for project briefs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .batch import discover_brief_files
from .input import load_brief
from .models import BriefError, BriefInput
from .planning import ActionState, build_brief


def validate_window_days(value: int) -> int:
    """Validate a practical, explicit forecast horizon."""

    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 365:
        raise BriefError("window_days must be an integer from 1 to 365")
    return value


@dataclass(frozen=True)
class WorkloadCounts:
    """Aggregate action counts that contain no note or owner values."""

    overdue: int
    due_today: int
    due_within_window: int
    due_later: int
    unscheduled: int
    assigned: int
    unassigned: int

    @property
    def total(self) -> int:
        return (
            self.overdue
            + self.due_today
            + self.due_within_window
            + self.due_later
            + self.unscheduled
        )


@dataclass(frozen=True)
class BriefWorkload:
    """Value-free workload forecast for one validated brief."""

    as_of: date
    window_days: int
    counts: WorkloadCounts


def summarize_brief_workload(
    source: BriefInput,
    *,
    as_of: date,
    window_days: int = 7,
) -> BriefWorkload:
    """Classify actions without retaining titles, descriptions, or owner names."""

    horizon = validate_window_days(window_days)
    counts = {
        "overdue": 0,
        "due_today": 0,
        "due_within_window": 0,
        "due_later": 0,
        "unscheduled": 0,
        "assigned": 0,
        "unassigned": 0,
    }
    for item in build_brief(source, as_of=as_of).actions:
        if item.action.owner is None:
            counts["unassigned"] += 1
        else:
            counts["assigned"] += 1

        if item.state is ActionState.OVERDUE:
            counts["overdue"] += 1
        elif item.state is ActionState.DUE_TODAY:
            counts["due_today"] += 1
        elif item.state is ActionState.UNSCHEDULED:
            counts["unscheduled"] += 1
        elif item.days_until is not None and item.days_until <= horizon:
            counts["due_within_window"] += 1
        else:
            counts["due_later"] += 1

    return BriefWorkload(
        as_of=as_of,
        window_days=horizon,
        counts=WorkloadCounts(**counts),
    )


@dataclass(frozen=True)
class PortfolioWorkload:
    """Path-free workload forecast for a bounded folder of briefs."""

    as_of: date
    window_days: int
    discovered: int
    valid: int
    invalid: int
    counts: WorkloadCounts


def summarize_brief_folder(
    root: str | Path,
    *,
    as_of: date,
    window_days: int = 7,
    recursive: bool = False,
    max_files: int = 100,
) -> PortfolioWorkload:
    """Aggregate workloads while isolating malformed briefs and omitting values."""

    horizon = validate_window_days(window_days)
    paths = discover_brief_files(
        root,
        recursive=recursive,
        max_files=max_files,
    )
    totals = {
        "overdue": 0,
        "due_today": 0,
        "due_within_window": 0,
        "due_later": 0,
        "unscheduled": 0,
        "assigned": 0,
        "unassigned": 0,
    }
    valid = 0
    for path in paths:
        try:
            source = load_brief(path)
        except BriefError:
            continue
        valid += 1
        forecast = summarize_brief_workload(
            source,
            as_of=as_of,
            window_days=horizon,
        )
        for name in totals:
            totals[name] += getattr(forecast.counts, name)

    return PortfolioWorkload(
        as_of=as_of,
        window_days=horizon,
        discovered=len(paths),
        valid=valid,
        invalid=len(paths) - valid,
        counts=WorkloadCounts(**totals),
    )
