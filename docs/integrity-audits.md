# Read-only brief integrity audits

BriefBot integrity audits detect structural duplication and inconsistent records
without modifying source notes or printing their values.

## Findings

The audit emits stable codes:

- `duplicate_context`, `duplicate_decision`, `duplicate_risk`, and
  `duplicate_action` are warnings for repeated normalized records;
- `action_owner_conflict` and `action_due_date_conflict` are errors when
  the same normalized action description has inconsistent metadata;
- `risk_owner_conflict` is an error when the same normalized risk has
  inconsistent owners;
- `risk_action_overlap` is a warning when a normalized description appears
  in both risks and actions.

Matching is case-insensitive and treats repeated whitespace as equivalent.
Duplicate counts represent copies beyond the first record. Conflict counts
represent normalized descriptions with more than one distinct value. The audit
does not decide which record is correct.

## Audit one brief

```bash
briefbot audit-integrity ~/private/project.json \
  --as-of 2026-09-13 \
  --json
```

Exit status 0 means no findings, 1 means review is required, and 2 means the
input, arguments, or output request is invalid.

## Audit a portfolio

```bash
briefbot audit-integrity-folder ~/private/briefs \
  --as-of 2026-09-13 \
  --recursive \
  --max-files 100 \
  --json \
  --output ~/private/reports/integrity.json
```

Folder audits use deterministic bounded discovery, reject symbolic-link roots,
skip linked entries, and isolate malformed briefs. Reports contain discovered,
valid, invalid, clean, and affected brief counts plus aggregate finding codes,
severities, occurrences, and affected-brief counts.

## Safety and interpretation

Audits are read-only and exports never overwrite existing files. Reports omit
titles, audiences, objectives, note text, descriptions, owner names, dates,
filenames, paths, and per-brief results.

A finding is a review signal, not proof of an error. Repeated text may be
intentional, and similar wording is not semantic equivalence. BriefBot does not
repair, merge, delete, upload, or share briefs. Review the private source and
decide what to change.
