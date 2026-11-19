# Job: fuller default keymap + on-top cheat sheet

Owner decisions (2026-11-18). Start from `main`. Work in the numbered
steps below; each ends with a commit and a note in
`docs/progress/job-keymap-defaults-and-cheat-sheet.md`. No changes outside
a step's scope. Each behaviour-changing step carries a before/after test.

Conventions kept: an unmodified key acts on the active cell, Shift does
the same to all cells. Most mice have only two side buttons (Back,
Forward); modifiers give them more jobs, never extra buttons. Nothing
destructive goes on a default key (no Delete, even to the Recycle Bin).

All keys below were free on `main` d7d1056; re-check with
`find_duplicate_shortcuts` before committing, and stop if any clash.

## Step 1: bind existing, unbound actions (keymap only)

Mouse:

| Binding | Action |
| --- | --- |
| Back-Click / Forward-Click | Play Previous File / Play Next File |
| Shift+Back-Click / Shift+Forward-Click | Back From Random File / Play Random File |
| Ctrl+Back-Click / Ctrl+Forward-Click | -30s / +30s |
| Middle-Click (no drag) | Audio Volume - Mute / Unmute, cell under cursor (Middle-Drag stays pan) |
| Shift+Wheel-Up / -Down | Audio Volume - Increase / Decrease [ALL] |
| Alt+Wheel-Up / -Down | +1% / -1% |

Keyboard:

| Key | Action |
| --- | --- |
| Up / Down | Audio Volume - Increase / Decrease (active) |
| Shift+Up / Shift+Down | same [ALL] |
| Ctrl+M | Audio Volume - Mute / Unmute (active; M stays ALL) |
| Ctrl+K / Ctrl+H | Audio Delay Reset / Subtitle Delay Reset |
| Ctrl+PgUp / Ctrl+PgDown | Previous Chapter / Next Chapter |
| Ctrl+B | Add Bookmark |
| Alt+PgUp / Alt+PgDown | Previous Bookmark / Next Bookmark |
| Ctrl+E | Show in Folder |
| Alt+V | Find Subtitles on SubtitleCat |
| Ctrl+R | Rotate 90 |
| F2 (added to F4) | Rename |
| F11 (added to F) | Fullscreen |
| Ctrl+W (added to Ctrl+F4) | Close |

Confirm Middle-Click with no movement reaches the keymap as a click
(see `params/gestures.py`) and that Shift/Alt+Wheel modifiers are
parsed; if a modifier+wheel is not supported, report and skip that row.
Test: defaults load with no duplicates; each new binding resolves to
its action.

## Step 2: new cycle actions

- `A`: cycle view mode Fit -> Fill -> Stretch (active); `Shift+A` all.
- `V`: cycle subtitle track (active), including Off; `Shift+V` all.
Tests for wrap-around and for a cell with no subtitle tracks.

## Step 3: keymap cheat sheet window

- New action "Keymap Cheat Sheet", key `F3`, also in the menu.
- A separate, non-modal, frameless-or-tool window that stays on top of
  the player; the grid keeps playing and taking keys and clicks while
  it is open.
- Opacity slider (20-100%) and a "click-through" toggle (mouse passes
  to the videos underneath). F3 toggles it even when click-through is on.
- Shows the live bindings (user overrides included), grouped like the
  Shortcuts page, with a filter box.
- Remembers position, size, opacity, click-through in settings.
- Tests: opening it does not block the player's event loop; opacity and
  position persist; bindings shown match the active keymap.

## Step 4 (optional, owner to OK): ports from Vlad's upstream

Vlad's current defaults have features this fork lacks: Reopen Closed
Video (Ctrl+Shift+T), Undo/Redo Grid Change (Ctrl+Z, Ctrl+Y /
Ctrl+Shift+Z), Bring to Front / Send to Back (Ctrl+Click /
Ctrl+Shift+Click), Show Big. Write a short port plan only; do not port
without owner OK.

## Out of scope

Changing any existing default binding; anything on Delete.
