from datetime import date

from briefbot.disclosure import DisclosurePolicy, build_shared_brief
from briefbot.input import brief_from_dict


def source():
    return brief_from_dict(
        {
            "schema_version": 1,
            "title": "Private launch",
            "audience": "Partner team",
            "objective": "Approve launch",
            "context": ["Confidential customer signal"],
            "decisions": ["Use staged rollout"],
            "risks": [{"description": "Timeline", "owner": "Ari"}],
            "actions": [
                {
                    "description": "Review controls",
                    "owner": "Bea",
                    "due_on": "2026-09-12",
                }
            ],
        }
    )


def test_builds_conservative_share_view():
    policy = DisclosurePolicy(name="external")
    result = build_shared_brief(source(), as_of=date(2026, 9, 11), policy=policy)

    assert result.policy_name == "external"
    assert result.objective == "Approve launch"
    assert result.context == ()
    assert result.decisions == ("Use staged rollout",)
    assert result.risks == ()
    assert result.actions[0].description == "Review controls"
    assert result.actions[0].owner is None
    assert result.actions[0].due_on == date(2026, 9, 12)
    assert result.included_sections == ("objective", "decisions", "actions")


def test_owner_and_due_metadata_require_explicit_permission():
    policy = DisclosurePolicy(
        name="internal",
        include_risks=True,
        include_owner_names=True,
        include_due_dates=False,
    )

    result = build_shared_brief(source(), as_of=date(2026, 9, 11), policy=policy)

    assert result.risks[0].owner == "Ari"
    assert result.actions[0].owner == "Bea"
    assert result.actions[0].due_on is None


def test_excluded_sections_do_not_retain_source_values():
    policy = DisclosurePolicy(
        name="minimal",
        include_objective=False,
        include_context=False,
        include_decisions=False,
        include_risks=False,
        include_actions=False,
    )

    result = build_shared_brief(source(), as_of=date(2026, 9, 11), policy=policy)

    assert result.objective is None
    assert result.context == ()
    assert result.decisions == ()
    assert result.risks == ()
    assert result.actions == ()
    assert result.included_sections == ()
