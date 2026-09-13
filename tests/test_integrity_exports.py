import json

from briefbot.cli import run


def write_clean_brief(path):
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "title": "Private",
                "audience": "Internal",
                "objective": "Confidential",
                "context": [],
                "decisions": [],
                "risks": [],
                "actions": [],
            }
        ),
        encoding="utf-8",
    )


def test_integrity_export_is_atomic_and_non_overwriting(tmp_path, capsys):
    source = tmp_path / "source.json"
    output = tmp_path / "reports" / "integrity.json"
    write_clean_brief(source)
    command = [
        "audit-integrity",
        str(source),
        "--as-of",
        "2026-09-13",
        "--json",
        "--output",
        str(output),
    ]

    assert run(command) == 0
    assert capsys.readouterr().out == "Wrote integrity.json\n"
    assert json.loads(output.read_text(encoding="utf-8"))["clean"] is True

    assert run(command) == 2
    assert "already exists" in capsys.readouterr().err


def test_folder_integrity_export_preserves_existing_file(tmp_path, capsys):
    briefs = tmp_path / "briefs"
    briefs.mkdir()
    write_clean_brief(briefs / "source.json")
    output = tmp_path / "integrity.json"
    output.write_text("preserve", encoding="utf-8")

    assert run(
        [
            "audit-integrity-folder",
            str(briefs),
            "--json",
            "--output",
            str(output),
        ]
    ) == 2

    assert "already exists" in capsys.readouterr().err
    assert output.read_text(encoding="utf-8") == "preserve"
