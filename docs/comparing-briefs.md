# Comparing brief versions

BriefBot can compare two validated brief inputs without displaying their note
values. This is useful in local review workflows and CI checks where the
question is whether a brief changed, not what its confidential content says.

## Run a comparison

```bash
briefbot diff ~/private/brief-v1.json ~/private/brief-v2.json
briefbot diff ~/private/brief-v1.json ~/private/brief-v2.json --json
```

The report identifies whether `title`, `audience`, or `objective` changed
by field name only. For context, decisions, risks, and actions it reports
added, removed, and unchanged counts.

Collections are compared as multisets. Repeated items are counted separately,
and reordering alone is not considered a change. Changing a risk owner, action
owner, or action due date counts as removing the previous item and adding the
current item.

## Exit statuses

- 0: the validated versions are identical;
- 1: one or more changes were detected;
- 2: an input, output path, or command value is invalid.

These statuses let automation detect drift without parsing output.

## Export safely

```bash
briefbot diff ~/private/brief-v1.json ~/private/brief-v2.json \
  --json \
  --output ~/private/reports/brief-changes.json
```

Exports use the same atomic, non-overwriting safeguard as rendered briefs.
BriefBot refuses to replace an existing report.

Comparison reports contain aggregate counts and metadata field names only.
They do not include titles, audiences, objectives, note text, descriptions,
owners, or due dates. The tool reads both inputs locally, performs no external
actions, and never modifies either source file.
