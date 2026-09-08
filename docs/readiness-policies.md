# Reusable readiness policies

A readiness policy defines the minimum structure and ownership expected before
a project brief is shared. BriefBot evaluates policies locally and returns
aggregate finding codes and counts; it does not include titles, objectives,
notes, action descriptions, owners, or risk descriptions in the report.

## Policy format

Policies are strict JSON objects with schema version 1:

```json
{
  "schema_version": 1,
  "name": "launch-readiness",
  "min_context_items": 2,
  "min_decisions": 1,
  "min_actions": 2,
  "require_action_owners": true,
  "require_action_due_dates": true,
  "require_risk_owners": true,
  "max_overdue_actions": 0
}
```

All fields are required. Minimum and maximum values must be non-negative
integers. Unknown fields and unsupported schema versions are rejected.

Validate a policy before using it:

```bash
briefbot validate-policy examples/readiness-policy.json
briefbot validate-policy examples/readiness-policy.json --json
```

## Check a brief

```bash
briefbot check ~/private/project-notes.json \
  --policy examples/readiness-policy.json \
  --as-of 2026-09-08
```

Use an explicit `--as-of` date for reproducible overdue results. The command
returns exit code 0 when the brief has no findings, 1 when review is required,
and 2 for invalid input, policy, or command data.

Error findings cover missing minimum sections and excessive overdue actions.
Warning findings cover missing action owners, action due dates, and risk
owners. A warning still means review is required: BriefBot does not silently
waive a configured requirement.

Readiness checks are advisory and never edit notes, assign work, send messages,
or publish a brief. A human remains responsible for interpreting each finding
and deciding whether the brief is ready to share.
