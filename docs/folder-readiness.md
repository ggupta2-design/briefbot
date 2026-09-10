# Folder-level readiness audits

BriefBot can audit a directory of JSON briefs in one bounded, read-only pass.
It validates each discovered file, applies the same readiness policy to every
valid brief, and reports only portfolio-level counts.

## Run an audit

```bash
briefbot check-folder ~/private/briefs \
  --policy examples/readiness-policy.json \
  --as-of 2026-09-10

briefbot check-folder ~/private/briefs \
  --policy examples/readiness-policy.json \
  --as-of 2026-09-10 \
  --recursive \
  --max-files 50 \
  --json
```

Discovery is shallow unless `--recursive` is supplied. Only regular files
with a case-insensitive `.json` suffix are considered. Results are ordered
deterministically. Symbolic-link roots are rejected, linked files and
directories are skipped, and directory links are never followed.

The default limit is 100 files. `--max-files` accepts values from 1 through
1000. If discovery exceeds the limit, BriefBot stops before loading brief
content and returns an error rather than silently auditing a partial folder.

## Results and privacy

Malformed or schema-invalid briefs are counted as invalid without stopping
other files. Valid briefs are counted as ready or review required. Readiness
findings are aggregated by stable code, total occurrences, and number of
affected briefs.

Reports do not contain paths, filenames, titles, audiences, objectives, note
text, action or risk descriptions, owners, or due dates. Because invalid files
are not named, investigate them separately with `briefbot validate` in an
appropriate private environment.

Exit status 0 means at least one brief was discovered and every brief was valid
and ready. Status 1 means the folder was empty, contained invalid briefs, or
had readiness findings. Status 2 means the folder, policy, limit, output, or
command input was invalid.

## Export safely

```bash
briefbot check-folder ~/private/briefs \
  --as-of 2026-09-10 \
  --json \
  --output ~/private/reports/readiness.json
```

Exports are atomic and never replace an existing file. Folder audits never
modify source briefs, assign work, send notifications, or publish reports.
