import json

from briefbot.cli import run


def write_brief(path):
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "title": "Confidential",
                "audience": "Internal",
                "objective": "Private",
                "context": [],
                "decisions": [],
                "risks": [],
                "actions": [],
            }
        ),
        encoding="utf-8",
    )


def test_workload_export_is_atomic_and_non_overwriting(tmp_path, capsys):
    source = tmp_path / "source.json"
    output = tmp_path / "reports" / "workload.json"
    write_brief(source)
    command = [
        "workload",
        str(source),
        "--as-of",
        "2026-09-12",
        "--json",
        "--output",
        str(output),
    ]

    assert run(command) == 0
    assert capsys.readouterr().out == "Wrote workload.json\n"
    assert json.loads(output.read_text(encoding="utf-8"))["actions"]["total"] == 0

    assert run(command) == 2
    assert "already exists" in capsys.readouterr().err


def test_portfolio_workload_export_preserves_existing_file(tmp_path, capsys):
    briefs = tmp_path / "briefs"
    briefs.mkdir()
    write_brief(briefs / "source.json")
    output = tmp_path / "portfolio.json"
    output.write_text("preserve", encoding="utf-8")

    assert run(
        [
            "workload-folder",
            str(briefs),
            "--json",
            "--output",
            str(output),
        ]
    ) == 2

    assert "already exists" in capsys.readouterr().err
    assert output.read_text(encoding="utf-8") == "preserve"
