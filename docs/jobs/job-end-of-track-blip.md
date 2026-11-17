# Job: End-of-track blip

**Resource:** Grok Build (multi-file coding).
**Size:** medium.
**Priority:** high (music listening; interacts with the Sync popup's
per-cell Loop checkbox).
**Branch from:** `fix/subtitle-encoding-rc2` if PR #2 is still open, else
`main`. New branch, for example `fix/end-of-track-blip`. Do not merge,
tag, or release.

## Goal

When a cell's When Finished action is not Loop This File, the file must
not restart for a moment before Next, Previous, Shuffle, Pause at Start,
Stop, or Close runs. That restart is the blip.

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
strips input-repeat for every file is wrong.

A sound approach: when `not is_end_a_loop`, watch time (with a small
headspace, in the same spirit as the existing 100 ms loop-start
headspace) and call `loop_end_action` before VLC wraps; or, for
non-Loop cells only, do not put `:input-repeat` on that input and
handle end through `cb_end_reached` / `time_changed` without a wrap.
Prefer the approach that keeps Loop seamless and needs no process
restart. Measure the headspace against real short files if you can;
unit tests should not depend on a magic machine-specific delay.

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
