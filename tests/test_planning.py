from datetime import date

from briefbot.models import ActionItem, BriefInput
from briefbot.planning import ActionState, build_brief


def source_with_actions(*actions):
    return BriefInput(
        title="Weekly launch",
        audience="Project team",
        objective="Agree on next steps",
        actions=actions,
    )


def test_actions_are_classified_and_prioritized():
    source = source_with_actions(
        ActionItem("No date"),
        ActionItem("Next task", due_on=date(2026, 9, 9)),
        ActionItem("Late task", due_on=date(2026, 9, 5)),
        ActionItem("Today task", due_on=date(2026, 9, 7)),
    )

    brief = build_brief(source, as_of=date(2026, 9, 7))

    assert [item.state for item in brief.actions] == [
        ActionState.OVERDUE,
        ActionState.DUE_TODAY,
        ActionState.UPCOMING,
        ActionState.UNSCHEDULED,
    ]
    assert [item.days_until for item in brief.actions] == [-2, 0, 2, None]


def test_same_state_actions_use_stable_tie_breakers():
    source = source_with_actions(
        ActionItem("Second", owner="Zoe", due_on=date(2026, 9, 9)),
        ActionItem("Third", owner=None, due_on=date(2026, 9, 9)),
        ActionItem("First", owner="Amy", due_on=date(2026, 9, 9)),
    )

    brief = build_brief(source, as_of=date(2026, 9, 7))

    assert [item.action.description for item in brief.actions] == [
        "Third",
        "First",
        "Second",
    ]


def test_building_a_brief_does_not_mutate_source_notes():
    source = source_with_actions(ActionItem("Task", due_on=date(2026, 9, 8)))

    first = build_brief(source, as_of=date(2026, 9, 7))
    second = build_brief(source, as_of=date(2026, 9, 9))

    assert source.actions[0].due_on == date(2026, 9, 8)
    assert first.actions[0].state == ActionState.UPCOMING
    assert second.actions[0].state == ActionState.OVERDUE
