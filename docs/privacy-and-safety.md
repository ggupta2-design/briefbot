# Privacy and safety

BriefBot processes project notes locally. It does not call an AI model, access
the network, send messages, or request credentials. The generated brief may
contain every value supplied in the source file, so both source and output
should be treated according to the sensitivity of the project.

## Safe storage

- Keep real notes outside the repository.
- Use a private directory with restrictive operating-system permissions.
- Do not include passwords, tokens, credentials, or unnecessary personal data.
- Review generated content before sharing it.
- Delete temporary exports when they are no longer needed.

The repository ignores common private input and output locations, but ignore
rules are not a security boundary. Check staged changes before every commit.

## Output safeguards

BriefBot writes a completed temporary file in the destination directory and
then links it into place atomically. If the destination already exists, the
operation fails and preserves the original. It does not provide a force or
overwrite option.

Validation output reports only section counts. Readiness checks add a policy
name, section counts, and aggregate finding codes and counts. They never echo
titles, audiences, objectives, context, decisions, risk descriptions, action
descriptions, or owner names. Policy names appear in reports, so avoid putting
sensitive project information in a policy name.

A readiness policy is configuration, not a security control. It can identify
missing metadata and overdue work, but it cannot determine whether note content
is accurate, complete, appropriate to share, or free of sensitive information.
Warnings require review just like errors, and checks never edit the source.

Folder audits report only aggregate totals. They omit paths and filenames as
well as all brief values. Invalid files are counted but not identified, which
prevents error output from leaking sensitive filenames. Use single-file
validation privately when a folder report shows invalid inputs.

Folder discovery rejects a symbolic-link root, skips linked entries, never
follows directory links, and stops if the explicit file limit is exceeded.
These safeguards reduce accidental traversal, but they do not replace
operating-system permissions or careful directory selection.

Version comparisons return only changed metadata field names and aggregate
added, removed, and unchanged counts. They do not return either version's note
values. BriefBot still reads both complete local files, so operating-system
permissions and safe storage remain important. A changed owner or due date is
represented as one removal and one addition; the report does not identify the
affected action.

Comparison output is a drift signal, not a content review. An unchanged report
does not prove that a brief is accurate, safe to share, or ready for use.

Rendered Markdown and JSON
intentionally contain source material, because their purpose is to produce the
brief. Direct rendered output only to an appropriate private location.

## Disclosure policies

The `share` command creates a separate view and removes excluded sections,
owner names, and due dates before formatting. The policy name and permitted
section list remain in output so reviewers can see which controls were used.
Validate a disclosure policy before opening source notes when possible.

Disclosure controls operate by field, not by content. Text allowed by a policy
may still mention confidential information, credentials, personal data, names,
or dates. A policy cannot understand or sanitize those meanings. Review every
share-ready output before distribution and choose a conservative policy for
external recipients.

BriefBot does not identify or verify recipients, encrypt exports, send
messages, upload files, or revoke shared copies. Keep output in an appropriate
private location until a person approves its destination.

## Automation boundary

Action states are date calculations, not external actions. BriefBot never
assigns work, changes a project system, sends reminders, or publishes a brief.
A person must review the result and decide what to share or do next.
