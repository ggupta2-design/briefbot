# BriefBot project status

BriefBot 0.7.0 completes the project's seven-milestone development block.

## Delivered capabilities

1. **Deterministic briefs** — validate strict local JSON notes and render stable
   Markdown or JSON action briefs.
2. **Readiness policies** — apply reusable rules and produce value-free finding
   codes with automation-friendly statuses.
3. **Version comparisons** — compare brief revisions through metadata signals
   and aggregate section deltas without exposing note values.
4. **Folder readiness** — audit bounded portfolios with deterministic discovery,
   symlink safeguards, and invalid-file isolation.
5. **Controlled sharing** — remove disallowed sections, owners, and dates before
   rendering share-ready views.
6. **Workload forecasting** — count schedule and assignment workload across one
   brief or a bounded portfolio.
7. **Integrity auditing** — detect normalized duplicates, conflicting metadata,
   and risk/action overlap through read-only aggregate findings.

## Operating boundaries

BriefBot is local-first and uses no accounts, API keys, network services, or
external AI providers. It never sends or publishes project material. Output
files are created atomically and existing files are never overwritten.

Value-free reports omit source text and identifying paths, but aggregate counts
can still be sensitive. Full rendered and controlled-share outputs may contain
source values. Users remain responsible for reviewing outputs, protecting local
files, confirming recipients, and deciding whether findings require changes.

## Supported environment

- Python 3.10 through 3.13
- command-line and importable Python APIs
- deterministic Markdown and JSON reporting
- continuous integration across every supported Python version
