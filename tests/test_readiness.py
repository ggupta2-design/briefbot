from datetime import date

from briefbot.models import ActionItem, BriefInput, RiskItem
from briefbot.readiness import (
    ReadinessCode,
    ReadinessPolicy,
    ReadinessSeverity,
    assess_readiness,
)


AS_OF = date(2026, 9, 8)


def complete_brief(**changes):
    values = {
        "title": "Launch",
        "audience": "Team",
        "objective": "Confirm readiness",
        "context": ("Pilot complete",),
        "decisions": ("Use staged rollout",),
        "risks": (RiskItem("Schedule risk", "Lead"),),
        "actions": (ActionItem("Finish tests", "Dev", date(2026, 9, 9)),),
    }
    values.update(changes)
    return BriefInput(**values)


def codes(result):
    return [item.code for item in result.findings]


def test_complete_brief_passes_default_policy():
    result = assess_readiness(complete_brief(), as_of=AS_OF)

    assert result.ready is True
    assert result.finding_count == 0
    assert result.policy_name == "default"
    assert (result.context_items, result.decisions, result.risks, result.actions) == (
        1,
        1,
        1,
        1,
    )


def test_minimum_section_shortfalls_are_errors():
    result = assess_readiness(
        complete_brief(context=(), decisions=(), actions=()),
        as_of=AS_OF,
    )

    assert set(codes(result)) == {
        ReadinessCode.CONTEXT_BELOW_MINIMUM,
        ReadinessCode.DECISIONS_BELOW_MINIMUM,
        ReadinessCode.ACTIONS_BELOW_MINIMUM,
    }
    assert result.error_count == 3
    assert result.warning_count == 0


def test_missing_owners_and_dates_are_warnings():
    result = assess_readiness(
        complete_brief(
            risks=(RiskItem("Schedule risk"),),
            actions=(ActionItem("Finish tests"),),
        ),
        as_of=AS_OF,
    )

    assert set(codes(result)) == {
        ReadinessCode.UNOWNED_ACTION,
        ReadinessCode.UNSCHEDULED_ACTION,
        ReadinessCode.UNOWNED_RISK,
    }
    assert all(
        item.severity == ReadinessSeverity.WARNING
        for item in result.findings
    )
    assert result.warning_count == 3


def test_overdue_action_limit_reports_actual_overdue_count():
    result = assess_readiness(
        complete_brief(
            actions=(
                ActionItem("One", "Dev", date(2026, 9, 6)),
                ActionItem("Two", "Dev", date(2026, 9, 7)),
            )
        ),
        as_of=AS_OF,
    )

    assert codes(result) == [ReadinessCode.OVERDUE_ACTION_LIMIT]
    assert result.findings[0].count == 2


def test_custom_policy_can_relax_optional_metadata_checks():
    source = complete_brief(
        risks=(RiskItem("Schedule risk"),),
        actions=(ActionItem("Finish tests"),),
    )
    policy = ReadinessPolicy(
        name="early-draft",
        require_action_owners=False,
        require_action_due_dates=False,
        require_risk_owners=False,
    )

    result = assess_readiness(source, as_of=AS_OF, policy=policy)

    assert result.ready is True
    assert result.policy_name == "early-draft"


def test_custom_policy_enforces_larger_minimums():
    policy = ReadinessPolicy(
        name="decision-review",
        min_context_items=3,
        min_decisions=2,
        min_actions=4,
        max_overdue_actions=5,
    )

    result = assess_readiness(complete_brief(), as_of=AS_OF, policy=policy)

    counts = {item.code: item.count for item in result.findings}
    assert counts[ReadinessCode.CONTEXT_BELOW_MINIMUM] == 2
    assert counts[ReadinessCode.DECISIONS_BELOW_MINIMUM] == 1
    assert counts[ReadinessCode.ACTIONS_BELOW_MINIMUM] == 3


def test_policy_allows_bounded_overdue_work():
    policy = ReadinessPolicy(max_overdue_actions=1)
    source = complete_brief(
        actions=(ActionItem("Late", "Dev", date(2026, 9, 7)),)
    )

    assert assess_readiness(source, as_of=AS_OF, policy=policy).ready is True
