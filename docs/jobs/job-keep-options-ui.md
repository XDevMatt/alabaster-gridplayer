# Job: Keep options UI

**Resource:** Grok Build (multi-file coding).
**Size:** medium.
**Priority:** after the top five.
**Branch from:** `main` is fine. New branch, for example
`feat/keep-options`. Do not merge, tag, or release.

## Goal

Give Keep (`E`) a settings UI: turn it on or off. Keep always
**copies**. At session end (app exit / session close), Alabaster
verifies each Keep copy against its original with BLAKE2 and, after
the user confirms a preview list, sends matching originals to the
Recycle Bin.

**Decided:** the default (and only) Keep action is Copy, not Move.
Move is not offered. It is replaced by copy plus the verified recycle
at session end, below. There is no remaining reason to keep a Move
option: an immediate move could lose the original before the copy is
proven, which this flow avoids.

Today Keep always copies, works only in single mode on a local file,
has no settings, and shows nothing on screen (result is only in the
log). See `docs/user-guide/keep.md` and `docs/FUTURE.md`.

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
- During Keep (`E`), the original is never touched (it only copies).
- Failures are logged, and the cell still moves on.

## Required behaviour

- Settings (a small Keep section, probably under Player or Playlist):
  - **Enable Keep** (on by default, so current users of `E` are
    unchanged). Off: `E` and the menu item do nothing, or the menu
    item is hidden.
  - No Copy / Move setting. Keep always copies.
- Still single mode and local files only for `E`.
- Show a brief on-cell or overlay note on success or skip or
  failure, not only a log line. Keep the wording short.
- Remember each successful Keep this session as a pair: the original
  path and the copy path (for example
  `D:\clips\beach\IMG_0042.mp4` and
  `D:\clips\beach_keep\IMG_0042.mp4`). Do not include skipped
  Keeps (destination already existed, so no new copy was made).
- **When the session ends** (app exit or session close):
  1. Gather all files kept this session.
  2. Hash each original and its Keep copy with BLAKE2
     (`hashlib.blake2b`, streamed in chunks; do not read a whole
     file into memory).
  3. Show a **preview list** of originals whose copies match
     exactly (same digest), and separately list any originals whose
     copy is missing or whose digest does not match. Nothing is
     touched yet. Never call this a "dry run".
  4. On the user's go, send the originals whose copies matched
     exactly to the Recycle Bin (`send2trash` or an equivalent that
     actually lands in the Recycle Bin). Never permanently delete.
     Leave the Keep copies in place.
  5. Any missing or mismatched copy is listed and its original is
     left untouched. A hash or recycle failure for one file must
     not recycle that original, and must not skip listing the
     others.
  6. If the user dismisses or cancels, leave every original in
     place.
- If there were no successful Keeps this session, do not prompt.
- Update `docs/user-guide/keep.md` and the known-limitations line
  about Keep (including that Move is not offered).
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

- Copy (default, and the only action): file appears in
  `../<folder>_keep/`, original remains, next is called when
  navigable. The pair is remembered for session end.
- Existing destination name: skipped, original remains, no
  overwrite, pair is not remembered.
- Enable off: `keep_active_and_next` is a no-op (no copy, no next).
- Not single mode or not a local file: no-op, as today.
- Default settings match today's Keep action (enabled, copy). There
  is no Move setting.
- Session end, matching BLAKE2 digests: preview list shows those
  originals; after confirm, `send2trash` (or equivalent) is called
  for each matching original, copies remain, originals are not
  permanently deleted.
- Session end, missing copy or mismatched digest: that original is
  listed as not matching and is left untouched, even on confirm.
- Session end, cancel or dismiss: no original is recycled.
- Hashing uses `hashlib.blake2b` and streams the file in chunks.
- Preview list is shown before any recycle. UI, comments, and tests
  never contain the words "dry run".

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
