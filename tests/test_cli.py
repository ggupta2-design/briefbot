import json

from briefbot.cli import run


def write_source(tmp_path):
    path = tmp_path / "notes.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "title": "Private launch",
                "audience": "Core team",
                "objective": "Agree on launch readiness",
                "context": ["Pilot feedback reviewed"],
                "decisions": ["Keep access limited"],
                "risks": [{"description": "Timeline", "owner": None}],
                "actions": [
                    {
                        "description": "Finish review",
                        "owner": "Garima",
                        "due_on": "2026-09-06",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    return path


def test_validate_command_reports_counts_without_note_values(tmp_path, capsys):
    source = write_source(tmp_path)

    assert run(["validate", str(source), "--json"]) == 0
    output = capsys.readouterr().out
    payload = json.loads(output)

    assert payload == {
        "actions": 1,
        "context_items": 1,
        "decisions": 1,
        "risks": 1,
        "valid": True,
    }
    assert "Private launch" not in output
    assert "Garima" not in output


def test_render_command_outputs_reproducible_json(tmp_path, capsys):
    source = write_source(tmp_path)

    assert run(
        ["render", str(source), "--as-of", "2026-09-07", "--json"]
    ) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["title"] == "Private launch"
    assert payload["actions"][0]["state"] == "overdue"
    assert payload["actions"][0]["days_until"] == -1


def test_render_command_writes_new_output(tmp_path, capsys):
    source = write_source(tmp_path)
    output = tmp_path / "exports" / "brief.md"

    assert run(
        [
            "render",
            str(source),
            "--as-of",
            "2026-09-07",
            "--output",
            str(output),
        ]
    ) == 0

    assert capsys.readouterr().out == "Wrote brief.md\n"
    assert output.read_text(encoding="utf-8").startswith("# Private launch")


def test_render_command_preserves_existing_output(tmp_path, capsys):
    source = write_source(tmp_path)
    output = tmp_path / "brief.md"
    output.write_text("keep me", encoding="utf-8")

    assert run(["render", str(source), "--output", str(output)]) == 2

    assert "already exists" in capsys.readouterr().err
    assert output.read_text(encoding="utf-8") == "keep me"


def test_cli_reports_invalid_source_without_traceback(tmp_path, capsys):
    source = tmp_path / "bad.json"
    source.write_text("not json", encoding="utf-8")

    assert run(["validate", str(source)]) == 2
    assert "not valid JSON" in capsys.readouterr().err


def test_check_command_reports_review_status_without_note_values(
    tmp_path, capsys
):
    source = write_source(tmp_path)

    assert run(
        ["check", str(source), "--as-of", "2026-09-08", "--json"]
    ) == 1
    output = capsys.readouterr().out
    payload = json.loads(output)

    assert payload["ready"] is False
    assert payload["error_count"] == 1
    assert payload["warning_count"] == 1
    assert "Private launch" not in output
    assert "Garima" not in output


def test_check_command_applies_reusable_policy(tmp_path, capsys):
    source = write_source(tmp_path)
    policy = tmp_path / "policy.json"
    policy.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "name": "launch-ready",
                "min_context_items": 1,
                "min_decisions": 1,
                "min_actions": 1,
                "require_action_owners": True,
                "require_action_due_dates": True,
                "require_risk_owners": False,
                "max_overdue_actions": 1,
            }
        ),
        encoding="utf-8",
    )

    assert run(
        [
            "check",
            str(source),
            "--as-of",
            "2026-09-08",
            "--policy",
            str(policy),
            "--json",
        ]
    ) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["ready"] is True
    assert payload["policy"] == "launch-ready"
    assert payload["findings"] == []


def test_validate_policy_command_reports_rules(tmp_path, capsys):
    policy = tmp_path / "policy.json"
    policy.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "name": "review-standard",
                "min_context_items": 2,
                "min_decisions": 1,
                "min_actions": 1,
                "require_action_owners": True,
                "require_action_due_dates": True,
                "require_risk_owners": False,
                "max_overdue_actions": 0,
            }
        ),
        encoding="utf-8",
    )

    assert run(["validate-policy", str(policy), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["valid"] is True
    assert payload["name"] == "review-standard"
    assert payload["thresholds"]["min_context_items"] == 2


def test_validate_policy_command_rejects_unknown_fields(tmp_path, capsys):
    policy = tmp_path / "bad-policy.json"
    policy.write_text(
        json.dumps({"schema_version": 1, "name": "bad", "secret": "value"}),
        encoding="utf-8",
    )

    assert run(["validate-policy", str(policy)]) == 2
    output = capsys.readouterr()

    assert "must contain exactly the supported fields" in output.err
    assert "value" not in output.err


def test_diff_command_reports_changes_without_note_values(tmp_path, capsys):
    previous = write_source(tmp_path)
    current = tmp_path / "current.json"
    payload = json.loads(previous.read_text(encoding="utf-8"))
    payload["title"] = "Highly confidential rename"
    payload["context"].append("Private customer signal")
    current.write_text(json.dumps(payload), encoding="utf-8")

    assert run(["diff", str(previous), str(current), "--json"]) == 1
    output = capsys.readouterr().out
    report = json.loads(output)

    assert report["changed"] is True
    assert report["metadata_changed"] == ["title"]
    assert report["sections"]["context"]["added"] == 1
    assert "Private launch" not in output
    assert "Highly confidential rename" not in output
    assert "Private customer signal" not in output


def test_diff_command_returns_success_for_identical_versions(tmp_path, capsys):
    source = write_source(tmp_path)

    assert run(["diff", str(source), str(source), "--json"]) == 0
    report = json.loads(capsys.readouterr().out)

    assert report["changed"] is False
    assert report["total_changes"] == 0


def test_diff_command_rejects_invalid_current_version(tmp_path, capsys):
    previous = write_source(tmp_path)
    current = tmp_path / "current.json"
    current.write_text("not json", encoding="utf-8")

    assert run(["diff", str(previous), str(current)]) == 2
    assert "not valid JSON" in capsys.readouterr().err


def test_diff_command_exports_without_overwriting(tmp_path, capsys):
    source = write_source(tmp_path)
    output = tmp_path / "reports" / "changes.json"

    assert run(
        [
            "diff",
            str(source),
            str(source),
            "--json",
            "--output",
            str(output),
        ]
    ) == 0
    assert capsys.readouterr().out == "Wrote changes.json\n"
    assert json.loads(output.read_text(encoding="utf-8"))["changed"] is False

    assert run(
        [
            "diff",
            str(source),
            str(source),
            "--json",
            "--output",
            str(output),
        ]
    ) == 2
    assert "already exists" in capsys.readouterr().err


def test_check_folder_reports_aggregate_results(tmp_path, capsys):
    folder = tmp_path / "briefs"
    folder.mkdir()
    write_source(folder)
    (folder / "invalid.json").write_text("not json", encoding="utf-8")

    assert run(
        ["check-folder", str(folder), "--as-of", "2026-09-10", "--json"]
    ) == 1
    output = capsys.readouterr().out
    payload = json.loads(output)

    assert payload["summary"] == {
        "discovered": 2,
        "invalid": 1,
        "ready": 0,
        "review_required": 1,
        "valid": 1,
    }
    assert "notes.json" not in output
    assert "Private launch" not in output
    assert "Garima" not in output


def test_check_folder_applies_policy_and_returns_success(tmp_path, capsys):
    folder = tmp_path / "briefs"
    folder.mkdir()
    write_source(folder)
    policy = tmp_path / "policy.json"
    policy.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "name": "portfolio-standard",
                "min_context_items": 1,
                "min_decisions": 1,
                "min_actions": 1,
                "require_action_owners": True,
                "require_action_due_dates": True,
                "require_risk_owners": False,
                "max_overdue_actions": 1,
            }
        ),
        encoding="utf-8",
    )

    assert run(
        [
            "check-folder",
            str(folder),
            "--as-of",
            "2026-09-10",
            "--policy",
            str(policy),
            "--json",
        ]
    ) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["all_ready"] is True
    assert payload["policy"] == "portfolio-standard"


def test_check_folder_supports_recursive_discovery(tmp_path, capsys):
    folder = tmp_path / "briefs"
    nested = folder / "nested"
    nested.mkdir(parents=True)
    write_source(nested)

    assert run(
        [
            "check-folder",
            str(folder),
            "--recursive",
            "--as-of",
            "2026-09-10",
            "--json",
        ]
    ) == 1
    payload = json.loads(capsys.readouterr().out)

    assert payload["summary"]["discovered"] == 1
    assert payload["summary"]["valid"] == 1


def test_check_folder_enforces_file_limit(tmp_path, capsys):
    folder = tmp_path / "briefs"
    folder.mkdir()
    write_source(folder)
    second = folder / "second.json"
    second.write_text(
        (folder / "notes.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    assert run(
        ["check-folder", str(folder), "--max-files", "1"]
    ) == 2
    error = capsys.readouterr().err

    assert "more than max_files=1" in error
    assert "notes.json" not in error
    assert "second.json" not in error


def test_check_folder_exports_report_without_overwriting(tmp_path, capsys):
    folder = tmp_path / "briefs"
    folder.mkdir()
    write_source(folder)
    output = tmp_path / "reports" / "portfolio.json"
    command = [
        "check-folder",
        str(folder),
        "--as-of",
        "2026-09-10",
        "--json",
        "--output",
        str(output),
    ]

    assert run(command) == 1
    assert capsys.readouterr().out == "Wrote portfolio.json\n"
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["summary"]["discovered"] == 1

    assert run(command) == 2
    assert "already exists" in capsys.readouterr().err


def write_disclosure_policy(tmp_path, **changes):
    payload = {
        "schema_version": 1,
        "name": "external",
        "include_objective": True,
        "include_context": False,
        "include_decisions": True,
        "include_risks": False,
        "include_actions": True,
        "include_owner_names": False,
        "include_due_dates": True,
    }
    payload.update(changes)
    path = tmp_path / "disclosure-policy.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_share_command_applies_disclosure_policy(tmp_path, capsys):
    source = write_source(tmp_path)
    policy = write_disclosure_policy(tmp_path)

    assert run(
        [
            "share",
            str(source),
            "--policy",
            str(policy),
            "--as-of",
            "2026-09-11",
            "--json",
        ]
    ) == 0
    output = capsys.readouterr().out
    payload = json.loads(output)

    assert payload["policy"] == "external"
    assert "context" not in payload
    assert "risks" not in payload
    assert payload["actions"][0]["owner"] is None
    assert "Pilot feedback reviewed" not in output
    assert "Timeline" not in output
    assert "Garima" not in output


def test_share_command_rejects_invalid_policy(tmp_path, capsys):
    source = write_source(tmp_path)
    policy = tmp_path / "bad-policy.json"
    policy.write_text("not json", encoding="utf-8")

    assert run(["share", str(source), "--policy", str(policy)]) == 2
    assert "disclosure policy is not valid JSON" in capsys.readouterr().err


def test_share_command_exports_without_overwriting(tmp_path, capsys):
    source = write_source(tmp_path)
    policy = write_disclosure_policy(tmp_path)
    output = tmp_path / "shared" / "brief.json"
    command = [
        "share",
        str(source),
        "--policy",
        str(policy),
        "--as-of",
        "2026-09-11",
        "--json",
        "--output",
        str(output),
    ]

    assert run(command) == 0
    assert capsys.readouterr().out == "Wrote brief.json\n"
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert "context" not in payload

    assert run(command) == 2
    assert "already exists" in capsys.readouterr().err


def test_validate_disclosure_policy_command(tmp_path, capsys):
    policy = write_disclosure_policy(tmp_path)

    assert run(
        ["validate-disclosure-policy", str(policy), "--json"]
    ) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["valid"] is True
    assert payload["name"] == "external"
    assert payload["sections"]["context"] is False
    assert payload["metadata"]["owner_names"] is False
