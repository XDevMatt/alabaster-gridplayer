# Job: Opt-in stray-byte repair for any text subtitle

**Resource:** Grok Build (multi-file coding). SuperGrok can review the
PR #2 repair function first, then Grok Build can reuse it.
**Size:** small to medium.
**Priority:** medium (completes the encoding work in PR #2).
**Branch from:** `fix/subtitle-encoding-rc2` (needs
`repair_stray_bytes`). New branch, for example
`feat/opt-in-subtitle-repair`. Do not merge, tag, or release.

## Goal

A SubtitleCat download that is UTF-8 apart from a few broken bytes is
already saved as clean UTF-8 (`repair_stray_bytes` in
`gridplayer/plugins/subtitlecat/save.py` on
`fix/subtitle-encoding-rc2`). Sidecar and other non-SubtitleCat
`.srt` / text subtitles still need UTF-8 set by hand when they have
the same kind of stray byte, because libVLC 3.0 stops reading UTF-8
at the first bad cue and then falls back to Windows-1252, dropping
later cues.

Add an **opt-in** setting (off by default) that runs the same repair
when an external text subtitle is attached or auto-discovered, before
VLC reads it. Valid UTF-8, UTF-16, and legacy-encoded files must be
left byte-for-byte, as the SubtitleCat path already does. The default
encoding setting stays unset (VLC's own UTF-8 then Windows-1252).

## Required behaviour

- Off by default. Name and tooltip should say that it rewrites a
  mostly-UTF-8 file with a few invalid bytes, and that it does not
  guess a whole legacy code page.
- When on, apply `repair_stray_bytes` (move it to a shared module if
  both SubtitleCat and the attach path need it; do not duplicate the
  algorithm) to sidecar / dropped / chosen text subtitles
  (`.srt` and other text kinds already treated as external
  subtitles in `gridplayer/utils/external_subtitles.py`).
- Write the repaired bytes only when they differ. Prefer a repaired
  copy in the app cache or a sibling temp file that the cell owns,
  rather than silently overwriting the user's original. If you must
  write next to the original, use a clearly named copy and leave the
  original alone. State the choice in the PR.
- Embedded / muxed subtitle tracks inside a video are out of scope.
- ASS / SSA keep their own style and are not rewritten.
- Do not force Settings encoding to UTF-8.
- SubtitleCat should keep calling the same function; its behaviour
  must not change.

## Files to read first

- `gridplayer/plugins/subtitlecat/save.py` — `repair_stray_bytes`
  (on `fix/subtitle-encoding-rc2`)
- `tests/test_subtitlecat_save_encoding.py`
- `gridplayer/widgets/video_block_subtitles.py` — attach, drop,
  autodiscover
- `gridplayer/utils/external_subtitles.py`
- `gridplayer/player/managers/video_blocks.py` —
  `apply_subtitle_encoding`
- `gridplayer/params/settings_fields/subtitles.py` and
  `gridplayer/settings.py`

## Tests

Reuse the stray-byte fixtures from
`tests/test_subtitlecat_save_encoding.py`. Also:

- Setting off: attach leaves the file bytes unchanged and does not
  write a repaired copy.
- Setting on: a mostly-UTF-8 file with a stray byte is repaired;
  VLC is pointed at the repaired bytes; the original file is
  unchanged.
- Valid UTF-8, UTF-16, and a legacy-encoded file (more stray / 8-bit
  than valid multibyte) are left as received.
- SubtitleCat tests still pass.

## Constraints

- Windows-only. No macOS / Linux / i18n work.
- Identity is XDevMatt only. Never write the maintainer's personal
  name, handles, or personal email; use `<user>` if a placeholder is
  required.
- No merge, tag, or release.
- Never say "dry run".
- Do not use Jules or Antigravity.
- Follow Ruff as configured in `pyproject.toml`.
