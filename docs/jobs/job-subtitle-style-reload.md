# Job: Subtitle style change greys every cell

**Resource:** Grok Build (multi-file coding).
**Size:** medium.
**Priority:** medium-high (the remaining Settings grey-cell bug).
**Branch from:** `fix/subtitle-encoding-rc2` (PR #2 already fixed
encoding-change reloads). New branch, for example
`fix/subtitle-style-reload`. Do not merge, tag, or release.

## Goal

Changing a subtitle style knob in Settings must not grey every cell.
Cells with no subtitles must keep playing. Cells that have subtitles
must show the new style without a full-grid reload.

**Decided:** a significant rewrite is explicitly approved if that is
what fixing the root cause takes. Fix the root cause (subtitle style
is a VLC instance option, and a style change currently reloads every
cell). Do not land a workaround or a guard that leaves the bug in
place. Acceptance requires the bug to be gone: after a style-only
change, cells without subtitles are not greyed or reopened, and cells
with subtitles show the new style.

## Root cause (already known)

Subtitle style is a set of **VLC instance** options (`--freetype-*`,
`--sub-text-scale`), settled when a VLC process starts. See
`gridplayer/params/subtitle_style.py` and
`gridplayer/vlc_player/instance.py` (`_subtitle_style_options`).

`SettingsManager._is_reload_needed`
(`gridplayer/player/managers/settings.py`) includes every
`SUBTITLE_STYLE_SETTINGS` key, and a True result emits `reload`,
which reopens **every** cell (`VideoBlocksManager.reload_videos`).
PR #2 already made a *encoding* change reopen only cells that have
subtitle files or tracks (`apply_subtitle_encoding`). Style was left
alone because a new instance option usually means a new VLC process.

`tests/test_subtitle_style.py`
(`TestChangingItOpensTheVideosAgain.test_every_knob_asks_for_a_reload`)
currently asserts that any style change asks for a full reload. That
test must change with the new behaviour.

## Required behaviour

- Changing only subtitle style must not reload cells that have no
  subtitle files and no subtitle tracks. Those cells remember the
  setting and keep their picture.
- Cells that do have subtitles should show the new style. If the
  only safe way is to reopen those cells (or only the VLC processes
  that already have a style-using video), do that, not the whole
  grid.
- Videos-per-process may be greater than 1. If a process is shared
  by a cell with subtitles and a cell without, do not silently
  give them different instance options. Either split / reopen only
  what you must, or document and test the chosen rule. Do not
  require a full application restart for a font colour change if a
  narrower reopen works.
- Do not force the Settings encoding default to UTF-8.
- Do not regress PR #2's encoding path.
- ASS / SSA keep their own style, as the Settings page already says.

A process restart notice for style (`_is_restart_needed`) is a last
resort, worse than reopening only the cells that have subtitles.
Prefer the narrower reload.

## Files to read first

- `gridplayer/player/managers/settings.py` — `_is_reload_needed`,
  `_is_restart_needed`
- `gridplayer/player/managers/video_blocks.py` —
  `reload_videos`, `apply_subtitle_encoding`
- `gridplayer/params/subtitle_style.py`
- `gridplayer/vlc_player/instance.py`
- `gridplayer/multiprocess/process_manager.py` — instance options
  and process reuse
- `tests/test_subtitle_style.py`
- `tests/test_managers_settings.py`
- PR #2 discussion of style vs encoding

## Tests

- A style-only change does not report a full-grid reload (update
  `test_every_knob_asks_for_a_reload`).
- Cells with no subtitle files or tracks are not reopened.
- Cells with subtitles are reopened or otherwise receive the new
  options.
- An encoding-only change still uses `apply_subtitle_encoding` and
  does not reopen bare cells.
- Changing an unrelated setting that already requires a full reload
  (video driver, `misc/vlc_options`, and so on) still does.

## Constraints

- Windows-only. No macOS / Linux / i18n work.
- Identity is XDevMatt only. Never write the maintainer's personal
  name, handles, or personal email; use `<user>` if a placeholder is
  required.
- No merge, tag, or release.
- Never say "dry run".
- Do not use Jules or Antigravity.
- Follow Ruff as configured in `pyproject.toml`.
- A significant rewrite of instance handling, process reuse, or how
  style options are applied is approved. Do not stop at a workaround,
  a guard, or findings-only if the bug is still there.
