import json

from briefbot.diffing import compare_briefs
from briefbot.input import brief_from_dict
from briefbot.report import format_diff


def source(title, context, action):
    return brief_from_dict(
        {
            "schema_version": 1,
            "title": title,
            "audience": "Private board",
            "objective": "Confidential objective",
            "context": context,
            "decisions": ["Secret decision"],
            "risks": [{"description": "Private risk", "owner": "Ari"}],
            "actions": [
                {
                    "description": action,
                    "owner": "Bea",
                    "due_on": "2026-09-10",
                }
            ],
        }
    )


def test_json_diff_report_contains_counts_not_values():
    previous = source("Project Oak", ["Internal baseline"], "Old private action")
    current = source("Project Pine", ["Hidden update"], "New private action")

    output = format_diff(compare_briefs(previous, current), as_json=True)
    payload = json.loads(output)

    assert payload["changed"] is True
    assert payload["metadata_changed"] == ["title"]
    assert payload["sections"]["context"] == {
        "added": 1,
        "removed": 1,
        "unchanged": 0,
    }
    for value in (
        "Project Oak",
        "Project Pine",
        "Internal baseline",
        "Hidden update",
        "Old private action",
        "New private action",
        "Confidential objective",
        "Secret decision",
        "Private risk",
        "Ari",
        "Bea",
    ):
        assert value not in output


def test_text_diff_report_explains_aggregate_changes():
    previous = source("Project Oak", ["Baseline"], "Review")
    current = source("Project Pine", ["Baseline", "Update"], "Review")

    output = format_diff(compare_briefs(previous, current))

    assert "Status: changes detected" in output
    assert "Total changes: 2" in output
    assert "Metadata changed: title" in output
    assert "- context: +1 -0 =1 unchanged" in output


def test_unchanged_report_is_explicit():
    brief = source("Same", ["Stable"], "Review")

    output = format_diff(compare_briefs(brief, brief))

    assert "Status: no changes" in output
    assert "Metadata changed: none" in output
