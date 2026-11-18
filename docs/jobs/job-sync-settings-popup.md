# Job: Sync settings popup

**Resource:** Grok Build (multi-file coding).
**Size:** medium.
**Priority:** high.
**Branch from:** `main` (PR #2 is merged as `d7d1056`). New branch, for example `feat/sync-settings-popup`. Do not merge,
tag, or release.

## Goal

A non-modal panel that floats above the player (like a Violentmonkey
userscript settings panel on a website) and shows every Sync setting in
one place, plus a per-cell Loop checkbox. Playback continues in every
pane while it is open. The user can still click cells and use the player.
Changes are staged: nothing is applied until **Apply**. **Apply**
commits every staged change and closes the panel. **Cancel**, the
window close button, and Escape discard the draft and close.

Today these settings live in three places and apply immediately:

- Settings (modal) > Playlist > Sync
- Grid menu > Sync (live toggles)
- Cell menu > When Finished / Shift+L for Loop This File

The Settings dialog is modal (`gridplayer/dialogs/paged_dialog.py`
`setModal(True)`), so the player UI is blocked while it is open. Menu
toggles apply live today. There is no single staged view of sync plus
per-cell Loop.

**Decided:** Grid > Sync opens this staged panel (it replaces the
existing live Grid > Sync submenu toggles).

## Fields

### Grid-wide (playlist settings, apply to every cell)

Same four keys as the Settings Sync section
(`gridplayer/params/settings_pages.py`,
`gridplayer/params/settings_fields/playlist.py`):

| UI | Setting | Values |
| --- | --- | --- |
| Seek sync | `playlist/seek_sync_mode` | Disabled, Percent, Timecode (`SeekSyncMode`) |
| Sync zoom and position | `playlist/view_sync` | on / off |
| Sync play and pause | `playlist/pause_sync` | on / off |
| Sync speed | `playlist/rate_sync` | on / off |

Tooltips can reuse the existing Settings strings. Reuse
`choices.seek_sync_modes` for the seek control.

These are playlist-level, not per-cell. Write them through
`PlaylistSettings().set(...)` and the existing
`VideoBlocksManager` setters, not by poking `_ctx` alone.

### Per-cell Loop (one row per pane)

One checkbox row per current cell, labelled with the cell title (and
index if titles collide). Checked means **Loop This File**
(`VideoEndAction.LOOP_FILE`). Unchecked means regular playback: that
cell's When Finished action, not Loop.

Tie this to the existing per-cell end action, not a new flag:

- `VideoBlock.toggle_loop_file` (`gridplayer/widgets/video_block.py`),
  bound to Shift+L as `Toggle Loop File`
- `VideoBlock.set_end_action`
- `Video.end_action` and `Video.end_action_before_loop`
  (`gridplayer/models/video.py`)

On Apply, use the same semantics as Shift+L:

- Checking Loop: store the current `end_action` in
  `end_action_before_loop` if it is not already Loop, then
  `set_end_action(LOOP_FILE)`.
- Unchecking Loop: if `end_action_before_loop` is set, restore it and
  clear the stored value. If it is missing (Loop was chosen from the
  When Finished menu, which does not store a previous action), this is
  **decided:** set When Finished to Play Random File (`SHUFFLE_FILE`).
  When the current file ends, play a random file from the same folder
  as the current file, start it from the beginning (position 0), and
  mute it. Do not leave the checkbox unchecked while the cell stays
  on Loop.

Skip or disable the checkbox for live or unseekable cells
(`toggle_loop_file` is `@only_seekable`; the menu item is hidden for
live). Empty cells get no row, or a disabled row.

**Sync Others** (one-shot seek / view copy from a cell menu) stays on
the cell menu. It is not a setting and does not belong in this panel.

## Staging model

- Opening the panel copies current `PlaylistSettings` values and each
  cell's `end_action` / `end_action_before_loop` into a draft. The live
  player is unchanged.
- Editing widgets updates only the draft.
- **Apply** writes every staged change through the existing APIs
  below, then closes the panel.
- **Cancel**, the window close button, and Escape discard the draft and
  close. No writes.
- One instance only: a second open raises the existing panel and keeps
  its draft.
- If a cell is added or closed while the panel is open, refresh the
  rows. Keep staged Loop checks for cells that are still there. New
  cells start from their live end action. Apply must not touch a cell
  that no longer exists.
- Opening Settings while the panel is open: on Apply, the panel's
  draft wins for the keys it writes. Grid > Sync while the panel is
  already open raises the same instance and keeps the draft; it must
  not apply anything live.

## Apply path (existing APIs)

In `gridplayer/player/managers/video_blocks.py`:

- `set_seek_sync_mode(mode)` — already writes `PlaylistSettings` and
  `_ctx.seek_sync_mode`
- `set_view_sync(is_sync)` / `toggle_view_sync` — `set_view_sync`
  forgets `synced_view` when the value changes; if you set the flag
  directly, also write `PlaylistSettings` and call `set_view_sync` so
  that forget still happens
- `set_pause_sync` / `toggle_pause_sync`
- `set_rate_sync` / `toggle_rate_sync`

For Loop, call `VideoBlock.set_end_action` / the Shift+L logic on each
changed cell. Do not invent a second end-action store.

Wire Grid > Sync so it opens this panel, and give it a shortcut only
if it does not clash (check `gridplayer/params/actions.py`). Do not
keep a parallel live-toggle submenu under Grid > Sync.

## UI

- Non-modal `QDialog` or `QWidget` with `Qt.Tool` and a parent of the
  player window, so it floats above the player and does not block it.
  `isModal()` must be false. Do not use `exec_()`. Use `show()`.
- Stay on top of the player, not necessarily of other apps.
- Buttons: **Apply**, **Cancel**. Close = Cancel.
- Do not pause or reload cells just because the panel is open.
- Follow existing dialog typography and the current colour scheme.
- English strings only. Use `translate(...)` like the other dialogs,
  but do not add translation catalogue work.

Suggested home: `gridplayer/dialogs/sync_settings.py`, opened from
`VideoBlocksManager` or a small manager next to the tray / settings
managers.

## Interaction with the end-of-track blip

VLC is always started with `:input-repeat` (see
`gridplayer/vlc_player/player_base.py`, `INPUT_REPEAT_PASSES`). For
`LOOP_FILE`, `VideoBlock._loop_wrapped` returns early and the wrap is
seamless. For any other end action, `loop_end_action` should run, but
the wrap can already have restarted the first moments of the track
(the blip) before Next / Shuffle / Pause / Stop / Close happens.

That wrap is a **separate job**:
[job-end-of-track-blip.md](job-end-of-track-blip.md). This panel must
not reimplement input-repeat or end detection.

- Cells left or set to Loop on Apply must keep the current seamless
  wrap.
- Cells set to regular playback on Apply should then follow whatever
  end-of-track behaviour is in the tree at that time. If the blip fix
  is not in yet, the blip may still be heard on those cells; that is
  expected. If the blip fix is in, turning Loop off and Applying mid-
  track must take effect for the rest of that file (no restart blip
  at the end).
- Do not land a panel-only workaround that fights the blip fix later.

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

1. **Draft model (no UI).** A plain class that snapshots the four
   grid-wide sync values and each cell's `end_action` /
   `end_action_before_loop`, edits only the draft, and has `apply()` /
   `discard()`. Unit tests with fakes. *Behaviour change: none
   (not wired yet).*
2. **Apply semantics.** `apply()` writes through the existing setters
   and the Shift+L logic, including the decided Loop-off fallback
   (Play Random File from the same folder, from position 0, muted).
   *Behaviour change: none in the app yet.* Tests per rule.
3. **Panel widget.** Non-modal `Qt.Tool` panel bound to the draft;
   Apply closes, Cancel / Escape / close discard; single instance.
   *Behaviour change: none until wired.* Tests: `isModal()` false,
   `show()` not `exec_()`, no writes before Apply.
4. **Wire Grid > Sync** to open the panel and remove the live-toggle
   submenu. *Behaviour change: Grid > Sync opens the staged panel
   instead of toggling live.* Before/after test (old submenu test
   updated).
5. **Cell list refresh** when cells are added or closed while open;
   live / unseekable cells disabled. *Behaviour change: only the panel
   rows.* Tests.
6. **Real-app check** on Windows if available, result in the progress
   note.

## Tests (unit, no libVLC, no real window playback)

Add tests next to `tests/test_sync.py` and
`tests/test_video_block_repeat.py`. Update any Grid > Sync live-toggle
tests so they expect the staged panel to open instead.

At minimum:

- Opening snapshots current seek / view / pause / rate values and each
  cell's Loop state into the draft.
- Changing widgets does not call `set_seek_sync_mode`, the sync
  setters, or `set_end_action` until Apply.
- Apply writes all staged grid-wide settings through those APIs, then
  closes the panel.
- Apply sets `LOOP_FILE` on checked cells and restores
  `end_action_before_loop` (or the fallback above) on unchecked cells.
- Cancel, Escape, and the close button write nothing and close the
  panel.
- `isModal()` is false; the panel is shown with `show()`, not
  `exec_()`.
- A second open raises the same instance and keeps the draft.
- A cell that disappears before Apply does not crash Apply.
- Live / unseekable cells do not get an enabled Loop checkbox.
- Grid > Sync opens the panel (and a second Grid > Sync raises the
  same instance).

## Constraints

- Windows-only. No macOS / Linux / i18n work.
- Identity is XDevMatt only. Never write the maintainer's personal
  name, handles, or personal email; use `<user>` if a placeholder is
  required.
- No merge, tag, or release.
- Never say "dry run".
- Do not use Jules or Antigravity.
- Follow Ruff as configured in `pyproject.toml`. English comments in
  the project's usual voice.

## Out of scope

- Changing how seek / view / pause / rate sync actually follows a
  leader (`tests/test_sync.py` behaviour stays).
- Per-cell seek or speed sync (those settings stay grid-wide).
- A-B loop marks (`,` `.` `/`).
- Reworking the modal Settings Sync section; leaving it in place is
  fine. It may keep applying on OK as it does today.
