# HANDOFF (read first, then MILESTONE.md)

## Status
- Done: T1 subtitles (f206758), specs + engine analysis (milestone 2).
- Not done: T4, T7, T6, T5, T2, T3 - full specs at end of docs/after-qc.md.
- Last commit: run `git log --oneline -1`.

## Order and who
1. T4 loop toggle + [ ] keys  - Grok Build
2. T7 cell IDs + profile      - Grok Build (careful: old playlists must load)
3. T6 source pool             - Grok Build
4. T5 lookahead queue         - STRONGER AGENT, do not attempt
5. T2 aspect rules            - Grok Build (pure function, any time)
6. T3 shuffle + reflow        - STRONGER AGENT, do not attempt

## Exact next task: T4
1. gridplayer/models/video.py, class Video: add field
   `end_action_before_loop: VideoEndAction | None = None`.
2. gridplayer/widgets/video_block.py: next to `def set_end_action`, add
   `def toggle_loop_file(self)`: if end_action is LOOP_FILE and
   end_action_before_loop is set -> set_end_action(end_action_before_loop),
   clear it; else store current end_action, set_end_action(LOOP_FILE).
3. gridplayer/params/actions.py: copy the "When Finished Loop File" entry
   as "Toggle Loop File", func ("active", "toggle_loop_file"), key "Shift+L".
   Add "[" to "Set Loop Start" keys and "]" to "Set Loop End" keys
   (look how other actions list several keys; keep the old keys).
4. Write tests/real_app/scenarios/loop_toggle.py (copy the style of
   tests/real_app/scenarios/subtitle_drop.py).

## Test command and expected result
    .venv\Scripts\python -m tests.real_app.run loop_toggle --out %TEMP%\gp_loop
    .venv\Scripts\python -m tests.real_app.run subtitle_drop --out %TEMP%\gp_subdrop
Expected: last line "PASSED: ...", exit code 0, for both.
Unit tests: `.venv\Scripts\python -m pytest tests --ignore=tests/real_app --basetemp=%TEMP%\gp_pytest -q`
(without --basetemp you get a PermissionError; not your bug).

## Do not
- No refactors, no renames, no cleanups. Smallest change.
- No video re-encoding. No deleting files. No git push.
- No apostrophes in file names.
- Do not touch the VLC "non validated subtitle codec" warning (unfixable, harmless).
- Do not start T5 or T3.
- Max 3 attempts per problem, then STOP and write the blocker below.

## Stop when
T4 test passes and is committed locally
(`git commit -am "T4: loop toggle"`), OR 3 failed attempts. Then stop and report.

## Blockers
(none)
