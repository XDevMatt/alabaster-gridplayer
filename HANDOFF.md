# HANDOFF (read first, then MILESTONE.md)

## Status
- Done: T1 subtitles (f206758), specs (a4150d5), T4 loop keys (edbf1d7),
  T7 cell profile (bbd824d), T8 plan (2e901f0, b273679), T8a aspect filter
  (milestone 5).
- T8a: per-cell mode Off / Reject / Ask in `CellProfile.aspect_filter`
  (gridplayer/models/cell_profile.py, enum `AspectFilter` in
  gridplayer/params/static.py). Cell shape = its rect
  (`NavigationControl.cell_is_portrait`). Reject = `_aspect_fits` passed
  to `FolderNavigator(fits=...)` -> `ShuffleBag.next(exists=)` /
  `existing_neighbour(exists=)`, max 10 probes per step then any file.
  Ask = `_switch_checked` -> `_ask_about` (pause + dialog; Skip re-takes
  `FolderNavigator.last_step`). Probe + in-memory cache:
  gridplayer/utils/media_shape.py (`shape_of`, own VLC process).
  Profile access: commands `cell_profile`, `set_cell_profile_field`
  (gridplayer/player/managers/playlist.py), `VideoBlock.aspect_filter`.
  Applies to folder navigation only, not to cells that play a list.
- DEFERRED by the maintainer: T8 auto reflow (T8-1/T8-2), T2, T3 (layout stays
  manual), T6 (one playlist per cell). T5 not started.
- Known pre-existing failures (not yours, ignore): real_app `navigation`
  ("waiting until the list too", fails on the old code too);
  test_percent_re::test_every_import_of_yt_dlp_is_followed_by_the_repair;
  test_video_errors::TestVLCSaid::test_since_the_video_began_to_open.

## Exact next task: T8a-2 (spec at end of docs/after-qc.md)
1. tests/real_app/media.py: add a 5 s portrait clip (e.g. 360x640) and a
   second 5 s landscape clip in a new folder `shapes/`, generated with
   ffmpeg exactly the way the existing clips are made (test media only).
   Add their paths to the `Media` class.
2. New tests/real_app/scenarios/aspect_filter.py: open the landscape clip,
   `d.ctx.commands.set_cell_profile_field(b.video_params.id,
   "aspect_filter", AspectFilter.REJECT)`, set When Finished Shuffle,
   `d.act(b, "Next")`-style step 5 times (use the action that shuffles;
   see tests/real_app/scenarios/navigation.py) -> uri never the portrait.
3. gridplayer/utils/media_shape.py: save `_cache` to a json file in the
   app data folder (grep for where other files in that folder are
   written; reuse that path helper), load it on first `shape_of`.
4. Unit test in tests/test_aspect_filter.py: cache file written and read
   back (monkeypatch the folder to tmp_path).

## Test command and expected result
    .venv\Scripts\python -m pytest tests/test_aspect_filter.py tests/test_cell_profile.py tests/test_menu.py --basetemp=%TEMP%\gp_pt_t8a2 -q -p no:cacheprovider
    .venv\Scripts\python -m tests.real_app.run aspect_filter --out %TEMP%\gp_t8a2_af
    .venv\Scripts\python -m tests.real_app.run loop_toggle --out %TEMP%\gp_t8a2_loop
Expected: all passed / "PASSED: ...", exit 0 (new --out folder every run).
## Do not
- No refactors, no renames, no cleanups. Smallest change.
- No grid.py / layout changes (auto layout is deferred).
- No video re-encoding. No deleting files. No git push.
- No apostrophes in file names.
- Do not touch the VLC "non validated subtitle codec" warning (unfixable, harmless).
- Do not start T5, T3, T6, T8-1/T8-2 (deferred).
- Max 3 attempts per problem, then STOP and write the blocker below.

## Stop when
T8a tests pass and are committed locally
(`git add -A && git commit -m "T8a-2: aspect filter test + cache"`), OR 3 failed
attempts. Then stop and report.

## Blockers
(none)

