import json
from datetime import date

from briefbot.integrity import (
    BriefIntegrityResult,
    IntegrityCode,
    IntegrityFinding,
    IntegritySeverity,
    PortfolioIntegrityFinding,
    PortfolioIntegrityResult,
)
from briefbot.report import format_integrity, integrity_to_dict


def test_formats_single_brief_integrity_without_values():
    result = BriefIntegrityResult(
        as_of=date(2026, 9, 13),
        context_items=2,
        decisions=1,
        risks=1,
        actions=3,
        findings=(
            IntegrityFinding(
                IntegrityCode.DUPLICATE_ACTION,
                IntegritySeverity.WARNING,
                1,
            ),
        ),
    )

    output = format_integrity(result, as_json=True)
    payload = json.loads(output)

    assert payload["clean"] is False
    assert payload["summary"]["actions"] == 3
    assert payload["findings"][0] == {
        "code": "duplicate_action",
        "severity": "warning",
        "count": 1,
    }
    assert "Secret task" not in output
    assert "Owner name" not in output


def test_formats_path_free_portfolio_integrity():
    result = PortfolioIntegrityResult(
        as_of=date(2026, 9, 13),
        discovered=4,
        valid=3,
        invalid=1,
        clean_briefs=1,
        affected_briefs=2,
        findings=(
            PortfolioIntegrityFinding(
                IntegrityCode.ACTION_OWNER_CONFLICT,
                IntegritySeverity.ERROR,
                occurrences=2,
                briefs=2,
            ),
        ),
    )

    output = format_integrity(result)
    payload = integrity_to_dict(result)

    assert output.startswith("Brief portfolio integrity audit")
    assert "Affected briefs: 2" in output
    assert "action_owner_conflict: 2 (error) across 2 brief(s)" in output
    assert payload["summary"]["invalid"] == 1
    assert payload["findings"][0]["briefs"] == 2
    assert "private.json" not in output
    assert "/private/briefs" not in output


def test_clean_integrity_report_has_no_findings():
    result = BriefIntegrityResult(
        as_of=date(2026, 9, 13),
        context_items=0,
        decisions=0,
        risks=0,
        actions=0,
    )

    assert format_integrity(result).endswith("Findings: none")
    assert integrity_to_dict(result)["findings"] == []
