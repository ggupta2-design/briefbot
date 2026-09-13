import json

from briefbot.cli import run


def write_brief(path, decisions):
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "title": "Private project",
                "audience": "Internal",
                "objective": "Secret",
                "context": [],
                "decisions": decisions,
                "risks": [],
                "actions": [],
            }
        ),
        encoding="utf-8",
    )


def test_folder_integrity_aggregates_without_paths_or_values(tmp_path, capsys):
    write_brief(tmp_path / "affected.json", ["Sensitive choice", "sensitive choice"])
    write_brief(tmp_path / "clean.json", ["Unique"])
    (tmp_path / "broken.json").write_text("not json", encoding="utf-8")

    assert run(
        [
            "audit-integrity-folder",
            str(tmp_path),
            "--as-of",
            "2026-09-13",
            "--json",
        ]
    ) == 1
    output = capsys.readouterr().out
    payload = json.loads(output)

    assert payload["summary"] == {
        "discovered": 3,
        "valid": 2,
        "invalid": 1,
        "clean": 1,
        "affected": 1,
    }
    assert payload["findings"][0]["code"] == "duplicate_decision"
    assert "affected.json" not in output
    assert "clean.json" not in output
    assert "Sensitive choice" not in output
    assert "Private project" not in output


def test_folder_integrity_supports_recursive_bounded_scans(tmp_path, capsys):
    nested = tmp_path / "nested"
    nested.mkdir()
    write_brief(nested / "clean.json", ["Unique"])

    assert run(
        [
            "audit-integrity-folder",
            str(tmp_path),
            "--recursive",
            "--max-files",
            "1",
            "--as-of",
            "2026-09-13",
            "--json",
        ]
    ) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["clean"] is True
    assert payload["summary"]["discovered"] == 1


def test_folder_integrity_enforces_file_limit(tmp_path, capsys):
    write_brief(tmp_path / "one.json", [])
    write_brief(tmp_path / "two.json", [])

    assert run(
        ["audit-integrity-folder", str(tmp_path), "--max-files", "1"]
    ) == 2
    output = capsys.readouterr()

    assert "more than max_files=1" in output.err
    assert "one.json" not in output.err
    assert "two.json" not in output.err
