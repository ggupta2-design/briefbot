import json

import pytest

from briefbot.models import BriefError
from briefbot.share_policy import (
    disclosure_policy_from_dict,
    load_disclosure_policy,
)


def payload():
    return {
        "schema_version": 1,
        "name": "external",
        "include_objective": True,
        "include_context": False,
        "include_decisions": True,
        "include_risks": False,
        "include_actions": True,
        "include_owner_names": False,
        "include_due_dates": True,
    }


def test_builds_strict_disclosure_policy():
    policy = disclosure_policy_from_dict(payload())

    assert policy.name == "external"
    assert policy.include_context is False
    assert policy.include_actions is True


@pytest.mark.parametrize(
    "change,message",
    [
        (lambda value: value.update(schema_version=2), "unsupported"),
        (lambda value: value.update(extra=True), "exactly"),
        (lambda value: value.pop("include_actions"), "exactly"),
        (lambda value: value.update(include_risks="yes"), "true or false"),
    ],
)
def test_rejects_invalid_disclosure_policies(change, message):
    value = payload()
    change(value)

    with pytest.raises(BriefError, match=message):
        disclosure_policy_from_dict(value)


def test_loads_disclosure_policy_from_json(tmp_path):
    path = tmp_path / "sharing.json"
    path.write_text(json.dumps(payload()), encoding="utf-8")

    assert load_disclosure_policy(path).name == "external"


def test_rejects_malformed_disclosure_policy(tmp_path):
    path = tmp_path / "sharing.json"
    path.write_text("not json", encoding="utf-8")

    with pytest.raises(BriefError, match="not valid JSON"):
        load_disclosure_policy(path)
