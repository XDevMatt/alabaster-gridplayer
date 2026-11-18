# Job: End-of-track blip

**Resource:** Grok Build (multi-file coding).
**Size:** medium.
**Priority:** high (music listening; interacts with the Sync popup's
per-cell Loop checkbox).
**Branch from:** `main` (PR #2 is merged as `d7d1056`). New branch, for example `fix/end-of-track-blip`. Do not merge,
tag, or release.

## This is a regression

**The blip did not exist before.** Earlier builds went to the next /
shuffled file without replaying the start of the current one. Now VLC's
`:input-repeat` wrap replays roughly the first ~2 s of the file before
Next / Shuffle runs. Treat it as a regression: find the commit that
introduced it with `git bisect` **before** writing a fix (step 1).

## Goal

When a cell's When Finished action is not Loop This File, the file must
not restart for a moment before Next, Previous, Shuffle, Pause at Start,
Stop, or Close runs. That restart is the blip.

**Decided:** a significant rewrite is explicitly approved if that is
what fixing the root cause takes. Fix the root cause (`:input-repeat`
is always on, so VLC starts another pass before a non-Loop end action
runs). Do not land a workaround or a guard that leaves the blip in
place. Acceptance requires the bug to be gone: non-Loop end actions
must not play the start of the file again.

## Root cause (already known)

VLC is always given `:input-repeat={INPUT_REPEAT_PASSES}`
(`gridplayer/vlc_player/player_base.py`, around the
`INPUT_REPEAT_PASSES = 10_000` comment and the media-option append).
VLC loops the input in place so a real Loop is seamless: there is no
end-of-media teardown, and a finished pass shows up as the time going
backwards.

`VideoBlock.time_changed` (`gridplayer/widgets/video_block.py`) detects
that wrap with `is_loop_wrapped` and calls `_loop_wrapped`:

- If the end action is `LOOP_FILE` and there is no A-B start /
  random start, it returns and leaves VLC's wrap alone. That is
  correct.
- Otherwise it calls `loop_end_action`. By then VLC has often already
  started the file over, so you hear the first moments again before
  the next file (or pause / stop / close) takes over.

`cb_end_reached` is not a reliable place to step away: with
`:input-repeat` the player is set to repeat, so that callback is the
start of a new pass, not a clean end.

## Required behaviour

- **Loop This File** (and A-B / segment loops): keep the current
  seamless `:input-repeat` wrap. No regression on short clips or
  Ogg/Opus (see Known Limitations: loop may log "seek to 0%" lines;
  playback must still be clean).
- **Any other end action** (`NEXT_FILE`, `PREVIOUS_FILE`,
  `SHUFFLE_FILE`, `PAUSE`, `STOP`, `CLOSE`): act *before* the natural
  end so `:input-repeat` never starts another pass. Then run the
  existing `loop_end_action` path (`_step_at_end`, pause, stop, close,
  bookmark hold).
- A seek that would pass the end is already treated as the end arriving
  early when `not is_end_a_loop` (see `seek_shift_ms`). Keep that.
- Bookmark hold (`_hold_end_for_bookmarks` / `LEAVING_END_ACTIONS`)
  must still work: do not skip past a held end.
- List / folder navigation and Shuffle must still pick the right next
  item. Do not start the current file over first.
- Turning Loop off mid-track (Shift+L or the Sync popup Apply) must
  take effect for the rest of that file.

Do not remove `:input-repeat` globally. Loop needs it. A fix that
strips input-repeat for every file is wrong. A significant rewrite of
how Loop vs non-Loop inputs are started, or how end is detected, is
approved if that is what a root-cause fix takes. Do not leave a
workaround or guard that still lets the wrap start and then tries to
hide it.

A sound approach: when `not is_end_a_loop`, watch time (with a small
headspace, in the same spirit as the existing 100 ms loop-start
headspace) and call `loop_end_action` before VLC wraps; or, for
non-Loop cells only, do not put `:input-repeat` on that input and
handle end through `cb_end_reached` / `time_changed` without a wrap.
Prefer the approach that keeps Loop seamless and needs no process
restart. Measure the headspace against real short files if you can;
unit tests should not depend on a magic machine-specific delay.

## Working rules: steps and checkpoints (required)

Work in the numbered steps below, in order. Each step ends at a
checkpoint built for a context reset:

1. Run the tests named in the step plus the existing suite for the
   files touched; they must pass.
2. Commit (XDevMatt identity) with the step number in the message, for
   example `step 3: ...`.
3. Append an entry to `docs/progress/<job-name>.md` on the work branch:
   step number, what is done, what is next, which tests pass (command
   and count), and any open question. A fresh session must be able to
   continue from that note and `git log` alone.

Rules for every step:

- **No behaviour changes outside the step's stated scope.** If
  something else looks wrong, write it in the progress note; do not fix
  it in this step.
- Every step states **what behaviour it changes** (or "none" for a
  pure refactor or a test-only step).
- Every step that changes behaviour adds a **before/after regression
  test**: it fails on the commit before the step and passes after it.
  A refactor step proves "no change" with the existing tests passing
  unchanged.
- Steps stay small: one reviewable commit each. Split a step that grows.

## Steps

1. **Bisect (no code changes).** Write a reproducible check: a small
   test or a short real-app script on a few-second clip with When
   Finished = Next File, which reports whether the start of the file is
   heard/seen again (time going backwards to near 0 before the next
   file loads). Find a known-good commit (an older Alabaster build or
   upstream GridPlayer 0.5.x behaviour) and run `git bisect` between it
   and `main`. Record the first bad commit, its diff summary, and why it
   causes the replay in the progress note. *Behaviour change: none.*
   If no good commit can be found, record what was tried and stop for
   the user's call before step 2.
2. **Regression test.** Turn the bisect check into a unit test in
   `tests/test_video_block_repeat.py` (no libVLC) that fails on `main`
   for each leaving end action (`NEXT_FILE`, `PREVIOUS_FILE`,
   `SHUFFLE_FILE`, `PAUSE`, `STOP`, `CLOSE`). Mark it expected-fail
   only if the suite needs to stay green between commits, and remove
   the mark in step 3. *Behaviour change: none.*
3. **Root-cause fix**, informed by the bisect result (revert or redo
   the change that introduced it if that is the cause). Non-Loop end
   actions must act before VLC starts another pass. *Behaviour change:
   leaving end actions no longer replay the start.* Step 2's test now
   passes.
4. **Loop stays seamless.** Tests that `LOOP_FILE` and A-B / segment
   loops still wrap without calling `loop_end_action`; Ogg/Opus and
   short clips covered. *Behaviour change: none (guard test).*
5. **Edge cases.** Bookmark hold, `seek_shift_ms` past the end, and
   Loop toggled off mid-file (Shift+L / Sync popup Apply), each with a
   before/after test. *Behaviour change: only what the test names.*
6. **Real-app check** on Windows if available (short clip, Next and
   Shuffle), result in the progress note.

## Files to read first

- `gridplayer/vlc_player/player_base.py` — input-repeat comments,
  `cb_end_reached`, `cb_time_changed`, media options
- `gridplayer/widgets/video_block.py` — `time_changed`, `_loop_wrapped`,
  `loop_end_action`, `is_end_a_loop`, `seek_shift_ms`
- `gridplayer/vlc_player/static.py` — `is_loop_wrapped`
- `tests/test_video_block_repeat.py` — wrap detection and end actions
- `tests/real_app/scenarios/loop_toggle.py` — Shift+L

## Tests

Extend `tests/test_video_block_repeat.py` (no libVLC for the logic
tests):

- For `LOOP_FILE` with no A-B marks, a wrap still does not call
  `loop_end_action` / next / shuffle.
- The bisect-derived regression test from step 2.
- For `NEXT_FILE`, `PREVIOUS_FILE`, `SHUFFLE_FILE`, `PAUSE`, `STOP`,
  and `CLOSE`, approaching the end (time within the headspace, or a
  wrap if one still arrives) calls `loop_end_action` and does not
  leave the file playing from the start.
- A wrap that somehow still arrives on a non-Loop cell must not play
  on; it must take the end action.
- A-B / segment loops still loop to the start.
- Bookmark hold still delays a leaving end action.
- `seek_shift_ms` past the end on a non-Loop cell still steps away.
- Changing from Loop to a leaving action mid-file uses the new
  action at the end.

If you add a real-app scenario, keep it short and Windows-oriented;
do not fail the job on missing libVLC in CI.

## Interaction with the Sync settings popup

[job-sync-settings-popup.md](job-sync-settings-popup.md) adds a staged
per-cell Loop checkbox that calls the same `set_end_action` /
`toggle_loop_file` logic. This fix must honour the cell's
`end_action` at the moment of the end, including a value applied from
that panel mid-track. Do not add a second Loop flag. Either job may
land first; they must not fight.

## Constraints

- Windows-only. No macOS / Linux / i18n work.
- Identity is XDevMatt only. Never write the maintainer's personal
  name, handles, or personal email; use `<user>` if a placeholder is
  required.
- No merge, tag, or release.
- Never say "dry run".
- Do not use Jules or Antigravity.
- Follow Ruff as configured in `pyproject.toml`.
