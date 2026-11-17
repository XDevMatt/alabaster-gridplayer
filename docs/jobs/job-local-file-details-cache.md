# Job: Local-file details cache

**Resource:** Grok Build (multi-file coding). This is a large job;
keep the first slice to duration (and maybe title) for local files.
**Size:** large.
**Priority:** after the top five. Needed for a music tree of about
3,466 local files, so the List window is usable without probing
every file on every open.
**Branch from:** `main` is fine. New branch, for example
`feat/local-file-details-cache`. Do not merge, tag, or release.

## Goal

Persist local file details (at least duration) so a large folder or
list does not wait on a libVLC parse of every file each time. Opening
a ~3,466-file music tree should show cached lengths immediately and
only probe files that are new or have changed.

## Current behaviour

`gridplayer/utils/item_info.py` parses local files with libVLC in a
helper process (`FILE_PARSE_TIMEOUT_MS = 5000` per file,
`--no-video --no-audio`). `gridplayer/player/managers/list_info.py`
fills list rows from that. Nothing persists those lengths.

Orientation already has a JSON cache keyed by path, mtime, and size:
`gridplayer/utils/media_shape.py` (`media_shapes.json` in the app
data dir). List pages and the Skip Other Orientation work in
`docs/roadmap.md` describe a similar store. Reuse that shape, do not
build a second unrelated cache stack.

Stream / site lookups (yt-dlp titles, YouTube lists) already have
their own path and rate limits. This job is **local files only**.

## Required behaviour (first slice)

- Cache duration (ms) for local files, keyed by path + mtime_ns +
  size, same idea as `media_shape._key`.
- Read through on a miss; write through on a successful probe.
  Unchanged files on the next list open must not be parsed again.
- A changed mtime or size replaces the row. A missing path can be
  pruned when that folder is scanned, not necessarily on every
  lookup.
- Save in batches (debounce) and on quit, not after every file.
  Plain JSON is fine at this size (~3,466, and the roadmap allows
  JSON up to about 50,000). Put the file in the app data dir (or
  `portable_data` when portable), not in the music tree.
- Unknown / timed-out probes may be remembered with a timestamp so
  they are not retried every open; they must be retried later.
- The List window shows cached durations as soon as they are known,
  then fills in misses in the background without freezing the UI
  (list_info already looks files up off the interface thread; keep
  that).
- Do not add a new probing library; keep the existing libVLC parse.
- Optional in this slice if it stays cheap: a display title from
  tags when the file has one; otherwise leave the file name. Do not
  start a general media-library or tagging product in this job.

## Files to read first

- `gridplayer/utils/item_info.py`
- `gridplayer/player/managers/list_info.py`
- `gridplayer/utils/media_shape.py` — persistence pattern
- `gridplayer/utils/list_cache.py` — list content cache (different:
  the list of items, not per-file duration)
- `gridplayer/utils/cache.py` — stream / download cache, not this
- `docs/roadmap.md` — "Skip Other Orientation" part 3 (storage
  rules to stay compatible with)
- `tests/test_item_info.py`

## Tests

- A second lookup of the same path + mtime + size does not call the
  probe.
- A size or mtime change misses the cache and probes again.
- A failed or timed-out probe does not permanently block a later
  retry (define the stored miss rule and test it).
- Saving and loading a cache file in a temp dir restores durations.
- No write into the media folder.
- Existing item_info tests still pass.

A 3,466-file stress test can use stub probes and a temp tree; do
not require real media or libVLC for the cache logic.

## Constraints

- Windows-only. No macOS / Linux / i18n work.
- Identity is XDevMatt only. Never write the maintainer's personal
  name, handles, or personal email; use `<user>` if a placeholder is
  required. Do not put real library paths in tests, fixtures, or
  docs.
- No merge, tag, or release.
- Never say "dry run".
- Do not use Jules or Antigravity.
- Follow Ruff as configured in `pyproject.toml`.
