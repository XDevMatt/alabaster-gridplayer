# HANDOFF (read this first, then MILESTONE.md)

## Status
- DONE milestone 1 (subtitles):
  - Dropping .srt/.ass/.ssa/.vtt (any ext in SUPPORTED_SUBTITLE_EXT,
    gridplayer/params/extensions.py) on a cell attaches it to that cell.
    Code: gridplayer/player/managers/drag_n_drop.py,
    DragNDropManager._finish_drop -> DragNDropManager._drop_subtitles ->
    SubtitleControl.add_external (gridplayer/widgets/video_block_subtitles.py).
  - Test: tests/real_app/scenarios/subtitle_drop.py (passes).
  - VLC log "avcodec: refusing to decode non validated subtitle codec":
    NO FLAG EXISTS for this in VLC 3. Checked every avcodec-* option string
    in C:\Program Files\VideoLAN\VLC\plugins\codec\libavcodec_plugin.dll;
    there is no "unvalidated" option. The check is hardcoded in VLC 3's
    avcodec subtitle decoder. It is a harmless WARNING: VLC then uses its
    own subsdec/libass decoder and subtitles still show (tracks scenario
    passes with that line in the log). Do NOT add an --avcodec-... flag.
- NOT DONE: anything in docs/after-qc.md and the cell-layout work in
  MILESTONE.md. Do not start them until sysop says so.
- Last commit: see `git log --oneline -1` (milestone 1: subtitles).

## Exact next task
1. Wait for sysop to name milestone 2. Do nothing else on your own.
2. When told, read MILESTONE.md and docs/after-qc.md for that item only.

## Test command and expected result
    .venv\Scripts\python -m tests.real_app.run subtitle_drop --out %TEMP%\gp_subdrop
    .venv\Scripts\python -m tests.real_app.run tracks --out %TEMP%\gp_tracks
Expected: last line "PASSED: ...", exit code 0.
Plain pytest: pass --basetemp=%TEMP%\gp_pytest (default temp dir gives
PermissionError on this PC).

## Do not
- No refactors. No renaming. Smallest change that works.
- No video re-encoding. No deleting files. No git push.
- No apostrophes in file names.
- Max 3 attempts per problem. Then STOP and write the blocker below.

## Stop when
The named task's real_app scenario passes and is committed, OR you hit
3 failed attempts. Then stop and report.

## Blockers
(none)
