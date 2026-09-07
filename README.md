# BriefBot

BriefBot is a local-first command-line tool that turns structured project notes
into concise, action-oriented briefs.

The first release focuses on predictable automation:

- validate a strict, versioned JSON input format;
- summarize objectives, context, decisions, risks, and action items;
- classify actions as overdue, due today, upcoming, or unscheduled;
- produce deterministic Markdown or JSON;
- write exports atomically without replacing existing files;
- keep note contents local and require no account, API key, or network access.

BriefBot is being built as part of an eight-week automation project challenge.


## Quick start

```bash
python -m pip install -e .
briefbot validate examples/launch-brief.json
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
Rendered output contains the supplied notes, so review it before sharing.
Exports are atomic and refuse to replace an existing path.

See the [usage guide](docs/usage.md) and
[privacy and safety guide](docs/privacy-and-safety.md) for details.
