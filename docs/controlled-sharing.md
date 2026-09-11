# Controlled brief sharing

BriefBot normally renders every supplied value. The `share` workflow instead
requires a strict disclosure policy and builds a new in-memory view containing
only the sections and metadata that policy permits.

## Validate a policy

```bash
briefbot validate-disclosure-policy examples/disclosure-policy.json
briefbot validate-disclosure-policy examples/disclosure-policy.json --json
```

Validation reads only the policy. It does not open a brief. Disclosure policies
use schema version 1 and require every supported field:

- `name`;
- section controls for objective, context, decisions, risks, and actions;
- metadata controls for owner names and due dates.

Unknown, missing, non-Boolean, and unsupported-version values are rejected.

## Create a share-ready view

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

The output always includes the title, audience, review date, policy name, and
an `included_sections` record. Optional sections are omitted entirely when
disabled. Owner names and due dates are removed from the in-memory view before
formatting when their controls are disabled.

Actions retain BriefBot's deterministic priority ordering. If due dates are
excluded, schedule-state labels are also omitted so they cannot reveal hidden
timing.

## Safety boundary

A disclosure policy controls fields, not meaning. Included free text can still
contain confidential, personal, or credential-like information. Always inspect
the final output before sending or publishing it.

Exports are atomic and refuse to overwrite an existing path. BriefBot does not
send messages, upload files, publish briefs, or grant access to recipients.
