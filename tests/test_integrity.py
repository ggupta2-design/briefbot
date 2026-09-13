from datetime import date

from briefbot.integrity import IntegrityCode, IntegritySeverity, audit_brief_integrity
from briefbot.models import ActionItem, BriefInput, RiskItem


def test_detects_normalized_duplicate_section_entries():
    source = BriefInput(
        title="Private project",
        audience="Internal",
        objective="Deliver safely",
        context=("Pilot ready", "  PILOT   READY  ", "Unique context"),
        decisions=("Ship slowly", "ship slowly"),
        risks=(
            RiskItem("Capacity", "A"),
            RiskItem(" capacity ", "a"),
        ),
        actions=(
            ActionItem("Review", "B", date(2026, 9, 14)),
            ActionItem(" REVIEW ", "b", date(2026, 9, 14)),
        ),
    )

    result = audit_brief_integrity(source, as_of=date(2026, 9, 13))
    by_code = {item.code: item for item in result.findings}

    assert result.clean is False
    assert result.finding_count == 4
    assert result.warning_count == 4
    assert result.error_count == 0
    assert set(by_code) == {
        IntegrityCode.DUPLICATE_CONTEXT,
        IntegrityCode.DUPLICATE_DECISION,
        IntegrityCode.DUPLICATE_RISK,
        IntegrityCode.DUPLICATE_ACTION,
    }
    assert all(
        item.severity is IntegritySeverity.WARNING
        for item in result.findings
    )


def test_reports_clean_brief_without_retaining_values():
    source = BriefInput(
        title="Secret project",
        audience="Private team",
        objective="Confidential goal",
        context=("One",),
        decisions=("Two",),
        risks=(RiskItem("Three"),),
        actions=(ActionItem("Four"),),
    )

    result = audit_brief_integrity(source, as_of=date(2026, 9, 13))

    assert result.clean is True
    assert result.findings == ()
    assert result.context_items == 1
    assert result.decisions == 1
    assert result.risks == 1
    assert result.actions == 1
    assert not hasattr(result, "title")
    assert not hasattr(result, "audience")


def test_detects_conflicting_action_and_risk_records():
    source = BriefInput(
        title="Private",
        audience="Internal",
        objective="Coordinate",
        risks=(
            RiskItem("Launch delay", "A"),
            RiskItem("launch delay", "B"),
        ),
        actions=(
            ActionItem("Security review", "A", date(2026, 9, 14)),
            ActionItem("security review", "B", date(2026, 9, 15)),
            ActionItem("Launch delay", "C", date(2026, 9, 16)),
        ),
    )

    result = audit_brief_integrity(source, as_of=date(2026, 9, 13))
    by_code = {item.code: item for item in result.findings}

    assert by_code[IntegrityCode.ACTION_OWNER_CONFLICT].count == 1
    assert by_code[IntegrityCode.ACTION_DUE_DATE_CONFLICT].count == 1
    assert by_code[IntegrityCode.RISK_OWNER_CONFLICT].count == 1
    assert by_code[IntegrityCode.RISK_ACTION_OVERLAP].count == 1
    assert result.error_count == 3
    assert result.warning_count == 1


def test_same_description_and_metadata_is_duplicate_not_conflict():
    source = BriefInput(
        title="Private",
        audience="Internal",
        objective="Coordinate",
        risks=(RiskItem("Risk", "A"), RiskItem("risk", "a")),
        actions=(
            ActionItem("Task", "B", date(2026, 9, 14)),
            ActionItem("task", "b", date(2026, 9, 14)),
        ),
    )

    result = audit_brief_integrity(source, as_of=date(2026, 9, 13))
    codes = {item.code for item in result.findings}

    assert IntegrityCode.DUPLICATE_RISK in codes
    assert IntegrityCode.DUPLICATE_ACTION in codes
    assert IntegrityCode.ACTION_OWNER_CONFLICT not in codes
    assert IntegrityCode.ACTION_DUE_DATE_CONFLICT not in codes
    assert IntegrityCode.RISK_OWNER_CONFLICT not in codes
