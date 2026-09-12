# Privacy-safe workload forecasting

BriefBot can forecast action workload for one brief or a bounded folder without
printing project titles, audiences, objectives, descriptions, owner names,
filenames, or directory paths.

## What the forecast counts

Every valid action belongs to exactly one schedule bucket:

- **overdue** — due before the explicit review date;
- **due today** — due on the review date;
- **due within window** — due after the review date and within the selected
  forecast horizon;
- **due later** — dated beyond that horizon;
- **unscheduled** — no due date is recorded.

The same actions are also counted as assigned or unassigned. These two
assignment totals always add up to the total action count.

## Forecast one brief

```bash
briefbot workload ~/private/project.json \
  --as-of 2026-09-12 \
  --window-days 14
```

Use `--json` for a stable machine-readable payload. Use `--output PATH` to
write a new report atomically; BriefBot refuses to replace an existing file.

## Forecast a folder

```bash
briefbot workload-folder ~/private/briefs \
  --as-of 2026-09-12 \
  --window-days 14 \
  --recursive \
  --max-files 100 \
  --json
```

Folder forecasts reuse BriefBot's safe discovery rules. Symbolic-link roots are
rejected, linked entries are skipped, traversal is deterministic, and the
explicit file limit is enforced. Malformed briefs are isolated and counted as
invalid; no filename or validation detail is exposed.

The folder command exits with status 1 when invalid inputs are present.
Otherwise it exits with status 0. Add `--fail-on-overdue` to either workload
command when an automation should also receive status 1 for overdue actions.
Invalid arguments or unsafe output requests use status 2.

## Privacy boundary

Forecasts are count-only summaries, but counts can still reveal operational
information. Store reports appropriately and share them only with intended
recipients. BriefBot does not send, upload, publish, encrypt, authenticate
recipients, or decide whether a report is safe to disclose. A human remains
responsible for reviewing each exported report.
