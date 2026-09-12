import json

from briefbot.cli import run


def write_brief(path, *, description="Sensitive task", owner="Private owner"):
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "title": "Secret project",
                "audience": "Private team",
                "objective": "Confidential objective",
                "context": ["Sensitive context"],
                "decisions": ["Sensitive decision"],
                "risks": [{"description": "Sensitive risk", "owner": owner}],
                "actions": [
                    {
                        "description": description,
                        "owner": owner,
                        "due_on": "2026-09-14",
                    },
                    {
                        "description": "Undated secret",
                        "owner": None,
                        "due_on": None,
                    },
                ],
            }
        ),
        encoding="utf-8",
    )


def test_workload_command_reports_counts_without_values(tmp_path, capsys):
    source = tmp_path / "private.json"
    write_brief(source)

    assert run(
        [
            "workload",
            str(source),
            "--as-of",
            "2026-09-12",
            "--window-days",
            "3",
            "--json",
        ]
    ) == 0
    output = capsys.readouterr().out
    payload = json.loads(output)

    assert payload["actions"]["due_within_window"] == 1
    assert payload["actions"]["unscheduled"] == 1
    assert payload["actions"]["assigned"] == 1
    assert "Secret project" not in output
    assert "Sensitive task" not in output
    assert "Private owner" not in output
    assert "private.json" not in output


def test_workload_command_rejects_invalid_window(tmp_path, capsys):
    source = tmp_path / "private.json"
    write_brief(source)

    assert run(["workload", str(source), "--window-days", "0"]) == 2
    output = capsys.readouterr()

    assert "window_days" in output.err
    assert "Secret project" not in output.err


def test_workload_can_signal_overdue_actions(tmp_path, capsys):
    source = tmp_path / "private.json"
    write_brief(source)

    assert run(
        [
            "workload",
            str(source),
            "--as-of",
            "2026-09-15",
            "--fail-on-overdue",
            "--json",
        ]
    ) == 1
    payload = json.loads(capsys.readouterr().out)

    assert payload["actions"]["overdue"] == 1
    assert "Sensitive task" not in json.dumps(payload)
