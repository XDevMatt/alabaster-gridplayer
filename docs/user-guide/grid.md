# The grid

The grid is the main window. Each cell plays its own video or playlist,
independently of the others.

## Add videos to the grid

Drag files or folders onto the window:

- **Several files**: you get one cell per file.
- **A folder**: you get one cell that plays the files in the folder (and its
  subfolders when **Include subfolders** is on) as a playlist. See [Play a folder](playlists.md#play-a-folder).

How many cells a drop makes is the **Cells** setting (Settings, Defaults,
Playlist, Drag-n-Drop). The default, **One per item**, gives each file and
each folder its own cell. Adding more than 12 cells at once asks first.

## Control a cell

Keys and mouse commands act on the cell under the mouse pointer. Move the
pointer over a cell before you press a key. With the pointer outside every
cell, for example on the window's title bar, cell keys do nothing.

| To do this | Do this |
| --- | --- |
| Play or pause | Click the cell, or press `Ctrl+Space`. |
| Next file in the cell | Press `N` or `PgDown`. |
| Previous file in the cell | Press `B` or `PgUp`. |
| Open the cell menu | Right-click the cell. |

## Loop part of a video (A-B loop)

To repeat one section of a video:

1. At the point where the loop should start, press `[`.
2. At the point where the loop should end, press `]`.

The cell now plays that section over and over.

To clear the loop and go back to normal playback, press `\` (**Loop Reset**),
or right-click the cell and choose **Playback > Loop > Loop Reset**.
`Shift+[`, `Shift+]` and `Shift+\` do the same for every cell at once.

## Focus on one cell (Single Mode)

Single Mode shows one cell on its own, filling the window. The other cells
are hidden, and they pause while hidden (setting **Pause background videos on
single mode**, on by default). They play again when you leave Single Mode.

- To turn it on, double-click the cell, or right-click it and choose
  **Enter Single Mode**.
- To go back to the grid, double-click again.

Single Mode is only offered when the grid has more than one cell or place.

In Single Mode, `E` [keeps](keep.md) the file you're watching, and the
Media Next / Media Previous keys switch to the next or previous cell.

## Change the grid layout

Right-click anywhere in the grid and open the **Grid** menu. The same options
are in Settings, Defaults, Playlist, Grid.

| Menu item | What it does |
| --- | --- |
| **Auto (Rows First)** | The default. Cells fill the grid row by row, and the grid grows as you add cells. |
| **Auto (Columns First)** | The same, column by column. |
| **Fixed Grid** | A grid of a set number of rows and columns. Cells stay where you put them, and empty places are kept. |
| **Size: N** (Auto modes) | How many cells per row (Rows First) or per column (Columns First). Auto (0) keeps the grid as square as it can. |
| **Fit Cells** (Auto modes) | When the last row or column isn't full, its cells stretch to fill it. On by default. |
| **Grid Size: N** (Fixed Grid) | The number of rows and columns. The default is 3 by 3. |
| **Show All Cells** (Fixed Grid) | Always show every row and column, with empty cells. When off, the grid shrinks to the cells in use. |
| **Shuffle** (`Alt+R`) | Puts the cells in a random order. **Shuffle Grid On Load** does this each time the playlist opens. |

## More about cells

- [New cells](new-cells.md): what a cell starts with (muted, looping).
- [Per-cell settings](profiles.md): what each cell keeps and saves.
- [Mouse and side buttons](mouse.md): drags, wheel, side buttons.
- [Dropping folders](folder-drop.md): what a dropped folder becomes.

## Find every command

Right-click anywhere in the grid and choose **Shortcuts** to see every command
and its key. For the full list, see [Hotkeys](../reference/hotkeys.md).
