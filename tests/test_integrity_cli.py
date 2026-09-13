import json

from briefbot.cli import run


def write_brief(path, context):
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "title": "Secret initiative",
                "audience": "Private group",
                "objective": "Confidential objective",
                "context": context,
                "decisions": [],
                "risks": [],
                "actions": [],
            }
        ),
        encoding="utf-8",
    )


def test_audit_integrity_reports_findings_without_values(tmp_path, capsys):
    source = tmp_path / "private.json"
    write_brief(source, ["Secret signal", " secret   signal "])

    assert run(
        ["audit-integrity", str(source), "--as-of", "2026-09-13", "--json"]
    ) == 1
    output = capsys.readouterr().out
    payload = json.loads(output)

    assert payload["clean"] is False
    assert payload["findings"][0]["code"] == "duplicate_context"
    assert "Secret initiative" not in output
    assert "Secret signal" not in output
    assert "private.json" not in output


def test_audit_integrity_returns_success_for_clean_brief(tmp_path, capsys):
    source = tmp_path / "private.json"
    write_brief(source, ["Unique"])

    assert run(
        ["audit-integrity", str(source), "--as-of", "2026-09-13", "--json"]
    ) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["clean"] is True
    assert payload["findings"] == []


def test_audit_integrity_rejects_invalid_source_safely(tmp_path, capsys):
    source = tmp_path / "invalid.json"
    source.write_text("not json", encoding="utf-8")

    assert run(["audit-integrity", str(source)]) == 2
    output = capsys.readouterr()

    assert "not valid JSON" in output.err
    assert "not json" not in output.err
