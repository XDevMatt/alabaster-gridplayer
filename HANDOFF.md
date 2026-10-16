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
1. T6 source pool             - Grok Build
2. T5 lookahead queue         - STRONGER AGENT, do not attempt
3. T2 aspect rules            - Grok Build (pure function, any time)
4. T3 shuffle + reflow        - STRONGER AGENT, do not attempt

## Exact next task: T6 (pool logic + hook into shuffle; no UI)
1. New file gridplayer/utils/cell_pool.py, pure Python, no Qt:
   - `class CellPool:` `__init__(self, sources: list[CellSource], files_in)`
     where `files_in(path) -> list[Path]` lists video files of one folder
     (injected so tests need no disk).
   - `pick(self, rng: random.Random) -> Path | None`:
     a) drop folders with no files; if none left return None;
     b) choose a folder by `weight` (rng.choices(folders, weights));
     c) inside it choose uniformly among files NOT in `self.recent`;
        if all are recent, choose among all of that folder;
     d) append to `self.recent` (collections.deque);
        window size = min(500, int(0.8 * total files of all folders)), at least 1.
2. gridplayer/widgets/video_block_navigation.py, `NavigationControl.shuffle`:
   at the top, get the profile:
   `profiles = getattr(self._block._ctx.<playlist manager>, "cell_profiles", {})`
   - find how managers are reached from a block (grep `self._block._ctx.`
     in that file); if you cannot find the playlist manager in 3 tries,
     STOP and write it as a blocker. Do not invent a new global.
   If the cell has a profile with sources: keep one CellPool per cell
   (dict on the NavigationControl, keyed by `self._block.video_params.id`),
   pick a file and open it the way the existing random step opens a file
   (read `_navigator.step(FolderStep.RANDOM)` code path to see how a path
   is put into the cell). If no profile or no sources: old behaviour,
   unchanged.
   For listing files use gridplayer.utils.next_file (find the existing
   function that lists a folder's videos; do not write a new scanner).
3. New tests/test_cell_pool.py:
   - seeded `random.Random(1)`, folder A 3 files, folder B 300 files,
     weight 1 each, 1000 picks -> each folder between 40% and 60%.
   - weights 3:1 -> folder A between 65% and 85%.
   - no file repeats within the window (window = 0.8 * 303 = 242 picks)
     as long as the folder still has unplayed files.
   - empty folder list -> pick returns None.

## Test commands and expected result
    .venv\Scripts\python -m pytest tests/test_cell_pool.py tests/test_cell_profile.py --basetemp=%TEMP%\gp_pt_t6 -q -p no:cacheprovider
Expected: all passed.
Real app (use a NEW --out folder every run, reused ones fail with FileExistsError):
    .venv\Scripts\python -m tests.real_app.run loop_toggle --out %TEMP%\gp_t6_loop
    .venv\Scripts\python -m tests.real_app.run navigation --out %TEMP%\gp_t6_nav
Expected: "PASSED: ...", exit 0, for both.

## Do not
- No refactors, no renames, no cleanups. Smallest change.
- No UI, no settings page in T6.
- No video re-encoding. No deleting files. No git push.
- No apostrophes in file names.
- Do not touch the VLC "non validated subtitle codec" warning (unfixable, harmless).
- Do not start T5 or T3.
- Max 3 attempts per problem, then STOP and write the blocker below.

## Stop when
T6 tests pass and are committed locally
(`git add -A && git commit -m "T6: cell source pool"`), OR 3 failed
attempts. Then stop and report.

## Blockers
(none)
