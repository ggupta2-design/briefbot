import json
from datetime import date

from briefbot.report import format_workload, workload_to_dict
from briefbot.workload import PortfolioWorkload, WorkloadCounts


def private_portfolio():
    return PortfolioWorkload(
        as_of=date(2026, 9, 12),
        window_days=14,
        discovered=3,
        valid=2,
        invalid=1,
        counts=WorkloadCounts(
            overdue=2,
            due_today=1,
            due_within_window=3,
            due_later=4,
            unscheduled=5,
            assigned=8,
            unassigned=7,
        ),
    )


def test_workload_payload_has_stable_aggregate_shape():
    payload = workload_to_dict(private_portfolio())

    assert payload == {
        "as_of": "2026-09-12",
        "window_days": 14,
        "briefs": {"discovered": 3, "valid": 2, "invalid": 1},
        "actions": {
            "total": 15,
            "overdue": 2,
            "due_today": 1,
            "due_within_window": 3,
            "due_later": 4,
            "unscheduled": 5,
            "assigned": 8,
            "unassigned": 7,
        },
    }


def test_formats_readable_portfolio_workload():
    output = format_workload(private_portfolio())

    assert output.startswith("Brief portfolio workload forecast")
    assert "Forecast window: 14 day(s)" in output
    assert "Briefs invalid: 1" in output
    assert "Actions total: 15" in output
    assert "Unassigned: 7" in output


def test_json_workload_report_contains_no_source_values():
    output = format_workload(private_portfolio(), as_json=True)
    payload = json.loads(output)

    assert payload["actions"]["due_within_window"] == 3
    assert "Secret project" not in output
    assert "Alice" not in output
    assert "brief.json" not in output
    assert set(payload) == {"actions", "as_of", "briefs", "window_days"}
