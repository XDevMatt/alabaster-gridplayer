# Next work

A short plan for GridPlayer Alabaster after `main` and draft PR #2
(`fix/subtitle-encoding-rc2`). Nothing here is a promise of a date. Do not
merge, tag, or release until the maintainer asks. Windows only: no macOS,
Linux, or translation work.

Longer-horizon ideas stay in [roadmap.md](roadmap.md) and
[FUTURE.md](FUTURE.md). Job write-ups that can be pasted into another
assistant live in [jobs/](jobs/).

## In flight

Draft [PR #2](https://github.com/XDevMatt/alabaster-gridplayer/pull/2)
on `fix/subtitle-encoding-rc2`: attached subtitles render, a Settings
encoding change no longer greys cells that have no subtitles, SubtitleCat
stray-byte repair, and docs that used to point at the retired
`0.2beta-fixes` branch now point at `main`. A subtitle *style* change still
reloads every cell. Non-SubtitleCat `.srt` files are not repaired yet.

## Priority

Sizes: **S** a few hours, **M** a day or two, **L** a multi-day slice.

| # | Item | Size | Job | Who |
| --- | --- | --- | --- | --- |
| 1 | Sync settings popup (staged Apply / Cancel, per-cell Loop) | M | [job-sync-settings-popup.md](jobs/job-sync-settings-popup.md) | Grok Build |
| 2 | End-of-track blip on Next / Shuffle / other non-Loop actions | M | [job-end-of-track-blip.md](jobs/job-end-of-track-blip.md) | Grok Build |
| 3 | Portable zip upgrade (in-app button, preview list, Recycle Bin, rollback) | M | [job-windows-portable-upgrade.md](jobs/job-windows-portable-upgrade.md) | Grok Build |
| 4 | Settings: subtitle style change greys every cell | M | [job-subtitle-style-reload.md](jobs/job-subtitle-style-reload.md) | Grok Build |
| 5 | Opt-in stray-byte repair for any text subtitle, not only SubtitleCat | S–M | [job-opt-in-subtitle-repair.md](jobs/job-opt-in-subtitle-repair.md) | Grok Build |

Also queued, not in the top five:

| Item | Size | Job | Who |
| --- | --- | --- | --- |
| Keep options UI (enable, copy / move) | M | [job-keep-options-ui.md](jobs/job-keep-options-ui.md) | Grok Build |
| Local-file details cache (~3,466-file music tree) | L | [job-local-file-details-cache.md](jobs/job-local-file-details-cache.md) | Grok Build |
| Review PR #2 (encoding, attach, docs) | S | [job-review-pr2.md](jobs/job-review-pr2.md) | SuperGrok, or Gemini / Claude with the diff pasted |

## Resource fit

- **Grok Build:** multi-file coding jobs (1–7 above). Give it the job file
  and the repo. Do not use Jules or Antigravity.
- **SuperGrok:** code review of one diff or file. Best first reader for
  PR #2, or of a Grok Build patch before it is pushed.
- **Gemini (lowest paid tier, chat only) and free Claude (chat only, no
  GitHub, small context):** review only. Paste a single file or a short
  diff after the job brief. Do not ask them to edit the repo.

## Constraints for every job

- Identity is XDevMatt only. Never write the maintainer's personal name,
  handles, or personal email in a file, commit, PR, or doc; write
  `<user>` if a placeholder is required.
- No merge, tag, or release.
- Never call a preview a "dry run"; say **preview list**.
- Windows-only app. Leave macOS / Linux / i18n alone.

## Decided

- Grid > Sync opens the staged Sync settings panel (it replaces the
  live Grid > Sync submenu toggles). **Apply** commits every staged
  change and closes the panel. **Cancel** discards the draft and
  closes.
- Unchecking Loop on a cell that was set to Loop from the When Finished
  menu (no `end_action_before_loop`): play a random file from the same
  folder as the current file, start it from the beginning (position 0),
  and mute it (`SHUFFLE_FILE`).
- Keep: the default action is Copy, not Move.
- Local-file details cache stores, per file: name, length (duration),
  codec, and a thumbnail.
- Portable upgrade tool: an in-app button (for example Help or Settings
  "Upgrade from portable zip..."), not a standalone script. The user
  picks the new zip; the app does not download it. A helper process
  finishes the swap after the app exits.
- Bug fixes for subtitle style greying every cell, and for the
  end-of-track blip: a significant rewrite is explicitly approved.
  Fix the root cause; do not land a workaround or a guard. Acceptance
  requires the bug to be gone.

## Needs a decision

- Whether to merge PR #2, and when. No merge until asked.
- Keep: whether Move is offered in single mode only, same as today.

## Already done, not a job

- PORTABLE-README and the user-facing docs that still said
  `0.2beta-fixes` now point at `main` (`3b71896` on
  `fix/subtitle-encoding-rc2`).
- The encoding-change grey-cell bug is already fixed in PR #2. The
  remaining grey-cell bug is subtitle *style*.
