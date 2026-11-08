# Rotate to fit

Turn videos on their side when their shape is the other way round to their
cell: a landscape video stands up in a tall cell, and a portrait video lies
down in a wide cell. Handy for a column of phone clips, or a wall of tall
cells.

## Turn it on

- Settings, General, Player, Video and sound: **Rotate videos to fit their
  cells** (off by default).
- Or right-click, **Video > Transform > Rotate Videos to Fit Cells**.

It's one switch for every cell. **Turn direction** picks **Rotate 90
(clockwise)** (default) or **Rotate 270 (counter-clockwise)**.

## Rules

- A video that's square, or a cell that's square (within 5%), isn't turned.
- A transform you pick by hand from **Video > Transform** wins for that file.
  The next file in the cell is fitted again.
- A video shown at a fixed **Aspect Ratio** or **Crop** shape you picked isn't
  turned (turning couldn't make it fit), and one turned before is turned back.
- A transform that came from your New Videos defaults or an older playlist is
  left as it is.
- Crop, screenshots and the crop dialog follow the turned picture.

## Not the same as the aspect filter

Rotate to fit changes how a file is shown. The [aspect filter](aspect-filter.md)
decides whether a file of the other orientation is played at all when a
cell moves on. You can use either, or both.
