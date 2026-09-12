import json

from briefbot.cli import run


def write_brief(path):
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "title": "Top secret portfolio item",
                "audience": "Private team",
                "objective": "Confidential goal",
                "context": [],
                "decisions": [],
                "risks": [],
                "actions": [
                    {
                        "description": "Private deliverable",
                        "owner": "Hidden owner",
                        "due_on": "2026-09-12",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


def test_workload_folder_reports_aggregates_and_invalid_status(tmp_path, capsys):
    write_brief(tmp_path / "secret.json")
    (tmp_path / "broken.json").write_text("not json", encoding="utf-8")

    assert run(
        [
            "workload-folder",
            str(tmp_path),
            "--as-of",
            "2026-09-12",
            "--json",
        ]
    ) == 1
    output = capsys.readouterr().out
    payload = json.loads(output)

    assert payload["briefs"] == {"discovered": 2, "valid": 1, "invalid": 1}
    assert payload["actions"]["due_today"] == 1
    assert "secret.json" not in output
    assert "broken.json" not in output
    assert "Top secret portfolio item" not in output
    assert "Hidden owner" not in output


def test_workload_folder_supports_recursive_and_file_limits(tmp_path, capsys):
    nested = tmp_path / "nested"
    nested.mkdir()
    write_brief(nested / "one.json")

    assert run(
        [
            "workload-folder",
            str(tmp_path),
            "--recursive",
            "--max-files",
            "1",
            "--as-of",
            "2026-09-12",
            "--json",
        ]
    ) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["briefs"]["discovered"] == 1
    assert payload["actions"]["total"] == 1


def test_workload_folder_rejects_exceeded_file_limit(tmp_path, capsys):
    write_brief(tmp_path / "one.json")
    write_brief(tmp_path / "two.json")

    assert run(
        ["workload-folder", str(tmp_path), "--max-files", "1"]
    ) == 2
    output = capsys.readouterr()

    assert "more than max_files=1" in output.err
    assert "one.json" not in output.err
    assert "two.json" not in output.err
