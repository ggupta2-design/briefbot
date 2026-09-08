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

Rendered Markdown and JSON
intentionally contain source material, because their purpose is to produce the
brief. Direct rendered output only to an appropriate private location.

## Automation boundary

Action states are date calculations, not external actions. BriefBot never
assigns work, changes a project system, sends reminders, or publishes a brief.
A person must review the result and decide what to share or do next.
