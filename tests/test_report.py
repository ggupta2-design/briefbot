import json
from datetime import date

from briefbot.models import ActionItem, BriefInput, RiskItem
from briefbot.planning import build_brief
from briefbot.report import format_brief


def populated_brief():
    source = BriefInput(
        title="Launch review",
        audience="Product team",
        objective="Confirm a safe launch",
        context=("Pilot completed",),
        decisions=("Use a staged rollout",),
        risks=(RiskItem("Schedule pressure", "Garima"),),
        actions=(
            ActionItem("Finish tests", "Dev", date(2026, 9, 6)),
            ActionItem("Write announcement"),
        ),
    )
    return build_brief(source, as_of=date(2026, 9, 7))


def test_markdown_report_contains_every_brief_section():
    output = format_brief(populated_brief())

    assert output.startswith("# Launch review\n")
    assert "## Objective" in output
    assert "## Context" in output
    assert "## Decisions" in output
    assert "## Risks" in output
    assert "## Actions" in output
    assert "Finish tests (overdue; owner: Dev; due: 2026-09-06)" in output
    assert output.endswith("\n")


def test_json_report_has_stable_summary_and_action_metadata():
    payload = json.loads(format_brief(populated_brief(), as_json=True))

    assert payload["as_of"] == "2026-09-07"
    assert payload["summary"] == {
        "actions": 2,
        "context_items": 1,
        "decisions": 1,
        "risks": 1,
    }
    assert payload["actions"][0]["state"] == "overdue"
    assert payload["actions"][0]["days_until"] == -1


def test_empty_sections_are_explicit_in_markdown():
    brief = build_brief(
        BriefInput("Title", "Team", "Goal"),
        as_of=date(2026, 9, 7),
    )

    output = format_brief(brief)

    assert output.count("- None recorded.") == 4
