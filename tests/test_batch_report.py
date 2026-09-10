import json
from datetime import date

from briefbot.batch import BatchFinding, BatchReadinessResult
from briefbot.readiness import ReadinessCode
from briefbot.report import format_batch_readiness


def result():
    return BatchReadinessResult(
        as_of=date(2026, 9, 10),
        policy_name="team-standard",
        discovered=3,
        valid=2,
        invalid=1,
        ready=1,
        review_required=1,
        findings=(
            BatchFinding(
                code=ReadinessCode.UNOWNED_ACTION,
                occurrences=2,
                briefs=1,
            ),
        ),
    )


def test_json_folder_report_contains_only_aggregate_results():
    output = format_batch_readiness(result(), as_json=True)
    payload = json.loads(output)

    assert payload == {
        "all_ready": False,
        "as_of": "2026-09-10",
        "finding_count": 2,
        "findings": [
            {
                "briefs": 1,
                "code": "unowned_action",
                "occurrences": 2,
            }
        ],
        "policy": "team-standard",
        "summary": {
            "discovered": 3,
            "invalid": 1,
            "ready": 1,
            "review_required": 1,
            "valid": 2,
        },
    }


def test_text_folder_report_explains_review_status():
    output = format_batch_readiness(result())

    assert "Status: review required" in output
    assert "Invalid: 1" in output
    assert "Finding occurrences: 2" in output
    assert "- unowned_action: 2 occurrence(s) across 1 brief(s)" in output


def test_folder_report_does_not_include_paths_or_note_values():
    output = format_batch_readiness(result(), as_json=True)

    for private_value in (
        "/private/client/launch.json",
        "Secret launch",
        "Confidential objective",
        "Private owner",
    ):
        assert private_value not in output
