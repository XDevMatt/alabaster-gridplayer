# Mouse and side buttons

## Default mouse actions

These act on the cell under the pointer.

| Mouse | Does |
| --- | --- |
| Click | Play / pause the cell |
| Double-click | Single Mode on / off |
| Double-click the cell's title strip | Single Mode on / off for that cell, whatever double-click is set to |
| Wheel up / down | Volume up / down (3% per notch) |
| `Ctrl` + wheel | Zoom in / out |
| Right-click | The menu |
| Drag a cell | Move it to another place in the grid (drop on another cell to swap) |
| Middle-drag | Move the picture inside its cell |
| `Ctrl` + drag | Zoom into the part of the picture you draw around |
| Hold `Shift` while dropping | Do the other drop action (Add / Replace, Move / Swap / Replace) |

Touchpads and smooth-scrolling wheels are counted in whole notches, so one
swipe doesn't fire a dozen volume steps.

All of these can be changed on the Shortcuts page (Settings, Shortcuts, or
right-click, **Shortcuts**). The drags and the drop key are listed there too.

## Side buttons (Back / Forward)

Mouse side buttons have no default action. Give them one on the Shortcuts
page: pick an action (for example **Play Next File** and **Play Previous
File**), add a shortcut, and press the side button. It's recorded as
`Back-Click`, `Forward-Click`, or `Click-4` and up for extra buttons.

## Turning off clicks or the wheel

Right-click, **Playlist Settings**:

- **Disable Mouse Click Events**: clicks on a video do nothing (no pause, no
  Single Mode). Keys still work. **Side buttons still work**: they're
  treated like keys, so a side button set to Next / Previous keeps working
  with clicks off.
- **Disable Mouse Wheel Events**: the wheel over a video does nothing. Keys
  still work.

Both are saved with the playlist, with defaults in Settings, Defaults,
Playlist, Input.

## The pointer and the overlay

- The pointer hides after 5 seconds without moving (Settings, General,
  Player, Timeouts).
- The cell overlay (title, seek bar, buttons) hides after 3 seconds (Settings,
  Defaults, Playlist, Overlay). It can also be turned off.
- **Tab** / **Shift+Tab** move the active cell without the mouse.
