# BriefBot

BriefBot is a local-first command-line tool that turns structured project notes
into concise, action-oriented briefs.

BriefBot focuses on predictable, privacy-aware automation:

- validate a strict, versioned JSON input format;
- summarize objectives, context, decisions, risks, and action items;
- classify actions as overdue, due today, upcoming, or unscheduled;
- produce deterministic Markdown or JSON;
- check brief readiness against strict reusable policies;
- report only aggregate readiness counts and finding codes;
- compare brief versions through value-free change summaries;
- write exports atomically without replacing existing files;
- keep note contents local and require no account, API key, or network access.

BriefBot is being built as part of an eight-week automation project challenge.


## Quick start

```bash
python -m pip install -e .
briefbot validate examples/launch-brief.json
briefbot validate-policy examples/readiness-policy.json
briefbot check examples/launch-brief.json \
  --policy examples/readiness-policy.json \
  --as-of 2026-09-08
briefbot diff ~/private/brief-v1.json ~/private/brief-v2.json --json
briefbot render examples/launch-brief.json --as-of 2026-09-07
briefbot render examples/launch-brief.json \
  --as-of 2026-09-07 \
  --json \
  --output briefbot-output.json
```

BriefBot requires every input section explicitly, rejects unknown fields, and
limits each collection to 100 items. Dated actions are sorted into overdue,
due-today, and upcoming groups; undated work remains visible as unscheduled.

The `validate` command reports counts without echoing project content.
The `check` command applies default or reusable readiness rules for minimum
sections, ownership, due dates, and overdue work. Its reports contain counts
and stable finding codes rather than note values, and its exit status
distinguishes ready, review-required, and invalid inputs.
The `diff` command reports changed metadata field names and aggregate section
counts without exposing either version's note values. It preserves duplicate
items and ignores reordering.

Rendered output contains the supplied notes, so review it before sharing.
Exports are atomic and refuse to replace an existing path.

See the [usage guide](docs/usage.md),
[brief comparison guide](docs/comparing-briefs.md), and
[readiness policy guide](docs/readiness-policies.md), and
[privacy and safety guide](docs/privacy-and-safety.md) for details.
