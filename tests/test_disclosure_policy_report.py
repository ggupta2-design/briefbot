import json

from briefbot.disclosure import DisclosurePolicy
from briefbot.report import format_disclosure_policy


def test_json_disclosure_summary_lists_every_control():
    policy = DisclosurePolicy(
        name="partner-share",
        include_context=True,
        include_risks=True,
        include_owner_names=True,
        include_due_dates=False,
    )

    payload = json.loads(format_disclosure_policy(policy, as_json=True))

    assert payload == {
        "metadata": {"due_dates": False, "owner_names": True},
        "name": "partner-share",
        "sections": {
            "actions": True,
            "context": True,
            "decisions": True,
            "objective": True,
            "risks": True,
        },
        "valid": True,
    }


def test_text_disclosure_summary_explains_permissions():
    policy = DisclosurePolicy(
        name="minimal",
        include_objective=False,
        include_decisions=False,
        include_actions=False,
    )

    output = format_disclosure_policy(policy)

    assert "Disclosure policy is valid: minimal" in output
    assert "Included sections: none" in output
    assert "Include owner names: false" in output
    assert "Include due dates: true" in output
