import json
from datetime import date

import pytest

from briefbot.integrity import IntegrityCode, audit_brief_folder_integrity
from briefbot.models import BriefError


def write_brief(path, context):
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "title": "Confidential initiative",
                "audience": "Private team",
                "objective": "Sensitive objective",
                "context": context,
                "decisions": [],
                "risks": [],
                "actions": [],
            }
        ),
        encoding="utf-8",
    )


def test_aggregates_findings_and_isolates_invalid_briefs(tmp_path):
    write_brief(tmp_path / "clean.json", ["One"])
    write_brief(tmp_path / "duplicate.json", ["Secret", " secret "])
    (tmp_path / "invalid.json").write_text("not json", encoding="utf-8")

    result = audit_brief_folder_integrity(
        tmp_path,
        as_of=date(2026, 9, 13),
    )

    assert result.discovered == 3
    assert result.valid == 2
    assert result.invalid == 1
    assert result.clean_briefs == 1
    assert result.affected_briefs == 1
    assert result.clean is False
    assert result.finding_count == 1
    finding = result.findings[0]
    assert finding.code is IntegrityCode.DUPLICATE_CONTEXT
    assert finding.occurrences == 1
    assert finding.briefs == 1


def test_clean_portfolio_requires_at_least_one_brief(tmp_path):
    empty = audit_brief_folder_integrity(
        tmp_path,
        as_of=date(2026, 9, 13),
    )
    write_brief(tmp_path / "clean.json", ["Unique"])
    clean = audit_brief_folder_integrity(
        tmp_path,
        as_of=date(2026, 9, 13),
    )

    assert empty.clean is False
    assert clean.clean is True


def test_portfolio_integrity_supports_recursive_discovery(tmp_path):
    nested = tmp_path / "nested"
    nested.mkdir()
    write_brief(nested / "brief.json", ["One", "one"])

    shallow = audit_brief_folder_integrity(
        tmp_path,
        as_of=date(2026, 9, 13),
    )
    recursive = audit_brief_folder_integrity(
        tmp_path,
        as_of=date(2026, 9, 13),
        recursive=True,
    )

    assert shallow.discovered == 0
    assert recursive.discovered == 1
    assert recursive.affected_briefs == 1


def test_portfolio_integrity_enforces_file_limit(tmp_path):
    write_brief(tmp_path / "one.json", [])
    write_brief(tmp_path / "two.json", [])

    with pytest.raises(BriefError, match="more than max_files=1"):
        audit_brief_folder_integrity(
            tmp_path,
            as_of=date(2026, 9, 13),
            max_files=1,
        )
