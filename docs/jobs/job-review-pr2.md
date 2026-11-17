# Job: Review draft PR #2

**Resource:** SuperGrok first. Gemini (lowest paid tier, chat only)
or free Claude (chat only, no GitHub, small context) can also review
if the diff or one file is pasted after this brief. Not a Grok Build
coding job. Do not use Jules or Antigravity.

**Size:** small.
**What to review:**
https://github.com/XDevMatt/alabaster-gridplayer/pull/2
Branch `fix/subtitle-encoding-rc2` into `main`. Draft. Do not merge,
approve as a ship decision, tag, or release.

## What the PR claims

1. A subtitle file added during playback is given up to 3 seconds to
   appear as a track, then selected, then seeked so the current line
   is drawn.
2. Dropped subtitle files are no longer thrown away before the cell
   handler.
3. A Settings *encoding* change reopens only cells with subtitle
   files or tracks; other cells just remember the setting. A
   *style* change still reloads every cell (known, later job).
4. Some user-visible strings say GridPlayer Alabaster.
5. SubtitleCat failed downloads are logged without secrets; limit
   vs other HTTP failures are distinguished.
6. SubtitleCat saves a mostly-UTF-8 file with a few stray bytes as
   clean UTF-8 (`repair_stray_bytes`). Valid UTF-8, UTF-16, and
   legacy files are left as received. Default encoding stays unset.
7. Docs that pointed at `0.2beta-fixes` now point at `main`.

## What to look for

- Seek-after-attach: any chance of a visible hitch, a loop wrap, or
  a missed select on a slow load.
- Drop filter: subtitle files reach the cell; media drops still
  work; paths are compared as paths, not as slash-style strings
  (there was already a Windows slash test fix).
- Encoding reload: cells with no tracks but a soon-to-be-discovered
  sidecar are not stuck on the old encoding.
- `repair_stray_bytes`: false positives on legacy code pages;
  UTF-16 detection; whether Windows-1252 is the right mapping for a
  stray byte; no overwrite surprises; no secrets in SubtitleCat
  error logs (query strings, cookies, token-like assignments).
- Tests: gaps vs the claims; anything that needs libVLC and is not
  marked.
- Identity: no personal name, personal email, or private handles in
  the diff. Upstream credit (vzhd1701) is expected and fine.
- Docs: leftover `0.2beta-fixes` pointers that still claim the
  branch exists (a historical "done in 0.2beta-fixes" note in the
  release checklist is fine).

## How to paste (Gemini / Claude)

Do not ask those chats to clone the repo. Paste, in this order, as
many as fit:

1. This brief.
2. The PR summary (or the body text).
3. One of: `gridplayer/plugins/subtitlecat/save.py` (repair),
   `gridplayer/player/managers/video_blocks.py`
   (`apply_subtitle_encoding`), or the main attach/seek change in
   the video-block / subtitle widget. One file or a short diff per
   turn is better than the whole PR.

SuperGrok can be given the PR URL and this brief.

## What to return

A short review: real bugs first, then risks, then nits. Say whether
the encoding repair looks safe to ship as an opt-in later for
non-SubtitleCat files. Do not push commits. Do not merge.
