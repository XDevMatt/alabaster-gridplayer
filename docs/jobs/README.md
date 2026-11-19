# Job packages

Self-contained write-ups for other assistants. Paste one file as the
brief. Grok Build may also be given the repo. SuperGrok, Gemini, and
Claude are for review. Do not use Jules or Antigravity.

See [ROADMAP-next.md](../ROADMAP-next.md) for priority and sizes.

| Job | Resource |
| --- | --- |
| [job-sync-settings-popup.md](job-sync-settings-popup.md) | Grok Build |
| [job-end-of-track-blip.md](job-end-of-track-blip.md) | Grok Build |
| [job-windows-portable-upgrade.md](job-windows-portable-upgrade.md) | Grok Build |
| [job-subtitle-style-reload.md](job-subtitle-style-reload.md) | Grok Build |
| [job-opt-in-subtitle-repair.md](job-opt-in-subtitle-repair.md) | Grok Build |
| [job-keep-options-ui.md](job-keep-options-ui.md) | Grok Build |
| [job-local-file-details-cache.md](job-local-file-details-cache.md) | Grok Build |
| [job-default-view-fit.md](job-default-view-fit.md) | Grok Build |
| [job-review-pr2.md](job-review-pr2.md) | SuperGrok; Gemini or Claude with the diff pasted |

Grok Build jobs work in numbered steps with a commit and a progress
note (`docs/progress/<job-name>.md`) at each checkpoint, so a context
reset can resume from the note and `git log`. No behaviour changes
outside a step's scope; each behaviour-changing step carries a
before/after regression test. The end-of-track blip is a regression:
bisect it first.
