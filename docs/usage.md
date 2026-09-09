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
