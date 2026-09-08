import json
from datetime import date

from briefbot.input import brief_from_dict
from briefbot.readiness import assess_readiness
from briefbot.report import format_readiness


def private_source():
    return brief_from_dict(
        {
            "schema_version": 1,
            "title": "Secret acquisition",
            "audience": "Confidential committee",
            "objective": "Approve Project Redwood",
            "context": ["Nonpublic valuation"],
            "decisions": ["Proceed quietly"],
            "risks": [{"description": "Leak risk", "owner": None}],
            "actions": [
                {
                    "description": "Call private counsel",
                    "owner": None,
                    "due_on": "2026-09-07",
                }
            ],
        }
    )


def test_json_readiness_report_is_value_free():
    result = assess_readiness(private_source(), as_of=date(2026, 9, 8))

    output = format_readiness(result, as_json=True)
    payload = json.loads(output)

    assert payload["ready"] is False
    assert payload["summary"] == {
        "actions": 1,
        "context_items": 1,
        "decisions": 1,
        "risks": 1,
    }
    assert {item["code"] for item in payload["findings"]} == {
        "overdue_action_limit",
        "unowned_action",
        "unowned_risk",
    }
    for private_value in (
        "Secret acquisition",
        "Confidential committee",
        "Project Redwood",
        "Nonpublic valuation",
        "Proceed quietly",
        "Leak risk",
        "Call private counsel",
    ):
        assert private_value not in output


def test_text_readiness_report_explains_aggregate_findings():
    result = assess_readiness(private_source(), as_of=date(2026, 9, 8))

    output = format_readiness(result)

    assert "Status: review required" in output
    assert "Errors: 1" in output
    assert "Warnings: 2" in output
    assert "- overdue_action_limit: 1 (error)" in output


def test_ready_report_has_explicit_empty_findings():
    source = brief_from_dict(
        {
            "schema_version": 1,
            "title": "Ready",
            "audience": "Team",
            "objective": "Ship",
            "context": ["Reviewed"],
            "decisions": ["Approved"],
            "risks": [{"description": "Delay", "owner": "Ari"}],
            "actions": [
                {
                    "description": "Launch",
                    "owner": "Bea",
                    "due_on": "2026-09-09",
                }
            ],
        }
    )
    result = assess_readiness(source, as_of=date(2026, 9, 8))

    assert format_readiness(result).endswith("Findings: none")
