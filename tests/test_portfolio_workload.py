import json
from datetime import date

import pytest

from briefbot.models import BriefError
from briefbot.workload import summarize_brief_folder


def write_brief(path, actions):
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "title": "Confidential initiative",
                "audience": "Private working group",
                "objective": "Deliver a sensitive outcome",
                "context": ["Private context"],
                "decisions": ["Private decision"],
                "risks": [],
                "actions": actions,
            }
        ),
        encoding="utf-8",
    )


def test_aggregates_valid_briefs_and_isolates_invalid_files(tmp_path):
    write_brief(
        tmp_path / "one.json",
        [
            {"description": "Secret overdue", "owner": "Alice", "due_on": "2026-09-10"},
            {"description": "Secret upcoming", "owner": None, "due_on": "2026-09-15"},
        ],
    )
    write_brief(
        tmp_path / "two.json",
        [{"description": "Secret undated", "owner": "Bob", "due_on": None}],
    )
    (tmp_path / "invalid.json").write_text("not json", encoding="utf-8")

    result = summarize_brief_folder(
        tmp_path,
        as_of=date(2026, 9, 12),
        window_days=7,
    )

    assert (result.discovered, result.valid, result.invalid) == (3, 2, 1)
    assert result.counts.total == 3
    assert result.counts.overdue == 1
    assert result.counts.due_within_window == 1
    assert result.counts.unscheduled == 1
    assert result.counts.assigned == 2
    assert result.counts.unassigned == 1


def test_folder_forecast_honors_recursive_discovery(tmp_path):
    nested = tmp_path / "nested"
    nested.mkdir()
    write_brief(
        nested / "brief.json",
        [{"description": "Hidden action", "owner": None, "due_on": None}],
    )

    shallow = summarize_brief_folder(tmp_path, as_of=date(2026, 9, 12))
    recursive = summarize_brief_folder(
        tmp_path,
        as_of=date(2026, 9, 12),
        recursive=True,
    )

    assert shallow.discovered == 0
    assert recursive.discovered == 1
    assert recursive.counts.unscheduled == 1


def test_folder_forecast_uses_existing_file_limit_safeguard(tmp_path):
    write_brief(tmp_path / "one.json", [])
    write_brief(tmp_path / "two.json", [])

    with pytest.raises(BriefError, match="more than max_files=1"):
        summarize_brief_folder(
            tmp_path,
            as_of=date(2026, 9, 12),
            max_files=1,
        )


def test_folder_forecast_rejects_symlink_root(tmp_path):
    real = tmp_path / "real"
    real.mkdir()
    linked = tmp_path / "linked"
    linked.symlink_to(real, target_is_directory=True)

    with pytest.raises(BriefError, match="symbolic link"):
        summarize_brief_folder(linked, as_of=date(2026, 9, 12))
