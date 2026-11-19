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

## Step 2: regression test (no behaviour change)

**Done.**

- `tests/test_video_block_repeat.py`, parametrized over every leaving end
  action (`NEXT_FILE`, `PREVIOUS_FILE`, `SHUFFLE_FILE`, `PAUSE`, `STOP`,
  `CLOSE`):
  - `test_a_leaving_file_is_not_started_over_by_vlc_at_its_end`: the
    options VLC is given for the file have no `:input-repeat` and do have
    `:play-and-pause` (hold the last picture at the end). Fails on `main`:
    `[':input-repeat=10000']`.
  - `test_the_end_of_a_leaving_file_runs_its_end_action`: the player
    saying it is held at the end runs `loop_end_action` (no fall back of
    the time waited for). Fails on `main`: no such path.
  - Both are `xfail(strict=True)` for now; step 3 removes the mark.
- Real-app scenario recorder fixed: it now listens to the player inside
  the cell's frame, which the cell cannot disconnect mid-report.

Real app on `main` with the fixed recorder (TOUCHME, three real movies):
every leaving end replayed the start of the file before the next one:

| case | file that ended | last times VLC reported |
| --- | --- | --- |
| Next | Big Buck Bunny (596459 ms) | ... 596029, 596334, **401** |
| Shuffle | Elephants Dream (658320 ms) | ... 656943, 657442, **401** |
| Last to first | Sintel trailer (52209 ms), played whole | ... 51774, 52031, **402** |
| Loop This File | Big Buck Bunny | 596229, 402, 902 ... same player (correct) |

libVLC probe on TOUCHME (3.0.24, Sintel trailer, 2 s before the end):
`:input-repeat` reports 51971 then 400 (another pass); `:play-and-pause`
reports 52070 then a Paused event, no EndReached, no pass, and
`set_time(0)` + `play()` from there plays on from 0. That is the fix's
basis.

Next: step 3, the root-cause fix.

Tests: `uv run pytest tests/test_video_block_repeat.py
tests/test_vlc_player_loop.py`: 92 passed, 12 xfailed; with `--runxfail
-k leaving`: 12 failed (the new tests fail on `main` as they should).

## Step 3: root-cause fix

**Done.** Behaviour change: a file whose end action leaves it (Next,
Previous, Shuffle, Pause at Start, Stop, Close) is no longer started over
by VLC at its end; it plays to its very end, holds on its last picture,
and the end action runs from there.

The cause (b14e633) was the input being opened to go round
(`:input-repeat`) whatever the end action, with the end action only
caught after the wrap. The fix redoes how the input is opened, per end
action, instead of acting on the wrap:

- `vlc_player/static.py`: `is_end_a_loop(video)` (segment or Loop This
  File), now the one definition; `VideoBlock.is_end_a_loop` uses it.
- `vlc_player/player_base.py`:
  - Loop inputs keep `:input-repeat` (seamless loop untouched).
  - Leaving inputs get `END_HOLD_OPTION` (`:play-and-pause`) and no
    `:input-repeat`; the media list player is set to `default` for them so
    nothing restarts one that ends instead of holding.
  - `cb_paused`: a pause on a held input that nobody asked for
    (`_is_pause_asked`, set by `set_pause`, cleared by `play`) is the
    hold at the end: `notify_end_reached()`, not a pause to show.
  - `cb_end_reached`: a held input that ended anyway (VLC could not pause
    it) is the end too.
- New `end_reached` signal carried player -> driver -> frame -> cell for
  all four drivers (process HW/SW via `cmd_send`, single-process HW/SW via
  Qt signals); `VideoBlock._end_reached` runs `loop_end_action`, which
  keeps the existing paths (`_step_at_end`, pause at start, stop, close,
  bookmark hold).
- `_loop_wrapped` is left as the backstop for a wrap that still arrives
  on a non-Loop cell (it runs the end action).
- `tests/real_app/test_scenarios.py`: `end_of_track` off `KNOWN_BUGS`.
- `tests/test_single_mode_next_file.py`: its fake surface gets the new
  signal.

Not in this step (step 5): Loop toggled on or off mid-file. The input
keeps the way it was opened until then.

Tests: box `uv run pytest -m "not real_app"`: 7454 passed, 21 skipped,
1 failed (`test_network_checkup` name lookup, box DNS, fails on `main`
too). Step 2's 12 tests pass with the xfail mark removed.

Next: step 4 (Loop guard tests), then the real-app run on TOUCHME.
