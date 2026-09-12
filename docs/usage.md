# Using BriefBot

Install BriefBot in a virtual environment:

```bash
python -m pip install -e .
```

Copy the example and keep your real notes in a private location:

```bash
cp examples/launch-brief.json ~/private/project-notes.json
```

## Input format

BriefBot accepts one strict JSON object with schema version 1. Required fields
are:

- `title`, `audience`, and `objective` strings;
- `context` and `decisions` arrays of strings;
- `risks` with `description` and nullable `owner`;
- `actions` with `description`, nullable `owner`, and nullable ISO
  `due_on` date.

Unknown or missing fields, unsupported schema versions, invalid dates, blank
text, and oversized collections are rejected.

## Validate notes

```bash
briefbot validate ~/private/project-notes.json
briefbot validate ~/private/project-notes.json --json
```

Validation reports section counts without echoing note values.

## Check readiness

Validate the example policy, then apply it without printing source values:

```bash
briefbot validate-policy examples/readiness-policy.json
briefbot check ~/private/project-notes.json \
  --policy examples/readiness-policy.json \
  --as-of 2026-09-08
briefbot check ~/private/project-notes.json \
  --policy examples/readiness-policy.json \
  --as-of 2026-09-08 \
  --json
```

Readiness output contains section counts plus aggregate finding codes and
counts. Exit status 0 means ready, 1 means review required, and 2 means invalid
input or policy. See [readiness-policies.md](readiness-policies.md) for the
strict policy schema and finding behavior.

## Audit a folder

```bash
briefbot check-folder ~/private/briefs \
  --policy examples/readiness-policy.json \
  --as-of 2026-09-10
briefbot check-folder ~/private/briefs \
  --recursive \
  --max-files 50 \
  --as-of 2026-09-10 \
  --json \
  --output ~/private/reports/readiness.json
```

Folder audits isolate invalid inputs and report aggregate ready,
review-required, invalid, and finding counts without printing paths or note
values. Exit status 0 means all discovered briefs are valid and ready, 1 means
review is required, and 2 means invalid configuration. See
[folder-readiness.md](folder-readiness.md) for discovery and privacy rules.

## Compare two versions

```bash
briefbot diff ~/private/brief-v1.json ~/private/brief-v2.json
briefbot diff ~/private/brief-v1.json ~/private/brief-v2.json --json
briefbot diff ~/private/brief-v1.json ~/private/brief-v2.json \
  --json \
  --output ~/private/reports/changes.json
```

Comparison output contains changed metadata field names and aggregate section
counts, not note values. Exit status 0 means identical, 1 means changes were
detected, and 2 means invalid input or output. Exports are atomic and refuse
to overwrite. See [comparing-briefs.md](comparing-briefs.md) for exact
comparison semantics.

## Render a brief

```bash
briefbot render ~/private/project-notes.json --as-of 2026-09-07
briefbot render ~/private/project-notes.json --as-of 2026-09-07 --json
```

The explicit review date makes overdue and due-today classification
reproducible. Actions are ordered as overdue, due today, upcoming, and
unscheduled. Ties use due date, owner, and description for stable output.

## Create a controlled share view

Validate the disclosure policy without reading source notes:

```bash
briefbot validate-disclosure-policy examples/disclosure-policy.json
```

Then create a view containing only permitted fields:

```bash
briefbot share ~/private/project-notes.json \
  --policy examples/disclosure-policy.json \
  --as-of 2026-09-11
briefbot share ~/private/project-notes.json \
  --policy examples/disclosure-policy.json \
  --as-of 2026-09-11 \
  --json \
  --output ~/private/shared/project-update.json
```

Disabled sections are omitted entirely. Owner names and due dates are removed
before formatting when disallowed. See
[controlled-sharing.md](controlled-sharing.md) for the strict policy schema
and important review boundary.

## Forecast action workload

Generate a value-free forecast for one brief:

```bash
briefbot workload ~/private/project-notes.json \
  --as-of 2026-09-12 \
  --window-days 14 \
  --json
```

Aggregate a bounded portfolio without exposing brief names or action values:

```bash
briefbot workload-folder ~/private/briefs \
  --as-of 2026-09-12 \
  --window-days 14 \
  --recursive \
  --max-files 100 \
  --fail-on-overdue \
  --json \
  --output ~/private/reports/workload.json
```

Forecasts separate overdue, due-today, near-term, later, and unscheduled work,
plus assigned and unassigned totals. Folder forecasts isolate malformed files
and return status 1 for invalid inputs; `--fail-on-overdue` also returns status
1 when overdue actions exist. Reports contain counts only. See
[workload-forecasting.md](workload-forecasting.md) for exact semantics and
privacy boundaries.

## Export safely

```bash
briefbot render ~/private/project-notes.json \
  --as-of 2026-09-07 \
  --output ~/private/briefs/launch.md
```

Exports are atomic and never overwrite an existing path. Choose `--json`
before `--output` to export JSON. BriefBot prints only the destination file
name after a successful write.

Read [privacy-and-safety.md](privacy-and-safety.md) before processing real
project material.
