import json

from briefbot.readiness import ReadinessPolicy
from briefbot.report import format_policy


def test_json_policy_summary_is_stable():
    policy = ReadinessPolicy(
        name="delivery-ready",
        min_context_items=2,
        min_decisions=3,
        min_actions=4,
        require_action_owners=True,
        require_action_due_dates=False,
        require_risk_owners=True,
        max_overdue_actions=1,
    )

    assert json.loads(format_policy(policy, as_json=True)) == {
        "name": "delivery-ready",
        "requirements": {
            "action_due_dates": False,
            "action_owners": True,
            "risk_owners": True,
        },
        "thresholds": {
            "max_overdue_actions": 1,
            "min_actions": 4,
            "min_context_items": 2,
            "min_decisions": 3,
        },
        "valid": True,
    }


def test_text_policy_summary_explains_all_rules():
    output = format_policy(ReadinessPolicy(name="team-standard"))

    assert "Readiness policy is valid: team-standard" in output
    assert "Minimum context items: 1" in output
    assert "Maximum overdue actions: 0" in output
    assert "Require action owners: true" in output
    assert "Require action due dates: true" in output
    assert "Require risk owners: true" in output
