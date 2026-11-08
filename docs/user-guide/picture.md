# Zoom, crop and picture

Everything here is on the right-click menu under **Video**, per cell, and
under **[ALL] > Video** for every cell. Keys act on the cell under the pointer;
add `Shift` for every cell.

## View mode

**Video > View Mode**:

- **Fill** (default): covers the cell, cutting off the edges.
- **Fit**: the whole picture, with bars.
- **Stretch**: covers the cell, changing the picture's shape.

## Zoom

| Do | Key |
| --- | --- |
| Zoom in | `.` or `+`, or `Ctrl`+wheel up |
| Zoom out | `,` or `-`, or `Ctrl`+wheel down |
| Zoom reset | `/` or `*` |
| Zoom into an area | `Ctrl`+drag around it, or **Zoom > Zoom to Selection** then drag |

- **Zoom to Cursor** zooms toward the pointer instead of the alignment point.
- Step size: Settings, Defaults, Playlist, Step Sizes, **Zoom** (10%), and
  **Proportional zoom** for steps that feel the same at 2x and 8x.

## Move the picture

- Middle-drag the picture, or `Alt` + arrow keys.
- **Position**: align to the center, an edge or a corner; **Set Position**
  for exact numbers; **Position Reset**.
- **Move Past Edges** lets a moved or zoomed picture go past the cell edge,
  as long as half of it stays in view.

## Aspect ratio and crop

- **Aspect Ratio**: Default (the video's own), or 16:9, 4:3, 1:1, 16:10,
  2.21:1, 2.35:1, 2.39:1, 5:4.
- **Crop**: a shape (16:10, 16:9, 4:3, 1.85:1, 2.21:1, 2.35:1, 2.39:1, 5:3,
  5:4, 1:1), **Custom…**, or margins with keys:

| Crop | More | Less |
| --- | --- | --- |
| Left | `U` | `I` |
| Top | `O` | `P` |
| Right | `Alt+U` | `Alt+I` |
| Bottom | `Alt+O` | `Alt+P` |
| Off | `Y` | |

## Transform

**Video > Transform**: Rotate 90 / 180 / 270, Flip Horizontally / Vertically,
Transpose, Anti-transpose, No Transform. **Rotate Videos to Fit Cells** is at
the bottom; see [Rotate to fit](rotate-to-fit.md).

## Deinterlace

**Video > Deinterlace**: Automatic (default, only videos marked interlaced),
On, Off, and the mode (Auto, Discard, Blend, Mean, Bob, Linear, X, Yadif,
Yadif 2x, Phosphor, Film NTSC). Yadif 2x, Bob and Phosphor double the frame
rate, which costs more with many cells.

## Video track

**Video > Video Track** picks another video track when a file has several.

## Screenshots

`Alt+S` saves a screenshot of the cell under the pointer; `Shift+Alt+S`
saves every cell. Settings, General, Player, Screenshots:

- **Folder**: empty means `screenshots` in the [data folder](../reference/data-folder.md).
- **File name**: default `%F_%P` (name without extension, then position).
  Tokens: `%f` name, `%F` name without extension, `%p` position `HH-MM-SS`,
  `%P` position with milliseconds, `%n` a number (0001 and up), `%D` date,
  `%T` date and time, `%%` a percent sign.
- **Format**: PNG (default) or JPG, with a **Quality** for JPG.

## Sync

Right-click, **Sync** (whole grid): **Zoom and Position** makes zooming or
moving one picture do the same in the others. **Sync Others > Zoom and
Position** on a cell copies its zoom and position to the others once.
