# HANDOFF (read first, then MILESTONE.md)

## Status
- Done: T1 subtitles (f206758), specs (a4150d5), T4 loop keys (milestone 3).
  T4: Shift+L = "Toggle Loop File" (`VideoBlock.toggle_loop_file`,
  field `Video.end_action_before_loop`). `[` / `]` now also = Set Loop
  Start / End; they were -5% / +5% seek before (those keep Shift+Wheel).
- Not done: T7, T6, T5, T2, T3 - specs at end of docs/after-qc.md.
- Known pre-existing unit test failures (not yours, ignore):
  test_percent_re::test_every_import_of_yt_dlp_is_followed_by_the_repair,
  test_video_errors::TestVLCSaid::test_since_the_video_began_to_open.
  test_media_list_dialog::...nothing_new is flaky in the full run only.

## Order and who
1. T7 cell IDs + profile      - Grok Build (careful: old playlists must load)
2. T6 source pool             - Grok Build
3. T5 lookahead queue         - STRONGER AGENT, do not attempt
4. T2 aspect rules            - Grok Build (pure function, any time)
5. T3 shuffle + reflow        - STRONGER AGENT, do not attempt

## Exact next task: T7 (data model only, no UI, no applying scalers)
1. New file gridplayer/models/cell_profile.py:
   - `class CellSource(BaseModel)`: `path: Path`, `weight: float = 1.0`.
   - `class CellProfile(BaseModel)`: `sources: list[CellSource] = []`,
     `upscale: str | None = None`, `downscale: str | None = None`,
     `deband: bool | None = None`, `end_action: VideoEndAction | None = None`,
     `loop: bool | None = None`. Import VideoEndAction from
     gridplayer.params.static. None = use the app setting.
   - `def effective(profile, name, default)`: return the profile value if
     not None, else default.
2. gridplayer/models/playlist.py, `class Playlist`: add
   `cell_profiles: dict[UUID, CellProfile] | None = None`.
   In `Playlist.dumps` write it as doc["cell_profiles"] = {str(id): profile
   model_dump(mode="json", exclude_none=True)} only when not empty.
   In `Playlist._parse_json` read doc.get("cell_profiles") (missing = None).
   Look at how "lists" is done in the same two functions and copy that.
3. Cell id: `Video.id` (gridplayer/models/video.py) is the cell id. Check
   it survives `Playlist.dumps` -> `Playlist.parse` (it should; just test it).
4. New tests/test_cell_profile.py:
   - round-trip a Playlist with 2 videos and 2 profiles keyed by video.id;
     ids and profile fields come back equal.
   - a playlist text without "cell_profiles" parses, cell_profiles is None.
   - effective(CellProfile(), "deband", False) is False;
     effective(CellProfile(deband=True), "deband", False) is True.

## Test command and expected result
    .venv\Scripts\python -m pytest tests/test_cell_profile.py tests/test_playlist_settings.py tests/test_managers_playlist.py --basetemp=%TEMP%\gp_pt_t7 -q -p no:cacheprovider
Expected: all passed.
Then (new --out folder every run, reused folders fail with FileExistsError):
    .venv\Scripts\python -m tests.real_app.run loop_toggle --out %TEMP%\gp_t7_loop
Expected: "PASSED: ...", exit 0.

## Do not
- No refactors, no renames, no cleanups. Smallest change.
- No UI, no settings page, no scaler/deband code in T7.
- No video re-encoding. No deleting files. No git push.
- No apostrophes in file names.
- Do not touch the VLC "non validated subtitle codec" warning (unfixable, harmless).
- Do not start T5 or T3.
- Max 3 attempts per problem, then STOP and write the blocker below.

## Stop when
T7 tests pass and are committed locally
(`git add -A && git commit -m "T7: cell profile model"`), OR 3 failed
attempts. Then stop and report.

## Blockers
(none)
