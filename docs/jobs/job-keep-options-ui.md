# Job: Keep options UI

**Resource:** Grok Build (multi-file coding).
**Size:** medium.
**Priority:** after the top five.
**Branch from:** `main` is fine. New branch, for example
`feat/keep-options`. Do not merge, tag, or release.

## Goal

Give Keep (`E`) a settings UI: turn it on or off, and choose **copy**
or **move**. Today Keep always copies, works only in single mode on a
local file, has no settings, and shows nothing on screen (result is
only in the log). See `docs/user-guide/keep.md` and
`docs/FUTURE.md`.

## Current behaviour (keep this unless a setting says otherwise)

`ActiveBlockManager.keep_active_and_next` and `keep_active_file` in
`gridplayer/player/managers/active_block.py`:

- Single mode only; in the grid, `E` does nothing and Keep is not on
  the menu.
- Local files only. Links / streams are a later "Keep a Copy"
  feature, out of scope here.
- Copies to `../<folder>_keep/<filename>` (example:
  `D:\clips\beach\IMG_0042.mp4` →
  `D:\clips\beach_keep\IMG_0042.mp4`).
- Skips if that name already exists in the keep folder; never
  overwrites.
- Then plays the next file when the cell can step.
- The original is never touched (because it only copies).
- Failures are logged, and the cell still moves on.

## Required behaviour

- Settings (a small Keep section, probably under Player or Playlist):
  - **Enable Keep** (on by default, so current users of `E` are
    unchanged). Off: `E` and the menu item do nothing, or the menu
    item is hidden.
  - **Keep action:** Copy (default) or Move.
- Move, when chosen: move the file to the same `../<folder>_keep/`
  destination, still skip if the name exists, never overwrite, never
  touch a file in another cell. After a successful move, the cell
  must not keep pointing at the old path; go to the next file as it
  already does. If move fails (in use, permission, other volume
  issues), log it, leave the original in place, and do not pretend it
  was kept.
- Still single mode and local files only.
- Show a brief on-cell or overlay note on success or skip or
  failure, not only a log line. Keep the wording short.
- Update `docs/user-guide/keep.md` and the known-limitations line
  about Keep.
- Do not implement "Keep a Copy" for streams in this job.

## Files to read first

- `gridplayer/player/managers/active_block.py` —
  `keep_active_and_next`, `keep_active_file`
- `gridplayer/params/actions.py` — Keep
- `docs/user-guide/keep.md`
- `docs/FUTURE.md` (Keep options)
- `docs/KNOWN-LIMITATIONS.md`
- `gridplayer/params/settings_fields/` and `settings_pages.py` for
  how to add a setting

## Tests

There are no Keep tests today; add unit tests with a temp folder:

- Copy (default): file appears in `../<folder>_keep/`, original
  remains, next is called when navigable.
- Existing destination name: skipped, original remains, no
  overwrite.
- Move: original is gone, destination has the file, next is called.
- Move when destination exists: skipped, original remains.
- Move failure (mock `OSError`): original remains, next may still be
  called; assert it was not deleted.
- Enable off: `keep_active_and_next` is a no-op (no copy, no next).
- Not single mode or not a local file: no-op, as today.
- Default settings match today's behaviour (enabled, copy).

## Constraints

- Windows-only. No macOS / Linux / i18n work.
- Identity is XDevMatt only. Never write the maintainer's personal
  name, handles, or personal email; use `<user>` if a placeholder is
  required. Do not put real user paths in tests or docs; use
  examples like `D:\clips\beach\`.
- No merge, tag, or release.
- Never say "dry run".
- Do not use Jules or Antigravity.
- Follow Ruff as configured in `pyproject.toml`.
