# Progress: end-of-track blip

Job brief: `docs/jobs/job-end-of-track-blip.md` (on `plan/next`).
Branch: `fix/end-of-track-blip`, from `main` at `d7d1056`.

## Step 1: bisect (no code changes)

**Done.**

Checks written:

- `scripts/bisect/end_of_track_check.py`: a cell on file 1 of a two-file
  folder, When Finished = Next File, is fed the times VLC reports to the
  end of the file (every 250 ms, then the time falling back to near 0, as
  VLC reports when it starts the same input again). Exit 0 if the end
  action runs before the end, 1 if it runs only after the fall back (the
  replay), 125 if the commit cannot be checked.
- `tests/real_app/scenarios/end_of_track.py`: the real app on a folder of
  two files or more (real movies when `GRIDPLAYER_BLIP_MOVIES` names a
  folder, else the generated clips): Next, Shuffle, the last file going
  round to the first, and Loop This File. It records every time each
  file's player reports, ahead of the cell, and fails on any time back in
  the first half of a file once that file was near its end. Listed in
  `KNOWN_BUGS` (strict xfail) until step 3.

Bisect: good `848487b` (end_action introduced, act 500 ms before the end),
bad `main` (`d7d1056`). `git bisect run` over 229 revisions, 9 steps:

```
good 848487b  bad d7d1056  bad 1077354  bad 15ffef2  good 06cc200
bad 92fd049   bad 687ad79  bad fa490af  good 5793303 bad 117b2ea
bad b14e633
first bad commit: b14e633 fix: improve looping mechanics
```

**First bad commit: `b14e633` "fix: improve looping mechanics"** (upstream,
2026-09-19). Diff summary: removes `VIDEO_END_LOOP_MARGIN_MS = 500`;
`VideoBlock.loop_end` becomes the full length instead of `length - 500`;
`player_base` puts `:input-repeat=2000000000` (later
`INPUT_REPEAT_PASSES = 10_000`, `b0ce4f2`) on every non-live input; adds
`is_loop_wrapped` and `VideoBlock._loop_wrapped`, which runs the end action
once the time has fallen back.

Why it replays: before, every end action ran 500 ms before the end, so a
leaving action started the next file before VLC got to the end. After,
the time can never pass `loop_end` (= length), so a non-Loop end action
only runs from `_loop_wrapped`, after VLC has already wrapped the input to
the start. The old input then keeps playing from 0 until the next file
replaces it, which takes as long as the folder lookup and the load (with
Include subfolders on by default the folder index can be scanned first),
heard as the first moments of the file again.

Real app on `main` (TOUCHME, Windows, libVLC 3.0.24, three Blender open
movies: Big Buck Bunny 9:56, Elephants Dream 10:58, Sintel trailer 0:52):
first run, Next from Big Buck Bunny: player reported 596229 ms then 401 ms
before Elephants Dream loaded (replay). The recorder of that run listened
after the cell, so it missed the wrap report where the cell let the player
go on it; fixed to record ahead of the cell before the next run.

Next: step 2, a unit regression test in `tests/test_video_block_repeat.py`
for each leaving end action.

Tests: box `uv run pytest -m "not real_app"`: 7442 passed, 21 skipped,
1 failed (`test_network_checkup` name lookup, no DNS sandbox on the box;
fails the same on `main`).
