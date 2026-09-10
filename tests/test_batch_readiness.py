import json
from datetime import date

from briefbot.batch import audit_brief_folder
from briefbot.readiness import ReadinessPolicy


def write_brief(path, *, owner="Ari", due_on="2026-09-11"):
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "title": "Private project",
                "audience": "Team",
                "objective": "Ship",
                "context": ["Reviewed"],
                "decisions": ["Approved"],
                "risks": [{"description": "Delay", "owner": owner}],
                "actions": [
                    {
                        "description": "Launch",
                        "owner": owner,
                        "due_on": due_on,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


def test_audits_ready_and_review_required_briefs(tmp_path):
    write_brief(tmp_path / "ready.json")
    write_brief(tmp_path / "review.json", owner=None)

    result = audit_brief_folder(tmp_path, as_of=date(2026, 9, 10))

    assert result.discovered == 2
    assert result.valid == 2
    assert result.invalid == 0
    assert result.ready == 1
    assert result.review_required == 1
    assert result.all_ready is False


def test_isolates_invalid_brief_files(tmp_path):
    write_brief(tmp_path / "ready.json")
    (tmp_path / "invalid.json").write_text("not json", encoding="utf-8")

    result = audit_brief_folder(tmp_path, as_of=date(2026, 9, 10))

    assert result.discovered == 2
    assert result.valid == 1
    assert result.invalid == 1
    assert result.ready == 1
    assert result.review_required == 0
    assert result.all_ready is False


def test_all_ready_requires_at_least_one_valid_file(tmp_path):
    empty = audit_brief_folder(tmp_path, as_of=date(2026, 9, 10))
    write_brief(tmp_path / "ready.json")
    ready = audit_brief_folder(tmp_path, as_of=date(2026, 9, 10))

    assert empty.all_ready is False
    assert ready.all_ready is True


def test_applies_custom_policy_to_every_valid_brief(tmp_path):
    write_brief(tmp_path / "one.json", owner=None, due_on=None)
    policy = ReadinessPolicy(
        name="relaxed",
        require_action_owners=False,
        require_action_due_dates=False,
        require_risk_owners=False,
    )

    result = audit_brief_folder(
        tmp_path,
        as_of=date(2026, 9, 10),
        policy=policy,
    )

    assert result.policy_name == "relaxed"
    assert result.ready == 1
