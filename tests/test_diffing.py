from briefbot.diffing import compare_briefs
from briefbot.input import brief_from_dict


def source(**changes):
    payload = {
        "schema_version": 1,
        "title": "Launch",
        "audience": "Team",
        "objective": "Ship safely",
        "context": ["Pilot complete", "Budget approved"],
        "decisions": ["Use staged rollout"],
        "risks": [{"description": "Delay", "owner": "Ari"}],
        "actions": [
            {
                "description": "Review controls",
                "owner": "Bea",
                "due_on": "2026-09-10",
            }
        ],
    }
    payload.update(changes)
    return brief_from_dict(payload)


def test_identical_briefs_have_no_changes():
    result = compare_briefs(source(), source())

    assert result.changed is False
    assert result.total_changes == 0
    assert result.metadata_changed == ()
    assert result.context.added == 0
    assert result.context.removed == 0
    assert result.context.unchanged == 2


def test_counts_collection_additions_and_removals():
    previous = source()
    current = source(
        context=["Budget approved", "Security reviewed"],
        decisions=["Use staged rollout", "Require approval"],
        risks=[],
        actions=[],
    )

    result = compare_briefs(previous, current)

    assert (result.context.added, result.context.removed) == (1, 1)
    assert (result.decisions.added, result.decisions.removed) == (1, 0)
    assert (result.risks.added, result.risks.removed) == (0, 1)
    assert (result.actions.added, result.actions.removed) == (0, 1)
    assert result.total_changes == 5


def test_reports_only_changed_metadata_field_names():
    result = compare_briefs(
        source(),
        source(title="Private rename", objective="Confidential direction"),
    )

    assert result.metadata_changed == ("title", "objective")
    assert result.total_changes == 2


def test_preserves_duplicate_items_during_comparison():
    previous = source(context=["Repeated", "Repeated", "Stable"])
    current = source(context=["Repeated", "Stable", "Stable"])

    result = compare_briefs(previous, current)

    assert result.context.added == 1
    assert result.context.removed == 1
    assert result.context.unchanged == 2


def test_owner_or_due_date_change_is_counted_as_action_replacement():
    previous = source()
    current = source(
        actions=[
            {
                "description": "Review controls",
                "owner": "Casey",
                "due_on": "2026-09-11",
            }
        ]
    )

    result = compare_briefs(previous, current)

    assert result.actions.added == 1
    assert result.actions.removed == 1
    assert result.actions.unchanged == 0
