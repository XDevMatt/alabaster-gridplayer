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
1. T8a orientation layout function - Grok Build
2. T8b wiring into the grid        - stronger agent (Grok Build only with care)
3. T2 aspect rules / T3 remainder  - T2 Grok Build, T3 STRONG
4. T6 source pool                  - Grok Build (old step list in git: bbd824d HANDOFF.md)
5. T5 lookahead queue              - STRONG
Full spec: "T8" at the end of docs/after-qc.md.

## Exact next task: T8a ONLY (pure function + unit test, no Qt, no grid code)
1. New file gridplayer/utils/layout/orientation_layout.py with
   `OrientationLayout` (NamedTuple: col_stretch, row_stretch, places) and
   `orientation_layout(cells, previous=None)` returning the rects from the
   T8 table for 0..4 portraits; None unless exactly 4 cells.
2. Same file: `is_portrait(width, height, transform)`; 90/270 rotation
   swaps width and height (see `VideoTransform` in gridplayer/params/static.py).
3. Portrait slots in order: left full-height, right full-height,
   centre-bottom; for 4P use 4 columns. With `previous`, keep a cell in
   its old slot when that slot still has its orientation.
4. New tests/test_orientation_layout.py: the 5 states match the table;
   each cell placed once; no two rects overlap; flipping one cell moves
   at most 2 cells; 3 cells -> None.

## Test command and expected result
    .venv\Scripts\python -m pytest tests/test_orientation_layout.py --basetemp=%TEMP%\gp_pt_t8a -q -p no:cacheprovider
Expected: all passed.
## Do not
- No refactors, no renames, no cleanups. Smallest change.
- No Qt, no grid.py changes in T8a (that is T8b).
- No video re-encoding. No deleting files. No git push.
- No apostrophes in file names.
- Do not touch the VLC "non validated subtitle codec" warning (unfixable, harmless).
- Do not start T5 or T3.
- Max 3 attempts per problem, then STOP and write the blocker below.

## Stop when
T8a tests pass and are committed locally
(`git add -A && git commit -m "T8a: orientation layout"`), OR 3 failed
attempts. Then stop and report.

## Blockers
(none)

