import json
from datetime import date

import pytest

from briefbot.input import brief_from_dict, load_brief
from briefbot.models import BriefError


def payload():
    return {
        "schema_version": 1,
        "title": "Launch review",
        "audience": "Product team",
        "objective": "Confirm readiness",
        "context": ["Pilot completed"],
        "decisions": ["Keep the rollout private"],
        "risks": [{"description": "Schedule may slip", "owner": "Garima"}],
        "actions": [
            {
                "description": "Finish test plan",
                "owner": "Dev",
                "due_on": "2026-09-09",
            }
        ],
    }


def test_builds_brief_from_strict_payload():
    brief = brief_from_dict(payload())

    assert brief.title == "Launch review"
    assert brief.actions[0].due_on == date(2026, 9, 9)
    assert brief.risks[0].owner == "Garima"


@pytest.mark.parametrize(
    "change,message",
    [
        (lambda value: value.update(schema_version=2), "unsupported"),
        (lambda value: value.update(context="not a list"), "must be a list"),
        (lambda value: value["actions"][0].update(extra=True), "unknown fields"),
        (lambda value: value["actions"][0].update(due_on="09/09/2026"), "YYYY-MM-DD"),
    ],
)
def test_rejects_invalid_or_ambiguous_payloads(change, message):
    value = payload()
    change(value)

    with pytest.raises(BriefError, match=message):
        brief_from_dict(value)


def test_rejects_unknown_root_fields():
    value = payload()
    value["api_key"] = "must not be accepted"

    with pytest.raises(BriefError, match="exactly"):
        brief_from_dict(value)


def test_loads_utf8_json_file(tmp_path):
    path = tmp_path / "brief.json"
    path.write_text(json.dumps(payload()), encoding="utf-8")

    assert load_brief(path).objective == "Confirm readiness"


@pytest.mark.parametrize("content,message", [("not json", "not valid JSON"), ("[]", "exactly")])
def test_rejects_malformed_files(tmp_path, content, message):
    path = tmp_path / "brief.json"
    path.write_text(content, encoding="utf-8")

    with pytest.raises(BriefError, match=message):
        load_brief(path)
