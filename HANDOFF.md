# HANDOFF (read first, then MILESTONE.md)

## Side by side with upstream GridPlayer (10-21-2026)
- The fork uses its own single-instance pipe and its own settings folder, so it
  runs next to upstream (Legacy) GridPlayer without taking its files or sharing
  its settings. Do not revert this when merging upstream.
- Pipe: `__instance_name__ = "gridplayer-alabaster-fileopen"` (gridplayer/version.py),
  used in gridplayer/utils/single_instance.py. Windows `\\.\pipe\gridplayer-alabaster-fileopen`,
  Linux/flatpak `gridplayer-alabaster-fileopen.socket`. Upstream: `gridplayer-fileopen`.
- Settings: `__settings_name__ = "GridPlayer-Alabaster"` (gridplayer/version.py), set as
  the Qt application name in gridplayer/main/init_app_env.py. Data folder
  `%APPDATA%\vzhd1701\GridPlayer-Alabaster` (settings.ini, log, cookies, screenshots,
  media_shapes.json), cache `%LOCALAPPDATA%\vzhd1701\GridPlayer-Alabaster\cache`.
  Upstream stays in `%APPDATA%\vzhd1701\GridPlayer`.
- On 10-21 settings.ini and media_shapes.json were copied (not moved) from the old
  shared folder into the new one. The old folder is now upstream GridPlayer's only.
  Backups: `C:\Users\<user>\agent-tools\gridplayer-split-2026-10-21\`.
- Still shared with upstream: `__app_id__` (Windows taskbar AppUserModelID) and the
  file-association ProgIDs built from `__app_name__` by scripts/windows.

## Alabaster identity (10-19-2026)
Newest section. The 10-18 section below is still valid, except: the doc files
are now committed (`docs: handoff state 10-18/10-19`), not "uncommitted on purpose".

- Name: **GridPlayer Alabaster**, a modified fork of GridPlayer by vzhd1701.
  Commit `832fc29` (name, version, NOTICE, About page, crash link).
- Version: `__fork_version__ = "0.5.5-alabaster.N"` (now `.1`) in
  gridplayer/version.py, shown in About, `--version` and the startup log line.
  `__version__` and pyproject `version` stay `0.5.5` (the upstream base):
  `-alabaster.N` is not a valid PEP 440 version, and scripts/init_app_vars.sh and
  scripts/stamp_dev_version.py parse `__version__`. Bump only `.N` for fork releases.
- Repo URL: ONE literal constant, `__app_url__` in gridplayer/version.py =
  `https://github.com/XDevMatt/gridplayer-alabaster` (private). Issues and new-issue
  URLs are built from it; scripts/init_app_vars.sh reads it with sed, so keep it a
  plain string literal. The GitHub account rename (old account -> XDevMatt) is
  pending; use the XDevMatt URL everywhere, including the new git remote.
- Crash dialog (gridplayer/dialogs/exception.py) links to `<__app_url__>/issues/new`.
  Nothing is sent automatically: no telemetry, no upload, no prefilled issue.
  The dialog shows the traceback (it includes local file paths) with a Copy button.
- Do NOT change `__app_name__`, `__author_name__`, `__app_id__`: they name the
  log file, app ids and build scripts, and `__author_name__` is the vzhd1701 part
  of the settings path. The settings folder itself now comes from
  `__settings_name__` (see the 10-21 section). Only display text was changed.
- GPL obligations, keep them: `LICENSE` (unchanged GPL-3.0 text), `NOTICE`
  (original work by vzhd1701, modifications (C) 2026 XDevMatt, change summary), the
  README "GridPlayer Alabaster (this fork)" section, and every upstream credit and
  third-party attribution (README Attributions, About dialog, Hack font license).
  Update NOTICE's change list and dates when features are added.
- Credit the fork author ONLY as `XDevMatt`. Never write a real name anywhere
  (code, docs, commit author). Commits use `-c user.name=XDevMatt -c user.email=341465779+XDevMatt@users.noreply.github.com`
  (no git identity is configured on this PC; do not set a global one).
- Open decisions for the maintainer (left pointing upstream): `.github/FUNDING.yml`
  (vzhd1701 donation links), `APP_REPO_SLUG="vzhd1701/gridplayer"` in
  scripts/init_app_vars.sh (release builds only), `JS_RUNTIME_HELP_URL` in
  gridplayer/utils/ytdlp_checkup.py, the translators link on the Settings page
  (resources/ui/settings_dialog.ui).
- GitHub repo settings: Actions and Projects disabled, Issues on.
- Push plan (NOT done; only when the maintainer says):
  `git remote rename origin upstream` (vzhd1701/gridplayer),
  `git remote add origin https://github.com/XDevMatt/gridplayer-alabaster.git`,
  `git push -u origin master`. `*.rar` and `*.bak-*` are gitignored and must not be
  pushed; check `git status --ignored` first.

## State as of 10-18-2026 (supersedes MILESTONE.md/AGENTS.md freeze notes)
Read this section first. Where MILESTONE.md or AGENTS.md disagree, this wins.

The maintainer is writing the next work. No queued task. Do not start anything until the maintainer says so.

### Repo state
- Head `f9e168e` (10-18 16:21 PT), master 13 commits ahead of origin. Still no git push.
- Uncommitted on purpose: this file, `MILESTONE.md`, and `AGENTS.md`. Do not commit them unless the maintainer asks.
- One local commit per finished task is the rule. AGENTS.md "frozen for QC" / "no commits" is superseded. MILESTONE.md "Dirty files" / "Nothing here has been committed" are obsolete (`0205a73`).
- Untracked: a local venv backup archive (`*.venv.rar`, repo root). Do not touch, move, delete, or commit it. The maintainer decides.
- The `*.bak-20261018` copies of the three doc files were removed 10-18. They were older snapshots of those files.

### Stopped here (10-18 evening)
- P1 seek-to-start log flood: DONE in `f9e168e`. `time_changed` skips loop-start/loop-end checks when `video_driver.length <= 0` and no A-B marks are set. Unit test `test_zero_length_loop_file_does_not_seek_to_start`. real_app `loop_toggle`, `subtitle_drop`, `aspect_filter` passed. No repeated-VLC-log guard.
- P1 deleted-VideoBlock crash: DONE in `116a37c`. real_app `closed_cell_all_commands` passed.
- real_app `tracks`: passed 3/3 on `f9e168e` with media folder `build/test-media/a0073ef78993`, each run alone. "the commentary plays" returned in 0.1-0.2s. No code change. On 10-16 it failed 3/3 at that step (VLC added the slave, the track never played), including on milestone 5 code, and the scenario still says the step is flaky under load. Do not edit `gridplayer/vlc_player/*` to chase it.

### Feature truth table (checked against source 10-18)
| Feature | State | Where |
|---|---|---|
| Subtitle file drop (.srt/.ass/.ssa/.vtt) on a cell | DONE | player/managers/drag_n_drop.py `_drop_subtitles` |
| "non validated subtitle codec" VLC line | wontfix (harmless) | - |
| Shift+L Toggle Loop File | DONE | params/actions.py, widgets/video_block.py, models/video.py |
| `[` `]` extra keys for Loop Start/End | DONE (see decision) | params/actions.py |
| Stable cell id + CellProfile saved in playlist | DONE | models/cell_profile.py, models/playlist.py |
| Aspect filter Off/Skip/Ask per cell | DONE | utils/media_shape.py, widgets/video_block_navigation.py |
| CellProfile upscale/downscale/deband | STORED ONLY, not applied, no UI | models/cell_profile.py |
| CellProfile sources (per-cell folders/weights) | STORED ONLY, unused (T6 deferred) | models/cell_profile.py |
| gradfun deband / scaler choice on Decoder page | NOT BUILT | - |
| Orientation layouts / reflow (T8, T2, T3) | NOT BUILT, deferred | - |
| Length-aware lookahead queue (T5) | NOT BUILT | - |

### Decision for the maintainer (do not change without his answer)
- T4 (`edbf1d7`) took `[` and `]` off -5% / +5% seek (params/actions.py "+5%"/"-5%"; now only Shift+Wheel). Keep `[` `]` as loop keys, or give them back to seek?

### Deferred (do not start)
T8-1/T8-2 auto reflow, T2, T3 (layout stays manual), T6 (one playlist per cell). T5 not started. Picture-quality work (deband, upscale/downscale around 100%) is the stored CellProfile fields above, not a queued task.

### Known failures to ignore
- real_app `navigation` ("waiting until the list too"; fails on the old code too)
- `test_percent_re::test_every_import_of_yt_dlp_is_followed_by_the_repair`
- `test_video_errors::TestVLCSaid::test_since_the_video_began_to_open`

### Logs
- App log: `%APPDATA%\vzhd1701\GridPlayer-Alabaster\gridplayer.log` (+ `.1`, `.2`); logs before 10-21 are in `...\vzhd1701\GridPlayer\`. Real-app logs: `<--out folder>\app.log`.
- settings.ini: `log_level=40`, `log_level_vlc=40` (ERROR). The seek flood that used to rotate these is fixed (`f9e168e`).
- Other ERROR noise, low priority: `avcodec: more than 5 seconds of late video`, `main: Failed to set on top`, `buffer deadlock prevented`, timestamp conversion errors.

## Do not
- No refactors, renames, or cleanups. Smallest change.
- No grid.py / layout changes.
- No video re-encoding. No git push. No apostrophes in file names.
- Do not touch the VLC "non validated subtitle codec" warning.
- Do not edit `gridplayer/vlc_player/vlc.py` (vendored) or translations.
- Max 3 attempts per problem, then STOP and write it here.
