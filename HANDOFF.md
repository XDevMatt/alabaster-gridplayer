# HANDOFF (read first, then MILESTONE.md)

## Status
- Done: T1 subtitles (f206758), specs (a4150d5), T4 loop keys (edbf1d7),
  T7 cell profile (bbd824d), T8 plan (2e901f0, b273679), T8a aspect filter
  (9237cf7), T8a-2 test clips + disk cache (milestone 6).
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

## Exact next task: fix the real_app `tracks` blocker (see Blockers), then wait for the maintainer
T8a-2 is DONE (milestone 6): portrait/landscape test clips in
tests/real_app/media.py (`Media.shapes`: wide1.mp4, wide2.mp4, tall.mp4),
scenario tests/real_app/scenarios/aspect_filter.py, shape cache saved to
`<app data dir>/media_shapes.json` (gridplayer/utils/media_shape.py
`_load`/`_save`), probe process ends with the app (`_exit_with_parent`,
`release`).
1. Run `.venv\Scripts\python -m tests.real_app.run tracks --out %TEMP%\gp_tr_1`.
2. In that folder's report.json find the last step before "the commentary
   plays"; in app.log look after "Adding audio slave ...commentary.m4a".
3. The same failure happens on milestone 5 code (9237cf7) with the new
   media folder, so the cause is the environment or the new media folder
   (build/test-media/a0073ef78993), not the aspect filter. Try: run once
   with nothing else open; compare with build/test-media/e49ef1887ba2.
4. If not found in 3 tries: STOP, leave a note here. Do not edit
   gridplayer/vlc_player/* to "fix" it.
After that, no queued task: ask the maintainer. Deferred: T8-1/T8-2, T2, T3, T6; T5 not started.

## Test command and expected result
    .venv\Scripts\python -m pytest tests/test_aspect_filter.py tests/test_cell_profile.py tests/test_menu.py --basetemp=%TEMP%\gp_pt_x -q -p no:cacheprovider
    .venv\Scripts\python -m tests.real_app.run aspect_filter --out %TEMP%\gp_af_x
    .venv\Scripts\python -m tests.real_app.run loop_toggle --out %TEMP%\gp_loop_x
    .venv\Scripts\python -m tests.real_app.run subtitle_drop --out %TEMP%\gp_sub_x
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
`tracks` passes (commit "fix tracks scenario"), OR 3 failed attempts. Then stop and report.

## Blockers
- 2026-10-16: real_app `tracks` fails 3/3 at "the commentary plays" (20 s timeout; VLC adds the audio slave but its track never plays). Also fails with the milestone 5 code, so not caused by T8a-2. It passed earlier the same day with the old media folder e49ef1887ba2. The scenario itself says this step is flaky under load.
