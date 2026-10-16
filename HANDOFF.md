# HANDOFF (read first, then MILESTONE.md)

## Status
- Done: T1 subtitles (f206758), specs (a4150d5), T4 loop keys (edbf1d7),
  T7 cell profile model (milestone 4).
  T7: gridplayer/models/cell_profile.py (`CellSource`, `CellProfile`,
  `effective`). `Playlist.cell_profiles: dict[UUID, CellProfile] | None`,
  saved as top-level "cell_profiles" (only when not empty; old playlists
  load with None). Cell id = `Video.id`. `PlaylistManager.cell_profiles`
  (gridplayer/player/managers/playlist.py) holds them after load and
  `_cell_profiles_to_save` writes back those whose cell still exists.
  Nothing READS a profile yet, and there is no UI to edit one.
- Not done: T6, T5, T2, T3 - specs at end of docs/after-qc.md.
- Known pre-existing unit test failures (not yours, ignore):
  test_percent_re::test_every_import_of_yt_dlp_is_followed_by_the_repair,
  test_video_errors::TestVLCSaid::test_since_the_video_began_to_open.
  test_media_list_dialog::...nothing_new is flaky in the full run only.

## Order and who
1. T8a aspect filter (shuffle/next keep orientation) - Grok Build
2. T8-1 orientation layout function (pure)          - Grok Build
3. T8-2 reflow wiring into the grid                 - stronger agent
4. T2 aspect rules / T3 remainder                   - T2 Grok Build, T3 STRONG
5. T6 source pool                                   - Grok Build (old steps: git show bbd824d:HANDOFF.md)
6. T5 lookahead queue                               - STRONG
Full specs at the end of docs/after-qc.md ("T8a aspect filter", "T8").

## Exact next task: T8a ONLY
1. gridplayer/utils/item_info.py: add `shape_of(path) -> bool | None`
   (True portrait, False landscape, None unknown). Copy `_length_of`; read
   the first video track width/height; 90/270 rotation swaps them. Cache
   in a module dict keyed by (str(path), mtime, size).
2. gridplayer/models/video.py class Video: add `is_aspect_filter: bool = False`.
3. gridplayer/utils/folder_navigator.py `FolderNavigator._take_step`:
   when the video has is_aspect_filter and the current shape is known,
   - RANDOM: `self._shuffle_bag.next(avoid=..., exists=fits)` where
     `fits(p) = p.is_file() and shape_of(p) in (None, want)`;
   - NEXT: step `scan.existing_neighbour` forward until one fits.
   Stop checking after 10 probes or 1.5 s and take the next file anyway.
   Current shape: pass a callable into FolderNavigator from
   `NavigationControl` (gridplayer/widgets/video_block_navigation.py)
   that reads the block's `video_driver.media.video_tracks` dimensions.
   If you cannot find how FolderNavigator is built in 3 tries, STOP and
   write the blocker.
4. gridplayer/params/actions.py: add "Keep Orientation" (toggle, func
   ("active", "toggle_aspect_filter"), check_if is_active_param_set_to
   is_aspect_filter True), no default key; add it to menu.py "When
   Finished" group under "When Finished Shuffle". Add
   `VideoBlock.toggle_aspect_filter` in gridplayer/widgets/video_block.py.
5. tests/test_aspect_filter.py (monkeypatch shape_of): 6 files, 3
   portrait, 20 random steps from a portrait -> only portraits; all wrong
   shape -> a file is still returned; None counts as fit.

## Test command and expected result
    .venv\Scripts\python -m pytest tests/test_aspect_filter.py tests/test_cell_profile.py --basetemp=%TEMP%\gp_pt_t8a -q -p no:cacheprovider
    .venv\Scripts\python -m tests.real_app.run navigation --out %TEMP%\gp_t8a_nav
    .venv\Scripts\python -m tests.real_app.run loop_toggle --out %TEMP%\gp_t8a_loop
Expected: all passed / "PASSED: ..." exit 0 (new --out folder every run).
## Do not
- No refactors, no renames, no cleanups. Smallest change.
- No grid.py / layout changes in T8a (that is T8-2).
- No video re-encoding. No deleting files. No git push.
- No apostrophes in file names.
- Do not touch the VLC "non validated subtitle codec" warning (unfixable, harmless).
- Do not start T5 or T3.
- Max 3 attempts per problem, then STOP and write the blocker below.

## Stop when
T8a tests pass and are committed locally
(`git add -A && git commit -m "T8a: aspect filter"`), OR 3 failed
attempts. Then stop and report.

## Blockers
(none)

