import json
from datetime import date

from briefbot.disclosure import DisclosurePolicy, build_shared_brief
from briefbot.input import brief_from_dict
from briefbot.report import format_shared_brief


def source():
    return brief_from_dict(
        {
            "schema_version": 1,
            "title": "Launch summary",
            "audience": "Partners",
            "objective": "Private objective",
            "context": ["Secret context"],
            "decisions": ["Approved rollout"],
            "risks": [{"description": "Hidden risk", "owner": "Ari"}],
            "actions": [
                {
                    "description": "Publish checklist",
                    "owner": "Bea",
                    "due_on": "2026-09-12",
                }
            ],
        }
    )


def test_json_output_omits_excluded_fields_entirely():
    policy = DisclosurePolicy(name="external")
    shared = build_shared_brief(source(), as_of=date(2026, 9, 11), policy=policy)

    output = format_shared_brief(shared, as_json=True)
    payload = json.loads(output)

    assert "context" not in payload
    assert "risks" not in payload
    assert payload["actions"][0]["owner"] is None
    assert "Secret context" not in output
    assert "Hidden risk" not in output
    assert "Ari" not in output
    assert "Bea" not in output


def test_markdown_contains_only_permitted_sections_and_metadata():
    policy = DisclosurePolicy(
        name="internal",
        include_context=True,
        include_risks=True,
        include_owner_names=True,
        include_due_dates=False,
    )
    shared = build_shared_brief(source(), as_of=date(2026, 9, 11), policy=policy)

    output = format_shared_brief(shared)

    assert "## Context" in output
    assert "Secret context" in output
    assert "## Risks" in output
    assert "Owner: Ari" in output
    assert "owner: Bea" in output
    assert "2026-09-12" not in output


def test_minimal_policy_produces_valid_header_only_brief():
    policy = DisclosurePolicy(
        name="minimal",
        include_objective=False,
        include_decisions=False,
        include_actions=False,
    )
    shared = build_shared_brief(source(), as_of=date(2026, 9, 11), policy=policy)

    payload = json.loads(format_shared_brief(shared, as_json=True))

    assert set(payload) == {
        "as_of",
        "audience",
        "included_sections",
        "policy",
        "title",
    }
