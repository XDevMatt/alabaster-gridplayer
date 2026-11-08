# Aspect filter (Other Orientation)

The aspect filter decides what a cell does, **when it moves on to another
file**, with a file of the other orientation: a portrait file in a cell
that's wider than tall, or a landscape file in a cell that's taller than
wide. It never touches the file already playing.

| Choice | Menu name | What happens |
| --- | --- | --- |
| **Play it** (default) | Off | No filtering. |
| **Skip it** | Skip Other Orientation | Files of the other orientation are passed over. |
| **Ask** | Ask on Other Orientation | The cell pauses and asks **Play anyway** or **Skip**. |

## Set it

- One cell: right-click, **Playback > Other Orientation**.
- Every cell: **[ALL] > Playback > Other Orientation**.
- New cells: Settings, Defaults, New Videos, Playback, **Other orientation**.

It's saved with the playlist.

## How orientation is decided

- **The cell**: taller than wide means it wants portrait files; otherwise
  landscape. It's measured live, so resizing the window or changing the
  grid can change what fits.
- **The file**: VLC reads its width, height, rotation flag and pixel shape
  in the background. The answer is remembered per file (in
  `media_shapes.json` in the data folder) until the file changes.
- A file whose shape can't be read in time (about 3 seconds) counts as
  fitting.

## Limits

- It works when a cell steps through a **folder**: Next, Previous, Random
  and When Finished. Each step looks at up to **10 files**; if none fits, the
  next one plays anyway. (A version that keeps going is on the
  [roadmap](../FUTURE.md).)
- Files you drop or open yourself always play.
- It does not filter items of a [single-cell list](lists.md); it is
  folder-only.
- **Ask** is built but has not been re-verified recently. Treat it as
  experimental; **Skip it** is the supported mode.

## See also

[Rotate to fit](rotate-to-fit.md) turns a file to fit its cell instead of
skipping it.
