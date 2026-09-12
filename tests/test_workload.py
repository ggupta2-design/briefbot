from datetime import date

import pytest

from briefbot.models import ActionItem, BriefError, BriefInput
from briefbot.workload import summarize_brief_workload, validate_window_days


def source_with_actions() -> BriefInput:
    return BriefInput(
        title="Private roadmap",
        audience="Internal team",
        objective="Coordinate delivery",
        actions=(
            ActionItem("Past item", owner="A", due_on=date(2026, 9, 10)),
            ActionItem("Today item", due_on=date(2026, 9, 12)),
            ActionItem("Near item", owner="B", due_on=date(2026, 9, 18)),
            ActionItem("Later item", due_on=date(2026, 9, 20)),
            ActionItem("Undated item", owner="C"),
        ),
    )


def test_summarizes_schedule_and_assignment_counts():
    result = summarize_brief_workload(
        source_with_actions(),
        as_of=date(2026, 9, 12),
        window_days=7,
    )

    assert result.as_of == date(2026, 9, 12)
    assert result.window_days == 7
    assert result.counts.overdue == 1
    assert result.counts.due_today == 1
    assert result.counts.due_within_window == 1
    assert result.counts.due_later == 1
    assert result.counts.unscheduled == 1
    assert result.counts.assigned == 3
    assert result.counts.unassigned == 2
    assert result.counts.total == 5


def test_forecast_horizon_changes_only_upcoming_buckets():
    short = summarize_brief_workload(
        source_with_actions(),
        as_of=date(2026, 9, 12),
        window_days=3,
    )
    long = summarize_brief_workload(
        source_with_actions(),
        as_of=date(2026, 9, 12),
        window_days=30,
    )

    assert short.counts.due_within_window == 0
    assert short.counts.due_later == 2
    assert long.counts.due_within_window == 2
    assert long.counts.due_later == 0
    assert short.counts.assigned == long.counts.assigned


@pytest.mark.parametrize("value", [0, 366, -1, True, 2.5])
def test_rejects_invalid_forecast_horizons(value):
    with pytest.raises(BriefError, match="window_days"):
        validate_window_days(value)
