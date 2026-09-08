import json

import pytest

from briefbot.models import BriefError
from briefbot.policy import load_policy, policy_from_dict


def payload():
    return {
        "schema_version": 1,
        "name": "launch-ready",
        "min_context_items": 2,
        "min_decisions": 1,
        "min_actions": 3,
        "require_action_owners": True,
        "require_action_due_dates": True,
        "require_risk_owners": False,
        "max_overdue_actions": 1,
    }


def test_builds_validated_readiness_policy():
    policy = policy_from_dict(payload())

    assert policy.name == "launch-ready"
    assert policy.min_actions == 3
    assert policy.require_risk_owners is False
    assert policy.max_overdue_actions == 1


@pytest.mark.parametrize(
    "change,message",
    [
        (lambda value: value.update(schema_version=2), "unsupported"),
        (lambda value: value.update(min_actions=-1), "non-negative"),
        (lambda value: value.update(require_action_owners="yes"), "true or false"),
        (lambda value: value.update(extra="unknown"), "exactly"),
    ],
)
def test_rejects_invalid_policy_values(change, message):
    value = payload()
    change(value)

    with pytest.raises(BriefError, match=message):
        policy_from_dict(value)


def test_loads_policy_from_utf8_json(tmp_path):
    path = tmp_path / "policy.json"
    path.write_text(json.dumps(payload()), encoding="utf-8")

    assert load_policy(path).name == "launch-ready"


def test_rejects_malformed_policy_file(tmp_path):
    path = tmp_path / "policy.json"
    path.write_text("not json", encoding="utf-8")

    with pytest.raises(BriefError, match="not valid JSON"):
        load_policy(path)
