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
